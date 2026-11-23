"""Download a Discord channel's message history to a JSON-lines file.

    python -m taskbot.feed.download --config <old bot config.yml> <out.jsonl>

Each line is one message exactly as Discord's REST API returned it, oldest
first. The file is only ever appended to: a later run reads the newest message
id already saved and continues after it, so the same command both does the
first full pull and catches up later (for example right before the cutover).
A catch-up run does not see edits or deletions of messages it already saved;
delete the file and pull again for that.

The token is the old bot's (`login` in its config.yml, which also names the
channel as `bot_input_channel`). The download uses plain HTTP requests only and
never opens a gateway connection, so it does not disturb the running bot with
the same token. It does share that bot's rate limits, so it stays well below
them: one request at a time, a minimum interval between requests, waits out
whatever the rate-limit headers ask for, and gives up after a few 429 replies
rather than pushing on.

The token is never printed or written anywhere.
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Optional

import yaml

from ..inference import snowflake_time

API_BASE = "https://discord.com/api/v10"
PAGE_SIZE = 100
USER_AGENT = "DiscordBot (https://discord.com, 1.0) taskbot-feed-download"


@dataclass
class Response:
    status: int
    headers: dict[str, str]
    body: bytes


# Performs one GET; separated out so tests can fake Discord.
Fetcher = Callable[[str, dict[str, str]], Response]


def urllib_fetch(url: str, headers: dict[str, str]) -> Response:
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return Response(resp.status, {k.lower(): v for k, v in resp.headers.items()}, resp.read())
    except urllib.error.HTTPError as e:
        return Response(e.code, {k.lower(): v for k, v in e.headers.items()}, e.read())


class DownloadError(Exception):
    pass


@dataclass
class Pacing:
    min_interval: float = 0.35
    max_rate_limited: int = 3
    max_server_errors: int = 8


def _last_newline_before(f: Any, end: int) -> int:
    """Offset just past the last newline before `end`, 0 if there is none."""
    pos = end
    while pos > 0:
        start = max(0, pos - (1 << 16))
        f.seek(start)
        cut = f.read(pos - start).rfind(b"\n")
        if cut >= 0:
            return start + cut + 1
        pos = start
    return 0


def last_saved_id(path: str) -> int:
    """Newest message id in the file, 0 if none. Cuts off a torn final line."""
    if not os.path.exists(path):
        return 0
    with open(path, "rb+") as f:
        size = f.seek(0, os.SEEK_END)
        end = _last_newline_before(f, size)
        if end != size:
            print(f"Truncating a partial final line at byte {end}", file=sys.stderr)
            f.truncate(end)
        if end == 0:
            return 0
        line_start = _last_newline_before(f, end - 1)
        f.seek(line_start)
        return int(json.loads(f.read(end - line_start))["id"])


class ChannelDownloader:
    def __init__(self, token: str, channel_id: int, fetch: Fetcher = urllib_fetch,
                 pacing: Optional[Pacing] = None, sleep: Callable[[float], None] = time.sleep,
                 clock: Callable[[], float] = time.monotonic):
        self._headers = {"Authorization": f"Bot {token}", "User-Agent": USER_AGENT}
        self._channel_id = channel_id
        self._fetch = fetch
        self._pacing = pacing or Pacing()
        self._sleep = sleep
        self._clock = clock
        self._next_allowed = 0.0
        self._rate_limited = 0

    def _wait_turn(self) -> None:
        delay = self._next_allowed - self._clock()
        if delay > 0:
            self._sleep(delay)

    def page_after(self, after: int) -> list[dict[str, Any]]:
        """Up to PAGE_SIZE messages newer than `after`, oldest first."""
        url = f"{API_BASE}/channels/{self._channel_id}/messages?after={after}&limit={PAGE_SIZE}"
        server_errors = 0
        while True:
            self._wait_turn()
            try:
                resp = self._fetch(url, self._headers)
            except OSError as e:
                resp = Response(0, {}, str(e).encode())
            now = self._clock()
            self._next_allowed = now + self._pacing.min_interval
            if resp.headers.get("x-ratelimit-remaining") == "0":
                reset_after = float(resp.headers.get("x-ratelimit-reset-after", "1"))
                self._next_allowed = max(self._next_allowed, now + reset_after + 0.1)

            if resp.status == 200:
                messages: list[dict[str, Any]] = json.loads(resp.body)
                messages.sort(key=lambda m: int(m["id"]))
                return messages
            if resp.status == 429:
                self._rate_limited += 1
                try:
                    retry_after = float(json.loads(resp.body).get("retry_after", 5))
                except ValueError:
                    retry_after = 5.0
                scope = resp.headers.get("x-ratelimit-scope", "?")
                print(f"Rate limited (429 #{self._rate_limited}, scope {scope}), waiting {retry_after:.1f} s",
                      file=sys.stderr)
                if self._rate_limited >= self._pacing.max_rate_limited:
                    raise DownloadError("Rate limited too often; stopping so the live bot is not affected")
                self._next_allowed = max(self._next_allowed, now + retry_after + 1)
                continue
            if resp.status in (0, 500, 502, 503, 504):
                server_errors += 1
                if server_errors > self._pacing.max_server_errors:
                    raise DownloadError(f"Giving up after {server_errors} server/network errors "
                                        f"(last: {resp.status} {resp.body[:200]!r})")
                backoff = min(60.0, 2.0 ** server_errors)
                print(f"Server/network error {resp.status}, retrying in {backoff:.0f} s", file=sys.stderr)
                self._next_allowed = max(self._next_allowed, now + backoff)
                continue
            # 401/403/404 and anything else: a setup problem, not worth retrying.
            raise DownloadError(f"HTTP {resp.status}: {resp.body[:300]!r}")

    def download(self, path: str, max_pages: Optional[int] = None,
                 progress: Callable[[int, int, int], None] = lambda pages, total, last: None) -> int:
        """Append everything newer than the file's last message. Returns messages added."""
        after = last_saved_id(path)
        added = 0
        pages = 0
        with open(path, "ab") as out:
            while max_pages is None or pages < max_pages:
                messages = self.page_after(after)
                if not messages:
                    break
                for m in messages:
                    if int(m["id"]) <= after:
                        raise DownloadError(f"Discord returned message {m['id']} not after {after}")
                    out.write(json.dumps(m, ensure_ascii=False, separators=(",", ":")).encode() + b"\n")
                out.flush()
                os.fsync(out.fileno())
                after = int(messages[-1]["id"])
                added += len(messages)
                pages += 1
                progress(pages, added, after)
        return added


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m taskbot.feed.download", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", required=True, help="the old bot's config.yml (token and channel)")
    parser.add_argument("--channel", type=int, help="channel id (default: bot_input_channel from the config)")
    parser.add_argument("--max-pages", type=int, help="stop after this many pages (for trying it out)")
    parser.add_argument("out", help="JSON-lines file to create or extend")
    args = parser.parse_args(argv)

    with open(args.config, encoding="utf-8") as f:
        config: dict[str, Any] = yaml.safe_load(f)
    token = str(config["login"])
    channel_id = args.channel or int(config["bot_input_channel"])

    start = time.monotonic()

    def progress(pages: int, total: int, last: int) -> None:
        if pages % 50 == 0:
            stamp = time.strftime("%Y-%m-%d", time.gmtime(snowflake_time(last)))
            rate = total / max(1e-6, time.monotonic() - start)
            print(f"{total} messages ({pages} pages), up to {stamp}, {rate:.0f}/s", file=sys.stderr)

    downloader = ChannelDownloader(token, channel_id)
    try:
        added = downloader.download(args.out, max_pages=args.max_pages, progress=progress)
    except DownloadError as e:
        print(f"Stopped: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Interrupted; run again to continue", file=sys.stderr)
        return 130
    print(f"Added {added} messages to {args.out} in {time.monotonic() - start:.0f} s", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
