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
| `~bug dupe <n> <original> [note]` | Closes n as a duplicate of the original, linking them. Same permission as `reject`. Also works inside interactive sessions. |
| `~bug reject <n> dupe of <original>` | People rejected duplicates this way before `dupe` existed, so `reject` and `fix` read the reason: one that says duplicate ("dupe of #123", "same issue as 123") closes as a duplicate, linked to the original when the reason names an entry that exists. `fix` does so only when an original is named. The reason is kept as typed, and the reply says it was closed as a duplicate. The same applies through slash commands, the API and in game. |
| `~bug history <n>` | Who changed an entry and when. |
| `~bug cstats [days] [minimum]` | Who closed the most entries, split into fixed / rejected / duplicate. Authors closing their own entries are counted separately. Overall (no days, or 0) lists only people with at least 20 closes, since most closers have a handful; a minimum overrides that. |
| `~bug chart [name] [options]` | Posts a chart (backlog, intake, closes, closers, age, labels). Without a name, lists them. Options pick the period (`90d`, `2y`, `all`) and the bucket (`week`, `month`). The backlog is stacked by complexity, or by priority with `priority`, and a label name limits it to entries with that label (`backlog plugin`). Intake is split by label (each entry under its first label other than misc), closes and closers by resolution. |
| `~bug redact <n>` | Hides an entry's text, close reason, images and the text in its history from everyone but the team (replaces `delete`, which now only points here). Anything added to a redacted entry afterwards (an edit, an append, a close reason) shows as usual until it is redacted again. Level 1. |
| `~bug purge <n>` | Leads: deletes an entry for good, with its history, saved images and anything redacted. Asks for `purge <n> confirm`. |
| `~bug reupload <n>` | Team: posts the saved copies of an entry's images in the feed channel and shows those from then on, for when Discord has lost an image (its message was deleted). Never for a redacted entry. |
| `/bug <command>` | Slash versions of the commands, replying only to whoever uses them (see "Slash commands" below). |
| `/bug context <n>`, `/bug redacted <n>` | Team only, and only visible to whoever asks: the context attached to an entry (such as where an in-game report was made), and what redaction hid, with the saved copies of its images attached. (`~bug context` points here, since the feed channel is public.) |
| `/bug api_token create` / `revoke` | Team only: mint or revoke a token for the API. |

`history`, `cstats` and `chart` are for the team (privilege 2), as is the API.

Other differences, all deliberate:

- Every change is recorded with who made it and when, so closer statistics and history
  exist from cutover on. Closes are recorded as fixed, rejected or duplicate rather than
  only free text.
- An entry that others were closed as duplicates of lists them on a line after its
  description (`Duplicates: #12, #40`) in the tracking channel and in replies, and
  `taskctl` shows them too. The line is left out when the message would go over Discord's
  2000 characters. At the first start after the cutover the bot edits the tracking
  messages of the originals to add it (a few hundred edits, which take some minutes).
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
feed channel (`Combustible fixed bug #12 (/bug)`), as API changes do, so the channel stays
a complete log. The bot registers the commands with Discord when it starts, only when they
have changed, so `~bug sync` is no longer needed.

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
through any without a copy in the background, 50 at a time, newest entries first. That is
also how the images of an imported database get saved (an estimated 7 GB for both
instances, over a few hours at the first start). An image Discord no longer has is
recorded as lost and not tried again. Other failures are retried an hour later per failure
(at most a day), after every image not yet tried, so a few bad links can't hold up the
rest.

The saved copies are kept through image edits and redaction, and deleted with the entry
by `purge`. The team gets them back with `taskctl images <n>` (or the API), sees a
redacted entry's privately in `/bug redacted`, and can have a lost image posted again with
`reupload`. Nothing the bot posts in a channel ever comes from a redacted entry: posting a
saved image checks that first, and redacting an entry deletes the bot's own copies of its
images from the feed channel (the reporter's original messages still have to be deleted
by hand, as before). The bot remembers each of those messages until Discord confirms it is
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
| `taskbot/legacy.py`, `taskbot/inference.py` | Import of the old JSON file at cutover; close-reason classification and creation-time estimation. |
| `taskbot/api.py` | Quart `/api/*` routes, user and service token authentication. |
| `taskbot/identity.py` | Whether a Discord user or Minecraft player is a given entry's author; where a future account link plugs in. |
| `taskbot/tokens.py` | `python -m taskbot.tokens`: service tokens for the game plugin. |
| `taskbot/bot.py` | The discord.py side: message routing, the tracking channel publisher, image links, reactions, backups. |
| `taskbot/slash.py` | The slash commands, their private replies and forms (over the same command handler). |
| `taskbot/feed/` | Downloads the old bots' feed channels and replays them into a history of events (see below). |
| `cli/taskctl.py` | Stdlib-only API client. |
| `plugin/` | The Paper plugin for in-game reports (Java, its own build and tests). |

