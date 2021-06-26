#!/usr/bin/env python3

import shutil
import sys
import os
import yaml
import asyncio
import traceback
from pprint import pprint

from lib_py3.lib_sockets import SocketManager
from lib_py3.lib_k8s import KubernetesManager

################################################################################
# Config / Environment

config = {}

if "BOT_CONFIG" in os.environ and os.path.isfile(os.environ["BOT_CONFIG"]):
    config_path = os.environ["BOT_CONFIG"]
else:
    config_dir = os.path.expanduser("~/.monumenta_bot/")
    config_path = os.path.join(config_dir, "config.yml")

# Read the bot's config files
with open(config_path, 'r') as ymlfile:
    config = yaml.load(ymlfile, Loader=yaml.FullLoader)

pprint("Config: \n{}".format(config))

socket = None
k8s = None
try:

    if "rabbitmq" in config:
        conf = config["rabbitmq"]
        if "log_level" in conf:
            log_level = conf["log_level"]
        else:
            log_level = 20

        socket = SocketManager(conf["host"], "daily_restart", durable=False, callback=None, log_level=log_level)

    k8s = KubernetesManager(config["k8s_namespace"])
except KeyError as e:
    sys.exit('Config missing key: {}'.format(e))

os.umask(0o022)

# Config / Environment
################################################################################

def send_broadcast_msg(time_left):
    socket.send_packet("*", "monumentanetworkrelay.command",
            {"command": '''tellraw @a ["",{"text":"[Alert] ","color":"red"},{"text":"Monumenta will perform its daily restart in","color":"white"},{"text":" ''' + time_left + '''","color":"red"},{"text":". This helps reduce lag! The server will be down for ~90 seconds."}]'''}
    )

async def main():
    # Short wait to make sure socket connects correctly
    await asyncio.sleep(3)

    try:
        # Set all shards to restart the next time they are empty (many will restart immediately)
        print("Broadcasting restart-empty command to all shards...")
        socket.send_packet("*", "monumentanetworkrelay.command",
                {"command": 'restart-empty'}
        )

        send_broadcast_msg("5 minutes")
        await asyncio.sleep(120)
        send_broadcast_msg("3 minutes")
        await asyncio.sleep(60)
        send_broadcast_msg("2 minutes")
        await asyncio.sleep(60)
        send_broadcast_msg("1 minute")
        await asyncio.sleep(30)
        send_broadcast_msg("30 seconds")
        await asyncio.sleep(15)
        send_broadcast_msg("15 seconds")
        await asyncio.sleep(10)
        send_broadcast_msg("5 seconds")
        await asyncio.sleep(5)
    except:
        print("Failed to notify players about pending restart: {}".format(traceback.format_exc()))

    # Read the BungeeDisplay config file
    with open(f'{config["shards"]["bungee"]}/plugins/BungeeDisplay/config.yml', 'r') as ymlfile:
        bungee_display_yml = yaml.load(ymlfile, Loader=yaml.FullLoader)

    # Modify the file to set maintenance mode - this kicks everyone
    bungee_display_yml["maintenance"]["enabled"] = True
    bungee_display_yml["maintenance"]["join"] = '&cMonumenta is currently down for daily restart - try again in a few minutes'
    bungee_display_yml["maintenance"]["kick_message"] = '&cMonumenta is going down for daily restart - join again in 5 minutes'
    bungee_display_yml["maintenance"]["information"] = '&6Please try again in a few minutes'
    bungee_display_yml["motd"]["maintenance"]["line2"] = '              &c&lDown for Daily Restart'
    with open(f'{config["shards"]["bungee"]}/plugins/BungeeDisplay/config.yml', 'w') as ymlfile:
        yaml.dump(bungee_display_yml, ymlfile, default_flow_style=False)

    # Just a bit of time to process config and kick players
    await asyncio.sleep(5)

    # Restart bungee
    print("Restarting bungee...")
    socket.send_packet("bungee", "Monumenta.Bungee.Command", {"command": "end"})

    # At this point shards that didn't already restart will do so

    # Enough time for everything to stabilize
    await asyncio.sleep(85)

    # Turn maintenance mode back off
    bungee_display_yml["maintenance"]["enabled"] = False
    with open(f'{config["shards"]["bungee"]}/plugins/BungeeDisplay/config.yml', 'w') as ymlfile:
        yaml.dump(bungee_display_yml, ymlfile, default_flow_style=False)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
