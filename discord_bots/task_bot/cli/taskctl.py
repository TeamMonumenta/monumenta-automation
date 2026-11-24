#!/usr/bin/env python3
"""taskctl: command line client for a task bot's network API.

Stdlib only, so it needs no venv. It knows nothing about what the server
tracks: the words it prints ("bug", "suggestion", ...) come from the server's
/api/info. Point it at a server with environment variables:

    TASKCTL_URL     base URL (default http://localhost:8080)
    TASKCTL_TOKEN   token from the bot's `/<thing> api_token create` slash command

See cli/README.md for usage.
"""

# Command functions share the (client, args) signature
# pylint: disable=unused-argument

import argparse
import datetime
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Optional, cast

DEFAULT_URL = "http://localhost:8080"
DEFAULT_TIMEOUT = 60



class _NoRedirects(urllib.request.HTTPRedirectHandler):
    """urllib would send the token along to wherever a redirect points."""

    def redirect_request(self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> None:
        raise urllib.error.HTTPError(newurl, code, f"redirected to {newurl}; set TASKCTL_URL to that",
                                     headers, fp)


# Proxies are bypassed so $http_proxy can't make a reachable server look unreachable
_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}), _NoRedirects())


def check_url(url: str) -> None:
    """The token goes in every request, so only over https, except to this machine."""
    parts = urllib.parse.urlsplit(url)
    if parts.scheme == "https" or (parts.scheme == "http" and parts.hostname in ("localhost", "127.0.0.1", "::1")):
        return
    raise ApiError(f"TASKCTL_URL must be https:// (or http:// to localhost), not {url!r}")


class ApiError(Exception):
    def __init__(self, message: str, status: Optional[int] = None):
        super().__init__(message)
        self.status = status


