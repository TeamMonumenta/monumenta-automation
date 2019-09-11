#!/usr/bin/env python3

import sys
import os
import yaml
import asyncio
from pprint import pprint

from lib_py3.lib_rcon import rcon_command
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
    config = yaml.load(ymlfile)

pprint("Config: \n{}".format(config))

if "rcon_port" not in config:
    sys.exit("'rcon_port' missing from config!")
elif "rcon_pass" not in config:
    sys.exit("'rcon_pass' missing from config!")

os.umask(0o027)

# Config / Environment
################################################################################

async def main():
    k8s = KubernetesManager(config["k8s_namespace"])

    # Start with all the things in this namespace
    k8s_shards_list = await k8s.list()

    # Restrict this down to just the shards the bot is managing
    shards = [shard.replace('_', '') for shard in config["shards"].keys() if shard.replace('_', '') in k8s_shards_list]

    pprint("Will process these shards for potential restart: [{}]".format(" ".join(shards)))

    try:
        rcon_command("region1", config["rcon_port"], config["rcon_pass"],
                     '''broadcastcommand tellraw @a ["",{"text":"[Alert] ","color":"red"},{"text":"Monumenta will perform its daily restart in","color":"white"},{"text":" 5 minutes","color":"red"},{"text":". This helps reduce lag! The server will be down for ~5 minutes."}]''')
        await asyncio.sleep(60)
        rcon_command("region1", config["rcon_port"], config["rcon_pass"],
                     '''broadcastcommand tellraw @a ["",{"text":"[Alert] ","color":"red"},{"text":"Monumenta will perform its daily restart in","color":"white"},{"text":" 3 minutes","color":"red"},{"text":". This helps reduce lag! The server will be down for ~5 minutes."}]''')
        await asyncio.sleep(60)
        rcon_command("region1", config["rcon_port"], config["rcon_pass"],
                     '''broadcastcommand tellraw @a ["",{"text":"[Alert] ","color":"red"},{"text":"Monumenta will perform its daily restart in","color":"white"},{"text":" 2 minutes","color":"red"},{"text":". This helps reduce lag! The server will be down for ~5 minutes."}]''')
        await asyncio.sleep(60)
        rcon_command("region1", config["rcon_port"], config["rcon_pass"],
                     '''broadcastcommand tellraw @a ["",{"text":"[Alert] ","color":"red"},{"text":"Monumenta will perform its daily restart in","color":"white"},{"text":" 1 minute","color":"red"},{"text":". This helps reduce lag! The server will be down for ~5 minutes."}]''')
        await asyncio.sleep(30)
        rcon_command("region1", config["rcon_port"], config["rcon_pass"],
                     '''broadcastcommand tellraw @a ["",{"text":"[Alert] ","color":"red"},{"text":"Monumenta will perform its daily restart in","color":"white"},{"text":" 30 seconds","color":"red"},{"text":". This helps reduce lag! The server will be down for ~5 minutes."}]''')
        await asyncio.sleep(15)
        rcon_command("region1", config["rcon_port"], config["rcon_pass"],
                     '''broadcastcommand tellraw @a ["",{"text":"[Alert] ","color":"red"},{"text":"Monumenta will perform its daily restart in","color":"white"},{"text":" 15 seconds","color":"red"},{"text":". This helps reduce lag! The server will be down for ~5 minutes."}]''')
        await asyncio.sleep(10)
        rcon_command("region1", config["rcon_port"], config["rcon_pass"],
                     '''broadcastcommand tellraw @a ["",{"text":"[Alert] ","color":"red"},{"text":"Monumenta will perform its daily restart in","color":"white"},{"text":" 5 seconds","color":"red"},{"text":". This helps reduce lag! The server will be down for ~5 minutes."}]''')
        await asyncio.sleep(5)
    except:
        print("Failed to notify players about pending restart")

    print("Stopping bungee...")
    await k8s.stop("bungee")

    for shard in shards:
        if k8s_shards_list[shard]['replicas'] == 0:
            print("Skipping {} because it is already down".format(shard))
        else:
            # Only restart shards that are currently up!
            try:
                if "bungee" not in shard:
                    print("Stopping {}...".format(shard))
                    rcon_command(shard, config["rcon_port"], config["rcon_pass"], "stop")
            except:
                print("Failed to restart shard {}".format(shard))

    print("Sleeping for 120s...")
    await asyncio.sleep(120)
    print("Starting bungee...")
    await k8s.start("bungee")


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
