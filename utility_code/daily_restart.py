#!/usr/bin/env python3

import asyncio
import json
import os
import sys
import traceback
from pprint import pprint
from pathlib import Path
import yaml

from lib_py3.lib_sockets import SocketManager
from lib_py3.lib_k8s import KubernetesManager

def send_broadcast_time(time_left):
    """Broadcasts a restart warning with how much time is remaining to all players"""
    raw_json_text = [
        "",
        {"text": "[Alert] ", "color": "red"},
        {"text": "Monumenta will perform its daily restart in ", "color": "white"},
        {"text": time_left, "color": "red"},
        {"text": ". This helps reduce lag! The server will be down for ~120 seconds."}
    ]
    send_broadcast_message(raw_json_text)


def send_broadcast_message(raw_json_text):
    """Broadcasts an arbitrary raw json text message to all players"""
    command = '''tellraw @a[all_worlds=true] ''' + json.dumps(raw_json_text, ensure_ascii=False, separators=(',', ':'))
    socket.send_packet("*", "monumentanetworkrelay.command",
                       {"command": command})


async def main():
    """Perform a scheduled restart with warnings"""
    # Short wait to make sure socket connects correctly
    await asyncio.sleep(3)

    try:
        send_broadcast_time("15 minutes")
        await asyncio.sleep(60)
        send_broadcast_time("14 minutes")
        await asyncio.sleep(60)
        send_broadcast_time("13 minutes")
        await asyncio.sleep(60)
        send_broadcast_time("12 minutes")
        await asyncio.sleep(60)
        send_broadcast_time("11 minutes")
        await asyncio.sleep(60)
        send_broadcast_time("10 minutes")
        await asyncio.sleep(60)
        send_broadcast_time("9 minutes")
        await asyncio.sleep(60)
        send_broadcast_time("8 minutes" )
        await asyncio.sleep(60)
        send_broadcast_time("7 minutes")
        await asyncio.sleep(60)

        # TODO: add shutoff to creating dungeon instances and starting world bosses
        send_broadcast_time("6 minutes")
        await asyncio.sleep(60)

        # Set all shards to restart the next time they are empty (many will restart immediately) at 5 minutes
        print("Broadcasting restart-empty command to all shards...")
        socket.send_packet("*", "monumentanetworkrelay.command",
                           {"command": 'restart-empty', "server_type": 'minecraft'})

        send_broadcast_time("5 minutes")
        await asyncio.sleep(60)
        send_broadcast_time("4 minutes")
        await asyncio.sleep(60)
        send_broadcast_time("3 minutes")
        await asyncio.sleep(60)
        send_broadcast_time("2 minutes")
        await asyncio.sleep(60)
        send_broadcast_time("1 minute")
        await asyncio.sleep(30)
        send_broadcast_time("30 seconds")
        await asyncio.sleep(15)
        send_broadcast_time("15 seconds")
        await asyncio.sleep(5)
        send_broadcast_time("10 seconds")
        await asyncio.sleep(5)
        send_broadcast_time("5 seconds")
        await asyncio.sleep(5)
    except Exception:
        print("Failed to notify players about pending restart: {}".format(traceback.format_exc()))

    try:
        # Turn on Maintenance
        socket.send_packet("*", "monumentanetworkrelay.command",
                           {"command": 'maintenance on', "server_type": 'proxy'})
        # Wait for proxies to process command
        await asyncio.sleep(5)

        # Kick anyone with ops who bypassed maintenance
        #### TODO: Disabled for now, just stopping bungee directly. Eventually we may want this back so bungee stays up to tell people why it is down.
        # print("Broadcasting kick @a[all_worlds=true] command to all shards...")
        # socket.send_packet("*", "monumentanetworkrelay.command",
        #         {"command": 'kick @a[all_worlds=true]'}
        # )

        # At this point shards that didn't already restart will do so

        # Restart proxies
        # TODO: don't hardcode velocity instances here
        shards = await k8s.list()
        velocityShards = list(filter(lambda x: (x.startswith("velocity")), shards))
        await k8s.restart(velocityShards)

        # Some time for everything to stabilize
        await asyncio.sleep(120)

        # Turn maintenance mode back off
        socket.send_packet("*", "monumentanetworkrelay.command",
                           {"command": 'maintenance off', "server_type": 'proxy'})
    except Exception:
        print("Failed to restart the server: {}".format(traceback.format_exc()))
        send_broadcast_message([
            "",
            {"text": "[Alert] ", "color": "red"},
            {"text": "Monumenta has failed to perform its daily restart"}
        ])

if __name__ == '__main__':
    ################################################################################
    # Config / Environment

    config = {}

    if "BOT_CONFIG" in os.environ and os.path.isfile(os.environ["BOT_CONFIG"]):
        config_path = os.environ["BOT_CONFIG"]
    else:
        config_dir = os.path.expanduser("~/.monumenta_bot/")
        config_path = os.path.join(config_dir, "automated-restart.yml")

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

            socket = SocketManager(conf["host"], "daily_restart", durable=False, callback=None, log_level=log_level, server_type="daily-restart")

        k8s = KubernetesManager(config["k8s_namespace"])
    except KeyError as e:
        sys.exit('Config missing key: {}'.format(e))

    os.umask(0o022)

    # Config / Environment
    ################################################################################

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
