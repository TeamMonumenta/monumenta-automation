#!/usr/bin/env python3

import shutil
import os
from pathlib import Path
import json

def extract_value(data, search_key) -> list[str]:
    results = []

    # If the current data is a dictionary
    if isinstance(data, dict):
        for key, value in data.items():
            if key == search_key and isinstance(value, str):  # Check if it's a string value
                results.append(value)
            # Recursively search for loot_table in nested structures
            elif isinstance(value, (dict, list)):
                results.extend(extract_value(value, search_key))

    # If the current data is a list
    elif isinstance(data, list):
        for item in data:
            results.extend(extract_value(item, search_key))

    return results

def find_loot_table_refs(table, dst, visited: set[str]):
    if table in visited:
        return

    visited.add(table)

    try:
        with open(f"{dst}/data/datapacks/base/data/epic/loot_tables/{table}.json", "r") as f:
            data = json.load(f)
    except:
        return

    for subtable in extract_value(data, "name"):
        find_loot_table_refs(subtable.removeprefix("epic:"), dst, visited)

def rm_filter(path, filters):
    directory = Path(path)
    for item in directory.iterdir():
        if item.is_dir():
            rm_filter(item, filters)
        elif True not in [x in str(item.absolute()) for x in filters]:
            item.unlink()
    try:
        directory.rmdir()
    except:
        pass

