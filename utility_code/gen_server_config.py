#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import shutil
import re

SERVER_TYPE='build'

# Main entry point
if (len(sys.argv) < 2):
    sys.exit("Usage: " + sys.argv[0] + " [--play] <minecraft_directory> <dir2> ...")

server_list = [];
for arg in sys.argv[1:]:
    if (arg == "--play"):
        SERVER_TYPE='play'
    else:
        server_list += [arg,]

if (len(server_list) < 1):
    print "ERROR: No folders specified"
    sys.exit("Usage: " + sys.argv[0] + " [--play] <minecraft_directory> <dir2> ...")

if SERVER_TYPE == 'build':
    print "Using build server settings!"
else:
    print "Using play server settings!"

server_config_to_copy = [
        ('eula.txt',),
        ('bukkit.yml',),
        ('commands.yml',),
        ('help.yml',),
        ('permissions.yml',),
        ('spigot.yml',),
        ('wepif.yml',),
        ('mark2-scripts.txt',),
        ('plugins/FastAsyncWorldEdit/config.yml',),
        ('plugins/NBTEditor/CustomItems/NBTEditor.yml',),
        ('plugins/CoreProtect/config.yml',),
        ('plugins/OpenInv/config.yml',),
        ('plugins/Monumenta-Plugins/config.yml',),
        ('plugins/Monumenta-Plugins/Properties.json',),
    ]

server_config_min = [
        ('spigot.jar', '../server_config/spigot.jar'),
    ]

server_config_min_plus_data = server_config_min + [
        ('Project_Epic-WORLDOOG/data/functions', '../../../server_config/data/functions'),
        ('Project_Epic-WORLDOOG/data/loot_tables', '../../../server_config/data/loot_tables'),
        ('Project_Epic-WORLDOOG_the_end/data/functions', '../../../server_config/data/functions'),
        ('Project_Epic-WORLDOOG_the_end/data/loot_tables', '../../../server_config/data/loot_tables'),
    ]

server_config = server_config_min_plus_data + [
        ('plugins/ScriptedQuests/npcs', '../../../server_config/data/scriptedquests/npcs'),
        ('plugins/ScriptedQuests/compass', '../../../server_config/data/scriptedquests/compass'),
        ('plugins/ScriptedQuests/death', '../../../server_config/data/scriptedquests/death'),
        ('plugins/EpicStructureManagement/structures', '../../../server_config/data/structures'),
    ]

advancements_disabled = [
        ('Project_Epic-WORLDOOG/data/advancements', '../../../server_config/data/advancements_disabled'),
    ]

advancements_r1 = [
        ('Project_Epic-WORLDOOG/data/advancements', '../../../server_config/data/advancements'),
    ]

structures = [
        ('Project_Epic-WORLDOOG/structures', '../../server_config/structures'),
    ]

coreprotect = [
        ('plugins/CoreProtect.jar', '../../server_config/plugins/CoreProtect.jar'),
    ]

easywarp = [
        ('plugins/EasyWarp.jar', '../../server_config/plugins/EasyWarp.jar'),
        ('plugins/EasyWarp/config.yml', '../../../server_config/plugins/EasyWarp/config.yml'),
    ]

worldedit = [
        ('plugins/FastAsyncWorldEdit.jar', '../../server_config/plugins/FastAsyncWorldEdit.jar'),
        ('plugins/WorldEdit.jar', '../../server_config/plugins/WorldEdit.jar'),
        ('plugins/WorldEdit/config.yml', '../../../server_config/plugins/WorldEdit/config.yml'),
        ('plugins/WorldEdit/schematics', '../../../server_config/plugins/WorldEdit/schematics'),

    # Build Commands (WorldEdit Craftscripts) - 1.8 installed currently
        ('plugins/js.jar', '../../server_config/plugins/js.jar'),
        ('plugins/WorldEdit/bo2s', '../../../server_config/plugins/WorldEdit/bo2s'),
        ('plugins/WorldEdit/craftscripts', '../../../server_config/plugins/WorldEdit/craftscripts'),
        ('plugins/WorldEdit/shapes', '../../../server_config/plugins/WorldEdit/shapes'),
    ]

