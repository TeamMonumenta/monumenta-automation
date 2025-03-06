import os
import sys

from lib_py3.common import get_item_name_from_nbt
from lib_py3.common import parse_name_possibly_json
from lib_py3.common import mark_dirty
from lib_py3.common import update_plain_tag

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types.text_format import unformat_text
from quarry.types import nbt

class SubstitutionRule():
    """Base substitution rule for item replacements, used to preserve and edit data."""
    # Edit this for all new objects:
    name = "Undefined substitution rule"

    def __init__(self):
        """Local data storage"""

    def process(self, item_meta, item):
        """Edit the item name and ID before doing other replacements.

        Read the item details.
        Edit item name and ID here, and it will change
        which item NBT is used for replacements.
        """

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

substitution_rules = []

################################################################################
# Substitution rules begin

class ResetDirty(SubstitutionRule):
    """Rule to reset the dirty flag"""
    name = "Reset Dirty tag"

    def process(self, item_meta, item):
        if not item.nbt.has_path('tag.Monumenta.Dirty'):
            return
        item.tag.at_path('Monumenta').value.pop('Dirty')
        if len(item.nbt.at_path('tag.Monumenta').value) == 0:
            item.tag.value.pop('Monumenta')

class NameUnnamedItems(SubstitutionRule):
    """Rule to apply a name to unnamed items"""
    name = "Name Unnamed Items"
    NAME_TABLE = {}

    @classmethod
    def _init_unnamed_items(cls):
        NameUnnamedItems.NAME_TABLE = {}
        # These two lists allow replacing items that are missing lore text and/or item names, which would otherwise be
        # ignored. The item NBT must match exactly with the exception of adding the name of the item for replacement
        # purposes, including the order of data in lists, and the exact raw json text strings
        # (formatting has the same capitalization, order, spaces, yada yada)

        # These items do not have display names in-game; the only difference from the items to be replaced should be the
        # addition of the display name for the sake of replacements. If the NBT otherwise matches exactly, the name and
        # lore text are set on the items before continuing with item updates.
        unnamed_chests = (
            # OLD EXAMPLE, DO NOT USE. This is pre 1.19 data
            # r'''{Items:[{Count:1b,Slot:0b,id:"minecraft:golden_apple",tag:{display:{Name:'{"text":"Kingfruit"}'},plain:{display:{Name:"Kingfruit"}}}},{Count:1b,Slot:1b,id:"minecraft:enchanted_golden_apple",tag:{display:{Name:'{"text":"Soulfruit"}'},plain:{display:{Name:"Soulfruit"}}}}]}''',
            # Somehow some Summoning Crystals ended up with no lore after they were added to the loot tables
            r'''{Items:[{Count:1b,Slot:0b,id:"minecraft:yellow_dye",tag:{display:{Name:'{"extra":[{"bold":true,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"gold","text":"Summoning Crystal"}],"text":""}'},plain:{display:{Name:"Summoning Crystal"}}}}]}''',
        )

        # These items have no lore text, which means they're assumed to be on mobs and will be skipped to prevent them
        # from dropping or changing stats. Items that match exactly will be given a temporary line of lore so they can
        # be replaced.
        named_chests = (
            # Blast Prot 100 boots again
            r'''{Items:[{Count:1b,Slot:13b,id:"minecraft:golden_boots",tag:{AttributeModifiers:[{Amount:1.0d,AttributeName:"minecraft:generic.armor_toughness",Name:"MMDummy",Operation:2,UUID:[I;0,0,0,0]}],Damage:0,Enchantments:[{id:"minecraft:power",lvl:1s}],HideFlags:3,Monumenta:{Stock:{Enchantments:{"Blast Protection":{Level:100}}}},display:{Lore:['{"italic":false,"color":"gray","text":"Blast Protection C"}'],Name:'{"bold":false,"italic":false,"underlined":false,"color":"#81D434","text":"Boots of Deleting"}'},plain:{display:{Lore:["Blast Protection C"],Name:"Boots of Deleting"}}}}]}''',
        )

        for chest_mojangson in unnamed_chests:
            chest = nbt.TagCompound.from_mojangson(chest_mojangson)
            for unnamed_item in chest.iter_multipath('Items[]'):
                item_id = unnamed_item.at_path('id').value
                item_name = get_item_name_from_nbt(unnamed_item.at_path('tag'))
                item_tag = unnamed_item.at_path('tag').deep_copy()

                del item_tag.at_path('display').value['Name']
                if len(item_tag.at_path('display').value) == 0:
                    del item_tag.value['display']
                if item_tag.has_path('plain.display.Name'):
                    del item_tag.at_path('plain.display').value['Name']
                    if len(item_tag.at_path('plain.display').value) == 0:
                        del item_tag.at_path('plain').value['display']
                    if len(item_tag.at_path('plain').value) == 0:
                        del item_tag.value['plain']

                if item_id not in NameUnnamedItems.NAME_TABLE:
                    NameUnnamedItems.NAME_TABLE[item_id] = {}
                NameUnnamedItems.NAME_TABLE[item_id][item_tag] = item_name

        for chest_mojangson in named_chests:
            chest = nbt.TagCompound.from_mojangson(chest_mojangson)
            for unnamed_item in chest.iter_multipath('Items[]'):
                item_id = unnamed_item.at_path('id').value
                item_name = get_item_name_from_nbt(unnamed_item.at_path('tag'))
                item_tag = unnamed_item.at_path('tag').deep_copy()

                if item_id not in NameUnnamedItems.NAME_TABLE:
                    NameUnnamedItems.NAME_TABLE[item_id] = {}
                NameUnnamedItems.NAME_TABLE[item_id][item_tag] = item_name

    def process(self, item_meta, item):
        if NameUnnamedItems.NAME_TABLE is None:
            NameUnnamedItems._init_unnamed_items()

        item_map = NameUnnamedItems.NAME_TABLE.get(item_meta['id'], None)
        if item_map is None:
            return
        item_tag = item.nbt.value.get('tag', None)
        if item_tag is None:
            item_meta['name'] = item_map.get(None, None)
            if item_meta['name'] is not None:
                item.nbt.value['tag'] = nbt.TagCompound({
                    'display': nbt.TagCompound({
                        'Lore': nbt.TagList([
                            nbt.TagString('''{"text":"Don't skip this if it's missing lore!"}''')
                        ])
                    })
                })
            return
        for tag_to_match, new_name in item_map.items():
            if item_tag == tag_to_match:
                item_meta['name'] = new_name
                if not item_tag.has_path('display'):
                    item_tag.value['display'] = nbt.TagCompound({})
                if not item_tag.has_path('display.Lore'):
                    item_tag.at_path('display').value['Lore'] = nbt.TagList([])
                item_tag.at_path('display.Lore').value.append(nbt.TagString('''{"text":"Don't skip this if it's missing lore!"}'''))
                return

