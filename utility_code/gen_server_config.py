#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import shutil
import re

# TODO: Need to find a way to link some things, copy others by groups.
# Many things don't need coreprotect config or nbteditor config...

server_config_to_copy = [
        ('eula.txt',),
        ('bukkit.yml',),
        ('commands.yml',),
        ('help.yml',),
        ('permissions.yml',),
        ('spigot.yml',),
        ('wepif.yml',),
        ('mark2-scripts.txt',),
        ('plugins/NBTEditor/CustomItems/NBTEditor.yml',),
        ('plugins/CoreProtect/config.yml',),
        ('plugins/Monumenta-Plugins/config.yml',),
        ('plugins/Monumenta-Plugins/Properties.json',),
    ]

server_config = [
        ('spigot.jar', '../server_config/spigot.jar'),
        ('Project_Epic-WORLDOOG/data/functions', '../../../server_config/data/functions'),
        ('Project_Epic-WORLDOOG/data/loot_tables', '../../../server_config/data/loot_tables'),
        ('Project_Epic-WORLDOOG_the_end/data/functions', '../../../server_config/data/functions'),
        ('Project_Epic-WORLDOOG_the_end/data/loot_tables', '../../../server_config/data/loot_tables'),
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

# F3 + n switch creative/spectator for non-ops
f3n = [
        ('plugins/F3NPerm.jar', '../../server_config/plugins/F3NPerm.jar'),
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

luckperms = [
        ('plugins/LuckPerms.jar', '../../server_config/plugins/LuckPerms.jar'),
        ('plugins/LuckPerms/config.yml', '../../../server_config/plugins/LuckPerms/config.yml'),
        ('plugins/LuckPerms/yaml-storage/groups', '../../../../server_config/plugins/LuckPerms/yaml-storage/groups'),
        ('plugins/LuckPerms/yaml-storage/tracks', '../../../../server_config/plugins/LuckPerms/yaml-storage/tracks'),
        ('plugins/LuckPerms/yaml-storage/users', '../../../../server_config/plugins/LuckPerms/yaml-storage/users'),
    ]

monumenta = [
        ('plugins/Monumenta-Plugins.jar', '../../server_config/plugins/Monumenta-Plugins.jar'),
    ]

nbteditor = [
        ('plugins/nbteditor.jar', '../../server_config/plugins/nbteditor.jar'),
        ('plugins/NBTEditor/config.yml', '../../../server_config/plugins/NBTEditor/config.yml'),
    ]

openinv = [
        ('plugins/OpenInv.jar', '../../server_config/plugins/OpenInv.jar'),
        ('plugins/OpenInv/config.yml', '../../../server_config/plugins/OpenInv/config.yml'),
    ]

socket4mc = [
        ('plugins/socket4mc.jar', '../../server_config/plugins/socket4mc.jar'),
    ]

speedchanger = [
        ('plugins/SpeedChanger.jar', '../../server_config/plugins/SpeedChanger.jar'),
    ]

voxelsniper = [
        ('plugins/VoxelSniper.jar', '../../server_config/plugins/VoxelSniper.jar'),
        ('plugins/VoxelSniper/config.yml', '../../../server_config/plugins/VoxelSniper/config.yml'),
    ]

# Index of nodes:
#   server_config
#   advancements_disabled
#   advancements_r1
#   structures
#
# base_plugins:
#   easywarp
#   f3n
#   luckperms
#   monumenta
#   openinv
#   socket4mc
#
# build_plugins:
#   speedchanger
#   worldedit
#   nbteditor
#   voxelsniper

base_plugins = easywarp + f3n + luckperms + monumenta + openinv + socket4mc
build_plugins = worldedit + speedchanger + nbteditor + voxelsniper
# build_plugins = []

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
    #   Difficulty
    #   Backups invoked from mark2-scripts.txt
    #   Tab complete=4 in spigot.yml

    'region_1':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=8'),
            ('server.properties', 'server-port', 'server-port=25566'),
            ('plugins/Socket4MC/config.yml', 'host', 'host: "127.0.0.2"'),
            ('mark2-scripts.txt', '     0    3    *    *    *    /setblock -1449 1 -1440 redstone_block'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=768M'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=768M'),
            #('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=3G'),
            #('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=3G'),
            ('plugins/Monumenta-Plugins/Properties.json', '"dailyResetEnabled":', '"dailyResetEnabled": true,'),
            ('plugins/Monumenta-Plugins/Properties.json', '"plotSurvivalMinHeight":', '"plotSurvivalMinHeight": 95,'),
        ],
        'linked':server_config + advancements_r1 + base_plugins + coreprotect + build_plugins,
    },

    'region_2':{
        'config':server_config_to_copy + [
            ('server.properties', 'server-port', 'server-port=25568'),
            ('plugins/Socket4MC/config.yml', 'host', 'host: "127.0.0.3"'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=768M'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=768M'),
        ],
        'linked':server_config + advancements_disabled + base_plugins + coreprotect + build_plugins,
    },

    'tutorial':{
        'config':server_config_to_copy + [
            ('server.properties', 'server-port', 'server-port=25567'),
            ('plugins/Socket4MC/config.yml', 'host', 'host: "127.0.0.7"'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=512M'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=512M'),
            ('plugins/Monumenta-Plugins/Properties.json', '"transferDataEnabled":', '"transferDataEnabled": false,'),
        ],
        'linked':server_config + advancements_disabled + base_plugins,
    },

    'dungeon':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=12'),
            ('server.properties', 'server-port', 'server-port=25572'),
            ('plugins/Socket4MC/config.yml', 'host', 'host: "127.0.0.6"'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=768M'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=768M'),
        ],
        'linked':server_config + advancements_disabled + base_plugins + coreprotect + build_plugins,
    },

    'roguelike':{
        'config':server_config_to_copy + [
            ('server.properties', 'server-port', 'server-port=25569'),
            ('plugins/Socket4MC/config.yml', 'host', 'host: "127.0.0.4"'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=768M'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=768M'),
        ],
        'linked':server_config + advancements_disabled + base_plugins + coreprotect + build_plugins,
    },

    'test':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=8'),
            ('server.properties', 'server-port', 'server-port=25571'),
            ('plugins/Socket4MC/config.yml', 'host', 'host: "127.0.0.5"'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=768M'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=768M'),
        ],
        'linked':server_config + advancements_r1 + base_plugins + build_plugins,
    },

    'r1plots':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=7'),
            ('server.properties', 'server-port', 'server-port=25573'),
            ('server.properties', 'difficulty', 'difficulty=0'),
            ('plugins/Socket4MC/config.yml', 'host', 'host: "127.0.0.8"'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=768M'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=768M'),
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
            ('server.properties', 'server-port', 'server-port=25574'),
            ('server.properties', 'difficulty', 'difficulty=0'),
            ('plugins/Socket4MC/config.yml', 'host', 'host: "127.0.0.9"'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=3G'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=3G'),
            ('plugins/Monumenta-Plugins/Properties.json', '"isTownWorld":', '"isTownWorld": true,'),
            ('plugins/Monumenta-Plugins/Properties.json', '"plotSurvivalMinHeight":', '"plotSurvivalMinHeight": 95,'),
        ],
        'linked':server_config + advancements_disabled + base_plugins + coreprotect + build_plugins,
    },

    'purgatory':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=4'),
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
            ('server.properties', 'server-port', 'server-port=25580'),
            ('plugins/Socket4MC/config.yml', 'host', 'host: "127.0.0.10"'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=2G'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=2G'),
        ],
        'linked':server_config + advancements_disabled + base_plugins,
    },

    'orange':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=12'),
            ('server.properties', 'server-port', 'server-port=25581'),
            ('plugins/Socket4MC/config.yml', 'host', 'host: "127.0.0.11"'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=2G'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=2G'),
        ],
        'linked':server_config + advancements_disabled + base_plugins,
    },

    'magenta':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=12'),
            ('server.properties', 'server-port', 'server-port=25582'),
            ('plugins/Socket4MC/config.yml', 'host', 'host: "127.0.0.12"'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=2G'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=2G'),
        ],
        'linked':server_config + advancements_disabled + base_plugins,
    },

    'lightblue':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=12'),
            ('server.properties', 'server-port', 'server-port=25583'),
            ('plugins/Socket4MC/config.yml', 'host', 'host: "127.0.0.13"'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=2G'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=2G'),
        ],
        'linked':server_config + advancements_disabled + base_plugins,
    },

    'yellow':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=8'),
            ('server.properties', 'server-port', 'server-port=25584'),
            ('plugins/Socket4MC/config.yml', 'host', 'host: "127.0.0.14"'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=3G'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=3G'),
        ],
        'linked':server_config + advancements_disabled + base_plugins,
    },

    'r1bonus':{
        'config':server_config_to_copy + [
            ('server.properties', 'view-distance', 'view-distance=8'),
            ('server.properties', 'server-port', 'server-port=25600'),
            ('plugins/Socket4MC/config.yml', 'host', 'host: "127.0.0.30"'),
            ('mark2.properties', 'java.cli.X.ms', 'java.cli.X.ms=2G'),
            ('mark2.properties', 'java.cli.X.mx', 'java.cli.X.mx=2G'),
        ],
        'linked':server_config + advancements_disabled + base_plugins,
    },
}

if (len(sys.argv) != 2 or (not(sys.argv[1] in config))):
    sys.exit("Usage: " + sys.argv[0] + " <minecraft_directory>")

servername = sys.argv[1]
dest = config[servername]
config = dest["config"]

################################################################################
# Copy customized configuration per-server
################################################################################

# Get a unique list of files to copy
files = [i[0] for i in config]
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
for replacement in config:
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

print "Success"