luckperms_standalone = [
        ('plugins/LuckPerms.jar', '../../server_config/plugins/LuckPerms.jar'),
        ('plugins/LuckPerms/config.yml', '../../../server_config/plugins/LuckPerms/config.yml'),
    ]

luckperms = luckperms_standalone + [
        ('plugins/LuckPerms/yaml-storage/groups', '../../../../server_config/plugins/LuckPerms/yaml-storage/groups'),
        ('plugins/LuckPerms/yaml-storage/tracks', '../../../../server_config/plugins/LuckPerms/yaml-storage/tracks'),
        ('plugins/LuckPerms/yaml-storage/users', '../../../../server_config/plugins/LuckPerms/yaml-storage/users'),
    ]

monumenta = [
        ('plugins/Monumenta-Plugins.jar', '../../server_config/plugins/Monumenta-Plugins.jar'),
        ('plugins/ScriptedQuests.jar', '../../server_config/plugins/ScriptedQuests.jar'),
        ('plugins/EpicStructureManagement.jar', '../../server_config/plugins/EpicStructureManagement.jar'),
    ]

nbteditor = [
        ('plugins/nbteditor.jar', '../../server_config/plugins/nbteditor.jar'),
        ('plugins/NBTEditor/config.yml', '../../../server_config/plugins/NBTEditor/config.yml'),
    ]

openinv = [
        ('plugins/OpenInv.jar', '../../server_config/plugins/OpenInv.jar'),
    ]

socket4mc = [
        ('plugins/socket4mc.jar', '../../server_config/plugins/socket4mc.jar'),
    ]

speedchanger = [
        ('plugins/SpeedChanger.jar', '../../server_config/plugins/SpeedChanger.jar'),
    ]

voxelsniper = [
        ('plugins/FastAsyncVoxelSniper.jar', '../../server_config/plugins/FastAsyncVoxelSniper.jar'),
        ('plugins/VoxelSniper.jar', '../../server_config/plugins/VoxelSniper.jar'),
        ('plugins/VoxelSniper/config.yml', '../../../server_config/plugins/VoxelSniper/config.yml'),
    ]

# Index of nodes:
#   server_config
#   advancements_disabled
#   advancements_r1
#   structures

base_plugins = easywarp + luckperms + monumenta + openinv + socket4mc + worldedit
if (SERVER_TYPE == 'build'):
    build_plugins = speedchanger + nbteditor + voxelsniper
else:
    build_plugins = []

# String replacements:
# WORLDOOG - server name
#('server.properties', 'motd', 'motd=Monumenta\: WORLDOOG shard'),
#('plugins/Socket4MC/config.yml', 'name', 'name: "WORLDOOG"'),
#('mark2.properties', 'plugin.backup.path', 'plugin.backup.path=../backups/WORLDOOG/WORLDOOG_{timestamp}.tar.gz'),
#('server.properties', 'level-name', 'level-name=Project_Epic-WORLDOOG'),

template_dir = 'server_config/server_config_template'

