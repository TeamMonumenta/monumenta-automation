#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import sys
import os
import re

SERVER_TYPE='build'

# Main entry point
if (len(sys.argv) < 2):
    sys.exit("Usage: " + sys.argv[0] + " [--play] <minecraft_directory> [dir2] ...")

server_list = [];
for arg in sys.argv[1:]:
    if (arg == "--play"):
        SERVER_TYPE='play'
    else:
        server_list += [arg,]

if (len(server_list) < 1):
    print "ERROR: No folders specified"
    sys.exit("Usage: " + sys.argv[0] + " [--play] <minecraft_directory> [dir2] ...")

if SERVER_TYPE == 'build':
    print "Using build server settings!"
else:
    print "Using play server settings!"

server_config_to_copy = [
        ('bukkit.yml',),
        ('commands.yml',),
        ('eula.txt',),
        ('help.yml',),
        ('mark2.properties',),
        ('mark2-scripts.txt',),
        ('permissions.yml',),
        ('server.properties',),
        ('spigot.yml',),
        ('start.sh',),
        ('wepif.yml',),
        ('plugins/CoreProtect/config.yml',),
        ('plugins/FastAsyncWorldEdit/config.yml',),
        ('plugins/FastAsyncWorldEdit/config-legacy.yml',),
        ('plugins/Monumenta-Plugins/config.yml',),
        ('plugins/Monumenta-Plugins/Properties.json',),
        ('plugins/OpenInv/config.yml',),
        ('plugins/ProtocolLib/config.yml',),
        ('plugins/Socket4MC/config.yml',),
        ('plugins/Vault/config.yml',),
    ]


server_config_min = [
        ('spigot.jar', '../server_config/spigot.jar'),
        ('plugins/CommandAPI.jar', '../../server_config/plugins/CommandAPI.jar'),
        ('plugins/BungeeTabListPlus_BukkitBridge.jar', '../../server_config/plugins/BungeeTabListPlus_BukkitBridge.jar'),
        ('plugins/Vault.jar', '../../server_config/plugins/Vault.jar'),
        ('plugins/ProtocolLib.jar', '../../server_config/plugins/ProtocolLib.jar'),
        ('plugins/PlaceholderAPI.jar', '../../server_config/plugins/PlaceholderAPI.jar'),
        ('plugins/PlaceholderAPI', '../../server_config/plugins/PlaceholderAPI'),
        ('plugins/VentureChat.jar', '../../server_config/plugins/VentureChat.jar'),
        ('plugins/VentureChat/config.yml', '../../../server_config/plugins/VentureChat/{}/config.yml'.format(SERVER_TYPE)),
        ('plugins/BKCommonLib.jar', '../../server_config/plugins/BKCommonLib.jar'),
        ('plugins/LightCleaner.jar', '../../server_config/plugins/LightCleaner.jar'),
    ]

server_config = server_config_min + [
        ('Project_Epic-{servername}/generated', '../../server_config/data/generated'),
        ('Project_Epic-{servername}/datapacks', '../../server_config/data/datapacks'),
        ('Project_Epic-{servername}_the_end/datapacks', '../../server_config/data/datapacks'),
    ]

monumenta_without_mobs_plugins = [
        ('plugins/EpicWarps.jar', '../../server_config/plugins/EpicWarps.jar'),
        ('plugins/ScriptedQuests.jar', '../../server_config/plugins/ScriptedQuests.jar'),
        ('plugins/ScriptedQuests/npcs/{servername}', '../../../../server_config/data/scriptedquests/npcs/{servername}'),
        ('plugins/ScriptedQuests/npcs/common', '../../../../server_config/data/scriptedquests/npcs/common'),
        ('plugins/ScriptedQuests/compass/{servername}', '../../../../server_config/data/scriptedquests/compass/{servername}'),
        ('plugins/ScriptedQuests/compass/common', '../../../../server_config/data/scriptedquests/compass/common'),
        ('plugins/ScriptedQuests/death/{servername}', '../../../../server_config/data/scriptedquests/death/{servername}'),
        ('plugins/ScriptedQuests/death/common', '../../../../server_config/data/scriptedquests/death/common'),
        ('plugins/ScriptedQuests/races/{servername}', '../../../../server_config/data/scriptedquests/races/{servername}'),
        ('plugins/ScriptedQuests/races/common', '../../../../server_config/data/scriptedquests/races/common'),
        ('plugins/EpicStructureManagement.jar', '../../server_config/plugins/EpicStructureManagement.jar'),
        ('plugins/EpicStructureManagement/structures', '../../../server_config/data/structures'),
        ('plugins/EpicStructureManagement/config.yml', '../../../server_config/data/plugins/{servername}/EpicStructureManagement/config.yml'),
    ]
