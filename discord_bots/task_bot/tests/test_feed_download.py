"""Feed downloader against a fake Discord: paging, resume, rate limits."""

import json
from pathlib import Path
from typing import Any

import pytest

from taskbot.feed.download import ChannelDownloader, DownloadError, Pacing, Response, last_saved_id


class FakeDiscord:
    def __init__(self, ids: list[int]):
        self.ids = ids
        self.calls: list[str] = []
        self.queued: list[Response] = []

    def __call__(self, url: str, headers: dict[str, str]) -> Response:
        assert headers["Authorization"] == "Bot secret"
        self.calls.append(url)
        if self.queued:
            return self.queued.pop(0)
        after = int(url.split("after=")[1].split("&")[0])
        page = [i for i in self.ids if i > after][:100]
        # Discord returns newest first.
        body = [{"id": str(i), "content": f"m{i}"} for i in reversed(page)]
        return Response(200, {"x-ratelimit-remaining": "4"}, json.dumps(body).encode())


class FakeTime:
    def __init__(self) -> None:
        self.now = 0.0
        self.slept: list[float] = []

    def sleep(self, s: float) -> None:
        self.slept.append(s)
        self.now += s

    def clock(self) -> float:
        return self.now


def make(fake: FakeDiscord, t: FakeTime) -> ChannelDownloader:
    return ChannelDownloader("secret", 1, fetch=fake, pacing=Pacing(min_interval=0.5), sleep=t.sleep, clock=t.clock)


def read_ids(path: Path) -> list[int]:
    return [int(json.loads(line)["id"]) for line in path.read_text().splitlines()]


def test_full_pull_then_resume(tmp_path: Path) -> None:
    out = tmp_path / "feed.jsonl"
    fake = FakeDiscord(list(range(10, 260)))
    t = FakeTime()
    assert make(fake, t).download(str(out)) == 250
    assert read_ids(out) == list(range(10, 260))
    assert len(fake.calls) == 4  # three pages and an empty one
    assert all(s == pytest.approx(0.5) for s in t.slept)

    fake.ids += [300, 301]
    assert make(fake, t).download(str(out)) == 2
    assert "after=259" in fake.calls[4]
    assert read_ids(out)[-3:] == [259, 300, 301]


def test_torn_last_line_is_dropped(tmp_path: Path) -> None:
    out = tmp_path / "feed.jsonl"
    out.write_text('{"id":"5"}\n{"id":"7"}\n{"id":"9","con')
    assert last_saved_id(str(out)) == 7
    assert out.read_text() == '{"id":"5"}\n{"id":"7"}\n'
    single = tmp_path / "single.jsonl"
    single.write_text('{"id":"5"')
    assert last_saved_id(str(single)) == 0
    assert last_saved_id(str(tmp_path / "missing.jsonl")) == 0


def test_long_lines(tmp_path: Path) -> None:
    out = tmp_path / "feed.jsonl"
    big = "x" * 200_000
    out.write_text(json.dumps({"id": "5", "c": big}) + "\n" + json.dumps({"id": "6", "c": big}) + "\n")
    assert last_saved_id(str(out)) == 6


def test_rate_limit_waits_then_gives_up(tmp_path: Path) -> None:
    out = tmp_path / "feed.jsonl"
    fake = FakeDiscord([1, 2])
    t = FakeTime()
    fake.queued.append(Response(429, {"x-ratelimit-scope": "user"}, b'{"retry_after": 3.0}'))
    assert make(fake, t).download(str(out)) == 2
    assert max(t.slept) >= 4.0

    limited: Any = Response(429, {}, b'{"retry_after": 1}')
    fake.queued += [limited, limited, limited]
    with pytest.raises(DownloadError):
        make(fake, t).download(str(out))


def test_bucket_exhaustion_waits_for_reset(tmp_path: Path) -> None:
    out = tmp_path / "feed.jsonl"
    fake = FakeDiscord([1])
    t = FakeTime()
    fake.queued.append(Response(200, {"x-ratelimit-remaining": "0", "x-ratelimit-reset-after": "2.5"},
                                b'[{"id": "1"}]'))
    assert make(fake, t).download(str(out)) == 1
    assert max(t.slept) >= 2.5


def test_auth_failure_stops(tmp_path: Path) -> None:
    fake = FakeDiscord([])
    fake.queued.append(Response(403, {}, b'{"message": "Missing Access"}'))
    with pytest.raises(DownloadError):
        make(fake, FakeTime()).download(str(tmp_path / "f.jsonl"))
