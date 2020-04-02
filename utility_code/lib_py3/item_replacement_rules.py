#!/usr/bin/env python3

import os
import re
import sys

import traceback

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types import nbt
from quarry.types.text_format import unformat_text

class GlobalRule(object):
    """
    Base pre/post processing rule for item replacements, used to preserve and edit data.
    """
    # Edit this for all new objects:
    name = "Undefined global rule"

    def __init__(self):
        """
        Local data storage
        """
        pass

    def preprocess(self, template, item):
        """
        Read the unedited item.
        Return True to abort replacement and changes.
        Make no edits here.
        """
        pass

    def postprocess(self, item):
        """
        Edit the item with last stored value
        """
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

def enchantify(item, player, enchantment, owner_prefix=None, TEMPLORE=False):
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
    if not item.has_path('tag.display.Lore'):
        return
    lore = item.at_path('tag.display.Lore').value

    if len(lore) == 0:
        return

    newLore = []
    enchantmentFound = False
    nameAdded = (owner_prefix is None)
    for loreEntry in lore:
        loreText = loreEntry.value
        if (enchantment) in loreText:
            if TEMPLORE:
                newLore.append(nbt.TagString("PRE COST ADJUST"))
            enchantmentFound = True

        loreStripped = unformat_text(loreText)
        HEADER_LORE = ("King's Valley :", "Celsian Isles :", "Monumenta :", "Armor", "Magic Wand")
        if not enchantmentFound and (
            any(x in loreStripped for x in HEADER_LORE) or
            len(loreStripped) == 0
        ):
            if TEMPLORE:
                newLore.append(nbt.TagString("PRE COST ADJUST"))
            newLore.append(nbt.TagString(enchantment))
            enchantmentFound = True

        if (not nameAdded and len(loreStripped) == 0):
            newLore.append(nbt.TagString(owner_prefix + " " + player))
            nameAdded = True

        newLore.append(nbt.TagString(loreText))

    if not enchantmentFound:
        # Don't apply changes
        return

    if not nameAdded:
        newLore.append(nbt.TagString(owner_prefix + " " + player))

    item.at_path('tag.display.Lore').value = newLore

def shatter_item(item):
    """Applies shattered enchantment to an item

    Must be kept in sync with plugin version!

    Note that the logic to check if the item *should*
    be shattered is skipped here, as this will only
    be called if the item definitely should be
    shattered.

    item is an item stack, including id and Count.
    """

    if not item.has_path('tag'):
        item.value['tag'] = nbt.TagCompound({})
    if not item.has_path('tag.display'):
        item.at_path('tag').value['display'] = nbt.TagCompound({})
    if not item.has_path('tag.display.Lore'):
        item.at_path('tag.display').value['Lore'] = nbt.TagList([])

    lore = item.at_path('tag.display.Lore').value

    lore.append(nbt.TagString("§4§l* SHATTERED *"))
    lore.append(nbt.TagString("§4Maybe a Master Repairman"))
    lore.append(nbt.TagString("§4could reforge it..."))

################################################################################
# Global rules begin

class AbortNoLore(GlobalRule):
    name = "Abort if there's no lore text"

    def preprocess(self, template, item):
        if not item.has_path('tag.display.Lore'):
            'Abort!'
            return True

class PreserveArmorColor(GlobalRule):
    name = 'Preserve armor color'

    def preprocess(self, template, item):
        self.color = None
        if item.has_path('tag.display.color'):
            self.color = item.at_path('tag.display.color').value

    def postprocess(self, item):
        if self.color is None:
            if item.has_path('tag.display.color'):
                item.at_path('tag.display').value.pop('color')
            return

        # Make sure tag exists first
        if not item.has_path('tag'):
            item.value['tag'] = nbt.TagCompound({})
        if not item.has_path('tag.display'):
            item.at_path('tag').value['display'] = nbt.TagCompound({})
        if not item.has_path('tag.display.color'):
            item.at_path('tag.display').value['color'] = nbt.TagInt(0)

        # Apply color
        item.at_path('tag.display.color').value = self.color

class PreserveDamage(GlobalRule):
    name = 'Preserve damage'

    def preprocess(self, template, item):
        self.damage = None
        if item.has_path('tag.Damage'):
            self.damage = item.at_path('tag.Damage').value

    def postprocess(self, item):
        if self.damage is None:
            if item.has_path('tag.Damage'):
                item.at_path('tag').value.pop('Damage')
            return

        # Make sure tag exists first
        if not item.has_path('tag'):
            item.value['tag'] = nbt.TagCompound({})
        if not item.has_path('tag.Damage'):
            item.at_path('tag').value['Damage'] = nbt.TagInt(0)

        # Apply damage
        item.at_path('tag.Damage').value = self.damage

