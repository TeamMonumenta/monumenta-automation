import os
import sys

import traceback

from lib_py3.common import get_item_name_from_nbt, get_entity_name_from_nbt, parse_name_possibly_json, eprint
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
    pop_if_present(entity_nbt, 'Brain')
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
    pop_if_present(entity_nbt, 'Paper.SpawnReason')
    pop_if_present(entity_nbt, 'Paper.OriginWorld')
    pop_if_present(entity_nbt, 'Bukkit.Aware')
    pop_if_present(entity_nbt, 'HurtByTimestamp')
    pop_if_present(entity_nbt, 'InWaterTime')
    pop_if_present(entity_nbt, 'Team')

    # Recurse over passengers
    for entity in entity_nbt.iter_multipath('Passengers[]'):
        remove_unwanted_spawner_tags(entity)

class MobReplacementManager(object):
    """
    A tool to replace mobs while preserving certain data.
    """
    def __init__(self):
        # Replacement Map
        # For example:
        # _mob_map["wither_skeleton"]["Frost Moon Brute"] = TagCompound(...)
        self._mob_map = {}
        # Substitution List
        # For example:
        # _substitutions = [(lambda(mob) -> bool, replacement)]
        self._substitutions = []

        # Whether to always try all substitutions, even if a matching mob exists
        self._substitutions_forced = False

    def add_replacements(self, replacements: [nbt.TagCompound], allow_unwanted_spawner_tags=False) -> None:
        """
        Add additional replacements to the mob map

        Replacements should be a list of TagCompound objects
        """

        for mob in replacements:
            if mob.has_path('id'):
                mob_id = mob.at_path('id').value
            elif mob.has_path('Id'):
                mob_id = mob.at_path('Id').value
            else:
                raise Exception("Replacements mob missing 'id': {}".format(mob.to_mojangson()))

            mob_name = get_entity_name_from_nbt(mob)
            if not mob_name:
                raise Exception("Replacements mob missing 'CustomName': {}".format(mob.to_mojangson()))

            # Make a copy of the NBT so it can be manipulated without mangling the caller
            mob = mob.deep_copy()

            # Make sure replacements don't have junk spawner tags (unless desired)
            if not allow_unwanted_spawner_tags:
                remove_unwanted_spawner_tags(mob)

            # Create the dict for this mob_id if it doesn't already exist
            if mob_id not in self._mob_map:
                self._mob_map[mob_id] = {}

            # Check for dupes
            if mob_name in self._mob_map[mob_id]:
                raise Exception("Mob {} {!r} already exists in replacements".format(mob_id, mob_name))

            # Make sure this mob doesn't match any of the existing substitutions
            for sub_matcher, sub_mob in self._substitutions:
                if sub_matcher(mob):
                    raise Exception("New replacements mob {!r} matches existing substitution {!r}".format(mob_name, get_entity_name_from_nbt(sub_mob)))

            self._mob_map[mob_id][mob_name] = mob

    # This is needed to prevent re-replacing things that don't need replacing
    # What was happening before was:
    # - Iterate a top-level mob
    # - Replace that mob with the LoS version, which had a passenger that was outdated
    # - Iterate into the passenger, and replace it with the correct top-level replacement
    # - Save
    #
    # Problem is, next time when an nbt diff is done against a mob replacement
    # candidate, it looks like it needs replacing (because the nbt doesn't
    # match the LoS master)
    #
    # So - we need to run replacements pre-emptively on the master copy
    # passengers to ensure they're the same as what would ultimately end up
    # resulting to prevent false-positive matches
    #

    def recurse_replace(self, entity_nbt) -> int:
        replacements = 0
        if self.replace_mob(entity_nbt):
            from lib_py3.common import get_entity_name_from_nbt
            eprint(f"Incorrect passenger {get_entity_name_from_nbt(entity_nbt)}")
            replacements += 1

        for entity_nbt in entity_nbt.iter_multipath('Passengers[]'):
            replacements += self.recurse_replace(entity_nbt)

        return replacements

    def run_replacements_on_master_passengers(self) -> int:
        replacements = 0
        for mob_id in self._mob_map:
            mob_type = self._mob_map[mob_id]
            for mob_name in mob_type:
                replacements += self.recurse_replace(mob_type[mob_name])
        return replacements

    def add_substitutions(self, substitutions: [dict], force_add_ignoring_conflicts=False) -> None:
        """
        Add a substitution rule.
        The format should be:
        (
            "Mob Name",
            lambda(TagCompound) -> boolean
        )

        lambda function should return true when given a matching mob, and false otherwise

        lambda functions that match too broadly will trigger an exception
        """
        if force_add_ignoring_conflicts:
            self._substitutions_forced = True

        for sub in substitutions:
            replacement = None
            for mob_id in self._mob_map:
                for mob_name in self._mob_map[mob_id]:
                    if mob_name == sub[0]:
                        replacement = self._mob_map[mob_id][mob_name]
                    elif force_add_ignoring_conflicts and sub[1](self._mob_map[mob_id][mob_name]):
                        eprint("WARNING: Substitution for {!r} also matches mob {!r}".format(sub[0], mob_name))
                    elif sub[1](self._mob_map[mob_id][mob_name]):
                        # This substitution matches a different named mob in the replacements - critical error!
                        raise Exception("Substitution for {!r} also matches mob {!r}".format(sub[0], mob_name))

            if replacement is None:
                raise Exception("Substitution for {!r} missing replacement mob".format(sub[0]))

            self._substitutions.append((sub[1], replacement))

    # Returns True if the item was updated, False otherwise
    def replace_mob(self, mob, log_dict=None, debug_path="") -> bool:
        """
        Replace a mob with the version from the map (if any)
        """
        if mob.has_path('id'):
            mob_id = mob.at_path('id').value
        elif mob.has_path('Id'):
            mob_id = mob.at_path('Id').value
        else:
            return False

        new_nbt = None

        # Try the more efficient direct name update first
        mob_name = get_entity_name_from_nbt(mob)
        if mob_name:
            new_nbt = self._mob_map.get(mob_id,{}).get(mob_name,None)
        else:
            mob_name = "<nameless>"

        if not new_nbt or self._substitutions_forced:
            # No luck with exact name/id match replacement - try substitutions

            # Linear performance with substitutions, so keep the list short!
            for sub_matcher, sub_mob in self._substitutions:
                if sub_matcher(mob):
                    new_nbt = sub_mob
                    break

            # No substitution found - abort
            if new_nbt is None:
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
                    log_dict[log_key]["FROM"][orig_mojangson] = []

                log_dict[log_key]["FROM"][orig_mojangson].append(debug_path)

            mob.value = new_nbt.deep_copy().value

            return True

        # No update needed
        return False
