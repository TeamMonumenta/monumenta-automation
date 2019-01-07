#!/usr/bin/env python3

import os
import sys
import traceback
import json
import pprint

from lib_py3.json_file import jsonFile
from lib_py3.common import eprint
from lib_py3.common import remove_formatting
from lib_py3.loot_table_manager import LootTableManager
from lib_py3.world import World

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt


mgr = LootTableManager()

# AUTOFORMAT
#mgr.autoformat_json_files_in_directory("/home/rock/project_epic/server_config/data/datapacks", indent=4)
#mgr.autoformat_json_files_in_directory("/home/rock/project_epic/server_config/data/scriptedquests", indent=2)
#sys.exit(0)

mgr.load_loot_tables_subdirectories("/home/rock/project_epic/server_config/data/datapacks")
mgr.load_advancements_subdirectories("/home/rock/project_epic/server_config/data/datapacks")
mgr.load_functions_subdirectories("/home/rock/project_epic/server_config/data/datapacks")
mgr.load_scripted_quests_directory("/home/rock/project_epic/server_config/data/scriptedquests")
#mgr.load_world(World("/home/rock/MCEdit-And-Automation/utility_code/Project_Epic-mobs"))
#mgr.load_world(World("/home/rock/project_epic/mobs/Project_Epic-mobs"))
#mgr.load_world(World("/home/rock/project_epic/region_1/Project_Epic-region_1"))

invalid_references = mgr.get_invalid_loot_table_references()
if len(invalid_references.keys()) > 0:
    print("\033[1;31m", end="")
    print("ERROR! Invalid references found!")
    pprint.pprint(invalid_references)
    print("\033[0;0m")

sys.exit(0)



#replacements = mgr.get_as_replacements()
#pprint.pprint(mgr.table_map)
#pprint.pprint(replacements)

#item_id = "minecraft:fishing_rod"
#item_nbt = r'''{Enchantments:[{lvl:3s,id:"lure"},{lvl:2s,id:"unbreaking"}],display:{Lore:["§8King's Valley : Tier III"],Name:"{\"text\":\"§fAngler's Rod\"}"}}'''
#mgr.update_item_in_loot_tables(item_id, nbt.TagCompound.from_mojangson(item_nbt))

