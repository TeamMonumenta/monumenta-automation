import os
import logging
from pprint import pformat
import yaml

CONFIG_DIR = os.environ.get("TASK_HOME", os.path.expanduser("~/.task_bot/"))
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.yml")

# Read the bot's config file
with open(CONFIG_PATH, 'r') as ymlfile:
    bot_config = yaml.load(ymlfile, Loader=yaml.FullLoader)

LOGIN = bot_config["login"]
APPLICATION_ID = bot_config["application_id"]
GUILD_ID = bot_config["guild_id"]
DATABASE_PATH = bot_config["database_path"]
BOT_INPUT_CHANNEL = bot_config["bot_input_channel"]
CHANNEL_ID = bot_config["channel_id"]
DISCUSSION_ID = bot_config["discussion_id"]
PREFIX = bot_config["prefix"]
DESCRIPTOR_SHORT = bot_config["descriptor_short"]
DESCRIPTOR_SINGLE = bot_config["descriptor_single"]
DESCRIPTOR_PROPER = bot_config["descriptor_proper"]
DESCRIPTOR_PLURAL = bot_config["descriptor_plural"]
USER_PRIVILEGES = bot_config["user_privileges"]
GROUP_PRIVILEGES = bot_config["group_privileges"]
REACTIONS = bot_config["reactions"]

KANBOARD = bot_config.get("kanboard", None)

logging.info("\nBot Configuration: %s\n", pformat(bot_config))
