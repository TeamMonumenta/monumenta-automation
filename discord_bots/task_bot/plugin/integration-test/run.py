#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Byron Marohn
"""End-to-end test of the task bot plugin: a real Paper server, a real task bot API, and
simulated players.

1. Starts the task bot API (api_server.py, on a temporary database) with a service token.
2. Starts Paper 1.20.4 (offline mode, flat world) with CommandAPI and the freshly built
   plugin, configured for that API.
3. Connects two headless players with monumenta-testbot: a regular player with the
   permissions players would get, and an op.
4. Reports, searches, closes, notices and permission checks through real commands, and
   checks both what the players see in chat and what the API recorded.

Usage:  ./run.py [--no-build] [--keep]
Needs:  Java 21, the task bot's venv (make venv), ~/dev/monumenta/monumenta-testbot built.
Paper and CommandAPI are downloaded once into integration-test/.cache/.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
import uuid
from pathlib import Path
from typing import Any, Optional

HERE = Path(__file__).resolve().parent
PLUGIN_DIR = HERE.parent
TASK_BOT_DIR = PLUGIN_DIR.parent
CACHE = HERE / ".cache"
TESTBOT = Path(os.environ.get("TESTBOT_DIR", Path.home() / "dev/monumenta/monumenta-testbot"))
PAPER_VERSION = "1.20.4"
PAPER_BUILD_URL = "https://fill.papermc.io/v3/projects/paper/versions/1.20.4/builds/latest"
COMMANDAPI_URL = "https://github.com/JorelAli/CommandAPI/releases/download/9.4.1/CommandAPI-9.4.1.jar"
USER_AGENT = "monumenta-task-bot-plugin-integration-test"

PLAYER = "tb_alice"
MOD = "tb_mod"

# What players would be granted on prod (by the permissions plugin); ops get everything
PERMISSIONS_YML = """
monumenta.taskbot.players:
  default: true
  children:
    monumenta.taskbot.bug.create: true
    monumenta.taskbot.bug.view: true
    monumenta.taskbot.bug.notify: true
    monumenta.taskbot.bug.append.own: true
    monumenta.taskbot.bug.reject.own: true
"""


def offline_uuid(name: str) -> str:
    """Java's UUID.nameUUIDFromBytes("OfflinePlayer:" + name)."""
    return str(uuid.UUID(bytes=hashlib.md5(f"OfflinePlayer:{name}".encode()).digest(), version=3))


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def download(url: str, target: Path, sha256: Optional[str] = None) -> None:
    if target.exists():
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    print(f"downloading {url}")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = resp.read()
    if sha256 is not None and hashlib.sha256(data).hexdigest() != sha256.lower():
        sys.exit(f"{url} doesn't match its published checksum")
    target.write_bytes(data)