renameraw = '''
datapacks/region_1/data/epic/loot_tables/items/r1/races/cloak.json -> datapacks/region_1/data/epic/loot_tables/r1/items/races/cloak.json
datapacks/region_1/data/epic/loot_tables/items/r1/races/cxp.json -> datapacks/region_1/data/epic/loot_tables/r1/items/races/cxp.json
datapacks/region_1/data/epic/loot_tables/items/r1/races/doll.json -> datapacks/region_1/data/epic/loot_tables/r1/items/races/doll.json
datapacks/region_1/data/epic/loot_tables/items/r1/races/fishfin.json -> datapacks/region_1/data/epic/loot_tables/r1/items/races/fishfin.json
datapacks/region_1/data/epic/loot_tables/items/r1/races/primordialhelm.json -> datapacks/region_1/data/epic/loot_tables/r1/items/races/primordialhelm.json
datapacks/region_1/data/epic/loot_tables/items/r1/races/speedleaf.json -> datapacks/region_1/data/epic/loot_tables/r1/items/races/speedleaf.json
datapacks/region_1/data/epic/loot_tables/items/r1/races/speedleafhelm.json -> datapacks/region_1/data/epic/loot_tables/r1/items/races/speedleafhelm.json
datapacks/region_1/data/epic/loot_tables/items/r1/races/swimmingshoes.json -> datapacks/region_1/data/epic/loot_tables/r1/items/races/swimmingshoes.json

datapacks/base/data/epic/loot_tables/loot/filler_d1.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/1/filler.json
datapacks/base/data/epic/loot_tables/loot/items_d1.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/1/items.json
datapacks/base/data/epic/loot_tables/loot/rares_d1.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/1/rares.json
datapacks/base/data/epic/loot_tables/loot/filler_d2.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/2/filler.json
datapacks/base/data/epic/loot_tables/loot/items_d2.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/2/items.json
datapacks/base/data/epic/loot_tables/loot/rares_d2.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/2/rares.json
datapacks/base/data/epic/loot_tables/loot/filler_d3.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/3/filler.json
datapacks/base/data/epic/loot_tables/loot/items_d3.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/3/items.json
datapacks/base/data/epic/loot_tables/loot/rares_d3.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/3/rares.json
datapacks/base/data/epic/loot_tables/loot/filler_d4a.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/4/filler_a.json
datapacks/base/data/epic/loot_tables/loot/filler_d4u.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/4/filler_u.json
datapacks/base/data/epic/loot_tables/loot/items_d4a.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/4/items_a.json
datapacks/base/data/epic/loot_tables/loot/items_d4u.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/4/items_u.json
datapacks/base/data/epic/loot_tables/loot/rares_d4.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/4/rares.json
datapacks/base/data/epic/loot_tables/loot/filler_bonus.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/bonus/filler.json
datapacks/base/data/epic/loot_tables/loot/rares_bonus.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/bonus/rares.json
datapacks/base/data/epic/loot_tables/loot/filler_d0.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/oldlabs/filler.json
datapacks/base/data/epic/loot_tables/loot/items_0.json -> datapacks/base/data/epic/loot_tables/r1/world/sets/items_0.json
datapacks/base/data/epic/loot_tables/loot/items_1.json -> datapacks/base/data/epic/loot_tables/r1/world/sets/items_1.json
datapacks/base/data/epic/loot_tables/loot/items_2.json -> datapacks/base/data/epic/loot_tables/r1/world/sets/items_2.json
datapacks/base/data/epic/loot_tables/loot/items_3.json -> datapacks/base/data/epic/loot_tables/r1/world/sets/items_3.json
datapacks/base/data/epic/loot_tables/loot/items_4.json -> datapacks/base/data/epic/loot_tables/r1/world/sets/items_4.json
datapacks/base/data/epic/loot_tables/loot/items_5.json -> datapacks/base/data/epic/loot_tables/r1/world/sets/items_5.json
datapacks/base/data/epic/loot_tables/loot/money_0.json -> datapacks/base/data/epic/loot_tables/r1/world/sets/money_0.json
datapacks/base/data/epic/loot_tables/loot/money_1.json -> datapacks/base/data/epic/loot_tables/r1/world/sets/money_1.json
datapacks/base/data/epic/loot_tables/loot/money_2.json -> datapacks/base/data/epic/loot_tables/r1/world/sets/money_2.json
datapacks/base/data/epic/loot_tables/loot/money_3.json -> datapacks/base/data/epic/loot_tables/r1/world/sets/money_3.json
datapacks/base/data/epic/loot_tables/loot/money_4.json -> datapacks/base/data/epic/loot_tables/r1/world/sets/money_4.json
datapacks/base/data/epic/loot_tables/loot/money_5.json -> datapacks/base/data/epic/loot_tables/r1/world/sets/money_5.json

datapacks/base/data/epic/loot_tables/quests/r1/quest01_jeweled_tiara.json -> datapacks/base/data/epic/loot_tables/r1/quests/01_jeweled_tiara.json
datapacks/base/data/epic/loot_tables/quests/r1/quest01_topaz_cap.json -> datapacks/base/data/epic/loot_tables/r1/quests/01_topaz_cap.json
datapacks/base/data/epic/loot_tables/quests/r1/quest02_watchers_sword.json -> datapacks/base/data/epic/loot_tables/r1/quests/02_watchers_sword.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest04_claystaff.json -> datapacks/base/data/epic/loot_tables/r1/quests/04_claystaff.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest04_elementalstaff.json -> datapacks/base/data/epic/loot_tables/r1/quests/04_elementalstaff.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest04_mudstaff.json -> datapacks/base/data/epic/loot_tables/r1/quests/04_mudstaff.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest04_waterstaff.json -> datapacks/base/data/epic/loot_tables/r1/quests/04_waterstaff.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest05_hollowed_gladius.json -> datapacks/base/data/epic/loot_tables/r1/quests/05_hollowed_gladius.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest05_key.json -> datapacks/base/data/epic/loot_tables/r1/quests/05_key.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest05_xp.json -> datapacks/base/data/epic/loot_tables/r1/quests/05_xp.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest06_steelsiege.json -> datapacks/base/data/epic/loot_tables/r1/quests/06_steelsiege.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest07_give_medicine_and_elixirs.json -> datapacks/base/data/epic/loot_tables/r1/quests/07_give_medicine_and_elixirs.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest07_give_medicine_minus_elixir.json -> datapacks/base/data/epic/loot_tables/r1/quests/07_give_medicine_minus_elixir.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest07_give_medicine_only.json -> datapacks/base/data/epic/loot_tables/r1/quests/07_give_medicine_only.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest07_rewards.json -> datapacks/base/data/epic/loot_tables/r1/quests/07_rewards.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest08_water_robe.json -> datapacks/base/data/epic/loot_tables/r1/quests/08_water_robe.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest09_rewards.json -> datapacks/base/data/epic/loot_tables/r1/quests/09_rewards.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest10_rewards.json -> datapacks/base/data/epic/loot_tables/r1/quests/10_rewards.json
datapacks/base/data/epic/loot_tables/quests/r1/quest11_monks_robe.json -> datapacks/base/data/epic/loot_tables/r1/quests/11_monks_robe.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest13_highstorm.json -> datapacks/base/data/epic/loot_tables/r1/quests/13_highstorm.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest14_scalawags_hatchet.json -> datapacks/base/data/epic/loot_tables/r1/quests/14_scalawags_hatchet.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest15_compensation.json -> datapacks/base/data/epic/loot_tables/r1/quests/15_compensation.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest15_rewards.json -> datapacks/base/data/epic/loot_tables/r1/quests/15_rewards.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest15_telescope.json -> datapacks/base/data/epic/loot_tables/r1/quests/15_telescope.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest16_rewards.json -> datapacks/base/data/epic/loot_tables/r1/quests/16_rewards.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest16_salmon.json -> datapacks/base/data/epic/loot_tables/r1/quests/16_salmon.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest17_chefs_knife.json -> datapacks/base/data/epic/loot_tables/r1/quests/17_chefs_knife.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest18_umbral_robe.json -> datapacks/base/data/epic/loot_tables/r1/quests/18_umbral_robe.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest19_nelfinebook.json -> datapacks/base/data/epic/loot_tables/r1/quests/19_nelfinebook.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest19_rewards.json -> datapacks/base/data/epic/loot_tables/r1/quests/19_rewards.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest20_runners_boots.json -> datapacks/base/data/epic/loot_tables/r1/quests/20_runners_boots.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest22_rewards.json -> datapacks/base/data/epic/loot_tables/r1/quests/22_rewards.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest23_inertbottle.json -> datapacks/base/data/epic/loot_tables/r1/quests/23_inertbottle.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest23_sensor.json -> datapacks/base/data/epic/loot_tables/r1/quests/23_sensor.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest23_vargosbook.json -> datapacks/base/data/epic/loot_tables/r1/quests/23_vargosbook.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest24_dreadfulmemory.json -> datapacks/base/data/epic/loot_tables/r1/quests/24_dreadfulmemory.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest24_glassdagger.json -> datapacks/base/data/epic/loot_tables/r1/quests/24_glassdagger.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest24_inspiredmemory.json -> datapacks/base/data/epic/loot_tables/r1/quests/24_inspiredmemory.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest24_lettertoarian.json -> datapacks/base/data/epic/loot_tables/r1/quests/24_lettertoarian.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest24_miraculous.json -> datapacks/base/data/epic/loot_tables/r1/quests/24_miraculous.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest24_sorrowfulmemory.json -> datapacks/base/data/epic/loot_tables/r1/quests/24_sorrowfulmemory.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest25_rewards.json -> datapacks/base/data/epic/loot_tables/r1/quests/25_rewards.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest25_thegenerals.json -> datapacks/base/data/epic/loot_tables/r1/quests/25_thegenerals.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest26_lense3.json -> datapacks/base/data/epic/loot_tables/r1/quests/26_lense3.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest26_rewards.json -> datapacks/base/data/epic/loot_tables/r1/quests/26_rewards.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest27_rewards.json -> datapacks/base/data/epic/loot_tables/r1/quests/27_rewards.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest29_crackedcrystal.json -> datapacks/base/data/epic/loot_tables/r1/quests/29_crackedcrystal.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest29_healingcrystal.json -> datapacks/base/data/epic/loot_tables/r1/quests/29_healingcrystal.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest29_purecrystal.json -> datapacks/base/data/epic/loot_tables/r1/quests/29_purecrystal.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest29_rewards.json -> datapacks/base/data/epic/loot_tables/r1/quests/29_rewards.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest30_rewards.json -> datapacks/base/data/epic/loot_tables/r1/quests/30_rewards.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest31_sea_legs.json -> datapacks/base/data/epic/loot_tables/r1/quests/31_sea_legs.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest32_rewards.json -> datapacks/base/data/epic/loot_tables/r1/quests/32_rewards.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest32_temporal_crystal.json -> datapacks/base/data/epic/loot_tables/r1/quests/32_temporal_crystal.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest35_full_supply.json -> datapacks/base/data/epic/loot_tables/r1/quests/35_full_supply.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest35_icechest.json -> datapacks/base/data/epic/loot_tables/r1/quests/35_icechest.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest35_reciept.json -> datapacks/base/data/epic/loot_tables/r1/quests/35_reciept.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest35_rewards.json -> datapacks/base/data/epic/loot_tables/r1/quests/35_rewards.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest37_rewards.json -> datapacks/base/data/epic/loot_tables/r1/quests/37_rewards.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest39_hawk.json -> datapacks/base/data/epic/loot_tables/r1/quests/39_hawk.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest39_jaguar.json -> datapacks/base/data/epic/loot_tables/r1/quests/39_jaguar.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest39_serpant.json -> datapacks/base/data/epic/loot_tables/r1/quests/39_serpant.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest40_book.json -> datapacks/base/data/epic/loot_tables/r1/quests/40_book.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest40_reward.json -> datapacks/base/data/epic/loot_tables/r1/quests/40_reward.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest43_crutches.json -> datapacks/base/data/epic/loot_tables/r1/quests/43_crutches.json
datapacks/region_1/data/epic/loot_tables/quests/r1/quest43_reward.json -> datapacks/base/data/epic/loot_tables/r1/quests/43_reward.json
datapacks/region_1/data/epic/loot_tables/quests/r1/hellpactritual.json -> datapacks/base/data/epic/loot_tables/r1/quests/hellpactritual.json
datapacks/region_1/data/epic/loot_tables/quests/r1/tutorial_money.json -> datapacks/base/data/epic/loot_tables/r1/quests/tutorial_money.json
datapacks/region_1/data/epic/loot_tables/quests/r1/tutorial_murano.json -> datapacks/base/data/epic/loot_tables/r1/quests/tutorial_murano.json

datapacks/region_1/data/epic/loot_tables/r1/items/races/cloak.json -> datapacks/base/data/epic/loot_tables/r1/races/cloak.json
datapacks/region_1/data/epic/loot_tables/r1/items/races/cxp.json -> datapacks/base/data/epic/loot_tables/r1/races/cxp.json
datapacks/region_1/data/epic/loot_tables/r1/items/races/doll.json -> datapacks/base/data/epic/loot_tables/r1/races/doll.json
datapacks/region_1/data/epic/loot_tables/r1/items/races/fishfin.json -> datapacks/base/data/epic/loot_tables/r1/races/fishfin.json
datapacks/region_1/data/epic/loot_tables/r1/items/races/primordialhelm.json -> datapacks/base/data/epic/loot_tables/r1/races/primordialhelm.json
datapacks/region_1/data/epic/loot_tables/r1/items/races/speedleaf.json -> datapacks/base/data/epic/loot_tables/r1/races/speedleaf.json
datapacks/region_1/data/epic/loot_tables/r1/items/races/speedleafhelm.json -> datapacks/base/data/epic/loot_tables/r1/races/speedleafhelm.json
datapacks/region_1/data/epic/loot_tables/r1/items/races/swimmingshoes.json -> datapacks/base/data/epic/loot_tables/r1/races/swimmingshoes.json
datapacks/region_2/data/epic/loot_tables/quests/r2/quest103a_reward.json -> datapacks/base/data/epic/loot_tables/r2/quests/103a_reward.json
datapacks/region_2/data/epic/loot_tables/quests/r2/quest103a_sigil.json -> datapacks/base/data/epic/loot_tables/r2/quests/103a_sigil.json

datapacks/base/data/epic/loot_tables/loot/slot_0.json -> datapacks/base/data/epic/loot_tables/r1/casino/slot_0.json
datapacks/base/data/epic/loot_tables/loot/slot_1.json -> datapacks/base/data/epic/loot_tables/r1/casino/slot_1.json
datapacks/base/data/epic/loot_tables/loot/slot_2.json -> datapacks/base/data/epic/loot_tables/r1/casino/slot_2.json
datapacks/base/data/epic/loot_tables/loot/slot_3.json -> datapacks/base/data/epic/loot_tables/r1/casino/slot_3.json
datapacks/base/data/epic/loot_tables/loot/slot_4.json -> datapacks/base/data/epic/loot_tables/r1/casino/slot_4.json
datapacks/base/data/monumenta/loot_tables/loot2/filler/filler_dcanyon.json -> datapacks/base/data/epic/loot_tables/r2/world/filler/desert/canyon.json
datapacks/base/data/monumenta/loot_tables/loot2/filler/filler_ddesert.json -> datapacks/base/data/epic/loot_tables/r2/world/filler/desert/desert.json
datapacks/base/data/monumenta/loot_tables/loot2/filler/filler_dfire.json -> datapacks/base/data/epic/loot_tables/r2/world/filler/desert/fire.json
datapacks/base/data/monumenta/loot_tables/loot2/filler/filler_dmagic.json -> datapacks/base/data/epic/loot_tables/r2/world/filler/desert/magic.json
datapacks/base/data/monumenta/loot_tables/loot2/filler/filler_dmesa.json -> datapacks/base/data/epic/loot_tables/r2/world/filler/desert/mesa.json
datapacks/base/data/monumenta/loot_tables/loot2/filler/filler_vbeach.json -> datapacks/base/data/epic/loot_tables/r2/world/filler/isles/beach.json
datapacks/base/data/monumenta/loot_tables/loot2/filler/filler_vreef.json -> datapacks/base/data/epic/loot_tables/r2/world/filler/isles/reef.json
datapacks/base/data/monumenta/loot_tables/loot2/filler/filler_vruins.json -> datapacks/base/data/epic/loot_tables/r2/world/filler/isles/ruins.json
datapacks/base/data/monumenta/loot_tables/loot2/filler/filler_vship.json -> datapacks/base/data/epic/loot_tables/r2/world/filler/isles/ship.json
datapacks/base/data/monumenta/loot_tables/loot2/filler/filler_vtemple.json -> datapacks/base/data/epic/loot_tables/r2/world/filler/isles/temple.json
datapacks/base/data/monumenta/loot_tables/loot2/filler/filler_tfrost.json -> datapacks/base/data/epic/loot_tables/r2/world/filler/tundra/frost.json
datapacks/base/data/monumenta/loot_tables/loot2/filler/filler_tmagic.json -> datapacks/base/data/epic/loot_tables/r2/world/filler/tundra/magic.json
datapacks/base/data/monumenta/loot_tables/loot2/filler/filler_tmountain.json -> datapacks/base/data/epic/loot_tables/r2/world/filler/tundra/mountain.json
datapacks/base/data/monumenta/loot_tables/loot2/filler/filler_truins.json -> datapacks/base/data/epic/loot_tables/r2/world/filler/tundra/ruins.json
datapacks/base/data/monumenta/loot_tables/loot2/filler/filler_ttundra.json -> datapacks/base/data/epic/loot_tables/r2/world/filler/tundra/tundra.json
datapacks/base/data/monumenta/loot_tables/loot2/level_1_dgeneric.json -> datapacks/base/data/epic/loot_tables/r2/world/generic_chests/level_1.json
datapacks/base/data/monumenta/loot_tables/loot2/level_2_dgeneric.json -> datapacks/base/data/epic/loot_tables/r2/world/generic_chests/level_2.json
datapacks/base/data/monumenta/loot_tables/loot2/level_3_dgeneric.json -> datapacks/base/data/epic/loot_tables/r2/world/generic_chests/level_3.json
datapacks/base/data/monumenta/loot_tables/loot2/level_4_dgeneric.json -> datapacks/base/data/epic/loot_tables/r2/world/generic_chests/level_4.json
datapacks/base/data/monumenta/loot_tables/loot2/level_5_dgeneric.json -> datapacks/base/data/epic/loot_tables/r2/world/generic_chests/level_5.json
datapacks/base/data/monumenta/loot_tables/loot2/level_1_tgeneric.json -> datapacks/base/data/epic/loot_tables/r2/world/generic_chests/level_1.json
datapacks/base/data/monumenta/loot_tables/loot2/level_1_vgeneric.json -> datapacks/base/data/epic/loot_tables/r2/world/generic_chests/level_1.json
datapacks/base/data/monumenta/loot_tables/loot2/level_2_tgeneric.json -> datapacks/base/data/epic/loot_tables/r2/world/generic_chests/level_2.json
datapacks/base/data/monumenta/loot_tables/loot2/level_2_vgeneric.json -> datapacks/base/data/epic/loot_tables/r2/world/generic_chests/level_2.json
datapacks/base/data/monumenta/loot_tables/loot2/level_3_tgeneric.json -> datapacks/base/data/epic/loot_tables/r2/world/generic_chests/level_3.json
datapacks/base/data/monumenta/loot_tables/loot2/level_3_vgeneric.json -> datapacks/base/data/epic/loot_tables/r2/world/generic_chests/level_3.json
datapacks/base/data/monumenta/loot_tables/loot2/level_4_tgeneric.json -> datapacks/base/data/epic/loot_tables/r2/world/generic_chests/level_4.json
datapacks/base/data/monumenta/loot_tables/loot2/level_4_vgeneric.json -> datapacks/base/data/epic/loot_tables/r2/world/generic_chests/level_4.json
datapacks/base/data/monumenta/loot_tables/loot2/level_5_tgeneric.json -> datapacks/base/data/epic/loot_tables/r2/world/generic_chests/level_5.json
datapacks/base/data/monumenta/loot_tables/loot2/level_5_vgeneric.json -> datapacks/base/data/epic/loot_tables/r2/world/generic_chests/level_5.json

data/monumenta/loot_tables/loot2/money/crystalline_shard.json -> data/epic/loot_tables/r2/items/crystalline_shard.json
data/monumenta/loot_tables/loot2/money/enchanted_crystalline_shard.json -> data/epic/loot_tables/r2/items/enchanted_crystalline_shard.json
data/monumenta/loot_tables/loot2/money/r2money_1.json -> data/epic/loot_tables/r2/world/sets/money_1.json
data/monumenta/loot_tables/loot2/money/r2money_2.json -> data/epic/loot_tables/r2/world/sets/money_2.json
data/monumenta/loot_tables/loot2/money/r2money_3.json -> data/epic/loot_tables/r2/world/sets/money_3.json
data/monumenta/loot_tables/loot2/money/r2money_4.json -> data/epic/loot_tables/r2/world/sets/money_4.json
data/monumenta/loot_tables/loot2/money/r2money_5.json -> data/epic/loot_tables/r2/world/sets/money_5.json
data/monumenta/loot_tables/loot2/gear/rare_1_r2.json -> data/epic/loot_tables/r2/world/sets/rares.json

datapacks/base/data/epic/loot_tables/loot/level_1_generic.json -> datapacks/base/data/epic/loot_tables/r1/world/collections/level_1.json
datapacks/base/data/epic/loot_tables/loot/level_2_generic.json -> datapacks/base/data/epic/loot_tables/r1/world/collections/level_2.json
datapacks/base/data/epic/loot_tables/loot/level_3_generic.json -> datapacks/base/data/epic/loot_tables/r1/world/collections/level_3.json
datapacks/base/data/epic/loot_tables/loot/level_4_generic.json -> datapacks/base/data/epic/loot_tables/r1/world/collections/level_4.json
datapacks/base/data/epic/loot_tables/loot/level_5_generic.json -> datapacks/base/data/epic/loot_tables/r1/world/collections/level_5.json
datapacks/base/data/epic/loot_tables/r1/world/sets/money_0.json -> datapacks/base/data/epic/loot_tables/r1/world/collections/money_0.json
datapacks/base/data/epic/loot_tables/r1/world/sets/money_1.json -> datapacks/base/data/epic/loot_tables/r1/world/collections/money_1.json
datapacks/base/data/epic/loot_tables/r1/world/sets/money_2.json -> datapacks/base/data/epic/loot_tables/r1/world/collections/money_2.json
datapacks/base/data/epic/loot_tables/r1/world/sets/money_3.json -> datapacks/base/data/epic/loot_tables/r1/world/collections/money_3.json
datapacks/base/data/epic/loot_tables/r1/world/sets/money_4.json -> datapacks/base/data/epic/loot_tables/r1/world/collections/money_4.json
datapacks/base/data/epic/loot_tables/r1/world/sets/money_5.json -> datapacks/base/data/epic/loot_tables/r1/world/collections/money_5.json
datapacks/base/data/epic/loot_tables/r2/world/generic_chests/level_1.json -> datapacks/base/data/epic/loot_tables/r2/world/collections/level_1.json
datapacks/base/data/epic/loot_tables/r2/world/generic_chests/level_2.json -> datapacks/base/data/epic/loot_tables/r2/world/collections/level_2.json
datapacks/base/data/epic/loot_tables/r2/world/generic_chests/level_3.json -> datapacks/base/data/epic/loot_tables/r2/world/collections/level_3.json
datapacks/base/data/epic/loot_tables/r2/world/generic_chests/level_4.json -> datapacks/base/data/epic/loot_tables/r2/world/collections/level_4.json
datapacks/base/data/epic/loot_tables/r2/world/generic_chests/level_5.json -> datapacks/base/data/epic/loot_tables/r2/world/collections/level_5.json
datapacks/base/data/epic/loot_tables/r2/world/sets/money_1.json -> datapacks/base/data/epic/loot_tables/r2/world/collections/money_1.json
datapacks/base/data/epic/loot_tables/r2/world/sets/money_2.json -> datapacks/base/data/epic/loot_tables/r2/world/collections/money_2.json
datapacks/base/data/epic/loot_tables/r2/world/sets/money_3.json -> datapacks/base/data/epic/loot_tables/r2/world/collections/money_3.json
datapacks/base/data/epic/loot_tables/r2/world/sets/money_4.json -> datapacks/base/data/epic/loot_tables/r2/world/collections/money_4.json
datapacks/base/data/epic/loot_tables/r2/world/sets/money_5.json -> datapacks/base/data/epic/loot_tables/r2/world/collections/money_5.json

minigames/loot_tables/arena/blaze.json -> epic/loot_tables/r1/arena_of_terth/blaze.json
minigames/loot_tables/arena/firstboss.json -> epic/loot_tables/r1/arena_of_terth/firstboss.json
minigames/loot_tables/arena/glowstone.json -> epic/loot_tables/r1/arena_of_terth/glowstone.json
minigames/loot_tables/arena/miniboss.json -> epic/loot_tables/r1/arena_of_terth/miniboss.json
minigames/loot_tables/arena/soul.json -> epic/loot_tables/r1/arena_of_terth/soul.json

datapacks/base/data/epic/loot_tables/items/r1/adventure_crystal.json -> datapacks/base/data/epic/loot_tables/r1/items/currency/adventure_crystal.json
datapacks/base/data/epic/loot_tables/items/r1/concentrated_experience.json -> datapacks/base/data/epic/loot_tables/r1/items/currency/concentrated_experience.json
datapacks/base/data/epic/loot_tables/loot/dust.json -> datapacks/base/data/epic/loot_tables/r1/items/currency/pulsating_dust.json
datapacks/base/data/epic/loot_tables/items/r1/mechanisms/pulsating_gold.json -> datapacks/base/data/epic/loot_tables/r1/items/currency/pulsating_gold.json
datapacks/base/data/epic/loot_tables/items/r1/royal_crystal.json -> datapacks/base/data/epic/loot_tables/r1/items/currency/royal_crystal.json
datapacks/base/data/epic/loot_tables/items/r1/roguelike/records/deepest_blues.json -> datapacks/base/data/epic/loot_tables/r1/items/roguelike/deepest_blues.json
datapacks/base/data/epic/loot_tables/items/r1/roguelike/records/embalmers_mixtape.json -> datapacks/base/data/epic/loot_tables/r1/items/roguelike/embalmers_mixtape.json
datapacks/base/data/epic/loot_tables/items/r1/roguelike/records/ethereal_expressions.json -> datapacks/base/data/epic/loot_tables/r1/items/roguelike/ethereal_expressions.json
datapacks/base/data/epic/loot_tables/items/r1/roguelike/records/obsidian_hits.json -> datapacks/base/data/epic/loot_tables/r1/items/roguelike/obsidian_hits.json
datapacks/base/data/epic/loot_tables/items/r1/roguelike/records/sandy_smooth_jazz.json -> datapacks/base/data/epic/loot_tables/r1/items/roguelike/sandy_smooth_jazz.json
datapacks/base/data/epic/loot_tables/items/r1/roguelike/records/web_covered_classics.json -> datapacks/base/data/epic/loot_tables/r1/items/roguelike/web_covered_classics.json

datapacks/base/data/epic/loot_tables/items/r1/event/aprilfools2018/thank_you_note.json -> datapacks/base/data/epic/loot_tables/event/aprilfools2018/thank_you_note.json
datapacks/base/data/epic/loot_tables/loot/events/easterchest.json -> datapacks/base/data/epic/loot_tables/event/easter_chest_2018.json
datapacks/base/data/epic/loot_tables/items/r1/event/ebola_shirt.json -> datapacks/base/data/epic/loot_tables/event/ebola_shirt.json
datapacks/base/data/epic/loot_tables/items/r1/event/halloween2017/plague_bearers_boots.json -> datapacks/base/data/epic/loot_tables/event/halloween2017/plague_bearers_boots.json
datapacks/base/data/epic/loot_tables/items/r1/event/halloween2017/plague_bearers_head.json -> datapacks/base/data/epic/loot_tables/event/halloween2017/plague_bearers_head.json
datapacks/base/data/epic/loot_tables/items/r1/event/halloween2017/plague_bearers_soiled_trousers.json -> datapacks/base/data/epic/loot_tables/event/halloween2017/plague_bearers_soiled_trousers.json
datapacks/base/data/epic/loot_tables/items/r1/event/halloween2017/plague_bearers_tunic.json -> datapacks/base/data/epic/loot_tables/event/halloween2017/plague_bearers_tunic.json
datapacks/base/data/epic/loot_tables/items/r1/event/halloween2017/pumpkin_spythe.json -> datapacks/base/data/epic/loot_tables/event/halloween2017/pumpkin_spythe.json
datapacks/base/data/epic/loot_tables/items/r1/event/valentines2018/items/banner_of_love.json -> datapacks/base/data/epic/loot_tables/event/valentines2018/banner_of_love.json
datapacks/base/data/epic/loot_tables/items/r1/event/valentines2018/items/cloud_nine_token.json -> datapacks/base/data/epic/loot_tables/event/valentines2018/cloud_nine_token.json
datapacks/base/data/epic/loot_tables/items/r1/event/valentines2018/items/cupid.json -> datapacks/base/data/epic/loot_tables/event/valentines2018/cupid.json
datapacks/base/data/epic/loot_tables/items/r1/event/valentines2018/items/essence_of_devotion.json -> datapacks/base/data/epic/loot_tables/event/valentines2018/essence_of_devotion.json
datapacks/base/data/epic/loot_tables/items/r1/event/valentines2018/items/essence_of_love.json -> datapacks/base/data/epic/loot_tables/event/valentines2018/essence_of_love.json
datapacks/base/data/epic/loot_tables/items/r1/event/valentines2018/items/essence_of_passion.json -> datapacks/base/data/epic/loot_tables/event/valentines2018/essence_of_passion.json
datapacks/base/data/epic/loot_tables/items/r1/event/valentines2018/items/essence_of_romance.json -> datapacks/base/data/epic/loot_tables/event/valentines2018/essence_of_romance.json
datapacks/base/data/epic/loot_tables/items/r1/event/valentines2018/items/essence_of_yearning.json -> datapacks/base/data/epic/loot_tables/event/valentines2018/essence_of_yearning.json
datapacks/base/data/epic/loot_tables/items/r1/event/valentines2018/items/happy_heart_potion.json -> datapacks/base/data/epic/loot_tables/event/valentines2018/happy_heart_potion.json
datapacks/base/data/epic/loot_tables/loot/event_love_chest.json -> datapacks/base/data/epic/loot_tables/event/valentines2018/love_chest.json
datapacks/base/data/epic/loot_tables/items/r1/event/winter2017/items/animated_coal.json -> datapacks/base/data/epic/loot_tables/event/winter2017/animated_coal.json
datapacks/base/data/epic/loot_tables/items/r1/event/winter2017/items/everlasting_snow.json -> datapacks/base/data/epic/loot_tables/event/winter2017/everlasting_snow.json
datapacks/base/data/epic/loot_tables/items/r1/event/winter2017/items/fangorn_draught.json -> datapacks/base/data/epic/loot_tables/event/winter2017/fangorn_draught.json
datapacks/base/data/epic/loot_tables/items/r1/event/winter2017/items/olfactory_carrot.json -> datapacks/base/data/epic/loot_tables/event/winter2017/olfactory_carrot.json
datapacks/base/data/epic/loot_tables/items/r1/event/winter2017/items/prehensile_stick.json -> datapacks/base/data/epic/loot_tables/event/winter2017/prehensile_stick.json
datapacks/base/data/epic/loot_tables/items/r1/event/winter2017/items/rod_of_the_onodrim.json -> datapacks/base/data/epic/loot_tables/event/winter2017/rod_of_the_onodrim.json
datapacks/base/data/epic/loot_tables/items/r1/event/winter2017/items/snegovik_boots.json -> datapacks/base/data/epic/loot_tables/event/winter2017/snegovik_boots.json
datapacks/base/data/epic/loot_tables/items/r1/event/winter2017/items/snegovik_cuirass.json -> datapacks/base/data/epic/loot_tables/event/winter2017/snegovik_cuirass.json
datapacks/base/data/epic/loot_tables/items/r1/event/winter2017/items/snegovik_greaves.json -> datapacks/base/data/epic/loot_tables/event/winter2017/snegovik_greaves.json
datapacks/base/data/epic/loot_tables/items/r1/event/winter2017/items/snegovik_helm.json -> datapacks/base/data/epic/loot_tables/event/winter2017/snegovik_helm.json
datapacks/base/data/epic/loot_tables/items/r1/event/winter2018/blistering_cold.json -> datapacks/base/data/epic/loot_tables/event/winter2018/blistering_cold.json
datapacks/base/data/epic/loot_tables/items/r1/event/winter2018/frozen_growths.json -> datapacks/base/data/epic/loot_tables/event/winter2018/frozen_growths.json
datapacks/base/data/epic/loot_tables/items/r1/event/winter2018/ice_diamond.json -> datapacks/base/data/epic/loot_tables/event/winter2018/ice_diamond.json
datapacks/base/data/epic/loot_tables/items/r1/event/winter2018/ice_trophy.json -> datapacks/base/data/epic/loot_tables/event/winter2018/ice_trophy.json
datapacks/base/data/epic/loot_tables/items/r1/event/winter2018/icy_gold.json -> datapacks/base/data/epic/loot_tables/event/winter2018/icy_gold.json
datapacks/base/data/epic/loot_tables/items/r1/event/winter2018/nivalis_core.json -> datapacks/base/data/epic/loot_tables/event/winter2018/nivalis_core.json
datapacks/base/data/epic/loot_tables/items/r1/event/winter2018/permafrost.json -> datapacks/base/data/epic/loot_tables/event/winter2018/permafrost.json
datapacks/base/data/epic/loot_tables/items/r1/event/winter2018/snowball_key.json -> datapacks/base/data/epic/loot_tables/event/winter2018/snowball_key.json
datapacks/base/data/epic/loot_tables/items/r1/event/winter2018/snowball_lose.json -> datapacks/base/data/epic/loot_tables/event/winter2018/snowball_lose.json
datapacks/base/data/epic/loot_tables/items/r1/event/winter2018/snowball_mvp.json -> datapacks/base/data/epic/loot_tables/event/winter2018/snowball_mvp.json
datapacks/base/data/epic/loot_tables/items/r1/event/winter2018/snowball_win.json -> datapacks/base/data/epic/loot_tables/event/winter2018/snowball_win.json
datapacks/base/data/epic/loot_tables/items/r1/event/winter2018/yule_log.json -> datapacks/base/data/epic/loot_tables/event/winter2018/yule_log.json
datapacks/base/data/epic/loot_tables/loot/azacor/artifact.json -> datapacks/base/data/epic/loot_tables/r1/azacor/artifact.json
datapacks/base/data/epic/loot_tables/loot/azacor/r_hard.json -> datapacks/base/data/epic/loot_tables/r1/azacor/r_hard.json
datapacks/base/data/epic/loot_tables/loot/azacor/r_normal.json -> datapacks/base/data/epic/loot_tables/r1/azacor/r_normal.json
datapacks/base/data/epic/loot_tables/loot/azacor/shard.json -> datapacks/base/data/epic/loot_tables/r1/azacor/shard.json
datapacks/base/data/epic/loot_tables/loot/azacor/uncommon.json -> datapacks/base/data/epic/loot_tables/r1/azacor/uncommon.json
datapacks/base/data/epic/loot_tables/loot/slot_machine.json -> datapacks/base/data/epic/loot_tables/r1/casino/slot_machine_chest.json
datapacks/base/data/epic/loot_tables/loot/final_dungeon1.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/1/final_chest.json
datapacks/base/data/epic/loot_tables/loot/level_2_dungeon1.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/1/level_2_chest.json
datapacks/base/data/epic/loot_tables/loot/level_3_dungeon1.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/1/level_3_chest.json
datapacks/base/data/epic/loot_tables/loot/final_dungeon2.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/2/final_chest.json
datapacks/base/data/epic/loot_tables/loot/level_2_dungeon2.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/2/level_2_chest.json
datapacks/base/data/epic/loot_tables/loot/level_3_dungeon2.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/2/level_3_chest.json
datapacks/base/data/epic/loot_tables/loot/level_4_dungeon2.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/2/level_4_chest.json
datapacks/base/data/epic/loot_tables/loot/final_dungeon3.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/3/final_chest.json
datapacks/base/data/epic/loot_tables/loot/level_3_dungeon3.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/3/level_3_chest.json
datapacks/base/data/epic/loot_tables/loot/level_4_dungeon3.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/3/level_4_chest.json
datapacks/base/data/epic/loot_tables/loot/final_dungeon4.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/4/final_chest.json
datapacks/base/data/epic/loot_tables/loot/level_3_dungeon4a.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/4/level_3_chest_a.json
datapacks/base/data/epic/loot_tables/loot/level_3_dungeon4u.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/4/level_3_chest_u.json
datapacks/base/data/epic/loot_tables/loot/level_4_dungeon4a.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/4/level_4_chest_a.json
datapacks/base/data/epic/loot_tables/loot/level_4_dungeon4u.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/4/level_4_chest_u.json
datapacks/base/data/epic/loot_tables/loot/dungeons/4/unicorn_puke.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/4/unicorn_puke.json
datapacks/base/data/epic/loot_tables/loot/dungeons/5/dragon-1.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/5/dragon-1.json
datapacks/base/data/epic/loot_tables/loot/dungeons/5/dragon-2.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/5/dragon-2.json
datapacks/base/data/epic/loot_tables/loot/dungeons/5/dragon_filler.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/5/dragon_filler.json
datapacks/base/data/epic/loot_tables/loot/dungeons/5/ender-1.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/5/ender-1.json
datapacks/base/data/epic/loot_tables/loot/dungeons/5/ender_filler.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/5/ender_filler.json
datapacks/base/data/epic/loot_tables/loot/dungeons/5/fish-1.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/5/fish-1.json
datapacks/base/data/epic/loot_tables/loot/dungeons/5/fish-2.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/5/fish-2.json
datapacks/base/data/epic/loot_tables/loot/dungeons/5/fish_filler.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/5/fish_filler.json
datapacks/base/data/epic/loot_tables/loot/dungeons/5/items.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/5/items.json
datapacks/base/data/epic/loot_tables/loot/mobs/mimic/yellow_mimic.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/5/mimic.json
datapacks/base/data/epic/loot_tables/loot/dungeons/5/overgrown-man-1.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/5/overgrown-man-1.json
datapacks/base/data/epic/loot_tables/loot/dungeons/5/overgrown-man-2.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/5/overgrown-man-2.json
datapacks/base/data/epic/loot_tables/loot/dungeons/5/overgrown-man_filler.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/5/overgrown-man_filler.json
datapacks/base/data/epic/loot_tables/loot/dungeons/5/poison-man-1.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/5/poison-man-1.json
datapacks/base/data/epic/loot_tables/loot/dungeons/5/poison-man-2.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/5/poison-man-2.json
datapacks/base/data/epic/loot_tables/loot/dungeons/5/poison-man_filler.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/5/poison-man_filler.json
datapacks/base/data/epic/loot_tables/loot/dungeons/5/polar-1.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/5/polar-1.json
datapacks/base/data/epic/loot_tables/loot/dungeons/5/polar_filler.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/5/polar_filler.json
datapacks/base/data/epic/loot_tables/loot/dungeons/5/rares.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/5/rares.json
datapacks/base/data/epic/loot_tables/loot/dungeons/5/tier1.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/5/tier1.json
datapacks/base/data/epic/loot_tables/loot/dungeons/5/tier2.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/5/tier2.json
datapacks/base/data/epic/loot_tables/loot/final_dungeonb.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/bonus/final_chest.json
datapacks/base/data/epic/loot_tables/loot/level_4_dungeonb.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/bonus/level_4_chest.json
datapacks/base/data/epic/loot_tables/loot/level_5_dungeonb.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/bonus/level_5_chest.json
datapacks/base/data/epic/loot_tables/loot/mobs/mimic/bonus_mimic.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/bonus/mimic.json
datapacks/base/data/epic/loot_tables/loot/level_0_dungeon0.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/oldlabs/level_0_chest.json
datapacks/base/data/epic/loot_tables/loot/level_1_dungeon0.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/oldlabs/level_1_chest.json
datapacks/base/data/epic/loot_tables/items/r1/boss/caxtalmask.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/reverie/caxtalmask.json
datapacks/base/data/epic/loot_tables/loot/dungeons/corrupted/charms.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/reverie/charms.json
datapacks/base/data/epic/loot_tables/loot/dungeons/corrupted.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/reverie/chest.json
datapacks/base/data/epic/loot_tables/loot/dungeons/corrupted/filler.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/reverie/filler.json
datapacks/base/data/epic/loot_tables/loot/dungeons/corrupted/rares.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/reverie/rares.json
datapacks/base/data/epic/loot_tables/loot/dungeons/corrupted/shard.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/reverie/shard.json
datapacks/base/data/epic/loot_tables/loot/dungeons/corrupted/tier.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/reverie/tier.json
datapacks/base/data/epic/loot_tables/loot/dungeons/corrupted/uncommon.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/reverie/uncommon.json
datapacks/base/data/epic/loot_tables/loot/tutorial/starter_chest.json -> datapacks/base/data/epic/loot_tables/r1/dungeons/tutorial/starter_chest.json
datapacks/base/data/epic/loot_tables/acrobat/apartments_lousy_shirt.json -> datapacks/base/data/epic/loot_tables/r1/items/acrobat/apartments_lousy_shirt.json
datapacks/base/data/epic/loot_tables/items/r1/atoned_sandles.json -> datapacks/base/data/epic/loot_tables/r1/items/advancements/atoned_sandles.json
datapacks/base/data/epic/loot_tables/items/r1/eternal_cuirass.json -> datapacks/base/data/epic/loot_tables/r1/items/advancements/eternal_cuirass.json
datapacks/base/data/epic/loot_tables/items/r1/misc/breadhead.json -> datapacks/base/data/epic/loot_tables/r1/items/misc/breadhead.json
datapacks/base/data/epic/loot_tables/items/r1/buginamber.json -> datapacks/base/data/epic/loot_tables/r1/items/misc/buginamber.json
datapacks/base/data/epic/loot_tables/loot/mobs/mimic/chestey.json -> datapacks/base/data/epic/loot_tables/r1/items/misc/chestey.json
datapacks/base/data/epic/loot_tables/loot/mobs/mimic/rare.json -> datapacks/base/data/epic/loot_tables/r1/items/misc/emblem_of_greed.json
datapacks/base/data/epic/loot_tables/items/r1/misc/kings_greaves.json -> datapacks/base/data/epic/loot_tables/r1/items/misc/kings_greaves.json
datapacks/base/data/epic/loot_tables/items/r1/misc/kings_sabatons.json -> datapacks/base/data/epic/loot_tables/r1/items/misc/kings_sabatons.json
datapacks/base/data/epic/loot_tables/items/r1/misc/light_of_salvation.json -> datapacks/base/data/epic/loot_tables/r1/items/misc/light_of_salvation.json
datapacks/base/data/epic/loot_tables/items/r1/misc/lofi_hip_hop_radio.json -> datapacks/base/data/epic/loot_tables/r1/items/misc/lofi_hip_hop_radio.json
datapacks/base/data/epic/loot_tables/items/r1/misc/stylish_black_shirt.json -> datapacks/base/data/epic/loot_tables/r1/items/misc/stylish_black_shirt.json
datapacks/base/data/epic/loot_tables/items/r1/boss/tradedmask.json -> datapacks/base/data/epic/loot_tables/r1/items/misc/tradedmask.json
datapacks/base/data/epic/loot_tables/items/r1/misc/zombie_plushie.json -> datapacks/base/data/epic/loot_tables/r1/items/misc/zombie_plushie.json
datapacks/base/data/epic/loot_tables/items/r1/patreon/entropic_skull.json -> datapacks/base/data/epic/loot_tables/r1/items/patreon/entropic_skull.json
datapacks/base/data/epic/loot_tables/items/r1/patreon/eventide.json -> datapacks/base/data/epic/loot_tables/r1/items/patreon/eventide.json
datapacks/base/data/epic/loot_tables/items/r1/patreon/gem_encrusted_manpance.json -> datapacks/base/data/epic/loot_tables/r1/items/patreon/gem_encrusted_manpance.json
datapacks/base/data/epic/loot_tables/items/r1/patreon/holy_feather.json -> datapacks/base/data/epic/loot_tables/r1/items/patreon/holy_feather.json
datapacks/base/data/epic/loot_tables/loot/hide.json -> datapacks/base/data/epic/loot_tables/r1/items/patreon/immaculate_hide.json
datapacks/base/data/epic/loot_tables/items/r1/patreon/polar_bear_hide.json -> datapacks/base/data/epic/loot_tables/r1/items/patreon/polar_bear_hide.json
datapacks/base/data/epic/loot_tables/items/r1/patreon/ruby_scythe.json -> datapacks/base/data/epic/loot_tables/r1/items/patreon/ruby_scythe.json
datapacks/base/data/epic/loot_tables/items/r1/patreon/sanctifying_guard.json -> datapacks/base/data/epic/loot_tables/r1/items/patreon/sanctifying_guard.json
datapacks/base/data/epic/loot_tables/items/r1/patreon/sharpened_holy_feather.json -> datapacks/base/data/epic/loot_tables/r1/items/patreon/sharpened_holy_feather.json
datapacks/base/data/epic/loot_tables/items/r1/patreon/silvered_sight.json -> datapacks/base/data/epic/loot_tables/r1/items/patreon/silvered_sight.json
datapacks/base/data/epic/loot_tables/items/r1/patreon/water_gem.json -> datapacks/base/data/epic/loot_tables/r1/items/patreon/water_gem.json
datapacks/base/data/epic/loot_tables/items/generic/potion/barrier_potion.json -> datapacks/base/data/epic/loot_tables/r1/items/potion/barrier_potion.json
datapacks/base/data/epic/loot_tables/items/generic/potion/extinguisher.json -> datapacks/base/data/epic/loot_tables/r1/items/potion/extinguisher.json
datapacks/base/data/epic/loot_tables/items/generic/potion/potion_of_protection.json -> datapacks/base/data/epic/loot_tables/r1/items/potion/potion_of_protection.json
datapacks/base/data/epic/loot_tables/items/generic/potion/sanctify_potion.json -> datapacks/base/data/epic/loot_tables/r1/items/potion/sanctify_potion.json
datapacks/base/data/epic/loot_tables/items/generic/potion/weak_barrier_potion.json -> datapacks/base/data/epic/loot_tables/r1/items/potion/weak_barrier_potion.json
datapacks/base/data/epic/loot_tables/items/generic/potion/weak_sanctify_potion.json -> datapacks/base/data/epic/loot_tables/r1/items/potion/weak_sanctify_potion.json
datapacks/base/data/epic/loot_tables/items/r1/quest/gloop.json -> datapacks/base/data/epic/loot_tables/r1/quests/03_gloop.json
datapacks/base/data/epic/loot_tables/items/r1/quest/morphic_shield.json -> datapacks/base/data/epic/loot_tables/r1/quests/03_morphic_shield.json
datapacks/base/data/epic/loot_tables/items/r1/quest/silver_knights_hammer.json -> datapacks/base/data/epic/loot_tables/r1/quests/12_silver_knights_hammer.json
datapacks/base/data/epic/loot_tables/items/r1/quest/grass_fed_cow.json -> datapacks/base/data/epic/loot_tables/r1/quests/17_grass_fed_cow.json
datapacks/base/data/epic/loot_tables/loot/rares_transmog.json -> datapacks/base/data/epic/loot_tables/r1/transmog/rares.json
datapacks/base/data/epic/loot_tables/loot/amplified.json -> datapacks/base/data/epic/loot_tables/r1/world/amplified_reward_chest.json
datapacks/base/data/epic/loot_tables/loot/events/filler_house.json -> datapacks/base/data/epic/loot_tables/r1/world/filler/grove_house.json
datapacks/base/data/epic/loot_tables/loot/events/filler_spooky.json -> datapacks/base/data/epic/loot_tables/r1/world/filler/grove_spooky.json
datapacks/base/data/epic/loot_tables/loot/filler_mimic.json -> datapacks/base/data/epic/loot_tables/r1/world/mimic/filler.json
datapacks/base/data/epic/loot_tables/loot/level_4_mimic.json -> datapacks/base/data/epic/loot_tables/r1/world/mimic/level_4_mimic.json
datapacks/base/data/epic/loot_tables/loot/mobs/r1/nightmarish_enderman.json -> datapacks/base/data/epic/loot_tables/r1/world/mobs/nightmarish_enderman.json
datapacks/base/data/epic/loot_tables/loot/mobs/mimic/overworld_mimic.json -> datapacks/base/data/epic/loot_tables/r1/world/mobs/overworld_mimic.json
datapacks/base/data/epic/loot_tables/items/r1/poi/blackroots_fury.json -> datapacks/base/data/epic/loot_tables/r1/world/poi_uncommon_chests/blackroots_fury.json
datapacks/base/data/epic/loot_tables/items/r1/poi/blazing_soul.json -> datapacks/base/data/epic/loot_tables/r1/world/poi_uncommon_chests/blazing_soul.json
datapacks/base/data/epic/loot_tables/items/r1/poi/blighted_scythe.json -> datapacks/base/data/epic/loot_tables/r1/world/poi_uncommon_chests/blighted_scythe.json
datapacks/base/data/epic/loot_tables/items/r1/poi/chitin_helmet.json -> datapacks/base/data/epic/loot_tables/r1/world/poi_uncommon_chests/chitin_helmet.json
datapacks/base/data/epic/loot_tables/items/r1/poi/cutting_breeze.json -> datapacks/base/data/epic/loot_tables/r1/world/poi_uncommon_chests/cutting_breeze.json
datapacks/base/data/epic/loot_tables/items/r1/poi/drowned_shellmet.json -> datapacks/base/data/epic/loot_tables/r1/world/poi_uncommon_chests/drowned_shellmet.json
datapacks/base/data/epic/loot_tables/items/r1/poi/ensanguined_flower.json -> datapacks/base/data/epic/loot_tables/r1/world/poi_uncommon_chests/ensanguined_flower.json
datapacks/base/data/epic/loot_tables/items/r1/poi/fangridian_catcrappe.json -> datapacks/base/data/epic/loot_tables/r1/world/poi_uncommon_chests/fangridian_catcrappe.json
datapacks/base/data/epic/loot_tables/items/r1/poi/groovy_chakram.json -> datapacks/base/data/epic/loot_tables/r1/world/poi_uncommon_chests/groovy_chakram.json
datapacks/base/data/epic/loot_tables/items/r1/poi/infernal_robe.json -> datapacks/base/data/epic/loot_tables/r1/world/poi_uncommon_chests/infernal_robe.json
datapacks/base/data/epic/loot_tables/items/r1/poi/lingering_flame.json -> datapacks/base/data/epic/loot_tables/r1/world/poi_uncommon_chests/lingering_flame.json
datapacks/base/data/epic/loot_tables/items/r1/poi/oncoming_wave.json -> datapacks/base/data/epic/loot_tables/r1/world/poi_uncommon_chests/oncoming_wave.json
datapacks/base/data/epic/loot_tables/items/r1/poi/ponderous_stone.json -> datapacks/base/data/epic/loot_tables/r1/world/poi_uncommon_chests/ponderous_stone.json
datapacks/base/data/epic/loot_tables/items/r1/poi/poultrygeist.json -> datapacks/base/data/epic/loot_tables/r1/world/poi_uncommon_chests/poultrygeist.json
datapacks/base/data/epic/loot_tables/items/r1/poi/raiders_charm.json -> datapacks/base/data/epic/loot_tables/r1/world/poi_uncommon_chests/raiders_charm.json
datapacks/base/data/epic/loot_tables/items/r1/poi/swiftwood_shortbow.json -> datapacks/base/data/epic/loot_tables/r1/world/poi_uncommon_chests/swiftwood_shortbow.json
datapacks/base/data/epic/loot_tables/items/r1/poi/vermins_scourge.json -> datapacks/base/data/epic/loot_tables/r1/world/poi_uncommon_chests/vermins_scourge.json
datapacks/base/data/epic/loot_tables/items/r1/poi/voltaic_edge.json -> datapacks/base/data/epic/loot_tables/r1/world/poi_uncommon_chests/voltaic_edge.json
datapacks/base/data/epic/loot_tables/loot/potions_0.json -> datapacks/base/data/epic/loot_tables/r1/world/sets/potions_0.json
datapacks/base/data/epic/loot_tables/loot/potions_1.json -> datapacks/base/data/epic/loot_tables/r1/world/sets/potions_1.json
datapacks/base/data/epic/loot_tables/loot/potions_2.json -> datapacks/base/data/epic/loot_tables/r1/world/sets/potions_2.json
datapacks/base/data/epic/loot_tables/loot/potions_3.json -> datapacks/base/data/epic/loot_tables/r1/world/sets/potions_3.json
datapacks/base/data/epic/loot_tables/loot/potions_4.json -> datapacks/base/data/epic/loot_tables/r1/world/sets/potions_4.json
datapacks/base/data/epic/loot_tables/loot/potions_5.json -> datapacks/base/data/epic/loot_tables/r1/world/sets/potions_5.json
datapacks/base/data/epic/loot_tables/loot/rare_3.json -> datapacks/base/data/epic/loot_tables/r1/world/sets/rare_3.json
datapacks/base/data/epic/loot_tables/loot/rare_4.json -> datapacks/base/data/epic/loot_tables/r1/world/sets/rare_4.json
datapacks/base/data/epic/loot_tables/loot/level_0_bandit.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_0_bandit.json
datapacks/base/data/epic/loot_tables/loot/level_0_fire.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_0_fire.json
datapacks/base/data/epic/loot_tables/loot/level_0_forest.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_0_forest.json
datapacks/base/data/epic/loot_tables/loot/level_0_mines.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_0_mines.json
datapacks/base/data/epic/loot_tables/loot/level_0_temple.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_0_temple.json
datapacks/base/data/epic/loot_tables/loot/level_0_water.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_0_water.json
datapacks/base/data/epic/loot_tables/loot/level_1_bandit.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_1_bandit.json
datapacks/base/data/epic/loot_tables/loot/level_1_fire.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_1_fire.json
datapacks/base/data/epic/loot_tables/loot/level_1_forest.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_1_forest.json
datapacks/base/data/epic/loot_tables/loot/level_1_mines.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_1_mines.json
datapacks/base/data/epic/loot_tables/loot/level_1_temple.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_1_temple.json
datapacks/base/data/epic/loot_tables/loot/level_1_water.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_1_water.json
datapacks/base/data/epic/loot_tables/loot/level_2_bandit.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_2_bandit.json
datapacks/base/data/epic/loot_tables/loot/level_2_fire.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_2_fire.json
datapacks/base/data/epic/loot_tables/loot/level_2_forest.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_2_forest.json
datapacks/base/data/epic/loot_tables/loot/level_2_mines.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_2_mines.json
datapacks/base/data/epic/loot_tables/loot/level_2_temple.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_2_temple.json
datapacks/base/data/epic/loot_tables/loot/level_2_water.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_2_water.json
datapacks/base/data/epic/loot_tables/loot/level_3_bandit.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_3_bandit.json
datapacks/base/data/epic/loot_tables/loot/level_3_fire.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_3_fire.json
datapacks/base/data/epic/loot_tables/loot/level_3_forest.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_3_forest.json
datapacks/base/data/epic/loot_tables/loot/level_3_mines.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_3_mines.json
datapacks/base/data/epic/loot_tables/loot/level_3_temple.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_3_temple.json
datapacks/base/data/epic/loot_tables/loot/level_3_water.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_3_water.json
datapacks/base/data/epic/loot_tables/loot/level_4_bandit.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_4_bandit.json
datapacks/base/data/epic/loot_tables/loot/level_4_fire.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_4_fire.json
datapacks/base/data/epic/loot_tables/loot/level_4_forest.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_4_forest.json
datapacks/base/data/epic/loot_tables/loot/events/level_4_house.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_4_grove_house.json
datapacks/base/data/epic/loot_tables/loot/events/level_4_spooky.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_4_grove_spooky.json
datapacks/base/data/epic/loot_tables/loot/level_4_mines.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_4_mines.json
datapacks/base/data/epic/loot_tables/loot/level_4_temple.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_4_temple.json
datapacks/base/data/epic/loot_tables/loot/level_4_water.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_4_water.json
datapacks/base/data/epic/loot_tables/loot/level_5_bandit.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_5_bandit.json
datapacks/base/data/epic/loot_tables/loot/level_5_fire.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_5_fire.json
datapacks/base/data/epic/loot_tables/loot/level_5_forest.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_5_forest.json
datapacks/base/data/epic/loot_tables/loot/level_5_mines.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_5_mines.json
datapacks/base/data/epic/loot_tables/loot/level_5_temple.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_5_temple.json
datapacks/base/data/epic/loot_tables/loot/level_5_water.json -> datapacks/base/data/epic/loot_tables/r1/world/tiered_chests/level_5_water.json
'''

manual_renames = '''
minecraft:entities/null -> minecraft:empty
minecraft:0 -> minecraft:empty
0 -> minecraft:empty
epic:loot/items/r1/patreon/holy_feather -> epic:r1/items/patreon/holy_feather
epic:loot/items/r1/patreon/polar_bear_hide -> epic:r1/items/patreon/polar_bear_hide
epic:loot/items/r1/patreon/water_gem -> epic:r1/items/patreon/water_gem
minecraft:banditb -> minecraft:empty
heyyy -> minecraft:empty
empty -> minecraft:empty
'''

for item in renameraw.splitlines():
    if " -> " in item:
        split = item.split(" -> ")
        mgr.update_table_link_everywhere(mgr.to_namespaced_path(split[0]), mgr.to_namespaced_path(split[1]))

for item in manual_renames.splitlines():
    if " -> " in item:
        split = item.split(" -> ")
        mgr.update_table_link_everywhere(split[0], split[1])
