"""Mining the old bots' feed channels for history the legacy JSON never kept.

`download` copies a channel's full message history to a local JSON-lines file
that later runs extend. The replay that turns those messages into events reads
only that file, never Discord.
"""
