# Database schema

One SQLite database per instance (`tasks.db`), in WAL mode with `secure_delete` on so
purged text doesn't linger in free pages. The schema version is `PRAGMA user_version`
(currently 1); `taskbot/db.py` holds the DDL and applies migrations in order, each in one
transaction. Version 1 is what the production databases were created with, so it never
changes; a schema change is a new migration (the docstring of `taskbot/db.py` says how).
The bot never creates the database; `python -m taskbot.db init` makes an empty one.
Production data from before 2026-11-23 was imported from the old bot at the cutover
(README, "Imported history"), which explains the `legacy` and `backfill` rows below.
Times are epoch seconds; Discord ids are stored as integers.

## entries

One row per bug or suggestion. `id` is the public number and is never reused: the next
number is kept in `meta.next_index` rather than derived from `MAX(id)`.

| Column | Meaning |
|---|---|
| `description`, `author_id`, `priority`, `complexity` | As before. `author_id` 0 means unknown (127 early bugs). |
| `status` | `open` or `closed`. |
| `resolution` | NULL while open; `fixed`, `rejected` or `duplicate`. |
| `close_reason` | The text shown after "Closed:". |
| `closed_at`, `closed_by` | Set when an entry is closed. For imported closes the old feed channel doesn't cover, `closed_at` is the creation time (or, for some, the time of their last event in the feed: the cutover's estimate, so statistics have no gap) and `closed_by` is NULL. |
| `author_mc_uuid`, `closed_by_mc_uuid` | For in-game activity: the Minecraft player who filed or closed the entry (`author_id` / `closed_by` are then 0 / NULL). |
| `duplicate_of` | The original, for duplicates (for imported entries, recovered from reasons like "dupe of 123" when that number exists). |
| `assignee_id` | Current assignee. |
| `redacted` | 1 after `redact`. Separate from the resolution, so redacting a fixed entry doesn't hide the fix from statistics. |
| `message_id` | The tracking channel message; NULL when there is none. `prune` clears it as it deletes the message, publishing clears it when the message has gone, and the reaction sweep (which re-reads every tracking message in turn) clears it for closed entries whose message has disappeared and reposts open ones. |
| `pending_notification` | Same rule as before: set by others' changes, cleared by the author's own and by `send_notifications`. |
| `created_at` | The best known time. Exact when recorded by this bot or recovered from the old feed channel, which covers all but about 1,200 imported entries. Of those, the first ~500 suggestions have the day from their text and most others are within a day; bugs below about #720, imported in April 2019 from older channels, only mean "on or before" (see README). |
| `updated_at` | Last change. |
| `channel_dirty` | Non-zero while the tracking message still has to be sent or edited: every change adds one, and the bot clears it after publishing only if it hasn't changed meanwhile (otherwise it publishes again). |
| `reactions_checked_at` | When the reaction counts were last read from the tracking message. |

`entry_labels(entry_id, label, position)` holds labels in their given order, which shows
in the rendering (`[quest,boss - High]`). `entry_images` holds images in order, with the
attachment id parsed out of Discord CDN URLs (only those can be refreshed) and the most
recently refreshed signed URL with its expiry.

## Identities