monumenta = monumenta_without_mobs_plugins + [
        ('plugins/Monumenta-Plugins.jar', '../../server_config/plugins/Monumenta-Plugins.jar'),
        ('plugins/Monumenta-Bossfights.jar', '../../server_config/plugins/Monumenta-Bossfights.jar'),
    ]

coreprotect = [
        ('plugins/CoreProtect.jar', '../../server_config/plugins/CoreProtect.jar'),
    ]

worldedit = [
        ('plugins/FastAsyncWorldEdit.jar', '../../server_config/plugins/FastAsyncWorldEdit.jar'),
        ('plugins/DummyFawe.jar', '../../server_config/plugins/DummyFawe.jar'),
        ('plugins/FastAsyncWorldEdit/commands', '../../../server_config/plugins/FastAsyncWorldEdit/commands'),
        ('plugins/FastAsyncWorldEdit/schematics', '/home/rock/4_SHARED/schematics'),
    ]

dynmap = [
        ('plugins/Dynmap.jar', '../../server_config/plugins/Dynmap.jar'),
        ('plugins/dynmap/configuration.txt', '../../../server_config/data/plugins/{servername}/dynmap/' + SERVER_TYPE + '/configuration.txt'),
        ('plugins/dynmap/worlds.txt', '../../../server_config/data/plugins/{servername}/dynmap/' + SERVER_TYPE + '/worlds.txt'),
    ]

luckperms_standalone = [
        ('plugins/LuckPerms-Bukkit.jar', '../../server_config/plugins/LuckPerms-Bukkit.jar'),
        ('plugins/LuckPerms/lib', '../../../server_config/plugins/LuckPerms/{}/lib'.format(SERVER_TYPE)),
    ]
luckperms = [
        ('plugins/LuckPerms-Bukkit.jar', '../../server_config/plugins/LuckPerms-Bukkit.jar'),
        ('plugins/LuckPerms', '../../server_config/plugins/LuckPerms/{}'.format(SERVER_TYPE)),
    ]

nbteditor = [
        ('plugins/nbteditor.jar', '../../server_config/plugins/nbteditor.jar'),
        ('plugins/NBTEditor', '../../server_config/plugins/NBTEditor'),
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
    ]

# Analytics plugin - only for the play server!
plan = [
        ('plugins/Plan.jar', '../../server_config/plugins/Plan.jar'),
        ('plugins/Plan', '../../server_config/data/plugins/{servername}/Plan'),
    ]


# Index of nodes:
#   server_config
#   structures

base_plugins = luckperms + monumenta + openinv + socket4mc + worldedit + coreprotect
if (SERVER_TYPE == 'build'):
    base_plugins += speedchanger + nbteditor + voxelsniper
else:
    base_plugins += []

# String replacements:
# {servername} - server name
#('server.properties', 'motd', 'motd=Monumenta\: {servername} shard'),
#('plugins/Socket4MC/config.yml', 'name', 'name: "{servername}"'),
#('mark2.properties', 'plugin.backup.path', 'plugin.backup.path=../backups/{servername}/{servername}_{timestamp}.tar.gz'),
#('server.properties', 'level-name', 'level-name=Project_Epic-{servername}'),

