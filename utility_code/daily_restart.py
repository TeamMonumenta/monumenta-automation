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
        {"text": ". This helps reduce lag! The server will be down for ~90 seconds."}
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
        # Set all shards to restart the next time they are empty (many will restart immediately)
        print("Broadcasting restart-empty command to all shards...")
        socket.send_packet("*", "monumentanetworkrelay.command",
                           {"command": 'restart-empty'})

        send_broadcast_time("5 minutes")
        await asyncio.sleep(120)
        send_broadcast_time("3 minutes")
        await asyncio.sleep(60)
        send_broadcast_time("2 minutes")
        await asyncio.sleep(60)
        send_broadcast_time("1 minute")
        await asyncio.sleep(30)
        send_broadcast_time("30 seconds")
        await asyncio.sleep(15)
        send_broadcast_time("15 seconds")
        await asyncio.sleep(10)
        send_broadcast_time("5 seconds")
        await asyncio.sleep(5)
    except Exception:
        print("Failed to notify players about pending restart: {}".format(traceback.format_exc()))

    try:
        # Read the BungeeDisplay config file
        primary_bungee_name = config["primary_bungee_name"]
        #bungee_instances = config["bungee_instances"]
        bungee_instances = {}
        for path in Path('/home/epic/play/').glob('*/*/plugins/BungeeDisplay/config.yml'):
            bungee_name = path.parents[2].name
            bungee_instances[bungee_name] = path

        primary_path = bungee_instances.get(primary_bungee_name, None)
        if primary_path is None:
            if len(bungee_instances) == 0:
                print("Could not find ANY bungee instances! Did our plugin code change?")
                send_broadcast_message([
                    "",
                    {"text": "[Alert] ", "color": "red"},
                    {"text": "Monumenta has failed to perform its daily restart"}
                ])
                return
            fallback_bungee_name, primary_path = list(bungee_instances.items())[0]
            print(f"Could not find primary bungee instance {primary_bungee_name}! Using {fallback_bungee_name} instead.")

        with open(bungee_instances[primary_bungee_name], 'r') as ymlfile:
            bungee_display_yml = yaml.load(ymlfile, Loader=yaml.FullLoader)

        # Modify the file to set maintenance mode - this kicks everyone
        bungee_display_yml["maintenance"]["enabled"] = True
        bungee_display_yml["maintenance"]["join"] = '&cMonumenta is currently down for daily restart - try again in a few minutes'
        bungee_display_yml["maintenance"]["kick_message"] = '&cMonumenta is going down for daily restart - join again in 5 minutes'
        bungee_display_yml["maintenance"]["information"] = '&6Please try again in a few minutes'
        bungee_display_yml["motd"]["maintenance"]["line2"] = '              &c&lDown for Daily Restart'

        # Write the updated config file to enable maintenance mode
        for path in bungee_instances.values():
            with open(path, 'w') as ymlfile:
                yaml.dump(bungee_display_yml, ymlfile, default_flow_style=False)

        # Just a bit of time to process config and kick players
        await asyncio.sleep(5)

        # Kick anyone with ops who bypassed maintenance
        #### TODO: Disabled for now, just stopping bungee directly. Eventually we may want this back so bungee stays up to tell people why it is down.
        # print("Broadcasting kick @a[all_worlds=true] command to all shards...")
        # socket.send_packet("*", "monumentanetworkrelay.command",
        #         {"command": 'kick @a[all_worlds=true]'}
        # )

        # At this point shards that didn't already restart will do so

        # Stop bungee
        print("Stopping bungee...")
        await k8s.stop(list(bungee_instances.keys()))

        # Some time for everything to stabilize
        await asyncio.sleep(55)

        # Turn maintenance mode back off
        bungee_display_yml["maintenance"]["enabled"] = False

        # Update maintenance state again
        for path in bungee_instances.values():
            with open(path, 'w') as ymlfile:
                yaml.dump(bungee_display_yml, ymlfile, default_flow_style=False)
                os.fsync(ymlfile)

        # Some more time for file to propagate and shards to stabilize
        await asyncio.sleep(30)

        # Start bungee
        print("Starting bungee...")
        await k8s.start(list(bungee_instances.keys()))
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