def paper_jar() -> Path:
    jar = CACHE / "jars" / f"paper-{PAPER_VERSION}.jar"
    if jar.exists():
        return jar
    req = urllib.request.Request(PAPER_BUILD_URL, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp:
        build = json.load(resp)
    server = build["downloads"]["server:default"]
    download(server["url"], jar, (server.get("checksums") or {}).get("sha256"))
    return jar


def plugin_jar() -> Path:
    jars = [p for p in (PLUGIN_DIR / "build/libs").glob("MonumentaTaskBot-*.jar")
            if not p.name.endswith(("-sources.jar", "-javadoc.jar"))]
    if not jars:
        sys.exit("no plugin jar; run without --no-build")
    return max(jars, key=lambda p: p.stat().st_mtime)


class Checks:
    def __init__(self) -> None:
        self.failed: list[str] = []
        self.passed = 0

    def check(self, ok: bool, what: str, detail: Any = "") -> None:
        if ok:
            self.passed += 1
            print(f"  ok   {what}")
        else:
            self.failed.append(what)
            print(f"  FAIL {what} {detail}")


class Api:
    def __init__(self, url: str, token: str):
        self.url = url
        self.token = token

    def call(self, method: str, path: str, body: Optional[dict[str, Any]] = None) -> Any:
        data = json.dumps(body).encode() if body is not None else None
        # As the op, with team privilege, the way the plugin would for a moderator
        req = urllib.request.Request(self.url + path, data=data, method=method, headers={
            "Authorization": f"Bearer {self.token}", "Content-Type": "application/json",
            "X-Taskbot-Player": offline_uuid(MOD), "X-Taskbot-Player-Name": MOD,
            "X-Taskbot-Privilege": "2"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.load(resp)


class Tb:
    def __init__(self) -> None:
        self.bin = str(TESTBOT / "bin/tb")

    def run(self, *args: str, timeout: float = 60) -> str:
        out = subprocess.run([self.bin, *args], capture_output=True, text=True, timeout=timeout)
        if out.returncode != 0:
            raise RuntimeError(f"tb {' '.join(args)} failed: {out.stderr.strip() or out.stdout.strip()}")
        return out.stdout.strip()

    def mark(self) -> str:
        return self.run("mark", "step").split()[-1]

    def cmd(self, bot: str, command: str) -> str:
        """Run a command as a bot; returns the mark to wait from."""
        m = self.mark()
        self.run("cmd", bot, command)
        return m

    def wait_chat(self, bot: str, pattern: str, since: str, timeout: float = 20) -> Optional[str]:
        try:
            out = self.run("wait", bot, "--type", "chat", "--match", pattern, "--since", since,
                           "--timeout", str(timeout), "--json", timeout=timeout + 10)
        except RuntimeError:
            return None
        return out or None

    def chat_since(self, bot: str, since: str) -> str:
        return self.run("events", bot, "--type", "chat", "--since", since)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-build", action="store_true")
    parser.add_argument("--keep", action="store_true", help="leave the server directory for inspection")
    args = parser.parse_args()

    if not args.no_build:
        subprocess.run(["./gradlew", "build", "-q", "-x", "test"], cwd=PLUGIN_DIR, check=True)
    download(COMMANDAPI_URL, CACHE / "jars/CommandAPI-9.4.1.jar")
    paper = paper_jar()

    checks = Checks()
    procs: list[subprocess.Popen[str]] = []
    tb = Tb()
    server_dir = CACHE / "server"
    try:
        # 1. The task bot API
        api_port = free_port()
        api_proc = subprocess.Popen([str(TASK_BOT_DIR / ".venv/bin/python"), str(HERE / "api_server.py"),
                                     str(api_port)], cwd=TASK_BOT_DIR, stdout=subprocess.PIPE,
                                    stderr=subprocess.DEVNULL, text=True)
        procs.append(api_proc)
        assert api_proc.stdout is not None
        info = json.loads(api_proc.stdout.readline())
        api = Api(info["url"], info["token"])
        for _ in range(50):
            try:
                api.call("GET", "/api/health")
                break
            except OSError:
                time.sleep(0.1)
        else:
            raise RuntimeError(f"the task bot API on {info['url']} never answered")
        print(f"task bot API on {info['url']}")

        # 2. Paper with CommandAPI and the plugin
        (server_dir / "plugins").mkdir(parents=True, exist_ok=True)
        for old in (server_dir / "plugins").glob("*.jar"):
            old.unlink()
        shutil.copy(CACHE / "jars/CommandAPI-9.4.1.jar", server_dir / "plugins")
        shutil.copy(plugin_jar(), server_dir / "plugins/MonumentaTaskBot.jar")
        mc_port = free_port()
        (server_dir / "eula.txt").write_text("eula=true\n")
        (server_dir / "server.properties").write_text(
            # Offline mode with an op: only reachable from this machine
            f"server-ip=127.0.0.1\nserver-port={mc_port}\nonline-mode=false\nlevel-type=minecraft\\:flat\n"
            'generator-settings={"layers":[{"block":"minecraft:bedrock","height":1}],"biome":"minecraft:plains"}\n'
            "generate-structures=false\nspawn-protection=0\n")
        (server_dir / "permissions.yml").write_text(PERMISSIONS_YML)
        (server_dir / "ops.json").write_text(json.dumps([{
            "uuid": offline_uuid(MOD), "name": MOD, "level": 4, "bypassesPlayerLimit": False}]))
        # A second instance (pointed at the same API) that players are granted nothing for
        env = dict(os.environ, TASKBOT_INSTANCES="bug suggestion", TASKBOT_BUG_URL=info["url"],
                   TASKBOT_BUG_TOKEN=info["token"], TASKBOT_SUGGESTION_URL=info["url"],
                   TASKBOT_SUGGESTION_TOKEN=info["token"], TASKBOT_SERVER_NAME="it-shard",
                   TASKBOT_REPORT_COOLDOWN_SECONDS="0")
        log = open(server_dir / "it.log", "w", encoding="utf-8")  # pylint: disable=consider-using-with
        mc = subprocess.Popen(["java", "-Xmx1G", "-jar", str(paper), "--nogui"], cwd=server_dir, env=env,
                              stdin=subprocess.PIPE, stdout=log, stderr=subprocess.STDOUT, text=True)
        procs.append(mc)
        deadline = time.monotonic() + 300
        while time.monotonic() < deadline:
            text = (server_dir / "it.log").read_text(errors="replace")
            if "Done (" in text:
                break
            if mc.poll() is not None:
                sys.exit("Paper exited during startup; see " + str(server_dir / "it.log"))
            time.sleep(1)
        else:
            sys.exit("Paper did not start in time")
        # The command is registered once the plugin has the tracker's labels
        deadline = time.monotonic() + 30
        while "Registered /bug with labels" not in (server_dir / "it.log").read_text(errors="replace") \
                and time.monotonic() < deadline:
            time.sleep(1)
        text = (server_dir / "it.log").read_text(errors="replace")
        checks.check("Registered /bug with labels [misc, quest, item]" in text,
                     "plugin registered /bug with the tracker's labels")

        # 3. Players
        tb.run("daemon", "start", "--host", "127.0.0.1", "--port", str(mc_port))
        tb.run("connect", PLAYER, MOD, timeout=120)
        time.sleep(2)

        # 4. Scenarios
        print("player reports a bug")
        m = tb.cmd(PLAYER, "bug report quest the lever in the tower does nothing when pulled")
        checks.check(tb.wait_chat(PLAYER, r"filed\. Thank you", m) is not None, "report confirmed in chat",
                     tb.chat_since(PLAYER, m))
        entries = api.call("GET", "/api/entries?status=all")["entries"]
        checks.check(len(entries) == 1, "the API has the entry", entries)
        entry = entries[0] if entries else {}
        author = entry.get("author") or {}
        checks.check(author.get("kind") == "minecraft" and author.get("uuid") == offline_uuid(PLAYER)
                     and author.get("name") == PLAYER, "authored by the player", author)
        checks.check(entry.get("labels") == ["quest"], "filed with the chosen label", entry.get("labels"))
        ctx = api.call("GET", f"/api/entries/{entry.get('id', 1)}/context")["context"]
        location = next((c["data"] for c in ctx if c["section"] == "location"), {})
        checks.check(location.get("server") == "it-shard" and "world" in location and "x" in location,
                     "location context attached", ctx)

        print("player lists and reads")
        m = tb.cmd(PLAYER, "bug mine")
        checks.check(tb.wait_chat(PLAYER, r"#1 open", m) is not None, "/bug mine lists it", tb.chat_since(PLAYER, m))
        m = tb.cmd(PLAYER, "bug search lever tower")
        checks.check(tb.wait_chat(PLAYER, r"#1 open", m) is not None, "/bug search finds it", tb.chat_since(PLAYER, m))
        m = tb.cmd(PLAYER, "bug get 1")
        checks.check(tb.wait_chat(PLAYER, r"By tb_alice, open", m) is not None, "/bug get shows it",
                     tb.chat_since(PLAYER, m))

        print("permissions")
        m = tb.cmd(PLAYER, "bug fix 1")
        time.sleep(2)
        chat = tb.chat_since(PLAYER, m)
        # The headless client shows the untranslated key (command.unknown.*)
        checks.check("closed as fixed" not in chat and ("command.unknown" in chat or "Unknown" in chat),
                     "a player can't fix", chat)
        m = tb.cmd(PLAYER, "suggestion report misc players should not see this command at all")
        time.sleep(2)
        chat = tb.chat_since(PLAYER, m)
        checks.check("command.unknown" in chat or "Unknown" in chat,
                     "a command with no granted operations is hidden", chat)
        m = tb.cmd(PLAYER, "bug report nolabel this label does not exist anywhere")
        time.sleep(2)
        chat = tb.chat_since(PLAYER, m)
        checks.check("filed" not in chat and ("command.unknown" in chat or "Unknown" in chat),
                     "a label the tracker doesn't have is refused", chat)
        m = tb.cmd(PLAYER, "bug report misc too short")
        checks.check(tb.wait_chat(PLAYER, r"at least 5 words", m) is not None,
                     "short reports are caught in game", tb.chat_since(PLAYER, m))
        m = tb.cmd(PLAYER, "bug context 1")
        time.sleep(2)
        chat = tb.chat_since(PLAYER, m)
        checks.check("location" not in chat, "a player can't see context", chat)
        m = tb.cmd(PLAYER, "bug append 1 it happens every time after a restart")
        checks.check(tb.wait_chat(PLAYER, r"#1 updated", m) is not None, "the author can append to their own",
                     tb.chat_since(PLAYER, m))
        m = tb.cmd(MOD, "bug report item the mod also found a broken door in town")
        checks.check(tb.wait_chat(MOD, r"filed", m) is not None, "a second player can report",
                     tb.chat_since(MOD, m))
        m = tb.cmd(PLAYER, "bug reject 2 not my report")
        checks.check(tb.wait_chat(PLAYER, r"do not have permission to reject #2", m) is not None,
                     "the server refuses rejecting someone else's report (own-only permission)",
                     tb.chat_since(PLAYER, m))

        print("moderator closes, the player gets a notice")
        m = tb.cmd(MOD, "bug context 1")
        checks.check(tb.wait_chat(MOD, r"location:.*it-shard", m) is not None, "an op sees context",
                     tb.chat_since(MOD, m))
        m = tb.cmd(MOD, "bug priority 1 hi")
        checks.check(tb.wait_chat(MOD, r"#1 priority set to High", m) is not None,
                     "priority from the tracker's vocabulary", tb.chat_since(MOD, m))
        m = tb.cmd(MOD, "bug fix 1 the lever is wired up now")
        checks.check(tb.wait_chat(MOD, r"#1 closed as fixed", m) is not None, "an op can fix", tb.chat_since(MOD, m))
        closed = api.call("GET", "/api/entries/1")
        checks.check((closed.get("closed_by") or {}).get("uuid") == offline_uuid(MOD), "closed_by is the op",
                     closed.get("closed_by"))
        queued = api.call("POST", "/test/notify")["queued"]
        checks.check(queued == 1, "one in-game notice queued", queued)
        m = tb.mark()
        tb.run("disconnect", PLAYER)
        tb.run("connect", PLAYER, timeout=120)
        checks.check(tb.wait_chat(PLAYER, r"Your bug #1 was closed \(fixed\): the lever is wired up now", m,
                                  timeout=30) is not None, "notice shown after rejoining", tb.chat_since(PLAYER, m))
        time.sleep(2)
        pending = api.call("POST", "/test/notify")["queued"]
        checks.check(pending == 0, "notice marked delivered", pending)

        print("notification settings")
        m = tb.cmd(PLAYER, "bug notify off")
        checks.check(tb.wait_chat(PLAYER, r"will not get notices", m) is not None, "/bug notify off",
                     tb.chat_since(PLAYER, m))
    finally:
        try:
            tb.run("daemon", "stop")
        except (RuntimeError, OSError, subprocess.TimeoutExpired):
            pass
        for p in reversed(procs):
            if p.poll() is None:
                if p.stdin is not None:
                    try:
                        p.stdin.write("stop\n")
                        p.stdin.flush()
                        p.wait(timeout=60)
                    except (OSError, subprocess.TimeoutExpired):
                        p.kill()
                else:
                    p.terminate()
                    p.wait(timeout=10)
        if not args.keep:
            for leftover in ("world", "world_nether", "world_the_end"):
                shutil.rmtree(server_dir / leftover, ignore_errors=True)

    print(f"\n{checks.passed} passed, {len(checks.failed)} failed")
    for f in checks.failed:
        print(f"  failed: {f}")
    return 1 if checks.failed else 0


if __name__ == "__main__":
    sys.exit(main())