template_dir = 'server_config/data/server_config_template'

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
            ('server.properties', 'view-distance', 'view-distance=9'),
            ('spigot.yml', 'view-distance', '    view-distance: 9'),
            ('server.properties', 'server-port', 'server-port=25566'),
            ('mark2-scripts.txt', '     0    3    *    *    *    /setblock -1449 1 -1440 redstone_block'),
            ('plugins/Monumenta-Plugins/Properties.json', '"dailyResetEnabled":', '"dailyResetEnabled": true,'),
            ('plugins/Monumenta-Plugins/Properties.json', '"plotSurvivalMinHeight":', '"plotSurvivalMinHeight": 95,'),
            ('plugins/Monumenta-Plugins/Properties.json', '"questCompassEnabled":', '"questCompassEnabled": true,'),
            ('plugins/Monumenta-Plugins/Properties.json', '"locationBounds":', '''"locationBounds": [
        {"name":"Arena", "type":"AdventureZone", "pos1":"-966 90 -124", "pos2":"-926 256 -84"},
        {"name":"Capital", "type":"Capital", "pos1":"-1130 0 -284", "pos2":"-498 256 344"},

        {"name":"Nyr", "type":"SafeZone", "pos1":"-181 0 -166", "pos2":"-79 256 14"},
        {"name":"NyrAddon", "type":"SafeZone", "pos1":"-229 1 -126", "pos2":"-182 33 -79"},
        {"name":"NyrSewer", "type":"SafeZone", "pos1":"-170 28 -75", "pos2":"-217 0 -126"},
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
        {"name":"Kathryn's Trees", "type":"AdventureZone", "pos1":"869 108 213", "pos2":"895 135 183"},
        {"name":"Malevolent Reverie Lobby", "type":"SafeZone", "pos1":"1130 55 155", "pos2":"1172 88 222"},

        {"name":"Monument", "type":"SafeZone", "pos1":"1160 0 -320", "pos2":"1400 256 -115"},
        {"name":"Mystic Grotto", "type":"SafeZone", "pos1":"317 61 309", "pos2":"383 106 392"},
        {"name":"Brown Co 57 Floating Island", "type":"SafeZone", "pos1":"887 0 -927", "pos2":"978 255 -899"},
        {"name":"Tutorial Dungeon Flashback", "type":"SafeZone", "pos1":"1126 5 148", "pos2":"1177 35 224"},
        {"name":"Roguelike Entrance Puzzle", "type":"SafeZone", "pos1":"825 0 173", "pos2":"889 97 217"},
        {"name":"Mansion Vault", "type":"SafeZone", "pos1":"-14 84 -231", "pos2":"10 102 -202"},
        {"name":"Replica Hall", "type":"SafeZone", "pos1":"-2133 44 551", "pos2":"-2077 113 798"},

        {"name":"Commands", "type":"RestrictedZone", "pos1":"-1584 0 -1632", "pos2":"-1329 255 -1377"},
        {"name":"Siege Of Highwatch", "type":"AdventureZone", "pos1":"1505 102 -178", "pos2":"1631 256 -16"},
        {"name":"Ctaz", "type":"AdventureZone", "pos1":"227 10 294", "pos2":"252 256 320"},
        {"name":"Hermy", "type":"AdventureZone", "pos1":"-331 86 334", "pos2":"-310 110 355"},
        {"name":"West Water Tower", "type":"AdventureZone", "pos1":"-1377 0 -173", "pos2":"-1336 255 -132"},
        {"name":"Storytime Island", "type":"AdventureZone", "pos1":"-1802 0 -291", "pos2":"-1779 255 -264"},

        {"name":"Fountain of Miracles Patreon Trader", "type":"AdventureZone", "pos1":"501 67 437", "pos2":"512 57 422"},
        {"name":"Cursed Forest Patreon Trader", "type":"AdventureZone", "pos1":"1163 100 87", "pos2":"1151 90 80"},
        {"name":"Nivalis Cave", "type":"AdventureZone", "pos1":"998 119 -320", "pos2":"1008 135 -295"},
        {"name":"Haunted House Quest", "type":"AdventureZone", "pos1":"1000 7 72", "pos2":"1042 38 108"},
        {"name":"Lost In My Mind - Bunker", "type":"AdventureZone", "pos1":"572 93 243", "pos2":"582 111 262"},
        {"name":"Crew To Remember", "type":"AdventureZone", "pos1":"-1443 130 21", "pos2":"-1530 82 -90"},
        {"name":"Crew To Remember Smuggler Drop", "type":"AdventureZone", "pos1":"-60 60 -4", "pos2":"-48 46 8"},
        {"name":"Crew To Remember Cabin", "type":"AdventureZone", "pos1":"642 52 475", "pos2":"660 40 491"},
        {"name":"Xin Old", "type":"AdventureZone", "pos1":"798 172 -393", "pos2":"781 161 -376"},
        {"name":"Xin New", "type":"AdventureZone", "pos1":"1092 99 -234", "pos2":"1076 116 -218"},

        {"name":"Azacors Arena", "type":"AdventureZone", "pos1":"873 216 -465", "pos2":"769 169 -524"},
        {"name":"Azacor Witch Hut", "type":"AdventureZone", "pos1":"1443 166 164", "pos2":"1475 191 192"},
        {"name":"Azacor Ritual Room", "type":"AdventureZone", "pos1":"1256 140 304", "pos2":"1301 116 343"},
        {"name":"Azacor Lobby", "type":"SafeZone", "pos1":"1223 0 -156", "pos2":"1341 28 -80"},
        {"name":"Azacor Arena Tunnel 1", "type":"AdventureZone", "pos1":"1432 13 -390", "pos2":"1436 16 -380"},
        {"name":"Azacor Arena Tunnel 2", "type":"AdventureZone", "pos1":"1432 14 -240", "pos2":"1436 17 -230"},
        {"name":"Azacor Arena Tunnel 3", "type":"AdventureZone", "pos1":"1432 15 -90", "pos2":"1436 18 -80"},
        {"name":"Outer Demons", "type":"AdventureZone", "pos1":"1601 42 79", "pos2":"1687 12 -10"},
        {"name":"Chesterfield Grove Ruins", "type":"AdventureZone", "pos1":"1331 200 17", "pos2":"1347 218 35"},

        {"name":"Light Blue Tower Basement", "type":"AdventureZone", "pos1":"881 153 -334", "pos2":"824 109 -303"},

        {"name":"Starrier Night - Gaius Tower", "type":"AdventureZone", "pos1":"-99 115 69", "pos2":"-120 70 93"},
        {"name":"Starrier Night - Lowtide Montana", "type":"SafeZone", "pos1":"739 121 433", "pos2":"717 97 409"},
        {"name":"Starrier Night - Fishing Huts Bunker", "type":"AdventureZone", "pos1":"-408 43 -15", "pos2":"-384 28 9"},
        {"name":"Starrier Night - Fishing Hut Bunker Entrance", "type":"AdventureZone", "pos1":"-401 80 -8", "pos2":"-391 90 4"},

        {"name":"Nelfine 2 - New Lab", "type":"AdventureZone", "pos1":"813 54 -243", "pos2":"767 8 -135"},
        {"name":"Nelfine 2 - Destroyed Lab", "type":"AdventureZone", "pos1":"323 63 426", "pos2":"393 115 499"},
        {"name":"Nelfine 2 - Arian Office Replica", "type":"AdventureZone", "pos1":"1248 156 -120", "pos2":"1266 132 -98"},
        {"name":"Nelfine 2 - Old Farr", "type":"AdventureZone", "pos1":"892 256 415", "pos2":"771 172 541"},

        {"name":"Orange Quest Entrance Locked", "type":"AdventureZone", "pos1":"315 125 -239", "pos2":"343 102 -202"},
        {"name":"Orange Quest Entrance Outside", "type":"AdventureZone", "pos1":"350 81 -137", "pos2":"376 66 -104"},
        {"name":"Orange Quest Crypt", "type":"SafeZone", "pos1":"297 28 1598", "pos2":"427 191 1821"},
        {"name":"Orange Quest Alchemy", "type":"AdventureZone", "pos1":"428 28 1598", "pos2":"463 191 1821"},
        {"name":"Orange Quest Arena", "type":"AdventureZone", "pos1":"353 65 1538", "pos2":"425 127 1597"},

        {"name":"Quarantined Farr", "type":"SafeZone", "pos1":"781 261 725", "pos2":"908 169 590"},
        {"name":"Valara", "type":"AdventureZone", "pos1":"915 167 702", "pos2":"1018 229 797"},
        {"name":"Sewer Gate", "type":"AdventureZone", "pos1":"482 88 134", "pos2":"518 59 94"},

        {"name":"Ta'Eldim Gateway", "type":"AdventureZone", "pos1":"440 101 -256", "pos2":"485 68 -214"},
        {"name":"Ta'Eldim", "type":"SafeZone", "pos1":"376 255 -461", "pos2":"543 147 -297"},

        {"name":"post-monument Sage Draiikali", "type":"AdventureZone", "pos1":"1220 0 -126", "pos2":"1242 255 -103"},
        {"name":"Farr race", "type":"AdventureZone", "pos1":"1036 99 -119", "pos2":"1051 112 -105"}
    ],'''),
        ],
        'linked':server_config + base_plugins + dynmap + [
            ('plugins/nuvotifier.jar', '../../server_config/plugins/nuvotifier.jar'),
            ('plugins/Votifier', '../../server_config/data/plugins/region_1/Votifier'),
        ],
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
        'linked':server_config + base_plugins + dynmap,
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
        'linked':server_config + base_plugins,
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
        'linked':server_config + base_plugins + dynmap,
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
        'linked':server_config + base_plugins,
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
        'linked':server_config + base_plugins,
    },

    'build':{
        'config':server_config_to_copy + [
            ('server.properties', 'white-list', 'white-list=true'),
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
        'linked':server_config_min + luckperms_standalone + monumenta + socket4mc + worldedit + speedchanger + nbteditor + voxelsniper
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
        'linked':server_config + luckperms + openinv + socket4mc + worldedit + nbteditor + dynmap + monumenta_without_mobs_plugins + [
            ('plugins/Monumenta-Plugins.jar', '/home/epic/mob_shard_plugins/Monumenta-Plugins.jar'),
            ('plugins/Monumenta-Bossfights.jar', '/home/epic/mob_shard_plugins/Monumenta-Bossfights.jar'),
        ]
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
            ('plugins/Monumenta-Plugins/Properties.json', '"isTownWorld":', '"isTownWorld": true,'),
            ('plugins/Monumenta-Plugins/Properties.json', '"plotSurvivalMinHeight":', '"plotSurvivalMinHeight": 0,'),
        ],
        'linked':server_config + base_plugins,
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
        'linked':server_config + base_plugins,
    },

    'nightmare':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=10'),
            ('spigot.yml', 'view-distance', '    view-distance: 10'),
            ('server.properties', 'server-port', 'server-port=25576'),
            ('server.properties', 'spawn-animals', 'spawn-animals=false'),
            ('plugins/Socket4MC/config.yml', 'host', 'host: "127.0.0.26"'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=3G'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=3G'),
            ('plugins/Monumenta-Plugins/Properties.json', '"locationBounds":', '''"locationBounds": [
        {"name":"Commands", "type":"RestrictedZone", "pos1":"-1584 0 -1632", "pos2":"-1329 255 -1377"}
    ],'''),
        ],
        'linked':server_config + base_plugins,
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
        'linked':server_config_min,
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
        'linked':server_config + base_plugins,
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
        'linked':server_config + base_plugins,
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
        'linked':server_config + base_plugins,
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
        'linked':server_config + base_plugins,
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
        'linked':server_config + base_plugins,
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
        'linked':server_config + base_plugins,
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
    config = add_config_if_not_set(config, ('server.properties', 'white-list', 'white-list=true'))

    config['region_1']['config'] += [
        ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=1536M'),
        ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=1536M'),
        ('server.properties', 'server-ip=', 'server-ip=127.0.0.1'),
        ('plugins/Socket4MC/config.yml', 'host', 'host: "127.0.0.2"'),
    ]
    config['roguelike']['config'] += [
        ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=1536M'),
        ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=1536M'),
    ]
