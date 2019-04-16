#!/usr/bin/env python3

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
    print("ERROR: No folders specified")
    sys.exit("Usage: " + sys.argv[0] + " [--play] <minecraft_directory> [dir2] ...")

if SERVER_TYPE == 'build':
    print("Using build server settings!")
else:
    print("Using play server settings!")

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
        ('paper.yml',),
        ('start.sh',),
        ('wepif.yml',),
        ('plugins/CoreProtect/config.yml',),
        ('plugins/FastAsyncWorldEdit/config.yml',),
        ('plugins/FastAsyncWorldEdit/config-legacy.yml',),
        ('plugins/MonumentaMain/config.yml',),
        ('plugins/ScriptedQuests/config.yml',),
        ('plugins/OpenInv/config.yml',),
        ('plugins/ProtocolLib/config.yml',),
        ('plugins/Socket4MC/config.yml',),
        ('plugins/Vault/config.yml',),
        ('plugins/ChestSort/config.yml',),
        ('plugins/dynmap/custom-lightings.txt',),
    ]

purgatory_min = [
        ('paperclip.jar', '../server_config/paperclip.jar'),
        ('plugins/Vault.jar', '../../server_config/plugins/Vault.jar'),
        ('plugins/ProtocolLib.jar', '../../server_config/plugins/ProtocolLib.jar'),
        ('plugins/PlaceholderAPI.jar', '../../server_config/plugins/PlaceholderAPI.jar'),
        ('plugins/VentureChat.jar', '../../server_config/plugins/VentureChat.jar'),
        ('plugins/VentureChat/config.yml', '../../../server_config/plugins/VentureChat/{}/config.yml'.format(SERVER_TYPE)),
    ]

server_config_min = purgatory_min + [
        ('plugins/PlaceholderAPI', '../../server_config/plugins/PlaceholderAPI'),
        ('plugins/CommandAPI.jar', '../../server_config/plugins/CommandAPI.jar'),
        ('plugins/BungeeTabListPlus_BukkitBridge.jar', '../../server_config/plugins/BungeeTabListPlus_BukkitBridge.jar'),
        ('plugins/BKCommonLib.jar', '../../server_config/plugins/BKCommonLib.jar'),
        ('plugins/LightCleaner.jar', '../../server_config/plugins/LightCleaner.jar'),
    ]

server_config = server_config_min + [
        ('Project_Epic-{servername}/generated', '../../server_config/data/generated'),
        ('Project_Epic-{servername}/datapacks', '../../server_config/data/datapacks'),
    ]

monumenta_without_mobs_plugins = [
        ('plugins/EpicWarps.jar', '../../server_config/plugins/EpicWarps.jar'),
        ('plugins/ScriptedQuests.jar', '../../server_config/plugins/ScriptedQuests.jar'),
        ('plugins/JeffChestSort.jar', '../../server_config/plugins/JeffChestSort.jar'),
        ('plugins/ScriptedQuests/npcs/{servername}', '../../../../server_config/data/scriptedquests/npcs/{servername}'),
        ('plugins/ScriptedQuests/npcs/common', '../../../../server_config/data/scriptedquests/npcs/common'),
        ('plugins/ScriptedQuests/compass/{servername}', '../../../../server_config/data/scriptedquests/compass/{servername}'),
        ('plugins/ScriptedQuests/compass/common', '../../../../server_config/data/scriptedquests/compass/common'),
        ('plugins/ScriptedQuests/death/{servername}', '../../../../server_config/data/scriptedquests/death/{servername}'),
        ('plugins/ScriptedQuests/death/common', '../../../../server_config/data/scriptedquests/death/common'),
        ('plugins/ScriptedQuests/races/{servername}', '../../../../server_config/data/scriptedquests/races/{servername}'),
        ('plugins/ScriptedQuests/races/common', '../../../../server_config/data/scriptedquests/races/common'),
        ('plugins/ScriptedQuests/traders/{servername}', '../../../../server_config/data/scriptedquests/traders/{servername}'),
        ('plugins/ScriptedQuests/traders/common', '../../../../server_config/data/scriptedquests/traders/common'),
        ('plugins/EpicStructureManagement.jar', '../../server_config/plugins/EpicStructureManagement.jar'),
        ('plugins/EpicStructureManagement/structures', '../../../server_config/data/structures'),
        ('plugins/EpicStructureManagement/config.yml', '../../../server_config/data/plugins/{servername}/EpicStructureManagement/config.yml'),
        ('plugins/MonumentaMain/Properties.json', '../../../server_config/data/plugins/{servername}/MonumentaMain/Properties.json'),
    ]
