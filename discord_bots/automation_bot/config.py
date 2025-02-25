import os
import logging
from pathlib import Path
from pprint import pformat
import yaml

# TODO: This is ugly and needs updating if we ever move this file
_file_depth = 3
_file = Path(__file__).absolute()
_top_level = _file.parents[_file_depth-1]


if "BOT_CONFIG" in os.environ and os.path.isfile(os.environ["BOT_CONFIG"]):
    AUTH_PATH = Path(os.environ["BOT_CONFIG"])
    AUTH_DIR = AUTH_PATH.parent
else:
    AUTH_DIR = Path("~/.monumenta_bot/").expanduser()
    AUTH_PATH = AUTH_DIR / "config.yml"

# Read the bot's auth files
with open(AUTH_PATH, 'r') as ymlfile:
    bot_auth = yaml.load(ymlfile, Loader=yaml.FullLoader)

logging.info("\nBot Authorization: %s\n", pformat(bot_auth))

old_umask = os.umask(0o022)
logging.info("New umask=0o022, old umask=%s", oct(old_umask))

NAME = bot_auth["name"]
LOGIN = bot_auth["login"]
APPLICATION_ID = bot_auth["application_id"]
GUILD_ID = bot_auth["guild_id"]

CONFIG_DIR = _top_level / 'discord_bots/automation_bot/configs'
CONFIG_PATH = CONFIG_DIR / f'{NAME}.yml'

# Read the bot's config files
with open(CONFIG_PATH, 'r') as ymlfile:
    bot_config = yaml.load(ymlfile, Loader=yaml.FullLoader)


PREFIX = bot_config["prefix"]
RABBITMQ = bot_config.get("rabbitmq", None)
K8S_NAMESPACE = bot_config["k8s_namespace"]
REACTIONS_ENABLED = bot_config["reactions_enabled"]
REACTIONS_LOG_LEVEL = logging.DEBUG # TODO configurable
IGNORED_REACTION_CHANNELS = bot_config["ignored_reaction_channels"]
CHANNELS = bot_config["channels"]
NO_READY_MESSAGE_CHANNELS = bot_config.get("no_ready_message_channels", [])
STATUS_CHANNEL = bot_config.get("status_channel", None)
SERVER_DIR = bot_config["server_dir"]
SHARDS = bot_config["shards"]
COMMANDS = bot_config["commands"]
PERMISSIONS = bot_config["permissions"]
STAGE_SOURCE = bot_config.get("stage_source", None)
COMMON_WEEKLY_UPDATE_TASKS = bot_config.get("common_weekly_update_tasks", True)

CPU_COUNT = bot_config.get("cpu_count", -1)
if CPU_COUNT < 1:
    CPU_COUNT = os.cpu_count()
    if not isinstance(CPU_COUNT, int) or CPU_COUNT < 1:
        CPU_COUNT = 1