class Client:
    def __init__(self, base_url: str, token: Optional[str], timeout: int = DEFAULT_TIMEOUT):
        check_url(base_url)
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self._info: Optional[dict[str, Any]] = None

    def raw(self, method: str, path: str, *, query: Optional[dict[str, Any]] = None,
            body: Optional[dict[str, Any]] = None) -> tuple[bytes, str]:
        url = self.base_url + path
        if query:
            pairs = [(k, str(v)) for k, v in query.items() if v is not None and v != "" and v != []]
            if pairs:
                url += "?" + urllib.parse.urlencode(pairs)
        data = json.dumps(body).encode("utf-8") if body is not None else None
        # Cloudflare in front of the public API refuses urllib's default User-Agent
        # ("error code: 1010")
        headers: dict[str, str] = {"User-Agent": "taskctl"}
        if data is not None:
            headers["Content-Type"] = "application/json"
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with _OPENER.open(req, timeout=self.timeout) as resp:
                return resp.read(), resp.headers.get_content_type()
        except urllib.error.HTTPError as e:
            message = f"HTTP {e.code}"
            raw_body = e.read()
            try:
                payload = json.loads(raw_body)
                if isinstance(payload, dict) and "error" in payload:
                    message = str(cast(dict[str, Any], payload)["error"])
            except (ValueError, TypeError):
                # Not one of our JSON errors: a proxy in the way, or not a task bot at all
                snippet = " ".join(raw_body[:200].decode("utf-8", "replace").split())
                message += f" from {self.base_url} (is TASKCTL_URL a task bot API?)"
                if snippet:
                    message += f": {snippet}"
            if e.code == 401 and not self.token:
                message += " (set TASKCTL_TOKEN)"
            raise ApiError(message, e.code) from e
        except TimeoutError as e:
            raise ApiError(f"request to {url} timed out after {self.timeout}s") from e
        except urllib.error.URLError as e:
            raise ApiError(f"could not reach {self.base_url}: {e.reason}") from e

    def call(self, method: str, path: str, *, query: Optional[dict[str, Any]] = None,
             body: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        data, _ = self.raw(method, path, query=query, body=body)
        return cast(dict[str, Any], json.loads(data)) if data else {}

    def info(self) -> dict[str, Any]:
        if self._info is None:
            self._info = self.call("GET", "/api/info")
        return self._info

    def word(self, key: str) -> str:
        return str(self.info()["descriptor"][key])


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

# A bare "m" could be minutes or months (chart periods use it for months), so it takes neither
_REL_RE = re.compile(r"^(\d+)(min|h|d|w|mo|y)$")
_REL_SECONDS = {"min": 60, "h": 3600, "d": 86400, "w": 7 * 86400, "mo": 30 * 86400, "y": 365 * 86400}


def parse_time(value: Optional[str], now: Optional[float] = None) -> Optional[int]:
    """'30min' / '12h' / '7d' / '2w' / '6mo' / '1y' ago, an ISO date or datetime (local
    time), or epoch seconds."""
    if value is None or value == "":
        return None
    now = now if now is not None else datetime.datetime.now().timestamp()
    m = _REL_RE.match(value.strip().lower())
    if m:
        return int(now - int(m.group(1)) * _REL_SECONDS[m.group(2)])
    if value.isdigit():
        return int(value)
    if re.match(r"^\d+m$", value.strip().lower()):
        raise SystemExit(f"taskctl: {value!r} could be minutes or months; use {value[:-1]}min or {value[:-1]}mo")
    try:
        return int(datetime.datetime.fromisoformat(value).timestamp())
    except ValueError:
        raise SystemExit(f"taskctl: can't understand time {value!r} (use 30min, 12h, 7d, 6mo, 2026-01-31 ...)") from None


def read_ids(args: list[str]) -> list[int]:
    """Entry numbers from args; '-' reads whitespace-separated numbers from stdin."""
    raw: list[str] = []
    for a in args:
        if a == "-":
            raw.extend(sys.stdin.read().split())
        else:
            raw.extend(a.replace(",", " ").split())
    ids: list[int] = []
    for r in raw:
        r = r.strip().lstrip("#")
        if not r:
            continue
        try:
            n = int(r)
        except ValueError:
            raise SystemExit(f"taskctl: {r!r} is not a number") from None
        if n not in ids:
            ids.append(n)
    if not ids:
        raise SystemExit("taskctl: no ids given")
    return ids


def read_id(arg: str) -> int:
    """One entry number, for commands that act on a single entry."""
    ids = read_ids([arg])
    if len(ids) > 1:
        raise SystemExit(f"taskctl: this command takes one id, not {arg!r}")
    return ids[0]


def fmt_time(ts: Optional[int], with_time: bool = False) -> str:
    if ts is None:
        return "?"
    d = datetime.datetime.fromtimestamp(ts)
    return d.strftime("%Y-%m-%d %H:%M" if with_time else "%Y-%m-%d")


def user_name(u: Optional[dict[str, Any]]) -> str:
    """A person's display name; Minecraft players (in-game reporters) are marked."""
    if not u:
        return "-"
    if u.get("kind") == "minecraft":
        return f"{u.get('name') or str(u.get('uuid'))[:8]} (in-game)"
    return str(u.get("name") or u.get("id"))


def one_line(text: str, width: int) -> str:
    text = " ".join(text.split())
    return text if len(text) <= width else text[:width - 3] + "..."


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def entry_line(e: dict[str, Any], width: int = 60) -> str:
    """One aligned line: fixed-width columns first, variable ones (labels, author, text) last."""
    state = e["status"] if e["status"] == "open" else (e.get("resolution_name") or "closed")
    pc = f"{e['priority']}/{e['complexity']}"
    created = fmt_time(e.get("created_at"))
    return (f"#{e['id']:<6} {state[:11]:<11} {pc:<16} {created:<11}  {one_line(e['description'], width):<{width}}  "
            f"[{','.join(e['labels'])}] {user_name(e.get('author'))}")


def entry_block(e: dict[str, Any], proper: str) -> str:
    lines = [f"{proper} #{e['id']}  [{','.join(e['labels'])}]  {e['priority']} / {e['complexity']}"]
    created = fmt_time(e.get("created_at"), with_time=True)
    lines.append(f"  author:   {user_name(e.get('author'))}, created {created}")
    if e.get("assignee"):
        lines.append(f"  assigned: {user_name(e['assignee'])}")
    if e["status"] == "closed":
        how = e.get("resolution_name") or "closed"
        who = f" by {user_name(e['closed_by'])}" if e.get("closed_by") else ""
        when = f" on {fmt_time(e['closed_at'], True)}" if e.get("closed_at") else ""
        lines.append(f"  closed:   {how}{who}{when}: {e.get('close_reason') or ''}")
        if e.get("duplicate_of"):
            lines.append(f"  duplicate of #{e['duplicate_of']}")
    else:
        lines.append("  status:   open")
    if e.get("duplicates"):
        lines.append("  duplicates: " + ", ".join(f"#{i}" for i in cast(list[int], e["duplicates"])))
    if e.get("reactions"):
        lines.append("  reactions: " + "  ".join(f"{r['emoji']} {r['count']}" for r in e["reactions"]))
    if e.get("link"):
        lines.append(f"  link:     {e['link']}")
    for url in cast(list[str], e.get("images") or []):
        lines.append(f"  image:    {url}")
    lines.append("")
    lines.extend("  " + line for line in str(e["description"]).splitlines())
    return "\n".join(lines)


def event_line(ev: dict[str, Any], with_entry: bool = False) -> str:
    when = fmt_time(ev.get("at"), True) if ev.get("at") else "(before new bot)"
    if ev.get("source") == "legacy" and ev.get("at"):
        # Imported, and the time is an estimate (README, "Imported history"): the day only,
        # in UTC as the bot shows it
        when = datetime.datetime.fromtimestamp(ev["at"], datetime.timezone.utc).strftime("%Y-%m-%d")
    who = user_name(ev.get("actor")) if ev.get("actor") else "?"
    what = ev["kind"]
    if ev["kind"] == "closed":
        what = f"closed as {ev.get('new')}" + (f": {one_line(ev['reason'], 80)}" if ev.get("reason") else "")
    elif ev["kind"] == "author":
        what = f"author {user_name(ev.get('old_user'))} -> {user_name(ev.get('new_user'))}"
    elif ev["kind"] in ("priority", "complexity", "labels"):
        what = f"{ev['kind']} {ev.get('old')} -> {ev.get('new')}"
    elif ev["kind"] == "appended" and ev.get("new"):
        what = "appended: " + one_line(str(ev["new"]), 80)
    elif ev["kind"] == "assigned":
        what = f"assigned to {user_name(ev.get('new_user'))}"
    src = {"discord": "", "legacy": " [imported]"}.get(str(ev.get("source")), f" [{ev.get('source')}]")
    prefix = f"#{ev['entry_id']:<6} " if with_entry else ""
    return f"{prefix}{when:<17} {who:<20} {what}{src}"


def print_json(obj: Any) -> None:
    print(json.dumps(obj, ensure_ascii=False))


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_info(c: Client, a: argparse.Namespace) -> int:
    info = c.info()
    if a.json:
        print_json(info)
        return 0
    d = info["descriptor"]
    me = info["me"]
    print(f"Server:      {c.base_url} ({d['plural']}, prefix {d['prefix']})")
    print(f"You:         {me['name']} (privilege {me['privilege']}{', read-only token' if me['read_only'] else ''})")
    print(f"Labels:      {', '.join(info['labels'])}")
    print(f"Priorities:  {', '.join(info['priorities'])}")
    print(f"Complexities:{' ' if info['complexities'] else ''}{', '.join(info['complexities'])}")
    print(f"Resolutions: {', '.join(info['resolutions'].values())}")
    print(f"Charts:      {', '.join(info['charts'])}")
    return 0


def _list_query(a: argparse.Namespace) -> dict[str, Any]:
    return {
        "status": a.status, "label": ",".join(a.label or []), "priority": ",".join(a.priority or []),
        "complexity": ",".join(a.complexity or []), "resolution": ",".join(a.resolution or []),
        "author": a.author, "author_player": a.author_player, "assignee": a.assignee,
        "closed_by": a.closed_by,
        "q": " ".join(a.q or []), "reason_contains": " ".join(a.reason_contains or []),
        "idle_since": parse_time(a.idle),
        "reaction": a.reaction,
        "created_after": parse_time(a.created_after), "created_before": parse_time(a.created_before),
        "closed_after": parse_time(a.closed_after), "closed_before": parse_time(a.closed_before),
        "sort": a.sort, "order": "desc" if a.desc else "asc",
    }


def cmd_list(c: Client, a: argparse.Namespace) -> int:
    query = _list_query(a)
    entries: list[dict[str, Any]] = []
    total = 0
    offset = a.offset
    remaining = a.limit if a.limit > 0 else None
    while True:
        page = 500 if remaining is None else min(500, remaining)
        resp = c.call("GET", "/api/entries", query={**query, "limit": page, "offset": offset,
                                                    "text": "1" if a.text else None})
        batch = cast(list[dict[str, Any]], resp["entries"])
        total = int(resp["total"])
        entries.extend(batch)
        offset += len(batch)
        if remaining is not None:
            remaining -= len(batch)
        if not batch or offset >= total or (remaining is not None and remaining <= 0):
            break
    if a.ids:
        for e in entries:
            print(e["id"])
    elif a.json:
        for e in entries:
            print_json(e)
    elif a.text:
        for e in entries:
            print(e["text"])
            print()
    else:
        for e in entries:
            print(entry_line(e))
        shown = f"{len(entries)} of {total}" if len(entries) < total else str(total)
        print(f"({shown} {c.word('single') if total == 1 else c.word('plural')})", file=sys.stderr)
    return 0


def _for_each(c: Client, ids: list[int], action: Any) -> int:
    """Run action(id) for each id; keep going past per-id API errors, report at the end."""
    failed: list[str] = []
    for n in ids:
        try:
            action(n)
        except ApiError as e:
            if e.status is None or e.status == 401:
                raise
            failed.append(f"#{n}")
            hint = " (--force closes it again)" if e.status == 409 and "already closed" in str(e) else ""
            print(f"taskctl: #{n}: {e}{hint}", file=sys.stderr)
    if len(ids) > 1 and failed:
        print(f"taskctl: {len(ids) - len(failed)} of {len(ids)} done; failed: {' '.join(failed)}", file=sys.stderr)
    return 1 if failed else 0


def cmd_get(c: Client, a: argparse.Namespace) -> int:
    proper = c.word("proper")
    first = [True]

    def show(n: int) -> None:
        e = c.call("GET", f"/api/entries/{n}", query={"text": "1" if a.text else None})
        if a.json:
            print_json(e)
        elif a.text:
            print(e["text"])
        else:
            if not first[0]:
                print()
            print(entry_block(e, proper))
        first[0] = False
    return _for_each(c, read_ids(a.ids), show)


def cmd_history(c: Client, a: argparse.Namespace) -> int:
    ids = read_ids(a.ids)
    # With several entries each line names its entry, and a blank line separates them
    several = len(ids) > 1
    first = [True]

    def show(n: int) -> None:
        events: list[dict[str, Any]] = c.call("GET", f"/api/entries/{n}/events")["events"]
        if a.json:
            for ev in events:
                print_json(ev)
            return
        if several and not first[0]:
            print()
        first[0] = False
        for ev in events:
            print(event_line(ev, with_entry=several))
    return _for_each(c, ids, show)


def cmd_redacted(c: Client, a: argparse.Namespace) -> int:
    print_json(c.call("GET", f"/api/entries/{read_id(a.id)}/redacted"))
    return 0


def cmd_images(c: Client, a: argparse.Namespace) -> int:
    n = read_id(a.id)
    images: list[dict[str, Any]] = c.call("GET", f"/api/entries/{n}/images")["images"]
    if a.json:
        for im in images:
            print_json(im)
        return 0
    if not images:
        print(f"{c.word('proper')} #{n} has no saved images", file=sys.stderr)
        return 0
    if a.list:
        for im in images:
            print(f"{im['name']}  {im['size'] or 0:>10}  {fmt_time(im['saved_at'], True)}  {im['url']}")
        return 0
    out = a.output or f"{c.word('single')}-{n}"
    os.makedirs(out, exist_ok=True)
    for im in images:
        data, _ = c.raw("GET", f"/api/entries/{n}/images/{urllib.parse.quote(im['name'])}")
        name = os.path.basename(str(im["name"]))
        if name in ("", ".", ".."):
            raise ApiError(f"the server sent an unusable image name {im['name']!r}")
        path = os.path.join(out, name)
        with open(path, "wb") as f:
            f.write(data)
        print(path)
    return 0


# The most events the server returns per call (MAX_LIMIT in taskbot/api.py)
EVENTS_PAGE = 1000


def cmd_activity(c: Client, a: argparse.Namespace) -> int:
    # Events come newest first; each further page asks for those below the lowest id so far,
    # until a short page says there are no more
    query = {"since": parse_time(a.since), "kind": ",".join(a.kind or []), "actor": a.actor}
    events: list[dict[str, Any]] = []
    remaining = a.limit if a.limit > 0 else None
    before_id: Optional[int] = None
    while remaining is None or remaining > 0:
        page = EVENTS_PAGE if remaining is None else min(EVENTS_PAGE, remaining)
        resp = c.call("GET", "/api/events", query={**query, "limit": page, "before_id": before_id})
        batch = cast(list[dict[str, Any]], resp["events"])
        if before_id is not None:
            # Only what is below the last page: a server that ignored before_id would
            # otherwise repeat pages forever
            batch = [ev for ev in batch if int(ev["id"]) < before_id]
        events.extend(batch)
        if remaining is not None:
            remaining -= len(batch)
        if len(batch) < page:
            break
        before_id = min(int(ev["id"]) for ev in batch)
    events.reverse()
    for ev in events:
        if a.json:
            print_json(ev)
        else:
            print(event_line(ev, with_entry=True))
    return 0


def _show_result(c: Client, a: argparse.Namespace, e: dict[str, Any], verb: str) -> None:
    if a.json:
        print_json(e)
    else:
        print(f"{c.word('proper')} #{e['id']} {verb}")


def cmd_add(c: Client, a: argparse.Namespace) -> int:
    text = " ".join(a.text) if a.text != ["-"] else sys.stdin.read()
    e = c.call("POST", "/api/entries", body={"description": text, "labels": a.label or []})
    _show_result(c, a, e, "created")
    return 0


def cmd_edit(c: Client, a: argparse.Namespace) -> int:
    body: dict[str, Any] = {}
    for key in ("description", "labels", "priority", "complexity", "author"):
        value = getattr(a, key)
        if value is not None:
            body[key] = value
    if not body:
        raise SystemExit("taskctl: nothing to change (--description, --labels, --priority, --complexity, --author)")
    e = c.call("PATCH", f"/api/entries/{read_id(a.id)}", body=body)
    _show_result(c, a, e, "updated")
    return 0


def cmd_append(c: Client, a: argparse.Namespace) -> int:
    e = c.call("POST", f"/api/entries/{read_id(a.id)}/append", body={"text": " ".join(a.text)})
    _show_result(c, a, e, "updated")
    return 0


def _simple(path: str, verb: str, body_of: Any = None) -> Any:
    def run(c: Client, a: argparse.Namespace) -> int:
        def act(n: int) -> None:
            e = c.call("POST", f"/api/entries/{n}/{path}", body=body_of(a) if body_of else {})
            _show_result(c, a, e, verb)
        return _for_each(c, read_ids(a.ids), act)
    return run


def _reason(a: argparse.Namespace) -> dict[str, Any]:
    return {"reason": str(a.reason or "")}


def _close_body(a: argparse.Namespace) -> dict[str, Any]:
    return {**_reason(a), "force": bool(a.force)}


cmd_fix = _simple("fix", "closed as fixed", _close_body)
cmd_reject = _simple("reject", "rejected", _close_body)
cmd_reopen = _simple("reopen", "reopened")
cmd_redact = _simple("redact", "redacted")
cmd_unassign = _simple("unassign", "unassigned")


def cmd_dupe(c: Client, a: argparse.Namespace) -> int:
    of = read_id(a.of)

    def act(n: int) -> None:
        e = c.call("POST", f"/api/entries/{n}/dupe", body={"of": of, "note": a.note or "",
                                                          "force": bool(a.force)})
        _show_result(c, a, e, f"closed as a duplicate of #{of}")
    return _for_each(c, read_ids(a.ids), act)


def cmd_assign(c: Client, a: argparse.Namespace) -> int:
    def act(n: int) -> None:
        e = c.call("POST", f"/api/entries/{n}/assign", body={"user": a.user} if a.user else {})
        _show_result(c, a, e, f"assigned to {user_name(e.get('assignee'))}")
    return _for_each(c, read_ids(a.ids), act)


def cmd_stats(c: Client, a: argparse.Namespace) -> int:
    s = c.call("GET", "/api/stats")
    if a.json:
        print_json(s)
        return 0
    print(f"Open {c.word('plural')}: {s['open']}    closed: {s['closed']} "
          f"({', '.join(f'{k} {v}' for k, v in s['closed_by_resolution'].items())})")
    grid = cast(dict[str, dict[str, int]], s["open_by_priority_complexity"])
    first_row: dict[str, int] = next(iter(grid.values())) if grid else {}
    comps = list(first_row.keys())
    print()
    print(f"{'':<10}" + "".join(f"{x:>10}" for x in comps) + f"{'total':>10}")
    for prio, row in grid.items():
        print(f"{prio:<10}" + "".join(f"{row.get(x, 0):>10}" for x in comps) + f"{sum(row.values()):>10}")
    print()
    print("Open by label: " + ", ".join(f"{k} {v}" for k, v in s["open_by_label"].items()))
    return 0


def cmd_authors(c: Client, a: argparse.Namespace) -> int:
    s = c.call("GET", "/api/stats/authors", query={"limit": a.limit})
    for row in s["authors"]:
        if a.json:
            print_json(row)
        else:
            print(f"{user_name(row['user']):<24} {row['total']:>6} ({row['open']} open)")
    return 0


def cmd_closers(c: Client, a: argparse.Namespace) -> int:
    s = c.call("GET", "/api/stats/closers", query={"days": a.days, "limit": a.limit})
    if a.json:
        print_json(s)
        return 0
    names = cast(dict[str, str], c.info()["resolutions"])
    keys = list(names)
    if not s["closers"]:
        period = f"in the last {a.days} days" if a.days else "overall"
        print(f"No closes recorded {period}.")
    else:
        print(f"{'':<24}" + "".join(f"{names[k]:>11}" for k in keys) + f"{'total':>8}")
    for row in s["closers"]:
        print(f"{user_name(row['user']):<24}" + "".join(f"{row[k]:>11}" for k in keys) + f"{row['total']:>8}")
    if s["self_closes"]:
        print(f"({s['self_closes']} closed by their own authors not counted)", file=sys.stderr)
    if s["unknown_closer"] and not a.days:
        print(f"({s['unknown_closer']} closed with no recorded closer)", file=sys.stderr)
    return 0


def cmd_chart(c: Client, a: argparse.Namespace) -> int:
    if not a.name:
        charts = c.info()["charts"]
        for name, summary in charts.items():
            print(f"{name:<10} {summary}")
        return 0
    query = {"options": " ".join(a.options)}
    if a.json:
        print_json(c.call("GET", f"/api/charts/{a.name}.json", query=query))
        return 0
    data, _ = c.raw("GET", f"/api/charts/{a.name}.png", query=query)
    out = a.output or f"{c.word('single')}-{a.name}.png"
    if out == "-":
        sys.stdout.buffer.write(data)
    else:
        with open(out, "wb") as f:
            f.write(data)
        print(out)
    return 0


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="taskctl", description="Query and update a task bot (bugs, suggestions, ...) from the terminal.",
        epilog="Server and token come from $TASKCTL_URL and $TASKCTL_TOKEN. Ids accept '-' to read from stdin.")
    p.add_argument("--url", help="server base URL (default $TASKCTL_URL or %(default)s)".replace(
        "%(default)s", DEFAULT_URL))
    p.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    sub = p.add_subparsers(dest="command", required=True, metavar="command")

    def add(name: str, func: Any, help_text: str, aliases: Optional[list[str]] = None) -> argparse.ArgumentParser:
        sp = sub.add_parser(name, help=help_text, description=help_text, aliases=aliases or [])
        sp.set_defaults(func=func)
        sp.add_argument("--json", action="store_true", help="print raw API JSON (one object per line)")
        return sp

    add("info", cmd_info, "show what the server tracks and who you are", ["whoami"])

    sp = add("list", cmd_list, "list entries (default: open ones, oldest first)", ["ls"])
    sp.add_argument("--status", choices=["open", "closed", "all"], default="open")
    sp.add_argument("-l", "--label", action="append", help="must have this label (repeatable; all must match)")
    sp.add_argument("-p", "--priority", action="append", help="any of these priorities")
    sp.add_argument("-c", "--complexity", action="append", help="any of these complexities")
    sp.add_argument("-r", "--resolution", action="append", help="fixed, rejected or duplicate (implies closed)")
    sp.add_argument("--author", help="user id, name prefix, or 'me'")
    sp.add_argument("--author-player", help="a Minecraft player's name or uuid (in-game reports)")
    sp.add_argument("--assignee", help="user id, name prefix, 'me', 'any' or 'none'")
    sp.add_argument("--closed-by", help="user id, name prefix, or 'me'")
    sp.add_argument("-q", action="append", help="words that must all appear in the description (repeatable)")
    sp.add_argument("--reason-contains", action="append", help="words that must all appear in the close reason (repeatable)")
    sp.add_argument("--idle", metavar="WHEN", help="no change since then (1y, 2026-01-31, ...)")
    sp.add_argument("--reaction", help="only entries with this reaction, most reacted first")
    for flag in ("created-after", "created-before", "closed-after", "closed-before"):
        sp.add_argument(f"--{flag}", metavar="WHEN", help="7d, 12h, 2026-01-31, ...")
    sp.add_argument("--sort", default="id", choices=["id", "priority", "created", "updated", "closed"])
    sp.add_argument("--desc", action="store_true", help="reverse the sort order")
    sp.add_argument("-n", "--limit", type=int, default=50, help="0 for all (default %(default)s)")
    sp.add_argument("--offset", type=int, default=0)
    out = sp.add_mutually_exclusive_group()
    out.add_argument("--ids", action="store_true", help="print only ids, one per line (for piping)")
    out.add_argument("--text", action="store_true", help="print each entry as Discord shows it")

    sp = add("get", cmd_get, "show entries in full", ["show"])
    sp.add_argument("ids", nargs="+", help="ids, or - for stdin")
    sp.add_argument("--text", action="store_true", help="print as Discord shows it")

    sp = add("history", cmd_history, "who changed entries and when")
    sp.add_argument("ids", nargs="+", help="ids, or - for stdin")

    sp = add("activity", cmd_activity, "recent changes across all entries")
    sp.add_argument("--since", default="7d", help="default %(default)s")
    sp.add_argument("--kind", action="append", help="created, closed, reopened, assigned, ... (repeatable)")
    sp.add_argument("--actor", help="user id, name prefix, or 'me'")
    sp.add_argument("-n", "--limit", type=int, default=200, help="0 for all (default %(default)s)")

    sp = add("add", cmd_add, "create an entry as yourself")
    sp.add_argument("-l", "--label", action="append")
    sp.add_argument("text", nargs="+", help="description, or - for stdin")

    sp = add("edit", cmd_edit, "change fields of an entry")
    sp.add_argument("id")
    sp.add_argument("-d", "--description")
    sp.add_argument("-l", "--labels", help="comma separated, replaces the current labels")
    sp.add_argument("-p", "--priority")
    sp.add_argument("-c", "--complexity")
    sp.add_argument("--author", help="user id or name prefix")

    sp = add("append", cmd_append, "append text to an entry's description")
    sp.add_argument("id")
    sp.add_argument("text", nargs="+")

    sp = add("fix", cmd_fix, "close entries as fixed")
    sp.add_argument("ids", nargs="+")
    sp.add_argument("--reason", help='default "Fixed"')
    sp.add_argument("--force", action="store_true", help="also re-close entries that are already closed")

    sp = add("reject", cmd_reject, "close entries as rejected")
    sp.add_argument("ids", nargs="+")
    sp.add_argument("--reason", required=True)
    sp.add_argument("--force", action="store_true", help="also re-close entries that are already closed")

    sp = add("dupe", cmd_dupe, "close entries as duplicates of another")
    sp.add_argument("ids", nargs="+")
    sp.add_argument("--of", required=True, help="the original entry")
    sp.add_argument("--note")
    sp.add_argument("--force", action="store_true", help="also re-close entries that are already closed")

    sp = add("reopen", cmd_reopen, "reopen closed entries", ["unfix"])
    sp.add_argument("ids", nargs="+")

    sp = add("assign", cmd_assign, "assign entries (to yourself by default)")
    sp.add_argument("ids", nargs="+")
    sp.add_argument("--user", help="user id or name prefix")

    sp = add("unassign", cmd_unassign, "unassign entries")
    sp.add_argument("ids", nargs="+")

    sp = add("redact", cmd_redact, "hide entries' text from everyone but the team")
    sp.add_argument("ids", nargs="+")

    sp = add("redacted", cmd_redacted, "show what redaction hid (team only)")
    sp.add_argument("id")

    sp = add("images", cmd_images, "download the saved copies of an entry's images")
    sp.add_argument("id")
    sp.add_argument("-o", "--output", help="directory to write to (default <thing>-<id>)")
    sp.add_argument("--list", action="store_true", help="only list them")

    add("stats", cmd_stats, "open entries by priority, complexity and label")
    sp = add("authors", cmd_authors, "who reported the most")
    sp.add_argument("-n", "--limit", type=int, default=25)
    sp = add("closers", cmd_closers, "who closed the most")
    sp.add_argument("--days", type=int, help="only the last N days")
    sp.add_argument("-n", "--limit", type=int, default=25)

    sp = add("chart", cmd_chart, "render a chart to a PNG (no name: list charts)")
    sp.add_argument("name", nargs="?")
    sp.add_argument("options", nargs="*", help="e.g. 2y priority plugin")
    sp.add_argument("-o", "--output", help="file to write, - for stdout (default <thing>-<name>.png)")
    return p


def main(argv: Optional[list[str]] = None, env: Optional[dict[str, str]] = None) -> int:
    env = dict(os.environ) if env is None else env
    args = build_parser().parse_args(argv)
    try:
        client = Client(args.url or env.get("TASKCTL_URL") or DEFAULT_URL, env.get("TASKCTL_TOKEN"),
                        args.timeout)
        return int(args.func(client, args))
    except ApiError as e:
        print(f"taskctl: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130
    except BrokenPipeError:
        return 0


if __name__ == "__main__":
    sys.exit(main())
