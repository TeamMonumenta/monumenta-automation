#!/usr/bin/env python3
"""Generates server configuration for Monumenta's shards"""

import argparse
import os
import re
import uuid
import copy
from pathlib import Path
import yaml

MONUMENTA_NAMESPACE = uuid.UUID('444c3990-e4e4-4c28-97c7-a8f6b1f09d30')

def get_alt_version(alt_version, original_path_str, relative_to=Path('.')):
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
    original_path = Path(original_path_str)

    if alt_version is None:
        return original_path_str

    parts = original_path.name.split('.', maxsplit=1)
    parts[0] = parts[0] + f'-{alt_version}'
    alt_name = f'.'.join(parts)

    test_path = original_path.parent / alt_name
    if not test_path.is_absolute():
        test_path = relative_to / test_path
    if test_path.exists():
        return original_path.parent / alt_name

    return original_path_str

# config should be the entire config map
# data should be a tuple like ('server.properties', 'difficulty', 'difficulty=peaceful')
def add_config_if_not_set(config, data):
    for shard_config in config.values():
        exists = False
        for replacement in shard_config['config']:
            if len(replacement) == 3 and data[0] in replacement[0] and data[1] in replacement[1]:
                exists = True
        if not exists:
            shard_config['config'] += [data]

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
    serverConfig = dest['config']

    # If this was a copy of another shard, get the other shard name to be used for {servername} replacements
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

        altold = get_alt_version(alt_version, old)
        if altold != old:
            print(f"Using alternate suffix {alt_version} for copied file {altold}")
            old = altold

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

        newtargetname = get_alt_version(alt_version, targetname, relative_to=Path(linkname).parent)
        if targetname != newtargetname:
            print(f"Using alternate suffix {alt_version} for link to {newtargetname}")
            targetname = newtargetname

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

    ################################################################################
    # Fix plan UUIDs
    ################################################################################

    plan_server_info_path = f"{servername}/plugins/Plan/ServerInfoFile.yml"
    if os.path.isfile(plan_server_info_path):
        with open(plan_server_info_path, 'r') as fp:
            plan_server_info_contents = yaml.load(fp, Loader=yaml.FullLoader)

        shard_uuid = uuid.uuid5(MONUMENTA_NAMESPACE, servername)
        shard_numeric_id = hash(shard_uuid) & ((1 << 31) - 1)

        plan_server_info_contents["Server"]["ID"] = shard_numeric_id
        plan_server_info_contents["Server"]["UUID"] = str(shard_uuid)

        with open(plan_server_info_path, 'w') as fp:
            yaml.dump(plan_server_info_contents, fp, indent=4, allow_unicode=True, sort_keys=False)

    print("Success - " + servername)

