#!/usr/bin/env python3

import json
import os
import re
import sys

from typing import Union

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry/brigadier.py"))

from brigadier.string_reader import StringReader
from lib_py3.common import update_plain_tag
from lib_py3.json_file import jsonFile
from minecraft.player_dat_format.item import Item
from quarry.types import nbt

ITEM_WITH_NBT_START = re.compile(' ([a-z]+:)?[a-z_]+{')

TEST_ITEMS = '''
stick
stick{}
stick{a:1}
stick{a:{}}
stick{a:{b:2}}
grass_block
grass_block{}
'''

def upgrade_line_nbt_format(line: str, debug: bool = False) -> str:
    reader = StringReader(line)
    result_line = ''

    if debug:
        print(line)
        match_line = ''

    start = 0
    for match in ITEM_WITH_NBT_START.finditer(line):
        result_line += line[start:match.start()+1]
        start = match.start() + 1

        reader.set_cursor(start)
        item = Item.from_command_format(reader, check_count=True)
        end = reader.get_cursor()

        if debug:
            match_line = f'{match_line:<{start}}[{"^"*(end - start - 2)}]'

        if item.has_tag():
            tag = item.tag

            # TODO Do item replacements here
            # TODO handle remaining 1.15 -> 1.16 upgrades

            # Store unformatted version of formatted text on items
            update_plain_tag(tag)

            if debug and tag.has_path('plain'):
                tag.at_path('plain').tree()

            if debug:
                entry = item.to_loot_table_entry(include_count=True, weight=10)
                print(json.dumps(entry, ensure_ascii=False, indent=4))

            item.tag = tag

        result_line += item.to_command_format(include_count=True)
        start = end

    result_line += line[start:]

    if debug:
        print(line)
        print(match_line)
        print(result_line)
        print('='*4)

    return result_line

def upgrade_mcfunction(path: str):
    lines = []
    with open(path, 'r') as fp:
        lines = fp.readlines()
    newlines = []
    for line in lines:
        newlines.append(upgrade_line_nbt_format(line))
    with open(path, 'w') as fp:
        fp.writelines(newlines)

def upgrade_json_walk(obj: Union[str, dict, list, int, bool]) -> Union[str, dict, list, int, bool]:
    if isinstance(obj, str):
        return upgrade_line_nbt_format(obj)
    elif isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            new_obj[k] = upgrade_json_walk(v)
        return new_obj
    elif isinstance(obj, list):
        new_obj = []
        for v in obj:
            new_obj.append(upgrade_json_walk(v))
        return new_obj
    else:
        return new_obj

def upgrade_json(path: str):
    json_file = jsonFile(path)
    json_file.dict = upgrade_json_walk(json_file.dict)
    json_file.save()

'''
for prefix in ['give @s ', 'give @p[gamemode=survival] ', 'give @p[gamemode=survival,nbt={Inventory:[{}]}] ', 'clear @s ', 'execute run give @s ']:
    for item_str in TEST_ITEMS.splitlines():
        for suffix in ['', ' 5']:
            line = prefix + item_str + suffix
            new_line = upgrade_line_nbt_format(line)
'''

upgrade_line_nbt_format('''give @s stone{} 5 stick 2 banana{display:{Name:'{"text":"Phone"}'}}''', debug=True)
#upgrade_line_nbt_format(r'''/give @p minecraft:written_book{pages:['{"extra":[{"obfuscated":true,"text":"\\u0027A NEI XEALOT OX A\\u0027I NTIIA NITE\\u0027 AAL NOONE AA O\\u0027IINIOTA TOAL TOATIACX NEI NIENE TIIXIAN NEI XNAXX T\\u0027NE NEI XOEITI OX ACC NE\\u0027ANX AAL NEIA COE HAC IANII NEI IIACH OX NIEI L\\u0027ANX"}],"text":""}'],generation:0,resolved:1b,display:{Lore:['{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"light_purple","text":"* Quest Item *"}],"text":""}','{"text":"#Q03I01"}']},author:"Ezariah",title:"Jungle Research Notes"} 16''', debug=True)
#upgrade_line_nbt_format(r'''/give @p minecraft:written_book{pages:['{"text":"C\'Zanil long remained an enigmatic figure within the Tlaxan forces, spoke of in little more than whispers by prisoners captured and coerced into giving information. They called him the Soulcrusher, but what this meant was unknown for the longest time."}','{"text":"It was only days ago that C\'Zanil\'s role in the war became clear, when we captured a powerful Ritualist carrying a Bottle of Souls. In a desperate attempt to cast his death magics, the Ritualist attempted to tear the bottle open as he screamed words of"}','{"text":"power, but a sharpshooter pierced his hand, rendering his attempts futile.§0\\n§0\\n§0Stunningly, the Ritualist talked to us. He told us of the three Tlaxan Shamans overseeing the war efforts, C\'Zanil, C\'Axtal, and C\'Shura. Detailed below is his"}','{"text":"account of C\'Zanil, the Soulcrusher.§0\\n§0\\n§0              -§0\\n§0\\"C\'Zanil, yes. The foremost of the three. The Soulcrusher, the harvester of the dead. C\'Zanil creates our magics. He fuels our power with the souls of the dead."}','{"text":"He lurks within our massive complex, A\'arsllum Quetzal, the Halls of Wind and Blood, wherein sacrifices are brought to him. With his magics and his blade, he harvests their souls, bottling them to allow our warlocks to hurl potent spells at your puny"}','{"text":"forces. This bottle alone should have wiped out your forces. I plan to shatter it soon, no matter how you try to stop me. I will see your people turned to bone, your ashes scattered on the winds, your souls screaming for C\'Zanil to harvest, to use to"}','{"text":"slaughter more.§0\\n§0\\n§0\\"You have no escape from this fate. This is the way things will be. This is the way Quetzalcoatl wills it. Kaul is on our side.§0\\n§0\\n§0\\"You invaders shall be removed from our home.\\"§0\\n§0             -"}','{"text":"After this, the Ritualist fell silent and refused to speak for hours. Later he would briefly touch on the other two Shamans he mentioned, but two days later, he was dead.§0\\n§0\\n§0The bottle remains safely locked in the Vault."}','{"text":"Whatever C\'Zanil has planned, whatever vile and strange magic he has sealed within this bottle using the souls of his own dying men, will never come to fruition if I have anything to do with it."}'],generation:0,title:"C'Zanil",author:"General Skeldin",display:{Name:'{"extra":[{"bold":true,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"gold","text":"C\'Zanil"}],"text":""}',Lore:['{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"light_purple","text":"* Quest Item *"}],"text":""}','{"text":"#Q23I02"}']},resolved:1b} 2''', debug=True)

