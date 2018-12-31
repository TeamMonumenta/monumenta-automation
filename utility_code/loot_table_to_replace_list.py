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

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt


mgr = LootTableManager()

mgr.load_loot_tables_subdirectories("/home/rock/project_epic/server_config/data/datapacks")
mgr.load_advancements_subdirectories("/home/rock/project_epic/server_config/data/datapacks")
mgr.load_functions_subdirectories("/home/rock/project_epic/server_config/data/datapacks")
mgr.load_scripted_quests_directory("/home/rock/project_epic/server_config/data/scriptedquests")

#mgr.autoformat_json_files_in_directory("/home/rock/project_epic/server_config/data/datapacks", indent=4)
#mgr.autoformat_json_files_in_directory("/home/rock/project_epic/server_config/data/scriptedquests", indent=2)

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
'''

for item in renameraw.splitlines():
    if " -> " in item:
        split = item.split(" -> ")
        mgr.update_table_link_everywhere(split[0], split[1])


