"""Instance configuration, read from the same config.yml the original bot used.

The bug and suggestion deployments run the same code; everything that differs
between them lives in this file's inputs.
"""

import os
from dataclasses import dataclass, field
from typing import Any, Optional

import yaml


# The cluster-only API listener, the only one that accepts service tokens (the game plugin).
# Fixed, since the shards' configuration names it.
API_INTERNAL_PORT = 8081


@dataclass
class InstanceConfig:
    # Discord
    login: str = ""
    application_id: int = 0
    guild_id: int = 0
    bot_input_channel: int = 0   # where commands are typed (e.g. #bug-report-bot-feed)
    channel_id: int = 0          # where entries are tracked (e.g. #bug-reports)
    discussion_id: int = 0       # where `bug-123` mentions are expanded

    # Wording
    prefix: str = "~bug"
    descriptor_short: str = "bug"
    descriptor_single: str = "bug"
    descriptor_proper: str = "Bug"
    descriptor_plural: str = "bugs"

    # Privileges: 0 everyone, 1 author/trusted, 2 team, 3 leads, 4 owner
    user_privileges: dict[int, int] = field(default_factory=dict[int, int])
    group_privileges: dict[int, int] = field(default_factory=dict[int, int])

    reactions: list[str] = field(default_factory=list[str])

    # Storage
    config_dir: str = "."
    db_path: str = "tasks.db"

    # Network API
    api_port: int = 8080
    api_token_default_ttl_hours: int = 24 * 30
    api_token_max_ttl_hours: int = 24 * 365
    # Shown to users when they create a token, e.g. https://bugs-api.playmonumenta.com
    api_public_url: Optional[str] = None

    # Display names for resolutions, e.g. {"fixed": "implemented"} for suggestions.
    # Only affects new output (history, cstats, API); the stored values never change.
    resolution_names: dict[str, str] = field(default_factory=dict[str, str])

    def resolve(self, path: str) -> str:
        return path if os.path.isabs(path) else os.path.join(self.config_dir, path)

    @property
    def db_file(self) -> str:
        return self.resolve(self.db_path)

    @property
    def images_dir(self) -> str:
        """Saved copies of entries' images (images.py), next to the database."""
        return self.resolve("images")

    def entry_link(self, message_id: int) -> str:
        return f"https://discord.com/channels/{self.guild_id}/{self.channel_id}/{message_id}"


def _int_keyed(raw: Any) -> dict[int, int]:
    if not raw:
        return {}
    return {int(k): int(v) for k, v in dict(raw).items()}


def from_dict(data: dict[str, Any], config_dir: str = ".") -> InstanceConfig:
    """Build a config from parsed YAML. Unknown keys are ignored."""
    cfg = InstanceConfig(
        login=str(data.get("login", "")),
        application_id=int(data.get("application_id", 0)),
        guild_id=int(data.get("guild_id", 0)),
        bot_input_channel=int(data.get("bot_input_channel", 0)),
        channel_id=int(data.get("channel_id", 0)),
        discussion_id=int(data.get("discussion_id", 0)),
        prefix=str(data.get("prefix", "~bug")),
        descriptor_short=str(data.get("descriptor_short", "bug")),
        descriptor_single=str(data.get("descriptor_single", "bug")),
        descriptor_proper=str(data.get("descriptor_proper", "Bug")),
        descriptor_plural=str(data.get("descriptor_plural", "bugs")),
        user_privileges=_int_keyed(data.get("user_privileges")),
        group_privileges=_int_keyed(data.get("group_privileges")),
        reactions=[str(r) for r in list(data.get("reactions") or [])],
        config_dir=config_dir,
        db_path=str(data.get("db_path", "tasks.db")),
        api_port=int(data.get("api_port", 8080)),
        api_token_default_ttl_hours=int(data.get("api_token_default_ttl_hours", 24 * 30)),
        api_token_max_ttl_hours=int(data.get("api_token_max_ttl_hours", 24 * 365)),
        api_public_url=str(data["api_public_url"]) if data.get("api_public_url") else None,
        resolution_names={str(k): str(v) for k, v in dict(data.get("resolution_names") or {}).items()},
    )
    # A token in the environment (from a Kubernetes secret) wins over config.yml
    if os.environ.get("DISCORD_TOKEN"):
        cfg.login = os.environ["DISCORD_TOKEN"]
    return cfg


def load(config_dir: Optional[str] = None) -> InstanceConfig:
    """Load $TASK_HOME/config.yml (default ~/.task_bot/config.yml), as the old bot did."""
    if config_dir is None:
        config_dir = os.environ.get("TASK_HOME", os.path.expanduser("~/.task_bot/"))
    with open(os.path.join(config_dir, "config.yml"), "r", encoding="utf-8") as f:
        data: dict[str, Any] = dict(yaml.safe_load(f) or {})
    return from_dict(data, config_dir)