config = {

    # Config: if three args, replace line in 1st arg file starting with 2nd arg with 3rd arg
    #         if two args, append line to file
    #         if one, just copy file unmodified

    # Change between play and beta:
    #   Memory allocation
    #   Hugepages in mark2.properties
    #   Difficulty
    #   Tab complete=9999 in spigot.yml

    'region_1':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=11'),
            ('spigot.yml', 'view-distance', '    view-distance: 11'),
            ('server.properties', 'server-port', 'server-port=25566'),
            ('plugins/Socket4MC/config.yml', 'host', 'host: "127.0.0.2"'),
            ('mark2-scripts.txt', '     0    3    *    *    *    /setblock -1449 1 -1440 redstone_block'),
            ('plugins/Monumenta-Plugins/Properties.json', '"dailyResetEnabled":', '"dailyResetEnabled": true,'),
            ('plugins/Monumenta-Plugins/Properties.json', '"plotSurvivalMinHeight":', '"plotSurvivalMinHeight": 95,'),
            ('plugins/Monumenta-Plugins/Properties.json', '"questCompassEnabled":', '"questCompassEnabled": true,'),
            ('plugins/Monumenta-Plugins/Properties.json', '"locationBounds":', '''"locationBounds": [
        {"name":"Arena", "type":"AdventureZone", "pos1":"-966 90 -124", "pos2":"-926 256 -84"},
        {"name":"Capital", "type":"Capital", "pos1":"-1130 0 -284", "pos2":"-498 256 344"},

        {"name":"Nyr", "type":"SafeZone", "pos1":"-181 0 -166", "pos2":"-79 256 14"},
        {"name":"Farr", "type":"SafeZone", "pos1":"538 0 100", "pos2":"658 256 229"},
        {"name":"Highwatch", "type":"SafeZone", "pos1":"1130 0 -156", "pos2":"1217 256 -76"},
        {"name":"Lowtide Chef Quest Basement", "type":"AdventureZone", "pos1":"729 56 452", "pos2":"752 43 487"},
        {"name":"Lowtide Main", "type":"SafeZone", "pos1":"675 0 421", "pos2":"767 255 558"},
        {"name":"Lowtide docks", "type":"SafeZone", "pos1":"664 0 474", "pos2":"675 255 483"},
        {"name":"Lowtide boat", "type":"SafeZone", "pos1":"650 0 483", "pos2":"675 255 558"},

        {"name":"White Wool Lobby", "type":"SafeZone", "pos1":"136 53 -186", "pos2":"176 83 -120"},
        {"name":"Orange Wool Lobby", "type":"SafeZone", "pos1":"27 64 164", "pos2":"67 94 229"},
        {"name":"Magenta Wool Lobby", "type":"SafeZone", "pos1":"453 12 5", "pos2":"493 42 70"},
        {"name":"Light Blue Wool Lobby", "type":"SafeZone", "pos1":"770 76 -366", "pos2":"810 106 -301"},
        {"name":"Yellow Wool Lobby", "type":"SafeZone", "pos1":"1141 39 3", "pos2":"1181 69 68"},
        {"name":"Bonus Lobby", "type":"SafeZone", "pos1":"295 10 -163", "pos2":"335 40 -98"},
        {"name":"Roguelike Lobby", "type":"SafeZone", "pos1":"766 7 156", "pos2":"814 45 235"},

        {"name":"Monument", "type":"SafeZone", "pos1":"1160 0 -320", "pos2":"1400 256 -115"},
        {"name":"Mystic Grotto", "type":"SafeZone", "pos1":"317 61 309", "pos2":"383 106 392"},
        {"name":"Brown Co 57 Floating Island", "type":"SafeZone", "pos1":"887 0 -927", "pos2":"978 255 -899"},
        {"name":"Roguelike Entrance Puzzle", "type":"SafeZone", "pos1":"825 0 173", "pos2":"889 97 217"},
        {"name":"Vanilla Pilot", "type":"SafeZone", "pos1":"410 156 157", "pos2":"429 190 176"},

        {"name":"Commands", "type":"RestrictedZone", "pos1":"-1584 0 -1632", "pos2":"-1329 255 -1377"},
        {"name":"Siege Of Highwatch", "type":"AdventureZone", "pos1":"1505 102 -178", "pos2":"1631 256 -16"},
        {"name":"Ctaz", "type":"AdventureZone", "pos1":"227 10 294", "pos2":"252 256 320"},
        {"name":"Hermy", "type":"AdventureZone", "pos1":"-331 86 334", "pos2":"-310 110 355"},
        {"name":"West Water Tower", "type":"AdventureZone", "pos1":"-1377 0 -173", "pos2":"-1336 255 -132"},

        {"name":"Fountain of Miracles Patreon Trader", "type":"AdventureZone", "pos1":"501 67 437", "pos2":"512 57 422"},
        {"name":"Cursed Forest Patreon Trader", "type":"AdventureZone", "pos1":"1163 100 87", "pos2":"1151 90 80"},
        {"name":"Nivalis Cave", "type":"AdventureZone", "pos1":"998 119 -320", "pos2":"1008 135 -295"},
        {"name":"Haunted House Quest", "type":"AdventureZone", "pos1":"1000 7 72", "pos2":"1042 38 108"},

        {"name":"post-monument Sage Draiikali", "type":"AdventureZone", "pos1":"1220 0 -126", "pos2":"1242 255 -103"},
        {"name":"Farr race", "type":"AdventureZone", "pos1":"1036 99 -119", "pos2":"1051 112 -105"}
    ],'''),
        ],
        'linked':server_config + advancements_r1 + base_plugins + coreprotect + build_plugins,
    },

    'region_2':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=8'),
            ('spigot.yml', 'view-distance', '    view-distance: 8'),
            ('server.properties', 'server-port', 'server-port=25568'),
            ('plugins/Socket4MC/config.yml', 'host', 'host: "127.0.0.3"'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=1536M'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=1536M'),
            ('plugins/Monumenta-Plugins/Properties.json', '"locationBounds":', '''"locationBounds": [
        {"name":"Commands", "type":"RestrictedZone", "pos1":"-1584 0 -1632", "pos2":"-1329 255 -1377"}
    ],'''),
        ],
        'linked':server_config + advancements_disabled + base_plugins + coreprotect + build_plugins,
    },

    'tutorial':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=9'),
            ('server.properties', 'white-list', 'white-list=false'),
            ('spigot.yml', 'view-distance', '    view-distance: 9'),
            ('server.properties', 'server-port', 'server-port=25567'),
            ('server.properties', 'spawn-animals', 'spawn-animals=false'),
            ('plugins/Socket4MC/config.yml', 'host', 'host: "127.0.0.7"'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=1G'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=1G'),
            ('plugins/Monumenta-Plugins/Properties.json', '"transferDataEnabled":', '"transferDataEnabled": false,'),
            ('plugins/Monumenta-Plugins/Properties.json', '"allowedTransferTargets":', '"allowedTransferTargets": [],'),
            ('plugins/Monumenta-Plugins/Properties.json', '"locationBounds":', '''"locationBounds": [
        {"name":"Commands", "type":"RestrictedZone", "pos1":"-1584 0 -1632", "pos2":"-1329 255 -1377"},
        {"name":"New Player Lobby", "type":"SafeZone", "pos1":"-1456 0 -1216", "pos2":"-1425 255 -1185"}
    ],'''),
        ],
        'linked':server_config + advancements_disabled + base_plugins + build_plugins,
    },

    'dungeon':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=12'),
            ('spigot.yml', 'view-distance', '    view-distance: 12'),
            ('server.properties', 'server-port', 'server-port=25572'),
            ('server.properties', 'spawn-animals', 'spawn-animals=false'),
            ('plugins/Socket4MC/config.yml', 'host', 'host: "127.0.0.6"'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=1536M'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=1536M'),
            ('plugins/Monumenta-Plugins/Properties.json', '"locationBounds":', '''"locationBounds": [
        {"name":"Commands", "type":"RestrictedZone", "pos1":"-1584 0 -1632", "pos2":"-1329 255 -1377"}
    ],'''),
        ],
        'linked':server_config + advancements_disabled + base_plugins + coreprotect + build_plugins,
    },

    'roguelike':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=16'),
            ('spigot.yml', 'view-distance', '    view-distance: 16'),
            ('server.properties', 'server-port', 'server-port=25569'),
            ('plugins/Socket4MC/config.yml', 'host', 'host: "127.0.0.4"'),
            ('plugins/Monumenta-Plugins/Properties.json', '"isSleepingEnabled":', '"isSleepingEnabled": false,'),
            ('plugins/Monumenta-Plugins/Properties.json', '"unbreakableBlocks":', '"unbreakableBlocks": ["OBSERVER", "WOOD_PLATE", "STONE_PLATE", "IRON_PLATE", "GOLD_PLATE"],'),
            ('plugins/Monumenta-Plugins/Properties.json', '"locationBounds":', '''"locationBounds": [
        {"name":"Commands", "type":"RestrictedZone", "pos1":"-1584 0 -1632", "pos2":"-1329 255 -1377"},
        {"name":"Lobby and reward room", "type":"SafeZone", "pos1":"-9999999 60 -9999999", "pos2":"9999999 255 9999999"}
    ],'''),
        ],
        'linked':server_config + advancements_disabled + base_plugins + coreprotect + build_plugins,
    },

    'test':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=8'),
            ('spigot.yml', 'view-distance', '    view-distance: 8'),
            ('server.properties', 'server-port', 'server-port=25571'),
            ('plugins/Socket4MC/config.yml', 'host', 'host: "127.0.0.5"'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=1G'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=1G'),
        ],
        'linked':server_config + advancements_r1 + base_plugins + build_plugins,
    },

    'build':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=8'),
            ('spigot.yml', 'view-distance', '    view-distance: 8'),
            ('server.properties', 'server-port', 'server-port=25599'),
            ('plugins/Socket4MC/config.yml', 'host', 'host: "127.0.0.29"'),
            ('spigot.yml', 'tab-complete', '  tab-complete: 0'),
            ('server.properties', 'difficulty', 'difficulty=0'),
            ('server.properties', 'gamemode', 'gamemode=1'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=1280M'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=1280M'),
            ('plugins/Monumenta-Plugins/Properties.json', '"transferDataEnabled":', '"transferDataEnabled": false,'),
            ('plugins/Monumenta-Plugins/Properties.json', '"broadcastCommandEnabled":', '"broadcastCommandEnabled": false,'),
            ('plugins/Monumenta-Plugins/Properties.json', '"allowedTransferTargets":', '"allowedTransferTargets": ["region_1"],'),
        ],
        'linked':server_config_min + advancements_disabled + luckperms_standalone + easywarp + monumenta + socket4mc + coreprotect + worldedit + speedchanger + nbteditor + voxelsniper,
    },

    'mobs':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=6'),
            ('spigot.yml', 'view-distance', '    view-distance: 6'),
            ('server.properties', 'server-port', 'server-port=25598'),
            ('plugins/Socket4MC/config.yml', 'host', 'host: "127.0.0.28"'),
            ('server.properties', 'difficulty', 'difficulty=2'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=512M'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=512M'),
            ('plugins/Monumenta-Plugins/Properties.json', '"locationBounds":', '''"locationBounds": [
        {"name":"Diamond Platform", "type":"AdventureZone", "pos1":"-1002 69 -1483", "pos2":"-1032 57 -1456"}
    ],'''),
        ],
        'linked':server_config + advancements_disabled + base_plugins + coreprotect + build_plugins,
    },

    'r1plots':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=7'),
            ('spigot.yml', 'view-distance', '    view-distance: 7'),
            ('server.properties', 'server-port', 'server-port=25573'),
            ('server.properties', 'difficulty', 'difficulty=0'),
            ('plugins/Socket4MC/config.yml', 'host', 'host: "127.0.0.8"'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=3G'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=3G'),
            #('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=2G'),
            #('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=2G'),
            ('plugins/Monumenta-Plugins/Properties.json', '"isTownWorld":', '"isTownWorld": true,'),
            ('plugins/Monumenta-Plugins/Properties.json', '"plotSurvivalMinHeight":', '"plotSurvivalMinHeight": 0,'),
        ],
        'linked':server_config + advancements_disabled + base_plugins + coreprotect + build_plugins,
    },

    'betaplots':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=7'),
            ('spigot.yml', 'view-distance', '    view-distance: 7'),
            ('server.properties', 'server-port', 'server-port=25574'),
            ('server.properties', 'difficulty', 'difficulty=0'),
            ('plugins/Socket4MC/config.yml', 'host', 'host: "127.0.0.9"'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=1536M'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=1536M'),
            ('plugins/Monumenta-Plugins/Properties.json', '"isTownWorld":', '"isTownWorld": true,'),
            ('plugins/Monumenta-Plugins/Properties.json', '"plotSurvivalMinHeight":', '"plotSurvivalMinHeight": 95,'),
        ],
        'linked':server_config_min_plus_data + advancements_disabled + base_plugins + coreprotect + build_plugins,
    },

    'vanilla':{
        'config':[
            ('eula.txt',),
            ('commands.yml',),
            ('help.yml',),
            ('permissions.yml',),
            ('spigot.yml',),
            ('wepif.yml',),
            # Note - mark2-scripts.txt is static!
            ('plugins/FastAsyncWorldEdit/config.yml',),
            ('plugins/CoreProtect/config.yml',),
            ('plugins/Monumenta-Plugins/config.yml',),
            ('plugins/Monumenta-Plugins/Properties.json',),

            ('server.properties', 'view-distance', 'view-distance=8'),
            ('server.properties', 'difficulty', 'difficulty=3'),
            ('server.properties', 'generate-structures', 'generate-structures=true'),
            ('server.properties', 'server-port', 'server-port=25575'),
            ('spigot.yml', 'view-distance', '    view-distance: 8'),
            ('spigot.yml', 'save-structure-info', '    save-structure-info: true'),
            ('plugins/Socket4MC/config.yml', 'host', 'host: "127.0.0.27"'),
            ('server.properties', 'difficulty', 'difficulty=3'),
            ('server.properties', 'gamemode', 'gamemode=0'),
            ('server.properties', 'allow-nether', 'allow-nether=true'),
            ('server.properties', 'white-list', 'white-list=false'),
            ('server.properties', 'spawn-protection', 'spawn-protection=16'),
            ('server.properties', 'pvp', 'pvp=true'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=2048M'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=2048M'),
            ('plugins/Monumenta-Plugins/Properties.json', '"transferDataEnabled":', '"transferDataEnabled": false,'),
            ('plugins/Monumenta-Plugins/Properties.json', '"broadcastCommandEnabled":', '"broadcastCommandEnabled": false,'),
            ('plugins/Monumenta-Plugins/Properties.json', '"allowedTransferTargets":', '"allowedTransferTargets": ["region_1"],'),
            ('plugins/Monumenta-Plugins/Properties.json', '"locationBounds":', '''"locationBounds": [
        {"name":"Spawn", "type":"SafeZone", "pos1":"-1520 43 1087", "pos2":"-1475 255 1126"}
    ],'''),
        ],
        'linked':server_config_min + luckperms_standalone + easywarp + socket4mc + coreprotect + worldedit + [('plugins/ScriptedQuests.jar', '../../server_config/plugins/ScriptedQuests.jar'),('plugins/EpicStructureManagement.jar', '../../server_config/plugins/EpicStructureManagement.jar'),('plugins/TogglePvp.jar', '../../server_config/plugins/TogglePvp.jar')]
    },

    'purgatory':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=4'),
            ('spigot.yml', 'view-distance', '    view-distance: 4'),
            ('server.properties', 'force-gamemode', 'force-gamemode=true'),
            ('server.properties', 'gamemode', 'gamemode=2'),
            ('server.properties', 'server-port', 'server-port=25570'),
            ('server.properties', 'enable-command-block', 'enable-command-block=false'),
            ('server.properties', 'white-list', 'white-list=false'),
            ('server.properties', 'spawn-animals', 'spawn-animals=false'),
            ('server.properties', 'spawn-monsters', 'spawn-monsters=false'),
            ('server.properties', 'spawn-npcs', 'spawn-npcs=false'),
            ('server.properties', 'spawn-protection', 'spawn-protection=16'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=128M'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=128M'),
        ],
        'linked':server_config + advancements_disabled,
    },

    'white':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=14'),
            ('spigot.yml', 'view-distance', '    view-distance: 14'),
            ('server.properties', 'server-port', 'server-port=25580'),
            ('server.properties', 'spawn-animals', 'spawn-animals=false'),
            ('plugins/Socket4MC/config.yml', 'host', 'host: "127.0.0.10"'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=2G'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=2G'),
            ('plugins/Monumenta-Plugins/Properties.json', '"locationBounds":', '''"locationBounds": [
        {"name":"Commands", "type":"RestrictedZone", "pos1":"-1584 0 -1632", "pos2":"-1329 255 -1377"}
    ],'''),
        ],
        'linked':server_config + advancements_disabled + base_plugins + coreprotect,
    },

    'orange':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=12'),
            ('spigot.yml', 'view-distance', '    view-distance: 12'),
            ('server.properties', 'server-port', 'server-port=25581'),
            ('server.properties', 'spawn-animals', 'spawn-animals=false'),
            ('plugins/Socket4MC/config.yml', 'host', 'host: "127.0.0.11"'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=2G'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=2G'),
            ('plugins/Monumenta-Plugins/Properties.json', '"locationBounds":', '''"locationBounds": [
        {"name":"Commands", "type":"RestrictedZone", "pos1":"-1584 0 -1632", "pos2":"-1329 255 -1377"}
    ],'''),
        ],
        'linked':server_config + advancements_disabled + base_plugins + coreprotect,
    },

    'magenta':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=12'),
            ('spigot.yml', 'view-distance', '    view-distance: 12'),
            ('server.properties', 'server-port', 'server-port=25582'),
            ('server.properties', 'spawn-animals', 'spawn-animals=false'),
            ('plugins/Socket4MC/config.yml', 'host', 'host: "127.0.0.12"'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=2G'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=2G'),
            ('plugins/Monumenta-Plugins/Properties.json', '"locationBounds":', '''"locationBounds": [
        {"name":"Commands", "type":"RestrictedZone", "pos1":"-1584 0 -1632", "pos2":"-1329 255 -1377"}
    ],'''),
        ],
        'linked':server_config + advancements_disabled + base_plugins + coreprotect,
    },

    'lightblue':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=12'),
            ('spigot.yml', 'view-distance', '    view-distance: 12'),
            ('server.properties', 'server-port', 'server-port=25583'),
            ('server.properties', 'spawn-animals', 'spawn-animals=false'),
            ('plugins/Socket4MC/config.yml', 'host', 'host: "127.0.0.13"'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=2G'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=2G'),
            ('plugins/Monumenta-Plugins/Properties.json', '"locationBounds":', '''"locationBounds": [
        {"name":"Commands", "type":"RestrictedZone", "pos1":"-1584 0 -1632", "pos2":"-1329 255 -1377"}
    ],'''),
        ],
        'linked':server_config + advancements_disabled + base_plugins + coreprotect,
    },

    'yellow':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=8'),
            ('spigot.yml', 'view-distance', '    view-distance: 8'),
            ('server.properties', 'server-port', 'server-port=25584'),
            ('server.properties', 'spawn-animals', 'spawn-animals=false'),
            ('plugins/Socket4MC/config.yml', 'host', 'host: "127.0.0.14"'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=2G'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=2G'),
            ('plugins/Monumenta-Plugins/Properties.json', '"locationBounds":', '''"locationBounds": [
        {"name":"Commands", "type":"RestrictedZone", "pos1":"-1584 0 -1632", "pos2":"-1329 255 -1377"}
    ],'''),
        ],
        'linked':server_config + advancements_disabled + base_plugins + coreprotect,
    },

    'r1bonus':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=8'),
            ('spigot.yml', 'view-distance', '    view-distance: 8'),
            ('server.properties', 'server-port', 'server-port=25600'),
            ('server.properties', 'spawn-animals', 'spawn-animals=false'),
            ('plugins/Socket4MC/config.yml', 'host', 'host: "127.0.0.30"'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=2G'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=2G'),
            ('plugins/Monumenta-Plugins/Properties.json', '"locationBounds":', '''"locationBounds": [
        {"name":"Commands", "type":"RestrictedZone", "pos1":"-1584 0 -1632", "pos2":"-1329 255 -1377"}
    ],'''),
        ],
        'linked':server_config + advancements_disabled + base_plugins + coreprotect,
    },
}


