#!/usr/bin/env python3

import json
import os
import re
import sys

import traceback

from lib_py3.common import eprint
from lib_py3.common import jsonify_text
from lib_py3.common import parse_name_possibly_json

from minecraft.chunk_format.block_entity import BlockEntity
from minecraft.chunk_format.entity import Entity
from minecraft.player_dat_format.item import Item

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

def enchantify(item, player, enchantment, owner_prefix=None):
    """Applies a lore-text enchantment to item (full item nbt, including id and Count).

    Must be kept in sync with the plugin version!

    Lore format is:
    ```
    ...
    enchantment
    ...
    owner_prefix player
    ...
    ```
    regions is a list of the relevant region names, such as ["King's Valley", "Celsian Isles"]
    player is the player's name

    The plugin version of this also requires:
    sender, who/what is sending the command
    duplicateItem, whether to make an unedited copy
    """
    if not item.nbt.has_path('tag.display.Lore'):
        return
    lore = item.tag.at_path('display.Lore').value

    if len(lore) == 0:
        return

    newLore = []
    enchantmentFound = False
    nameAdded = (owner_prefix is None)
    for loreEntry in lore:
        loreText = parse_name_possibly_json(loreEntry.value)
        if enchantment in loreText:
            enchantmentFound = True

        loreStripped = unformat_text(loreText).strip()
        HEADER_LORE = ("King's Valley :", "Celsian Isles :", "Monumenta :", "Armor", "Magic Wand")
        if not enchantmentFound and (
            any(x in loreStripped for x in HEADER_LORE) or
            len(loreStripped) == 0
        ):
            enchantment_json = jsonify_text_hack("§7" + enchantment)
            newLore.append(nbt.TagString(enchantment_json))
            enchantmentFound = True

        if (not nameAdded and len(loreStripped.strip()) == 0):
            owner_json = jsonify_text_hack(owner_prefix + " " + player)
            newLore.append(nbt.TagString(owner_json))
            nameAdded = True

        newLore.append(loreEntry)

    if not enchantmentFound:
        # Don't apply changes
        return

    if not nameAdded:
        owner_json = jsonify_text_hack(owner_prefix + " " + player)
        newLore.append(nbt.TagString(owner_json))

    item.tag.at_path('display.Lore').value = newLore

def freeInfusion(player: str, item: Item, selection: str, level: str):
    """Infuse an item with <selection> infusion at level <level>"""
    newLore = []
    if item.nbt.has_path('tag.display.Lore'):
        for line in item.tag.iter_multipath('display.Lore[]'):
            if not line.value.contains("PRE COST ADJUST"):
                newLore.append(line.deep_copy())
        item.tag.at_path('display.Lore').value = newLore

    numeral = level
    if isinstance(level, int):
        numeral = {
            1: " I",
            2: " II",
            3: " III",
            4: " IV",
        }[level]
    enchantify(item, player, selection + numeral)

def shatter_item(item):
    """Applies shattered enchantment to an item

    Must be kept in sync with plugin version!

    Note that the logic to check if the item *should*
    be shattered is skipped here, as this will only
    be called if the item definitely should be
    shattered.

    item is type Item.
    """

    if not item.has_tag():
        item.tag = nbt.TagCompound({})
    if not item.tag.has_path('display'):
        item.tag.value['display'] = nbt.TagCompound({})
    if not item.tag.has_path('display.Lore'):
        item.tag.at_path('display').value['Lore'] = nbt.TagList([])

    lore = item.tag.at_path('display.Lore').value

    lore.append(nbt.TagString(jsonify_text_hack("§4§l* SHATTERED *")))
    lore.append(nbt.TagString(jsonify_text_hack("§4Maybe a Master Repairman")))
    lore.append(nbt.TagString(jsonify_text_hack("§4could reforge it...")))

################################################################################
# Global rules begin