The layering is what makes the bot testable without Discord: everything above `bot.py`
runs against fakes in `tests/`.

## Configuration

`$TASK_HOME/config.yml` (default `~/.task_bot/config.yml`), the same file the old bot
read. Existing keys keep their meaning; `kanboard` and `database_path` are ignored. New,
all optional:

| Key | Default | Meaning |
|---|---|---|
| `db_path` | `tasks.db` | SQLite file, relative to the config directory. It must exist; see "Cutover" below. |
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

The tests in `tests/test_legacy_compat.py` load the original bot's code from git and
compare its rendering, search and stats output with the new code on the production
data. They need a copy of the production JSON files (set `TASKBOT_LEGACY_SNAPSHOT` to a
directory with `bugs/bug_reports.json` and `suggestions/suggestions.json`) and skip
without one.

To try the bot against real Discord, point `TASK_HOME` at a directory with a `config.yml`
for a test guild and run `.venv/bin/python main.py`.

## Deployment

The image is built from this directory (`./docker_build_and_push.sh`) and deployed by
`docker/k8s/bug-bot.yml` and `suggestion-bot.yml`. Each mounts its old data directory
(`/nfs/task-bot/bugs`, `/nfs/task-bot/suggestions`) at `/data`, reads the Discord token
from a secret, and exposes the API on port 8080 behind an ingress and on port 8081 inside
the cluster for the game plugin.

The bot writes a backup of the database to `backups/` once a day (seven kept). Backups
are copies, so text removed with `purge` stays in them until they age out (a week).

The bot never creates its database: on start it opens `tasks.db` and refuses to run if it
is missing, rather than begin an empty tracker numbered from #1 over the existing
messages. At cutover the database comes from the import below; for a new instance or a
test guild, `python -m taskbot.db init tasks.db` makes an empty one.

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

### Cutover

The cutover is one-way: once the new bot is live, the old one doesn't run again.

1. Scale the old deployment to zero and wait for it to stop. Two bots logged in with the
   same token would both answer every command.
2. Build `tasks.db` from the old JSON and the old feed channel's history (see "Mining the
   old feed channels" below): catch up the download, replay it, `python -m
   taskbot.legacy import` the JSON (which is never modified) and `python -m
   taskbot.feed.apply` the replay. The import writes the classification of every old
   close reason next to the database as `tasks.db.classification.txt`, for review.
3. Put `tasks.db` where the bot looks for it (`db_path` in `config.yml`) and deploy the
   new bot. It registers its slash commands with Discord on its first start.

`legacy.py`, `inference.py`, `taskbot/feed/` and their tests (`tests/test_legacy.py`,
`tests/test_legacy_compat.py`, `tests/test_feed_*.py`) only matter until the cutover is
done, and can be deleted after it. The rendering the old bot's users know is also pinned
by golden replies in `tests/test_commands.py`, which stay.

Reaction counts aren't in the old JSON. After the import the bot reads them from each
tracking message, a few a second, so `rsearch` is complete after roughly 15 minutes
for bugs and 25 for suggestions; until then it says so.

The old JSON carries over entries, labels, priorities, complexities, assignees, images,
notification settings and tracking messages, but no times and no closers. The import
guesses each close's resolution from its reason and estimates creation times; the feed
replay (next section) then supplies exact times, closers and resolutions for nearly
everything.

Creation times are estimated from the Discord ids attached to each entry (its tracking
message and image attachments), which are timestamps; entry numbers grow with time, so
the earliest of those ids at or after an entry bounds its creation time. The first 487
suggestions were imported from an older channel with their original dates in the text,
and those dates are used. Entries newer than the last Discord id the JSON holds (none, in
practice) take the time of the entry before them. After the replay about 1,200 estimates
remain: on the November 2026 data, 99.7% of bug and 96% of suggestion estimates were
within a day of the time the feed knows. The exception is bugs below about #720, imported
on 2019-04-20 from older channels before the feed began: their dates only mean "on or
before", and may be weeks or months late. Nothing marks which times are estimates beyond
the history, where an imported creation shows only its day.

### Mining the old feed channels

The old bots never stored who did what or when. Their command channels
(`bug-reports-bot-feed`, `suggestions-bot-feed`) hold every command since April 2019 and
the bot's reply to it. `taskbot.feed` recovers that history in three steps: two that only
read and write local files, and one that writes it into a freshly imported database.

`taskbot.feed.download` copies a channel to a JSON-lines file, one message per line
exactly as Discord's REST API returns it, oldest first. It uses the old bot's token and
channel from its `config.yml` (the token is never printed) and plain HTTP only, so it
doesn't disturb the bot running with the same token; it paces itself and stops after a
few rate-limit refusals rather than push on. Running it again continues after the newest
saved message, so the same command catches up just before the cutover. The bug channel
(about 527k messages) takes about 90 minutes, the suggestion channel about 50.

```bash
python -m taskbot.feed.download --config bugs/config.yml feed/bugs.jsonl
python -m taskbot.feed.replay --prefix '~bug' --snapshot bugs/bug_reports.json \
    feed/bugs.jsonl feed/bugs.events.jsonl feed/bugs.report.txt
