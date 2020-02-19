#!/usr/bin/env python3

import os
import sys

import traceback

from lib_py3.common import get_item_name_from_nbt, get_entity_name_from_nbt, parse_name_possibly_json
from lib_py3.item_replacement_rules import global_rules
from lib_py3.item_replacement_substitutions import substitution_rules

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types import nbt

def pop_if_present(entity_nbt: nbt.TagCompound, key: str):
    if isinstance(entity_nbt, nbt.TagCompound) and key in entity_nbt.value:
        name = get_entity_name_from_nbt(entity_nbt)
        entity_nbt.value.pop(key)

def remove_unwanted_spawner_tags(entity_nbt: nbt.TagCompound):
    pop_if_present(entity_nbt, 'Pos')
    pop_if_present(entity_nbt, 'Leashed')
    pop_if_present(entity_nbt, 'Air')
    pop_if_present(entity_nbt, 'OnGround')
    pop_if_present(entity_nbt, 'Dimension')
    pop_if_present(entity_nbt, 'Rotation')
    pop_if_present(entity_nbt, 'WorldUUIDMost')
    pop_if_present(entity_nbt, 'WorldUUIDLeast')
    pop_if_present(entity_nbt, 'HurtTime')
    pop_if_present(entity_nbt, 'HurtByTimestamp')
    pop_if_present(entity_nbt, 'FallFlying')
    pop_if_present(entity_nbt, 'PortalCooldown')
    pop_if_present(entity_nbt, 'FallDistance')
    pop_if_present(entity_nbt, 'DeathTime')
    pop_if_present(entity_nbt, 'HandDropChances')
    pop_if_present(entity_nbt, 'ArmorDropChances')
    pop_if_present(entity_nbt, 'CanPickUpLoot')
    pop_if_present(entity_nbt, 'Bukkit.updateLevel')
    pop_if_present(entity_nbt, 'Spigot.ticksLived')
    pop_if_present(entity_nbt, 'Paper.AAAB')
    pop_if_present(entity_nbt, 'Paper.Origin')
    pop_if_present(entity_nbt, 'Paper.FromMobSpawner')
    pop_if_present(entity_nbt, 'Team')

    # Recurse over passengers
    if (entity_nbt.has_path('Passengers')):
        remove_unwanted_spawner_tags(entity_nbt.at_path('Passengers'))

class MobReplacementManager(object):
    """
    A tool to replace mobs while preserving certain data.
    """
    def __init__(self):
        # Replacement Map
        # For example:
        # _mob_map["wither_skeleton"]["Frost Moon Brute"] = TagCompound(...)
        self._mob_map = {}

    def add_replacements(self, replacements: [nbt.TagCompound], allow_unwanted_spawner_tags=False):
        """
        Add additional replacements to the mob map

        Replacements should be a list of TagCompound objects
        """
        for mob in replacements:
            if not mob.has_path('id'):
                raise Exception("Replacements mob missing 'id': {}".format(mob.to_mojangson()))
            mob_id = mob.at_path('id').value

            mob_name = get_entity_name_from_nbt(mob)
            if not mob_name:
                raise Exception("Replacements mob missing 'CustomName': {}".format(mob.to_mojangson()))

            # Make a copy of the NBT so it can be manipulated without mangling the caller
            mob = mob.deep_copy()

            if not allow_unwanted_spawner_tags:
                remove_unwanted_spawner_tags(mob)

            # Looks good - add it to the map
            if mob_id not in self._mob_map:
                self._mob_map[mob_id] = {}
            self._mob_map[mob_id][mob_name] = mob

    # Returns True if the item was updated, False otherwise
    def replace_mob(self, mob, log_dict=None, debug_path=""):
        """
        Replace a mob with the version from the map (if any)
        """
        if not mob.has_path('id'):
            return False
        mob_id = mob.at_path('id').value

        mob_name = get_entity_name_from_nbt(mob)
        if not mob_name:
            return False

        # TODO: Mob substitutions go here

        new_nbt = self._mob_map.get(mob_id,{}).get(mob_name,None)
        if not new_nbt:
            return False

        # Inexact comparison is sufficient - ordering does not matter for mobs
        if not mob == new_nbt:
            # mob needs to be updated
            if log_dict is not None:
                log_key = mob_name + "  " + mob_id
                if log_key not in log_dict:
                    log_dict[log_key] = {}

                    log_dict[log_key]["NAME"] = mob_name
                    log_dict[log_key]["ID"] = mob_id
                    log_dict[log_key]["TO"] = new_nbt.to_mojangson()
                    log_dict[log_key]["FROM"] = {}

                orig_mojangson = mob.to_mojangson()

                if orig_mojangson not in log_dict[log_key]["FROM"]:
                    log_dict[log_key]["FROM"][orig_mojangson] = set()

                log_dict[log_key]["FROM"][orig_mojangson].add(debug_path)

            mob.value = new_nbt.deep_copy().value

            return True

        # No update needed
        return False
