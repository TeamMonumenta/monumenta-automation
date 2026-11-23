"""taskctl against a live API server on a random local port."""

import asyncio
import io
import json
import os
import socket
import sys
import threading
import time
from collections.abc import Iterator
from contextlib import redirect_stderr, redirect_stdout
from typing import Any

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cli"))
# pylint: disable=wrong-import-position,import-error,wrong-import-order
import taskctl  # noqa: E402

from conftest import ALICE, LEAD, TEAM, Harness
from taskbot.api import create_app
from taskbot.tokens import mint_token

DESC = "the quest npc refuses to talk to me"


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


class Server:
    def __init__(self, h: Harness):
        self.h = h
        self.port = _free_port()
        self.url = f"http://127.0.0.1:{self.port}"
        self._loop = asyncio.new_event_loop()
        self._stop: asyncio.Event
        self._thread = threading.Thread(target=self._run, daemon=True)

    def _run(self) -> None:
        asyncio.set_event_loop(self._loop)
        self._stop = asyncio.Event()
        app = create_app(self.h.service, self.h.port, self.h.charts)
        self._loop.run_until_complete(app.run_task(host="127.0.0.1", port=self.port,
                                                   shutdown_trigger=self._stop.wait))

    def start(self) -> None:
        self._thread.start()
        for _ in range(100):
            try:
                with socket.create_connection(("127.0.0.1", self.port), timeout=0.1):
                    return
            except OSError:
                time.sleep(0.05)
        raise RuntimeError("server did not start")

    def stop(self) -> None:
        self._loop.call_soon_threadsafe(self._stop.set)
        self._thread.join(timeout=5)


@pytest.fixture
def server(h: Harness) -> Iterator[Server]:
    s = Server(h)
    s.start()
    yield s
    s.stop()


def run(server: Server, user: int, *argv: str, stdin: str = "") -> tuple[int, str, str]:
    token = mint_token(server.h.service, user, 24, "write")[0]
    out, err = io.StringIO(), io.StringIO()
    old_stdin = sys.stdin
    sys.stdin = io.StringIO(stdin)
    try:
        with redirect_stdout(out), redirect_stderr(err):
            code = taskctl.main(list(argv), env={"TASKCTL_URL": server.url, "TASKCTL_TOKEN": token})
    finally:
        sys.stdin = old_stdin
    return code, out.getvalue(), err.getvalue()


def test_info_uses_server_words(server: Server) -> None:
    code, out, _ = run(server, TEAM, "info")
    assert code == 0 and "bugs, prefix ~bug" in out and "Team Nick (privilege 2)" in out


def test_add_list_get_pipeline(server: Server) -> None:
    assert run(server, LEAD, "add", "-l", "quest", *DESC.split())[1] == "Bug #1 created\n"
    assert run(server, TEAM, "add", "the boss fight is broken in this way")[0] == 0
    code, out, err = run(server, TEAM, "list")
    first = out.splitlines()[0]
    assert code == 0 and first.startswith("#1      open        N/A/unknown      ")
    assert first.endswith("[quest] Lead") and DESC in first
    assert err.strip() == "(2 bugs)"
    code, out, _ = run(server, TEAM, "list", "-l", "quest", "--ids")
    assert out == "1\n"
    # Compose: ids from one command feed the next
    code, out, _ = run(server, TEAM, "get", "-", "--json", stdin=out)
    assert json.loads(out)["id"] == 1
    code, out, _ = run(server, TEAM, "get", "2", "--text")
    assert out.startswith("`#2 [misc - N/A] Teammate`")
    code, out, _ = run(server, TEAM, "get", "1")
    assert "Bug #1  [quest]  N/A / unknown" in out and "author:   Lead" in out


def test_bulk_close_continues_past_failures(server: Server) -> None:
    for i in range(3):
        run(server, LEAD, "add", f"report number {i} {DESC}")
    code, out, err = run(server, TEAM, "fix", "1", "99", "3", "--reason", "done")
    assert code == 1
    assert out == "Bug #1 closed as fixed\nBug #3 closed as fixed\n"
    assert "#99: Bug #99 not found" in err and "2 of 3 done; failed: #99" in err
    code, out, _ = run(server, TEAM, "list", "--status", "closed", "--ids")
    assert out == "1\n3\n"
    # Closing again needs --force, so a sloppy pipeline can't rewrite who closed what
    code, _, err = run(server, TEAM, "reject", "1", "--reason", "x")
    assert code == 1 and "already closed (fixed) (--force closes it again)" in err
    assert run(server, TEAM, "reject", "1", "--reason", "x", "--force")[0] == 0


def test_edit_history_activity(server: Server) -> None:
    run(server, LEAD, "add", DESC)
    assert run(server, TEAM, "edit", "1", "--priority", "high", "--labels", "boss,mob")[0] == 0
    run(server, TEAM, "dupe", "1", "--of", "1")
    run(server, LEAD, "add", DESC + " again")
    assert run(server, TEAM, "dupe", "2", "--of", "1")[1] == "Bug #2 closed as a duplicate of #1\n"
    _, out, _ = run(server, TEAM, "history", "1")
    assert "priority N/A -> High" in out and "[api]" in out
    _, out, _ = run(server, TEAM, "activity", "--kind", "closed")
    assert "#2" in out and "closed as duplicate" in out


def test_stats_closers_chart(server: Server, tmp_path: Any) -> None:
    run(server, LEAD, "add", DESC)
    run(server, TEAM, "fix", "1")
    code, out, _ = run(server, TEAM, "stats")
    assert code == 0 and "closed: 1 (fixed 1)" in out
    code, out, _ = run(server, TEAM, "closers")
    assert "Teammate" in out
    target = str(tmp_path / "c.png")
    code, out, _ = run(server, TEAM, "chart", "intake", "week", "30d", "-o", target)
    assert code == 0 and out.strip() == target
    with open(target, "rb") as f:
        assert f.read(4) == b"\x89PNG"
    code, out, _ = run(server, TEAM, "chart")
    assert out.startswith("backlog")


def test_bad_token_and_unreachable(server: Server) -> None:
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = taskctl.main(["info"], env={"TASKCTL_URL": server.url, "TASKCTL_TOKEN": "nope"})
    assert code == 1 and "invalid or expired token" in err.getvalue()
    code, _, message = run(server, ALICE, "list")
    assert code == 1 and "API access is for team members" in message
    with redirect_stdout(out), redirect_stderr(err):
        code = taskctl.main(["info"], env={"TASKCTL_URL": "http://127.0.0.1:1"})
    assert code == 1 and "could not reach" in err.getvalue()
    # The token only goes over https, except to this machine
    with redirect_stdout(out), redirect_stderr(err):
        code = taskctl.main(["info"], env={"TASKCTL_URL": "http://bug-bot.example.com", "TASKCTL_TOKEN": "t"})
    assert code == 1 and "must be https://" in err.getvalue()


def test_parse_time() -> None:
    assert taskctl.parse_time("7d", now=1_000_000) == 1_000_000 - 7 * 86400
    assert taskctl.parse_time("12h", now=100_000) == 100_000 - 12 * 3600
    assert taskctl.parse_time("1700000000") == 1_700_000_000
    assert taskctl.parse_time(None) is None
    with pytest.raises(SystemExit):
        taskctl.parse_time("yesterday")
