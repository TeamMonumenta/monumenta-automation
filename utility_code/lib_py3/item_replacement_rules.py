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
            enchantmentFound = True

        loreStripped = unformat_text(loreText)
        HEADER_LORE = ("King's Valley :", "Celsian Isles :", "Monumenta :", "Armor", "Magic Wand")
        if not enchantmentFound and (
            any(x in loreStripped for x in HEADER_LORE) or
            len(loreStripped) == 0
        ):
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

class _PreserveEnchantmentBase(GlobalRule):
    name = 'Preserve Enchantment Base (SHOULD NOT BE USED DIRECTLY)'
    enchantment = '§7Enchantment'
    owner_prefix = None
    # This, but requiring a space at the beginning, while still matching an empty string.
    # Also matches a single space, requiring a final check.
    # https://stackoverflow.com/a/267405
    _RE_ROMAN_NUMERAL = re.compile(r'''^( M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3}))?$''')

    def __init__(self):
        self.enchant_found = False
        self.enchant_level = None
        self.player = None

    def _get_enchant_level(self, lore):
        """Return the string that represents the enchantment level.

        An empty string "" is a valid level - the default of 1.
        Returns None if the enchantment doesn't match.
        """
        if not lore.startswith(self.enchantment):
            return None

        enchant_level = lore[len(self.enchantment):]
        if self._RE_ROMAN_NUMERAL.match(enchant_level):
            if enchant_level == ' ':
                return None
            else:
                return enchant_level
        else:
            return None

    def preprocess(self, template, item):
        self.enchant_found = False
        self.enchant_level = None
        self.player = None

        if template.has_path('display.Lore'):
            for lore in template.at_path('display.Lore').value:
                if lore.value.startswith(self.enchantment):
                    # Don't apply the enchant if it already exists
                    return

        if item.has_path('tag.display.Lore'):
            for lore in item.at_path('tag.display.Lore').value:
                if self.enchantment in lore.value:
                    self.enchant_found = True
                    self.enchant_level = self._get_enchant_level(lore.value)
                if self.owner_prefix is not None and self.owner_prefix in lore.value:
                    self.player = lore.value[len(self.owner_prefix)+1:]

    def postprocess(self, item):
        if not self.enchant_found:
            return

        if self.player:
            enchantify(item, self.player, self.enchantment + self.enchant_level, owner_prefix=self.owner_prefix)
        else:
            # Apply the enchantment without saying who added it (workaround for previous bug)
            enchantify(item, self.player, self.enchantment + self.enchant_level, owner_prefix=None)

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

class PreserveHope(_PreserveEnchantmentBase):
    name = 'Preserve Hope'
    enchantment = '§7Hope'
    owner_prefix = 'Infused by'

class PreserveGilded(_PreserveEnchantmentBase):
    name = 'Preserve Gilded'
    enchantment = '§7Gilded'
    owner_prefix = 'Gilded by'

class PreserveFestive(_PreserveEnchantmentBase):
    name = 'Preserve Festive'
    enchantment = '§7Festive'
    owner_prefix = 'Decorated by'

    wrongPrefix = "Infused by"

    def preprocess(self, template, item):
        super().preprocess(template, item)

        if self.enchant_found and not self.player:
            for lore in item.at_path('tag.display.Lore').value:
                if self.wrongPrefix in lore.value:
                    self.player = lore.value[len(self.wrongPrefix)+1:]
                    return

class PreserveAcumen(_PreserveEnchantmentBase):
    name = 'Preserve Acumen'
    enchantment = '§7Acumen'

class PreserveFocus(_PreserveEnchantmentBase):
    name = 'Preserve Focus'
    enchantment = '§7Focus'

class PreservePerspicacity(_PreserveEnchantmentBase):
    name = 'Preserve Perspicacity'
    enchantment = '§7Perspicacity'

class PreserveTenacity(_PreserveEnchantmentBase):
    name = 'Preserve Tenacity'
    enchantment = '§7Tenacity'

class PreserveVigor(_PreserveEnchantmentBase):
    name = 'Preserve Vigor'
    enchantment = '§7Vigor'

class PreserveVitality(_PreserveEnchantmentBase):
    name = 'Preserve Vitality'
    enchantment = '§7Vitality'

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