if __name__ == '__main__':

    # Main entry point
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument('--play', action='store_true', help="Uses play server configuration, rather than the build server's")
    arg_parser.add_argument('shard_path', type=Path, nargs='+', help="The shards/proxies to configure")
    args = arg_parser.parse_args()

    is_play = args.play
    SERVER_TYPE = 'play' if is_play else 'build'
    server_list = args.shard_path

    if is_play:
        print("Using play server settings!")
    else:
        print("Using build server settings!")

    server_config_to_copy = [
        ('bukkit.yml',),
        ('commands.yml',),
        ('eula.txt',),
        ('help.yml',),
        ('permissions.yml',),
        ('server.properties',),
        ('spigot.yml',),
        ('config/paper-global.yml',),
        ('config/paper-world-defaults.yml',),
        ('config/monumenta-mixins.yml',),
        ('wepif.yml',),
        ('plugins/ViaVersion/config.yml',),
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
        ('log4j2-shard.xml',),
        ('plugins/TAB/config.yml',),
        ('plugins/TAB/skincache.yml',),
    ]

    mixins = [
        ('mods/MonumentaMixins.jar', '../../server_config/mods/MonumentaMixins.jar'),
        ('server.jar', '../server_config/mixinloader.jar'),
    ]

    purgatory_min = mixins + [
        ('paperclip.jar', '../server_config/paperclip.jar'),
        ('plugins/Vault.jar', '../../server_config/plugins/Vault.jar'),
        ('plugins/ProtocolLib.jar', '../../server_config/plugins/ProtocolLib.jar'),
        ('plugins/PlaceholderAPI.jar', '../../server_config/plugins/PlaceholderAPI.jar'),
        ('plugins/CommandAPI.jar', '../../server_config/plugins/CommandAPI.jar'),
        ('plugins/RedisSync.jar', '../../server_config/plugins/RedisSync.jar'),
        ('plugins/ViaVersion.jar', '../../server_config/plugins/ViaVersion.jar'),
    ]

    proxy_copy = [
        ('log4j2-velocity.xml',),
        ('plugins/maintenance/config.yml',),
        ('plugins/monumenta-redisapi/config.yaml',),
        ('velocity.toml',),
        ('forwarding.secret',),
    ]

    proxy_link = [
        ('velocity.jar', '../server_config/velocity.jar'),
        ('server-icon.png', '../server_config/data/server_config_template/server-icon.png'),
        ('plugins/AdvancedServerList-Velocity.jar', '../../server_config/plugins/AdvancedServerList-Velocity.jar'),
        ('plugins/advancedserverlist/config.yml', '../../../server_config/data/server_config_template/plugins/AdvancedServerList/config.yml'),
        ('plugins/advancedserverlist/profiles', '../../../server_config/data/server_config_template/plugins/AdvancedServerList/profiles/{}'.format(SERVER_TYPE)),
        ('plugins/LiteBans.jar', '../../server_config/plugins/LiteBans.jar'),
        ('plugins/litebans/config.yml', '../../../server_config/data/plugins/proxy/litebans/config.yml'),
        ('plugins/litebans/messages.yml', '../../../server_config/data/plugins/proxy/litebans/messages.yml'),
        ('plugins/litebans/webhooks.yml', f'../../../server_config/data/plugins/proxy/litebans/{SERVER_TYPE}/webhooks.yml'),
        ('plugins/LuckPerms-Velocity.jar', '../../server_config/plugins/LuckPerms-Velocity.jar'),
        ('plugins/luckperms', '../../server_config/plugins/LuckPerms/{}'.format(SERVER_TYPE)),
        ('plugins/Maintenance-Velocity.jar', '../../server_config/plugins/Maintenance-Velocity.jar'),
        ('plugins/Monumenta.jar', '../../server_config/plugins/Monumenta.jar'),
        ('plugins/monumenta-velocity/config.yaml', '../../../server_config/data/plugins/proxy/monumenta-velocity/config.yaml'),
        ('plugins/MonumentaNetworkRelay.jar', '../../server_config/plugins/MonumentaNetworkRelay.jar'),
        ('plugins/monumenta-network-relay/config.yaml', '../../../server_config/data/plugins/proxy/monumenta-network-relay/config.yaml'),
        ('plugins/MonumentaRedisSync.jar', '../../server_config/plugins/MonumentaRedisSync.jar'),
        ('plugins/nuvotifier.jar', '../../server_config/plugins/nuvotifier.jar'),
        ('plugins/nuvotifier', '../../server_config/data/plugins/proxy/nuvotifier'),
        ('plugins/PremiumVanish.jar', '../../server_config/plugins/PremiumVanish.jar'),
        ('plugins/premiumvanish/velocity-config.yml', '../../../server_config/data/plugins/proxy/premiumvanish/velocity-config.yml'),
        ('plugins/spark-velocity.jar', '../../server_config/plugins/spark-velocity.jar'),
        ('plugins/spark', '/home/epic/5_SCRATCH/spark'),
        #('plugins/ViaVersion.jar', '../../server_config/plugins/ViaVersion.jar'), # needs to be 5.0.0+ since that is when Velocity support was added
        #('plugins/viaversion/config.yml', '../../../server_config/data/server_config_template/plugins/ViaVersion/config.yml'),
        ('plugins/velocity-prometheus-exporter.jar', '../../server_config/plugins/velocity-prometheus-exporter.jar'),
        ('plugins/velocity-prometheus-exporter/config.json', '../../../server_config/data/plugins/proxy/velocity-prometheus-exporter/config.json'),
    ]

    proxy_plan = [
        ('plugins/Plan.jar', '../../server_config/plugins/Plan.jar'), # TODO: how to use same config?
        ('plugins/plan/config.yml', '../../../server_config/data/server_config_template/plugins/plan/config.yml'),
    ]

    server_config_min = purgatory_min + [
        ('plugins/PlaceholderAPI', '../../server_config/plugins/PlaceholderAPI'),
        ('plugins/BKCommonLib.jar', '../../server_config/plugins/BKCommonLib.jar'),
        ('plugins/LightCleaner.jar', '../../server_config/plugins/LightCleaner.jar'),
    ]

    server_config = server_config_min + [
        ('Project_Epic-{servername}/generated', '../../server_config/data/generated'),
        ('Project_Epic-{servername}/datapacks', '../../server_config/data/datapacks'),
    ]

    network_chat = [
        ('plugins/MonumentaNetworkChat.jar', '../../server_config/plugins/MonumentaNetworkChat.jar'),
        ('plugins/MonumentaNetworkChat/config.yml', '../../../server_config/data/plugins/all/MonumentaNetworkChat/config.yml'),
        ('plugins/MonumentaNetworkChat/global_filters', '/home/epic/4_SHARED/global_chat_filters'),
        ('plugins/MonumentaNetworkChat/help', '../../../server_config/data/plugins/all/MonumentaNetworkChat/help'),
    ]

    monumenta = [
        ('plugins/MonumentaNetworkRelay.jar', '../../server_config/plugins/MonumentaNetworkRelay.jar'),
        ('plugins/MonumentaWorldManagement.jar', '../../server_config/plugins/MonumentaWorldManagement.jar'),
        ('plugins/MonumentaWorldManagement/config.yml', '../../../server_config/data/plugins/{servername}/MonumentaWorldManagement/config.yml'),
        ('plugins/Monumenta.jar', '../../server_config/plugins/Monumenta.jar'),
        ('plugins/Monumenta/experiencinator_config.json', '../../../server_config/data/plugins/all/Monumenta/experiencinator_config.json'),
        ('plugins/Monumenta/SiriusBlightArena.json', '../../../server_config/data/plugins/all/Monumenta/SiriusBlightArena.json'),
        ('plugins/Monumenta/skins.json', '../../../server_config/data/plugins/all/Monumenta/skins.json'),
        ('plugins/Monumenta/mmquest.json', '../../../server_config/data/plugins/all/Monumenta/mmquest.json'),
        ('plugins/Monumenta/market.json', '../../../server_config/data/plugins/all/Monumenta/market.json'),
        ('plugins/Monumenta/ItemIndex', '../../../server_config/data/plugins/all/ItemIndex'),
        ('plugins/Monumenta/DataCollection', '/home/epic/3_DOMAIN_SHARED/DataCollection'),
        ('plugins/Monumenta/DepthsStats', '/home/epic/3_DOMAIN_SHARED/DepthsStats'),
        ('plugins/Monumenta/seasonalevents', '../../../server_config/data/plugins/all/Monumenta/seasonalevents'),
        ('plugins/Monumenta/images', '../../../server_config/data/plugins/all/Monumenta/images'),
        ('plugins/Monumenta/InfinityTower/TowerMobs.json', '../../../../server_config/data/plugins/valley/Monumenta/InfinityTower/TowerMobs.json'),
        ('plugins/Monumenta/InfinityTower/InfinityTowerDefault.json', '../../../../server_config/data/plugins/valley/Monumenta/InfinityTower/InfinityTowerDefault.json'),
        ('plugins/Monumenta/properties/CommonProperties.json', '../../../../server_config/data/plugins/all/Monumenta/properties/CommonProperties.json'),
        ('plugins/Monumenta/properties/LocalProperties.json', '../../../../server_config/data/plugins/{servername}/Monumenta/properties/LocalProperties.json'),
        ('plugins/MonumentaWarps.jar', '../../server_config/plugins/MonumentaWarps.jar'),
        ('plugins/ChestSort.jar', '../../server_config/plugins/ChestSort.jar'),
        ('plugins/ChestSort/categories', '../../../server_config/data/plugins/all/ChestSort/categories'),
        ('plugins/HolographicDisplays.jar', '../../server_config/plugins/HolographicDisplays.jar'),
        ('plugins/HolographicDisplays/database.yml', '../../../server_config/data/plugins/{servername}/HolographicDisplays/database.yml'),
        ('plugins/spark.jar', '../../server_config/plugins/spark.jar'),
        ('plugins/spark', '/home/epic/5_SCRATCH/spark'),
        ('plugins/prometheus-exporter.jar', '../../server_config/plugins/prometheus-exporter.jar'),
        ('plugins/ScriptedQuests.jar', '../../server_config/plugins/ScriptedQuests.jar'),
        ('plugins/ScriptedQuests/translations', f'/home/epic/3_DOMAIN_SHARED/translations'),
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
        ('plugins/ScriptedQuests/zone_namespaces/{servername}', '../../../../server_config/data/scriptedquests/zone_namespaces/{servername}'),
        ('plugins/ScriptedQuests/zone_namespaces/common', '../../../../server_config/data/scriptedquests/zone_namespaces/common'),
        ('plugins/ScriptedQuests/zone_properties/{servername}', '../../../../server_config/data/scriptedquests/zone_properties/{servername}'),
        ('plugins/ScriptedQuests/zone_properties/common', '../../../../server_config/data/scriptedquests/zone_properties/common'),
        ('plugins/ScriptedQuests/zone_property_groups/{servername}', '../../../../server_config/data/scriptedquests/zone_property_groups/{servername}'),
        ('plugins/ScriptedQuests/zone_property_groups/common', '../../../../server_config/data/scriptedquests/zone_property_groups/common'),
        ('plugins/MonumentaStructureManagement.jar', '../../server_config/plugins/MonumentaStructureManagement.jar'),
        ('plugins/MonumentaStructureManagement/structures', '../../../server_config/data/structures'),
        ('plugins/MonumentaStructureManagement/config.yml', '../../../server_config/data/plugins/{servername}/MonumentaStructureManagement/config.yml'),
        ('plugins/TAB.jar', '../../server_config/plugins/TAB.jar'),
    ]

    vanish = [
        ('plugins/PremiumVanish.jar', '../../server_config/plugins/PremiumVanish.jar'),
        ('plugins/PremiumVanish/config.yml', '../../../server_config/data/plugins/all/PremiumVanish/config.yml'),
    ]

    coreprotect = [
        ('plugins/CoreProtect.jar', '../../server_config/plugins/CoreProtect.jar'),
    ]

    worldedit = [
        ('plugins/FastAsyncWorldEdit.jar', '../../server_config/plugins/FastAsyncWorldEdit.jar'),
        ('plugins/FastAsyncWorldEdit/schematics', '/home/epic/4_SHARED/schematics'),
    ]

    dynmap = [
        ('plugins/Dynmap.jar', '../../server_config/plugins/Dynmap.jar'),
        ('plugins/dynmap/configuration.txt', '../../../server_config/data/plugins/all/dynmap/' + SERVER_TYPE + '/configuration.txt'),
        ('plugins/dynmap/markers.yml', '../../../server_config/data/plugins/{servername}/dynmap/' + SERVER_TYPE + '/markers.yml'),
        ('plugins/dynmap/worlds.txt', '../../../server_config/data/plugins/{servername}/dynmap/' + SERVER_TYPE + '/worlds.txt'),
        ('plugins/dynmap/templates', '../../../server_config/data/plugins/all/dynmap/' + SERVER_TYPE + '/templates'),
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

    metatools = [
        ('plugins/MetaEdits.jar', '../../server_config/plugins/MetaEdits.jar'),
        ('plugins/MetaBrushes.jar', '../../server_config/plugins/MetaBrushes.jar'),
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

    litebans = [
        ('plugins/LiteBans.jar', '../../server_config/plugins/LiteBans.jar'),
        ('plugins/LiteBans/config.yml', '../../../server_config/data/plugins/all/LiteBans/config.yml'),
        ('plugins/LiteBans/messages.yml', '../../../server_config/data/plugins/all/LiteBans/messages.yml'),
        ('plugins/LiteBans/webhooks.yml', f'../../../server_config/data/plugins/all/LiteBans/{SERVER_TYPE}/webhooks.yml'),
    ]

    axiom = [
        ('plugins/AxiomPaper.jar', '../../server_config/plugins/AxiomPaper.jar'),
        ('plugins/AxiomPaper', '../../server_config/data/plugins/all/AxiomPaper'),
    ]

    # Index of nodes:
    #   server_config
    #   structures

    base_plugins = mixins + luckperms + monumenta + openinv + worldedit + coreprotect + nbteditor + network_chat
    if SERVER_TYPE == 'build':
        base_plugins += speedchanger + voxelsniper + gobrush + axiom
    else:
        base_plugins += vanish + litebans

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
            'config':server_config_to_copy,
            'linked':server_config + base_plugins + [
                ('plugins/Monumenta/InfinityTower/InfinityFloors.json', '../../../../server_config/data/plugins/valley/Monumenta/InfinityTower/InfinityFloors.json'),
                ('plugins/Monumenta/bounties', '../../../server_config/data/plugins/valley/Monumenta/bounties'),
            ],
        },

        'isles':{
            'config':server_config_to_copy + [
                ('spigot.yml', '      villagers:', '      villagers: 25'),
            ],
            'linked':server_config + base_plugins + [
                ('plugins/Monumenta/bounties', '../../../server_config/data/plugins/isles/Monumenta/bounties'),
            ],
        },

        'ring':{
            'config':server_config_to_copy + [
                ('spigot.yml', '      villagers:', '      villagers: 25'),
            ],
            'linked':server_config + base_plugins + [
                ('plugins/Monumenta/bounties', '../../../server_config/data/plugins/ring/Monumenta/bounties'),
            ],
        },

        #'futurama':{
        #    'config':server_config_to_copy + [
        #        ('server.properties', 'view-distance', 'view-distance=8'),
        #        ('spigot.yml', 'view-distance', '    view-distance: 8'),
        #        ('spigot.yml', '      villagers:', '      villagers: 25'),
        #    ],
        #    'linked':server_config + base_plugins + [
        #        ('plugins/Monumenta/bounties', '../../../server_config/data/plugins/ring/Monumenta/bounties'),
        #    ],
        #},

        'test2':{
            'config':server_config_to_copy + [
                ('server.properties', 'view-distance', 'view-distance=12'),
                ('spigot.yml', 'view-distance', '    view-distance: 12'),
            ],
            'linked':server_config + base_plugins + dynmap,
        },

        'dungeon':{
            'config':server_config_to_copy,
            'linked':server_config + base_plugins + dynmap + [
                ('plugins/Roguelite', '../../server_config/data/Roguelite'),
                ('plugins/Roguelite.jar', '../../server_config/plugins/Roguelite.jar'),
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
                ('spigot.yml', 'tab-complete', '  tab-complete: 0'),
                ('server.properties', 'difficulty', 'difficulty=peaceful'),
                ('server.properties', 'gamemode', 'gamemode=creative'),
                ('plugins/MonumentaNetworkRelay/config.yml', 'broadcast-command-sending-enabled', 'broadcast-command-sending-enabled: false'),
                ('plugins/FastAsyncWorldEdit/config-legacy.yml', "wand-item:", "wand-item: minecraft:diamond_axe"),
                ('plugins/FastAsyncWorldEdit/worldedit-config.yml', "wand-item:", "wand-item: minecraft:diamond_axe"),
            ],
            'linked':server_config_min + luckperms_standalone + monumenta + worldedit + speedchanger + voxelsniper + dynmap + coreprotect + gobrush + vanish + [
                ('plugins/MonumentaNetworkChat.jar', '../../server_config/plugins/MonumentaNetworkChat.jar'),
                ('plugins/MonumentaNetworkChat/config.yml', '../../../server_config/data/plugins/build/MonumentaNetworkChat/config.yml'),
                ('plugins/MonumentaNetworkChat/help', '../../../server_config/data/plugins/all/MonumentaNetworkChat/help'),
                ('plugins/nbteditor.jar', '../../server_config/plugins/nbteditor.jar'),
                ('plugins/LibraryOfSouls.jar', '../../server_config/plugins/LibraryOfSouls.jar'),
            ],
        },

        'mobs':{
            'config':server_config_to_copy + [
                ('server.properties', 'difficulty', 'difficulty=normal'),
                ('plugins/LibraryOfSouls/config.yml', 'read_only', 'read_only: false'),
            ],
            'linked':server_config + base_plugins + dynmap,
        },

        'event':{
            'config':server_config_to_copy,
            'linked':server_config + base_plugins + dynmap,
        },

        'dev1':{
            'config':server_config_to_copy + [
                ('server.properties', 'difficulty', 'difficulty=normal'),
            ],
            'linked':server_config + base_plugins + dynmap,
        },

        'dev2':{
            'config':server_config_to_copy + [
                ('server.properties', 'difficulty', 'difficulty=normal'),
            ],
            'linked':server_config + base_plugins + dynmap,
        },

        'dev3':{
            'config':server_config_to_copy + [
                ('server.properties', 'difficulty', 'difficulty=normal'),
            ],
            'linked':server_config + base_plugins + dynmap,
        },

        'dev4':{
            'config':server_config_to_copy + [
                ('server.properties', 'difficulty', 'difficulty=normal'),
            ],
            'linked':server_config + base_plugins,
        },

        'plots':{
            'config':server_config_to_copy + [
                # plots optimization for players with bad PCs
                # TODO: this is hardcoded to the defaults - if they change, this will break
                # TODO: you'll know this breaks when players complain about lag in market again :suffer:
                # refer to https://discord.com/channels/186225508562763776/447933054317494283/1121326813990367294
                ('spigot.yml', '      animals: 48', '      animals: 12'),
                ('spigot.yml', '      monsters: 48', '      monsters: 12'),
                ('spigot.yml', '      misc: 32', '      misc: 12'),
                ('spigot.yml', '      other: 96', '      other: 12'),
            ],
            'linked':server_config + base_plugins + dynmap,
        },

        'shiftingcity':{
            'config':server_config_to_copy,
            'linked':server_config + base_plugins + [
                ('plugins/Roguelite', '../../server_config/data/Roguelite'),
                ('plugins/Roguelite.jar', '../../server_config/plugins/Roguelite.jar'),
            ],
        },

        'purgatory':{
            'config':server_config_to_copy + [
                ('server.properties', 'force-gamemode', 'force-gamemode=true'),
                ('server.properties', 'gamemode', 'gamemode=adventure'),
                ('server.properties', 'enable-command-block', 'enable-command-block=false'),
                ('server.properties', 'white-list', 'white-list=false'),
                ('server.properties', 'spawn-monsters', 'spawn-monsters=false'),
                ('server.properties', 'spawn-npcs', 'spawn-npcs=false'),
                ('server.properties', 'spawn-protection', 'spawn-protection=16'),
                ('paper.yml', 'keep-spawn-loaded', '    keep-spawn-loaded: true'), # TODO FIXME
                ('permissions.yml', 'players:'),
                ('permissions.yml', '  description: Default players'),
                ('permissions.yml', '  default: true'),
                ('permissions.yml', '  children:'),
                ('permissions.yml', '    minecraft.command.help: true'),
                ('permissions.yml', '    minecraft.command.list: true'),
                ('permissions.yml', '    minecraft.command.me: true'),
                ('permissions.yml', '    minecraft.command.tell: true'),
                ('permissions.yml', '    minecraft.command.tps: true'),
                ('permissions.yml', '    monumenta.command.rejoin: true'),
                ('plugins/MonumentaRedisSync/config.yml', 'saving_disabled:', 'saving_disabled: true'),
                ('plugins/MonumentaRedisSync/config.yml', 'scoreboard_cleanup_enabled:', 'scoreboard_cleanup_enabled: false'),
            ],
            'linked':purgatory_min,
        },

        'velocity': {
            'config': proxy_copy + [
                ('plugins/maintenance/config.yml', 'maintenance-enabled:', 'maintenance-enabled: true'),
                ('velocity.toml', 'failover-on-unexpected-server-disconnect =', 'failover-on-unexpected-server-disconnect = {}'.format("true" if SERVER_TYPE == 'build' else "false")),
            ],
            'linked': proxy_link
        }

    }

    simple_view_distance_config = {
        'blue': 10,
        'brown': 11,
        'build': 10,
        'corridors': 10,
        'cyan': 10,
        'depths': 10,
        'dev1': 10,
        'dev2': 10,
        'dev3': 10,
        'dev4': 10,
        'dungeon': 12,
        'event': 10,
        'forum': 10,
        'gallery': 10,
        'gray': 10,
        'guildplots': 12,
        'hexfall': 10,
        'indigo': 10,
        'isles': 10,
        'labs': 10,
        'lightblue': 12,
        'lightgray': 11,
        'lime': 10,
        'magenta': 12,
        'mobs': 10,
        'orange': 12,
        'pink': 10,
        'playerplots': 10,
        'plots': 10,
        'portal': 10,
        'purgatory': 4,
        'purple': 10,
        'reverie': 10,
        'ring': 10,
        'ruin': 10,
        'rush': 10,
        'skt': 10,
        'shiftingcity': 15,
        'teal': 10,
        'test': 10,
        'tutorial': 10,
        'valley': 10,
        'white': 10,
        'willows': 10,
        'yellow': 10,
        'zenith': 10,
    }

    for key, distance in simple_view_distance_config.items():
        shard_config = config.get(key, None)
        if shard_config is None:
            shard_config = {
                'config': copy.deepcopy(server_config_to_copy),
                'linked': server_config + base_plugins,
            }
            config[key] = shard_config

        shard_config_changes = copy.deepcopy(shard_config.get('config', None))
        if shard_config_changes is None:
            shard_config_changes = copy.deepcopy(server_config_to_copy)
        shard_config['config'] = shard_config_changes

        shard_config_changes += [
            ('server.properties', 'view-distance', 'view-distance={}'.format(distance)),
            ('spigot.yml', 'view-distance', '    view-distance: {}'.format(distance)),
        ]

    simple_simulation_distance_config = {
        'blue': 8,
        'brown': 10,
        'build': 8,
        'corridors': 8,
        'cyan': 8,
        'depths': 5,
        'dev1': 6,
        'dev2': 6,
        'dev3': 6,
        'dev4': 6,
        'dungeon': 12,
        'event': 8,
        'forum': 8,
        'gallery': 8,
        'gray': 8,
        'guildplots': 6,
        'hexfall': 8,
        'indigo': 8,
        'isles': 8,
        'labs': 10,
        'lightblue': 10,
        'lightgray': 10,
        'lime': 9,
        'magenta': 10,
        'mobs': 6,
        'orange': 10,
        'pink': 8,
        'playerplots': 6,
        'plots': 6,
        'portal': 8,
        'purgatory': 4,
        'purple': 10,
        'reverie': 10,
        'ring': 8,
        'ruin': 8,
        'rush': 5,
        'skt': 8,
        'shiftingcity': 15,
        'teal': 9,
        'test': 8,
        'tutorial': 9,
        'valley': 8,
        'white': 8,
        'willows': 8,
        'yellow': 8,
        'zenith': 5,
    }

    for key, shard_config in config.items():
        distance = simple_simulation_distance_config.get(key, 10)
        view_distance = simple_view_distance_config.get(key, None)
        if view_distance is not None:
            # If simulation distance is larger, it overrides the view distance
            distance = min(distance, view_distance)

        shard_config_changes = copy.deepcopy(shard_config.get('config', None))
        if shard_config_changes is None:
            shard_config_changes = copy.deepcopy(server_config_to_copy)
        shard_config['config'] = shard_config_changes

        shard_config_changes += [
            ('server.properties', 'simulation-distance', 'simulation-distance={}'.format(distance)),
            ('spigot.yml', 'simulation-distance', '    simulation-distance: {}'.format(distance)),
        ]


    # These shards are copies of another shard, using that other shard's name for {servername} replacements
    copied_shard_config = {
        "valley-2": "valley",
        "valley-3": "valley",
        "isles-2": "isles",
        "isles-3": "isles",
        "ring-2": "ring",
        "ring-3": "ring",
        "ring-4": "ring",
        "ring-5": "ring",
        "ring-6": "ring",
        "ring-7": "ring",
        "ring-8": "ring",
        "ring-9": "ring",
        "ring-10": "ring",
        "ring-11": "ring",
        "ring-12": "ring",
        "ring-13": "ring",
        "ring-14": "ring",
        "ring-15": "ring",
        "ring-16": "ring",
        "white-2": "white",
        "orange-2": "orange",
        "magenta-2": "magenta",
        "magenta-3": "magenta",
        "lightblue-2": "lightblue",
        "lightblue-3": "lightblue",
        "yellow-2": "yellow",
        "yellow-3": "yellow",
        "willows-2": "willows",
        "willows-3": "willows",
        "indigo-2": "indigo",
        "indigo-3": "indigo",
        "indigo-4": "indigo",
        "indigo-5": "indigo",
        "indigo-6": "indigo",
        "indigo-7": "indigo",
        "indigo-8": "indigo",
        "indigo-9": "indigo",
        "indigo-10": "indigo",
        "blue-2": "blue",
        "blue-3": "blue",
        "blue-4": "blue",
        "brown-2": "brown",
        "brown-3": "brown",
        "reverie-2": "reverie",
        "reverie-3": "reverie",
        "gallery-2": "gallery",
        "gallery-3": "gallery",
        "skt-2": "skt",
        "skt-3": "skt",
        "depths-2": "depths",
        "zenith-2": "zenith",
        "zenith-3": "zenith",
        "zenith-4": "zenith",
        "zenith-5": "zenith",
        "zenith-6": "zenith",
        "zenith-7": "zenith",
        "zenith-8": "zenith",
        "zenith-9": "zenith",
        "zenith-10": "zenith",
        "zenith-11": "zenith",
        "zenith-12": "zenith",
        "hexfall-2": "hexfall",
        "hexfall-3": "hexfall",
        "hexfall-4": "hexfall",
        "hexfall-5": "hexfall",
        "hexfall-6": "hexfall",
        "hexfall-7": "hexfall",
        "hexfall-8": "hexfall",
        "hexfall-9": "hexfall",
        "hexfall-10": "hexfall",
        "hexfall-11": "hexfall",
        "hexfall-12": "hexfall",
        "hexfall-13": "hexfall",
        "hexfall-14": "hexfall",
        "hexfall-15": "hexfall",
        "hexfall-16": "hexfall",
        "velocity-12": "velocity",
        "velocity-13": "velocity",
        "velocity-17": "velocity",
        "velocity-18": "velocity",
    }

    for key, copy_of in copied_shard_config.items():
        config[key] = copy.deepcopy(config[copy_of])
        config[key]["copy_of"] = copy_of

    # For plugins that should only load on the first instance (not very elegant solution, but it should work)
    config["valley"]["linked"] += dynmap
    config["isles"]["linked"] += dynmap
    config["ring"]["linked"] += dynmap

    # Config additions that are specific to build or play server
    if SERVER_TYPE == 'build':
        add_config_if_not_set(config, ('server.properties', 'difficulty', 'difficulty=peaceful'))
        add_config_if_not_set(config, ('spigot.yml', 'tab-complete', '  tab-complete: 0'))
        add_config_if_not_set(config, ('server.properties', 'white-list', 'white-list=true'))
        add_config_if_not_set(config, ('server.properties', 'player-idle-timeout', 'player-idle-timeout=60'))
    else:
        add_config_if_not_set(config, ('server.properties', 'difficulty', 'difficulty=normal'))
        add_config_if_not_set(config, ('spigot.yml', 'tab-complete', '  tab-complete: 9999'))
        add_config_if_not_set(config, ('server.properties', 'white-list', 'white-list=false'))

        # Player analytics plugin only for play server
        for key, shard_config in config.items():
            if not "purgatory" in key:
                if "velocity" in key:
                    shard_config['linked'] += proxy_plan
                    continue
                if "build" in key:
                    shard_config['linked'] += plan
                else:
                    shard_config['linked'] += plan


    original_wd = Path('.').resolve()
    for server_path in server_list:
        os.chdir(server_path.parent)
        gen_server_config(server_path.name)
    os.chdir(original_wd)
