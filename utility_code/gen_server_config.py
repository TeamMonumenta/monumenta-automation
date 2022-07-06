#!/usr/bin/env python3

import sys
import os
import re
import copy

from pathlib import Path

def get_alt_version(alt_version, original_path, relative_to=Path('.')):
    """Returns alternate versions of a path, or the original if not found.

    Example transformations:
    get_alt_version(None, 'anything') -> Path('anything')
    get_alt_version('1.18', 'foo') -> Path('foo-1.18')
    get_alt_version('1.18', 'foo.bar') -> Path('foo-1.18.bar')
    get_alt_version('1.18', 'foo.bar.baz') -> Path('foo-1.18.bar.baz')

    Assuming there is a 'baz-1.18' in the current working directory:
    get_alt_version('1.18', '../../baz', 'foo/bar') -> Path('../../baz-1.18')
    """
    relative_to = Path(relative_to)
    original_path = Path(original_path)

    if alt_version is None:
        return original_path

    parts = original_path.name.split('.', maxsplit=1)
    parts[0] = parts[0] + f'-{alt_version}'
    alt_name = f'.'.join(parts)

    test_path = original_path.parent / alt_name
    if not test_path.is_absolute():
        test_path = relative_to / test_path
    if test_path.exists():
        return original_path.parent / alt_name

    return original_path

# config should be the entire config map
# data should be a tuple like ('server.properties', 'difficulty', 'difficulty=peaceful')
def add_config_if_not_set(config, data):
    for key in config:
        exists = False
        for replacement in config[key]['config']:
            if len(replacement) == 3 and data[0] in replacement[0] and data[1] in replacement[1]:
                exists = True
        if not exists:
            config[key]['config'] += [data]

    return config

def get_server_domain(servername):
    if servername == 'purgatory':
        return 'purgatory'
    if servername == 'build':
        return 'playerbuild'
    if servername == 'build2':
        return 'build2'
    if servername == 'tutorial':
        return 'tutorial'
    return SERVER_TYPE


def gen_server_config(servername):
    if servername not in config:
        print("ERROR: No config available for " + repr(servername))
        return

    dest = config[servername]
    serverConfig = dest["config"]

    # If this was a copy of another shard, get the other shard name to be used for {servername} replacements
    is_copy = "copy_of" in dest
    serverNameForReplacements = dest.get("copy_of", servername)
    server_domain = get_server_domain(serverNameForReplacements)

    alt_version = dest.get("alt_version", None)
    if server_domain == 'build' and alt_version is not None:
        server_domain = f'{server_domain}-{alt_version.replace(".", "")}'

    ################################################################################
    # Copy customized configuration per-server
    ################################################################################

    # Get a unique list of files to copy
    files = [i[0] for i in serverConfig]
    files = list(set(files))

    # Copy those files and replace {servername} and {serverdomain} with the appropriate string
    for filename in files:
        old = template_dir + "/" + filename
        new = servername + "/" + filename
        if os.path.islink(new):
            print("Warning - file " + repr(new) + " is link; not replacing it")
            continue

        if not os.path.isdir(os.path.dirname(new)):
            os.makedirs(os.path.dirname(new), mode=0o775)

        old = get_alt_version(alt_version, old)

        try:
            with open(old, "rt") as fin:
                with open(new, "wt") as fout:
                    for line in fin:
                        fout.write(line.replace("{servername}", serverNameForReplacements).replace("{serverdomain}", server_domain))
        except Exception as e:
            print(e)
            continue

    # Do the per-file replacements
    for replacement in serverConfig:
        filename = servername + "/" + replacement[0]
        filename = filename.replace("{servername}", serverNameForReplacements).replace("{serverdomain}", server_domain)
        if len(replacement) == 1:
            # Nothing to do here, just copying the file was enough
            continue

        if len(replacement) == 2:
            # Need to append the second argument to the file
            with open(filename, "a") as fout:
                fout.write(replacement[1] + "\n")
                fout.close()
        elif len(replacement) == 3:
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
        if os.path.islink(filename):
            os.unlink(filename)

    ################################################################################
    # Create symlinks
    ################################################################################

    linked = dest["linked"]
    for link in linked:
        linkname = servername + "/" + link[0]
        targetname = link[1]
        linkname = linkname.replace("{servername}", serverNameForReplacements).replace("{serverdomain}", server_domain)
        targetname = targetname.replace("{servername}", serverNameForReplacements).replace("{serverdomain}", server_domain)

        if os.path.islink(linkname):
            os.unlink(linkname)
        if os.path.isfile(linkname):
            print("Warning - file that should be link detected. Please remove this file:")
            print("  rm -f " + linkname)
            continue
        if os.path.isdir(linkname):
            print("Warning - directory that should be link detected. Please remove this directory:")
            print("  rm -rf " + linkname)
            continue

        if not os.path.isdir(os.path.dirname(linkname)):
            os.makedirs(os.path.dirname(linkname), mode=0o775)

        os.symlink(targetname, linkname)

    print("Success - " + servername)

