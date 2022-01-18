import json
import os
import re
import sys

import traceback

from lib_py3.common import eprint
from lib_py3.common import jsonify_text
from lib_py3.common import parse_name_possibly_json
from lib_py3.common import update_plain_tag

from minecraft.chunk_format.block_entity import BlockEntity
from minecraft.chunk_format.entity import Entity
from minecraft.player_dat_format.item import Item

import requests

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types import nbt
from quarry.types.text_format import unformat_text, TextFormats, TextStyles

def jsonify_text_hack(text):
    if text == "":
        return json.dumps({"text":""}, ensure_ascii=False, separators=(',', ':'))
    elif text.startswith("§"):
        extra = [{"bold":False,"italic":False,"underlined":False,"strikethrough":False,"obfuscated":False,"color":"light_purple","text":""}]
        while text:
            while text.startswith("§"):
                try:
                    format_ = TextFormats.get_format_by_section_code(text[:2])
                    if format_ == TextFormats.reset.value:
                        format_ = TextFormats.white.value
                    if any(style.value == format_ for style in TextStyles):
                        extra[-1][format_.technical_name] = True
                    else:
                        extra[-1]["color"] = format_.technical_name
                    text = text[2:]
                except KeyError:
                    extra[-1]["text"] += text[:2]
                    text = text[2:]
                    break
            while text and not text.startswith("§"):
                extra[-1]["text"] += text[:1]
                text = text[1:]
            if text:
                extra.append({"text":""})
        return json.dumps({"extra":extra,"text":""}, ensure_ascii=False, separators=(',', ':'))
    else:
        return json.dumps({"extra":[{"text":text}],"text":""}, ensure_ascii=False, separators=(',', ':'))

def to_number(numeral):
    if numeral == 'I':
        return 1
    elif numeral == 'II':
        return 2
    elif numeral == 'III':
        return 3
    elif numeral == 'IV':
        return 4
    else:
        return 0

def get_uuid(username):
    url = f'https://api.mojang.com/users/profiles/minecraft/{username}?'
    response = requests.get(url)
    uuid = response.json()['id']
    return uuid

class GlobalRule(object):
    """Base pre/post processing rule for item replacements, used to preserve and edit data."""
    # Edit this for all new objects:
    name = "Undefined global rule"

    def __init__(self):
        """Local data storage"""
        pass

    def preprocess(self, template, item):
        """Read the unedited item.

        Return True to abort replacement and changes.
        Make no edits here.
        """
        pass

    def postprocess(self, item):
        """Edit the item with last stored value"""
        pass

    @classmethod
    def recursive_public_subclasses(cls):
        """Return a list of initialized subclasses, not listing subclasses starting with '_'.

        Should multiple subclasses need to be derived from another subclass,
        a base subclass whose name starts with '_' should be created so
        its children are returned, but not the base subclass itself.
        """
        result = []

        for subclass in cls.__subclasses__():
            name = subclass.__name__

            # Ignore subclasses that exist only as a parent to other subclasses
            if not name.startswith("_"):
                result.append(subclass())

            result += subclass.recursive_public_subclasses()

        return result

    def __str__(self):
        return f'{self.name}: {vars(self)}'

    def __repr__(self):
        return f'{type(self).__name__}()'

################################################################################
# Global rules begin

class AbortNoLore(GlobalRule):
    name = "Abort if there's no lore text"

    def preprocess(self, template, item):
        # Items with lore are always replaced
        if item.nbt.has_path('tag.display.Lore'):
            return

        # Items without lore in spawners never get replaced
        if item.is_in_spawner():
            return True

        # Anything at this point is probably fine.
        return

