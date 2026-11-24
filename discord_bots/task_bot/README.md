# Task bot

The Discord bot that tracks Monumenta's bug reports and suggestions. Players file
entries with `~bug add ...` / `~suggestion add ...` in a feed channel; the bot keeps one
message per entry in a tracking channel, and the team triages them with text commands.
The same code runs both instances; everything that differs between them is in each
instance's `config.yml`.

Alongside the bot, the same process serves a network API (`/api/*`, see [API.md](API.md))
for scripts, agents and the `taskctl` command line client ([cli/README.md](cli/README.md)),
and for the game: the Paper plugin in [plugin/](plugin/README.md) lets players file and
follow reports in game (`/bug report ...`), using a service token.
Data lives in SQLite; [SCHEMA.md](SCHEMA.md) describes the tables.

## What it does

Every command from the original bot works as before, with the same abbreviations and
replies (`~bug f 123`, `~bug search quest hi`, interactive `isearch` sessions, ...). Type
`~bug` alone for the list. New since the rewrite:

| Command | What it does |
|---|---|
| `~bug dupe <n> <original> [note]` | Closes n as a duplicate of the original, linking them. The reason is "Duplicate of #original", followed by the note if there is one; a note that already names the original ("Dupe of 123", "Combined into 123") is the reason by itself. Same permission as `reject`. Also works inside interactive sessions. |
| `~bug reject <n> dupe of <original>` | People rejected duplicates this way before `dupe` existed, so `reject` and `fix` read the reason: one that says duplicate ("dupe of #123", "same issue as 123") closes as a duplicate, linked to the original when the reason names an entry that exists. `fix` does so only when an original is named. The reason is kept as typed, and the reply says it was closed as a duplicate. The same applies through slash commands, the API and in game. |
| `~bug history <n>` | Who changed an entry and when. |
| `~bug cstats [days] [minimum]` | Who closed the most entries, split into fixed / rejected / duplicate. Authors closing their own entries are counted separately. Overall (no days, or 0) lists only people with at least 20 closes, since most closers have a handful; a minimum overrides that. |
| `~bug chart [name] [options]` | Posts a chart (backlog, intake, closes, closers, age, labels). Without a name, lists them. Options pick the period (`90d`, `2y`, `all`) and the bucket (`week`, `month`). The backlog is stacked by complexity, or by priority with `priority`, and a label name limits it to entries with that label (`backlog plugin`). Intake is split by label (each entry under its first label other than misc), closes and closers by resolution. |
| `~bug redact <n>` | Hides an entry's text, close reason, images and the text in its history from everyone but the team (replaces `delete`, which now only points here). Anything added to a redacted entry afterwards (an edit, an append, a close reason) shows as usual until it is redacted again. Messages already in the feed channel that quote the entry (the reporter's own, and the bot's change lines) have to be deleted by hand. Level 1. |
| `~bug purge <n>` | Leads: deletes an entry for good, with its history, saved images and anything redacted. Asks for `purge <n> confirm`. |
| `~bug reupload <n>` | Team: posts the saved copies of an entry's images in the feed channel and shows those from then on, for when Discord has lost an image (its message was deleted). Never for a redacted entry. |
| `/bug <command>` | Slash versions of the commands, replying only to whoever uses them (see "Slash commands" below). |
| `/bug context <n>`, `/bug redacted <n>` | Team only, and only visible to whoever asks: the context attached to an entry (such as where an in-game report was made), and what redaction hid, with the saved copies of its images attached. (`~bug context` points here, since the feed channel is public.) |
| `/bug api_token create` / `revoke` | Team only: mint or revoke a token for the API. |

`history`, `cstats` and `chart` are for the team (privilege 2), as is the API.

Other differences, all deliberate:

- Every change is recorded with who made it and when, so there are closer statistics and
  a history (recovered back to 2019 for older entries; see "Imported history"). Closes
  are recorded as fixed, rejected or duplicate rather than only free text.
- An entry that others were closed as duplicates of lists them on a line after its
  description (`Duplicates: #12, #40`) in the tracking channel and in replies, and
  `taskctl` shows them too. The line is left out when the message would go over Discord's
  2000 characters.
