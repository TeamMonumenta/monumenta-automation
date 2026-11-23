"""Every action on entries, with the privilege rules and the event log.

Text commands and the network API both call TaskService, so an action is
allowed, validated and recorded the same way wherever it comes from. Methods
raise UserError subclasses carrying the exact text the old bot replied with.

Nothing here awaits: each action validates and writes in one synchronous
transaction, so two actions can never interleave half-way.
"""

import json
import re
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass, fields
from typing import Any, Optional, cast

from . import duplicates
from .config import InstanceConfig
from .matching import get_list_match
from .identity import LinkResolver, NoLinks, is_author
from .images import ImageArchive
from .models import Actor, Entry, Image, ImageFile
from .stats import resolution_name
from .store import TaskStore, make_image
from .vocab import (
    COMPLEXITIES, DEFAULT_COMPLEXITY, DEFAULT_LABEL, DEFAULT_PRIORITY, DUPLICATE, FIXED, PRIORITIES, REJECTED,
)

# Limits on context attached to an entry (sections are JSON objects)
MAX_CONTEXT_SECTIONS = 32        # per entry
MAX_CONTEXT_BYTES = 10 << 20     # per entry, bytes of JSON
_SECTION_RE = re.compile(r"^[a-z][a-z0-9_.-]{0,63}$")

MAX_DESCRIPTION = 1600
MAX_CLOSE_REASON = 1000    # with a long description, rendering shortens the description to fit
MIN_REPORT_WORDS = 5   # for a new entry's description

# Same pattern discord.utils.escape_mentions neutralizes
_MENTION_RE = re.compile(r"@(everyone|here|[!&]?[0-9]{17,20})")

PRIV_EVERYONE = 0
PRIV_AUTHOR = 1   # also granted by ownership of the entry
PRIV_TEAM = 2
PRIV_LEAD = 3
PRIV_OWNER = 4

EDIT_FIELDS = ("description", "label", "image", "author", "priority", "complexity")
# Events whose values are the entry's text (blanked by redaction).
_TEXT_EVENT_KINDS = ("created", "description", "appended", "image")

_EDIT_PRIV = {"description": PRIV_AUTHOR, "label": PRIV_AUTHOR, "image": PRIV_AUTHOR,
              "author": PRIV_TEAM, "priority": PRIV_TEAM, "complexity": PRIV_TEAM}


class UserError(Exception):
    """An error whose message is shown to the user as-is."""


class NotFound(UserError):
    pass


class Forbidden(UserError):
    pass


class Conflict(UserError):
    pass


_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")


def contains_mentions(text: str) -> bool:
    return _MENTION_RE.search(text) is not None


def _merge_hidden(earlier: dict[str, Any], later: dict[str, Any]) -> dict[str, Any]:
    """What a second redaction hides, added to what the first one did."""
    def text(key: str) -> Optional[str]:
        parts = [str(v) for v in (earlier.get(key), later.get(key)) if v and v != "redacted"]
        return "\n\n".join(dict.fromkeys(parts)) or None
    return {
        "description": text("description"),
        "close_reason": text("close_reason"),
        "images": list(dict.fromkeys([*(earlier.get("images") or []), *(later.get("images") or [])])),
        "events": [*(earlier.get("events") or []), *(later.get("events") or [])],
    }


def compute_privilege(config: InstanceConfig, user_id: int, role_ids: Sequence[int]) -> int:
    """Role/user based privilege, exactly as the old has_privilege computed it."""
    priv = max(0, config.user_privileges.get(user_id, 0))
    for role in role_ids:
        priv = max(priv, config.group_privileges.get(role, 0))
    return priv


@dataclass
class Change:
    """Passed to change listeners after an action commits."""
    entry_id: int
    actor: Actor
    action: str        # e.g. 'created', 'fixed', 'edited priority'


