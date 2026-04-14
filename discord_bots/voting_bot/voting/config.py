# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Byron Marohn
from dataclasses import dataclass
from typing import Any, cast

import yaml


@dataclass
class DiscordConfig:
    allowed_role_ids: set[int]
    # Role IDs whose names are captured and stored alongside each vote entry.
    # If empty, no roles are logged. Configure by ID (add a comment for the name).
    logged_role_ids: set[int]


@dataclass
class VotingConfig:
    data_dir: str
    guild_id: int
    discord: DiscordConfig


def load_config(path: str) -> VotingConfig:
    """Load and validate config from a YAML file. Raises on invalid config."""
    with open(path, encoding='utf-8') as f:
        data: dict[str, Any] = yaml.safe_load(f) or {}

    discord_data = cast(dict[str, Any], data.get('discord') or {})
    raw_allowed = cast(list[Any], discord_data.get('allowed_role_ids') or [])
    raw_logged = cast(list[Any], discord_data.get('logged_role_ids') or [])
    discord = DiscordConfig(
        allowed_role_ids=set(int(r) for r in raw_allowed),
        logged_role_ids=set(int(r) for r in raw_logged),
    )

    raw_guild_id = data.get('guild_id')
    if raw_guild_id is None:
        raise ValueError("guild_id is required in config")

    return VotingConfig(
        data_dir=str(data.get('data_dir', '/data')),
        guild_id=int(raw_guild_id),
        discord=discord,
    )