- `edit <n> author <user>` works (it was a stub).
- `~bug` alone shows the same commands to everyone; team members get one more line
  pointing to `~bug help team`, which lists the team's, leads' and owner's commands.
- An `edit` that changes nothing (setting the labels an entry already has) gets the usual
  reply but is not recorded: no history, no notification, no repost.
- Several images can be attached to an entry. Discord CDN links expire now; the bot asks
  Discord for fresh links whenever it shows an image.
- Images are kept even when Discord loses them; see "Images" below.
- `rsearch` is instant: reaction counts are kept in the database from Discord's reaction
  events, and re-read from each tracking message in the background.
- Text fields can't contain pings anywhere (before, only `add` checked), and the bot never
  pings except for `send_notifications` and `ping_assigned`.
- Mentions of `bug-123` in the discussion channel skip numbers that don't exist instead of
  ignoring the whole message.
- An edit to a closed entry whose tracking message was pruned no longer posts it back
  into the tracking channel.
- When Discord refuses to update an entry's tracking message, the bot says so in the feed
  channel (one line for all it refused at once) and tries again when the entry next
  changes. When Discord is down it waits, longer each time up to 15 minutes, and catches
  up once it is back; commands still update their entry's message straight away.
- `import` (dead since a discord.py upgrade), the Kanboard integration and its commands
  are gone. `sync` only says it is no longer needed.
- Priorities and complexities are the same for both instances (`taskbot/vocab.py`), so
  suggestions can be Critical too. Labels still differ and change with `addlabel`.
- A new entry's description needs 5 words of its own; labels typed before it don't count.
- Close reasons are limited to 1000 characters, text can't contain control characters, and
  `unfix` on an open entry says it isn't closed instead of marking it changed.

## Slash commands

`/bug` (and `/suggestion`) run the same handlers as the text commands, so permissions and
replies are the same, but the replies go only to whoever used them. Discord allows 25
subcommands, so related ones are grouped:

- `report`, `get`, `notify`, `append`, `fix`, `reject`, `dupe`, `reopen`, `redact`,
  `assign`, `unassign`, `history`, `send_notifications` (posts in the feed channel),
  `purge`, `reupload`, `context`, `redacted`, `api_token`
- `search labels`, `search description` (was the top-level `/bug_description_search`),
  `search author`, `search reaction`, `search assigned` (`list_assigned`)
- `edit description`, `edit labels`, `edit image`, `edit priority`, `edit complexity`
- `stats open`, `stats authors`, `stats closers` (`cstats`), `stats chart`

`report`, `edit description` and `append` open a form with a multi-line text box (and, for
reports, a pick-list of labels), since command options are a single line. If the bot
refuses what was typed, the reply gives the text back to copy. A form left open for more
than an hour, or across a restart of the bot, can't be sent.

Since nobody else sees the replies, changes made with slash commands get a line in the
feed channel saying what changed (`Combustible fixed bug #12: works now`), as API
changes do, so the channel stays a complete log. The bot registers the commands with
Discord when it starts, only when they have changed, so `~bug sync` is no longer needed.

## Images

Discord keeps an attachment only as long as the message it was posted with, and its links
are signed and stop working after a day. The bot asks for freshly signed links whenever it
posts or edits a message, and Discord re-signs the links in messages it already holds when
it shows them, so tracking messages keep their images. Two cases still lose them:

- An image attached to a slash command (`/bug report`, `/bug edit image`) belongs to no
  message, and Discord deletes it after about a day; refreshing its link doesn't help.
  The bot downloads such an image straight away and posts it in the feed channel
  ("Image for bug #12"), and the entry shows that copy from then on. If the image is
  larger than the bot may upload to the server, the reporter is told it will stop
  showing, and only the saved copy remains.
- When the message an image came with is deleted (a reporter tidying up, or a moderator
  removing an exploit), the image is gone. About 1% of imported bug images were already
  lost this way. Discord still signs links to them, so only downloading one shows that.

So the bot also saves every image to disk, in `images/<entry>/<attachment id>-<name>` next
to the database, recorded in `image_files`. It saves new images within moments, and works
through any without a copy in the background, 50 at a time, newest entries first. An
image Discord no longer has is recorded as lost and not tried again. Other failures are
retried an hour later per failure (at most a day), after every image not yet tried, so a
few bad links can't hold up the rest.