if __name__ == '__main__':
    SERVER_TYPE = 'build'

    # Main entry point
    if len(sys.argv) < 2:
        sys.exit("Usage: " + sys.argv[0] + " [--play] <minecraft_directory> [dir2] ...")

    server_list = []
    for arg in sys.argv[1:]:
        if arg == "--play":
            SERVER_TYPE = 'play'
        else:
            server_list += [arg,]

    if len(server_list) < 1:
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
        ('plugins/BKCommonLib/config.yml',),
        ('plugins/CoreProtect/config.yml',),
        ('plugins/FastAsyncWorldEdit/config.yml',),
        ('plugins/FastAsyncWorldEdit/config-legacy.yml', "wand-item:", "wand-item: {}".format("minecraft:diamond_axe" if SERVER_TYPE == 'build' else "minecraft:knowledge_book")),
        ('plugins/FastAsyncWorldEdit/worldedit-config.yml', "wand-item:", "wand-item: {}".format("minecraft:diamond_axe" if SERVER_TYPE == 'build' else "minecraft:knowledge_book")),
        ('plugins/FastAsyncVoxelSniper/config.yml',),
        ('plugins/NBTEditor/config.yml',),
        ('plugins/LightCleaner/config.yml',),
        ('plugins/ScriptedQuests/config.yml', 'show_timer_names', 'show_timer_names: {}'.format(SERVER_TYPE == 'build')),
        ('plugins/ScriptedQuests/config.yml', 'show_zones_dynmap', 'show_zones_dynmap: {}'.format(SERVER_TYPE == 'build')),
        ('plugins/PrometheusExporter/config.yml',),
        ('plugins/OpenInv/config.yml',),
        ('plugins/ProtocolLib/config.yml',),
        ('plugins/Vault/config.yml',),
        ('plugins/ChestSort/config.yml',),
        ('plugins/dynmap/custom-lightings.txt',),
        ('plugins/MonumentaRedisSync/config.yml',),
        ('plugins/MonumentaNetworkRelay/config.yml',),
        ('plugins/HolographicDisplays/config.yml',),
        ('plugins/HolographicDisplays/symbols.yml',),
    ]

    server_config_to_copy_1_18 = [
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
        ('plugins/BKCommonLib/config.yml',),
        ('plugins/CoreProtect/config.yml',),
        ('plugins/FastAsyncWorldEdit/config.yml',),
        ('plugins/FastAsyncWorldEdit/config-legacy.yml', "wand-item:", "wand-item: {}".format("minecraft:diamond_axe" if SERVER_TYPE == 'build' else "minecraft:knowledge_book")),
        ('plugins/FastAsyncWorldEdit/worldedit-config.yml', "wand-item:", "wand-item: {}".format("minecraft:diamond_axe" if SERVER_TYPE == 'build' else "minecraft:knowledge_book")),
        ('plugins/FastAsyncVoxelSniper/config.yml',),
        ('plugins/NBTEditor/config.yml',),
        ('plugins/LightCleaner/config.yml',),
        ('plugins/ScriptedQuests/config.yml', 'show_timer_names', 'show_timer_names: {}'.format(SERVER_TYPE == 'build')),
        ('plugins/ScriptedQuests/config.yml', 'show_zones_dynmap', 'show_zones_dynmap: {}'.format(SERVER_TYPE == 'build')),
        ('plugins/PrometheusExporter/config.yml',),
        ('plugins/ProtocolLib/config.yml',),
        ('plugins/Vault/config.yml',),
        ('plugins/ChestSort/config.yml',),
        ('plugins/MonumentaRedisSync/config.yml',),
        ('plugins/MonumentaNetworkRelay/config.yml',),
    ]

    purgatory_min = [
        ('paperclip.jar', '../server_config/paperclip.jar'),
        ('plugins/Vault.jar', '../../server_config/plugins/Vault.jar'),
        ('plugins/ProtocolLib.jar', '../../server_config/plugins/ProtocolLib.jar'),
        ('plugins/PlaceholderAPI.jar', '../../server_config/plugins/PlaceholderAPI.jar'),
        ('plugins/CommandAPI.jar', '../../server_config/plugins/CommandAPI.jar'),
        ('plugins/RedisSync.jar', '../../server_config/plugins/MonumentaRedisSync.jar'),
    ]

    purgatory_min_1_18 = [
        ('paperclip.jar', '../server_config/paperclip-1.18.jar'),
        ('plugins/Vault.jar', '../../server_config/plugins/Vault.jar'),
        ('plugins/ProtocolLib.jar', '../../server_config/plugins/ProtocolLib.jar'),
        ('plugins/PlaceholderAPI.jar', '../../server_config/plugins/PlaceholderAPI.jar'),
        ('plugins/CommandAPI.jar', '../../server_config/plugins/CommandAPI-1.18.jar'),
        ('plugins/RedisSync.jar', '../../server_config/plugins/MonumentaRedisSync.jar'),
    ]

    server_config_min = purgatory_min + [
        ('plugins/PlaceholderAPI', '../../server_config/plugins/PlaceholderAPI'),
        ('plugins/BungeeTabListPlus_BukkitBridge.jar', '../../server_config/plugins/BungeeTabListPlus_BukkitBridge.jar'),
        ('plugins/BKCommonLib.jar', '../../server_config/plugins/BKCommonLib.jar'),
        ('plugins/LightCleaner.jar', '../../server_config/plugins/LightCleaner.jar'),
    ]

    server_config_min_1_18 = purgatory_min_1_18 + [
        ('plugins/PlaceholderAPI', '../../server_config/plugins/PlaceholderAPI'),
        ('plugins/BungeeTabListPlus_BukkitBridge.jar', '../../server_config/plugins/BungeeTabListPlus_BukkitBridge.jar'),
        ('plugins/BKCommonLib.jar', '../../server_config/plugins/BKCommonLib.jar'),
        ('plugins/LightCleaner.jar', '../../server_config/plugins/LightCleaner.jar'),
    ]

    server_config = server_config_min + [
        ('Project_Epic-{servername}/generated', '../../server_config/data/generated'),
        ('Project_Epic-{servername}/datapacks', '../../server_config/data/datapacks'),
    ]

    server_config_1_18 = server_config_min_1_18 + [
        ('Project_Epic-{servername}/generated', '../../server_config/data/generated'),
        ('Project_Epic-{servername}/datapacks', '../../server_config/data/datapacks_1_18'),
    ]

    network_chat = [
        ('plugins/NetworkChat.jar', '../../server_config/plugins/NetworkChat.jar'),
        ('plugins/MonumentaNetworkChat/config.yml', '../../../server_config/data/plugins/all/MonumentaNetworkChat/config.yml'),
        ('plugins/MonumentaNetworkChat/help', '../../../server_config/data/plugins/all/MonumentaNetworkChat/help'),
    ]

    monumenta = [
        ('plugins/NetworkRelay.jar', '../../server_config/plugins/MonumentaNetworkRelay.jar'),
        ('plugins/WorldManagement.jar', '../../server_config/plugins/MonumentaWorldManagement.jar'),
        ('plugins/MonumentaWorldManagement/config.yml', '../../../server_config/data/plugins/{servername}/MonumentaWorldManagement/config.yml'),
        ('plugins/Monumenta.jar', '../../server_config/plugins/Monumenta.jar'),
        ('plugins/Monumenta/experiencinator_config.json', '../../../server_config/data/plugins/all/Monumenta/experiencinator_config.json'),
        ('plugins/Monumenta/ItemIndex', '../../../server_config/data/plugins/all/ItemIndex'),
        ('plugins/Monumenta/seasonalevents', '../../../server_config/data/plugins/all/Monumenta/seasonalevents'),
        ('plugins/Monumenta/InfinityTower/TowerMobs.json', '../../../../server_config/data/plugins/valley/Monumenta/InfinityTower/TowerMobs.json'),
        ('plugins/Monumenta/InfinityTower/InfinityTowerDefault.json', '../../../../server_config/data/plugins/valley/Monumenta/InfinityTower/InfinityTowerDefault.json'),
        ('plugins/Monumenta/CommonProperties.json', '../../../server_config/data/plugins/all/Monumenta/CommonProperties.json'),
        ('plugins/Monumenta/Properties.json', '../../../server_config/data/plugins/{servername}/Monumenta/Properties.json'),
        ('plugins/Warps.jar', '../../server_config/plugins/MonumentaWarps.jar'),
        ('plugins/ChestSort.jar', '../../server_config/plugins/ChestSort.jar'),
        ('plugins/ChestSort/categories', '../../../server_config/data/plugins/all/ChestSort/categories'),
        ('plugins/nbt-api.jar', '../../server_config/plugins/nbt-api.jar'),
        ('plugins/HolographicDisplays.jar', '../../server_config/plugins/HolographicDisplays.jar'),
        ('plugins/HolographicDisplays/database.yml', '../../../server_config/data/plugins/{servername}/HolographicDisplays/database.yml'),
        ('plugins/spark.jar', '../../server_config/plugins/spark.jar'),
        ('plugins/spark', '/home/epic/5_SCRATCH/spark'),
        ('plugins/prometheus-exporter.jar', '../../server_config/plugins/prometheus-exporter.jar'),
        ('plugins/ScriptedQuests.jar', '../../server_config/plugins/ScriptedQuests.jar'),
        ('plugins/ScriptedQuests/translations', f'/home/epic/4_SHARED/translations/{SERVER_TYPE}'),
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
        ('plugins/ScriptedQuests/growables/{servername}', '../../../../server_config/data/scriptedquests/growables/{servername}'),
        ('plugins/ScriptedQuests/growables/common', '../../../../server_config/data/scriptedquests/growables/common'),
        ('plugins/ScriptedQuests/guis/{servername}', '../../../../server_config/data/scriptedquests/guis/{servername}'),
        ('plugins/ScriptedQuests/guis/common', '../../../../server_config/data/scriptedquests/guis/common'),
        ('plugins/ScriptedQuests/traders/{servername}', '../../../../server_config/data/scriptedquests/traders/{servername}'),
        ('plugins/ScriptedQuests/traders/common', '../../../../server_config/data/scriptedquests/traders/common'),
        ('plugins/ScriptedQuests/codes/{servername}', '../../../../server_config/data/scriptedquests/codes/{servername}'),
        ('plugins/ScriptedQuests/codes/common', '../../../../server_config/data/scriptedquests/codes/common'),
        ('plugins/ScriptedQuests/interactables/{servername}', '../../../../server_config/data/scriptedquests/interactables/{servername}'),
        ('plugins/ScriptedQuests/interactables/common', '../../../../server_config/data/scriptedquests/interactables/common'),
        ('plugins/ScriptedQuests/zone_layers/{servername}', '../../../../server_config/data/scriptedquests/zone_layers/{servername}'),
        ('plugins/ScriptedQuests/zone_properties/common', '../../../../server_config/data/scriptedquests/zone_properties/common'),
        ('plugins/ScriptedQuests/zone_properties/{servername}', '../../../../server_config/data/scriptedquests/zone_properties/{servername}'),
        ('plugins/StructureManagement.jar', '../../server_config/plugins/MonumentaStructureManagement.jar'),
        ('plugins/MonumentaStructureManagement/structures', '../../../server_config/data/structures'),
        ('plugins/MonumentaStructureManagement/config.yml', '../../../server_config/data/plugins/{servername}/MonumentaStructureManagement/config.yml'),
    ]

    monumenta_1_18 = [
        ('plugins/NetworkRelay.jar', '../../server_config/plugins/MonumentaNetworkRelay.jar'),
        ('plugins/WorldManagement.jar', '../../server_config/plugins/MonumentaWorldManagement.jar'),
        ('plugins/MonumentaWorldManagement/config.yml', '../../../server_config/data/plugins/{servername}/MonumentaWorldManagement/config.yml'),
        ('plugins/Monumenta-1.18.jar', '../../server_config/plugins/Monumenta-1.18.jar'),
        ('plugins/Monumenta/experiencinator_config.json', '../../../server_config/data/plugins/all/Monumenta/experiencinator_config.json'),
        ('plugins/Monumenta/ItemIndex', '../../../server_config/data/plugins/all/ItemIndex'),
        ('plugins/Monumenta/seasonalevents', '../../../server_config/data/plugins/all/Monumenta/seasonalevents'),
        ('plugins/Monumenta/InfinityTower/TowerMobs.json', '../../../../server_config/data/plugins/valley/Monumenta/InfinityTower/TowerMobs.json'),
        ('plugins/Monumenta/InfinityTower/InfinityTowerDefault.json', '../../../../server_config/data/plugins/valley/Monumenta/InfinityTower/InfinityTowerDefault.json'),
        ('plugins/Monumenta/CommonProperties.json', '../../../server_config/data/plugins/all/Monumenta/CommonProperties.json'),
        ('plugins/Monumenta/Properties.json', '../../../server_config/data/plugins/{servername}/Monumenta/Properties.json'),
        ('plugins/Warps.jar', '../../server_config/plugins/MonumentaWarps.jar'),
        #('plugins/ChestSort.jar', '../../server_config/plugins/ChestSort.jar'),
        #('plugins/ChestSort/categories', '../../../server_config/data/plugins/all/ChestSort/categories'),
        ('plugins/nbt-api.jar', '../../server_config/plugins/nbt-api.jar'),
        #('plugins/HolographicDisplays.jar', '../../server_config/plugins/HolographicDisplays.jar'),
        #('plugins/HolographicDisplays/database.yml', '../../../server_config/data/plugins/{servername}/HolographicDisplays/database.yml'),
        ('plugins/spark.jar', '../../server_config/plugins/spark.jar'),
        ('plugins/spark', '/home/epic/5_SCRATCH/spark'),
        ('plugins/prometheus-exporter.jar', '../../server_config/plugins/prometheus-exporter.jar'),
        ('plugins/ScriptedQuests.jar', '../../server_config/plugins/ScriptedQuests.jar'),
        ('plugins/ScriptedQuests/translations', f'/home/epic/4_SHARED/translations/{SERVER_TYPE}'),
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
        ('plugins/ScriptedQuests/growables/{servername}', '../../../../server_config/data/scriptedquests/growables/{servername}'),
        ('plugins/ScriptedQuests/growables/common', '../../../../server_config/data/scriptedquests/growables/common'),
        ('plugins/ScriptedQuests/guis/{servername}', '../../../../server_config/data/scriptedquests/guis/{servername}'),
        ('plugins/ScriptedQuests/guis/common', '../../../../server_config/data/scriptedquests/guis/common'),
        ('plugins/ScriptedQuests/traders/{servername}', '../../../../server_config/data/scriptedquests/traders/{servername}'),
        ('plugins/ScriptedQuests/traders/common', '../../../../server_config/data/scriptedquests/traders/common'),
        ('plugins/ScriptedQuests/codes/{servername}', '../../../../server_config/data/scriptedquests/codes/{servername}'),
        ('plugins/ScriptedQuests/codes/common', '../../../../server_config/data/scriptedquests/codes/common'),
        ('plugins/ScriptedQuests/interactables/{servername}', '../../../../server_config/data/scriptedquests/interactables/{servername}'),
        ('plugins/ScriptedQuests/interactables/common', '../../../../server_config/data/scriptedquests/interactables/common'),
        ('plugins/ScriptedQuests/zone_layers/{servername}', '../../../../server_config/data/scriptedquests/zone_layers/{servername}'),
        ('plugins/ScriptedQuests/zone_properties/common', '../../../../server_config/data/scriptedquests/zone_properties/common'),
        ('plugins/ScriptedQuests/zone_properties/{servername}', '../../../../server_config/data/scriptedquests/zone_properties/{servername}'),
        #('plugins/StructureManagement.jar', '../../server_config/plugins/MonumentaStructureManagement.jar'),
        #('plugins/MonumentaStructureManagement/structures', '../../../server_config/data/structures'),
        #('plugins/MonumentaStructureManagement/config.yml', '../../../server_config/data/plugins/{servername}/MonumentaStructureManagement/config.yml'),
    ]

    vanish = [
        ('plugins/PremiumVanish.jar', '../../server_config/plugins/PremiumVanish.jar'),
        ('plugins/PremiumVanish/config.yml', '../../../server_config/data/plugins/all/PremiumVanish/config.yml'),
    ]

    coreprotect = [
        ('plugins/CoreProtect.jar', '../../server_config/plugins/CoreProtect.jar'),
    ]

    coreprotect_1_18 = [
        ('plugins/CoreProtect.jar', '../../server_config/plugins/CoreProtect-1.18.jar'),
    ]

    worldedit = [
        ('plugins/FastAsyncWorldEdit.jar', '../../server_config/plugins/FastAsyncWorldEdit.jar'),
        ('plugins/FastAsyncWorldEdit/schematics', '/home/epic/4_SHARED/schematics'),
    ]

    worldedit_1_18 = [
        ('plugins/FastAsyncWorldEdit.jar', '../../server_config/plugins/FastAsyncWorldEdit-1.18.jar'),
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
        ('plugins/LibraryOfSouls.jar', '../../server_config/plugins/LibraryOfSouls.jar'),
        ('plugins/LibraryOfSouls/souls_database.json', '../../../server_config/data/plugins/all/LibraryOfSouls/souls_database.json'),
        ('plugins/LibraryOfSouls/soul_parties_database.json', '../../../server_config/data/plugins/all/LibraryOfSouls/soul_parties_database.json'),
        ('plugins/LibraryOfSouls/soul_pools_database.json', '../../../server_config/data/plugins/all/LibraryOfSouls/soul_pools_database.json'),
        ('plugins/LibraryOfSouls/bestiary_config.yml', '../../../server_config/data/plugins/all/LibraryOfSouls/bestiary_config.yml'),
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

    voxelsniper_1_18 = [
        ('plugins/FastAsyncVoxelSniper.jar', '../../server_config/plugins/FastAsyncVoxelSniper-1.18.jar'),
    ]

    # Analytics plugin - only for the play server!
    plan = [
        ('plugins/Plan.jar', '../../server_config/plugins/Plan.jar'),
        ('plugins/Plan', '../../server_config/data/plugins/{servername}/Plan'),
    ]

    gobrush = [
        ('plugins/Arceon.jar', '../../server_config/plugins/Arceon.jar'),
        ('plugins/Arceon', '../../server_config/plugins/Arceon'),
        ('plugins/goBrush.jar', '../../server_config/plugins/goBrush.jar'),
        ('plugins/goBrush', '../../server_config/data/plugins/all/goBrush'),
        ('plugins/goPaint.jar', '../../server_config/plugins/goPaint.jar'),
        ('plugins/goPaint', '../../server_config/data/plugins/all/goPaint'),
        ('plugins/HeadDatabase.jar', '../../server_config/plugins/HeadDatabase.jar'),
        ('plugins/HeadDatabase', '../../server_config/data/plugins/all/HeadDatabase'),
    ]

    gobrush_1_18 = [
        ('plugins/Arceon.jar', '../../server_config/plugins/Arceon-1.18.jar'),
        ('plugins/Arceon', '../../server_config/plugins/Arceon'),
        ('plugins/goBrush.jar', '../../server_config/plugins/goBrush-1.18.jar'),
        ('plugins/goBrush', '../../server_config/data/plugins/all/goBrush'),
        ('plugins/goPaint.jar', '../../server_config/plugins/goPaint-1.18.jar'),
        ('plugins/goPaint', '../../server_config/data/plugins/all/goPaint'),
        ('plugins/HeadDatabase.jar', '../../server_config/plugins/HeadDatabase.jar'),
        ('plugins/HeadDatabase', '../../server_config/data/plugins/all/HeadDatabase'),
    ]

    # Index of nodes:
    #   server_config
    #   structures

    base_plugins = luckperms + monumenta + openinv + worldedit + coreprotect + nbteditor + network_chat
    base_plugins_1_18 = luckperms + monumenta_1_18 + worldedit_1_18 + coreprotect_1_18 + nbteditor + network_chat
    if SERVER_TYPE == 'build':
        base_plugins += speedchanger + voxelsniper + gobrush
        base_plugins_1_18 += speedchanger + voxelsniper_1_18 + gobrush_1_18
    else:
        base_plugins += vanish

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

        'valley':{
            'config':server_config_to_copy + [
                ('server.properties', 'view-distance', 'view-distance=8'),
                ('spigot.yml', 'view-distance', '    view-distance: 8'),
            ],
            'linked':server_config + base_plugins + dynmap + [
                ('plugins/Monumenta/InfinityTower/InfinityFloors.json', '../../../../server_config/data/plugins/valley/Monumenta/InfinityTower/InfinityFloors.json'),
                ('plugins/Monumenta/bounties', '../../../server_config/data/plugins/valley/Monumenta/bounties'),
            ],
        },

        'isles':{
            'config':server_config_to_copy + [
                ('server.properties', 'view-distance', 'view-distance=8'),
                ('spigot.yml', 'view-distance', '    view-distance: 8'),
                ('spigot.yml', '      villagers:', '      villagers: 25'),
            ],
            'linked':server_config + base_plugins + dynmap + [
                ('plugins/Roguelite', '../../server_config/data/Roguelite'),
                ('plugins/Roguelite.jar', '../../server_config/plugins/Roguelite.jar'),
                ('plugins/Monumenta/bounties', '../../../server_config/data/plugins/isles/Monumenta/bounties'),
            ],
        },

        'ring':{
            'alt_version': '1.18',
            'config':server_config_to_copy_1_18 + [
                ('server.properties', 'view-distance', 'view-distance=8'),
                ('spigot.yml', 'view-distance', '    view-distance: 8'),
                ('spigot.yml', '      villagers:', '      villagers: 25'),
            ],
            'linked':server_config_1_18 + base_plugins_1_18 + [
                ('plugins/Monumenta/bounties', '../../../server_config/data/plugins/ring/Monumenta/bounties'),
            ],
        },

        'futurama':{
            'alt_version': '1.18',
            'config':server_config_to_copy_1_18 + [
                ('server.properties', 'view-distance', 'view-distance=8'),
                ('spigot.yml', 'view-distance', '    view-distance: 8'),
                ('spigot.yml', '      villagers:', '      villagers: 25'),
            ],
            'linked':server_config_1_18 + base_plugins_1_18 + [
                ('plugins/Monumenta/bounties', '../../../server_config/data/plugins/ring/Monumenta/bounties'),
            ],
        },

        'test2':{
            'config':server_config_to_copy + [
                ('server.properties', 'view-distance', 'view-distance=12'),
                ('spigot.yml', 'view-distance', '    view-distance: 12'),
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
                ('server.properties', 'view-distance', 'view-distance=12'),
                ('spigot.yml', 'view-distance', '    view-distance: 12'),
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
                ('server.properties', 'difficulty', 'difficulty=peaceful'),
                ('server.properties', 'gamemode', 'gamemode=creative'),
                ('plugins/MonumentaNetworkRelay/config.yml', 'broadcast-command-sending-enabled', 'broadcast-command-sending-enabled: false'),
                ('plugins/FastAsyncWorldEdit/config-legacy.yml', "wand-item:", "wand-item: minecraft:diamond_axe"),
                ('plugins/FastAsyncWorldEdit/worldedit-config.yml', "wand-item:", "wand-item: minecraft:diamond_axe"),
            ],
            'linked':server_config_min + luckperms_standalone + monumenta + worldedit + speedchanger + voxelsniper + dynmap + coreprotect + gobrush + [
                ('plugins/NetworkChat.jar', '../../server_config/plugins/NetworkChat.jar'),
                ('plugins/MonumentaNetworkChat/config.yml', '../../../server_config/data/plugins/build/MonumentaNetworkChat/config.yml'),
                ('plugins/MonumentaNetworkChat/help', '../../../server_config/data/plugins/all/MonumentaNetworkChat/help'),
                ('plugins/nbteditor.jar', '../../server_config/plugins/nbteditor.jar'),
                ('plugins/LibraryOfSouls.jar', '../../server_config/plugins/LibraryOfSouls.jar'),
            ],
        },

        'mobs':{
            'config':server_config_to_copy + [
                ('server.properties', 'view-distance', 'view-distance=6'),
                ('spigot.yml', 'view-distance', '    view-distance: 6'),
                ('server.properties', 'difficulty', 'difficulty=normal'),
                ('plugins/LibraryOfSouls/config.yml', 'read_only', 'read_only: false'),
            ],
            'linked':server_config + base_plugins + dynmap,
        },

        'event':{
            'config':server_config_to_copy + [
                ('server.properties', 'view-distance', 'view-distance=8'),
                ('spigot.yml', 'view-distance', '    view-distance: 8'),
            ],
            'linked':server_config + base_plugins + dynmap,
        },

        'dev1':{
            'config':server_config_to_copy + [
                ('server.properties', 'view-distance', 'view-distance=6'),
                ('spigot.yml', 'view-distance', '    view-distance: 6'),
                ('server.properties', 'difficulty', 'difficulty=normal'),
            ],
            'linked':server_config + base_plugins + dynmap,
        },

        'dev2':{
            'config':server_config_to_copy + [
                ('server.properties', 'view-distance', 'view-distance=6'),
                ('spigot.yml', 'view-distance', '    view-distance: 6'),
                ('server.properties', 'difficulty', 'difficulty=normal'),
            ],
            'linked':server_config + base_plugins + dynmap,
        },

        'dev3':{
            'config':server_config_to_copy + [
                ('server.properties', 'view-distance', 'view-distance=6'),
                ('spigot.yml', 'view-distance', '    view-distance: 6'),
                ('server.properties', 'difficulty', 'difficulty=normal'),
            ],
            'linked':server_config + base_plugins + dynmap,
        },

        'dev4':{
            'alt_version': '1.18',
            'config':server_config_to_copy_1_18 + [
                ('server.properties', 'view-distance', 'view-distance=6'),
                ('spigot.yml', 'view-distance', '    view-distance: 6'),
                ('server.properties', 'difficulty', 'difficulty=normal'),
            ],
            'linked':server_config_1_18 + base_plugins_1_18,
        },

        'plots':{
            'config':server_config_to_copy + [
                ('server.properties', 'view-distance', 'view-distance=6'),
                ('spigot.yml', 'view-distance', '    view-distance: 6'),
            ],
            'linked':server_config + base_plugins + dynmap,
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
                ('server.properties', 'gamemode', 'gamemode=adventure'),
                ('server.properties', 'enable-command-block', 'enable-command-block=false'),
                ('server.properties', 'white-list', 'white-list=false'),
                ('server.properties', 'spawn-monsters', 'spawn-monsters=false'),
                ('server.properties', 'spawn-npcs', 'spawn-npcs=false'),
                ('server.properties', 'spawn-protection', 'spawn-protection=16'),
                ('paper.yml', 'keep-spawn-loaded', '    keep-spawn-loaded: true'),
                ('permissions.yml', 'players:'),
                ('permissions.yml', '  description: Default players'),
                ('permissions.yml', '  default: true'),
                ('permissions.yml', '  children:'),
                ('permissions.yml', '    minecraft.autocraft: true'),
                ('permissions.yml', '    minecraft.command.help: true'),
                ('permissions.yml', '    minecraft.command.list: true'),
                ('permissions.yml', '    minecraft.command.me: true'),
                ('permissions.yml', '    minecraft.command.tell: true'),
                ('permissions.yml', '    minecraft.command.tps: true'),
                ('permissions.yml', '    monumenta.command.transferserver: true'),
                ('plugins/MonumentaRedisSync/config.yml', 'saving_disabled:', 'saving_disabled: true'),
                ('plugins/MonumentaRedisSync/config.yml', 'scoreboard_cleanup_enabled:', 'scoreboard_cleanup_enabled: false'),
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
        'teal': 9,
        'forum': 8,
        'remorse': 8,

        'tutorial': 9,
        'labs': 10,
        'willows': 8,
        'corridors': 8,
        'verdant': 9,
        'sanctum': 10,
        'reverie': 10,
        'rush': 5,
        'mist': 8,
        'depths': 5,
        'test': 8,
        'playerplots': 6,
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


    # These shards are copies of another shard, using that other shard's name for {servername} replacements
    copied_shard_config = {
        "valley-2": "valley",
        "valley-3": "valley",
        "isles-2": "isles",
        "isles-3": "isles",
        "depths-2": "depths",
        "depths-3": "depths",
    }

    for key in copied_shard_config:
        copy_of = copied_shard_config[key]
        config[key] = copy.deepcopy(config[copy_of])
        config[key]["copy_of"] = copy_of


    # Config additions that are specific to build or play server
    if SERVER_TYPE == 'build':
        config = add_config_if_not_set(config, ('server.properties', 'difficulty', 'difficulty=peaceful'))
        config = add_config_if_not_set(config, ('spigot.yml', 'tab-complete', '  tab-complete: 0'))
        config = add_config_if_not_set(config, ('server.properties', 'white-list', 'white-list=true'))
        config = add_config_if_not_set(config, ('server.properties', 'player-idle-timeout', 'player-idle-timeout=60'))
    else:
        config = add_config_if_not_set(config, ('server.properties', 'difficulty', 'difficulty=normal'))
        config = add_config_if_not_set(config, ('spigot.yml', 'tab-complete', '  tab-complete: 9999'))
        config = add_config_if_not_set(config, ('server.properties', 'white-list', 'white-list=false'))

        # Player analytics plugin only for play server
        for key in config:
            if not "purgatory" in key:
                if "build" in key:
                    config[key]['linked'] = config[key]['linked'] + plan
                else:
                    config[key]['linked'] = config[key]['linked'] + plan


    for servername in server_list:
        gen_server_config(servername)
