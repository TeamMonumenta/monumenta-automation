"""The /api/* HTTP routes (see API.md).

Every route except /api/health needs a bearer token minted in Discord. The
token's owner must still be a guild member who can see the bot channels, and
acts with exactly the privileges they would have typing commands in Discord:
changes go through the same TaskService calls.
"""

import mimetypes
import os
import re
import uuid
from typing import Any, Optional, Protocol, cast

from quart import Quart, Response, jsonify, request
from werkzeug.exceptions import HTTPException

from .charts import CHARTS, ChartError, ChartRenderer
from .formatting import format_entry
from .matching import get_list_match
from .models import Actor, Entry, Event, Member
from .service import PRIV_TEAM, Conflict, Forbidden, NotFound, TaskService, UserError
from .stats import RESOLUTION_ORDER, closer_rows, closer_stats, resolution_name
from .store import ENTRY_SORTS, EntryQuery
from .tokens import hash_token
from .vocab import COMPLEXITIES, PRIORITIES

MAX_LIMIT = 1000


class Directory(Protocol):
    def resolve_member(self, user_id: int) -> Optional[Member]: ...
    def user_name(self, user_id: int) -> Optional[str]: ...
    def find_user(self, query: str) -> tuple[int, str]: ...
    def is_ready(self) -> bool:
        """Whether Discord's member list has loaded, so resolve_member can be trusted."""
        ...


_UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")

# Headers a service (the game plugin) sends to act for a Minecraft player
PLAYER_HEADER = "X-Taskbot-Player"            # uuid
PLAYER_NAME_HEADER = "X-Taskbot-Player-Name"
PRIVILEGE_HEADER = "X-Taskbot-Privilege"      # what the service grants this player, 0-4


class ApiError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status


