# taskctl

A command line client for the task bot's network API ([../API.md](../API.md)). One file,
standard library only, so it runs anywhere with Python 3.10+:

```bash
alias taskctl='python3 /path/to/discord_bots/task_bot/cli/taskctl.py'
```

It knows nothing about bugs or suggestions. It asks the server what it tracks and uses
the server's words in its output, so the same script talks to every instance.

## Setup

Team members get a token in Discord with `/bug api_token create` (or
`/suggestion api_token create`), then:

```bash
export TASKCTL_URL=https://bugs-api.playmonumenta.com
export TASKCTL_TOKEN=tb_...
taskctl info
```

There is no `--token` flag, so tokens don't end up in shell history or `ps`. The URL must
be `https://` (plain `http://` only to localhost), and redirects aren't followed, so the
token never travels in the clear or to another host. For more than one instance, wrap the
environment in aliases:

```bash
alias bugs='TASKCTL_URL=https://bugs-api.playmonumenta.com TASKCTL_TOKEN=$BUG_TOKEN taskctl'
alias sugs='TASKCTL_URL=https://suggestions-api.playmonumenta.com TASKCTL_TOKEN=$SUG_TOKEN taskctl'
```

`/... api_token create read_only:True` makes a token that can't change anything, which is
the right kind to give a script or an agent that only reads.

## Commands

```
taskctl info                      what the server tracks, who you are (alias: whoami)
taskctl list [filters]            entries, open by default (alias: ls)
taskctl get <id>... [--text]      full entries; --text prints them as Discord shows them
taskctl history <id>...           who changed entries and when
taskctl activity [--since 7d]     recent changes everywhere [--kind closed] [--actor me]
taskctl add [-l label] TEXT...    file an entry as yourself
taskctl edit <id> -p PRIORITY -c COMPLEXITY -l a,b -d TEXT --author U
taskctl append <id> TEXT...
taskctl fix <id>... [--reason R] [--force]
taskctl reject <id>... --reason R [--force]
taskctl dupe <id>... --of N [--note T] [--force]
taskctl reopen <id>...            (alias: unfix)
taskctl assign <id>... [--user U]   taskctl unassign <id>...
taskctl redact <id>...            taskctl redacted <id>   (team: what redaction hid)
taskctl images <id> [-o DIR] [--list]   (saved copies of its images, into bug-<id>/)
taskctl stats | authors | closers [--days N]
taskctl chart [name] [options] [-o FILE]
```

`taskctl <command> --help` lists every flag. Filters for `list`: `--status
open|closed|all`, `-l/--label` (repeatable, all must match), `-p/--priority`,
`-c/--complexity`, `-r/--resolution` (any may match), `--author`, `--assignee`,
`--closed-by` (user id, name prefix or `me`; assignee also takes `any`/`none`), `-q` words
in the description, `--reason-contains` words in the close reason, `--reaction`,
`--created-after/--created-before/--closed-after/--closed-before` and `--idle` (no change
at all since then; `30min`, `12h`, `7d`, `2w`, `6mo`, `1y`, `2026-01-31`, ...),
`--sort id|priority|created|updated|closed`, `--desc`, `-n/--limit` (default 50, `0` for all).

`activity` shows the newest events matching its filters, oldest first: `--since` (default
`7d`; `--since ""` for no limit, which also includes the few imported events with no
time), `--kind` (repeatable), `--actor`, and `-n/--limit` (default 200, `0` for all). It
fetches pages of 1,000 as needed, so `--since 10y --actor me --kind priority -n 0 --json`
gives every priority you ever set.

## Composing

Commands that take ids accept `-` to read them from stdin, and `list --ids` prints one id
per line, so commands chain:

```bash
# Read every open quest bug marked High
taskctl list -l quest -p high --ids | taskctl get -

# Close a batch found by a description search
taskctl list -q "spawner" -q "lag" --ids | taskctl fix - --reason "Fixed by the spawner rework"

# Open bugs nothing has happened to in a year, oldest first
taskctl list --idle 1y

# Was this fixed once already?
taskctl list --status closed --reason-contains "soul" --reason-contains "rework"

# What did I close this week?
taskctl list --status closed --closed-by me --closed-after 7d

# Chart for a meeting
taskctl chart closes week 6m -o closes.png
```

Closing commands skip entries that are already closed (exit status 1, reason on stderr)
unless given `--force`, so a pipeline that also matched closed entries can't rewrite who
closed them.

`--json` on any command prints the raw API objects, one per line, for `jq` and scripts.
Commands that act on several ids keep going when one fails, print the failures on
stderr, and exit non-zero. Times print in your local timezone, except the days of imported
events, which are in UTC as the bot shows them.
