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
        ('permissions.yml',),
        ('server.properties',),
        ('spigot.yml',),
        ('paper.yml',),
        ('start.sh',),
        ('wepif.yml',),
        ('plugins/CoreProtect/config.yml',),
        ('plugins/FastAsyncWorldEdit/config.yml',),
        ('plugins/FastAsyncWorldEdit/config-legacy.yml',),
        ('plugins/ScriptedQuests/config.yml',),
        ('plugins/OpenInv/config.yml',),
        ('plugins/ProtocolLib/config.yml',),
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
        ('plugins/MonumentaWarps.jar', '../../server_config/plugins/MonumentaWarps.jar'),
        ('plugins/ScriptedQuests.jar', '../../server_config/plugins/ScriptedQuests.jar'),
        ('plugins/JeffChestSort.jar', '../../server_config/plugins/JeffChestSort.jar'),
        ('plugins/ScriptedQuests/compass/{servername}', '../../../../server_config/data/scriptedquests/compass/{servername}'),
        ('plugins/ScriptedQuests/compass/common', '../../../../server_config/data/scriptedquests/compass/common'),
        ('plugins/ScriptedQuests/clickables/{servername}', '../../../../server_config/data/scriptedquests/clickables/{servername}'),
        ('plugins/ScriptedQuests/clickables/common', '../../../../server_config/data/scriptedquests/clickables/common'),
        ('plugins/ScriptedQuests/death/{servername}', '../../../../server_config/data/scriptedquests/death/{servername}'),
        ('plugins/ScriptedQuests/death/common', '../../../../server_config/data/scriptedquests/death/common'),
        ('plugins/ScriptedQuests/login/{servername}', '../../../../server_config/data/scriptedquests/login/{servername}'),
        ('plugins/ScriptedQuests/login/common', '../../../../server_config/data/scriptedquests/login/common'),
        ('plugins/ScriptedQuests/npcs/{servername}', '../../../../server_config/data/scriptedquests/npcs/{servername}'),
        ('plugins/ScriptedQuests/npcs/common', '../../../../server_config/data/scriptedquests/npcs/common'),
        ('plugins/ScriptedQuests/races/{servername}', '../../../../server_config/data/scriptedquests/races/{servername}'),
        ('plugins/ScriptedQuests/races/common', '../../../../server_config/data/scriptedquests/races/common'),
        ('plugins/ScriptedQuests/traders/{servername}', '../../../../server_config/data/scriptedquests/traders/{servername}'),
        ('plugins/ScriptedQuests/traders/common', '../../../../server_config/data/scriptedquests/traders/common'),
        ('plugins/ScriptedQuests/codes/{servername}', '../../../../server_config/data/scriptedquests/codes/{servername}'),
        ('plugins/ScriptedQuests/codes/common', '../../../../server_config/data/scriptedquests/codes/common'),
        ('plugins/ScriptedQuests/interactables/{servername}', '../../../../server_config/data/scriptedquests/interactables/{servername}'),
        ('plugins/ScriptedQuests/interactables/common', '../../../../server_config/data/scriptedquests/interactables/common'),
        ('plugins/ScriptedQuests/zone_layers/{servername}', '../../../../server_config/data/scriptedquests/zone_layers/{servername}'),
        ('plugins/ScriptedQuests/zone_layers/common', '../../../../server_config/data/scriptedquests/zone_layers/common'),
        ('plugins/ScriptedQuests/zone_properties/{servername}', '../../../../server_config/data/scriptedquests/zone_properties/{servername}'),
        ('plugins/ScriptedQuests/zone_properties/common', '../../../../server_config/data/scriptedquests/zone_properties/common'),
        ('plugins/EpicStructureManagement.jar', '../../server_config/plugins/EpicStructureManagement.jar'),
        ('plugins/EpicStructureManagement/structures', '../../../server_config/data/structures'),
        ('plugins/EpicStructureManagement/config.yml', '../../../server_config/data/plugins/{servername}/EpicStructureManagement/config.yml'),
        ('plugins/Monumenta/Properties.json', '../../../server_config/data/plugins/{servername}/Monumenta/Properties.json'),
        ('plugins/PremiumVanish.jar', '../../server_config/plugins/PremiumVanish.jar'),
        ('plugins/PremiumVanish/config.yml', '../../../server_config/data/plugins/all/PremiumVanish/config.yml'),
    ]
monumenta = monumenta_without_mobs_plugins + [
        ('plugins/Monumenta.jar', '../../server_config/plugins/Monumenta.jar'),
    ]

coreprotect = [
        ('plugins/CoreProtect.jar', '../../server_config/plugins/CoreProtect.jar'),
    ]

