# MonumentaTaskBot (Paper plugin)

In-game access to the task bots: players file bug reports with `/bug report ...`, find
and read them, and get a chat notice when one of their reports is updated; moderators can
triage and close reports without leaving the game. It talks to each task bot's network
API ([../API.md](../API.md)) with a service token, acting for the player.

Like `taskctl`, the plugin knows nothing about bugs or suggestions in particular. It is
configured with a list of instances, registers one command per instance (`/bug`,
`/suggestion`), and takes its wording and labels from each instance's `/api/info`.
Everything works the same for every instance; permissions decide which players may use
what.

Paper 1.20.4, needs CommandAPI. Built with gradle-config like the other Monumenta plugins:

```bash
./gradlew build          # jar in build/libs, runs the unit tests
integration-test/run.py  # end-to-end test, see below
```

## Configuration

Environment variables, like the exception reporter. An instance without a URL and a token
is disabled and registers no command, so the jar can be installed everywhere and only
report where it's configured.

| Variable | Meaning |
|---|---|
| `TASKBOT_INSTANCES` | Command names separated by spaces or commas: `bug suggestion`. Empty: the plugin does nothing. |
| `TASKBOT_<NAME>_URL` | The instance's internal API listener, e.g. `http://bug-bot.default.svc.cluster.local:8081`. Service tokens are refused on the public port. |
| `TASKBOT_<NAME>_TOKEN` | A service token for it. |
| `TASKBOT_<NAME>_TOKEN_FILE` | Or a file holding the token, e.g. a mounted secret. Keeps it out of the process environment, which crash reports can capture. |
| `TASKBOT_SERVER_NAME` | This shard's name in report context. Default `NETWORK_RELAY_NAME`, then `EXCEPTLOG_SERVER_NAME`, then the hostname. |
| `TASKBOT_REPORT_COOLDOWN_SECONDS` | Per-player wait between reports (default 60). |

On Kubernetes the shard Helm chart sets all of these from `taskBotInstances` (on for play
only, in `shard_deployment_tool_config.yaml`). The tokens come from a `task-bot-tokens`
secret in the shard's namespace, which is optional, so reporting stays off until it exists:

```bash
# Create a service token in each bot's database and put it straight into the secret
# (process substitution keeps the tokens off command lines and out of shell history)
kubectl -n play create secret generic task-bot-tokens \
  --from-file=bug=<(kubectl -n default exec deploy/bug-bot -- python -m taskbot.tokens create shards-play) \
  --from-file=suggestion=<(kubectl -n default exec deploy/suggestion-bot -- python -m taskbot.tokens create shards-play)
```

The token's `--max-privilege` (default 2, the most the plugin ever asks for) caps what the
plugin may grant through it; see "Permissions". The chart passes the token as an
environment variable. Either way the plugin holds it in memory, so it is in any heap dump
of a shard (play shards upload theirs). A leaked shard token works only on the in-cluster
listener, at privilege 2 at most, and only acting as players; revoke it with
`python -m taskbot.tokens revoke shards-play`.

## Commands

| Command | Permission | What it does |
|---|---|---|
| `/bug report <label> <description>` | `create` | Files a report as the player. The label is required and tab-completes from the tracker's labels; the description needs at least 5 words, and a cooldown applies after each successful report. Where they were (shard, world, coordinates) is attached as context for the team, never shown publicly. |
| `/bug get <n>` | `view` | Shows one report. |
| `/bug search <words>` | `view` | Open reports containing all the words. |
| `/bug mine` | `view` | The player's own reports. |
| `/bug append <n> <text>` | `append` | Adds to a report's description. |
| `/bug fix <n> [reason]` | `fix` | Closes as fixed. |
| `/bug reject <n> <reason>` | `reject` | Closes as rejected, or as a duplicate when the reason says so ("dupe of #12"), as in Discord. |
| `/bug dupe <n> <original>` | `dupe` | Closes as a duplicate. |
| `/bug reopen <n>` | `reopen` | Reopens. |
| `/bug priority <n> <level>` | `priority` | Sets the priority (tab completion comes from the tracker's list; abbreviations work). |
| `/bug context <n>` | `context` | Shows the context attached to a report. In Discord the team uses the ephemeral `/bug context`. |
| `/bug notify on\|off\|status` | `notify` | Chat notices about updates to one's reports. |

Results are clickable: `#123` runs `/bug get 123`.

## Permissions

Each subcommand has its own node, `monumenta.taskbot.<command>.<operation>`, for example
`monumenta.taskbot.bug.create`. `append`, `fix`, `reject`, `dupe` and `reopen` also have an
`.own` variant (`monumenta.taskbot.bug.reject.own`) that only allows it on reports the
player filed. Without a node, the subcommand doesn't show up at all, and a player with no
node for an instance doesn't see its command (`/suggestion`) either.
`monumenta.taskbot.<command>.create.nocooldown` skips the report cooldown.

The plugin registers every node with an op-only default, so players get nothing until the
permissions plugin grants it. Ops get everything. CommandAPI decides which subcommands a
player sees when they log in, so after a permission change the player may need to relog
before the command list matches (the permission check on use is always current).

A starting point for LuckPerms:

| Group | Nodes (for `bug`) |
|---|---|
| everyone | `create`, `view`, `notify`, `append.own`, `reject.own` |
| moderators | additionally `fix`, `reject`, `dupe`, `reopen`, `append`, `priority`, `context` |

A wildcard such as `monumenta.taskbot.bug.*` also grants `create.nocooldown`, which is
fine for staff.

Suggestions work the same way; granting nothing for `suggestion` keeps `/suggestion`
hidden while it is set up.

How this maps onto the bot's own rules: the task bot checks privilege levels (0 everyone,
1 authors, 2 team, ...) exactly as in Discord. With each request the plugin tells it the
level to use: the level the operation needs on anyone's report if the player holds the
full node (`fix` needs 1, `priority` and `context` need 2), or 0 if they only hold `.own`,
leaving the bot to check that the player filed the report. The token's `--max-privilege`
caps the level, so a leaked shard token can't do more than intended.

