#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

logging.basicConfig(level=logging.INFO)

import discord
import asyncio
import sys
import os
import subprocess
import traceback
import datetime

################################################################################
# Config / Environment

client = discord.Client()
channel = ""
extraDebug = False
lock = False

################################################################################
# Utility Functions

def datestr():
    return datetime.datetime.now().strftime("%Y_%m_%d")

def split_string(text):
    # Maximum number of characters in a single line
    n = 1950

    splits = text.splitlines()
    result = []
    cur = None
    for i in splits:
        while True:
            if cur is None and len(i) <= n:
                cur = i;
                break # Done with i
            elif cur is None and len(i) > n:
                # Annoying case - one uber long line. Have to split into chunks
                result = result + [i[:n]]
                i = i[n:]
                pass # Repeat this iteration
            elif len(cur) + len(i) < n:
                cur = cur + "\n" + i
                break # Done with i
            else:
                result = result + [cur]
                cur = None
                pass # Repeat this iteration

    if cur is not None:
        result = result + [cur]
        cur = None

    return result


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
            await do_actions(terrain_reset)

    if message.content.startswith('!aoeu'):
        counter = 0
        tmp = await client.send_message(message.channel, 'Calculating messages...')
        async for log in client.logs_from(message.channel, limit=100):

            if log.author == message.author:
                counter += 1
                await client.edit_message(tmp, 'You have {} messages.'.format(counter))
            elif message.content.startswith('!sleep'):
                await asyncio.sleep(5)
                await client.send_message(message.channel, 'Done sleeping')

################################################################################
# Scriptable Routines

async def sleep(seconds):
    await display("Sleeping for " + str(seconds) + " seconds")
    await asyncio.sleep(seconds)

async def cd(path):
    if extraDebug:
        await display("Changing path to `" + path + "`")
    os.chdir(path)

async def run(cmd, ret=0):
    splitCmd = cmd.split(' ')
    if extraDebug:
        await display("Executing: ```" + str(splitCmd) + "```")
    process = await asyncio.create_subprocess_exec(*splitCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = await process.communicate()
    rc = process.returncode

    if extraDebug:
        stdout = stdout.decode('utf-8')
        await display("Result: {}".format(rc))
        if stdout:
            await display("stdout from command '{}':".format(cmd))
            await display_verbatim(stdout)

    stderr = stderr.decode('utf-8')
    if stderr:
        await display("stderr from command '{}':".format(cmd))
        await display_verbatim(stderr)
        # TODO: Remove likely
        #if ret != None and ret == 0:
            #raise ValueError("Got unexpected stderr while processing '{}'".format(cmd))

    if ret != None and rc != ret:
        raise ValueError("Expected result {}, got result {} while processing '{}'".format(ret, rc, cmd))

async def assert_exists():
    pass

async def assert_equals():
    pass

async def display_verbatim(text):
    for chunk in split_string(text):
        await display("```" + chunk + "```")

async def display(debuginfo):
    await client.send_message(channel, debuginfo)

async def do_actions(actions):
    try:
        for item in actions:
            await item
    except Exception as e:
        #TODO: Delete this line
        #await client.send_message(channel, "**ERROR**: ```" + str(e) + "``` ```" + traceback.format_exc() + "```")
        await client.send_message(channel, "**ERROR**: ```" + str(e) + "```")

################################################################################
# Terrain reset logic

generate_instances = [
    display("Cleaning up old terrain reset data..."),
    run("rm -rf /home/rock/tmpreset", None),
    run("mkdir -p /home/rock/tmpreset"),

    display("Stopping the dungeon shard..."),
    run("mark2 send -n dungeon ~stop", None),
    sleep(5),
    run("mark2 send -n dungeon test", 1),

    display("Copying the dungeon master copies..."),
    run("cp -a /home/rock/project_epic/dungeon/Project_Epic-dungeon /home/rock/tmpreset/Project_Epic-dungeon"),

    display("Restarting the dungeon shard..."),
    cd("/home/rock/project_epic/dungeon"),
    run("mark2 start"),

    display("Unpacking the dungeon template..."),
    cd("/home/rock/tmpreset"),
    run("tar xzf /home/rock/dungeon_template-keep-this-12-29-2017.tgz"),

    display("Generating dungeon instances (this may take a while)..."),
    run("python2 /home/rock/MCEdit-And-Automation/utility_code/dungeon_instance_gen.py"),
    run("mv /home/rock/tmpreset/dungeons-out /home/rock/tmpreset/POST_RESET"),

    display("Cleaning up instance generation temp files..."),
    run("rm -rf /home/rock/tmpreset/Project_Epic-dungeon /home/rock/tmpreset/Project_Epic-template"),
    display("Dungeon instance generation complete!"),
]

prep_reset_bundle = [
    display("Stopping the region_1 shard..."),
    run("mark2 send -n region_1 ~stop", None),
    sleep(5),
    run("mark2 send -n region_1 test", 1),

    display("Copying region_1..."),
    run("mkdir -p /home/rock/tmpreset/TEMPLATE/region_1"),
    run("cp -a /home/rock/project_epic/region_1/Project_Epic-region_1 /home/rock/tmpreset/TEMPLATE/region_1/"),

    display("Restarting the region_1 shard..."),
    cd("/home/rock/project_epic/region_1"),
    run("mark2 start"),

    display("Copying bungee..."),
    run("cp -a /home/rock/project_epic/bungee /home/rock/tmpreset/TEMPLATE/"),

    display("Copying purgatory..."),
    run("cp -a /home/rock/project_epic/purgatory /home/rock/tmpreset/POST_RESET/"),

    display("Copying tutorial..."),
    run("mkdir -p /home/rock/tmpreset/POST_RESET/tutorial"),
    cd("/home/rock/tmpreset/POST_RESET/tutorial"),
    run("tar xzf /home/rock/Project_Epic-tutorial.good.jan-12-2018.tgz"),

    display("Copying server_config..."),
    run("cp -a /home/rock/project_epic/server_config /home/rock/tmpreset/POST_RESET/"),

    display("Packaging up reset bundle..."),
    cd("/home/rock/tmpreset"),
    run("tar czf /home/rock/tmpreset/project_epic_build_template_pre_reset_" + datestr() + ".tgz POST_RESET TEMPLATE"),

    display("Reset bundle ready!"),
]

terrain_reset = generate_instances + prep_reset_bundle

################################################################################
# Entry point
client.run('NDIwMDQ0ODMxMjg1NDQ0NjI5.DX49qQ.eIkPQMOllPAGKaaN8VInr6RKqHI')