class TaskService:
    def __init__(self, store: TaskStore, config: InstanceConfig,
                 clock: Callable[[], float] = time.time, links: Optional[LinkResolver] = None):
        # Discord <-> Minecraft account links; none exist yet (see identity.py)
        self.links: LinkResolver = links or NoLinks()
        self.store = store
        self.archive = ImageArchive(config.images_dir)
        self.config = config
        self._clock = clock
        self.listeners: list[Callable[[Change], None]] = []
        self._held: Optional[list[Change]] = None   # changes told only after edit_many commits

    def now(self) -> int:
        return int(self._clock())

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def proper(self) -> str:
        return self.config.descriptor_proper

    @property
    def single(self) -> str:
        return self.config.descriptor_single

    def get_entry(self, index_str: str | int) -> Entry:
        """Look up an entry by user-supplied number, with the old error text."""
        try:
            index = int(index_str)
        except (TypeError, ValueError):
            raise UserError(f"{index_str!r} is not a number") from None
        entry = self.store.get(index)
        if entry is None:
            raise NotFound(f"{self.proper} #{index} not found!")
        return entry

    def _reload(self, entry: Entry) -> Entry:
        """Bring the caller's copy of an entry up to date before acting on it. A front end
        may have read it before an await (or an interactive session long before), and an
        action on a stale copy could write back text a redaction hid meanwhile."""
        current = self.store.get(entry.id)
        if current is None:
            raise NotFound(f"{self.proper} #{entry.id} not found!")
        for f in fields(Entry):
            setattr(entry, f.name, getattr(current, f.name))
        return entry

    def is_author(self, actor: Actor, entry: Entry) -> bool:
        return is_author(actor, entry, self.links)

    def has_privilege(self, actor: Actor, min_privilege: int, entry: Optional[Entry] = None) -> bool:
        priv = actor.privilege
        if entry is not None and self.is_author(actor, entry):
            priv = max(priv, PRIV_AUTHOR)
        return priv >= min_privilege

    @staticmethod
    def _require_writable(actor: Actor) -> None:
        if actor.read_only:
            raise Forbidden("This API token is read-only")

    def _require(self, actor: Actor, min_privilege: int, message: str,
                 entry: Optional[Entry] = None) -> None:
        self._require_writable(actor)
        if not self.has_privilege(actor, min_privilege, entry):
            raise Forbidden(message)

    def check_text(self, text: str) -> None:
        """Reject text that would ping people, or carries control characters (terminal
        escapes, which taskctl would print as they are)."""
        if contains_mentions(text):
            raise UserError(f"Please do not include pings in your {self.single}")
        if _CONTROL_RE.search(text):
            raise UserError("Please do not include control characters")

    def _check_description(self, description: str) -> None:
        self.check_text(description)
        if len(description) > MAX_DESCRIPTION:
            raise UserError(
                f"Please limit your {self.single} to {MAX_DESCRIPTION} characters to allow for "
                f"formatting and close info (currently {len(description)} characters)")

    def _check_labels(self, labels: Sequence[str]) -> None:
        active = self.store.labels()
        if not labels or any(label not in active and label != DEFAULT_LABEL for label in labels):
            raise self.labels_error()

    def _event(self, entry_id: int, kind: str, actor: Actor, *, old: object = None,
               new: object = None, reason: Optional[str] = None) -> None:
        self.store.add_event(entry_id, kind, at=self.now(), actor_id=actor.id or None,
                             actor_mc_uuid=actor.mc_uuid,
                             source=actor.source, old=old, new=new, reason=reason,
                             source_ref=actor.source_ref)

    def _notify_flag(self, entry: Entry, actor: Actor) -> bool:
        """Old rule: the author's own changes clear the pending notification, others set it."""
        return not self.is_author(actor, entry)

    def _changed(self, entry_id: int, actor: Actor, action: str) -> None:
        change = Change(entry_id, actor, action)
        if self._held is not None:
            self._held.append(change)
            return
        for listener in list(self.listeners):
            listener(change)

    def edit_many(self, actor: Actor, entry: Entry, ops: Sequence[tuple[str, object]]) -> Entry:
        """Several `edit` operations, all or none: one refused leaves the entry as it was."""
        for op, _ in ops:
            self.check_edit(actor, entry, op)
        self._held = []
        try:
            with self.store.transaction():
                for op, value in ops:
                    entry = self.edit(actor, entry, op, value)
            held = self._held
        finally:
            self._held = None
        for change in held:
            for listener in list(self.listeners):
                listener(change)
        return entry

    def match_labels(self, raw: str) -> tuple[list[str], bool]:
        """Prefix-match comma separated labels. Returns (matched, any_failed)."""
        good: list[str] = []
        failed = False
        active = self.store.labels()
        for label in raw.strip().lower().split(","):
            match = get_list_match(label.strip(), active)
            if match is None:
                failed = True
            else:
                good.append(match)
        return good, failed

    def labels_error(self) -> UserError:
        return UserError(f"Labels must be one of: [{','.join(self.store.labels())}]")

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def add(self, actor: Actor, description: str, labels: Sequence[str],
            images: Sequence[Image] = (),
            context: Optional[dict[str, object]] = None) -> Entry:
        """Create an entry authored by actor (a Discord user or a Minecraft player).
        `labels` are already matched to label names; none means misc."""
        self._require_writable(actor)
        if context:
            self._check_context(actor, context)
        description = description.strip()
        if len(description.split()) < MIN_REPORT_WORDS:
            raise UserError(f"Description must contain at least {MIN_REPORT_WORDS} words")
        self._check_description(description)
        labels = list(labels) or [DEFAULT_LABEL]
        self._check_labels(labels)
        now = self.now()
        with self.store.transaction():
            index = self.store.allocate_index()
            entry = Entry(
                id=index, description=description, author_id=actor.id,
                author_mc_uuid=actor.mc_uuid, author_mc_name=actor.name if actor.mc_uuid else None,
                priority=DEFAULT_PRIORITY,
                complexity=DEFAULT_COMPLEXITY, labels=labels, images=list(images),
                created_at=now, updated_at=now)
            if actor.mc_uuid:
                self.store.remember_player(actor.mc_uuid, actor.name, now)
            self.store.insert_entry(entry)
            self.store.mark_dirty(index)
            self._event(index, "created", actor, new=description)
            for section, data in (context or {}).items():
                self.store.add_context(index, section, data, self._context_source(actor), now)
        self._changed(index, actor, "created")
        return entry

    # ------------------------------------------------------------------
    # Edit
    # ------------------------------------------------------------------

    def check_edit(self, actor: Actor, entry: Entry, operation: str) -> None:
        """Raise unless actor may perform this `edit` operation on entry."""
        if operation not in EDIT_FIELDS:
            raise UserError("Item to edit must be 'description', 'label', 'image', 'author', "
                            "'priority' or 'complexity'")
        self._require(actor, _EDIT_PRIV[operation],
                      f"You do not have permission to edit {operation} for entry #{entry.id}", entry)

    def edit(self, actor: Actor, entry: Entry, operation: str, value: object) -> Entry:
        """Apply one `edit` operation. `value` is already parsed:
        description: str, label: list[str], image: list[Image], author: int,
        priority / complexity: the matched vocabulary name."""
        self._reload(entry)
        self.check_edit(actor, entry, operation)
        if self._unchanged(entry, operation, value):
            # Accepted as before, but nothing happened: no history, notification or publish
            return entry

        fields: dict[str, object] = {}
        with self.store.transaction():
            if operation == "description":
                assert isinstance(value, str)
                description = value.strip()
                if not description:
                    raise UserError("You need to actually supply a new description")
                self._check_description(description)
                self._event(entry.id, "description", actor, old=entry.description, new=description)
                fields["description"] = description
                entry.description = description
            elif operation == "label":
                assert isinstance(value, list)
                labels = [str(v) for v in value]  # pyright: ignore[reportUnknownVariableType, reportUnknownArgumentType]
                self._check_labels(labels)
                self._event(entry.id, "labels", actor, old=entry.labels, new=labels)
                self.store.set_labels(entry.id, labels)
                entry.labels = labels
            elif operation == "image":
                assert isinstance(value, list)
                images: list[Image] = [v for v in value if isinstance(v, Image)]  # pyright: ignore[reportUnknownVariableType]
                self._event(entry.id, "image", actor, old=[i.url for i in entry.images],
                            new=[i.url for i in images])
                self.store.set_images(entry.id, images)
                entry.images = images
            elif operation == "author":
                assert isinstance(value, int)
                self._event(entry.id, "author", actor, old=entry.author_id or entry.author_mc_uuid,
                            new=value)
                # One author: a Discord user replaces an in-game reporter entirely
                fields["author_id"] = value
                fields["author_mc_uuid"] = None
                entry.author_id = value
                entry.author_mc_uuid = None
                entry.author_mc_name = None
            else:
                assert isinstance(value, str)
                if value not in (PRIORITIES if operation == "priority" else COMPLEXITIES):
                    raise UserError(f"Unknown {operation} {value!r}")
                old = entry.priority if operation == "priority" else entry.complexity
                self._event(entry.id, operation, actor, old=old, new=value)
                fields[operation] = value
                setattr(entry, operation, value)

            if self.is_author(actor, entry):
                entry.pending_notification = False
            elif operation != "label":
                # If only the label changed, the notification setting is left alone
                entry.pending_notification = True
            fields["pending_notification"] = entry.pending_notification
            fields["updated_at"] = entry.updated_at = self.now()
            self.store.update(entry.id, **fields)
            self.store.mark_dirty(entry.id)
        self._changed(entry.id, actor, f"edited {operation}")
        return entry

    @staticmethod
    def _unchanged(entry: Entry, operation: str, value: object) -> bool:
        """Whether an `edit` would leave the entry as it is."""
        if operation == "description":
            return isinstance(value, str) and value.strip() == entry.description
        if operation in ("label", "image"):
            if not isinstance(value, list):
                return False
            items = cast(list[object], value)
            if operation == "label":
                return list(dict.fromkeys(str(v) for v in items)) == entry.labels
            return [v.url for v in items if isinstance(v, Image)] == [i.url for i in entry.images]
        if operation == "author":
            return value == entry.author_id and entry.author_mc_uuid is None
        return value == (entry.priority if operation == "priority" else entry.complexity)

    def check_append(self, actor: Actor, entry: Entry) -> None:
        self._require(actor, PRIV_AUTHOR, f"You do not have permission to append to #{entry.id}", entry)

    def append(self, actor: Actor, entry: Entry, text: str) -> Entry:
        self._reload(entry)
        self.check_append(actor, entry)
        text = text.strip()
        self.check_text(text)
        description = f"{entry.description}\n{text}"
        if len(description) > MAX_DESCRIPTION:
            raise UserError(
                f"Appending this message brings the length to {len(description)} which exceeds "
                f"the {MAX_DESCRIPTION} character maximum to allow for formatting and close info")
        with self.store.transaction():
            self._event(entry.id, "appended", actor, new=text)
            entry.description = description
            entry.pending_notification = self._notify_flag(entry, actor)
            entry.updated_at = self.now()
            self.store.update(entry.id, description=description,
                              pending_notification=entry.pending_notification,
                              updated_at=entry.updated_at)
            self.store.mark_dirty(entry.id)
        self._changed(entry.id, actor, "appended")
        return entry

    # ------------------------------------------------------------------
    # Close / reopen
    # ------------------------------------------------------------------

    def close(self, actor: Actor, entry: Entry, resolution: str, reason: str,
              duplicate_of: Optional[int] = None, verb: Optional[str] = None) -> Entry:
        """Close (or re-close, which the old bot allowed) an entry.

        verb is the wording for the permission error: 'fix', 'reject', ...
        """
        if resolution not in (FIXED, REJECTED, DUPLICATE):
            raise UserError(f"Unknown resolution {resolution!r}")
        verb = verb or {FIXED: "fix", REJECTED: "reject"}.get(resolution, "close")
        self._reload(entry)
        self._require(actor, PRIV_AUTHOR, f"You do not have permission to {verb} #{entry.id}", entry)
        self.check_text(reason)
        if len(reason) > MAX_CLOSE_REASON:
            raise UserError(f"Please keep the reason to {MAX_CLOSE_REASON} characters "
                            f"(currently {len(reason)})")
        now = self.now()
        old_original = entry.duplicate_of
        with self.store.transaction():
            if entry.assignee_id is not None:
                self._event(entry.id, "unassigned", actor, old=entry.assignee_id, reason="closed")
            self._event(entry.id, "closed", actor, old=entry.resolution, new=resolution, reason=reason)
            entry.status = "closed"
            entry.resolution = resolution
            entry.close_reason = reason
            entry.closed_at = now
            entry.closed_by = actor.id or None
            entry.closed_by_mc_uuid = actor.mc_uuid
            entry.duplicate_of = duplicate_of
            entry.assignee_id = None
            entry.pending_notification = self._notify_flag(entry, actor)
            entry.updated_at = now
            self.store.update(
                entry.id, status="closed", resolution=resolution,
                close_reason=reason, closed_at=now, closed_by=entry.closed_by,
                closed_by_mc_uuid=actor.mc_uuid,
                duplicate_of=duplicate_of, assignee_id=None,
                pending_notification=entry.pending_notification, updated_at=now)
            self.store.mark_dirty(entry.id)
            self._originals_changed(old_original, duplicate_of)
        self._changed(entry.id, actor, {FIXED: "fixed", REJECTED: "rejected"}.get(resolution, "duped"))
        return entry

    def _originals_changed(self, *originals: Optional[int]) -> None:
        """An entry stopped or started being a duplicate: its originals list their duplicates,
        so their tracking messages are published again."""
        for original in set(originals):
            if original is not None:
                self.store.mark_dirty(original)

    def fix(self, actor: Actor, entry: Entry, reason: str = "") -> Entry:
        reason = reason.strip()
        original = self._original_named(entry, reason)
        if original is not None:
            # "fixed, dupe of 2360": a duplicate, if the reason names the original
            return self.close(actor, entry, DUPLICATE, reason, duplicate_of=original, verb="fix")
        return self.close(actor, entry, FIXED, reason or "Fixed")

    def reject(self, actor: Actor, entry: Entry, reason: str) -> Entry:
        reason = reason.strip()
        if not reason:
            raise UserError("A reason is required to reject")
        if duplicates.says_duplicate(reason):
            # "dupe of #123", from before `dupe` existed: linked if the number is an entry
            return self.close(actor, entry, DUPLICATE, reason,
                              duplicate_of=self._original_named(entry, reason), verb="reject")
        return self.close(actor, entry, REJECTED, reason)

    def _original_named(self, entry: Entry, reason: str) -> Optional[int]:
        """The entry a close reason says this one duplicates, if it says so and it exists."""
        if not duplicates.says_duplicate(reason):
            return None
        target = duplicates.duplicate_target(reason)
        if target is None or target == entry.id or self.store.get(target) is None:
            return None
        return target

    def dupe(self, actor: Actor, entry: Entry, original: Entry, note: str = "") -> Entry:
        if original.id == entry.id:
            raise UserError(f"{self.proper} #{entry.id} can not be a duplicate of itself")
        reason = f"Duplicate of #{original.id}"
        if note.strip():
            reason += f": {note.strip()}"
        return self.close(actor, entry, DUPLICATE, reason, duplicate_of=original.id,
                          verb="mark as duplicate")

    def reopen(self, actor: Actor, entry: Entry) -> Entry:
        self._reload(entry)
        self._require(actor, PRIV_AUTHOR, f"You do not have permission to unfix #{entry.id}", entry)
        if not entry.is_closed:
            raise Conflict(f"{self.proper} #{entry.id} is not closed")
        old_original = entry.duplicate_of
        with self.store.transaction():
            self._event(entry.id, "reopened", actor, old=entry.resolution,
                        reason=None if entry.redacted else entry.close_reason)
            entry.status = "open"
            entry.resolution = None
            entry.close_reason = None
            entry.closed_at = None
            entry.closed_by = None
            entry.closed_by_mc_uuid = None
            entry.duplicate_of = None
            entry.pending_notification = self._notify_flag(entry, actor)
            entry.updated_at = self.now()
            self.store.update(
                entry.id, status="open", resolution=None,
                close_reason=None, closed_at=None, closed_by=None, duplicate_of=None,
                closed_by_mc_uuid=None,
                pending_notification=entry.pending_notification, updated_at=entry.updated_at)
            self.store.mark_dirty(entry.id)
            self._originals_changed(old_original)
        self._changed(entry.id, actor, "reopened")
        return entry

    # ------------------------------------------------------------------
    # Redact (the `delete` command)
    # ------------------------------------------------------------------

    def redact(self, actor: Actor, entry: Entry) -> Entry:
        """Hide an entry's content from everyone but the team. The text, close reason,
        images and the text in its history move to `redacted_content`, readable at team
        privilege (`redacted_content()`); what remains says "redacted". As before, a
        closed entry stays closed and an open one open. `purge` removes it for good.

        Redacting again hides whatever was added since (an edit or append, a close
        reason), keeping what the first redaction hid."""
        self._reload(entry)
        self._require(actor, PRIV_AUTHOR, "You do not have permission to use this command")
        now = self.now()
        with self.store.transaction():
            events = [{"id": ev.id, "kind": ev.kind, "at": ev.at, "old": ev.old_value,
                       "new": ev.new_value, "reason": ev.reason}
                      for ev in self.store.events_for(entry.id)
                      if ev.reason or (ev.kind in _TEXT_EVENT_KINDS and (ev.old_value or ev.new_value))]
            hidden: dict[str, Any] = {
                "description": entry.description,
                "close_reason": entry.close_reason,
                "images": [img.url for img in entry.images],
                "events": events,
            }
            if entry.redacted:
                if entry.description == "redacted" and not entry.close_reason \
                        and not entry.images and not events:
                    raise Conflict(f"{self.proper} #{entry.id} is already redacted")
                hidden = _merge_hidden(self.store.redacted_content(entry.id) or {}, hidden)
            self.store.save_redacted(entry.id, hidden, now, actor.id or None)
            self.store.clear_notices(entry.id)
            self.store.scrub_events(entry.id, _TEXT_EVENT_KINDS)
            self.store.scrub_reasons(entry.id)
            self._event(entry.id, "redacted", actor)
            entry.description = "redacted"
            if entry.is_closed:
                entry.close_reason = ""
            entry.pending_notification = False
            entry.images = []
            entry.redacted = True
            entry.updated_at = now
            self.store.update(entry.id, description="redacted", close_reason=entry.close_reason,
                              pending_notification=False, redacted=True, updated_at=now)
            self.store.set_images(entry.id, [])
            self.store.mark_dirty(entry.id)
        self.store.checkpoint()
        self._changed(entry.id, actor, "redacted")
        return entry

    def redacted_content(self, actor: Actor, entry: Entry) -> dict[str, Any]:
        """What `redact` hid. Team only, and only ever shown privately."""
        self.require_team_view(actor)
        hidden = self.store.redacted_content(entry.id)
        if hidden is None:
            raise NotFound(f"{self.proper} #{entry.id} has no redacted content")
        return hidden

    def image_messages(self, entry: Entry) -> list[int]:
        """The bot's own messages in the feed channel holding an entry's images. `purge`
        needs them deleted first, since afterwards nothing would know of them."""
        return self.store.image_messages(entry.id)

    def purge(self, actor: Actor, entry: Entry) -> Optional[int]:
        """Delete an entry for good: its row, history, images and their saved copies, context
        and anything redacted. The number is not reused. Returns the tracking message id, for
        the caller to delete. The caller deletes `image_messages` before this."""
        self._require(actor, PRIV_LEAD, "You do not have permission to use this command")
        self._reload(entry)
        with self.store.transaction():
            self.store.delete_entry(entry.id)
            self._originals_changed(entry.duplicate_of)
        self.store.checkpoint()
        self.archive.remove_entry(entry.id)
        self._changed(entry.id, actor, "purged")
        return entry.message_id

    # ------------------------------------------------------------------
    # Saved images
    # ------------------------------------------------------------------

    def check_postable(self, entry_id: int) -> Entry:
        """Raise unless an entry's images may be posted in a channel. Every image the bot
        posts goes through here first: a redacted entry's images are never posted, only
        shown privately to the team."""
        entry = self.store.get(entry_id)
        if entry is None:
            raise NotFound(f"{self.proper} #{entry_id} not found!")
        if entry.redacted:
            raise Forbidden(f"{self.proper} #{entry_id} is redacted, so its images are not posted")
        return entry

    def image_posted(self, entry_id: int, old_url: str, new_url: str, path: Optional[str],
                     message_id: int, actor: Optional[Actor] = None) -> bool:
        """Record that the bot posted a copy of an entry's image in the feed channel, and show
        that copy from now on. With an actor (`reupload`) it is in the history. False when the
        entry was redacted (or purged) while the image was being posted: the message is
        recorded anyway, so `image_messages_to_delete` finds it if deleting it now fails."""
        with self.store.transaction():
            entry = self.store.get(entry_id)
            if entry is None:
                return False
            size = self.archive.size(path) if path is not None else None
            self.store.add_image_file(ImageFile(entry_id, new_url, path, size, self.now(), message_id))
            if entry.redacted:
                return False
            self.store.replace_image_url(entry_id, old_url, make_image(new_url))
            if actor is not None:
                self._event(entry_id, "image", actor, old=[old_url], new=[new_url])
            self.store.mark_dirty(entry_id)
        return True

    def image_messages_to_delete(self) -> list[int]:
        """The bot's own image messages in the feed channel that must go: those of redacted
        entries. The bot deletes them right after a redaction, and again on every pass of
        its save loop until Discord confirms (`image_message_deleted`)."""
        return self.store.redacted_image_messages()

    def image_message_deleted(self, message_id: int) -> None:
        self.store.forget_image_message(message_id)

    def check_reupload(self, actor: Actor, entry: Entry) -> list[tuple[Image, Optional[ImageFile]]]:
        """For `reupload`: the entry's images, each with its saved copy if there is one."""
        self.require_team(actor)
        self.check_postable(entry.id)
        saved = {f.url: f for f in self.store.image_files(entry.id) if f.path}
        return [(im, saved.get(im.url)) for im in entry.images]

    def saved_images(self, actor: Actor, entry: Entry) -> list[ImageFile]:
        """Saved copies of an entry's images, including earlier and redacted ones. Those of a
        redacted entry only for the team."""
        if entry.redacted:
            self.require_team_view(actor)
        seen: set[str] = set()
        files: list[ImageFile] = []
        for f in self.store.image_files(entry.id):
            if f.path and f.path not in seen:   # copies posted by the bot share a file
                seen.add(f.path)
                files.append(f)
        return files

    def redacted_images(self, actor: Actor, entry: Entry) -> list[ImageFile]:
        """Saved copies of the images redaction hid, for showing privately to the team."""
        hidden = self.redacted_content(actor, entry)
        urls: list[str] = hidden.get("images") or []
        saved = {f.url: f for f in self.store.image_files(entry.id) if f.path}
        return [saved[u] for u in urls if u in saved]

    # ------------------------------------------------------------------
    # Assignment
    # ------------------------------------------------------------------

    @staticmethod
    def require_team_view(actor: Actor) -> None:
        """For team-only views (history, closer stats, charts); read-only tokens qualify."""
        if actor.privilege < PRIV_TEAM:
            raise Forbidden("You do not have permission to use this command")

    def require_team(self, actor: Actor) -> None:
        self._require(actor, PRIV_TEAM, "You do not have permission to use this command")

    def assign(self, actor: Actor, entry: Entry, assignee_id: int) -> Entry:
        self._reload(entry)
        self.require_team(actor)
        with self.store.transaction():
            self._event(entry.id, "assigned", actor, old=entry.assignee_id, new=assignee_id)
            entry.assignee_id = assignee_id
            entry.updated_at = self.now()
            self.store.update(entry.id, assignee_id=assignee_id, updated_at=entry.updated_at)
            self.store.mark_dirty(entry.id)
        self._changed(entry.id, actor, "assigned")
        return entry

    def unassign(self, actor: Actor, entry: Entry) -> Entry:
        self._reload(entry)
        self.require_team(actor)
        if entry.assignee_id is None:
            raise Conflict(f"{self.proper} #{entry.id} is already unassigned")
        with self.store.transaction():
            self._event(entry.id, "unassigned", actor, old=entry.assignee_id)
            entry.assignee_id = None
            entry.updated_at = self.now()
            self.store.update(entry.id, assignee_id=None, updated_at=entry.updated_at)
            self.store.mark_dirty(entry.id)
        self._changed(entry.id, actor, "unassigned")
        return entry

    # ------------------------------------------------------------------
    # Labels
    # ------------------------------------------------------------------

    def add_label(self, actor: Actor, name: str) -> str:
        self._require(actor, PRIV_LEAD, "You do not have permission to use this command")
        name = name.lower()
        if not name or re.search("[^a-z]", name):
            raise UserError(f"Usage: {self.config.prefix} addlabel <label>\n"
                            "Labels can only contain a-z characters")
        match = get_list_match(name, self.store.labels())
        if match is not None:
            raise Conflict(f"Can not add label {name} because it matches {match}")
        self.store.add_label(name)
        return name

    def remove_label(self, actor: Actor, name: str) -> tuple[str, list[int]]:
        """Remove a label from the vocabulary and from every entry. Returns (label, changed ids)."""
        self._require(actor, PRIV_LEAD, "You do not have permission to use this command")
        name = name.lower()
        if not name or re.search("[^a-z]", name):
            raise UserError(f"Usage: {self.config.prefix} dellabel <label>\n"
                            "Labels can only contain a-z characters")
        match = get_list_match(name, self.store.labels())
        if match is None:
            raise UserError(f"Input {name} does not match any existing labels "
                            f"[{','.join(self.store.labels())}]")
        if match == DEFAULT_LABEL:
            raise UserError(f"{DEFAULT_LABEL} can't be removed: entries filed without a label get it")
        changed: list[int] = []
        with self.store.transaction():
            self.store.deactivate_label(match)
            for entry in self.store.get_many(self.store.entries_with_label(match)):
                labels = [lbl for lbl in entry.labels if lbl != match] or [DEFAULT_LABEL]
                self._event(entry.id, "labels", actor, old=entry.labels, new=labels,
                            reason=f"label {match} removed")
                self.store.set_labels(entry.id, labels)
                self.store.update(entry.id, updated_at=self.now())
                if not entry.is_closed or entry.message_id is not None:
                    self.store.mark_dirty(entry.id)
                changed.append(entry.id)
        for entry_id in changed:
            self._changed(entry_id, actor, "edited label")
        return match, changed

    # ------------------------------------------------------------------
    # Notifications
    # ------------------------------------------------------------------

    def set_notifications(self, actor: Actor, enabled: bool) -> None:
        """notify on/off, for whichever kind of account the actor is."""
        self._require_writable(actor)
        if actor.mc_uuid:
            self.store.set_player_notifications(actor.mc_uuid, enabled)
        else:
            self.store.set_notifications_disabled(actor.id, not enabled)

    def actor_notifications_enabled(self, actor: Actor) -> bool:
        if actor.mc_uuid:
            return self.store.player_notifications(actor.mc_uuid)
        return self.notifications_enabled(actor.id)

    # ------------------------------------------------------------------
    # Context (in-game location, player state, ...): team-only data
    # ------------------------------------------------------------------

    def can_see_context(self, actor: Actor) -> bool:
        return actor.privilege >= PRIV_TEAM

    @staticmethod
    def _context_source(actor: Actor) -> str:
        if actor.service:
            return f"service:{actor.service}"
        return f"discord:{actor.id}"

    def _check_context(self, actor: Actor, context: dict[str, object],
                       entry: Optional[Entry] = None) -> None:
        # Context describes where and how a report was made, so only trusted senders
        # (the game plugin's service token, or the team) may supply it
        if not actor.is_service and actor.privilege < PRIV_TEAM:
            raise Forbidden("Only services and team members can attach context")
        # A player (through a service) may only add to their own reports
        if entry is not None and actor.privilege < PRIV_TEAM and not self.is_author(actor, entry):
            raise Forbidden(f"You can only add context to your own {self.config.descriptor_plural}")
        sections, size = (0, 0) if entry is None else self.store.context_totals(entry.id)
        for name, data in context.items():
            if not _SECTION_RE.match(name):
                raise UserError(f"Bad context section name {name!r} (lowercase letters, digits, . _ -)")
            if not isinstance(data, dict):
                raise UserError(f"Context section {name!r} must be a JSON object")
            size += len(json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
        if sections + len(context) > MAX_CONTEXT_SECTIONS:
            raise UserError(f"At most {MAX_CONTEXT_SECTIONS} context sections per {self.single}")
        if size > MAX_CONTEXT_BYTES:
            raise UserError(f"At most {MAX_CONTEXT_BYTES >> 20} MB (bytes of JSON) of context per {self.single}")

    def add_context(self, actor: Actor, entry: Entry, context: dict[str, object]) -> None:
        """Attach more context sections to an existing entry."""
        self._require_writable(actor)
        self._check_context(actor, context, entry)
        now = self.now()
        with self.store.transaction():
            for section, data in context.items():
                self.store.add_context(entry.id, section, data, self._context_source(actor), now)

    def notifications_enabled(self, user_id: int) -> bool:
        return not self.store.notifications_disabled(user_id)

    def queue_game_notice(self, entry: Entry) -> bool:
        """For `send_notifications`: queue the in-game notice for an update to a player's
        report, which the game plugin shows when they next join. False if they opted out."""
        assert entry.author_mc_uuid is not None
        if not self.store.player_notifications(entry.author_mc_uuid):
            return False
        if entry.is_closed:
            what = f"was closed ({resolution_name(self.config, entry.resolution or '')})"
            if entry.close_reason:
                what += f": {entry.close_reason}"
        else:
            what = "was updated"
        self.store.add_notice(entry.author_mc_uuid, entry.id,
                              f"Your {self.single} #{entry.id} {what}", self.now())
        return True

    def mark_notified(self, actor: Actor, entry: Entry) -> None:
        with self.store.transaction():
            self.store.update(entry.id, pending_notification=False)
            self._event(entry.id, "notified", actor, new=entry.author_id or entry.author_mc_uuid)
        entry.pending_notification = False

    # ------------------------------------------------------------------
    # Tracking channel bookkeeping (no privilege checks: called by the bot)
    # ------------------------------------------------------------------

    def set_message_id(self, entry_id: int, message_id: Optional[int]) -> None:
        self.store.update(entry_id, message_id=message_id)

    def pruned(self, entry: Entry, message_id: int) -> None:
        """`prune` deleted the entry's tracking message. Only clears it while it is still that
        message: an entry reopened meanwhile may already have a new one."""
        self.store.clear_message_id(entry.id, message_id)
        entry.message_id = None
        current = self.store.get(entry.id)
        if current is not None and not current.is_closed:
            # Reopened while its message was being deleted: post it again
            self.store.mark_dirty(entry.id)