monumenta = monumenta_without_mobs_plugins + [
        ('plugins/MonumentaMain.jar', '../../server_config/plugins/MonumentaMain.jar'),
        ('plugins/MonumentaNMS.jar', '../../server_config/plugins/MonumentaNMS.jar'),
        ('plugins/MonumentaBosses.jar', '../../server_config/plugins/MonumentaBosses.jar'),
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
        ('plugins/dynmap/markers.yml', '../../../server_config/data/plugins/{servername}/dynmap/' + SERVER_TYPE + '/markers.yml'),
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

gobrush = [
        ('plugins/goBrush.jar', '../../server_config/plugins/goBrush.jar'),
        ('plugins/goPaint.jar', '../../server_config/plugins/goPaint.jar'),
        ('plugins/goBrush', '../../server_config/plugins/goBrush'),
    ]

# Index of nodes:
#   server_config
#   structures

base_plugins = luckperms + monumenta + openinv + socket4mc + worldedit + coreprotect
if (SERVER_TYPE == 'build'):
    base_plugins += speedchanger + nbteditor + voxelsniper + gobrush
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
            ('server.properties', 'view-distance', 'view-distance=8'),
            ('spigot.yml', 'view-distance', '    view-distance: 8'),
            ('server.properties', 'server-port', 'server-port=25566'),
            ('mark2-scripts.txt', '     0    3    *    *    *    /function monumenta:on_new_day/global'),
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
            ('mark2-scripts.txt', '     0    3    *    *    *    /function monumenta:on_new_day/global'),
        ],
        'linked':server_config + base_plugins + dynmap,
    },

    'tutorial':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=9'),
            ('server.properties', 'white-list', 'white-list=false'),
            ('spigot.yml', 'view-distance', '    view-distance: 9'),
            ('server.properties', 'server-port', 'server-port=25567'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=1G'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=1G'),
        ],
        'linked':server_config + base_plugins,
    },

    'dungeon':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=12'),
            ('spigot.yml', 'view-distance', '    view-distance: 12'),
            ('server.properties', 'server-port', 'server-port=25572'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=1536M'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=1536M'),
        ],
        'linked':server_config + base_plugins + dynmap + [
            ('plugins/ScriptedQuests/npcs/tutorial', '../../../../server_config/data/scriptedquests/npcs/tutorial'),
            ('plugins/ScriptedQuests/npcs/labs', '../../../../server_config/data/scriptedquests/npcs/labs'),
        ],
    },

    'roguelike':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=8'),
            ('spigot.yml', 'view-distance', '    view-distance: 8'),
            ('server.properties', 'server-port', 'server-port=25569'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=2G'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=2G'),
        ],
        'linked':server_config + base_plugins,
    },

    'test':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=8'),
            ('spigot.yml', 'view-distance', '    view-distance: 8'),
            ('server.properties', 'server-port', 'server-port=25571'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=1G'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=1G'),
        ],
        'linked':server_config + base_plugins,
    },

    'update_do_not_use':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=8'),
            ('spigot.yml', 'view-distance', '    view-distance: 8'),
            ('server.properties', 'server-port', 'server-port=25603'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=5G'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=5G'),
        ],
        'linked':server_config_min + luckperms_standalone + monumenta + socket4mc + worldedit + speedchanger + nbteditor + voxelsniper + coreprotect,
    },

    'pvp_do_not_use':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=8'),
            ('spigot.yml', 'view-distance', '    view-distance: 8'),
            ('server.properties', 'server-port', 'server-port=25604'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=5G'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=5G'),
        ],
        'linked':server_config_min + luckperms_standalone + monumenta + socket4mc + worldedit + speedchanger + nbteditor + voxelsniper + coreprotect,
    },

    'build':{
        'config':server_config_to_copy + [
            ('server.properties', 'white-list', 'white-list=true'),
            ('server.properties', 'view-distance', 'view-distance=8'),
            ('spigot.yml', 'view-distance', '    view-distance: 8'),
            ('server.properties', 'server-port', 'server-port=25599'),
            ('spigot.yml', 'tab-complete', '  tab-complete: 0'),
            ('server.properties', 'difficulty', 'difficulty=0'),
            ('server.properties', 'gamemode', 'gamemode=1'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=1280M'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=1280M'),
        ],
        'linked':server_config_min + luckperms_standalone + monumenta + socket4mc + worldedit + speedchanger + nbteditor + voxelsniper + dynmap + coreprotect + gobrush,
    },

    'mobs':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=6'),
            ('spigot.yml', 'view-distance', '    view-distance: 6'),
            ('server.properties', 'server-port', 'server-port=25598'),
            ('server.properties', 'difficulty', 'difficulty=2'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=768M'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=768M'),
        ],
        'linked':server_config + luckperms + openinv + socket4mc + worldedit + nbteditor + dynmap + speedchanger + monumenta_without_mobs_plugins + coreprotect + [
            ('plugins/MonumentaMain.jar', '/home/epic/mob_shard_plugins/MonumentaMain.jar'),
            ('plugins/MonumentaBosses.jar', '/home/epic/mob_shard_plugins/MonumentaBosses.jar'),
            ('plugins/MonumentaNMS.jar', '/home/epic/mob_shard_plugins/MonumentaNMS.jar'),
        ]
    },

    'r1plots':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=7'),
            ('spigot.yml', 'view-distance', '    view-distance: 7'),
            ('server.properties', 'server-port', 'server-port=25573'),
            ('server.properties', 'difficulty', 'difficulty=0'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=3G'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=3G'),
        ],
        'linked':server_config + base_plugins + dynmap,
    },

    'betaplots':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=7'),
            ('spigot.yml', 'view-distance', '    view-distance: 7'),
            ('server.properties', 'server-port', 'server-port=25574'),
            ('server.properties', 'difficulty', 'difficulty=0'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=1536M'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=1536M'),
        ],
        'linked':server_config + base_plugins,
    },

    'nightmare':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=10'),
            ('spigot.yml', 'view-distance', '    view-distance: 10'),
            ('server.properties', 'server-port', 'server-port=25576'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=3G'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=3G'),
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
            ('server.properties', 'spawn-monsters', 'spawn-monsters=false'),
            ('server.properties', 'spawn-npcs', 'spawn-npcs=false'),
            ('server.properties', 'spawn-protection', 'spawn-protection=16'),
            ('paper.yml', 'keep-spawn-loaded', '    keep-spawn-loaded: true'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=256M'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=256M'),
        ],
        'linked':purgatory_min,
    },

    'white':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=16'),
            ('spigot.yml', 'view-distance', '    view-distance: 16'),
            ('server.properties', 'server-port', 'server-port=25580'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=1536M'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=1536M'),
        ],
        'linked':server_config + base_plugins,
    },

    'orange':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=12'),
            ('spigot.yml', 'view-distance', '    view-distance: 12'),
            ('server.properties', 'server-port', 'server-port=25581'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=1536M'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=1536M'),
        ],
        'linked':server_config + base_plugins,
    },

    'magenta':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=12'),
            ('spigot.yml', 'view-distance', '    view-distance: 12'),
            ('server.properties', 'server-port', 'server-port=25582'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=1536M'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=1536M'),
        ],
        'linked':server_config + base_plugins,
    },

    'lightblue':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=12'),
            ('spigot.yml', 'view-distance', '    view-distance: 12'),
            ('server.properties', 'server-port', 'server-port=25583'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=1536M'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=1536M'),
        ],
        'linked':server_config + base_plugins,
    },

    'yellow':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=8'),
            ('spigot.yml', 'view-distance', '    view-distance: 8'),
            ('server.properties', 'server-port', 'server-port=25584'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=1536M'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=1536M'),
        ],
        'linked':server_config + base_plugins,
    },

    'lime':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=9'),
            ('spigot.yml', 'view-distance', '    view-distance: 9'),
            ('server.properties', 'server-port', 'server-port=25585'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=1536M'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=1536M'),
        ],
        'linked':server_config + base_plugins,
    },

    'pink':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=8'),
            ('spigot.yml', 'view-distance', '    view-distance: 8'),
            ('server.properties', 'server-port', 'server-port=25586'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=1536M'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=1536M'),
        ],
        'linked':server_config + base_plugins,
    },

    'gray':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=8'),
            ('spigot.yml', 'view-distance', '    view-distance: 8'),
            ('server.properties', 'server-port', 'server-port=25587'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=1536M'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=1536M'),
        ],
        'linked':server_config + base_plugins,
    },

    'lightgray':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=8'),
            ('spigot.yml', 'view-distance', '    view-distance: 8'),
            ('server.properties', 'server-port', 'server-port=25588'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=1536M'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=1536M'),
        ],
        'linked':server_config + base_plugins,
    },

    'cyan':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=8'),
            ('spigot.yml', 'view-distance', '    view-distance: 8'),
            ('server.properties', 'server-port', 'server-port=25589'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=1536M'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=1536M'),
        ],
        'linked':server_config + base_plugins,
    },

    'purple':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=8'),
            ('spigot.yml', 'view-distance', '    view-distance: 8'),
            ('server.properties', 'server-port', 'server-port=25590'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=1536M'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=1536M'),
        ],
        'linked':server_config + base_plugins,
    },

    'r1bonus':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=8'),
            ('spigot.yml', 'view-distance', '    view-distance: 8'),
            ('server.properties', 'server-port', 'server-port=25600'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=1536M'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=1536M'),
        ],
        'linked':server_config + base_plugins,
    },

    'sanctum':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=10'),
            ('spigot.yml', 'view-distance', '    view-distance: 10'),
            ('server.properties', 'server-port', 'server-port=25601'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=1536M'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=1536M'),
        ],
        'linked':server_config + base_plugins,
    },

    'labs':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=9'),
            ('spigot.yml', 'view-distance', '    view-distance: 9'),
            ('server.properties', 'server-port', 'server-port=25602'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=1536M'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=1536M'),
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
    config = add_config_if_not_set(config, ('plugins/ScriptedQuests/config.yml', 'show_timer_names', 'show_timer_names: true'))

    config['region_1']['config'] += [
        ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=3G'),
        ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=3G'),
    ]
    config['region_2']['config'] += [
        ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=4G'),
        ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=4G'),
    ]
else:
    config = add_config_if_not_set(config, ('server.properties', 'difficulty', 'difficulty=2'))
    config = add_config_if_not_set(config, ('spigot.yml', 'tab-complete', '  tab-complete: 9999'))
    config = add_config_if_not_set(config, ('server.properties', 'white-list', 'white-list=false'))
    config = add_config_if_not_set(config, ('plugins/ScriptedQuests/config.yml', 'show_timer_names', 'show_timer_names: false'))

    config['region_1']['config'] += [
        ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=8G'),
        ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=8G'),
    ]
    config['region_2']['config'] += [
        ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=8G'),
        ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=8G'),
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
        print("ERROR: No config available for '" + servername + "'")
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
            print("Warning - file '" + new + "' is link; not replacing it")
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
            print("Warning - file that should be link detected. Please remove this file:")
            print("  rm -f " + linkname)
            continue
        if (os.path.isdir(linkname)):
            print("Warning - directory that should be link detected. Please remove this directory:")
            print("  rm -rf " + linkname)
            continue

        try:
            os.makedirs(os.path.dirname(linkname))
        except OSError as e:
            pass

        os.symlink(targetname, linkname)

    print("Success - " + servername)

for servername in server_list:
    gen_server_config(servername)