def _int_param(name: str, default: Optional[int] = None) -> Optional[int]:
    raw = request.args.get(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError:
        raise ApiError(400, f"{name} must be an integer") from None


def _list_param(name: str) -> list[str]:
    out: list[str] = []
    for raw in request.args.getlist(name):
        out.extend(x.strip() for x in raw.split(",") if x.strip())
    return out


# Writes a player may make through a service in a minute (reports, appends, closes, ...)
PLAYER_WRITES_PER_MINUTE = 20


def create_app(service: TaskService, directory: Directory, charts: ChartRenderer,
               internal: bool = False) -> Quart:
    """The API. `internal` is the cluster-only listener: service tokens (the game plugin)
    are accepted only there, so a leaked shard token is useless from outside the cluster,
    and Discord users' tokens only on the public one."""
    app = Quart(__name__)
    player_writes: dict[str, list[float]] = {}
    # Keep dict order: vocabularies, resolutions and charts are listed in a meaningful order
    app.json.sort_keys = False  # type: ignore[attr-defined]
    # Room for a request carrying the most context an entry may hold (MAX_CONTEXT_BYTES),
    # even with JSON escapes
    app.config["MAX_CONTENT_LENGTH"] = 64 << 20
    store = service.store
    config = service.config

    def user_obj(user_id: Optional[int]) -> Optional[dict[str, Any]]:
        if not user_id:
            return None
        return {"kind": "discord", "id": str(user_id), "name": directory.user_name(user_id)}

    def identity_obj(key: str) -> Optional[dict[str, Any]]:
        kind, _, ref = key.partition(":")
        return person(int(ref), None) if kind == "discord" else person(None, ref)

    def person(user_id: Optional[int], mc_uuid: Optional[str]) -> Optional[dict[str, Any]]:
        """A Discord user or a Minecraft player, as {"kind": ..., ...}."""
        if user_id:
            return user_obj(user_id)
        if mc_uuid:
            return {"kind": "minecraft", "uuid": mc_uuid, "name": store.player_name(mc_uuid)}
        return None

    def entry_json(e: Entry, *, text: bool = False) -> dict[str, Any]:
        out: dict[str, Any] = {
            "id": e.id,
            "description": e.description,
            "labels": e.labels,
            "priority": e.priority,
            "complexity": e.complexity,
            "status": e.status,
            "resolution": e.resolution,
            "resolution_name": resolution_name(config, e.resolution) if e.resolution else None,
            "close_reason": e.close_reason,
            "closed_at": e.closed_at,
            "closed_by": person(e.closed_by, e.closed_by_mc_uuid),
            "duplicate_of": e.duplicate_of,
            "duplicates": store.duplicates_of(e.id),
            "author": person(e.author_id, e.author_mc_uuid),
            "assignee": user_obj(e.assignee_id),
            "created_at": e.created_at,
            "updated_at": e.updated_at,
            "redacted": e.redacted,
            "pending_notification": e.pending_notification,
            "link": config.entry_link(e.message_id) if e.message_id else None,
            "images": [i.best_url(service.now()) for i in e.images],
            "reactions": [{"emoji": r.emoji, "count": r.count} for r in store.reactions(e.id)],
        }
        if text:
            out["text"] = format_entry(e, config, directory.user_name,
                                       reactions=store.reactions(e.id), include_link=True,
                                       duplicates=out["duplicates"])
        return out

    def event_json(ev: Event) -> dict[str, Any]:
        out: dict[str, Any] = {
            "id": ev.id, "entry_id": ev.entry_id, "at": ev.at,
            "actor": person(ev.actor_id, ev.actor_mc_uuid),
            "kind": ev.kind, "old": ev.old_value, "new": ev.new_value, "reason": ev.reason,
            "source": ev.source,
        }
        if ev.kind in ("assigned", "unassigned", "author"):
            # old/new are user ids here; also give them as user objects
            for key in ("old", "new"):
                raw = out[key]
                out[f"{key}_user"] = user_obj(int(raw)) if raw and str(raw).isdigit() else None
        return out

    def authenticate() -> Actor:
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer ") or not header[7:].strip():
            raise ApiError(401, "missing Authorization: Bearer token")
        info = store.token_info(hash_token(header[7:].strip()), service.now())
        if info is None:
            raise ApiError(401, "invalid or expired token")
        ref = "api:" + uuid.uuid4().hex[:12]
        if info.service is not None:
            if not internal:
                raise ApiError(403, "Service tokens only work on the internal (in-cluster) port")
            return service_actor(info.service, info.max_privilege or 0, info.scope == "read", ref)
        if internal:
            # Each kind of token works on its own port only, so neither is any use where
            # the other is reachable
            raise ApiError(403, "Discord users' tokens only work on the public port")
        member = directory.resolve_member(info.discord_id)
        if member is None and not directory.is_ready():
            raise ApiError(503, "the bot is still starting up; try again in a minute")
        if member is None or not member.can_view:
            raise ApiError(403, "the token's owner can no longer see the bot channels in Discord")
        if member.privilege < PRIV_TEAM:
            raise ApiError(403, "API access is for team members; the token's owner no longer is one")
        return Actor(id=member.id, name=member.name, privilege=member.privilege, source="api",
                     source_ref=ref, read_only=info.scope == "read")

    def check_player_rate(player: str) -> None:
        now = service.now()
        recent = [t for t in player_writes.get(player, []) if t > now - 60]
        if len(recent) >= PLAYER_WRITES_PER_MINUTE:
            raise ApiError(429, "Too many changes in a short time; please wait a minute")
        recent.append(now)
        player_writes[player] = recent

    def service_actor(name: str, max_privilege: int, read_only: bool, ref: str) -> Actor:
        """The service itself, or the Minecraft player it is acting for (from headers)."""
        player = request.headers.get(PLAYER_HEADER, "").strip().lower()
        if not player:
            # The service on its own behalf only reads (the instance's wording); it gets
            # no privilege, so everything that changes data is attributed to a player
            if request.method != "GET":
                raise ApiError(403, f"A service token changes things only for a player ({PLAYER_HEADER})")
            return Actor(id=0, name=name, privilege=0, source="api",
                         source_ref=f"{ref} service:{name}", read_only=True, service=name)
        if not _UUID_RE.match(player):
            raise ApiError(400, f"{PLAYER_HEADER} must be a player uuid")
        player_name = request.headers.get(PLAYER_NAME_HEADER, "").strip()[:32] or player
        try:
            asserted = int(request.headers.get(PRIVILEGE_HEADER, "0"))
        except ValueError:
            raise ApiError(400, f"{PRIVILEGE_HEADER} must be an integer") from None
        if request.method != "GET" and not read_only:
            # Only changes record the name, so reads can't rename players in the channel
            store.remember_player(player, player_name, service.now())
            # Taking notices happens on every join, which players do often; it mustn't use
            # up the budget for their reports
            if not request.path.endswith("/notices/take"):
                check_player_rate(player)
        return Actor(id=0, name=player_name, privilege=max(0, min(asserted, max_privilege)),
                     source="api", source_ref=f"{ref} service:{name}", read_only=read_only,
                     mc_uuid=player, service=name)

    def get_entry(entry_id: int) -> Entry:
        entry = store.get(entry_id)
        if entry is None:
            raise ApiError(404, f"{config.descriptor_proper} #{entry_id} not found")
        return entry

    async def body() -> dict[str, Any]:
        data = await request.get_json(force=True, silent=True)
        if data is None:
            return {}
        if not isinstance(data, dict):
            raise ApiError(400, "body must be a JSON object")
        return data  # pyright: ignore[reportUnknownVariableType]

    def text_field(data: dict[str, Any], key: str) -> str:
        value = data.get(key)
        if value is None:
            return ""
        if not isinstance(value, str):
            raise ApiError(400, f"{key} must be a string")
        return value

    def value_field(data: dict[str, Any], key: str) -> str:
        """A field that must have a value when given: a non-empty string (or a number)."""
        value = data.get(key)
        if isinstance(value, int) and not isinstance(value, bool):
            return str(value)
        if not isinstance(value, str) or not value.strip():
            raise ApiError(400, f"{key} must be a non-empty string")
        return value.strip()

    def labels_field(data: dict[str, Any]) -> list[str]:
        raw: Any = data.get("labels")
        if raw is None:
            return []
        if isinstance(raw, str):
            raw = raw.split(",")
        if not isinstance(raw, list) or not all(isinstance(x, str) for x in raw):  # pyright: ignore[reportUnknownVariableType]
            raise ApiError(400, "labels must be a list of names, or one comma separated string")
        return [match_vocab("label", x.strip(), store.labels()) for x in cast(list[str], raw)]

    async def mutated(entry: Entry, status: int = 200) -> tuple[Response, int]:
        fresh = store.get(entry.id) or entry
        return jsonify(entry_json(fresh)), status

    def match_vocab(kind: str, raw: str, vocab: list[str]) -> str:
        m = get_list_match(raw, vocab)
        if m is None:
            raise ApiError(400, f"unknown {kind} {raw!r}; one of: {', '.join(vocab)}")
        return m

    def user_param(raw: Optional[str], me: Actor, must_exist: bool = False) -> Optional[int]:
        """A user from an id, a name prefix or 'me'. Filters accept any id (old authors may
        have left); values being stored (author, assignee) must be users Discord knows."""
        if raw is None or raw == "":
            return None
        if raw == "me":
            if not me.id:
                raise ApiError(400, "'me' is a Discord user here; for a player use author_player=me")
            return me.id
        try:
            user_id = int(raw)
        except ValueError:
            return directory.find_user(raw)[0]
        return directory.find_user(str(user_id))[0] if must_exist else user_id

    def player_param(raw: Optional[str], me: Actor) -> Optional[str]:
        """A Minecraft player from a uuid, a known name, or 'me' (a service acting for a player)."""
        if raw is None or raw == "":
            return None
        if raw == "me":
            if me.mc_uuid is None:
                raise ApiError(400, "author_player=me needs a request made for a player")
            return me.mc_uuid
        found = store.find_player(raw.lower() if _UUID_RE.match(raw.lower()) else raw)
        if found is None:
            if _UUID_RE.match(raw.lower()):
                return raw.lower()
            raise ApiError(400, f"no player named {raw!r} has reported anything")
        return found[0]

    resolution_lookup = {resolution_name(config, r).lower(): r for r in RESOLUTION_ORDER}
    resolution_lookup.update({r: r for r in RESOLUTION_ORDER})

    def match_resolution(raw: str) -> str:
        """A resolution by key or display name (e.g. 'implemented'), abbreviations allowed."""
        m = get_list_match(raw, resolution_lookup.keys())
        if m is None:
            raise ApiError(400, f"unknown resolution {raw!r}; one of: "
                           f"{', '.join(resolution_name(config, r) for r in RESOLUTION_ORDER)}")
        return resolution_lookup[m]

    def check_reclose(entry: Entry, data: dict[str, Any]) -> None:
        """Closing a closed entry again would overwrite who closed it and when; the API
        asks for that explicitly (Discord keeps the old behavior of allowing it)."""
        force = data.get("force", False)
        if not isinstance(force, bool):
            raise ApiError(400, "force must be true or false")
        if entry.is_closed and not force:
            # Shown as is in game, where there is no force: the API docs say how
            raise ApiError(409, f"{config.descriptor_proper} #{entry.id} is already closed "
                           f"({resolution_name(config, entry.resolution or '')})")

    # ------------------------------------------------------------------
    # Error handling: every /api response is a JSON object
    # ------------------------------------------------------------------

    @app.errorhandler(ApiError)
    async def _api_error(err: ApiError) -> tuple[Response, int]:
        resp = jsonify({"error": str(err)})
        if err.status == 401:
            resp.headers["WWW-Authenticate"] = "Bearer"
        return resp, err.status

    @app.errorhandler(UserError)
    async def _user_error(err: UserError) -> tuple[Response, int]:
        status = 403 if isinstance(err, Forbidden) else 404 if isinstance(err, NotFound) \
            else 409 if isinstance(err, Conflict) else 400
        return jsonify({"error": str(err)}), status

    @app.errorhandler(HTTPException)
    async def _http_error(err: HTTPException) -> tuple[Response, int]:
        return jsonify({"error": err.description or err.name}), err.code or 500

    @app.errorhandler(Exception)
    async def _internal_error(err: Exception) -> tuple[Response, int]:
        app.logger.exception("Unhandled API error", exc_info=err)
        return jsonify({"error": "internal server error"}), 500

    # ------------------------------------------------------------------
    # Routes
    # ------------------------------------------------------------------

    @app.get("/api/health")
    async def health() -> Response:
        return jsonify({"ok": True})

    @app.get("/api/info")
    async def info() -> Response:
        me = authenticate()
        return jsonify({
            "descriptor": {
                "single": config.descriptor_single, "plural": config.descriptor_plural,
                "proper": config.descriptor_proper, "short": config.descriptor_short,
                "prefix": config.prefix,
            },
            "labels": store.labels(),
            "priorities": PRIORITIES,
            "complexities": list(COMPLEXITIES),
            "resolutions": {r: resolution_name(config, r) for r in RESOLUTION_ORDER},
            "reactions": config.reactions,
            "sorts": list(ENTRY_SORTS),
            "charts": {name: spec.summary.format(plural=config.descriptor_plural)
                       for name, spec in CHARTS.items()},
            "me": {"id": str(me.id), "name": me.name, "privilege": me.privilege,
                   "read_only": me.read_only},
        })

    @app.get("/api/entries")
    async def list_entries() -> Response:
        me = authenticate()
        status = request.args.get("status", "open")
        if status not in ("open", "closed", "all"):
            raise ApiError(400, "status must be open, closed or all")
        sort = request.args.get("sort", "id")
        if sort not in ENTRY_SORTS:
            raise ApiError(400, f"sort must be one of {', '.join(ENTRY_SORTS)}")
        order = request.args.get("order", "asc")
        if order not in ("asc", "desc"):
            raise ApiError(400, "order must be asc or desc")
        resolutions = [match_resolution(r) for r in _list_param("resolution")]
        assignee = request.args.get("assignee")
        if assignee not in (None, "", "any", "none"):
            assignee = str(user_param(assignee, me))
        labels_all = store.labels(include_inactive=True)
        q = EntryQuery(
            status=status,
            labels=[match_vocab("label", x, labels_all) for x in _list_param("label")],
            priorities=[match_vocab("priority", x, PRIORITIES) for x in _list_param("priority")],
            complexities=[match_vocab("complexity", x, list(COMPLEXITIES))
                          for x in _list_param("complexity")],
            resolutions=resolutions,
            assignee=assignee or None,
            # author=me for a request made for a player means the player
            author_id=None if (request.args.get("author") == "me" and me.mc_uuid)
            else user_param(request.args.get("author"), me),
            author_mc_uuid=player_param("me" if (request.args.get("author") == "me" and me.mc_uuid)
                                        else request.args.get("author_player"), me),
            closed_by=user_param(request.args.get("closed_by"), me),
            terms=request.args.get("q", "").split(),
            reason_terms=request.args.get("reason_contains", "").split(),
            idle_since=_int_param("idle_since"),
            created_after=_int_param("created_after"), created_before=_int_param("created_before"),
            closed_after=_int_param("closed_after"), closed_before=_int_param("closed_before"),
            reaction=request.args.get("reaction") or None,
            sort=sort, descending=order == "desc",
            limit=max(0, min(MAX_LIMIT, _int_param("limit", 50) or 0)),
            offset=max(0, _int_param("offset", 0) or 0),
        )
        text = request.args.get("text") in ("1", "true", "yes")
        return jsonify({"entries": [entry_json(e, text=text) for e in store.query(q)],
                        "total": store.count(q)})

    @app.get("/api/entries/<int:entry_id>")
    async def get_one(entry_id: int) -> Response:
        authenticate()
        text = request.args.get("text") in ("1", "true", "yes")
        return jsonify(entry_json(get_entry(entry_id), text=text))

    @app.get("/api/entries/<int:entry_id>/events")
    async def entry_events(entry_id: int) -> Response:
        me = authenticate()
        service.require_team_view(me)
        get_entry(entry_id)
        return jsonify({"events": [event_json(ev) for ev in store.events_for(entry_id)]})

    @app.get("/api/events")
    async def events() -> Response:
        me = authenticate()
        service.require_team_view(me)
        kinds = _list_param("kind")
        evs = store.events(since=_int_param("since"), until=_int_param("until"), kinds=kinds,
                           actor_id=user_param(request.args.get("actor"), me),
                           limit=max(1, min(MAX_LIMIT, _int_param("limit", 100) or 100)),
                           before_id=_int_param("before_id"))
        return jsonify({"events": [event_json(ev) for ev in evs]})

    @app.post("/api/entries")
    async def create() -> tuple[Response, int]:
        me = authenticate()
        data = await body()
        description = text_field(data, "description")
        labels = labels_field(data)
        context = data.get("context")
        if context is not None and not isinstance(context, dict):
            raise ApiError(400, "context must be an object of named sections")
        entry = service.add(me, description, labels,
                            context=cast(dict[str, object], context) if context else None)
        return await mutated(entry, 201)

    @app.patch("/api/entries/<int:entry_id>")
    async def patch(entry_id: int) -> tuple[Response, int]:
        me = authenticate()
        data = await body()
        entry = get_entry(entry_id)  # after the await, so checks see the current row
        allowed = ("description", "labels", "priority", "complexity", "author")
        unknown = set(data) - set(allowed)
        if unknown:
            raise ApiError(400, f"unknown fields: {', '.join(sorted(unknown))}")
        if not data:
            raise ApiError(400, f"nothing to change; fields: {', '.join(allowed)}")
        # Parse and check privileges for every field before changing anything
        ops: list[tuple[str, object]] = []
        if "description" in data:
            ops.append(("description", text_field(data, "description")))
        if "labels" in data:
            labels = labels_field(data)
            if not labels:
                raise ApiError(400, "labels must not be empty")
            ops.append(("label", labels))
        if "priority" in data:
            ops.append(("priority", match_vocab("priority", value_field(data, "priority"), PRIORITIES)))
        if "complexity" in data:
            ops.append(("complexity", match_vocab("complexity", value_field(data, "complexity"),
                                                  list(COMPLEXITIES))))
        if "author" in data:
            author = user_param(value_field(data, "author"), me, must_exist=True)
            assert author is not None
            ops.append(("author", author))
        return await mutated(service.edit_many(me, entry, ops))

    @app.post("/api/entries/<int:entry_id>/append")
    async def append(entry_id: int) -> tuple[Response, int]:
        me = authenticate()
        data = await body()
        text = text_field(data, "text").strip()
        if not text:
            raise ApiError(400, "text is required")
        return await mutated(service.append(me, get_entry(entry_id), text))

    @app.post("/api/entries/<int:entry_id>/fix")
    async def fix(entry_id: int) -> tuple[Response, int]:
        me = authenticate()
        data = await body()
        entry = get_entry(entry_id)
        check_reclose(entry, data)
        return await mutated(service.fix(me, entry, text_field(data, "reason")))

    @app.post("/api/entries/<int:entry_id>/reject")
    async def reject(entry_id: int) -> tuple[Response, int]:
        me = authenticate()
        data = await body()
        reason = text_field(data, "reason").strip()
        if not reason:
            raise ApiError(400, "reason is required")
        entry = get_entry(entry_id)
        check_reclose(entry, data)
        return await mutated(service.reject(me, entry, reason))

    @app.post("/api/entries/<int:entry_id>/dupe")
    async def dupe(entry_id: int) -> tuple[Response, int]:
        me = authenticate()
        data = await body()
        try:
            of = int(str(data.get("of", "")).lstrip("#"))
        except ValueError:
            raise ApiError(400, "of must be the original's number") from None
        entry = get_entry(entry_id)
        check_reclose(entry, data)
        return await mutated(service.dupe(me, entry, get_entry(of), text_field(data, "note")))

    @app.post("/api/entries/<int:entry_id>/reopen")
    async def reopen(entry_id: int) -> tuple[Response, int]:
        me = authenticate()
        return await mutated(service.reopen(me, get_entry(entry_id)))

    @app.post("/api/entries/<int:entry_id>/assign")
    async def assign(entry_id: int) -> tuple[Response, int]:
        me = authenticate()
        data = await body()
        service.require_team(me)
        if not data.get("user") and not me.id:
            raise ApiError(400, "Only Discord users can be assigned; give user")
        assignee = user_param(str(data["user"]), me, must_exist=True) if data.get("user") else me.id
        assert assignee is not None
        return await mutated(service.assign(me, get_entry(entry_id), assignee))

    @app.post("/api/entries/<int:entry_id>/unassign")
    async def unassign(entry_id: int) -> tuple[Response, int]:
        me = authenticate()
        return await mutated(service.unassign(me, get_entry(entry_id)))

    @app.post("/api/entries/<int:entry_id>/redact")
    async def redact(entry_id: int) -> tuple[Response, int]:
        me = authenticate()
        return await mutated(service.redact(me, get_entry(entry_id)))

    @app.get("/api/entries/<int:entry_id>/redacted")
    async def get_redacted(entry_id: int) -> Response:
        me = authenticate()
        return jsonify(service.redacted_content(me, get_entry(entry_id)))

    @app.get("/api/entries/<int:entry_id>/images")
    async def list_images(entry_id: int) -> Response:
        me = authenticate()
        saved = service.saved_images(me, get_entry(entry_id))
        return jsonify({"images": [
            {"name": os.path.basename(f.path or ""), "url": f.url, "size": f.size, "saved_at": f.checked_at}
            for f in saved]})

    @app.get("/api/entries/<int:entry_id>/images/<name>")
    async def get_image(entry_id: int, name: str) -> Response:
        me = authenticate()
        for f in service.saved_images(me, get_entry(entry_id)):
            if f.path is not None and os.path.basename(f.path) == name \
                    and os.path.isfile(service.archive.absolute(f.path)):
                mimetype = mimetypes.guess_type(name)[0] or "application/octet-stream"
                return Response(service.archive.read(f.path), mimetype=mimetype,
                                headers={"Content-Disposition": f'attachment; filename="{name}"'})
        raise ApiError(404, f"no saved image {name!r}")

    @app.get("/api/entries/<int:entry_id>/context")
    async def get_context(entry_id: int) -> Response:
        me = authenticate()
        entry = get_entry(entry_id)
        if not service.can_see_context(me):
            raise ApiError(403, "Context is only visible to the team")
        return jsonify({"context": [
            {"id": c.id, "section": c.section, "created_at": c.created_at, "source": c.source,
             "size": c.size, "data": c.data} for c in store.context_for(entry.id)]})

    @app.post("/api/entries/<int:entry_id>/context")
    async def add_context(entry_id: int) -> tuple[Response, int]:
        me = authenticate()
        data = await body()
        entry = get_entry(entry_id)
        if not data:
            raise ApiError(400, "body must be an object of named sections")
        service.add_context(me, entry, data)
        return jsonify({"ok": True}), 201

    def require_service_for(uuid_: str, me: Actor) -> str:
        """Player routes are for services (the game plugin), acting for that same player."""
        uuid_ = uuid_.lower()
        if not me.is_service:
            raise ApiError(403, "Only service tokens can use player routes")
        if not _UUID_RE.match(uuid_):
            raise ApiError(400, "not a player uuid")
        if me.mc_uuid is not None and me.mc_uuid != uuid_:
            raise ApiError(403, "A service acting for one player can't act for another")
        if request.method != "GET" and me.read_only:
            raise ApiError(403, "This API token is read-only")
        return uuid_

    @app.post("/api/players/<player>/notices/take")
    async def take_notices(player: str) -> Response:
        """The player's undelivered notices, marked delivered: the game plugin shows them when
        the player joins. One lost to a disconnect at that moment is not sent again."""
        me = authenticate()
        player = require_service_for(player, me)
        return jsonify({"notices": [
            {"id": n.id, "entry_id": n.entry_id, "text": n.text, "created_at": n.created_at}
            for n in store.take_notices(player, service.now())]})

    @app.get("/api/players/<player>/settings")
    async def get_player_settings(player: str) -> Response:
        me = authenticate()
        player = require_service_for(player, me)
        return jsonify({"uuid": player, "name": store.player_name(player),
                        "notifications": store.player_notifications(player)})

    @app.post("/api/players/<player>/settings")
    async def set_player_settings(player: str) -> Response:
        me = authenticate()
        player = require_service_for(player, me)
        data = await body()
        if not isinstance(data.get("notifications"), bool):
            raise ApiError(400, "notifications must be true or false")
        service.set_notifications(me, bool(data["notifications"]))
        return jsonify({"uuid": player, "name": store.player_name(player),
                        "notifications": store.player_notifications(player)})

    @app.get("/api/users")
    async def users() -> Response:
        authenticate()
        query = request.args.get("q", "").strip()
        if not query:
            raise ApiError(400, "q is required")
        user_id, name = directory.find_user(query)
        return jsonify({"user": {"id": str(user_id), "name": name}})

    @app.get("/api/stats")
    async def stats() -> Response:
        authenticate()
        grid: dict[str, dict[str, int]] = {p: {c: 0 for c in COMPLEXITIES} for p in PRIORITIES}
        for (p, c), n in store.open_counts_by_priority_complexity().items():
            grid.setdefault(p, {})[c] = n
        return jsonify({
            "open": store.count(EntryQuery(status="open")),
            "closed": store.count(EntryQuery(status="closed")),
            "open_by_priority_complexity": grid,
            "open_by_label": store.open_counts_by_label(),
            "closed_by_resolution": store.closed_counts_by_resolution(),
        })

    @app.get("/api/stats/authors")
    async def author_stats() -> Response:
        authenticate()
        limit = max(1, min(MAX_LIMIT, _int_param("limit", 25) or 25))
        return jsonify({"authors": [{"user": person(a.author_id, a.author_mc_uuid), "total": a.total,
                                     "open": a.open} for a in store.author_counts(limit)]})

    @app.get("/api/stats/closers")
    async def closer_stats_route() -> Response:
        me = authenticate()
        service.require_team_view(me)
        days = _int_param("days")
        since = service.now() - days * 86400 if days else None
        cs = closer_stats(store, since=since)
        limit = max(1, min(MAX_LIMIT, _int_param("limit", 25) or 25))
        return jsonify({
            "closers": [{"user": identity_obj(key), **{r: counts.get(r, 0) for r in RESOLUTION_ORDER},
                         "total": sum(counts.values())} for key, counts in closer_rows(cs)[:limit]],
            "self_closes": cs.self_closes,
            "unknown_closer": cs.unknown_closer,
            "since": since,
        })

    @app.get("/api/charts")
    async def chart_list() -> Response:
        me = authenticate()
        service.require_team_view(me)
        return jsonify({"charts": [{"name": s.name, "summary": s.summary.format(plural=config.descriptor_plural)}
                                   for s in CHARTS.values()]})

    @app.get("/api/charts/<name>.<ext>")
    async def chart(name: str, ext: str) -> Response:
        me = authenticate()
        service.require_team_view(me)
        if name not in CHARTS:
            raise ApiError(404, f"unknown chart {name!r}; one of: {', '.join(CHARTS)}")
        try:
            opts = charts.parse_options(request.args.get("options", "").split())
            if ext == "json":
                return jsonify(charts.data(name, opts))
            if ext != "png":
                raise ApiError(404, "charts are available as .png or .json")
            png = await charts.render_async(name, opts)
        except ChartError as e:
            raise ApiError(400, str(e)) from None
        return Response(png, mimetype="image/png")

    @app.route("/api/<path:_rest>", methods=["GET", "POST", "PATCH", "PUT", "DELETE"])
    async def not_found(_rest: str) -> Response:
        raise ApiError(404, "no such endpoint")

    return app
