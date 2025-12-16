#!/usr/bin/env pypy3

import asyncio
import json
import os
import sys
import traceback
from pprint import pprint
import yaml

from lib_py3.lib_sockets import SocketManager
from lib_py3.lib_k8s import KubernetesManager

def send_broadcast_time(socket, time_left):
    """Broadcasts a restart warning with how much time is remaining to all players"""
    raw_json_text = [
        "",
        {"text": "[Alert] ", "color": "red"},
        {"text": "Monumenta will perform its daily restart in ", "color": "white"},
        {"text": time_left, "color": "red"},
        {"text": ". This helps reduce lag! The server will be down for ~180 seconds."}
    ]
    send_broadcast_message(socket, raw_json_text)


def send_broadcast_message(socket, raw_json_text):
    """Broadcasts an arbitrary raw json text message to all players"""
    command = '''tellraw @a[all_worlds=true] ''' + json.dumps(raw_json_text, ensure_ascii=False, separators=(',', ':'))
    socket.send_packet("*", "monumentanetworkrelay.command",
                       {"command": command})


def get_shards_by_type(socket, shard_type):
    """Gets a set of currently running shard names"""
    minecraft_shards = set()
    for shard in socket.remote_heartbeats():
        if socket.shard_type(shard) == "minecraft":
            minecraft_shards.add(shard)
    return minecraft_shards


async def await_stopped_inner(socket, pending_stop):
    """Waits for all shards in pending_stop to stop or time out"""
    # While there are entries in the pending_stop set...
    while pending_stop:
        running_shards = get_shards_by_type(socket, "minecraft")
        # ...remove entries that aren't in both running and pending_stop sets... (some might be back up before done)
        pending_stop.intersection_update(running_shards)
        # ...and wait.
        await asyncio.sleep(1)


async def await_stopped(socket, k8s, pending_stop):
    """Waits for all shards in pending_stop to stop or time out

    This force-restarts shards after 1 minute, then resumes waiting
    """

    try:
        async with asyncio.timeout(60):
            await await_stopped_inner(socket, pending_stop)
    except TimeoutError:
        await k8s.restart(list(pending_stop), wait=False)

    await await_stopped_inner(socket, pending_stop)


async def main(socket, k8s):
    """Perform a scheduled restart with warnings"""
    # Short wait to make sure socket connects correctly
    await asyncio.sleep(3)

    previous_shards = get_shards_by_type(socket, "minecraft")
    pending_stop = set(previous_shards)
    stop_task = None

    try:
        send_broadcast_time(socket, "15 minutes")
        await asyncio.sleep(60)
        send_broadcast_time(socket, "14 minutes")
        await asyncio.sleep(60)
        send_broadcast_time(socket, "13 minutes")
        await asyncio.sleep(60)
        send_broadcast_time(socket, "12 minutes")
        await asyncio.sleep(60)
        send_broadcast_time(socket, "11 minutes")
        await asyncio.sleep(60)
        send_broadcast_time(socket, "10 minutes")
        await asyncio.sleep(60)
        send_broadcast_time(socket, "9 minutes")
        await asyncio.sleep(60)
        send_broadcast_time(socket, "8 minutes" )
        await asyncio.sleep(60)
        send_broadcast_time(socket, "7 minutes")
        await asyncio.sleep(60)

        # TODO: add shutoff to creating dungeon instances and starting world bosses
        send_broadcast_time(socket, "6 minutes")
        await asyncio.sleep(60)

        # Set all shards to restart the next time they are empty (many will restart immediately) at 5 minutes
        print("Broadcasting restart-empty command to all shards...")
        stop_task = asyncio.create_task(await_stopped(socket, k8s, pending_stop))
        socket.send_packet("*", "monumentanetworkrelay.command",
                           {"command": 'restart-empty', "server_type": 'minecraft'})

        send_broadcast_time(socket, "5 minutes")
        await asyncio.sleep(60)
        send_broadcast_time(socket, "4 minutes")
        await asyncio.sleep(60)
        send_broadcast_time(socket, "3 minutes")
        await asyncio.sleep(60)
        send_broadcast_time(socket, "2 minutes")
        await asyncio.sleep(60)
        send_broadcast_time(socket, "1 minute")
        await asyncio.sleep(30)
        send_broadcast_time(socket, "30 seconds")
        await asyncio.sleep(15)
        send_broadcast_time(socket, "15 seconds")
        await asyncio.sleep(5)
        send_broadcast_time(socket, "10 seconds")
        await asyncio.sleep(5)
        send_broadcast_time(socket, "5 seconds")
        await asyncio.sleep(5)
    except Exception:
        print(f"Failed to notify players about pending restart: {traceback.format_exc()}")

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
        await k8s.restart(list(get_shards_by_type(socket, "proxy")))

        # Wait for shards to fully stop
        if stop_task is None:
            print("stop_task is None for some reason; waiting 2 minutes")
            await asyncio.sleep(120)
        else:
            stop_coroutine = stop_task.get_coro()
            if stop_coroutine:
                print("stop_task coroutine is None; all shards were likely already stopped? Possible bug otherwise?")
            else:
                print("Awaiting stop_task coroutine")
                await stop_coroutine
                print(f"Done waiting on stop_task; {len(pending_stop)} shards are still in pending_stop (should be 0 unless this is cloned by coroutines)")

            print("Waiting for shards to start back up with a timeout of 3 minutes")
            try:
                async with asyncio.timeout(180):
                    while previous_shards != get_shards_by_type(socket, "minecraft"):
                        await asyncio.sleep(1)
            except TimeoutError:
                print("Timed out waiting for shards to start back up; continuing anyway")

        # Turn maintenance mode back off
        socket.send_packet("*", "monumentanetworkrelay.command",
                           {"command": 'maintenance off', "server_type": 'proxy'})
    except Exception:
        print(f"Failed to restart the server: {traceback.format_exc()}")
        send_broadcast_message(socket, [
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
    with open(config_path, 'r', encoding='utf-8') as ymlfile:
        config = yaml.load(ymlfile, Loader=yaml.FullLoader)

    pprint(f"Config: \n{config}")

    socket = None
    k8s = None
    try:

        if "rabbitmq" in config:
            conf = config["rabbitmq"]
            log_level = conf.get("log_level", 20)

            socket = SocketManager(conf["host"], "daily_restart", durable=False, callback=None, log_level=log_level, server_type="daily-restart", track_heartbeats=True)

        k8s = KubernetesManager(config["k8s_namespace"])
    except KeyError as e:
        sys.exit(f'Config missing key: {e}')

    os.umask(0o022)

    # Config / Environment
    ################################################################################

    asyncio.run(main(socket, k8s))
