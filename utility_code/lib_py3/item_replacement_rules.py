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
    self.name = "Undefined global rule"

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
    self.name = "Abort if there's no lore text"

    def preprocess(self,item):
        if not item.has_path('tag.display.Lore'):
            'Abort!'
            return True

global_rules.append(abort_no_lore())

class preserve_armor_color(global_rule):
    self.name = 'Preserve armor color'

    def __init__(self):
        self.color = None

    def preprocess(self,item):
        if item.has_path('tag.display.color'):
            self.color = item.at_path('tag.display.color').value
        else
            self.color = None

    def postprocess(self,item):
        if not self.lore:
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
    self.name = 'Preserve damage'

    def __init__(self):
        self.damage = None

    def preprocess(self,item):
        if item.has_path('tag.Damage'):
            self.damage = item.at_path('tag.Damage').value
        else
            self.damage = None

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
    self.name = 'Preserve lore'

    def __init__(self):
        self.lore = None

    def preprocess(self,item):
        if item.has_path('tag.display.Lore'):
            self.lore = item.at_path('tag.display.Lore').value
        else
            self.lore = None

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
    self.name = 'Preserve shield banner'

    def __init__(self):
        self.color = None
        self.pattern = None

    def preprocess(self,item):
        # banner base color
        if item.has_path('tag.BlockEntityTag.Base'):
            self.pattern = item.at_path('tag.BlockEntityTag.Base').value
        else:
            self.pattern = None

        # banner patterns
        if item.has_path('tag.BlockEntityTag.Patterns'):
            self.color = item.at_path('tag.BlockEntityTag.Patterns').value
        else
            self.color = None

    def postprocess(self,item):
        # Remove banner if the player customized it as such
        if self.color is None and item.has_path('tag.BlockEntityTag.Base'):
            item.at_path('tag.BlockEntityTag').value.pop('Base')
        if self.pattern is None and item.has_path('tag.BlockEntityTag.Patterns'):
            item.at_path('tag.BlockEntityTag').value.pop('Patterns')

        # Add custom banner if the player applied one
        if ( self.color not is None) and ( self.pattern is not None ):
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

global_rules.append(preserve_shield_banner())

