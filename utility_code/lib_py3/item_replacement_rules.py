#!/usr/bin/env python3

import os
import sys

import traceback

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
    if self.damage:
      # Make sure tag exists first, though.
      item.at_path('tag.Damage').value = self.damage
global_rules.append(preserve_damage())

