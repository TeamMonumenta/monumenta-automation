# Monumenta-Automation

This is a collection of Monumenta's server operations tools, including weekly update, the discord bots, and various tools to investigate and update the world.

# License & Usage

The code in this repository is our own original work, developed for the
Monumenta minecraft server project.

You are free to adapt code here for your own purposes under the terms of the
GNU Affero Public License - which among other things means that you are free to
create derivative works based on things in this repository for any purpose, but
if you do you must also release that derived work under an AGPL compatible
license and make its source code available (preferably via GitHub fork).

Note that many of the things here build on various external APIs including
Quarry, Kubernetes, Docker, Discord, etc. These dependencies have their own
licenses.

# Overview of this repository

## discord_bots

Here you can find the automation bot and the task bot.

The automation bot allows moderators and developers to start and stop shards, run weekly updates, moderate player scores, copy the play server to the stage server for testing, etc.

The task bot manages the bug reports and suggestions channels, and is backed by a Kanboard server behind the scenes.

## docker

All of our shards and related services are in Docker/Kubernetes deployments. This folder has their configurations, allowing us to change their memory allocation, network settings, and prefered host server.

## quarry

This is an open source library that we use to modify most Minecraft files, using the Named Binary Tags (NBT) or Region file formats. We have modified it to support Mojangson, also known as SNBT, which is the format used by in-game commands to represent NBT data.

## reports

While not checked in, this folder contains data exported by the vanilla Minecraft servers. This includes the command tree and the internal IDs of every block and item. It can be generated with the command:
```
java -cp minecraft_server.jar net.minecraft.data.Main --reports
```

## rust

While most of our automation code is written in Python for its ease of use, we have found Rust to be much faster to run. Most of our player-focused code is either handled here, or exported to where Python code can further modify it.

## tests

When making changes to weekly update, it is important to test those changes before they are used for real to avoid down time. These tests run on specific cases, such as troublesome items, or operations that have broken before, and tests them without running on all of our player data at once. This reduces testing time from about an hour to about a minute.

## utility_code

This folder contains the bulk of our Python scripts - dungeon instance gen, gen server config, weekly update, and various smaller utilities.

### lib_py3

This is our second generation of automation libraries. This was written in a bit of a rush in preperation for the 1.13 update due to significant file format changes, which is the reason we use Quarry. It is still used in all of our scripts, but large parts of it have been phased out and removed in favor of...

### minecraft

This is our third generation of automation libraries. Here we've moved to an object-oriented approach to read and modify every item, entity, and block entity in any file except for commands and raw json text. It also features awareness of where each object comes from, and built-in debug methods.