People are Discord users (integer ids, in `author_id`, `closed_by`, `assignee_id`,
`events.actor_id`) or Minecraft players (uuids, in the `*_mc_uuid` columns), never mixed
in one column. The exception is the free-form values of events: an `author` event's old
value and a `notified` event's value are whichever the author had, an id or a uuid. No
accounts are linked yet. Every question of whether two of these are the same person for
permissions (is this the author, may they edit or close it) is asked through
`taskbot/identity.py`. When a Discord to Minecraft link exists, a `LinkResolver` over it
makes ownership work across both accounts with no other change, and players who never link
keep working. A few places still treat the two kinds of account separately and would want
a look then: filters by author (`asearch`, the API's `author` and `author_player`),
statistics (which group by `discord:<id>` / `mc:<uuid>` keys, so a linked person appears
twice and closing one's own report under the other account counts as a close), where
`send_notifications` delivers (by which column is set), and the separate notification
opt-outs.

## Vocabularies

Priorities and complexities are the same fixed lists for every instance, in
`taskbot/vocab.py`, since they have never changed. Labels differ between the bug and
suggestion instances and change with `addlabel` / `dellabel`, so they are a table,
`labels(name, position, active)`, always including `misc`, the label of entries filed
without one. Order matters for all three:
abbreviations are matched in this order, and `stats` prints rows in it. `dellabel` sets
`active = 0` (and removes the label from every entry, as before) so old history still
makes sense; `addlabel` of a removed label re-activates it at the end. Labels found on
imported entries but not in the old bot's label list (the 78 bugs labeled `suggestion`)
are inactive.

## events

The history, added to and never edited except by redaction (which blanks the text, below)
and purge (which deletes the entry): `entry_id, at, actor_id, kind, old_value, new_value,
reason, source, source_ref`. Values are text, JSON for lists. `source` is `discord`,
`api`, `legacy` (imported from the old bot's JSON at the cutover), `backfill` (recovered
from the old feed channel at the cutover); the schema also allows `system`, which nothing
writes. `source_ref` is the Discord message id of the command (for `backfill`, the bot's
reply when the command message was deleted), `interaction:<id>` for a slash command, or
`api:<request id>`.

| kind | old -> new |
|---|---|
| `created` | new: description (NULL in `legacy` events, some `backfill` ones, and after redaction) |
| `description`, `priority`, `complexity`, `author` | previous -> new value |
| `labels`, `image` | previous -> new list |
| `appended` | new: appended text |
| `closed` | previous resolution -> new resolution; `reason` is the close reason |
| `reopened` | old: the resolution that was undone |
| `assigned`, `unassigned` | previous -> new assignee (`unassigned` with reason `closed` when a close dropped it) |
| `redacted`, `notified` | |

Imported entries got a `created` event at the estimated time and, when closed or
redacted, a `closed` event at the estimated close time with no actor and a `redacted`
event with no time or actor, all `source='legacy'`. Where the old feed channel covered an
entry, its full history replaced those (`source='backfill'`), in time order; `legacy`
events remain only for what the feed didn't show. Event ids follow the order events were
written, so the imported ones don't follow time order. Only how history is shown
(`history`, taskctl) depends on where an event came from.

Redaction moves the text out of sight rather than destroying it: the description, close
reason, images and the values and reasons of the entry's earlier events are copied to
`redacted_content` and blanked everywhere else, so nothing that prints entries (the
channels, search, notifications, history) can show them; in-game notices about the entry
are deleted, since they quote its close reason. Redacting again adds whatever was written
since to what the first redaction kept. Only the team reads them back, privately (the API
and a slash command). `purge` deletes the entry row and with it everything attached
(events, images, context, redacted content); its number is not reused.

Closer statistics read `entries.closed_by`, the current state, so an entry that was
closed, reopened and closed again counts once.

## Other tables

| Table | Purpose |
|---|---|
| `reactions(entry_id, emoji, count, updated_at)` | Reaction counts per tracking message, in Discord's order. Updated from reaction events and replaced whenever the message is read. |
| `notifications_disabled(user_id)` | `notify off`. |
| `api_tokens(token_hash, discord_id, scope, created_at, expires_at, service, max_privilege, last_used_at)` | SHA-256 of each token, never the token. `scope` is `read` or `write`. Service tokens have `service` set, `discord_id` 0, and the most privilege they may grant. |
| `players(uuid, name, updated_at)` | Last known name of each Minecraft player seen. |
| `player_settings(uuid, notifications)` | In-game `notify off`. |
| `player_notices(id, uuid, entry_id, text, created_at, delivered_at)` | Update notices for in-game reporters, queued by `send_notifications` and marked delivered when the game plugin takes them (as the player joins a shard). At most one undelivered per player and entry. |
| `entry_context(id, entry_id, section, created_at, source, data)` | Team-only context: named sections, each a JSON object (at most 32 sections and 10 MB of JSON per entry). `source` says who supplied it (`service:shards-play`). Redaction keeps it; `purge` deletes it. |
| `image_files(entry_id, url, path, size, checked_at, missing, failures, message_id)` | Copies of images saved to disk (README, "Images"), one per entry and URL, for current, replaced and redacted images alike. `path` is relative to `images/`, NULL until saved. `missing` is 1 when Discord no longer had the image (it is not tried again); `failures` counts other failed downloads, retried an hour later per failure, at most a day. `message_id` is the bot's own feed channel message holding that URL, when it posted it (slash command images, `reupload`); for a redacted entry the bot deletes it and clears this only once Discord confirms. `purge` deletes the rows and files. |
| `redacted_content(entry_id, redacted_at, redacted_by, data)` | What `redact` hid, as JSON: `description`, `close_reason`, `images` and the hidden values of `events`. Team only. Entries the old bot's users redacted by editing the description to "redacted" have only their `images` here, with `redacted_at` 0. |
| `meta(key, value)` | `next_index`, and `slash_commands_sha256`: the slash commands as last registered with Discord, so the bot syncs them only when they change. |
