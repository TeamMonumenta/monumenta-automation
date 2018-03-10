#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

logging.basicConfig(level=logging.INFO)

import discord
import asyncio
import sys

client = discord.Client()
channel = ""

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
        await client.send_message(message.channel, 'Got test')
        await resetfunc()
        sys.stdout.flush()

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

async def sleep(seconds):
    await client.send_message(channel, "Sleeping for " + str(seconds) + " seconds")

async def cd(path):
    await client.send_message(channel, "Changing path to " + path)

async def run(cmd, debuginfo=None, ret=0):
    if debuginfo is not None:
        await client.send_message(channel, debuginfo)
    if cmd is not None:
        await client.send_message(channel, "Executing: `" + cmd + "`")

async def display(debuginfo):
    run(None, debuginfo)

terrain_reset = [
    run("mark2 send -n dungeon '~stop'", "Stopping the dungeon shard...", None),
    sleep(10),
    run("mark2 list | grep dungeon", "Checking that the dungeon shard is down...", 1),
    run("cp -a ~/project_epic/dungeon/Project_Epic-dungeon ~/tmp/Project_Epic-dungeon", "Copying the dungeon data..."),
    cd("~/project_epic/dungeon"),
    run("mark2 start", "Restarting the dungeon shard..."),

    cd("~/tmp"),
    run("tar xzf ~/dungeon_template-keep-this-12-29-2017.tgz", "Unpacking the dungeon template..."),
    run("~/MCEdit-And-Automation/utility_code/dungeon_instance_gen.py", "Running the dungeon instance generator..."),
    run("mv ~/tmp/dungeons-out ~/tmp/POST_RESET"),
    run("rm -rf ~/tmp/Project_Epic-dungeon ~/tmp/Project_Epic-template", "Cleaning up instance generation temp files..."),
    display("Dungeon instance generation complete!"),
]




async def resetfunc():
    for item in terrain_reset:
        status = await item


client.run('NDIwMDQ0ODMxMjg1NDQ0NjI5.DX49qQ.eIkPQMOllPAGKaaN8VInr6RKqHI')