The saved copies are kept through image edits and redaction, and deleted with the entry
by `purge`. The team gets them back with `taskctl images <n>` (or the API), sees a
redacted entry's privately in `/bug redacted`, and can have a lost image posted again with
`reupload`. Nothing the bot posts in a channel after a redaction comes from the redacted
entry: posting a saved image checks that first, and redacting an entry deletes the bot's
own copies of its images from the feed channel. What was posted before stays and has to be
deleted by hand, as before: the reporter's original messages, and the feed channel's lines
for changes made outside it (a new report's or an append's description, close reasons),
which name the entry. The bot remembers each of those messages until Discord confirms it is
deleted, and tries again on every pass of the save loop, so a failed delete, a restart or
a redaction during an upload can't leave one behind.

## Layout

| Path | Role |
|---|---|
| `main.py` | Entry point: loads config, opens the database (which must exist), runs the bot and the API in one event loop. |
| `taskbot/config.py` | `InstanceConfig`, read from `config.yml`. |
| `taskbot/db.py` | Schema and migrations (`PRAGMA user_version`); `python -m taskbot.db init` makes an empty database. |
| `taskbot/vocab.py` | The fixed priorities and complexities, and the priority sort order. |
| `taskbot/store.py` | `TaskStore`: all SQL. No permission checks, no Discord. |
| `taskbot/service.py` | `TaskService`: every action (add, edit, close, assign, ...) with its permission rule, validation and event log entry. Text commands and the API both go through it; only the commands that exist in Discord alone (`prune`, `repost`, `ping_assigned`, `send_notifications`) check their level in `commands.py`. |
| `taskbot/commands.py` | The `~bug <command>` interface: parsing, replies, usage text. Reaches Discord only through the small `BotPort` and `Responder` protocols. |
| `taskbot/interactive.py` | `isearch` / `iroulette` sessions. |
| `taskbot/formatting.py` | Entry and stats text, character for character as the old bot rendered them. |
| `taskbot/matching.py` | The old prefix matching, which abbreviations depend on. |
| `taskbot/stats.py`, `taskbot/charts.py` | Statistics, time series and chart rendering (matplotlib, no pyplot). |
| `taskbot/models.py` | Plain data objects shared by the layers. |
| `taskbot/duplicates.py` | Whether a `fix` or `reject` reason says the entry is a duplicate, and of what. |
| `taskbot/images.py` | Saved copies of images on disk (see "Images"). |
| `taskbot/api.py` | Quart `/api/*` routes, user and service token authentication. |
| `taskbot/identity.py` | Whether a Discord user or Minecraft player is a given entry's author; where a future account link plugs in. |
| `taskbot/tokens.py` | `python -m taskbot.tokens`: service tokens for the game plugin. |
| `taskbot/bot.py` | The discord.py side: message routing, the tracking channel publisher, image links, reactions, backups. |
| `taskbot/slash.py` | The slash commands, their private replies and forms (over the same command handler). |
| `cli/taskctl.py` | Stdlib-only API client. |
| `plugin/` | The Paper plugin for in-game reports (Java, its own build and tests). |

The layering is what makes the bot testable without Discord: everything above `bot.py`
runs against fakes in `tests/`.

## Configuration

`$TASK_HOME/config.yml` (default `~/.task_bot/config.yml`), the same file the old bot
read. Existing keys keep their meaning, and keys the bot doesn't use are ignored. New,
all optional:

| Key | Default | Meaning |
|---|---|---|
| `db_path` | `tasks.db` | SQLite file, relative to the config directory. It must exist; see "Deployment" below. |
| `api_port` | `8080` | Port for `/api/*`, for people (behind the ingress). The cluster-only port for service tokens (the game plugin) is always 8081. |
| `api_public_url` | | Public base URL, shown when someone creates a token. |
| `api_token_default_ttl_hours` | `720` | Token lifetime when `/... api_token create` gets no `lifetime_days`. |
| `api_token_max_ttl_hours` | `8760` | Upper bound on a token's lifetime. |
| `resolution_names` | | Display names for resolutions, for example `{fixed: implemented}` for suggestions. Only affects new output. |

