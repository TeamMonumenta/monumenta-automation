# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Byron Marohn
import asyncio
import logging
import os
import signal

from voting.config import load_config
from voting.store import VoteStore

logger = logging.getLogger(__name__)


def _mask_token(token: str) -> str:
    if len(token) <= 2:
        return '*' * len(token)
    return token[0] + '*' * (len(token) - 2) + token[-1]


async def main() -> None:
    config_path = os.environ.get('CONFIG_PATH', './config.yml')
    config = load_config(config_path)

    discord_token = os.environ.get('DISCORD_TOKEN')
    if not discord_token:
        raise RuntimeError("DISCORD_TOKEN environment variable is required")

    logger.info(
        "Starting with config:\n"
        "  CONFIG_PATH=%s\n"
        "  data_dir=%s\n"
        "  guild_id=%s\n"
        "  allowed_role_ids=%s\n"
        "  logged_role_ids=%s\n"
        "  DISCORD_TOKEN=%s",
        config_path,
        config.data_dir,
        config.guild_id,
        sorted(config.discord.allowed_role_ids) or '(all users)',
        sorted(config.discord.logged_role_ids) or '(none)',
        _mask_token(discord_token),
    )

    store = VoteStore(config.data_dir)

    from bot import VotingBot
    bot = VotingBot(config, store)

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop.set)

    bot_task = asyncio.create_task(bot.start(discord_token), name='discord')
    stop_task = asyncio.create_task(stop.wait(), name='stop')

    done, _ = await asyncio.wait([stop_task, bot_task], return_when=asyncio.FIRST_COMPLETED)
    stop_task.cancel()

    if stop_task in done:
        logger.info('Shutdown signal received, stopping...')
        bot_task.cancel()
        await bot.close()
        await asyncio.gather(bot_task, return_exceptions=True)

    logger.info('Shutdown complete.')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
