# Network API

`main.py` serves `/api/*` next to the Discord bot on two ports: `api_port` (default 8080),
which the ingress exposes and which accepts only Discord users' tokens, and 8081,
reachable only inside the cluster and accepting only service tokens. The
`taskctl` client ([cli/README.md](cli/README.md)) wraps all of it.

```bash
curl -H "Authorization: Bearer $TASKCTL_TOKEN" 'https://bugs-api.playmonumenta.com/api/entries?label=quest&limit=5'
```

The public hostnames are behind Cloudflare, which refuses some default client signatures
(Python's `urllib` among them) with a 403 reading "error code: 1010"; send a
`User-Agent` of your own, as `taskctl` does.

## Access

Every route except `GET /api/health` needs `Authorization: Bearer <token>`. Bug reports can
describe exploits, so reads are protected too.

The API is for the team: only members with privilege 2 or more can mint a token, and a
token stops working if its owner drops below that. Players reach the tracker in Discord or
through the game plugin (service tokens, below). Tokens are minted with the ephemeral
slash command `/<descriptor> api_token create [lifetime_days] [read_only]` (for example
`/bug api_token create`) and all of a user's tokens are revoked with `... revoke`. A token
is shown once; only its SHA-256 is stored. Each user may hold 20 live tokens.

On every request the token's owner must still be in the guild, able to see the feed
channel and on the team, so someone who leaves or loses access loses the API too (`403`).
Requests act with exactly the privileges the owner has in Discord at that moment, computed
from their roles the same way as for text commands. A `read_only` token can't change
anything.

History (`/events`), closer statistics and charts are team-only, as in Discord; that
matters only for players acting through a service token.

### Service tokens

Other programs, mainly the game plugin on the shards ([plugin/README.md](plugin/README.md)),
use service tokens instead. They are long-lived (ten years by default), belong to a named
service rather than a Discord user, and are managed with direct access to the database:

```bash
kubectl exec deploy/bug-bot -- python -m taskbot.tokens create shards-play [--max-privilege N (default 2)] [--days N] [--read-only]
kubectl exec deploy/bug-bot -- python -m taskbot.tokens list      # never shows the tokens themselves
kubectl exec deploy/bug-bot -- python -m taskbot.tokens revoke shards-play
```

Service tokens are only accepted on the internal port, and users' tokens only on the
public one; the other gets `403`. A request with a service token acts as the service
itself, with no privilege and only reading (enough for the instance's wording), or, when
it carries these headers, as a Minecraft player:

| Header | |
|---|---|
| `X-Taskbot-Player` | The player's uuid. |
| `X-Taskbot-Player-Name` | Their current name, remembered for display. |
| `X-Taskbot-Privilege` | The privilege level the service grants this player for this request (default 0), capped at the token's `--max-privilege`. |

The service decides what each player may do (the plugin uses permission nodes); the bot
applies the same rules as in Discord at the granted level, including ownership: a player
may always change reports they filed themselves. Changes are attributed to the player.
Shards reach the bot at `http://bug-bot.default.svc.cluster.local:8081`. Player names are
recorded only from requests other than `GET`, and each player may make at most 20
changes a minute (`429` past that; taking notices doesn't count).

Plain HTTP inside the cluster; the ingress terminates TLS. Don't expose the port any other
way, since tokens travel in a header.

## Conventions

- Bodies are JSON objects; list responses wrap the list
  (`{"entries": [...], "total": N}`).
- Times are epoch seconds. Discord ids are strings (they don't fit a JavaScript number). A
  person is either a Discord user, `{"kind": "discord", "id": "...", "name": "..."}`
  (`name` null when Discord doesn't know them), or a Minecraft player,
  `{"kind": "minecraft", "uuid": "...", "name": "..."}`. Authors, closers and event actors
  can be either.
- Optional fields are present as null rather than missing.
- Errors are `{"error": "..."}` with `400` (bad input), `401` (no or bad token), `403`
  (not allowed), `404` (unknown entry or route), `409` (conflict, e.g. already
  unassigned), `429` (too many changes from one player), `500`, or `503` for user tokens
  in the first moments after the bot starts, before it knows who is in the Discord server.
  Permission and validation messages are the same text Discord users see.
- Labels, priorities and complexities accept unambiguous abbreviations, as in Discord.
  Resolutions accept their key (`fixed`, `rejected`, `duplicate`), the instance's display
  name (`implemented` on the suggestion bot) or an abbreviation of either.
- Stored users (an author, an assignee) must be users Discord knows; filters accept any
  id, since many old authors have left.

## Endpoints

| Method | Path | Notes |
|---|---|---|
| `GET` | `/api/health` | `{"ok": true}`, no token needed. |
| `GET` | `/api/info` | What the instance tracks (`descriptor` words, vocabularies, resolutions with display names, charts) and who you are (`me`: id, name, privilege, read_only). Clients should take their wording from here. |
| `GET` | `/api/entries` | See query parameters below. |
| `GET` | `/api/entries/<id>` | One entry. `?text=1` adds `text`, the entry exactly as Discord shows it. |
| `GET` | `/api/entries/<id>/events` | Its history, oldest first. |
| `GET` | `/api/events` | Recent changes across all entries, newest first (by event id, which for events imported from the old bot is not time order): `since`, `until`, `kind` (comma separated), `actor`, `limit` (<= 1000, default 100), `before_id` for paging. |
| `POST` | `/api/entries` | `{"description", "labels"?, "context"?}`. Created as the caller (a Discord user, or a player through a service token); `context` (named sections of JSON, at most 32 and 10 MB) only from services and the team. The same checks as `add`: at least 5 words, at most 1600 characters, no pings, known labels (none means `misc`). `201`. |
| `PATCH` | `/api/entries/<id>` | Any of `description`, `labels` (list or comma separated), `priority`, `complexity`, `author`. Permission is checked for every field before anything changes: description and labels need ownership or level 1, the rest level 2. |
| `POST` | `/api/entries/<id>/append` | `{"text"}` |
| `POST` | `/api/entries/<id>/fix` | `{"reason"?, "force"?}`, default reason "Fixed". |
| `POST` | `/api/entries/<id>/reject` | `{"reason", "force"?}` |
| `POST` | `/api/entries/<id>/dupe` | `{"of", "note"?, "force"?}` |
| `POST` | `/api/entries/<id>/reopen` | `409` if it isn't closed. |
| `POST` | `/api/entries/<id>/assign` | `{"user"?}`: id, name prefix or `me`; default the caller. Level 2. |
| `POST` | `/api/entries/<id>/unassign` | Level 2. `409` if not assigned. |
| `POST` | `/api/entries/<id>/redact` | The `redact` command: hides the entry's text, images and the text in its history from everyone but the team. Again on a redacted entry, it hides what was added since (`409` if nothing was). Level 1. |
| `GET` | `/api/entries/<id>/redacted` | What redaction hid: `{redacted_at, redacted_by, description, close_reason, images, events: [{id, kind, at, old, new, reason}]}`. Privilege 2 (team) only. Entries redacted the old way (description edited to "redacted") have only `images`, with `redacted_at` 0 and `redacted_by` null. |
| `GET` | `/api/entries/<id>/images` | Saved copies of the entry's images, including replaced and redacted ones (README, "Images"): `{"images": [{name, url, size, saved_at}]}`. A redacted entry's only for the team. |
| `GET` | `/api/entries/<id>/images/<name>` | One saved image, as a file download. |
| `GET` | `/api/entries/<id>/context` | Context attached to the entry: `{"context": [{id, section, created_at, source, size, data}]}`. Privilege 2 (team) only. |
| `POST` | `/api/entries/<id>/context` | `{"<section>": {...}, ...}` adds sections. The team, or a player (through a service) on their own reports. |
| `POST` | `/api/players/<uuid>/notices/take` | The player's undelivered update notices, `{"notices": [{id, entry_id, text, created_at}]}`, marked delivered as they are returned (the game plugin shows them as the player joins). Service tokens only, and only for the player the request is made for. |
| `GET`, `POST` | `/api/players/<uuid>/settings` | `{"notifications": bool}`: in-game notices on or off. Service tokens only. |
| `GET` | `/api/users?q=` | Resolve a name prefix or id to a user, with Discord's "multiple users match" error. |
| `GET` | `/api/stats` | Open/closed counts, open by priority x complexity and by label, closed by resolution. |
| `GET` | `/api/stats/authors` | Top reporters: `limit`. |
| `GET` | `/api/stats/closers` | Top closers: `days`, `limit`. Also `self_closes` (authors closing their own) and `unknown_closer` (closes with no recorded closer, all of them imported). |
| `GET` | `/api/charts` | Available charts. |
| `GET` | `/api/charts/<name>.png` | The chart image; `options` takes the same words as `~bug chart` (`2y priority`). |
| `GET` | `/api/charts/<name>.json` | The data behind the chart: `kind` (`timeseries`, `bar`, `hbar`, `hbar_stacked`), `title`, `notes`, `colors` (series name to color) and either `times` (Unix seconds; bucket starts, except the backlog's, which are the instants counted, the last being now) with `series` and `stacked` (`area`, `bars` or absent), or `categories` with `values` or `series`. |

Closing an entry that is already closed returns `409` unless `force` is true, since it
replaces who closed it and when (the Discord commands still allow it, as before).

Events about users (`assigned`, `unassigned`, `author`) also carry `old_user` and
`new_user` objects next to the raw ids.

Calls that change an entry return the updated entry. They go through the same code as the
Discord commands, so the tracking channel message is updated within a few seconds, and a
line saying what changed, such as `Combustible rejected bug #123: can't reproduce`, is
posted to the feed channel, so that channel stays a complete log of changes. Lines are
gathered for a minute, and the same change to several entries shares one (`Combustible
fixed bugs #123, #125: Fixed`), so a bulk change makes only a few. Appends show the whole
description as it now reads. An entry redacted or purged before its lines go out has its
text (reasons, notes, descriptions) left out of them. Lines already posted are not changed
by a later redaction: they name the entry, and are deleted by hand like the reporter's own
messages. Changes from the game plugin (service tokens) and slash commands, whose replies
only their user sees, get the same lines. The lines don't say where a change came from,
which doesn't matter to readers; the entry's history has it.

### `GET /api/entries` parameters

| Parameter | Values |
|---|---|
| `status` | `open` (default), `closed`, `all` |
| `label` | all must match; repeat or comma separate |
| `priority`, `complexity`, `resolution` | any may match |
| `author`, `closed_by` | user id, name prefix or `me` |
| `author_player` | a Minecraft player's uuid or name, or `me` for a request made for a player |
| `assignee` | user id, name prefix, `me`, `any` or `none` |
| `q` | words that must all appear in the description (case-insensitive) |
| `reason_contains` | the same, for the close reason |
| `idle_since` | epoch seconds: only entries with no event since then (any change or creation; `send_notifications` telling the author doesn't count) |
| `reaction` | only entries with this reaction, most first |
| `created_after`, `created_before`, `closed_after`, `closed_before` | epoch seconds |
| `sort` | `id` (default), `priority` (the bot's priority x complexity order), `created`, `updated`, `closed` |
| `order` | `asc` (default) or `desc` |
| `limit`, `offset` | default 50, at most 1000 |
| `text` | `1` to include the Discord rendering |

`total` counts every match, regardless of `limit` and `offset`.

Each entry has `id, description, labels, priority, complexity, status, resolution,
resolution_name, close_reason, closed_at, closed_by, duplicate_of, duplicates, author,
assignee, created_at, updated_at, redacted, pending_notification, link, images,
reactions`. `duplicates` lists the entries closed as duplicates of this one, oldest first.
`closed_at` is set on every closed entry; for old closes the feed doesn't cover, it is the
creation time, or for some the time of their last event in the feed (see the README,
"Imported history"). `created_at` is the best known time; for bugs
below about #720 it only means "on or before" (see the README).

### Context

Context is data about an entry that is kept out of the public channel: where an in-game
report was made, and later perhaps the player's equipment or quest state. It is a list of
named sections (lowercase names such as `location`), each a JSON object, so a new kind of
context needs no change to the bot. An entry holds at most 32 sections and 10 MB of
context (UTF-8 JSON). The team can add it to any entry, players (through a service) only
to their own; only the team (privilege 2) can read it.
In Discord it is shown only through the ephemeral `/<descriptor> context` slash command,
never in a channel. Redaction keeps it; `purge` (Discord only, leads) deletes it with the
entry.