`$DISCORD_TOKEN`, when set, replaces `login` from the file, so the token can come from a
Kubernetes secret.

## Development

```bash
make venv     # create .venv with runtime and dev dependencies
make test     # pylint, pyright (strict) and pytest
```

The rendering the old bot's users know is pinned by golden replies in
`tests/test_commands.py`, and the abbreviations by `tests/test_matching.py`.

To try the bot against real Discord, point `TASK_HOME` at a directory with a `config.yml`
for a test guild and run `.venv/bin/python main.py`.

## Deployment

The image is built from this directory (`./docker_build_and_push.sh`) and deployed by
`docker/k8s/bug-bot.yml` and `suggestion-bot.yml`. Each mounts its data directory
(`/nfs/task-bot/bugs`, `/nfs/task-bot/suggestions`) at `/data`, reads the Discord token
from a secret, and exposes the API on port 8080 behind an ingress and on port 8081 inside
the cluster for the game plugin.

The bot writes a backup of the database to `backups/` once a day (seven kept). Backups
are copies, so text removed with `purge` stays in them until they age out (a week).

The bot never creates its database: on start it opens `tasks.db` and refuses to run if it
is missing, rather than begin an empty tracker numbered from #1 over the existing
messages. For a new instance or a test guild, `python -m taskbot.db init tasks.db` makes
an empty one.

The database is SQLite in WAL mode, which needs a local filesystem. `/nfs/task-bot` on
monumenta-17 is a local ZFS dataset mounted into the pod with hostPath, which is fine;
don't move it to a network mount.

### In-game reports

Entries can come from the game: the plugin files them for the player through a service
token, and the tracking channel shows `Steve (in-game)` as the author. Where the report was
made is stored as context, visible to the team with `/bug context <n>` and never posted.
In-game reporters own their reports just as Discord users do (they may append to or reject
them), and `send_notifications` queues a chat notice for them instead of a ping, shown the
next time they join a shard. Setup:
[plugin/README.md](plugin/README.md).

## Imported history

Entries from before the rewrite's launch on 2026-11-23 came from the old bot, which kept
only each entry's final state, in a JSON file: no times and no closers. At the cutover
that file was imported, and the old feed channels (`bug-reports-bot-feed`,
`suggestions-bot-feed`), which hold every command since April 2019 and the bot's reply to
it, were replayed over it to recover who did what and when. The code that did this was
removed once the launch had settled; it is in the git history. What it left in the
database:

- Events with `source` `backfill` come from the feed channels and have exact times.
  Events with `source` `legacy` come from the JSON alone, for what the feed didn't show:
  `created` and `closed` events at estimated times, of which `history` shows only the
  day, with no closer on the `closed` ones, and `redacted` events with no time or actor
  (`history` says "before the new bot").
- The replay found the exact close for 98% of closed bugs and 99% of closed suggestions,
  and the closer for 99% and 97% of those. The rest were closed without a feed command:
  the first ~700 bugs were imported on 2019-04-20 and closed outside the channel, and some
  later ones through Kanboard. Their close time is their creation time (or, for those
  whose feed close didn't match the JSON, the time of their last event in the feed), so
  every closed entry has one and statistics don't carry the gap forever; their closer is
  unknown. Those entries were really open for a while, so the backlog slightly undercounts
  the early years (by at most a few hundred), and the closes chart counts them in their
  creation month.
- A resolution is what the closer chose at the time, `fix` or `reject`, with rejects whose
  reason says duplicate counted as duplicates (and fixes whose reason names the original,
  "dupe of 2360"). Where the feed doesn't show the close, it was guessed from the close
  reason's text.
- About 1,200 creation times the feed doesn't show were estimated from the Discord ids
  attached to each entry (its tracking message and image attachments), since entry numbers
  grow with time. Checked against the entries whose time the feed does show, 99.7% of bug
  and 96% of suggestion estimates were within a day. The first 487 suggestions take their
  creation date from the text an older import wrote into them. The creation times of bugs
  below about #720, imported on 2019-04-20 from older channels before the feed began,
  only mean "on or before", and may be weeks or months late.
- Before `redact` existed, people redacted an entry by editing its description to
  "redacted". Such entries are marked redacted, and those that had an image have it
  hidden in `redacted_content`, with `redacted_at` 0.