def redact_loot_tables(dst):
    must_keep = [
        "r2/items/currency/hyper_crystalline_shard",
        "r2/quests/114_elements",
        "r3/items/currency/archos_ring",
        "r3/items/currency/hyperchromatic_archos_ring",
        "r3/depths2/potion_roll",
        "r3/depths2/relic_roll",
        "r3/items/currency/indigo_blightdust",
        "r3/items/currency/weightedfortitude",
        "r2/delves/items/twisted_pome",
        "r3/depths2/uriddans_eternal_call_a18",
        "event/halloween2019/creepers_delight",
        "r3/depths2/shattered_gem",
        "r3/depths2/relic_roll_asc4",
        "r3/depths2/relic_roll_asc3",
        "r3/depths2/relic_roll_asc2",
        "r3/depths2/relic_roll_asc1",
        "r2/items/currency/compressed_crystalline_shard",
        "r2/items/currency/hyper_crystalline_shard",
        "r2/depths/loot/potion_roll",
        "r2/depths/loot/relicroll",
        "r2/depths/loot/voidstained_geode",
        "r2/delves/items/twisted_pome",
        "r2/delves/trophies/depths",
        "event/halloween2019/creepers_delight",
        "r2/depths/utility/lightning_bottle",
        "r2/items/currency/compressed_crystalline_shard",
        "r3/items/currency/archos_ring",
        "r3/items/currency/indigo_blightdust",
        "r2/depths/utility/dawnbringer_talisman",
        "r2/depths/utility/earthbound_talisman",
        "r2/depths/utility/flamecaller_talisman",
        "r2/depths/utility/frostborn_talisman",
        "r2/depths/utility/steelsage_talisman",
        "r2/depths/utility/shadowdancer_talisman",
        "r2/depths/utility/windwalker_talisman",
        "r3/depths2/dawnbringer_talisman_zenith",
        "r3/depths2/earthbound_talisman_zenith",
        "r3/depths2/flamecaller_talisman_zenith",
        "r3/depths2/frostborn_talisman_zenith",
        "r3/depths2/steelsage_talisman_zenith",
        "r3/depths2/shadowdancer_talisman_zenith",
        "r3/depths2/windwalker_talisman_zenith",
        "r3/charms/charms_trinket",
        "items/functions/depths_trinket",
        "r1/quests/53_reward",
        "pass/seasonal_pass_trinket",
        "pass/personal_cosmetic_interface",
        "r2/items/randommistportjunk/portable_parrot_bell",
        "r1/items/misc/tlaxan_record_player",
        "r2/depths/loot/soulsinger",
        "r3/delves/items/delves_trinket",
        "r1/items/misc/emotes_trinket",
        "r1/quests/36_crimson_contract",
        "r2/depths/loot/voidstained_geode",
        "r1/quests/36_crimson_contract",
        "r2/items/currency/hyper_crystalline_shard",
        "r1/items/currency/hyper_experience",
        "r1/items/currency/pulsating_gold",
        "r2/items/currency/pulsating_emerald",
        "r1/items/currency/shard_of_the_mantle",
        "r2/eldrask/materials/epic_material",
        "r2/lich/materials/ancestral_effigy",
        "r2/depths/loot/voidstained_geode",
        "r1/delves/rogue/persistent_parchment",
        "r1/items/uncommons/lightblue/unicorn_puke",
        "r1/blitz/blitz_doubloon",
        "r3/dungeons/bluestrike/boss/blackblood_shard",
        "r3/dungeons/bluestrike/boss/blackblood_dagger",
        "r3/dungeons/bluestrike/boss/blackblood_shard",
        "r2/dungeons/forum/ex_nihilo",
        "r2/dungeons/forum/ex_nihilo_hallud",
        "r2/dungeons/forum/ex_nihilo_chasom",
        "r2/dungeons/forum/ex_nihilo_midat",
        "r2/dungeons/forum/ex_nihilo_daath",
        "r2/dungeons/forum/ex_nihilo_keter",
        "event/halloween2019/tricked_creeper",
        "r1/blitz/blitz_master_guide",
        "r1/blitz/blitz_doubloon",
        "pass/metamorphosis_token",
        "pass/treasure_wheel_token",
        "pass/relic_wheel_token",
        "items/potions/regeneration_boon",
        "items/potions/absorption_boon",
        "items/potions/speed_boon",
        "items/potions/resistance_boon",
        "items/potions/strength_boon",
        "items/potions/regeneration_boon_2",
        "items/potions/absorption_boon_2",
        "items/potions/speed_boon_2",
        "items/potions/resistance_boon_2",
        "items/potions/strength_boon_2",
        "r1/items/currency/hyper_experience",
        "r1/items/currency/royal_crystal",
        "r2/items/currency/hyper_crystalline_shard",
        "r2/items/gleaming_seashell",
        "r3/items/currency/hyperchromatic_archos_ring",
        "r3/items/currency/godtree_carving",
        "r2/delves/items/twisted_strand",
        "r2/delves/items/twisted_pigment",
        "r2/depths/loot/voidstained_geode",
        "r2/delves/items/twisted_strand",
        "r3/gallery/items/torn_canvas",
        "r3/items/currency/liferoot_sapling",
        "event/winter2018/ice_diamond",
        "event/winter2019/essence_of_winter",
        "event/winter2023/boost_carrot_3000",
        "r3/world/poi/amanita_colony/endweekly_v2",
        "r3/world/poi/arx_spirensis/endweekly_v2",
        "r3/world/poi/farm/endweekly_v2",
        "r3/world/poi/celestial_rampart/endweekly_v2",
        "r3/world/poi/chanterelle_village/endweekly_v2",
        "r3/world/poi/chittering_gutters/endweekly_v2",
        "r3/world/poi/constellation_tower/endweekly_v2",
        "r3/world/poi/coven_fortress/endweekly_v2",
        "r3/world/poi/doomed_encampment/endweekly_v2",
        "r3/world/poi/forsaken_manor/endweekly_v2",
        "r3/world/poi/locum_vernatia/endweekly_v2",
        "r3/world/poi/cathedral/endweekly_v2",
        "r3/world/poi/silverstrike_bastille/endweekly_v2",
        "r3/world/poi/terracotta_mine/endweekly_v2",
        "r3/world/poi/starbound_sanctuary/endweekly_v2",
        "r3/world/poi/waterfall_village/endweekly_v2",
        "r3/world/poi/the_nadir/endweekly_v2",
        "r3/world/poi/the_tolumaeus/endweekly_v2",
        "r3/world/poi/vibrant_hollow/endweekly_v2",
        "r3/dungeons/skr/standard_scroll",
        "r3/items/fishing/sand_dollar",
        "r3/items/currency/hyperchromatic_archos_ring",
        "r3/hunts/currency/ruck",
        "items/smart_hopper_workarounds/smart_blast_furnace",
        "items/smart_hopper_workarounds/smart_furnace",
        "items/smart_hopper_workarounds/smart_smoker",
        "r3/items/epics/starblood_ichor",
        "items/armed_armor_stand",
        "items/invisible_item_frame",
        "r2/delves/auxiliary/bonus_tiered",
        "items/arrows/ateoq_arrow",
        "items/arrows/axcanyotl_arrow",
        "items/arrows/tencualac_arrow",
        "astral_checked",
        "r1/items/currency/hyper_experience",
        "r1/items/currency/concentrated_experience",
        "r1/items/currency/experience",
        "r2/items/currency/hyper_crystalline_shard",
        "r2/items/currency/compressed_crystalline_shard",
        "r2/items/currency/crystalline_shard",
        "r3/items/currency/hyperchromatic_archos_ring",
        "r3/items/currency/archos_ring",
        "r1/items/currency/pulsating_gold_bar",
        "r1/items/currency/pulsating_gold",
        "r1/fragments/royal_dust",
        "r1/transmog/rare_frag",
        "r1/items/currency/pulsating_dust",
        "r1/items/currency/pulsating_dust_frag",
        "event/winter2021/blue_ornament",
        "event/winter2021/green_ornament",
        "event/winter2021/red_ornament",
        "event/winter2021/yellow_ornament",
        "event/winter2021/purple_ornament",
        "r2/items/currency/pulsating_emerald_block",
        "r2/items/currency/pulsating_emerald",
        "r2/fragments/gleaming_dust",
        "r2/transmog/rare_frag",
        "r2/transmog/pulsating_powder",
        "r2/transmog/t5_frag",
        "r3/items/currency/pulsating_diamond",
        "r3/items/currency/silver_dust",
        "r3/transmog/melted_candle",
        "r3/items/currency/alacrity_augment",
        "r3/items/currency/fortitude_augment",
        "r3/items/currency/potency_augment",
        "r3/items/currency/pulsating_shard",
        "r3/transmog/pulsating_shard_fragment",
        "r1/items/currency/hyper_experience",
        "r1/items/currency/experience",
        "r1/items/currency/concentrated_experience",
        "r1/items/currency/experience",
        "r1/items/currency/pulsating_gold_bar",
        "r1/fragments/royal_dust",
        "r1/items/currency/pulsating_gold",
        "r1/fragments/royal_dust",
        "r2/items/currency/hyper_crystalline_shard",
        "r2/items/currency/crystalline_shard",
        "r2/items/currency/compressed_crystalline_shard",
        "r2/items/currency/crystalline_shard",
        "r2/items/currency/pulsating_emerald_block",
        "r2/fragments/gleaming_dust",
        "r2/items/currency/pulsating_emerald",
        "r2/fragments/gleaming_dust",
        "r3/items/currency/hyperchromatic_archos_ring",
        "r3/items/currency/archos_ring",
        "r3/items/currency/pulsating_diamond",
        "r3/items/currency/silver_dust",
        "soul/twisted_soul_thread",
        "soul/soul_thread",
        "r2/blackmist/spectral_maradevi",
        "r2/blackmist/spectral_doubloon",
        "r2/items/currency/carnival_ticket_wheel",
        "r2/items/currency/carnival_ticket_bundle",
        "r2/dungeons/rushdown/a_dis_energy",
        "r2/dungeons/rushdown/dis_energy",
        "r3/world/fishing/ring_fish_full",
        "r3/world/fishing/custom_fishing/cache_lesser",
        "r3/world/fishing/custom_fishing/cache_greater_v2",
        "r3/world/fishing/custom_fishing/cache_abyssal1_v2",
        "r3/world/fishing/custom_fishing/cache_abyssal2_v2",
        "r3/items/fishing/fish/ring_fish_greater_weighted",
        "r3/items/fishing/fish/t",
        "r3/world/fishing/custom_fishing/fish/forest_flounder",
        "r3/world/fishing/custom_fishing/fish/forest_flounder_greater",
        "r3/world/fishing/custom_fishing/fish/hexed_salmon",
        "r3/world/fishing/custom_fishing/fish/hexed_salmon_greater",
        "r3/world/fishing/custom_fishing/fish/keep-side_sardine",
        "r3/world/fishing/custom_fishing/fish/keep-side_sardine_greater",
        "r3/world/fishing/custom_fishing/fish/mechanical_monkfish",
        "r3/world/fishing/custom_fishing/fish/mechanical_monkfish_greater",
        "r3/world/fishing/custom_fishing/fish/mungfish",
        "r3/world/fishing/custom_fishing/fish/mungfish_greater",
        "r3/world/fishing/custom_fishing/fish/shade_seabass",
        "r3/world/fishing/custom_fishing/fish/shade_seabass_greater",
        "r3/world/fishing/custom_fishing/fish/shroomfish",
        "r3/world/fishing/custom_fishing/fish/shroomfish_greater",
        "r3/world/fishing/custom_fishing/fish/trout_of_the_architect",
        "r3/world/fishing/custom_fishing/fish/trout_of_the_architect_greater",
        "r3/world/fishing/custom_fishing/fish/wolfswood_carp",
        "r3/world/fishing/custom_fishing/fish/wolfswood_carp_greater",
        "r3/world/fishing/custom_fishing/fish/startouched_swordfish",
        "r3/world/fishing/custom_fishing/fish/startouched_swordfish_greater",
        "r3/world/fishing/custom_fishing/fish/norvigut_tuna",
        "r3/world/fishing/custom_fishing/fish/norvigut_tuna_greater",
        "r3/world/fishing/custom_fishing/fish/crystallized_cod",
        "r3/world/fishing/custom_fishing/fish/crystallized_cod_greater",
        "r1/items/currency/experience",
        "r2/items/currency/crystalline_shard",
        "r3/items/currency/archos_ring",
        "r1/items/alchemists_bag",
        "soul/soul_thread",
        "r1/fragments/kings_fragment",
        "r1/items/currency/chip",
        "r1/dungeons/reverie/corrupted_malevolence",
        "r1/items/currency/experience",
        "r1/items/currency/concentrated_experience",
        "r1/items/currency/hyper_experience",
        "r2/items/currency/crystalline_shard",
        "r2/items/currency/compressed_crystalline_shard",
        "r2/items/currency/hyper_crystalline_shard",
        "r3/items/currency/archos_ring",
        "r3/items/currency/hyperchromatic_archos_ring",
        "r1/items/currency/concentrated_experience",
        "r1/items/currency/pulsating_gold",
        "r2/items/currency/pulsating_emerald",
        "r3/items/currency/pulsating_diamond",
        "r3/items/currency/hyperchromatic_archos_ring",
        "r3/items/currency/pulsating_shard",
        "r3/items/currency/pulsating_diamond",
        "r3/items/currency/fortitude_augment",
        "r3/items/currency/potency_augment",
        "r3/items/currency/alacrity_augment",
        "r3/masterwork/invalid_masterwork_selection",
        "r3/fragments/forest_fragment",
        "r3/items/currency/fenian_flower",
        "r3/fragments/keep_fragment",
        "r3/items/currency/iridium_catalyst",
        "r3/fragments/star_point_fragment",
        "r3/items/currency/dust_of_the_herald",
        "r3/fragments/silver_fragment",
        "r3/items/currency/silver_remnant",
        "r3/fragments/blue_fragment",
        "r3/items/currency/sorceress_stave",
        "r3/fragments/brown_fragment",
        "r3/items/currency/broken_god_gearframe",
        "r3/fragments/companion_fragment",
        "r3/items/currency/corrupted_circuit",
        "r3/fragments/masquerader_fragment",
        "r3/items/currency/shattered_mask",
        "r3/gallery/items/torn_canvas",
        "r3/gallery/map2/deathly_piece_of_eight",
        "r3/items/currency/indigo_blightdust",
        "r3/godspore/items/fungal_remnants",
        "r3/fragments/starblight_fragment",
        "r3/hunts/currency/ruck",
        "r3/items/fishing/sand_dollar",
        "r3/dungeons/skr/silver_memory_fragment",
        "r1/delves/white/auxiliary/delve_material",
        "r1/delves/orange/auxiliary/delve_material",
        "r1/delves/magenta/auxiliary/delve_material",
        "r1/delves/lightblue/auxiliary/delve_material",
        "r1/delves/yellow/auxiliary/delve_material",
        "r1/delves/willows/auxiliary/echoes_of_the_veil",
        "r1/delves/reverie/auxiliary/delve_material",
        "r3/items/currency/godtree_carving",
        "r3/shrine/curse_of_the_dark_soul",
        "r3/shrine/gift_of_the_stars",
        "r1/delves/white/auxiliary/delve_material",
        "r1/delves/orange/auxiliary/delve_material",
        "r1/delves/magenta/auxiliary/delve_material",
        "r1/delves/lightblue/auxiliary/delve_material",
        "r1/delves/yellow/auxiliary/delve_material",
        "r1/delves/willows/auxiliary/echoes_of_the_veil",
        "r1/delves/reverie/auxiliary/delve_material",
        "r1/delves/rogue/persistent_parchment",
        "r2/delves/lime/auxiliary/delve_material",
        "r2/delves/pink/auxiliary/delve_material",
        "r2/delves/gray/auxiliary/delve_material",
        "r2/delves/lightgray/auxiliary/delve_material",
        "r2/delves/cyan/auxiliary/delve_material",
        "r2/delves/purple/auxiliary/delve_material",
        "r2/delves/teal/auxiliary/delve_material",
        "r2/delves/shiftingcity/auxiliary/delve_material",
        "r2/delves/forum/auxiliary/delve_material",
        "r3/items/currency/sorceress_stave",
        "r3/items/currency/broken_god_gearframe",
        "r3/items/currency/silver_remnant",
        "r3/items/currency/fenian_flower",
        "r3/items/currency/iridium_catalyst",
        "r3/items/currency/corrupted_circuit",
        "r3/items/currency/shattered_mask",
        "r3/items/currency/dust_of_the_herald",
        "r3/items/currency/fragrant_branch_of_fen",
        "r3/items/currency/hyperchromatic_archos_ring",
        "r2/depths/loot/voidstained_geode",
        "r3/items/currency/indigo_blightdust",
        "r3/hunts/currency/ruck",
        "r3/hunts/loot/uamiel_unspoiled",
        "r3/hunts/loot/uamiel_spoiled",
        "r3/hunts/loot/experiment_seventy_one_unspoiled",
        "r3/hunts/loot/experiment_seventy_one_spoiled",
        "r3/hunts/loot/steel_wing_hawk_unspoiled",
        "r3/hunts/loot/steel_wing_hawk_spoiled",
        "r3/hunts/loot/aloc_acoc_unspoiled",
        "r3/hunts/loot/aloc_acoc_spoiled",
        "r3/hunts/loot/core_elemental_unspoiled",
        "r3/hunts/loot/core_elemental_spoiled",
        "r3/hunts/loot/the_impenetrable_unspoiled",
        "r3/hunts/loot/the_impenetrable_spoiled",
        "r1/items/misc/repair_anvil",
        "r1/items/currency/circus_ticket",
        "r2/items/currency/carnival_token"
    ]

    visited = set()
    for table in must_keep:
        find_loot_table_refs(table, dst, visited)

    rm_filter(os.path.join(dst, "data/datapacks/base/data/epic/"), list(visited))