python -m taskbot.legacy import bugs/bug_reports.json tasks.db
python -m taskbot.feed.apply tasks.db feed/bugs.events.jsonl
```

`taskbot.feed.replay` lets the bot's replies decide what happened (`Bug #12 marked as
fixed` means entry 12 was fixed then) and parses the commands only to find out who caused
each reply. It mirrors the old bot's handling closely enough for that: the command list
as it stood on each date (abbreviations resolve differently as commands were added),
interactive sessions where the owner types `f` or `e p l` against whichever entry the
session is showing, and the entry render the bot posted after each change, which gives
the old and new values. Each event records how it was attributed: `matched`;
`matched_loose` (the command was edited afterwards, and the bot acted on the original
text); `author_from_json` (a creation whose command was deleted, so the author comes from
the JSON and the time from the reply); `deleted_account` (Discord shows all deleted
accounts as one user, so the actor is unknown); or `unmatched` (the command is gone, the
time is still exact).

`taskbot.feed.apply` only accepts a database straight out of the import, so it runs during
the cutover, after the old bot has stopped (to redo it, import again). It also refuses
events that don't look like they belong with the database: when most creations in the feed
aren't by the entry's author (the other tracker's feed), or when the feed and the JSON end
at different entries (a download not caught up, or an older JSON); `--force` applies
anyway. For each entry the feed covers it replaces the import's placeholder events with
the real history, and sets the exact creation time and, when the feed's last close is the
one the JSON ended with, the close time, the closer and the resolution. The resolution is
what the closer chose at the time (`fix` or `reject`), with rejects whose reason says
duplicate counted as duplicates (and fixes whose reason names the original, "dupe of
2360"), rather than the import's guess from the text; 8% of bug and 10% of suggestion
closes change. Redacted entries get their history without the text. Author, assignee,
labels and the other current values stay as imported.

The report compares the result with a copy of the old JSON. On the November 2026 data, the
replay finds the exact close reason for 98% of closed bugs and 99% of closed suggestions,
and the closer for 99% and 97% of those respectively. The rest were closed without a feed
command: the first ~700 bugs were imported on 2019-04-20 and closed outside the channel,
and some later ones through Kanboard. Those get their creation time as the close time, so
every closed entry has one and statistics don't carry the gap forever; their closer stays
unknown. The few whose feed close doesn't match the JSON get the time of their last event
in the feed instead. Those entries were really open for a while, so the backlog slightly
undercounts the early years (by at most a few hundred), and the closes chart counts them
in their creation month.

Some of the old bot's habits the replay has to know: it ignored edited messages; replies
can carry a Discord id a moment earlier than their command; for a while it posted every
reply twice; `~b` was accepted as the prefix until 2019-09-26; close reasons were
lowercased until 2019-05-11; and its copy of a close reason turns custom emoji it
couldn't use into `:name:`.
