#!/usr/bin/env python3
"""Task bot entry point: the Discord bot and the network API in one process.

Reads $TASK_HOME/config.yml (default ~/.task_bot/config.yml) and opens the
database it names, which must already exist (see taskbot/db.py).
"""

import asyncio
import logging
import os
import signal
import sys
from typing import Any

from taskbot import config as config_mod
from taskbot.api import create_app
from taskbot.charts import ChartRenderer
from taskbot.service import TaskService
from taskbot.store import TaskStore

logger = logging.getLogger("taskbot")


def open_store(cfg: config_mod.InstanceConfig) -> TaskStore:
    db_file = cfg.db_file
    if not os.path.exists(db_file):
        sys.exit(f"No database at {db_file}. Create it first: `python -m taskbot.legacy import` "
                 "(cutover) or `python -m taskbot.db init` (a new, empty tracker).")
    store = TaskStore.open(db_file)
    if store.is_empty():
        store.close()
        sys.exit(f"{db_file} has no entries and no numbering, which is what an import that "
                 "failed part way leaves behind. Delete it and create it again.")
    return store


async def run(cfg: config_mod.InstanceConfig) -> int:
    """Run until a signal or until the bot or API stops. Returns the exit status."""
    from taskbot.bot import TaskBot  # imported here so tools importing main need no discord

    store = open_store(cfg)
    service = TaskService(store, cfg)
    charts = ChartRenderer(store, cfg, service.now)
    bot = TaskBot(cfg, service, charts)
    app = create_app(service, bot, charts)
    internal_app = create_app(service, bot, charts, internal=True)

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop.set)

    async def stopped() -> None:
        await stop.wait()

    # shutdown_trigger: otherwise Hypercorn installs its own signal handlers over ours, and
    # a SIGTERM stops one API by itself, which reads as an unexpected stop
    tasks: list[asyncio.Task[Any]] = [
        asyncio.create_task(app.run_task(host="0.0.0.0", port=cfg.api_port, shutdown_trigger=stopped),
                            name="api"),
        asyncio.create_task(internal_app.run_task(host="0.0.0.0", port=config_mod.API_INTERNAL_PORT,
                                                  shutdown_trigger=stopped),
                            name="api-internal"),
        asyncio.create_task(bot.start(cfg.login), name="discord"),
    ]
    stop_task = asyncio.create_task(stop.wait(), name="stop")
    done, _ = await asyncio.wait([stop_task, *tasks], return_when=asyncio.FIRST_COMPLETED)
    status = 0
    for task in done:
        if task is not stop_task and not stop.is_set():
            # The bot or the API ended without being asked to: exit non-zero so it gets restarted
            status = 1
            if task.exception() is not None:
                logger.error("%s stopped", task.get_name(), exc_info=task.exception())
    logger.info("Shutting down...")
    bot.stopping = True
    await bot.close()
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    store.close()
    logger.info("Shutdown complete")
    return status


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    cfg = config_mod.load()
    logger.info("Starting %s bot: prefix=%s db=%s api_port=%s", cfg.descriptor_single, cfg.prefix,
                cfg.db_file, cfg.api_port)
    sys.exit(asyncio.run(run(cfg)))


if __name__ == "__main__":
    main()