def do_redact(dst):
    redact_loot_tables(dst)
    shutil.rmtree(os.path.join(dst, "data/datapacks/base/data/monumenta/"))
    os.remove(os.path.join(dst, "data/plugins/all/LibraryOfSouls/soul_pools_database.json"))
    os.remove(os.path.join(dst, "data/plugins/all/LibraryOfSouls/soul_parties_database.json"))

    with open(os.path.join(dst, "data/plugins/all/LibraryOfSouls/souls_database.json"), "w") as f:
        f.write('{"souls":[],"data_version": 3700}')

def main():
    if not Path(os.path.join(os.getcwd(), "server_config")).exists():
        os.makedirs(os.path.join(os.getcwd(), "server_config"), exist_ok=True)

    src = os.path.expanduser("~/project_epic/server_config")
    dst = os.path.expanduser(os.path.join(os.getcwd(), "server_config"))

    jar_dir = [
        ".",
        "plugins",
        "mods"
    ]
    jar_exclude = [
        "velocity-prometheus-exporter.jar",
        "prometheus-exporter.jar",
        "AxiomPaper.jar",
        "Plan.jar",
        "PremiumVanish.jar",
        "HeadDatabase.jar",
        "LiteBans.jar",
        "Arceon.jar",
        "MetaBrushes.jar",
        "MetaEdits.jar"
    ]

    for dir in jar_dir:
        p = os.path.join(dst, dir)
        if not Path(p).exists():
            print(f"Creating {p}")
            os.makedirs(p, exist_ok=True)

        for jar in list(Path(os.path.join(src, dir)).glob("*.jar")):
            if not (any(c.isdigit() for c in jar.name) or jar.name in jar_exclude):
                shutil.copy(jar, p)
                print(jar.name)

    for dir in [p for p in Path(os.path.join(src, "plugins")).iterdir() if p.is_dir()]:
        p = os.path.join(dst, "plugins", dir.name)
        if not Path(p).exists():
            print(f"Creating {p}")
            os.makedirs(p, exist_ok=True)
        shutil.copytree(
            os.path.join(src, "plugins", dir.name),
            os.path.join(dst, "plugins", dir.name),
            dirs_exist_ok=True
        )

    data_include = [
        "server_config_template"
    ]

    if not Path(os.path.join(dst, "data")).exists():
        os.makedirs(os.path.join(dst, "data"), exist_ok=True)

    for item in data_include:
        shutil.copytree(
            os.path.join(src, "data", item),
            os.path.join(dst, "data", item),
            dirs_exist_ok=True
        )
        print(item)

    data_plugins_all_include = [
        "dynmap",
        "LibraryOfSouls",
        "Monumenta",
        "ChestSort",
        "MonumentaNetworkChat",
    ]

    if not Path(os.path.join(dst, "data/plugins/all")).exists():
        os.makedirs(os.path.join(dst, "data/plugins/all"), exist_ok=True)

    for item in data_plugins_all_include:
        shutil.copytree(
            os.path.join(src, "data/plugins/all", item),
            os.path.join(dst, "data/plugins/all", item),
            dirs_exist_ok=True
        )
        print(item)

    data_datapacks_include = [
        "base",
        "bukkit",
        "vanilla"
    ]

    if not Path(os.path.join(dst, "data/datapacks")).exists():
        os.makedirs(os.path.join(dst, "data/datapacks"), exist_ok=True)

    for item in data_datapacks_include:
        shutil.copytree(
            os.path.join(src, "data/datapacks", item),
            os.path.join(dst, "data/datapacks", item),
            dirs_exist_ok=True
        )
        print(item)

    data_plugins_proxy_include = [
        "litebans",
        "monumenta-network-relay",
        "monumenta-redisapi",
        "monumenta-velocity",
        "nuvotifier",
        "premiumvanish"
    ]

    if not Path(os.path.join(dst, "data/plugins/proxy")).exists():
        os.makedirs(os.path.join(dst, "data/plugins/proxy"), exist_ok=True)

    for item in data_plugins_proxy_include:
        shutil.copytree(
            os.path.join(src, "data/plugins/proxy", item),
            os.path.join(dst, "data/plugins/proxy", item),
            dirs_exist_ok=True
        )
        print(item)

    if not Path(os.path.join(dst, "data/generated")).exists():
        os.makedirs(os.path.join(dst, "data/generated"), exist_ok=True)

    # postprocess filter
    removed_dirs = [
        "plugins/1_19_4_staging",
        "plugins/LuckPerms/build/libs",
        "plugins/LuckPerms/play/libs"
    ]

    for item in removed_dirs:
        shutil.rmtree(os.path.join(dst, item))

    files_to_yoink = [
        ("data/plugins/dev1/Monumenta/properties/LocalProperties.json", "data/plugins/sdk1/Monumenta/properties/LocalProperties.json"),
        ("data/plugins/dev2/Monumenta/properties/LocalProperties.json", "data/plugins/sdk2/Monumenta/properties/LocalProperties.json")
    ]

    for (srcFrag, destFrag) in files_to_yoink:
        dstPath = Path(os.path.join(dst, destFrag))
        os.makedirs(dstPath.parent.absolute(), exist_ok=True)
        shutil.copy2(os.path.join(src, srcFrag), dstPath.absolute())

    do_redact(dst)

if __name__ == "__main__":
    main()
