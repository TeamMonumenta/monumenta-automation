import sys
import os
import json
import time
import re
from pprint import pformat
from lib_py3.common import parse_name_possibly_json, eprint
from lib_py3.upgrade import upgrade_entity
from lib_py3.mob_replacement_manager import MobReplacementManager

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))

from quarry.types import nbt
from quarry.types.nbt import TagCompound
from quarry.types.text_format import unformat_text


class LibraryOfSouls(object):
    def __init__(self, path: str, readonly=False):
        self._path = path
        self._souls = []
        self._index = None
        self._readonly = readonly

        with open(path, "r") as fp:
            self._souls = json.load(fp)

    def clear_tags(self) -> None:
        for soul_entry in self._souls:
            if "tags" in soul_entry:
                soul_entry.pop("tags")
            if "location_names" in soul_entry:
                soul_entry.pop("location_names")

    def refresh_index(self) -> None:
        self._index = {}

        new_souls = []
        for soul_entry in self._souls:
            soul_nbt = nbt.TagCompound.from_mojangson(soul_entry["history"][0]["mojangson"])

            if not soul_nbt.has_path("CustomName"):
                eprint("WARNING: Souls database entry is missing a name: {}".format(pformat(soul_entry)))
                continue
            else:
                name = unformat_text(parse_name_possibly_json(soul_nbt.at_path("CustomName").value))
                self._index[name] = soul_entry

            new_souls.append(soul_entry)

        self._souls = new_souls

    def get_soul(self, name: str) -> dict:
        if self._index is None:
            self.refresh_index()

        if name in self._index:
            return self._index[name]
        return None

    def get_soul_current_nbt(self, name: str) -> TagCompound:
        if self._index is None:
            self.refresh_index()

        if name in self._index:
            return nbt.TagCompound.from_mojangson(self._index[name]["history"][0]["mojangson"])
        return None

    # Add a soul to the database, and return its label for /los summon
    def add_soul(self, soul_nbt: TagCompound) -> str:
        if self._readonly:
            raise Exception("Attempted to save read-only Library of Souls")
        if self._index is None:
            self.refresh_index()

        # Make sure this NBT data is up to date, also prunes junk tags
        soul_nbt = self.upgrade_nbt(soul_nbt)

        if not soul_nbt.has_path("CustomName"):
            raise ValueError("Attempted to add souls database entity with no name")

        name = unformat_text(parse_name_possibly_json(soul_nbt.at_path("CustomName").value))
        los_summon_name = re.sub("[^a-zA-Z0-9]", "", name)

        if not name:
            raise ValueError("Attempted to add souls database entity with no name")

        if name in self._index:
            other = self.get_soul(name)
            other_nbt = nbt.TagCompound.from_mojangson(other["history"][0]["mojangson"])

            if other_nbt == soul_nbt:
                # Didn't need to add, it's already there and the same
                return los_summon_name
            raise ValueError(f"Attempted to add souls database entity '{name}' that already exists")

        soul_entry = {}
        hist_element = {}
        hist_element["mojangson"] = soul_nbt.to_mojangson()
        hist_element["modified_on"] = int(time.time())
        soul_entry["history"] = [hist_element, ]
        self._index[name] = soul_entry
        self._souls.append(soul_entry)

        return los_summon_name

    @classmethod
    def is_mob_riding_itself(cls, soul_nbt: TagCompound, bad_names: [str]) -> bool:
        if soul_nbt.has_path("CustomName"):
            name = unformat_text(parse_name_possibly_json(soul_nbt.at_path("CustomName").value))
            if len(name) > 0 and name in bad_names:
                return True
            bad_names.append(name)

        if soul_nbt.has_path("Passengers"):
            for passenger in soul_nbt.at_path("Passengers").value:
                return cls.is_mob_riding_itself(passenger, bad_names)

        return False


    def load_replacements(self, mgr: MobReplacementManager) -> None:
        if self._index is None:
            self.refresh_index()

        current_nbt = []
        for name in self._index:
            soul_nbt = self.get_soul_current_nbt(name)
            if self.is_mob_riding_itself(soul_nbt, []):
                eprint(f"WARNING: mob {name} is riding itself! Will not replace this mob")
                continue

            current_nbt.append(soul_nbt)

        mgr.add_replacements(current_nbt)
        mgr.run_replacements_on_master_passengers()

    def save(self) -> None:
        if self._readonly:
            raise Exception("Attempted to save read-only Library of Souls")
        with open(self._path, "w") as fp:
            json.dump(self._souls, fp, ensure_ascii=False, sort_keys=False, indent=2, separators=(',', ': '))

    @classmethod
    def upgrade_nbt(cls, soul_nbt: TagCompound) -> TagCompound:
        upgrade_entity(soul_nbt, False, ('Pos', 'Leashed', 'Air', 'OnGround', 'Dimension', 'Rotation', 'WorldUUIDMost',
                     'WorldUUIDLeast', 'HurtTime', 'HurtByTimestamp', 'FallFlying', 'PortalCooldown',
                     'FallDistance', 'DeathTime', 'HandDropChances', 'ArmorDropChances', 'CanPickUpLoot',
                     'Bukkit.updateLevel', 'Spigot.ticksLived', 'Paper.AAAB', 'Paper.Origin',
                     'Paper.FromMobSpawner', 'Brain', 'Paper.SpawnReason', 'Bukkit.Aware',
                     'Paper.ShouldBurnInDay', 'Paper.CanTick', 'Bukkit.MaxDomestication'))

        for junk in ('UUID', ):
            if soul_nbt.has_path(junk):
                soul_nbt.value.pop(junk)

        if soul_nbt.has_path("Passengers"):
            for passenger in soul_nbt.at_path("Passengers").value:
                for junk in ('UUID', ):
                    if passenger.has_path(junk):
                        passenger.value.pop(junk)

        for string_tag in soul_nbt.iter_multipath('Tags[]'):
            for old_part, new_part in (
                ('rejuvination', 'rejuvenation'),
                ('Rejuvination', 'Rejuvenation'),
                ('REJUVINATION', 'REJUVENATION'),
            ):
                if old_part in string_tag.value:
                    string_tag.value = string_tag.value.replace(old_part, new_part)

        return soul_nbt

    def upgrade_all(self) -> None:
        for soul_entry in self._souls:
            for history_entry in soul_entry["history"]:
                soul_nbt = nbt.TagCompound.from_mojangson(history_entry["mojangson"])
                history_entry["mojangson"] = self.upgrade_nbt(soul_nbt).to_mojangson()