class PreserveEnchantments(GlobalRule):
    name = 'Preserve Enchantments'
    enchantments = (
        {"enchantment": '§7Hope', "owner_prefix": 'Infused by', "TEMPLORE": False},
        {"enchantment": '§7Gilded', "owner_prefix": 'Gilded by', "TEMPLORE": False},
        {"enchantment": '§7Festive', "owner_prefix": 'Decorated by', "TEMPLORE": False},
        {"enchantment": '§7Acumen', "owner_prefix": None, "TEMPLORE": True},
        {"enchantment": '§7Focus', "owner_prefix": None, "TEMPLORE": True},
        {"enchantment": '§7Perspicacity', "owner_prefix": None, "TEMPLORE": True},
        {"enchantment": '§7Tenacity', "owner_prefix": None, "TEMPLORE": True},
        {"enchantment": '§7Vigor', "owner_prefix": None, "TEMPLORE": True},
        {"enchantment": '§7Vitality', "owner_prefix": None, "TEMPLORE": True},
    )

    def __init__(self):
        self.enchantment_state = []

    def preprocess(self, template, item):
        self.enchantment_state = []

        for enchantment in self.enchantments:
            self.enchantment_state.append({
                'enchantment': enchantment['enchantment'],
                'owner_prefix': enchantment['owner_prefix'],
                'TEMPLORE': enchantment['TEMPLORE'],
                'enchant_on_template': False,
                'enchant_found': False,
                'enchant_line': None,
                'player': None
            })

        if template.has_path('display.Lore'):
            for lore in template.at_path('display.Lore').value:
                for enchantment in self.enchantment_state:
                    if lore.value.startswith(enchantment['enchantment']):
                        enchantment['enchant_on_template'] = True

        if item.has_path('tag.display.Lore'):
            for lore in item.at_path('tag.display.Lore').value:
                for enchantment in self.enchantment_state:
                    if enchantment['enchant_on_template']:
                        # Don't apply the enchant if it already exists
                        continue
                    owner_prefix = enchantment['owner_prefix']
                    if lore.value.startswith(enchantment['enchantment']):
                        enchantment['enchant_found'] = True
                        enchantment['enchant_line'] = lore.value
                    if owner_prefix is not None and lore.value.startswith(owner_prefix):
                        enchantment['player'] = lore.value[len(owner_prefix)+1:]

    def postprocess(self, item):
        for enchantment in self.enchantment_state:
            enchant_found = enchantment['enchant_found']
            player = enchantment['player']
            enchant_line = enchantment['enchant_line']
            owner_prefix = enchantment['owner_prefix']

            if not enchant_found:
                continue

            if player:
                enchantify(item, player, enchant_line, owner_prefix=owner_prefix, TEMPLORE=enchantment['TEMPLORE'])
            else:
                # Apply the enchantment without saying who added it (workaround for past bug)
                enchantify(item, player, enchant_line, owner_prefix=None, TEMPLORE=enchantment['TEMPLORE'])

class PreserveShattered(GlobalRule):
    name = 'Preserve Shattered'
    enchantment = "§4§l* SHATTERED *"

    def preprocess(self, template, item):
        self.shattered = False

        if not item.has_path('tag.display.Lore'):
            return

        for lore in item.at_path('tag.display.Lore').value:
            if lore.value == self.enchantment:
                self.shattered = True
                return

    def postprocess(self, item):
        if self.shattered:
            shatter_item(item)

class PreserveSoulbound(GlobalRule):
    name = 'Preserve soulbound'

    def preprocess(self, template, item):
        self.player_line = None
        if item.has_path('tag.display.Lore'):
            for lore in item.at_path('tag.display.Lore').value:
                if lore.value.startswith("* Soulbound to "):
                    self.player_line = lore
                    return

    def postprocess(self, item):
        if self.player_line is None:
            return

        # Make sure tag exists first
        if not item.has_path('tag'):
            item.value['tag'] = nbt.TagCompound({})
        if not item.has_path('tag.display'):
            item.at_path('tag').value['display'] = nbt.TagCompound({})
        if not item.has_path('tag.display.Lore'):
            item.at_path('tag.display').value['Lore'] = nbt.TagList([])

        # Apply soulbound lore
        item.at_path('tag.display.Lore').value.append(self.player_line)

class PreserveBlockEntityTag(GlobalRule):
    name = 'Preserve shield banner'

    def preprocess(self, template, item):
        self.block_entity_tag = None
        if item.has_path('tag.BlockEntityTag'):
            self.block_entity_tag = item.at_path('tag.BlockEntityTag')

            # Some legacy items have this invalid tag.BlockEntityTag.id field
            if self.block_entity_tag.has_path('id'):
                self.block_entity_tag.value.pop('id')

    def postprocess(self, item):
        if item.has_path('tag.BlockEntityTag'):
            item.at_path('tag').value.pop('BlockEntityTag')

        if self.block_entity_tag is not None:
            if not item.has_path('tag'):
                item.value['tag'] = nbt.TagCompound({})
            item.at_path('tag').value['BlockEntityTag'] = self.block_entity_tag

################################################################################
# Global rules end

global_rules = GlobalRule.recursive_public_subclasses()