else:
    config = add_config_if_not_set(config, ('server.properties', 'difficulty', 'difficulty=2'))
    config = add_config_if_not_set(config, ('spigot.yml', 'tab-complete', '  tab-complete: 9999'))
    config = add_config_if_not_set(config, ('server.properties', 'white-list', 'white-list=false'))

    config['region_1']['config'] += [
        ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=20G'),
        ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=20G'),
        ('server.properties', 'server-ip=', 'server-ip='),
        ('plugins/Socket4MC/config.yml', 'host', 'host: "play.playmonumenta.com"'),
    ]
    config['roguelike']['config'] += [
        ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=3G'),
        ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=3G'),
    ]

    # Player analytics plugin only for play server
    for key in config:
        if not "purgatory" in key:
            if "build" in key:
                config[key]['linked'] = config[key]['linked'] + plan
            else:
                config[key]['linked'] = config[key]['linked'] + plan


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

    # Copy those files and replace {servername} with the appropriate string
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
                    fout.write(line.replace("{servername}",servername))
                fout.close()
            fin.close()

    # Do the per-file replacements
    for replacement in serverConfig:
        filename = servername + "/" + replacement[0]
        filename = filename.replace("{servername}",servername)
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
        targetname = link[1]
        linkname = linkname.replace("{servername}",servername)
        targetname = targetname.replace("{servername}",servername)

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

        os.symlink(targetname, linkname)

    print "Success - " + servername

for servername in server_list:
    gen_server_config(servername)