class PreserveArmorColor(GlobalRule):
    name = 'Preserve armor color'

    def preprocess(self, template, item):
        self.color = None
        if item.nbt.has_path('tag.display.color'):
            self.color = item.tag.at_path('display.color').value

    def postprocess(self, item):
        if item.id not in (
            'minecraft:leather_helmet',
            'minecraft:leather_chestplate',
            'minecraft:leather_leggings',
            'minecraft:leather_boots',
            'minecraft:leather_horse_armor',
        ):
            # Don't preserve armor color if it's no longer leather
            return

        if self.color is None:
            if item.nbt.has_path('tag.display.color'):
                item.tag.at_path('display').value.pop('color')
            return

        # Make sure tag exists first
        if not item.has_tag():
            item.tag = nbt.TagCompound({})
        if not item.tag.has_path('display'):
            item.tag.value['display'] = nbt.TagCompound({})
        if not item.tag.has_path('display.color'):
            item.tag.at_path('display').value['color'] = nbt.TagInt(0)

        # Apply color
        item.tag.at_path('display.color').value = self.color

class PreserveDamage(GlobalRule):
    name = 'Preserve damage'

    def preprocess(self, template, item):
        self.damage = None
        if item.nbt.has_path('tag.Damage'):
            self.damage = item.tag.at_path('Damage').value

    def postprocess(self, item):
        if not item.is_damageable():
            return

        if self.damage is None:
            if item.nbt.has_path('tag.Damage'):
                item.tag.value.pop('Damage')
            return

        # Make sure tag exists first
        if not item.has_tag():
            item.tag = nbt.TagCompound({})
        if not item.tag.has_path('Damage'):
            item.tag.value['Damage'] = nbt.TagInt(0)

        # Apply damage
        item.tag.at_path('Damage').value = self.damage

class PreserveCrossbowItem(GlobalRule):
    name = 'Preserve crossbow item'

    def preprocess(self, template, item):
        self.Charged = None
        self.ChargedProjectiles = None
        if item.nbt.has_path('tag.Charged'):
            self.Charged = item.tag.at_path('Charged').deep_copy()
        if item.nbt.has_path('tag.ChargedProjectiles'):
            self.ChargedProjectiles = item.tag.at_path('ChargedProjectiles').deep_copy()

    def postprocess(self, item):
        if item.id != 'minecraft:crossbow':
            # Don't preserve crossbow item if it's no longer a crossbow
            return

        if self.Charged is None:
            if item.nbt.has_path('tag.Charged'):
                item.tag.value.pop('Charged')
        if self.ChargedProjectiles is None:
            if item.nbt.has_path('tag.ChargedProjectiles'):
                item.tag.value.pop('ChargedProjectiles')
        if self.Charged is None and self.ChargedProjectiles is None:
            return

        # Make sure tag exists first
        if not item.has_tag():
            item.tag = nbt.TagCompound({})
        if self.Charged is not None:
            item.tag.value['Charged'] = self.Charged
        if self.ChargedProjectiles is not None:
            item.tag.value['ChargedProjectiles'] = self.ChargedProjectiles

