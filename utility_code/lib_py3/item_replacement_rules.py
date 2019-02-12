#!/usr/bin/env python3

import os
import sys

import traceback

from lib_py3.common import eprint

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types import nbt
from quarry.types.text_format import unformat_text

class global_rule(object):
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

def enchantify(item, player, region, enchantment, owner_prefix=None):
    """
    Applies a lore-text enchantment to item (full item nbt, including id and Count). Lore format is:
    ```
    ...
    enchantment
    ...
    owner_prefix player
    ...
    ```
    region is the relevant region name, such as "King's Valley"
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
    regionFound = False
    for loreEntry in lore:
        loreEntry = loreEntry.value
        if ( enchantment ) in loreEntry:
            enchantmentFound = True

        if region in loreEntry:
            regionFound = True

        loreStripped = unformat_text(loreEntry)

        if (not enchantmentFound and (region in loreEntry or
                                      "Armor" in loreEntry or
                                      "Magic Wand" in loreEntry or
                                      len(loreStripped) == 0)):
            newLore.append(nbt.TagString(enchantment))
            enchantmentFound = True

        if (not nameAdded and len(loreStripped) == 0):
            newLore.append(nbt.TagString(owner_prefix + " " + player))
            nameAdded = True

        newLore.append(nbt.TagString(loreEntry))

    if not nameAdded:
        newLore.append(nbt.TagString(owner_prefix + " " + player))

    if not regionFound:
        return

    item.at_path('tag.display.Lore').value = newLore

class preserve_enchantment_base(global_rule):
    name = 'Preserve Enchantment Base (SHOULD NOT BE USED DIRECTLY)'
    region = "King's Valley"
    enchantment = '§7Enchantment'
    owner_prefix = 'Whatever by'

    def preprocess(self, template, item):
        self.enchant_found = False
        self.player = None

        if template.has_path('display.Lore'):
            for lore in template.at_path('display.Lore').value:
                if self.enchantment in lore.value:
                    # Don't apply the enchant if it already exists
                    return

        if item.has_path('tag.display.Lore'):
            for lore in item.at_path('tag.display.Lore').value:
                if self.enchantment in lore.value:
                    self.enchant_found = True
                if self.owner_prefix in lore.value:
                    self.player = lore.value[len(self.owner_prefix)+1:]

    def postprocess(self, item):
        if self.enchant_found is False:
            return

        if self.player:
            enchantify(item, self.player, self.region, self.enchantment, owner_prefix=self.owner_prefix)
        else:
            # Apply the enchantment without saying who added it (workaround for previous bug)
            enchantify(item, self.player, self.region, self.enchantment, owner_prefix=None)

global_rules = []

class abort_no_lore(global_rule):
    name = "Abort if there's no lore text"

    def preprocess(self, template, item):
        if not item.has_path('tag.display.Lore'):
            'Abort!'
            return True

global_rules.append(abort_no_lore())

class preserve_armor_color(global_rule):
    name = 'Preserve armor color'

    def preprocess(self, template, item):
        self.color = None
        if item.has_path('tag.display.color'):
            self.color = item.at_path('tag.display.color').value

    def postprocess(self, item):
        if self.color is None:
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

global_rules.append(preserve_armor_color())

class preserve_damage(global_rule):
    name = 'Preserve damage'

    def preprocess(self, template, item):
        self.damage = None
        if item.has_path('tag.Damage'):
            self.damage = item.at_path('tag.Damage').value

    def postprocess(self, item):
        if self.damage is None:
            return

        # Make sure tag exists first
        if not item.has_path('tag'):
            item.value['tag'] = nbt.TagCompound({})
        if not item.has_path('tag.Damage'):
            item.at_path('tag').value['Damage'] = nbt.TagInt(0)

        # Apply damage
        item.at_path('tag.Damage').value = self.damage

global_rules.append(preserve_damage())

class preserve_hope(preserve_enchantment_base):
    name = 'Preserve Hope'
    enchantment = '§7Hope'
    owner_prefix = 'Infused by'

global_rules.append(preserve_hope())

class preserve_gilded(preserve_enchantment_base):
    name = 'Preserve Gilded'
    enchantment = '§7Gilded'
    owner_prefix = 'Gilded by'

global_rules.append(preserve_gilded())

class preserve_festive(preserve_enchantment_base):
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

global_rules.append(preserve_festive())

class preserve_soulbound(global_rule):
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

global_rules.append(preserve_soulbound())

class preserve_shield_banner(global_rule):
    name = 'Preserve shield banner'

    def preprocess(self, template, item):
        self.color = None
        self.pattern = None

        # banner base color
        if item.has_path('tag.BlockEntityTag.Base'):
            self.color = item.at_path('tag.BlockEntityTag.Base').value

        # banner patterns
        if item.has_path('tag.BlockEntityTag.Patterns'):
            self.pattern = item.at_path('tag.BlockEntityTag.Patterns').value

    def postprocess(self, item):
        # Remove banner if the player customized it as such
        if item.has_path('tag.BlockEntityTag.Base'):
            item.at_path('tag.BlockEntityTag').value.pop('Base')
        if item.has_path('tag.BlockEntityTag.Patterns'):
            item.at_path('tag.BlockEntityTag').value.pop('Patterns')

        # Add custom banner if the player applied one
        if ( self.color is not None ) or ( self.pattern is not None ):
            if not item.has_path('tag'):
                item.value['tag'] = nbt.TagCompound({})
            if not item.has_path('tag.BlockEntityTag'):
                item.at_path('tag').value['BlockEntityTag'] = nbt.TagCompound({})

        if self.color is not None:
            if not item.has_path('tag.BlockEntityTag.Base'):
                item.at_path('tag.BlockEntityTag').value['Base'] = nbt.TagInt(0)
            item.at_path('tag.BlockEntityTag.Base').value = self.color

        if self.pattern is not None:
            if not item.has_path('tag.BlockEntityTag.Patterns'):
                item.at_path('tag.BlockEntityTag').value['Patterns'] = nbt.TagList([])
            item.at_path('tag.BlockEntityTag.Patterns').value = self.pattern

        if item.has_path('tag.BlockEntityTag') and len(item.at_path('tag.BlockEntityTag').value.keys()) == 0:
            item.at_path('tag').value.pop('BlockEntityTag')

global_rules.append(preserve_shield_banner())
