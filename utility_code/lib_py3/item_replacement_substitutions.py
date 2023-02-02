import os
import sys

from lib_py3.common import always_equal
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
            r'''{Items:[{Count:1b,Slot:0b,id:"minecraft:golden_apple",tag:{display:{Name:'{"text":"Kingfruit"}'},plain:{display:{Name:"Kingfruit"}}}},{Count:1b,Slot:1b,id:"minecraft:enchanted_golden_apple",tag:{display:{Name:'{"text":"Soulfruit"}'},plain:{display:{Name:"Soulfruit"}}}}]}''',
        )
        named_chests = (
            r'''{Items:[{id:"minecraft:lingering_potion",tag:{Potion:"minecraft:poison",display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"dark_green","text":"Minor Venomous Vial"}'},plain:{display:{Name:"Minor Venomous Vial"}}},Count:1b,Slot:0b},{id:"minecraft:lingering_potion",tag:{display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#704c8a","text":"Reeking Vial"}'},plain:{display:{Name:"Reeking Vial"}},Potion:"minecraft:strong_harming"},Count:1b,Slot:1b},{id:"minecraft:lingering_potion",tag:{display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#790e47","text":"Fount of Strength"}'},plain:{display:{Name:"Fount of Strength"}},Potion:"minecraft:strong_strength"},Count:1b,Slot:2b},{id:"minecraft:lingering_potion",tag:{display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#c21e56","text":"Fount of Healing"}'},plain:{display:{Name:"Fount of Healing"}},Potion:"minecraft:strong_healing"},Count:1b,Slot:3b},{id:"minecraft:lingering_potion",tag:{display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#c21e56","text":"Fount of Minor Healing"}'},plain:{display:{Name:"Fount of Minor Healing"}},Potion:"minecraft:healing"},Count:1b,Slot:4b},{id:"minecraft:lingering_potion",tag:{display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"dark_green","text":"Minor Venomous Vial"}'},plain:{display:{Name:"Minor Venomous Vial"}},Potion:"minecraft:poison"},Count:1b,Slot:5b},{id:"minecraft:lingering_potion",tag:{display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"dark_green","text":"Venomous Vial"}'},plain:{display:{Name:"Venomous Vial"}},Potion:"minecraft:long_poison"},Count:1b,Slot:6b},{id:"minecraft:lingering_potion",tag:{plain:{display:{Name:"Crippling Vial"}},CustomPotionEffects:[{ShowParticles:1b,Id:18b,Duration:800,ShowIcon:1b,Amplifier:2b,Ambient:1b}],display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#b4acc3","text":"Crippling Vial"}'},CustomPotionColor:6366461,Potion:"minecraft:empty"},Count:1b,Slot:7b},{id:"minecraft:lingering_potion",tag:{plain:{display:{Name:"Crippling Vial"}},CustomPotionEffects:[{ShowParticles:1b,Id:18b,Duration:800,ShowIcon:1b,Amplifier:2b,Ambient:1b}],display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#b4acc3","text":"Crippling Vial"}'},CustomPotionColor:6366461,Potion:"minecraft:mundane"},Count:1b,Slot:8b},{id:"minecraft:lingering_potion",tag:{plain:{display:{Name:"Noxious Vial"}},CustomPotionEffects:[{ShowParticles:1b,Id:20b,Duration:800,ShowIcon:1b,Amplifier:2b,Ambient:1b}],display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#006400","text":"Noxious Vial"}'},CustomPotionColor:3355443,Potion:"minecraft:empty"},Count:1b,Slot:9b},{id:"minecraft:lingering_potion",tag:{plain:{display:{Name:"Noxious Vial"}},CustomPotionEffects:[{ShowParticles:1b,Id:20b,Duration:800,ShowIcon:1b,Amplifier:2b,Ambient:1b}],display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#006400","text":"Noxious Vial"}'},CustomPotionColor:3355443,Potion:"minecraft:mundane"},Count:1b,Slot:10b},{id:"minecraft:lingering_potion",tag:{plain:{display:{Name:"Rotting Vial"}},CustomPotionEffects:[{ShowParticles:1b,Id:19b,Duration:800,ShowIcon:1b,Amplifier:2b,Ambient:1b}],display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"dark_green","text":"Rotting Vial"}'},CustomPotionColor:5278007,Potion:"minecraft:empty"},Count:1b,Slot:11b},{id:"minecraft:lingering_potion",tag:{plain:{display:{Name:"Rotting Vial"}},CustomPotionEffects:[{ShowParticles:1b,Id:19b,Duration:800,ShowIcon:1b,Amplifier:2b,Ambient:1b}],display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"dark_green","text":"Rotting Vial"}'},CustomPotionColor:5278007,Potion:"minecraft:mundane"},Count:1b,Slot:12b},{id:"minecraft:lingering_potion",tag:{plain:{display:{Name:"Shadowcast Vial"}},CustomPotionEffects:[{ShowParticles:1b,Id:15b,Duration:800,ShowIcon:1b,Amplifier:2b,Ambient:1b}],display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#674c5b","text":"Shadowcast Vial"}'},CustomPotionColor:10898809,Potion:"minecraft:empty"},Count:1b,Slot:13b},{id:"minecraft:lingering_potion",tag:{plain:{display:{Name:"Shadowcast Vial"}},CustomPotionEffects:[{ShowParticles:1b,Id:15b,Duration:800,ShowIcon:1b,Amplifier:2b,Ambient:1b}],display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#674c5b","text":"Shadowcast Vial"}'},CustomPotionColor:10898809,Potion:"minecraft:mundane"},Count:1b,Slot:14b},{id:"minecraft:potion",tag:{Potion:"minecraft:awkward",display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"white","text":"Nulled Potion"}'},plain:{display:{Name:"Nulled Potion"}}},Count:1b,Slot:15b},{id:"minecraft:potion",tag:{Potion:"minecraft:harming",display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#5d2d87","text":"Minor Harming Potion"}'},plain:{display:{Name:"Minor Harming Potion"}}},Count:1b,Slot:16b},{id:"minecraft:potion",tag:{Potion:"minecraft:mundane",display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"white","text":"Lukewarm Potion"}'},plain:{display:{Name:"Lukewarm Potion"}}},Count:1b,Slot:17b},{id:"minecraft:potion",tag:{Potion:"minecraft:thick",display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"dark_aqua","text":"Thick Goo"}'},plain:{display:{Name:"Thick Goo"}}},Count:1b,Slot:18b},{id:"minecraft:potion",tag:{Potion:"minecraft:water",display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#0c2ca2","text":"Bottle of Water"}'},plain:{display:{Name:"Bottle of Water"}}},Count:1b,Slot:19b},{id:"minecraft:potion",tag:{display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#0c2ca2","text":"Bottle of Water"}'},plain:{display:{Name:"Bottle of Water"}},Potion:"minecraft:water"},Count:1b,Slot:20b},{id:"minecraft:potion",tag:{display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#1773b1","text":"Aqueous Potion"}'},plain:{display:{Name:"Aqueous Potion"}},Potion:"minecraft:long_water_breathing"},Count:1b,Slot:21b},{id:"minecraft:potion",tag:{display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#5d2d87","text":"Minor Harming Potion"}'},plain:{display:{Name:"Minor Harming Potion"}},Potion:"minecraft:harming"},Count:1b,Slot:22b},{id:"minecraft:potion",tag:{display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"dark_aqua","text":"Thick Goo"}'},plain:{display:{Name:"Thick Goo"}},Potion:"minecraft:thick"},Count:1b,Slot:23b},{id:"minecraft:potion",tag:{display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"dark_green","text":"Endless Venomous Potion"}'},plain:{display:{Name:"Endless Venomous Potion"}},Potion:"minecraft:long_poison"},Count:1b,Slot:24b},{id:"minecraft:potion",tag:{display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"dark_green","text":"Major Venomous Potion"}'},plain:{display:{Name:"Major Venomous Potion"}},Potion:"minecraft:strong_poison"},Count:1b,Slot:25b},{id:"minecraft:potion",tag:{display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"white","text":"Lukewarm Potion"}'},plain:{display:{Name:"Lukewarm Potion"}},Potion:"minecraft:mundane"},Count:1b,Slot:26b}]}''',
            r'''{Items:[{id:"minecraft:potion",tag:{display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"white","text":"Nulled Potion"}'},plain:{display:{Name:"Nulled Potion"}},Potion:"minecraft:awkward"},Count:1b,Slot:0b},{id:"minecraft:potion",tag:{plain:{display:{Name:"Bastion of Will"}},CustomPotionEffects:[{ShowParticles:1b,Id:21b,Duration:4800,ShowIcon:1b,Amplifier:0b,Ambient:1b},{ShowParticles:1b,Id:11b,Duration:4800,ShowIcon:1b,Amplifier:0b,Ambient:1b},{ShowParticles:1b,Id:22b,Duration:4800,ShowIcon:1b,Amplifier:0b,Ambient:1b},{ShowParticles:1b,Id:3b,Duration:4800,ShowIcon:1b,Amplifier:0b,Ambient:1b}],display:{Name:'{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"light_purple","text":"Bastion of Will"}],"text":""}'},CustomPotionColor:16777215,Potion:"minecraft:mundane"},Count:1b,Slot:1b},{id:"minecraft:potion",tag:{plain:{display:{Name:"DevCrack 10"}},CustomPotionEffects:[{ShowParticles:1b,Id:18b,Duration:1200000000,ShowIcon:1b,Amplifier:0b,Ambient:1b}],display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#ff69b4","text":"DevCrack 10"}'},Potion:"minecraft:mundane"},Count:1b,Slot:2b},{id:"minecraft:potion",tag:{plain:{display:{Name:"DevCrack 3"}},Enchantments:[{id:"minecraft:infinity",lvl:1s}],CustomPotionEffects:[{ShowParticles:1b,Id:11b,Duration:300,ShowIcon:1b,Amplifier:4b,Ambient:1b},{ShowParticles:1b,Id:19b,Duration:500,ShowIcon:1b,Amplifier:9b,Ambient:1b},{ShowParticles:1b,Id:1b,Duration:300,ShowIcon:1b,Amplifier:4b,Ambient:1b},{ShowParticles:1b,Id:3b,Duration:300,ShowIcon:1b,Amplifier:9b,Ambient:1b}],display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#ff69b4","text":"DevCrack 3"}'},Potion:"minecraft:mundane"},Count:1b,Slot:3b},{id:"minecraft:potion",tag:{plain:{display:{Name:"DevCrack 4"}},Enchantments:[{id:"minecraft:infinity",lvl:1s}],CustomPotionEffects:[{ShowParticles:1b,Id:11b,Duration:300,ShowIcon:1b,Amplifier:4b,Ambient:1b},{ShowParticles:1b,Id:19b,Duration:500,ShowIcon:1b,Amplifier:9b,Ambient:1b},{ShowParticles:1b,Id:1b,Duration:300,ShowIcon:1b,Amplifier:4b,Ambient:1b},{ShowParticles:1b,Id:3b,Duration:300,ShowIcon:1b,Amplifier:9b,Ambient:1b}],display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#ff69b4","text":"DevCrack 4"}'},Potion:"minecraft:mundane"},Count:1b,Slot:4b},{id:"minecraft:potion",tag:{plain:{display:{Name:"DevCrack 5"}},CustomPotionEffects:[{ShowParticles:1b,Id:18b,Duration:100000,ShowIcon:1b,Amplifier:9b,Ambient:1b},{ShowParticles:1b,Id:11b,Duration:100000,ShowIcon:1b,Amplifier:9b,Ambient:1b},{ShowParticles:1b,Id:2b,Duration:100000,ShowIcon:1b,Amplifier:9b,Ambient:1b}],display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#ff69b4","text":"DevCrack 5"}'},Potion:"minecraft:mundane"},Count:1b,Slot:5b},{id:"minecraft:potion",tag:{plain:{display:{Name:"DevCrack 6"}},CustomPotionEffects:[{ShowParticles:1b,Id:18b,Duration:1200000000,ShowIcon:1b,Amplifier:0b,Ambient:1b}],display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#ff69b4","text":"DevCrack 6"}'},Potion:"minecraft:mundane"},Count:1b,Slot:6b},{id:"minecraft:potion",tag:{plain:{display:{Name:"DevCrack 7"}},CustomPotionEffects:[{ShowParticles:1b,Id:18b,Duration:1200000000,ShowIcon:1b,Amplifier:0b,Ambient:1b}],display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#ff69b4","text":"DevCrack 7"}'},Potion:"minecraft:mundane"},Count:1b,Slot:7b},{id:"minecraft:potion",tag:{plain:{display:{Name:"DevCrack 8"}},CustomPotionEffects:[{ShowParticles:1b,Id:18b,Duration:100000,ShowIcon:1b,Amplifier:9b,Ambient:1b},{ShowParticles:1b,Id:11b,Duration:100000,ShowIcon:1b,Amplifier:9b,Ambient:1b},{ShowParticles:1b,Id:2b,Duration:100000,ShowIcon:1b,Amplifier:9b,Ambient:1b}],display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#ff69b4","text":"DevCrack 8"}'},Potion:"minecraft:mundane"},Count:1b,Slot:8b},{id:"minecraft:potion",tag:{plain:{display:{Name:"DevCrack 9"}},CustomPotionEffects:[{ShowParticles:1b,Id:18b,Duration:100000,ShowIcon:1b,Amplifier:9b,Ambient:1b},{ShowParticles:1b,Id:11b,Duration:100000,ShowIcon:1b,Amplifier:9b,Ambient:1b},{ShowParticles:1b,Id:2b,Duration:100000,ShowIcon:1b,Amplifier:9b,Ambient:1b}],display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#ff69b4","text":"DevCrack 9"}'},Potion:"minecraft:mundane"},Count:1b,Slot:9b},{id:"minecraft:potion",tag:{plain:{display:{Name:"Ragebrew"}},CustomPotionEffects:[{ShowParticles:1b,Id:1b,Duration:7200,ShowIcon:1b,Amplifier:0b,Ambient:1b},{ShowParticles:1b,Id:3b,Duration:7200,ShowIcon:1b,Amplifier:0b,Ambient:0b},{ShowParticles:1b,Id:5b,Duration:7200,ShowIcon:1b,Amplifier:0b,Ambient:0b},{ShowParticles:1b,Id:11b,Duration:7200,ShowIcon:1b,Amplifier:0b,Ambient:1b}],display:{Name:'{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"light_purple","text":"Ragebrew"}],"text":""}'},CustomPotionColor:2697513,Potion:"minecraft:mundane"},Count:1b,Slot:10b},{id:"minecraft:splash_potion",tag:{Enchantments:[{id:"minecraft:power",lvl:1s}],CustomPotionColor:16756736,HideFlags:71,Potion:"minecraft:mundane",plain:{display:{Name:"Extinguisher"}},CustomPotionEffects:[{ShowParticles:1b,Id:12b,Duration:200,ShowIcon:1b,Amplifier:0b,Ambient:1b}],AttributeModifiers:[{Name:"Dummy",Operation:2,UUID:[I;425995745,1264075117,-1232017366,1430706599],AttributeName:"minecraft:generic.armor_toughness",Amount:1.0d}],display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#ffbf00","text":"Extinguisher"}',Lore:[]}},Count:1b,Slot:11b},{id:"minecraft:splash_potion",tag:{Enchantments:[{id:"minecraft:power",lvl:1s}],HideFlags:71,CustomPotionColor:16756736,Potion:"minecraft:mundane",plain:{display:{Name:"Extinguisher"}},CustomPotionEffects:[{ShowParticles:1b,ShowIcon:1b,Duration:200,Id:12b,Ambient:1b,Amplifier:0b}],AttributeModifiers:[{Name:"Dummy",Operation:2,UUID:[I;425995745,1264075117,-1232017366,1430706599],Amount:1.0d,AttributeName:"minecraft:generic.armor_toughness"}],display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#ffbf00","text":"Extinguisher"}',Lore:[]}},Count:1b,Slot:12b},{id:"minecraft:splash_potion",tag:{Potion:"minecraft:strong_regeneration",display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#c8a2c8","text":"Major Regeneration Vial"}'},plain:{display:{Name:"Major Regeneration Vial"}}},Count:1b,Slot:13b},{id:"minecraft:splash_potion",tag:{Potion:"minecraft:thick",display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"dark_aqua","text":"Gooey Vial"}'},plain:{display:{Name:"Gooey Vial"}}},Count:1b,Slot:14b},{id:"minecraft:splash_potion",tag:{Potion:"minecraft:water",display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#0c2ca2","text":"Waterfilled Vial"}'},plain:{display:{Name:"Waterfilled Vial"}}},Count:1b,Slot:15b},{id:"minecraft:splash_potion",tag:{display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#0c2ca2","text":"Waterfilled Vial"}'},plain:{display:{Name:"Waterfilled Vial"}},Potion:"minecraft:water"},Count:1b,Slot:16b},{id:"minecraft:splash_potion",tag:{display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#1773b1","text":"Aqueous Vial"}'},plain:{display:{Name:"Aqueous Vial"}},Potion:"minecraft:long_water_breathing"},Count:1b,Slot:17b},{id:"minecraft:splash_potion",tag:{display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#196383","text":"Darksight Vial"}'},plain:{display:{Name:"Darksight Vial"}},Potion:"minecraft:long_night_vision"},Count:1b,Slot:18b},{id:"minecraft:splash_potion",tag:{display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#afc2e3","text":"Major Frosted Glass"}'},plain:{display:{Name:"Major Frosted Glass"}},Potion:"minecraft:strong_slowness"},Count:1b,Slot:19b},{id:"minecraft:splash_potion",tag:{display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#b4acc3","text":"Crippling Vial"}'},plain:{display:{Name:"Crippling Vial"}},Potion:"minecraft:long_weakness"},Count:1b,Slot:20b},{id:"minecraft:splash_potion",tag:{display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#b4acc3","text":"Minor Crippling Vial"}'},plain:{display:{Name:"Minor Crippling Vial"}},Potion:"minecraft:weakness"},Count:1b,Slot:21b},{id:"minecraft:splash_potion",tag:{display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#c8a2c8","text":"Major Regeneration Vial"}'},plain:{display:{Name:"Major Regeneration Vial"}},Potion:"minecraft:strong_regeneration"},Count:1b,Slot:22b},{id:"minecraft:splash_potion",tag:{display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#c8a2c8","text":"Regeneration Vial"}'},plain:{display:{Name:"Regeneration Vial"}},Potion:"minecraft:long_regeneration"},Count:1b,Slot:23b},{id:"minecraft:splash_potion",tag:{display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"#ffb43e","text":"Firecloak Vial"}'},plain:{display:{Name:"Firecloak Vial"}},Potion:"minecraft:fire_resistance"},Count:1b,Slot:24b},{id:"minecraft:splash_potion",tag:{display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"dark_aqua","text":"Gooey Vial"}'},plain:{display:{Name:"Gooey Vial"}},Potion:"minecraft:thick"},Count:1b,Slot:25b},{id:"minecraft:splash_potion",tag:{display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"dark_green","text":"Venom Bomb"}'},plain:{display:{Name:"Venom Bomb"}},Potion:"minecraft:long_poison"},Count:1b,Slot:26b}]}''',
            r'''{Items:[{id:"minecraft:splash_potion",tag:{display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"white","text":"Lukewarm Vial"}'},plain:{display:{Name:"Lukewarm Vial"}},Potion:"minecraft:mundane"},Count:1b,Slot:0b},{id:"minecraft:splash_potion",tag:{plain:{display:{Name:"Blinding Potion"}},CustomPotionEffects:[{ShowParticles:1b,Id:2b,Duration:1200,ShowIcon:1b,Amplifier:3b,Ambient:0b},{ShowParticles:1b,Id:15b,Duration:1200,ShowIcon:1b,Amplifier:0b,Ambient:0b}],display:{Name:'{"extra":[{"bold":true,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"white","text":"Blinding Potion"}],"text":""}'},Potion:"minecraft:mundane"},Count:1b,Slot:1b},{id:"minecraft:splash_potion",tag:{plain:{display:{Name:"Elixir of Draining Life"}},CustomPotionEffects:[{ShowParticles:1b,Id:2b,Duration:600,ShowIcon:1b,Amplifier:0b,Ambient:1b},{ShowParticles:1b,Id:4b,Duration:600,ShowIcon:1b,Amplifier:2b,Ambient:0b},{ShowParticles:1b,Id:17b,Duration:1200,ShowIcon:1b,Amplifier:1b,Ambient:0b},{ShowParticles:1b,Id:19b,Duration:600,ShowIcon:1b,Amplifier:1b,Ambient:1b}],display:{Name:'{"extra":[{"bold":false,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"white","text":"Elixir of Draining Life"}],"text":""}'},Potion:"minecraft:empty"},Count:1b,Slot:2b},{id:"minecraft:splash_potion",tag:{plain:{display:{Name:"Empowered Swiftshield Tincture"}},CustomPotionEffects:[{ShowParticles:1b,Id:1b,Duration:1200,ShowIcon:1b,Amplifier:1b,Ambient:1b},{ShowParticles:1b,Id:22b,Duration:1200,ShowIcon:1b,Amplifier:2b,Ambient:1b}],display:{Name:'{"bold":false,"italic":false,"underlined":false,"color":"green","text":"Empowered Swiftshield Tincture"}'},CustomPotionColor:13419264,Potion:"minecraft:mundane"},Count:1b,Slot:3b},{id:"minecraft:splash_potion",tag:{plain:{display:{Name:"Endless Venomous Vial"}},CustomPotionEffects:[{ShowParticles:1b,Id:19b,Duration:1000,ShowIcon:1b,Amplifier:2b,Ambient:1b}],display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"dark_green","text":"Endless Venomous Vial"}'},CustomPotionColor:4170260,Potion:"minecraft:empty"},Count:1b,Slot:4b},{id:"minecraft:splash_potion",tag:{plain:{display:{Name:"Endless Venomous Vial"}},CustomPotionEffects:[{ShowParticles:1b,Id:19b,Duration:1000,ShowIcon:1b,Amplifier:2b,Ambient:1b}],display:{Name:'{"bold":true,"italic":false,"underlined":false,"color":"dark_green","text":"Endless Venomous Vial"}'},CustomPotionColor:4170260,Potion:"minecraft:mundane"},Count:1b,Slot:5b},{id:"minecraft:splash_potion",tag:{plain:{display:{Name:"Holy Water"}},CustomPotionEffects:[{ShowParticles:1b,Id:10b,Duration:60,ShowIcon:1b,Amplifier:2b,Ambient:1b},{ShowParticles:1b,Id:20b,Duration:40,ShowIcon:1b,Amplifier:2b,Ambient:1b}],display:{Name:'{"extra":[{"bold":true,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"gold","text":"Holy Water"}],"text":""}'},CustomPotionColor:14934833,Potion:"minecraft:empty"},Count:1b,Slot:6b},{id:"minecraft:splash_potion",tag:{plain:{display:{Name:"Potion of Perseverance"}},CustomPotionEffects:[{ShowParticles:1b,Id:6b,Duration:0,ShowIcon:1b,Amplifier:2b,Ambient:1b},{ShowParticles:1b,Id:10b,Duration:300,ShowIcon:1b,Amplifier:0b,Ambient:1b}],display:{Name:'{"bold":false,"italic":false,"underlined":false,"color":"green","text":"Potion of Perseverance"}'},CustomPotionColor:9183488,Potion:"minecraft:mundane"},Count:1b,Slot:7b}]}''',
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
                #["minecraft:example_item_id", "Example Name", "minecraft:new_id", "Example New Name"],
                # Any name:
                #["minecraft:example_banned_item", always_equal, "minecraft:new_id", "Example New Name"],
                # No name:
                #["minecraft:example_vanilla_item", None, "minecraft:new_id", "Example New Name"],

                ["minecraft:bow", "Blazing Crossbow", "minecraft:crossbow", "Blazing Crossbow"],
                ["minecraft:bow", "Heatwave", "minecraft:crossbow", "Heatwave"],
                ["minecraft:bow", "Steel Arbalest", "minecraft:crossbow", "Steel Arbalest"],
                ["minecraft:bow", "Ghastcaller's Gunblade", "minecraft:crossbow", "Ghastcaller's Gunblade"],
                ["minecraft:bow", "Incendiary Inferno", "minecraft:crossbow", "Incendiary Inferno"],
                ["minecraft:bow", "Pirate's Flintlock", "minecraft:crossbow", "Pirate's Flintlock"],
                ["minecraft:bow", "Miner's Flintlock", "minecraft:crossbow", "Miner's Flintlock"],
                ["minecraft:experience_bottle", always_equal, "minecraft:experience_bottle", "Experience Bottle"],
                ["minecraft:bow", "Swiftwood Shortbow", "minecraft:spruce_leaves", "Mistleaf Bracer"],
                ["minecraft:bow", "Swiftwood Longbow", "minecraft:spruce_leaves", "Mistleaf Vambrace"],
                ["minecraft:totem_of_undying", "Cobaltean Charm", "minecraft:compass", "Cobaltean Charm"],
                ["minecraft:chainmail_leggings", "Jorts Of Monshee", "minecraft:chainmail_leggings", "Jorts of Monshee"],
                ["minecraft:stone_sword", "The Frodian Keyblade", "minecraft:stone_sword", "Frodian Keyblade"],
                ["minecraft:golden_helmet", "Rageroot Crown", "minecraft:chainmail_helmet", "Rageroot Crown"],
                ["minecraft:potion", "Wormwood Oil", "minecraft:glass_bottle", "Wormwood Oil"],
                ["minecraft:bone_meal", "Fierce Soul", "minecraft:white_dye", "Fierce Soul"],
                ["minecraft:lapis_lazuli", "Speed Charm", "minecraft:blue_dye", "Speed Charm"],
                ["minecraft:iron_hoe", "Demon's Scar", "minecraft:stone_hoe", "Demon's Scar"],
                ["minecraft:spider_spawn_egg", "Amalgamated Dissonant Energy", "nether_wart_block", "Amalgamated Dissonant Energy"],
                ["minecraft:iron_sword", "Blade of Destiny", "minecraft:stone_sword", "Blade of Destiny"],
                ["minecraft:potion", "Angry Fruit Juice", "minecraft:splash_potion", "Extinguisher"],
                ["minecraft:sunflower", "Despondent Doubloon", "minecraft:gold_nugget", "Despondent Doubloon"],
                ["minecraft:nether_star", "Aurora Shard", "minecraft:quartz", "Aurora Shard"],
                ["minecraft:stone_pickaxe", "Skyfeller", "minecraft:golden_pickaxe", "Skyfeller"],
                ["minecraft:crossbow", "Crimson Chicken", "minecraft:crossbow", "Red Rooster"],
                ["minecraft:sunflower", "Whirpool Coin", "minecraft:sunflower", "Whirlpool Coin"],
                ["minecraft:iron_axe", "Saving Grace", "minecraft:stone_axe", "Saving Grace"],
                ["minecraft:golden_shovel", "Myriad's Rapier", "minecraft:golden_sword", "Myriad's Rapier"],
                ["minecraft:turtle_helmet", "Seadiver's Shell", "minecraft:golden_chestplate", "Seadiver's Shell"],
                ["minecraft:quartz", "Fragment of Remorse", "minecraft:quartz", "Shard of Remorse"],
                ["minecraft:gold_ingot", "Blackflame Hoard", "minecraft:gold_ingot", "Blackflame Emblem"],
                ["minecraft:skeleton_skull", "Valgus' Skull", "minecraft:player_head", "Valgus' Skull"],
                ["minecraft:wooden_sword", "Requiem", "minecraft:jungle_sapling", "Deepdream Roots"],
                ["minecraft:leather_helmet", "Dragon Scale Helm", "minecraft:leather_helmet", "Crimstonian Helm"],
                ["minecraft:leather_chestplate", "Dragon Scale Chestpiece", "minecraft:leather_chestplate", "Crimstonian Chestpiece"],
                ["minecraft:leather_leggings", "Dragon Scale Leggings", "minecraft:leather_leggings", "Crimstonian Leggings"],
                ["minecraft:leather_boots", "Dragon Scale Boots", "minecraft:leather_boots", "Crimstonian Boots"],
                ["minecraft:potion", "Dragon Brew", "minecraft:potion", "Crimstonian Brew"],
                ["minecraft:player_head", "Ender Eyes", "minecraft:player_head", "Gaze of Judgement"],
                ["minecraft:stone_hoe", "Enderwrath", "minecraft:stone_hoe", "Sleepwalker's Sickle"],
                ["minecraft:leather_chestplate", "Bluescale Torso", "minecraft:leather_chestplate", "Warden's Ruin"],
                ["minecraft:stone_sword", "Frostbite", "minecraft:stone_sword", "Cascade"],
                ["minecraft:ink_sac", "Mitten of Madness", "minecraft:golden_hoe", "Mitten of Madness"],
                ["minecraft:flower_banner_pattern", "Alchemist's Bag", "minecraft:splash_potion", "Alchemist's Bag"],
                ["minecraft:flower_banner_pattern", "Alchemist's Bag (0)", "minecraft:splash_potion", "Alchemist's Bag (0)"],
                ["minecraft:flower_banner_pattern", "Alchemist's Bag (1)", "minecraft:splash_potion", "Alchemist's Bag (1)"],
                ["minecraft:flower_banner_pattern", "Alchemist's Bag (2)", "minecraft:splash_potion", "Alchemist's Bag (2)"],
                ["minecraft:flower_banner_pattern", "Alchemist's Bag (3)", "minecraft:splash_potion", "Alchemist's Bag (3)"],
                ["minecraft:flower_banner_pattern", "Alchemist's Bag (4)", "minecraft:splash_potion", "Alchemist's Bag (4)"],
                ["minecraft:flower_banner_pattern", "Alchemist's Bag (5)", "minecraft:splash_potion", "Alchemist's Bag (5)"],
                ["minecraft:flower_banner_pattern", "Alchemist's Bag (6)", "minecraft:splash_potion", "Alchemist's Bag (6)"],
                ["minecraft:flower_banner_pattern", "Alchemist's Bag (7)", "minecraft:splash_potion", "Alchemist's Bag (7)"],
                ["minecraft:flower_banner_pattern", "Alchemist's Bag (8)", "minecraft:splash_potion", "Alchemist's Bag (8)"],
                ["minecraft:flower_banner_pattern", "Alchemist's Bag (9)", "minecraft:splash_potion", "Alchemist's Bag (9)"],
                ["minecraft:flower_banner_pattern", "Alchemist's Bag (10)", "minecraft:splash_potion", "Alchemist's Bag (10)"],
                ["minecraft:flower_banner_pattern", "Alchemist's Bag (11)", "minecraft:splash_potion", "Alchemist's Bag (11)"],
                ["minecraft:flower_banner_pattern", "Alchemist's Bag (12)", "minecraft:splash_potion", "Alchemist's Bag (12)"],
                ["minecraft:flower_banner_pattern", "Alchemist's Bag (13)", "minecraft:splash_potion", "Alchemist's Bag (13)"],
                ["minecraft:flower_banner_pattern", "Alchemist's Bag (14)", "minecraft:splash_potion", "Alchemist's Bag (14)"],
                ["minecraft:flower_banner_pattern", "Alchemist's Bag (15)", "minecraft:splash_potion", "Alchemist's Bag (15)"],
                ["minecraft:flower_banner_pattern", "Alchemist's Bag (16)", "minecraft:splash_potion", "Alchemist's Bag (16)"],
                ["minecraft:wooden_shovel", "Stick Of Beating", "minecraft:wooden_shovel", "Stick of Beating"],
                ["minecraft:leather_chestplate", "Eternal Shroud", "minecraft:leather_chestplate", "Phoenix Shroud"],
                ["minecraft:nether_star", "Ancestral Sigil", "minecraft:firework_star", "Ancestral Sigil"],
                ["minecraft:gold_nugget", "Unlucky Horseshoe (Instant)", "minecraft:gold_nugget", "Unlucky Horseshoe"],
                ["minecraft:magma_block", "Roguelike Key Normal", "minecraft:magma_block", "Ephemeral Key Normal"],
                ["minecraft:magma_block", "Roguelike Key Hardcore Tier I", "minecraft:magma_block", "Ephemeral Key Hardcore Tier I"],
                ["minecraft:magma_block", "Roguelike Key Hardcore Tier II", "minecraft:magma_block", "Ephemeral Key Hardcore Tier II"],
                ["minecraft:magma_block", "Roguelike Key Hardcore Tier III", "minecraft:magma_block", "Ephemeral Key Hardcore Tier III"],
                ["minecraft:magma_block", "Roguelike Key Hardcore Tier IV", "minecraft:magma_block", "Ephemeral Key Hardcore Tier IV"],
                ["minecraft:magma_block", "Roguelike Key Hardcore Tier V", "minecraft:magma_block", "Ephemeral Key Hardcore Tier V"],
                ["minecraft:magma_block", "Roguelike Key Classic Tier I", "minecraft:magma_block", "Ephemeral Key Classic Tier I"],
                ["minecraft:magma_block", "Roguelike Key Classic Tier II", "minecraft:magma_block", "Ephemeral Key Classic Tier II"],
                ["minecraft:magma_block", "Roguelike Key Classic Tier III", "minecraft:magma_block", "Ephemeral Key Classic Tier III"],
                ["minecraft:magma_block", "Roguelike Key Classic Tier IV", "minecraft:magma_block", "Ephemeral Key Classic Tier IV"],
                ["minecraft:magma_block", "Roguelike Key Classic Tier V", "minecraft:magma_block", "Ephemeral Key Classic Tier V"],
                ["minecraft:golden_pickaxe", "Clearcut", "minecraft:golden_pickaxe", "Clearmine"],
                ["minecraft:golden_shovel", "Clearcut", "minecraft:golden_shovel", "Cleardig"],
                ["minecraft:bone", "Wand of C'Zanil", "minecraft:bone", "C'Zanil's Charm"],
                ["minecraft:bone", "Charm of C'Zanil", "minecraft:bone", "C'Zanil's Talisman"],
                ["minecraft:stick", "Shapeshifter's Wand", "minecraft:leather", "Shapeshifter's Gauntlet"],
                ["minecraft:leather_chestplate", "Basilisk Scales", "minecraft:leather_chestplate", "Ghoulskin Vestment"],
                ["minecraft:leather_chestplate", "Basilisk Hide", "minecraft:leather_chestplate", "Ghoulskin Shroud"],
                ["minecraft:stone_axe", "Searing Wrath", "minecraft:stone_axe", "Acrid Wrath"],
                ["minecraft:leather_helmet", "Iceborn Helmet", "minecraft:leather_helmet", "Seasoaked Helmet"],
                ["minecraft:stone_sword", "Iceborn Runeblade", "minecraft:stone_sword", "Seasoaked Runeblade"],
                ["minecraft:shield", "Imperial Bulwark", "minecraft:shield", "Walls of Velara"],
                ["minecraft:stick", "Deathchill Staff", "minecraft:stick", "Staff of the Soulseeker"],
                ["minecraft:stone_axe", "Giant's Axe", "minecraft:stone_axe", "Velara Crusher"],
                ["minecraft:stone_hoe", "Cryptkeeper's Scythe", "minecraft:stone_hoe", "Forest's Reaper"],
                ["minecraft:stone_pickaxe", "Pebblebane", "minecraft:stone_pickaxe", "Rubblebane"],
                ["minecraft:bow", "Demonbreath", "minecraft:bow", "Screamcaller"],
                ["minecraft:crossbow", "Redstone Repeater", "minecraft:crossbow", "Callum's Spellslinger"],
                ["minecraft:stone_sword", "Spirit Blade", "minecraft:stone_sword", "Bandit's Dagger"],
                ["minecraft:stone_sword", "Angelic Sword", "minecraft:stone_sword", "Axtan Blade"],
                ["minecraft:stone_sword", "Shadow Spike", "minecraft:stone_sword", "Abomination Splinter"],
                ["minecraft:stone_axe", "Mithril Cleaver", "minecraft:stone_axe", "Jaguartooth Cleaver"],
                ["minecraft:blaze_rod", "Hell's Fury", "minecraft:blaze_rod", "Molten Fury"],
                ["minecraft:stone_pickaxe", "Obsidian Pickaxe", "minecraft:stone_pickaxe", "Jaguartooth Pickaxe"],
                ["minecraft:bow", "Tempest Caller", "minecraft:bow", "Narsen's Will"],
                ["minecraft:crossbow", "Heaven's Blessing", "minecraft:crossbow", "Aphelion's Gift"],
                ["minecraft:leather_chestplate", "Voidguard", "minecraft:leather_chestplate", "Veilguard"],
                ["minecraft:leather_leggings", "Angelic Pants", "minecraft:leather_leggings", "Axtan Greaves"],
                ["minecraft:leather_helmet", "Scout's Visage", "minecraft:leather_helmet", "Visage of the Lost"],
                ["minecraft:crossbow", "Erix's Bloody Stream", "minecraft:crossbow", "Warforged Crossbow"],
                ["minecraft:quartz", "Render's Ruthless Claw", "minecraft:stone_hoe", "Render's Ruthless Claw"],
                ["minecraft:white_tulip", "Teewie's Eternal Tulip", "minecraft:pink_tulip", "Eternal Bloom"],
                ["minecraft:stone_axe", "The Annihilator", "minecraft:stone_axe", "Lunatic's Respite"],
                ["minecraft:bow", "Arcane Hailstorm", "minecraft:bow", "Xanatull's Skystorm"],
                ["minecraft:leather_boots", "Shadowborn Boots", "minecraft:leather_boots", "Grovewalker Sandals"],
                ["minecraft:leather_leggings", "Busty's Hotter Pants", "minecraft:leather_leggings", "Sulfuric Robes"],
                ["minecraft:jungle_sapling", "Staff of Memories", "minecraft:jungle_sapling", "Willowtwist Memory"],
                ["minecraft:iron_sword", "Soul Blade", "minecraft:iron_sword", "Mage Hunter's Blade"],
                ["minecraft:iron_axe", "Wrath of the Mountain", "minecraft:iron_axe", "Wrath of the Mountains"],
                ["minecraft:iron_boots", "Steel Sabatons", "minecraft:iron_boots", "Frostguard Sabatons"],
                ["minecraft:iron_pickaxe", "Sunshard Pickaxe", "minecraft:iron_pickaxe", "Molta's Labor"],
                ["minecraft:iron_sword", "Archangel's Blade", "minecraft:iron_sword", "Oasis Scimitar"],
                ["minecraft:chainmail_chestplate", "Archangel's Mail", "minecraft:chainmail_chestplate", "Oasis Mail"],
                ["minecraft:crossbow", "Soulstream", "minecraft:crossbow", "Phantom Flintlock"],
                ["minecraft:leather_boots", "Scarlet Ward", "minecraft:leather_boots", "Spellbinder's Slippers"],
                ["minecraft:stone_axe", "Redrum Cleaver", "minecraft:stone_axe", "Archeologist's Hammer"],
                ["minecraft:iron_sword", "Jade Longsword", "minecraft:iron_sword", "True Ice Splinter"],
                ["minecraft:iron_sword", "Hell's Torment", "minecraft:iron_sword", "Amaranth Blade"],
                ["minecraft:crossbow", "Steel Arbalest", "minecraft:crossbow", "Springloaded Gadget"],
                ["minecraft:bow", "Hoarfrost Shortbow", "minecraft:bow", "Legionis"],
                ["minecraft:iron_hoe", "Rebellious Scythe", "minecraft:iron_hoe", "Gambler's Cane"],
                ["minecraft:iron_sword", "Erisana", "minecraft:iron_sword", "Chainbreaker's Blight"],
                ["minecraft:iron_sword", "Bloodthirsty Crescent", "minecraft:iron_sword", "Putrid Maw"],
                ["minecraft:golden_boots", "Ifrit's Sandals", "minecraft:golden_boots", "Aspiration"],
                ["minecraft:iron_sword", "Glass Rapier", "minecraft:iron_sword", "Treasured Rapier"],
                ["minecraft:golden_hoe", "Spider's Crux", "minecraft:golden_hoe", "Marauder's Haze"],
                ["minecraft:wooden_sword", "Fangridian Cattcrappe", "minecraft:stone_sword", "Civit Dagger"],
                ["minecraft:stone_hoe", "Brimstone Scythe", "minecraft:stone_hoe", "Cavewalker Scythe"],
                ["minecraft:trident", "Celsian Sarissa", "minecraft:iron_sword", "Celsian Sarissa"],
                ["minecraft:trident", "Thalassic Lance", "minecraft:iron_sword", "Thalassic Lance"],
                ["minecraft:shield", "Tlaxia's Bulwark", "minecraft:shield", "Soulspoiler's Bulwark"],
                ["minecraft:leather_boots", "Shadowborn Boots", "minecraft:leather_boots", "Grovewalker Sandals"],
                ["minecraft:leather_helmet", None, "minecraft:leather_helmet", "Leather Cap"],
                ["minecraft:leather_chestplate", None, "minecraft:leather_chestplate", "Leather Tunic"],
                ["minecraft:leather_leggings", None, "minecraft:leather_leggings", "Leather Pants"],
                ["minecraft:leather_boots", None, "minecraft:leather_boots", "Leather Boots"],
                ["minecraft:golden_helmet", None, "minecraft:golden_helmet", "Golden Helmet"],
                ["minecraft:golden_chestplate", None, "minecraft:golden_chestplate", "Golden Chestplate"],
                ["minecraft:golden_leggings", None, "minecraft:golden_leggings", "Golden Leggings"],
                ["minecraft:golden_boots", None, "minecraft:golden_boots", "Golden Boots"],
                ["minecraft:chainmail_helmet", None, "minecraft:chainmail_helmet", "Chainmail Helmet"],
                ["minecraft:chainmail_chestplate", None, "minecraft:chainmail_chestplate", "Chainmail Chestplate"],
                ["minecraft:chainmail_leggings", None, "minecraft:chainmail_leggings", "Chainmail Leggings"],
                ["minecraft:chainmail_boots", None, "minecraft:chainmail_boots", "Chainmail Boots"],
                ["minecraft:iron_helmet", None, "minecraft:iron_helmet", "Iron Helmet"],
                ["minecraft:iron_chestplate", None, "minecraft:iron_chestplate", "Iron Chestplate"],
                ["minecraft:iron_leggings", None, "minecraft:iron_leggings", "Iron Leggings"],
                ["minecraft:iron_boots", None, "minecraft:iron_boots", "Iron Boots"],
                ["minecraft:diamond_helmet", None, "minecraft:diamond_helmet", "Diamond Helmet"],
                ["minecraft:diamond_chestplate", None, "minecraft:diamond_chestplate", "Diamond Chestplate"],
                ["minecraft:diamond_leggings", None, "minecraft:diamond_leggings", "Diamond Leggings"],
                ["minecraft:diamond_boots", None, "minecraft:diamond_boots", "Diamond Boots"],
                ["minecraft:netherite_helmet", None, "minecraft:netherite_helmet", "Netherite Helmet"],
                ["minecraft:netherite_chestplate", None, "minecraft:netherite_chestplate", "Netherite Chestplate"],
                ["minecraft:netherite_leggings", None, "minecraft:netherite_leggings", "Netherite Leggings"],
                ["minecraft:netherite_boots", None, "minecraft:netherite_boots", "Netherite Boots"],
                ["minecraft:turtle_helmet", None, "minecraft:turtle_helmet", "Turtle Shell"],
                ["minecraft:iron_shovel", "Earthsculpter", "minecraft:iron_shovel", "Earthsculptor"],
                ["minecraft:leather_boots", "Aquien's Boots", "minecraft:leather_boots", "Aquiren's Boots"],
                ["minecraft:leather_chestplate", "Robes of the Pharoah", "minecraft:leather_chestplate", "Robes of the Pharaoh"],
                ["minecraft:apple", "Forbidden Fruit of Ta‘Ksaav", "minecraft:apple", "Forbidden Fruit of Ta'Ksaav"],
                ["minecraft:apple", "Forbidden Fruit of Ta’Ksaav", "minecraft:apple", "Forbidden Fruit of Ta'Ksaav"],
                ["minecraft:cobweb", "Soul Conglomerate", "minecraft:cobweb", "Twisted Soul Thread"],
                ["minecraft:leather_chestplate", "Cultist's Robe", "minecraft:leather_chestplate", "Lunatic's Robe"],
                ["minecraft:player_head", "Earth‘s Maw", "minecraft:player_head", "Earth's Maw"],
                ["minecraft:player_head", "Earth’s Maw", "minecraft:player_head", "Earth's Maw"],
                ["minecraft:iron_boots", "Lieutenant‘s Storm", "minecraft:iron_boots", "Lieutenant's Storm"],
                ["minecraft:iron_boots", "Lieutenant’s Storm", "minecraft:iron_boots", "Lieutenant's Storm"],
                ["minecraft:chainmail_chestplate", "Veil‘s Horizon", "minecraft:chainmail_chestplate", "Veil's Horizon"],
                ["minecraft:chainmail_chestplate", "Veil’s Horizon", "minecraft:chainmail_chestplate", "Veil's Horizon"],
                ["minecraft:shield", "Mu‘xro‘hkr", "minecraft:shield", "Mu'xro'hkr"],
                ["minecraft:shield", "Mu‘xro’hkr", "minecraft:shield", "Mu'xro'hkr"],
                ["minecraft:shield", "Mu’xro‘hkr", "minecraft:shield", "Mu'xro'hkr"],
                ["minecraft:shield", "Mu’xro’hkr", "minecraft:shield", "Mu'xro'hkr"],
                ["minecraft:turtle_helmet", "Steel Aparatus", "minecraft:turtle_helmet", "Steel Apparatus"],
                ["minecraft:leather_leggings", "Seeker‘s Pursuit", "minecraft:leather_leggings", "Seeker's Pursuit"],
                ["minecraft:leather_leggings", "Seeker’s Pursuit", "minecraft:leather_leggings", "Seeker's Pursuit"],
                ["minecraft:golden_helmet", "Excavator‘s Hardlamp", "minecraft:iron_helmet", "Excavator's Hardlamp"],
                ["minecraft:golden_helmet", "Excavator’s Hardlamp", "minecraft:iron_helmet", "Excavator's Hardlamp"],
                ["minecraft:bamboo", "Ancient rifle barrel", "minecraft:bamboo", "Ancient Rifle Barrel"],
                ["minecraft:stone_sword", "Biding Saber", "minecraft:stone_sword", "Biding Sabre"],
                ["minecraft:blaze_rod", "Ta'Ferna's Quiver", "minecraft:stick", "Ta'Ferna's Quiver"],
                ["minecraft:leather_leggings", "Demoncaller Robes", "minecraft:leather_leggings", "Demoncaller Pants"],
                ["minecraft:leather_chestplate", "Soulbinder's Curiass", "minecraft:leather_chestplate", "Soulbinder's Cuirass"],
                ["minecraft:shield", "Soulspoiler's Bulwark", "minecraft:shield", "Soulblighter's Bulwark"],
                ["minecraft:bone", "Soulspoiler's Scepter", "minecraft:bone", "Soulblighter's Scepter"],
                ["minecraft:leather_leggings", "Soulblighter's Scepter", "minecraft:bone", "Soulblighter's Scepter"],
                ["minecraft:magma_block", "Ephemeral Key Normal", "minecraft:magma_block", "Ephemeral Key - Practice"],
                ["minecraft:magma_block", "Ephemeral Key Hardcore Tier I", "minecraft:magma_block", "Ephemeral Key - Standard"],
                ["minecraft:magma_block", "Ephemeral Key Hardcore Tier II", "minecraft:magma_block", "Ephemeral Key - Standard"],
                ["minecraft:magma_block", "Ephemeral Key Hardcore Tier III", "minecraft:magma_block", "Ephemeral Key - Standard"],
                ["minecraft:magma_block", "Ephemeral Key Hardcore Tier IV", "minecraft:magma_block", "Ephemeral Key - Standard"],
                ["minecraft:magma_block", "Ephemeral Key Hardcore Tier V", "minecraft:magma_block", "Ephemeral Key - Standard"],
                ["minecraft:magma_block", "Ephemeral Key Classic Tier I", "minecraft:magma_block", "Ephemeral Key - Fullwipe"],
                ["minecraft:magma_block", "Ephemeral Key Classic Tier II", "minecraft:magma_block", "Ephemeral Key - Fullwipe"],
                ["minecraft:magma_block", "Ephemeral Key Classic Tier III", "minecraft:magma_block", "Ephemeral Key - Fullwipe"],
                ["minecraft:magma_block", "Ephemeral Key Classic Tier IV", "minecraft:magma_block", "Ephemeral Key - Fullwipe"],
                ["minecraft:magma_block", "Ephemeral Key Classic Tier V", "minecraft:magma_block", "Ephemeral Key - Fullwipe"],
                ["minecraft:golden_hoe", "Thresher‘s Harvester", "minecraft:golden_hoe", "Thresher's Harvester"],
                ["minecraft:golden_hoe", "Thresher’s Harvester", "minecraft:golden_hoe", "Thresher's Harvester"],
                ["minecraft:splash_potion", "C‘Zanil‘s Transgression", "minecraft:splash_potion", "C'Zanil's Transgression"],
                ["minecraft:splash_potion", "C’Zanil’s Transgression", "minecraft:splash_potion", "C'Zanil's Transgression"],
                ["minecraft:turtle_spawn_egg", "Permafrost Golem Dummy", "minecraft:turtle_spawn_egg", "Permafrost Construct Dummy"],
                ["minecraft:chainmail_boots", "Consumption", "minecraft:chainmail_helmet", "Consumption"],
                ["minecraft:quartz", "Purified Claw", "minecraft:stone_sword", "Purified Claw"],
                ["minecraft:prismarine_shard", "Weathered Rune", "minecraft:popped_chorus_fruit", "Weathered Rune"],
                ["minecraft:stone_sword", "Bandit‘s Dagger", "minecraft:stone_sword", "Bandit's Dagger"],
                ["minecraft:stone_sword", "Bandit’s Dagger", "minecraft:stone_sword", "Bandit's Dagger"],
                ["minecraft:end_rod", "Spyglass", "minecraft:spyglass", "Spyglass"],
                ["minecraft:end_rod", "Telescope", "minecraft:spyglass", "Telescope"],
                ["minecraft:end_rod", "Midnight Spyglass", "minecraft:spyglass", "Midnight Spyglass"],
                ["minecraft:end_rod", "Captain Bijou's Spyglass", "minecraft:spyglass", "Captain Bijou's Spyglass"],
                ["minecraft:leather_chestplate", "Dichen Gambison", "minecraft:leather_chestplate", "Dichen Gambeson"],
                ["minecraft:gray_dye", "Archite Ring", "minecraft:gray_dye", "Archos Ring"],
                ["minecraft:firework_star", "Hyperchromatic Archite Ring", "minecraft:firework_star", "Hyperchromatic Archos Ring"],
                ["minecraft:golden_apple", None, "minecraft:golden_apple", "Kingfruit"],
                ["minecraft:enchanted_golden_apple", None, "minecraft:enchanted_golden_apple", "Soulfruit"],
                # ["minecraft:potion", None, "minecraft:potion", "Bygone Brew"], //TODO: Fix Water bottles and uncomment this line
                ["minecraft:splash_potion", None, "minecraft:potion", "Bygone Brew"],
                ["minecraft:lingering_potion", None, "minecraft:potion", "Bygone Brew"],
                ["minecraft:zombie_head", "Rebooting Lesser Charm", "minecraft:zombie_head", "Lesser Rebooting Charm"],
                ["minecraft:zombie_head", "Rebooting Greater Charm", "minecraft:zombie_head", "Greater Rebooting Charm"],
                ["minecraft:ice", "Hailing Lesser Charm", "minecraft:ice", "Lesser Hailing Charm"],
                ["minecraft:ice", "Hailing Greater Charm", "minecraft:ice", "Greater Hailing Charm"],
                ["minecraft:ice", "Hailing Swift Charm", "minecraft:ice", "Swift Hailing Charm"],
                ["minecraft:ice", "Hailing Distant Charm", "minecraft:ice", "Distant Hailing Charm"],
                ["minecraft:ice", "Hailing Sedated Charm", "minecraft:ice", "Sedated Hailing Charm"],
                ["minecraft:purple_concrete_powder", "Innate Lesser Charm", "minecraft:purple_concrete_powder", "Lesser Innate Charm"],
                ["minecraft:purple_concrete_powder", "Innate Greater Charm", "minecraft:purple_concrete_powder", "Greater Innate Charm"],
                ["minecraft:purple_concrete_powder", "Innate Swift Charm", "minecraft:purple_concrete_powder", "Swift Innate Charm"],
                ["minecraft:purple_concrete_powder", "Innate Sedated Charm", "minecraft:purple_concrete_powder", "Sedated Innate Charm"],
                ["minecraft:yellow_stained_glass", "Tesseract of Elements (u)", "minecraft:yellow_stained_glass", "Tesseract of the Elements (u)"],
                ["minecraft:nether_star", "Harrakafar's Roar", "minecraft:nether_star", "Harrakfar's Roar"],
                ["minecraft:blaze_rod", "C.A.L.D.E.R Non-Dimensional Wand", "minecraft:blaze_rod", "C.A.L.D.E.R. Non-Dimensional Wand"],
                ["minecraft:white_stained_glass", "Tesseract of Festivity", "minecraft:ice", "Tesseract of Festivity"],
                ["minecraft:white_stained_glass", "Tesseract of Festivity (u)", "minecraft:ice", "Tesseract of Festivity (u)"],
                ["minecraft:iron_boots", "Pelias’ Last Step", "minecraft:iron_boots", "Pelias' Last Step"],
                ["minecraft:iron_boots", "Pelias‘ Last Step", "minecraft:iron_boots", "Pelias' Last Step"],
                ["minecraft:slime_ball", "Hycenea’s Vinelash", "minecraft:slime_ball", "Hycenea's Vinelash"],
                ["minecraft:slime_ball", "Hycenea‘s Vinelash", "minecraft:slime_ball", "Hycenea's Vinelash"],
                ["minecraft:diamond_sword", "Inflation I", "minecraft:golden_sword", "Inflation I"],
                ["minecraft:diamond_sword", "Inflation II", "minecraft:golden_sword", "Inflation II"],
                ["minecraft:diamond_sword", "Inflation II", "minecraft:golden_sword", "Inflation II"],
                ["minecraft:diamond_sword", "Inflation III", "minecraft:golden_sword", "Inflation III"],
                ["minecraft:diamond_sword", "Inflation IV", "minecraft:golden_sword", "Inflation IV"],
                ["minecraft:diamond_sword", "Inflation V", "minecraft:golden_sword", "Inflation V"],
                ["minecraft:diamond_sword", "Inflation VI", "minecraft:golden_sword", "Inflation VI"],
                ["minecraft:diamond_sword", "Inflation VII", "minecraft:golden_sword", "Inflation VII"],
                ["minecraft:diamond_sword", "Inflation VIII", "minecraft:golden_sword", "Inflation VIII"],
                ["minecraft:diamond_sword", "Inflation IX", "minecraft:golden_sword", "Inflation IX"],
                ["minecraft:diamond_sword", "Inflation X", "minecraft:golden_sword", "Inflation X"],
                ["minecraft:diamond_sword", "Inflation XI", "minecraft:golden_sword", "Inflation XI"],
                ["minecraft:diamond_sword", "Inflation XII", "minecraft:golden_sword", "Inflation XII"],
                ["minecraft:diamond_sword", "Inflation XIII", "minecraft:golden_sword", "Inflation XIII"],
                ["minecraft:diamond_sword", "Inflation XIV", "minecraft:golden_sword", "Inflation XIV"],
                ["minecraft:diamond_sword", "Inflation XV", "minecraft:golden_sword", "Inflation XV"],
                ["minecraft:diamond_sword", "Inflation XVI", "minecraft:golden_sword", "Inflation XVI"],
                ["minecraft:diamond_sword", "Inflation XVII", "minecraft:golden_sword", "Inflation XVII"],
                ["minecraft:diamond_sword", "Inflation XVIII", "minecraft:golden_sword", "Inflation XVIII"],
                ["minecraft:diamond_sword", "Inflation XIX", "minecraft:golden_sword", "Inflation XIX"],
                ["minecraft:diamond_sword", "Inflation XX", "minecraft:golden_sword", "Inflation XX"],
                ["minecraft:diamond_sword", "Inflation XXI", "minecraft:golden_sword", "Inflation XXI"],
                ["minecraft:diamond_sword", "Inflation XXII", "minecraft:golden_sword", "Inflation XXII"],
                ["minecraft:diamond_sword", "Inflation XXIII", "minecraft:golden_sword", "Inflation XXIII"],
                ["minecraft:diamond_sword", "Inflation XXIV", "minecraft:golden_sword", "Inflation XXIV"],
                ["minecraft:diamond_sword", "Inflation XXV", "minecraft:golden_sword", "Inflation XXV"],
                ["minecraft:diamond_sword", "Inflation XXVI", "minecraft:golden_sword", "Inflation XXVI"],
                ["minecraft:diamond_sword", "Inflation XXVII", "minecraft:golden_sword", "Inflation XXVII"],
                ["minecraft:diamond_sword", "Inflation XXVIII", "minecraft:golden_sword", "Inflation XXVIII"],
                ["minecraft:diamond_sword", "Inflation XXIX", "minecraft:golden_sword", "Inflation XXIX"],
                ["minecraft:diamond_sword", "Inflation XXX", "minecraft:golden_sword", "Inflation XXX"],
                ["minecraft:diamond_sword", "Inflation XXXI", "minecraft:golden_sword", "Inflation XXXI"],
                ["minecraft:diamond_sword", "Hyperinflation", "minecraft:golden_sword", "Hyperinflation"],
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