class FixBookTitles(SubstitutionRule):
    """Rule to identify books by title if the name is not set"""
    name = "Fix book titles"

    def process(self, item_meta, item):
        if item.nbt.has_path('tag.display.Name') or not item.nbt.has_path('tag.title'):
            return
        title = item.tag.at_path('title').value
        item_meta['name'] = unformat_text(parse_name_possibly_json(title))

class FixBrokenSectionSymbols(SubstitutionRule):
    """Rule to fix section symbols with the wrong character encoding"""
    name = "Fix broken section symbols"

    @staticmethod
    def _fix(old_str):
        return old_str.replace(chr(0xfffd), chr(0xa7))

    def process(self, item_meta, item):
        # Name
        if not item.nbt.has_path('tag.display.Name'):
            return
        name = item.tag.at_path('display.Name').value
        new_name = self._fix(name)
        item.tag.at_path('display.Name').value = new_name
        item_meta['name'] = unformat_text(parse_name_possibly_json(new_name))

        # Lore lines
        for lore_line in item.tag.iter_multipath('display.Lore[]'):
            lore = lore_line.value
            new_lore = self._fix(lore)
            lore_line.value = new_lore

class FixDoubleJsonNames(SubstitutionRule):
    """Rule to fix item names that are json inside of json"""
    name = "Fixed json in json names"

    def process(self, item_meta, item):
        if not item.nbt.has_path('tag.display.Name'):
            return
        name = item.tag.at_path('display.Name').value
        name_json = parse_name_possibly_json(name)
        name_json_json = parse_name_possibly_json(name_json)
        if name_json != name_json_json:
            item.tag.at_path('display.Name').value = name_json
            item_meta['name'] = unformat_text(name_json_json)

class FixEscapedNames(SubstitutionRule):
    """Rule to un-escape valid json characters"""
    name = "Fixed escaped characters in json names"

    def process(self, item_meta, item):
        if not item.nbt.has_path('tag.display.Name'):
            return
        name = item.tag.at_path('display.Name').value
        name = name.replace(r"\\u0027", "'")
        name = name.replace(r"\\u00a7", "§")
        name_json = parse_name_possibly_json(name)
        item.tag.at_path('display.Name').value = name
        item_meta['name'] = unformat_text(name_json)