class PreserveEnchantments(GlobalRule):
    name = 'Preserve Enchantments'
    enchantments = (
        {"enchantment": 'Hope', "owner_prefix": 'Infused by'},
        {"enchantment": 'Gilded', "owner_prefix": 'Gilded by'},
        {"enchantment": 'Festive', "owner_prefix": 'Decorated by'},
        {"enchantment": 'Colossal', "owner_prefix": 'Reinforced by'},
        {"enchantment": 'Phylactery', "owner_prefix": 'Embalmed by'},
        {"enchantment": 'Soulbound', "owner_prefix": 'Soulbound to'},
        {"enchantment": 'Locked'},
        {"enchantment": 'Barking'},
        {"enchantment": 'Debarking'},

        # Infusions
        {"enchantment": 'Acumen', 'use_numeral': True},
        {"enchantment": 'Focus', 'use_numeral': True},
        {"enchantment": 'Perspicacity', 'use_numeral': True},
        {"enchantment": 'Tenacity', 'use_numeral': True},
        {"enchantment": 'Vigor', 'use_numeral': True},
        {"enchantment": 'Vitality', 'use_numeral': True},

        {"enchantment": 'Pennate', 'use_numeral': True},
        {"enchantment": 'Carapace', 'use_numeral': True},
        {"enchantment": 'Aura', 'use_numeral': True},
        {"enchantment": 'Expedite', 'use_numeral': True},
        {"enchantment": 'Choler', 'use_numeral': True},
        {"enchantment": 'Usurper', 'use_numeral': True},
        {"enchantment": 'Empowered', 'use_numeral': True},
        {"enchantment": 'Nutriment', 'use_numeral': True},
        {"enchantment": 'Execution', 'use_numeral': True},
        {"enchantment": 'Reflection', 'use_numeral': True},
        {"enchantment": 'Mitosis', 'use_numeral': True},
        {"enchantment": 'Ardor', 'use_numeral': True},
        {"enchantment": 'Epoch', 'use_numeral': True},
        {"enchantment": 'Natant', 'use_numeral': True},
        {"enchantment": 'Understanding', 'use_numeral': True},

        # Stat tracking
        {"enchantment": 'Stat Track', "owner_prefix": 'Tracked by'},
        {"enchantment": 'Mob Kills', 'use_number': True},
        {"enchantment": 'Spawners Broken', 'use_number': True},
        {"enchantment": 'Times Consumed', 'use_number': True},
        {"enchantment": 'Blocks Placed', 'use_number': True},
        {"enchantment": 'Melee Damage Dealt', 'use_number': True},
        {"enchantment": 'Boss Damage Dealt', 'use_number': True},
    )

    def __init__(self):
        self.enchantment_state = []
        self.apply = False

    def preprocess(self, template, item):
        self.enchantment_state = []
        self.tags_to_add = []

        for enchantment in self.enchantments:
            newstate = {
                'enchantment': enchantment['enchantment'],
                'owner_prefix': enchantment.get('owner_prefix', None),
                'use_numeral': enchantment.get('use_numeral', False),
                'use_number': enchantment.get('use_number', False),
            }

            self.enchantment_state.append(newstate)

        for lore in item.nbt.iter_multipath('tag.display.Lore[]'):
            for enchantment in self.enchantment_state:
                if enchantment['use_numeral'] and lore.contains(enchantment['enchantment']):
                    level = to_number(lore.split(' ')[1])
                    self.tags_to_add = {'enchant': enchantment['enchantment'], 'level': nbt.TagInt(level),
                                        'infuser': nbt.TagString(get_uuid('_Stickers1342'))}
                elif enchantment['use_number'] and lore.contains(enchantment['enchantment']):
                    level = lore.split(' ')[1]
                    self.tags_to_add = {'enchant': enchantment['enchantment'], 'level': nbt.TagInt(level + 1),
                                        'infuser': nbt.TagString(get_uuid('_Stickers1342'))}
                elif enchantment['owner_prefix'] is not None and lore.contains(enchantment['owner_prefix']):
                    username = lore.split(enchantment['owner_prefix'])[-1].replace(' ', '').replace('*', '').replace(')', '')
                    self.tags_to_add = {'enchant': enchantment['enchantment'], 'level': nbt.TagInt(1),
                                        'infuser': nbt.TagString(get_uuid(username))}
                elif lore.contains(enchantment['enchantment']):
                    self.tags_to_add = {'enchant': enchantment['enchantment'], 'level': nbt.TagInt(1),
                                        'infuser': nbt.TagString('_Stickers1342')}


    def postprocess(self, item):
        if not item.nbt.has_path('tag'):
            item.nbt.value['tag'] = nbt.TagCompound({})
        if not item.tag.has_path('Monumenta'):
            item.tag.value['Monumenta'] = nbt.TagCompound({})
        if not item.tag.has_path('Monumenta.PlayerModified'):
            item.tag.at_path('Monumenta').value['PlayerModified'] = nbt.TagCompound({})
        if not item.tag.has_path('Monumenta.PlayerModified.Infusions'):
            item.tag.at_path('Monumenta.PlayerModified').value['Infusions'] = nbt.TagCompound({})

        if len(self.tags_to_add) > 0:
            for infusion_dict in self.tags_to_add:
                enchant = infusion_dict['enchant']
                level = infusion_dict['level']
                infuser = infusion_dict['infuser']
                infusion_tag = item.nbt.TagCompound({})
                infusion_tag['Level'] = level
                infusion_tag['Infuser'] = infuser
                item.tag.at_path('Monumenta.PlayerModified.Infusions').value[
                    enchant.replace(' ', '')] = infusion_tag