## Notices

When the team runs `~bug send_notifications` in Discord, players whose in-game reports
changed get a notice queued instead of a Discord ping. The plugin shows a player's pending
notices a few seconds after they join a shard, which players do often as they move
between content. It takes them from the bot in one request, which marks them delivered,
so a notice lost to a disconnect at that moment isn't sent again. `/bug notify off` opts
out, like `~bug notify off` in Discord.

## Labels

Each instance's command is registered once the plugin has read the tracker's wording and
labels from `/api/info`, since the labels are part of `/bug report`. The plugin retries in
the background until the tracker answers; until then that command doesn't exist on the
shard. Labels change about once a year and the plugin restarts with the shard every day,
so a label added with `~bug addlabel` reaches the game at the next restart. Until then, a
label removed with `~bug dellabel` is still offered in game, and reports with it are refused
(or, if it is the start of another label's name, filed under that label).

## Load on the tracker

There are 50+ shards, so the plugin never blocks one and sends little. Every request is
asynchronous with a 10 second timeout, and only its result hops back to the main thread.
At startup a shard sends one `GET /api/info` per instance, retried after 15 s, 30 s and so
on up to every 10 minutes while the tracker is down, with a warning logged each time. On
every player join it sends one `POST .../notices/take` per instance, 5 seconds after the
join; failures there are logged only at FINE. Everything else is what players type. Joins
are the steady load. A join's request only reads unless a notice is waiting, and the bot
writes the service token's `last_used_at` and the player's name at most once a minute and
once an hour.

## Layout

| File | Role |
|---|---|
| `TaskBotPlugin` | Reads the config, sets up each instance once its tracker answers, delivers notices on join. |
| `PluginConfig` | Environment variables. |
| `TaskInstance` | One instance's command and its subcommands. |
| `Operation` | The operations, their permission nodes and privilege levels. |
| `ApiClient` | Asynchronous client for the API (`java.net.http`, Gson). Requests complete off the main thread; results hop back before touching players. |
| `ContextCollector` | The context attached to a report. Only the location for now; this is where equipment, player state and so on go later, each as its own section (the bot stores any named section, so it needs no change). |
| `Messages` | Chat rendering. |

## Testing

`./gradlew build` runs the unit tests: config parsing, the permission to privilege mapping,
and the API client against a local HTTP stub.

`integration-test/run.py` tests the whole path. It starts a real task bot API on a scratch
database (`api_server.py`, using the bot's venv), Paper 1.20.4 with CommandAPI and the
freshly built plugin, and two simulated players from
[monumenta-testbot](../../../../monumenta-testbot/README.md): a regular player with the
permissions above and an op. It then reports, lists, searches, checks that permissions
hold (with Bukkit's `permissions.yml` standing in for LuckPerms), that an instance with no
granted operations stays hidden, closes as the op, and checks the notice the player gets
after rejoining (queued by the real `send_notifications` code), both in chat and in the
database. Paper and CommandAPI are downloaded once into `integration-test/.cache/`. Needs
Java 21, the task bot's `.venv`, and a built testbot.
