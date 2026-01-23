#!/usr/bin/env pypy3

import asyncio
from datetime import datetime, timedelta, timezone
import json
import os
import sys
import traceback
from pprint import pprint
import yaml

from lib_py3.lib_sockets import SocketManager
from lib_py3.lib_k8s import KubernetesManager


ONE_SECOND = timedelta(seconds=1)


def send_broadcast_time(socket, seconds_left):
    """Broadcasts a restart warning with how much time is remaining to all players"""
    minutes_left, seconds_in_minute = divmod(seconds_left, 60)
    time_left = []

    if minutes_left > 1:
        time_left += [str(minutes_left), "minutes"]
    elif minutes_left == 1:
        time_left += ["1", "minute"]

    if seconds_in_minute > 1:
        time_left += [str(seconds_in_minute), "seconds"]
    elif seconds_in_minute == 1:
        time_left += ["1", "second"]
    elif minutes_left == 0:
        time_left = ["now"]

    time_left = " ".join(time_left)

    raw_json_text = [
        "",
        {"text": "[Alert] ", "color": "red"},
        {"text": "Monumenta will perform its daily restart " + ("in " if time_left else ""), "color": "white"},
        {"text": time_left if time_left else "now", "color": "red"},
        {"text": ". This helps reduce lag! The server will be down for ~180 seconds."}
    ]
    send_tablist_event(socket, seconds_left)
    send_broadcast_message(socket, raw_json_text)


def send_broadcast_message(socket, raw_json_text):
    """Broadcasts an arbitrary raw json text message to all players"""
    command = '''tellraw @a[all_worlds=true] ''' + json.dumps(raw_json_text, ensure_ascii=False, separators=(',', ':'))
    socket.send_packet("*", "monumentanetworkrelay.command",
                       {"command": command})


def send_tablist_event(socket, time):
    """Sends a daily restart event to display in the tab list"""
    event_data = {
        "shard": "daily_restart",
        "eventName": "DAILY_RESTART",
        "timeLeft": time,
        "status": "STARTING" if time > 0 else "IN_PROGRESS",
    }
    socket.send_packet("*", "monumenta.eventbroadcast.update", event_data)


def send_admin_alert(socket, message):
    """Sends an admin alert seeking help"""
    print(message, flush=True)
    event_data = {
        "message": message,
    }
    socket.send_packet("*", "Monumenta.Automation.AdminNotification", event_data)


def get_shards_by_type(socket, shard_type="minecraft"):
    """Gets a set of currently running shard names"""
    minecraft_shards = set()
    for shard in socket.remote_heartbeats():
        if socket.shard_type(shard) == shard_type:
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

    This force-restarts shards after timeout, then resumes waiting
    """

    try:
        async with asyncio.timeout(7 * 60):
            await await_stopped_inner(socket, pending_stop)
    except TimeoutError:
        await k8s.restart(list(pending_stop), wait=False)

    await await_stopped_inner(socket, pending_stop)


async def main(socket, k8s):
    """Perform a scheduled restart with warnings"""
    # Short wait to make sure socket connects correctly
    await asyncio.sleep(3)

    tz = timezone.utc
    stop_time = datetime.now(tz) + timedelta(minutes=15, seconds=5)

    previous_shards = get_shards_by_type(socket, "minecraft")
    print(f'Preparing to restart: {previous_shards}', flush=True)
    pending_stop = set(previous_shards)
    stop_task = None

    try:
        countdown_targets = sorted([60 * i for i in range(1, 15+1)] + [30, 15, 10, 5, 0], reverse=True)

        while countdown_targets:
            next_target = countdown_targets.pop(0)
            remaining_seconds = (stop_time - datetime.now(tz)) / ONE_SECOND
            if remaining_seconds < next_target:
                continue

            try:
                async with asyncio.timeout(remaining_seconds - next_target):
                    while True:
                        await asyncio.sleep(3)
                        remaining_seconds = (stop_time - datetime.now(tz)) / ONE_SECOND
                        send_tablist_event(socket, remaining_seconds)
            except TimeoutError:
                pass

            if next_target == 60 * 6:
                previous_shards |= get_shards_by_type(socket, "minecraft")
                pending_stop |= previous_shards

            if next_target == 60 * 5:
                # Set all shards to restart the next time they are empty (many will restart immediately) at 5 minutes
                print("Broadcasting restart-empty command to all shards...", flush=True)
                stop_task = asyncio.create_task(await_stopped(socket, k8s, pending_stop))
                socket.send_packet("*", "monumentanetworkrelay.command",
                                   {"command": 'restart-empty', "server_type": 'minecraft'})

            send_broadcast_time(socket, next_target)

    except Exception:
        send_admin_alert(socket, f"Failed to notify players about pending restart: {traceback.format_exc()}")

    try:
        # Turn on Maintenance
        socket.send_packet("*", "monumentanetworkrelay.command",
                           {"command": 'maintenance on', "server_type": 'proxy'})
        # Wait for proxies to process command
        await asyncio.sleep(5)

        # Kick anyone with ops who bypassed maintenance
        #### TODO: Disabled for now, just stopping bungee directly. Eventually we may want this back so bungee stays up to tell people why it is down.
        # print("Broadcasting kick @a[all_worlds=true] command to all shards...", flush=True)
        # socket.send_packet("*", "monumentanetworkrelay.command",
        #         {"command": 'kick @a[all_worlds=true]'}
        # )

        # At this point shards that didn't already restart will do so

        # Restart proxies
        await k8s.restart(list(get_shards_by_type(socket, "proxy")))

        # Wait for shards to fully stop
        if stop_task is None:
            send_admin_alert(socket, "stop_task is None for some reason; waiting 2 minutes")
            await asyncio.sleep(120)
        else:
            print("Awaiting stop_task", flush=True)
            await stop_task
            if pending_stop:
                send_admin_alert(socket, f"stop_task did not stop everything: {pending_stop}")
            else:
                print("Done waiting on stop_task", flush=True)

            print("Waiting for shards to start back up with a timeout", flush=True)
            try:
                async with asyncio.timeout(600):
                    while previous_shards != get_shards_by_type(socket, "minecraft"):
                        await asyncio.sleep(1)
                        send_tablist_event(socket, 0)
            except TimeoutError:
                print("Timed out waiting for shards to start back up; continuing anyway", flush=True)

        # Turn maintenance mode back off
        send_tablist_event(socket, -1)
        socket.send_packet("*", "monumentanetworkrelay.command",
                           {"command": 'maintenance off', "server_type": 'proxy'})
    except Exception:
        send_admin_alert(socket, f"Failed to restart the server: {traceback.format_exc()}")
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
    sys.stdout.flush()

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
