import os
import sys

from lib_py3.common import always_equal
from lib_py3.common import parse_name_possibly_json
from lib_py3.common import update_plain_tag

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types.text_format import unformat_text

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

class FixBrokenStatTrack(SubstitutionRule):
    """Note: To be deleted after the next weekly update (11/02/2022)."""
    name = "Fix stat track"

    def process(self, item_meta, item):
        if not item.nbt.has_path('tag.Monumenta.PlayerModified.Infusions.StatTrack'):
            return
        infusion_nbt = item.tag.at_path('Monumenta.PlayerModified.Infusions')
        for (bad_name, good_name) in (
                ('StatTrack', 'Stat Track'),
                ('BlocksPlaced', 'Blocks Placed'),
                ('TimesConsumed', 'Times Consumed'),
                ('SpawnersBroken', 'Spawners Broken'),
                ('MobKills', 'Mob Kills'),
                ('MeleeDamageDealt', 'Melee Damage Dealt'),
                ('BossDamageDealt', 'Boss Damage Dealt'),
        ):
            if good_name in infusion_nbt.value:
                del infusion_nbt.value[good_name]
            if infusion_nbt.has_path(bad_name):
                value = infusion_nbt.value.pop(bad_name)
                infusion_nbt.value[good_name] = value

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
