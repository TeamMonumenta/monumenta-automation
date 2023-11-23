import os
import sys
import re

from lib_py3.common import get_item_name_from_nbt
from lib_py3.common import parse_name_possibly_json
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
        pass

    def process(self, item_meta, item):
        """Edit the item name and ID before doing other replacements.

        Read the item details.
        Edit item name and ID here, and it will change
        which item NBT is used for replacements.
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

substitution_rules = []

################################################################################
# Substitution rules begin

class ResetDirty(SubstitutionRule):
    name = "Reset Dirty tag"

    def process(self, item_meta, item):
        if not item.nbt.has_path('tag.Monumenta.Dirty'):
            return
        item.tag.at_path('Monumenta').value.pop('Dirty')
        if len(item.nbt.at_path('tag.Monumenta').value) == 0:
            item.tag.value.pop('Monumenta')

class NameUnnamedItems(SubstitutionRule):
    name = "Name Unnamed Items"
    NAME_TABLE = None

    @classmethod
    def _init_unnamed_items(cls):
        NameUnnamedItems.NAME_TABLE = {}
        unnamed_chests = (
            # OLD EXAMPLE, DO NOT USE. This is pre 1.19 data
            # r'''{Items:[{Count:1b,Slot:0b,id:"minecraft:golden_apple",tag:{display:{Name:'{"text":"Kingfruit"}'},plain:{display:{Name:"Kingfruit"}}}},{Count:1b,Slot:1b,id:"minecraft:enchanted_golden_apple",tag:{display:{Name:'{"text":"Soulfruit"}'},plain:{display:{Name:"Soulfruit"}}}}]}''',
            # Begone evil Turtle Master potions!
            r'''{Items:[{Count:1b,Slot:0b,id:"minecraft:potion",tag:{Potion:"minecraft:strong_turtle_master",display:{Name:'{"text":"Potion of the Turtle Master"}'},plain:{display:{Name:"Potion of the Turtle Master"}}}}]}''',
        )
        named_chests = (
            r'''{Items:[{Count:1b,Slot:0b,id:"minecraft:lingering_potion",tag:{CustomPotionColor:16744576,CustomPotionEffects:[{Ambient:1b,Amplifier:2b,Duration:240,Id:10b,ShowIcon:1b,ShowParticles:1b},{Ambient:1b,Amplifier:0b,Duration:900,Id:22b,ShowIcon:1b,ShowParticles:1b}],Potion:"minecraft:mundane",display:{Name:'{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"green","text":"Strong Sanctify Potion"}],"text":""}'},plain:{display:{Name:"Strong Sanctify Potion"}}}}]}''',
            # Zombie Meat and Cooked Zombie Meat
            r'''{Items:[{Count:1b,Slot:0b,id:"minecraft:rabbit",tag:{display:{Name:'{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"white","text":"Zombie Meat"}],"text":""}'},plain:{display:{Name:"Zombie Meat"}}}}]}''',
            r'''{Items:[{Count:1b,Slot:0b,id:"minecraft:cooked_rabbit",tag:{display:{Name:'{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"white","text":"Cooked Zombie Meat"}],"text":""}'},plain:{display:{Name:"Cooked Zombie Meat"}}}}]}''',
            # Loreless potions
            r'''{Items:[{Count:1b,Slot:0b,id:"minecraft:potion",tag:{CustomPotionColor:9325341,CustomPotionEffects:[{Ambient:1b,Amplifier:0b,Duration:100,Id:9b,ShowIcon:1b,ShowParticles:1b},{Ambient:1b,Amplifier:0b,Duration:600,Id:19b,ShowIcon:1b,ShowParticles:1b},{Ambient:1b,Amplifier:1b,Duration:1200,Id:10b,ShowIcon:1b,ShowParticles:1b},{Ambient:1b,Amplifier:0b,Duration:1200,Id:5b,ShowIcon:1b,ShowParticles:1b}],Potion:"minecraft:mundane",display:{Name:'{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"white","text":"Blackroot Brew"}],"text":""}'},plain:{display:{Name:"Blackroot Brew"}}}}]}''',
            r'''{Items:[{Count:1b,Slot:0b,id:"minecraft:potion",tag:{CustomPotionEffects:[{Ambient:1b,Amplifier:0b,Duration:10800,Id:13b,ShowIcon:1b,ShowParticles:1b}],Potion:"minecraft:mundane",display:{Name:'{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"white","text":"Depth Lurker"}],"text":""}'},plain:{display:{Name:"Depth Lurker"}}}}]}''',
            r'''{Items:[{Count:1b,Slot:0b,id:"minecraft:potion",tag:{CustomPotionColor:14192676,CustomPotionEffects:[{Ambient:1b,Amplifier:0b,Duration:100,Id:9b,ShowIcon:1b,ShowParticles:1b},{Ambient:1b,Amplifier:0b,Duration:1800,Id:13b,ShowIcon:1b,ShowParticles:1b},{Ambient:1b,Amplifier:1b,Duration:100,Id:10b,ShowIcon:1b,ShowParticles:1b}],Potion:"minecraft:mundane",display:{Name:'{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"white","text":"Sunfish Rum"}],"text":""}'},plain:{display:{Name:"Sunfish Rum"}}}}]}''',
            r'''{Items:[{Count:1b,Slot:0b,id:"minecraft:potion",tag:{CustomPotionColor:13389173,CustomPotionEffects:[{Ambient:1b,Amplifier:0b,Duration:100,Id:9b,ShowIcon:1b,ShowParticles:1b},{Ambient:1b,Amplifier:0b,Duration:400,Id:12b,ShowIcon:1b,ShowParticles:1b},{Ambient:1b,Amplifier:0b,Duration:400,Id:11b,ShowIcon:1b,ShowParticles:1b}],Potion:"minecraft:mundane",display:{Name:'{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"white","text":"Blaze\'s Whiskey"}],"text":""}'},plain:{display:{Name:"Blaze's Whiskey"}}}}]}''',
            r'''{Items:[{Count:1b,Slot:0b,id:"minecraft:splash_potion",tag:{CustomPotionEffects:[{Ambient:0b,Amplifier:2b,Duration:600,Id:2b,ShowIcon:1b,ShowParticles:1b},{Ambient:0b,Amplifier:2b,Duration:600,Id:4b,ShowIcon:1b,ShowParticles:1b},{Ambient:0b,Amplifier:1b,Duration:1200,Id:17b,ShowIcon:1b,ShowParticles:1b}],Potion:"minecraft:water",display:{Name:'{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"text":"Potion of Draining Life"}],"text":""}'},plain:{display:{Name:"Potion of Draining Life"}}}}]}''',
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
    name = "Fix book titles"

    def process(self, item_meta, item):
        if item.nbt.has_path('tag.display.Name') or not item.nbt.has_path('tag.title'):
            return
        title = item.tag.at_path('title').value
        item_meta['name'] = unformat_text(parse_name_possibly_json(title))

class FixBrokenSectionSymbols(SubstitutionRule):
    name = "Fix broken section symbols"

    def _fix(self, old_str):
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

class ReplaceSuspiciousBlock(SubstitutionRule):
    name = "Replaces Suspicious Block black concrete with just black concrete"
    matcher = re.compile("""Suspicious Block[!',.:;i|]{3}""")

    def process(self, item_meta, item):
        if item.id != "minecraft:black_concrete":
            return

        if not item.nbt.has_path('tag.display.Name'):
            return

        name = item.tag.at_path('display.Name').value
        name_json = parse_name_possibly_json(name)

        if self.matcher.fullmatch(name_json):
            item.nbt.value.pop('tag')
            item_meta["name"] = None

class FixEscapedNames(SubstitutionRule):
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
    name = "Fix the plain tag"

    def process(self, item_meta, item):
        """Note: This is only useful for items that aren't in the loot tables."""
        if item.nbt.has_path("tag"):
            update_plain_tag(item.nbt.at_path("tag"))


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
    name = "Substitute the ID and name of items, ignoring other NBT"

    def __init__(self):
        self.replacements = {}

        for substitution in [
                # ["minecraft:example_item_id", "Example Name", "minecraft:new_id", "Example New Name"],
                # Any name:
                # ["minecraft:example_banned_item", always_equal, "minecraft:new_id", "Example New Name"],
                # No name:
                # ["minecraft:example_vanilla_item", None, "minecraft:new_id", "Example New Name"],
                # Example item type change:
                # ["minecraft:bow", "Blazing Crossbow", "minecraft:crossbow", "Blazing Crossbow"],
                ["minecraft:suspicious_stew", None, "minecraft:suspicious_stew", "Dichen Specialty Stew"],
                ["minecraft:pumpkin_seeds", "Lesser Charm of Multiplication", "minecraft:horn_coral_fan", "Lesser Trailblazer Charm"],
                ["minecraft:pumpkin_seeds", "Greater Charm of Multiplication", "minecraft:horn_coral_fan", "Greater Trailblazer Charm"],
                ["minecraft:pumpkin_seeds", "Focused Charm of Multiplication", "minecraft:horn_coral_fan", "Focused Trailblazer Charm"],
                ["minecraft:lingering_potion", "Crippling Vial", "minecraft:splash_potion", "Crippling Vial"],
                # Type changes by the request of the RP team
                ["minecraft:leather_boots", "Deathbound Cavaliers", "minecraft:lantern", "Deathbound Cavaliers"],
                ["minecraft:golden_helmet", "Dread Admiral's Hat", "minecraft:leather_helmet", "Dread Admiral's Hat"],
                # Potion of Draining Life -> Elixir of Draining Life
                ["minecraft:splash_potion", "Potion of Draining Life", "minecraft:splash_potion", "Elixir of Draining Life"],
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
