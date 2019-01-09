#!/usr/bin/env python3

import os
import sys

import traceback

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types import nbt

global_rules = []

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

    def preprocess(self,item):
        """
        Read the unedited item.
        Return True to abort replacement and changes.
        Make no edits here.
        """
        pass

    def postprocess(self,item):
        """
        Edit the item with last stored value
        """
        pass

class abort_no_lore(global_rule):
    name = "Abort if there's no lore text"

    def preprocess(self,item):
        if not item.has_path('tag.display.Lore'):
            'Abort!'
            return True

global_rules.append(abort_no_lore())

class preserve_armor_color(global_rule):
    name = 'Preserve armor color'

    def preprocess(self,item):
        self.color = None
        if item.has_path('tag.display.color'):
            self.color = item.at_path('tag.display.color').value

    def postprocess(self,item):
        if not self.color:
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

    def preprocess(self,item):
        self.damage = None
        if item.has_path('tag.Damage'):
            self.damage = item.at_path('tag.Damage').value

    def postprocess(self,item):
        if not self.damage:
            return

        # Make sure tag exists first
        if not item.has_path('tag'):
            item.value['tag'] = nbt.TagCompound({})
        if not item.has_path('tag.Damage'):
            item.at_path('tag').value['Damage'] = nbt.TagInt(0)

        # Apply damage
        item.at_path('tag.Damage').value = self.damage

global_rules.append(preserve_damage())

class preserve_lore(global_rule):
    name = 'Preserve lore'
    _lore_preserve_trigger_list = (
        'Soulbound to',
        'Infused by',
        'Gilded by',
        'Decorated by',
        '§7Hope',
        '§7Gilded',
        '§7Festive',
    )

    def preprocess(self,item):
        self.lore = None
        if item.has_path('tag.display.Lore'):
            for lore in item.at_path('tag.display.Lore').value:
                for lore_trigger in self._lore_preserve_trigger_list:
                    if lore_trigger in lore.value:
                        self.lore = item.at_path('tag.display.Lore').value
                        return

    def postprocess(self,item):
        if not self.lore:
            return

        # Make sure tag exists first
        if not item.has_path('tag'):
            item.value['tag'] = nbt.TagCompound({})
        if not item.has_path('tag.display'):
            item.at_path('tag').value['display'] = nbt.TagCompound({})
        if not item.has_path('tag.display.Lore'):
            item.at_path('tag.display').value['Lore'] = nbt.TagList([])

        # Apply lore
        item.at_path('tag.display.Lore').value = self.lore

global_rules.append(preserve_lore())

class preserve_shield_banner(global_rule):
    name = 'Preserve shield banner'

    def preprocess(self,item):
        self.color = None
        self.pattern = None

        # banner base color
        if item.has_path('tag.BlockEntityTag.Base'):
            self.color = item.at_path('tag.BlockEntityTag.Base').value

        # banner patterns
        if item.has_path('tag.BlockEntityTag.Patterns'):
            self.pattern = item.at_path('tag.BlockEntityTag.Patterns').value

    def postprocess(self,item):
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