class FixPlainTag(SubstitutionRule):
    """Rule to update the plain tag"""
    name = "Fix the plain tag"

    def process(self, item_meta, item):
        """Note: This is only useful for items that aren't in the loot tables."""
        if item.nbt.has_path("tag"):
            update_plain_tag(item.nbt.at_path("tag"))


class MarkPlayerModifiedDirty(SubstitutionRule):
    """Rule to mark items modified by players so the plugin code updates their lore text"""
    name = "Apply the dirty tag to items not in the loot tables"

    def process(self, item_meta, item):
        """Note: This is only useful for items that aren't in the loot tables."""
        if item.nbt.has_path('tag.Monumenta.PlayerModified'):
            mark_dirty(item)


class UpdateQuivers(SubstitutionRule):
    """Note: only has to be run once"""
    name = "Update quivers to new format as arrows"

    def process(self, item_meta, item):
        if (not item_meta['id'].endswith('shulker_box')
                or item_meta['name'] is None
                or not item_meta['name'].endswith(' Quiver')):
            return

        item_meta['id'] = 'minecraft:tipped_arrow'
        if item_meta['name'] == "Novice's Quiver":
            item_meta['name'] = "Scout's Quiver"

        if item.tag.has_path('BlockEntityTag.Items'):
            arrows = item.tag.at_path('BlockEntityTag.Items')
            for arrow in arrows.value:
                count = arrow.at_path('Count').value
                arrow.at_path('Count').value = 1
                if not arrow.has_path('tag'):
                    arrow.value['tag'] = nbt.TagCompound({})
                if not arrow.has_path('tag.Monumenta'):
                    arrow.at_path('tag').value['Monumenta'] = nbt.TagCompound({})
                if not arrow.has_path('tag.Monumenta.PlayerModified'):
                    arrow.at_path('tag.Monumenta').value['PlayerModified'] = nbt.TagCompound({})
                arrow.at_path('tag.Monumenta.PlayerModified').value['AmountInContainer'] = nbt.TagLong(count)
            if not item.tag.has_path('Monumenta'):
                item.tag.value['Monumenta'] = nbt.TagCompound({})
            if not item.tag.has_path('Monumenta.PlayerModified'):
                item.tag.at_path('Monumenta').value['PlayerModified'] = nbt.TagCompound({})
            item.tag.at_path('Monumenta.PlayerModified').value['Items'] = arrows
            del item.tag.value['BlockEntityTag']


class SubtituteItems(SubstitutionRule):
    """Rule to replace items by ID/name"""
    name = "Substitute the ID and name of items, ignoring other NBT"

    def __init__(self):
        super().__init__()
        self.replacements = {}

        for substitution in [
                # ["minecraft:example_item_id", "Example Name", "minecraft:new_id", "Example New Name"],
                # Any name:
                # ["minecraft:example_banned_item", always_equal, "minecraft:new_id", "Example New Name"],
                # No name:
                # ["minecraft:example_vanilla_item", None, "minecraft:new_id", "Example New Name"],
                # Example item type change:
                # ["minecraft:bow", "Blazing Crossbow", "minecraft:crossbow", "Blazing Crossbow"],
                # Boots of Deleting -> Infused Cloth Shoes
                ["minecraft:golden_boots", "Boots of Deleting", "minecraft:leather_boots", "Infused Cloth Shoes"],
                # Typo fix for Aggripa's Gearshredder
                ["minecraft:iron_sword", "Agrippa's Gearshredder", "minecraft:iron_sword", "Aggripa's Gearshredder"],
                # Please let this finally get rid of vanilla Suspicious Stews
                ["minecraft:suspicious_stew", None, "minecraft:suspicious_stew", "Dichen Specialty Stew"],
        ]:

            old_id, old_name, new_id, new_name = substitution

            if old_id not in self.replacements:
                self.replacements[old_id] = {}
            id_replacements = self.replacements[old_id]

            id_replacements[old_name] = (new_id, new_name)

    def process(self, item_meta, item):
        old_id = item_meta['id']
        old_name = item_meta['name']

        # This way around so always_equal works
        for replaceable_id in self.replacements:
            if replaceable_id == old_id:
                # This way around so always_equal works
                for replaceable_name in self.replacements[replaceable_id].keys():
                    if replaceable_name == old_name:
                        new_id, new_name = self.replacements[replaceable_id][replaceable_name]

                        item_meta['id'] = new_id
                        item_meta['name'] = new_name

################################################################################
# Substitution rules end

substitution_rules = SubstitutionRule.recursive_public_subclasses()
