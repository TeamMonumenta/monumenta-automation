import os
import logging
from pathlib import Path
from pprint import pformat
import yaml

# TODO: This is ugly and needs updating if we ever move this file
_file_depth = 3
_file = Path(__file__).absolute()
_top_level = _file.parents[_file_depth-1]


class Config():
    def __init__(self, auth_path=None, auth_dir=None):
        if auth_path is not None:
            self.AUTH_PATH = Path(auth_path).expanduser()
            self.AUTH_DIR = self.AUTH_PATH.parent
        elif auth_dir is not None:
            self.AUTH_DIR = Path(auth_dir).expanduser()
            self.AUTH_PATH = self.AUTH_DIR / "config.yml"
        elif "BOT_CONFIG" in os.environ and os.path.isfile(os.environ["BOT_CONFIG"]):
            self.AUTH_PATH = Path(os.environ["BOT_CONFIG"])
            self.AUTH_DIR = self.AUTH_PATH.parent
        else:
            self.AUTH_DIR = Path("~/.monumenta_bot/").expanduser()
            self.AUTH_PATH = self.AUTH_DIR / "config.yml"

        # Read the bot's auth files
        with open(self.AUTH_PATH, 'r') as ymlfile:
            bot_auth = yaml.load(ymlfile, Loader=yaml.FullLoader)

        old_umask = os.umask(0o022)
        logging.info("New umask=0o022, old umask=%s", oct(old_umask))

        self.NAME = bot_auth["name"]
        self.LOGIN = bot_auth["login"]
        self.APPLICATION_ID = bot_auth["application_id"]
        self.GUILD_ID = bot_auth["guild_id"]

        self.CONFIG_DIR = _top_level / 'discord_bots/automation_bot/configs'
        self.CONFIG_PATH = self.CONFIG_DIR / f'{self.NAME}.yml'

        # Read the bot's config files
        with open(self.CONFIG_PATH, 'r') as ymlfile:
            bot_config = yaml.load(ymlfile, Loader=yaml.FullLoader)

        logging.info("\nBot Configuration: %s\n", pformat(bot_config))

        self.PREFIX = bot_config["prefix"]
        self.RABBITMQ = bot_config.get("rabbitmq", None)
        self.K8S_NAMESPACE = bot_config["k8s_namespace"]
        self.REACTIONS_ENABLED = bot_config["reactions_enabled"]
        self.REACTIONS_LOG_LEVEL = logging.DEBUG # TODO configurable
        self.IGNORED_REACTION_CHANNELS = bot_config["ignored_reaction_channels"]
        self.CHANNELS = bot_config["channels"]
        self.NO_READY_MESSAGE_CHANNELS = bot_config.get("no_ready_message_channels", [])
        self.STATUS_CHANNEL = bot_config.get("status_channel", None)
        self.SERVER_DIR = bot_config["server_dir"]
        self.SHARDS = bot_config["shards"]
        self.COMMANDS = bot_config["commands"]
        self.PERMISSIONS = bot_config["permissions"]
        self.STAGE_SOURCE = bot_config.get("stage_source", None)
        self.COMMON_WEEKLY_UPDATE_TASKS = bot_config.get("common_weekly_update_tasks", True)
        self.ZFS_SNAPSHOT_MANAGER_CONFIG = bot_config.get("zfs_snapshot_manager", None)

        self.CPU_COUNT = bot_config.get("cpu_count", -1)
        if self.CPU_COUNT < 1:
            self.CPU_COUNT = os.cpu_count()
            if not isinstance(self.CPU_COUNT, int) or self.CPU_COUNT < 1:
                self.CPU_COUNT = 1