# config should be the entire config map
# data should be a tuple like ('server.properties', 'difficulty', 'difficulty=0')
def add_config_if_not_set(config, data):
    for key in config:
        exists = False
        for replacement in config[key]['config']:
            if len(replacement) == 3 and data[0] in replacement[0] and data[1] in replacement[1]:
                exists = True
        if not exists:
            config[key]['config'] += [data]

    return config

# Config additions that are specific to build or play server
if (SERVER_TYPE == 'build'):
    config = add_config_if_not_set(config, ('server.properties', 'difficulty', 'difficulty=0'))
    config = add_config_if_not_set(config, ('spigot.yml', 'tab-complete', '  tab-complete: 0'))

    config['region_1']['config'] += [
        ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=1536M'),
        ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=1536M'),
    ]
    config['roguelike']['config'] += [
        ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=1536M'),
        ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=1536M'),
    ]
else:
    config = add_config_if_not_set(config, ('server.properties', 'difficulty', 'difficulty=2'))
    config = add_config_if_not_set(config, ('spigot.yml', 'tab-complete', '  tab-complete: 9999'))

    config['region_1']['config'] += [
        ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=7G'),
        ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=7G'),
    ]
    config['roguelike']['config'] += [
        ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=3G'),
        ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=3G'),
    ]

def gen_server_config(servername):
    if not(servername in config):
        print "ERROR: No config available for '" + servername + "'"
        return

    dest = config[servername]
    serverConfig = dest["config"]

    ################################################################################
    # Copy customized configuration per-server
    ################################################################################

    # Get a unique list of files to copy
    files = [i[0] for i in serverConfig]
    files = list(set(files))

    # Copy those files and replace WORLDOOG with the appropriate string
    for filename in files:
        old = template_dir + "/" + filename
        new = servername + "/" + filename
        if (os.path.islink(new)):
            print "Warning - file '" + new + "' is link; not replacing it"
            continue

        try:
            os.makedirs(os.path.dirname(new))
        except OSError as e:
            pass

        with open(old, "rt") as fin:
            with open(new, "wt") as fout:
                for line in fin:
                    fout.write(line.replace('WORLDOOG', servername))
                fout.close()
            fin.close()

    # Do the per-file replacements
    for replacement in serverConfig:
        filename = servername + "/" + replacement[0]
        filename = filename.replace('WORLDOOG', servername)
        if (len(replacement) == 1):
            # Nothing to do here, just copying the file was enough
            continue;
        elif (len(replacement) == 2):
            # Need to append the second argument to the file
            with open(filename, "a") as fout:
                fout.write(replacement[1])
                fout.close()
        elif (len(replacement) == 3):
            os.rename(filename, filename + ".old")

            with open(filename + ".old", "rt") as fin:
                with open(filename, "wt") as fout:
                    for line in fin:
                        fout.write(re.sub("^[ \t]*" + replacement[1] + ".*$", replacement[2], line))
                    fout.close()
                fin.close()
            os.remove(filename + ".old")

    ################################################################################
    # Remove plugin directory symlinks if they exist
    ################################################################################
    for filename in os.listdir(servername + '/plugins'):
        filename = servername + '/plugins/' + filename
        if (os.path.islink(filename)):
            os.unlink(filename)

    ################################################################################
    # Create symlinks
    ################################################################################

    linked = dest["linked"]
    for link in linked:
        linkname = servername + "/" + link[0]
        linkname = linkname.replace('WORLDOOG', servername)

        if (os.path.islink(linkname)):
            os.unlink(linkname)
        if (os.path.isfile(linkname)):
            print "Warning - file that should be link detected. Please remove this file:"
            print "  rm -f " + linkname
            continue
        if (os.path.isdir(linkname)):
            print "Warning - directory that should be link detected. Please remove this directory:"
            print "  rm -rf " + linkname
            continue

        try:
            os.makedirs(os.path.dirname(linkname))
        except OSError as e:
            pass

        os.symlink(link[1], linkname)

    print "Success - " + servername

for servername in server_list:
    gen_server_config(servername)


