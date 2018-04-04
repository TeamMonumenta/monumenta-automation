#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

logging.basicConfig(level=logging.INFO)

import discord
import shell_common

################################################################################
# Config / Environment

client = discord.Client()
sh = shell_common.Shell(client, debug=True)

channel = ""
lock = False

################################################################################
# Discord event handlers

@client.event
async def on_ready():
    global channel

    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    channel = client.get_channel('420045459177078795')

@client.event
async def on_message(message):
    if message.content.startswith('!test'):
        if lock:
            await client.send_message(message.channel, 'Test already running, please wait')
        else:
            await client.send_message(message.channel, 'Running terrain reset')
            await sh.do_actions(channel, terrain_reset)


################################################################################
# Terrain reset logic

generate_instances = [
    sh.display("Cleaning up old terrain reset data..."),
    sh.run("rm -rf /home/rock/tmpreset", None),
    sh.run("mkdir -p /home/rock/tmpreset"),

    sh.display("Stopping the dungeon shard..."),
    sh.run("mark2 send -n dungeon ~stop", None),
    sh.sleep(5),
    sh.run("mark2 send -n dungeon test", 1),

    sh.display("Copying the dungeon master copies..."),
    sh.run("cp -a /home/rock/project_epic/dungeon/Project_Epic-dungeon /home/rock/tmpreset/Project_Epic-dungeon"),

    sh.display("Restarting the dungeon shard..."),
    sh.cd("/home/rock/project_epic/dungeon"),
    sh.run("mark2 start"),

    sh.display("Unpacking the dungeon template..."),
    sh.cd("/home/rock/tmpreset"),
    sh.run("tar xzf /home/rock/dungeon_template-keep-this-12-29-2017.tgz"),

    sh.display("Generating dungeon instances (this may take a while)..."),
    sh.run("python2 /home/rock/MCEdit-And-Automation/utility_code/dungeon_instance_gen.py"),
    sh.run("mv /home/rock/tmpreset/dungeons-out /home/rock/tmpreset/POST_RESET"),

    sh.display("Cleaning up instance generation temp files..."),
    sh.run("rm -rf /home/rock/tmpreset/Project_Epic-dungeon /home/rock/tmpreset/Project_Epic-template"),
    sh.display("Dungeon instance generation complete!"),
]

prep_reset_bundle = [
    sh.display("Stopping the region_1 shard..."),
    sh.run("mark2 send -n region_1 ~stop", None),
    sh.sleep(5),
    sh.run("mark2 send -n region_1 test", 1),

    sh.display("Copying region_1..."),
    sh.run("mkdir -p /home/rock/tmpreset/TEMPLATE/region_1"),
    sh.run("cp -a /home/rock/project_epic/region_1/Project_Epic-region_1 /home/rock/tmpreset/TEMPLATE/region_1/"),

    sh.display("Restarting the region_1 shard..."),
    sh.cd("/home/rock/project_epic/region_1"),
    sh.run("mark2 start"),

    sh.display("Copying bungee..."),
    sh.run("cp -a /home/rock/project_epic/bungee /home/rock/tmpreset/TEMPLATE/"),

    sh.display("Copying purgatory..."),
    sh.run("cp -a /home/rock/project_epic/purgatory /home/rock/tmpreset/POST_RESET/"),

    sh.display("Copying tutorial..."),
    sh.run("mkdir -p /home/rock/tmpreset/POST_RESET/tutorial"),
    sh.cd("/home/rock/tmpreset/POST_RESET/tutorial"),
    sh.run("tar xzf /home/rock/Project_Epic-tutorial.good.jan-12-2018.tgz"),

    sh.display("Copying server_config..."),
    sh.run("cp -a /home/rock/project_epic/server_config /home/rock/tmpreset/POST_RESET/"),

    sh.display("Packaging up reset bundle..."),
    sh.cd("/home/rock/tmpreset"),
    sh.run("tar czf /home/rock/tmpreset/project_epic_build_template_pre_reset_" + shell_common.datestr() + ".tgz POST_RESET TEMPLATE"),

    sh.display("Reset bundle ready!"),
]

terrain_reset = generate_instances + prep_reset_bundle

################################################################################
# Entry point
client.run('NDIwMDQ0ODMxMjg1NDQ0NjI5.DX49qQ.eIkPQMOllPAGKaaN8VInr6RKqHI')