worldedit = [
        ('plugins/FastAsyncWorldEdit.jar', '../../server_config/plugins/FastAsyncWorldEdit.jar'),
        ('plugins/DummyFawe.jar', '../../server_config/plugins/DummyFawe.jar'),
        ('plugins/FastAsyncWorldEdit/commands', '../../../server_config/plugins/FastAsyncWorldEdit/commands'),
        ('plugins/FastAsyncWorldEdit/schematics', '/home/epic/4_SHARED/schematics'),
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

base_plugins = luckperms + monumenta + openinv + worldedit + coreprotect
if (SERVER_TYPE == 'build'):
    base_plugins += speedchanger + nbteditor + voxelsniper + gobrush
else:
    base_plugins += []

# String replacements:
# {servername} - server name
#('server.properties', 'motd', 'motd=Monumenta\: {servername} shard'),
#('plugins/Socket4MC/config.yml', 'name', 'name: "{servername}"'),
#('server.properties', 'level-name', 'level-name=Project_Epic-{servername}'),

template_dir = 'server_config/data/server_config_template'

config = {

    # Config: if three args, replace line in 1st arg file starting with 2nd arg with 3rd arg
    #         if two args, append line to file
    #         if one, just copy file unmodified

    # Change between play and beta:
    #   Difficulty
    #   Tab complete=9999 in spigot.yml

    'region_1':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=8'),
            ('spigot.yml', 'view-distance', '    view-distance: 8'),
        ],
        'linked':server_config + base_plugins + dynmap,
    },

    'region_2':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=8'),
            ('spigot.yml', 'view-distance', '    view-distance: 8'),
        ],
        'linked':server_config + base_plugins + dynmap,
    },

    'dungeon':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=12'),
            ('spigot.yml', 'view-distance', '    view-distance: 12'),
        ],
        'linked':server_config + base_plugins + dynmap + [
            ('plugins/ScriptedQuests/npcs/tutorial', '../../../../server_config/data/scriptedquests/npcs/tutorial'),
            ('plugins/ScriptedQuests/npcs/labs', '../../../../server_config/data/scriptedquests/npcs/labs'),
        ],
    },

    'update_do_not_use':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=8'),
            ('spigot.yml', 'view-distance', '    view-distance: 8'),
        ],
        'linked':server_config_min + luckperms_standalone + monumenta + worldedit + speedchanger + nbteditor + voxelsniper + coreprotect,
    },

    'pvp_do_not_use':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=8'),
            ('spigot.yml', 'view-distance', '    view-distance: 8'),
        ],
        'linked':server_config_min + luckperms_standalone + monumenta + worldedit + speedchanger + nbteditor + voxelsniper + coreprotect,
    },

    'build':{
        'config':server_config_to_copy + [
            ('server.properties', 'white-list', 'white-list=true'),
            ('server.properties', 'view-distance', 'view-distance=8'),
            ('spigot.yml', 'view-distance', '    view-distance: 8'),
            ('spigot.yml', 'tab-complete', '  tab-complete: 0'),
            ('server.properties', 'difficulty', 'difficulty=0'),
            ('server.properties', 'gamemode', 'gamemode=1'),
        ],
        'linked':server_config_min + luckperms_standalone + monumenta + worldedit + speedchanger + nbteditor + voxelsniper + dynmap + coreprotect + gobrush,
    },

    'mobs':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=6'),
            ('spigot.yml', 'view-distance', '    view-distance: 6'),
            ('server.properties', 'difficulty', 'difficulty=2'),
        ],
        'linked':server_config + luckperms + openinv + worldedit + nbteditor + dynmap + speedchanger + monumenta_without_mobs_plugins + coreprotect,
    },

    'plots':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=6'),
            ('spigot.yml', 'view-distance', '    view-distance: 6'),
        ],
        'linked':server_config + base_plugins + dynmap,
    },

    'betaplots':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=7'),
            ('spigot.yml', 'view-distance', '    view-distance: 7'),
            ('server.properties', 'difficulty', 'difficulty=0'),
        ],
        'linked':server_config + base_plugins,
    },

    'shiftingcity':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=15'),
            ('spigot.yml', 'view-distance', '    view-distance: 15'),
        ],
        'linked':server_config + base_plugins + [
            ('plugins/Roguelite', '../../server_config/data/Roguelite'),
            ('plugins/Roguelite.jar', '../../server_config/plugins/Roguelite.jar'),
        ],
    },

    'purgatory':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=4'),
            ('spigot.yml', 'view-distance', '    view-distance: 4'),
            ('server.properties', 'force-gamemode', 'force-gamemode=true'),
            ('server.properties', 'gamemode', 'gamemode=2'),
            ('server.properties', 'enable-command-block', 'enable-command-block=false'),
            ('server.properties', 'white-list', 'white-list=false'),
            ('server.properties', 'spawn-monsters', 'spawn-monsters=false'),
            ('server.properties', 'spawn-npcs', 'spawn-npcs=false'),
            ('server.properties', 'spawn-protection', 'spawn-protection=16'),
            ('paper.yml', 'keep-spawn-loaded', '    keep-spawn-loaded: true'),
        ],
        'linked':purgatory_min,
    },


}

simple_view_distance_config = {
    'white': 8,
    'orange': 12,
    'magenta': 12,
    'lightblue': 12,
    'yellow': 8,
    'lime': 9,
    'pink': 8,
    'gray': 8,
    'lightgray': 11,
    'cyan': 8,
    'purple': 10,

    'tutorial': 9,
    'labs': 9,
    'willows': 8,
    'roguelike': 8,
    'sanctum': 10,
    'reverie': 10,
    'test': 8,
}

for key in simple_view_distance_config:
    distance = simple_view_distance_config[key]
    config[key] = {
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance={}'.format(distance)),
            ('spigot.yml', 'view-distance', '    view-distance: {}'.format(distance)),
        ],
        'linked':server_config + base_plugins,
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
else:
    config = add_config_if_not_set(config, ('server.properties', 'difficulty', 'difficulty=2'))
    config = add_config_if_not_set(config, ('spigot.yml', 'tab-complete', '  tab-complete: 9999'))
    config = add_config_if_not_set(config, ('server.properties', 'white-list', 'white-list=false'))
    config = add_config_if_not_set(config, ('plugins/ScriptedQuests/config.yml', 'show_timer_names', 'show_timer_names: false'))

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

        if not os.path.isdir(os.path.dirname(new)):
            os.makedirs(os.path.dirname(new), mode=0o775)

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

        if not os.path.isdir(os.path.dirname(linkname)):
            os.makedirs(os.path.dirname(linkname), mode=0o775)

        os.symlink(targetname, linkname)

    print("Success - " + servername)

for servername in server_list:
    gen_server_config(servername)