class AbortNoLore(GlobalRule):
    name = "Abort if there's no lore text"

    def preprocess(self, template, item):
        # Items with lore are always replaced
        if item.nbt.has_path('tag.display.Lore'):
            return

        # Items without lore in spawners never get replaced
        parent = item.parent
        while parent:
            if isinstance(parent, (BlockEntity, Entity)):
                if parent.nbt.has_path("id") and parent.nbt.at_path("id").value.contains("spawner"):
                    # Not replaced
                    return True
            # Remember to go up a level, or infinite recursion issues occur
            parent = parent.parent

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
        {"enchantment": 'Acumen', "owner_prefix": None},
        {"enchantment": 'Focus', "owner_prefix": None},
        {"enchantment": 'Perspicacity', "owner_prefix": None},
        {"enchantment": 'Tenacity', "owner_prefix": None},
        {"enchantment": 'Vigor', "owner_prefix": None},
        {"enchantment": 'Vitality', "owner_prefix": None},
        {"enchantment": 'Barking', "owner_prefix": None},
        {"enchantment": 'Debarking', "owner_prefix": None},
    )

    def __init__(self):
        self.enchantment_state = []

    def preprocess(self, template, item):
        self.enchantment_state = []

        for enchantment in self.enchantments:
            self.enchantment_state.append({
                'enchantment': enchantment['enchantment'],
                'owner_prefix': enchantment['owner_prefix'],
                'enchant_found': False,
                'enchant_line': None,
                'players': []
            })

        if template.has_path('display.Lore'):
            for lore in template.iter_multipath('display.Lore[]'):
                for enchantment in self.enchantment_state:
                    lore_text = parse_name_possibly_json(lore.value)
                    if unformat_text(lore_text).startswith(enchantment['enchantment']):
                        enchantment['enchant_on_template'] = True

        for lore in item.nbt.iter_multipath('tag.display.Lore[]'):
            for enchantment in self.enchantment_state:
                owner_prefix = enchantment['owner_prefix']
                lore_text = unformat_text(parse_name_possibly_json(lore.value))
                if lore_text.startswith(enchantment['enchantment']):
                    enchantment['enchant_found'] = True
                    if not enchantment["enchantment"].startswith("Gilded"):
                        enchantment['enchant_line'] = lore_text
                    else:
                        enchantment['enchant_line'] = 'Gilded'
                if owner_prefix is not None and lore_text.startswith(owner_prefix):
                    if not enchantment["enchantment"].startswith("Gilded") or len(enchantment['players']) <= 0:
                        enchantment['players'].append(lore_text[len(owner_prefix)+1:])

    def postprocess(self, item):
        for enchantment in self.enchantment_state:
            enchant_found = enchantment['enchant_found']
            players = enchantment['players']
            enchant_line = enchantment['enchant_line']
            owner_prefix = enchantment['owner_prefix']

            if not enchant_found:
                continue

            if players:
                for player in players:
                   enchantify(item, player, enchant_line, owner_prefix=owner_prefix)
            else:
                # Apply the enchantment without saying who added it (workaround for past bug)
                enchantify(item, None, enchant_line, owner_prefix=None)

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
            shatter_item(item)

class PreserveSoulbound(GlobalRule):
    name = 'Preserve soulbound'

    def preprocess(self, template, item):
        self.player_line = None
        for lore in item.nbt.iter_multipath('tag.display.Lore[]'):
            lore_text = parse_name_possibly_json(lore.value)
            if unformat_text(lore_text).startswith("* Soulbound to "):
                self.player_line = lore
                return

    def postprocess(self, item):
        if self.player_line is None:
            return

        # Make sure tag exists first
        if not item.has_tag():
            item.tag = nbt.TagCompound({})
        if not item.tag.has_path('display'):
            item.tag.value['display'] = nbt.TagCompound({})
        if not item.tag.has_path('display.Lore'):
            item.tag.at_path('display').value['Lore'] = nbt.TagList([])

        # Apply soulbound lore
        item.tag.at_path('display.Lore').value.append(self.player_line)

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

################################################################################
# Global rules end

global_rules = GlobalRule.recursive_public_subclasses()

