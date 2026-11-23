# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Byron Marohn
"""A real task bot API on a temporary database, for the plugin's end-to-end test.

Run with the task bot's venv from discord_bots/task_bot (run.py does this). Prints one
JSON line {"url", "token", "db"} once listening. Discord is absent, so only the service
token works (this serves the internal listener, the one shards use). POST /test/notify runs
the real `~bug send_notifications` command, which queues in-game notices.
"""

import asyncio
import json
import os
import sys
import tempfile
from typing import Any, Optional

sys.path.insert(0, os.getcwd())

# pylint: disable=wrong-import-position
from quart import jsonify

from taskbot.api import create_app
from taskbot.charts import ChartRenderer
from taskbot.commands import CommandHandler, IncomingMessage, OutFile
from taskbot.config import InstanceConfig
from taskbot.models import Member
from taskbot.service import TaskService, UserError
from taskbot.store import TaskStore
from taskbot.tokens import mint_service_token


class NoDiscord:
    def resolve_member(self, user_id: int) -> Optional[Member]:  # pylint: disable=unused-argument
        return None

    def user_name(self, user_id: int) -> Optional[str]:  # pylint: disable=unused-argument
        return None

    def find_user(self, query: str) -> tuple[int, str]:
        raise UserError(f"User {query!r} not found")

    def is_ready(self) -> bool:
        return True

    async def refresh_images(self, images: Any) -> None:
        pass


async def main() -> None:
    port = int(sys.argv[1])
    tmp = tempfile.mkdtemp(prefix="taskbot-it-")
    cfg = InstanceConfig(descriptor_single="bug", descriptor_plural="bugs", descriptor_proper="Bug",
                         prefix="~bug", config_dir=tmp)
    store = TaskStore.open(os.path.join(tmp, "tasks.db"))
    store.set_label_list(["misc", "quest", "item"])
    store.set_meta("next_index", "1")
    service = TaskService(store, cfg)
    token = mint_service_token(service, "integration-test", 2, 1)[0]
    directory = NoDiscord()
    app = create_app(service, directory, ChartRenderer(store, cfg, service.now), internal=True)
    handler = CommandHandler(service, directory)  # type: ignore[arg-type]

    class Replies:
        def __init__(self) -> None:
            self.texts: list[str] = []

        async def send(self, text: str, *, images: Any = (), file: Optional[OutFile] = None,
                       mentions: Any = ()) -> None:  # pylint: disable=unused-argument
            self.texts.append(text)

    @app.post("/test/notify")
    async def notify() -> Any:
        replies = Replies()
        await handler.cmd_send_notifications(
            IncomingMessage(content="", author_id=1, author_name="team", privilege=2), "", replies)
        players = {e.author_mc_uuid for e in store.all_entries() if e.author_mc_uuid}
        queued = sum(len(store.pending_notices(uuid)) for uuid in players)
        return jsonify({"queued": queued, "replies": replies.texts})

    print(json.dumps({"url": f"http://127.0.0.1:{port}", "token": token,
                      "db": os.path.join(tmp, "tasks.db")}), flush=True)
    await app.run_task(host="127.0.0.1", port=port)


if __name__ == "__main__":
    asyncio.run(main())
