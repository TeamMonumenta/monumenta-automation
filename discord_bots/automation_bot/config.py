import os
import logging
from pprint import pformat
import yaml

if "BOT_CONFIG" in os.environ and os.path.isfile(os.environ["BOT_CONFIG"]):
    CONFIG_PATH = os.environ["BOT_CONFIG"]
    CONFIG_DIR = os.path.dirname(CONFIG_PATH)
else:
    CONFIG_DIR = os.path.expanduser("~/.monumenta_bot/")
    CONFIG_PATH = os.path.join(CONFIG_DIR, "config.yml")

# Read the bot's config files
with open(CONFIG_PATH, 'r') as ymlfile:
    bot_config = yaml.load(ymlfile, Loader=yaml.FullLoader)

logging.info("\nBot Configuration: %s\n", pformat(bot_config))

old_umask = os.umask(0o022)
logging.info("New umask=0o022, old umask=%s", oct(old_umask))

NAME = bot_config["name"]
LOGIN = bot_config["login"]
APPLICATION_ID = bot_config["application_id"]
GUILD_ID = bot_config["guild_id"]

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