class PreserveShattered(GlobalRule):
    name = 'Preserve Shattered'
    enchantment = "§4§l* SHATTERED *"

    def preprocess(self, template, item):
        self.shattered = False

        for lore in item.nbt.iter_multipath('tag.display.Lore[]'):
            if unformat_text(parse_name_possibly_json(lore.value)) == unformat_text(self.enchantment):
                self.shattered = True
                return

    def postprocess(self, item):
        if self.shattered:
            if not item.nbt.has_path('tag'):
                item.nbt.value['tag'] = nbt.TagCompound({})
            if not item.tag.has_path('Monumenta'):
                item.tag.value['Monumenta'] = nbt.TagCompound({})
            if not item.tag.has_path('Monumenta.PlayerModified'):
                item.tag.at_path('Monumenta').value['PlayerModified'] = nbt.TagCompound({})
            if not item.tag.has_path('Monumenta.PlayerModified.Shattered'):
                item.tag.at_path('Monumenta.PlayerModified').value['Shattered'] = nbt.TagCompound({})

            item.tag.at_path('Monumenta.PlayerModified.Shattered').value['Shattered'] = nbt.TagInt(1)

class PreserveBlockEntityTag(GlobalRule):
    name = 'Preserve block entity tag'

    def preprocess(self, template, item):
        self.block_entity_tag = None
        if item.nbt.has_path('tag.BlockEntityTag'):
            self.block_entity_tag = item.tag.at_path('BlockEntityTag')

            if type(self.block_entity_tag) is not nbt.TagCompound:
                self.block_entity_tag = None
                eprint("Skipping invalid BlockEntityTag: " + item.nbt.to_mojangson(highlight=False))
                return

            # Some legacy items have this invalid tag.BlockEntityTag.id field
            if self.block_entity_tag.has_path('id'):
                self.block_entity_tag.value.pop('id')

    def postprocess(self, item):
        if item.nbt.has_path('tag.BlockEntityTag'):
            item.tag.value.pop('BlockEntityTag')

        if self.block_entity_tag is not None:
            if not item.has_tag():
                item.tag = nbt.TagCompound({})
            item.tag.value['BlockEntityTag'] = self.block_entity_tag

class PreserveTotemOfTransposing(GlobalRule):
    name = 'Preserve Totem of Transposing tags'

    def preprocess(self, template, item):
        self.channel = None
        if item.nbt.has_path('tag.TransposingID') and isinstance(item.tag.at_path('TransposingID').value, int):
            self.channel = item.tag.at_path('TransposingID').value

    def postprocess(self, item):
        if self.channel is not None:
            if not item.nbt.has_path('tag.display.Lore[0]'):
                return
            for i, oldLoreTag in enumerate(item.tag.at_path('display.Lore').value):
                if 'Transposing Channel:' in oldLoreTag.value:
                    item.tag.value['TransposingID'] = nbt.TagInt(self.channel)
                    item.tag.at_path('display.Lore').value[i].value = '{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"gold","extra":[{"text":"Transposing Channel: "},{"text":"$TRANSPOSING_ID$"}],"text":""}'.replace('$TRANSPOSING_ID$', str(self.channel))
                    plain_tag_path = 'plain.display.Lore[$INDEX$]'.replace('$INDEX$', str(i))
                    if item.tag.has_path(plain_tag_path):
                        item.tag.at_path(plain_tag_path).value = 'Transposing Channel: $TRANSPOSING_ID$'.replace('$TRANSPOSING_ID$', str(self.channel))

class UpdatePlainTag(GlobalRule):
    name = 'Update plain tag'

    def postprocess(self, item):
        if item.nbt.has_path("tag"):
            update_plain_tag(item.nbt.at_path("tag"))

################################################################################
# Global rules end

global_rules = GlobalRule.recursive_public_subclasses()

