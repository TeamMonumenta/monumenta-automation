import sys
import os
import uuid
import json
import re
from typing import Union
from lib_py3.common import get_entity_uuid, uuid_to_mc_uuid_tag_int_array, update_plain_tag
from lib_py3.json_file import jsonFile

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))

from quarry.types import nbt
from quarry.types.nbt import TagCompound, TagList, TagString, TagShort
from brigadier.string_reader import StringReader

_single_item_locations = (
    "ArmorItem",
    "Book",
    "Item",
    "RecordItem",
    "SaddleItem",
    "Trident",
)

_list_item_locations = (
    "ChargedProjectiles", # Crossbows
    "ArmorItems",
    "EnderItems",
    "HandItems",
    "Inventory",
    "Items",
)

def translate_lore(lore: str) -> str:
    lore = lore.replace(r"\\u0027", "'")
    lore = lore.replace(r"\\u00a7", "§")
    lore = lore.replace(r"When in main hand:", "When in Main Hand:")
    lore = lore.replace(r"When in off hand:", "When in Off Hand:")
    lore = lore.replace(r"When on head:", "When on Head:")
    lore = lore.replace(r"When on body:", "When on Body:")
    lore = lore.replace(r"When on legs:", "When on Legs:")
    lore = lore.replace(r"When on feet:", "When on Feet:")
    # This script doesn't do these
    # Use this shell script:
    #    find . -type f -exec perl -p -i -e 's|\+0\.([0-9]) Knockback Resistance|+\1 Knockback Resistance|g' {} \;
    #"&9+0.X Knockback Resistance" --> "&9+X Knockback Resistance"
    #"&c-0.X Knockback Resistance" --> "&c-X Knockback Resistance"
    return lore

def translate_attribute_name(name: str) -> str:
    name = name.replace("maxHealth", "max_health")
    name = name.replace("followRange", "follow_range")
    name = name.replace("knockbackResistance", "knockback_resistance")
    name = name.replace("movementSpeed", "movement_speed")
    name = name.replace("attackDamage", "attack_damage")
    name = name.replace("armor", "armor")
    name = name.replace("armorToughness", "armor_toughness")
    name = name.replace("attackKnockback", "attack_knockback")
    name = name.replace("attackSpeed", "attack_speed")
    name = name.replace("luck", "luck")
    name = name.replace("jumpStrength", "jump_strength")
    name = name.replace("flyingSpeed", "flying_speed")
    name = name.replace("spawnReinforcements", "spawn_reinforcements")

    if name == "max_health" or name == "generic.max_health":
        name = "minecraft:generic.max_health"
    if name == "follow_range" or name == "generic.follow_range":
        name = "minecraft:generic.follow_range"
    if name == "knockback_resistance" or name == "generic.knockback_resistance":
        name = "minecraft:generic.knockback_resistance"
    if name == "movement_speed" or name == "generic.movement_speed":
        name = "minecraft:generic.movement_speed"
    if name == "attack_damage" or name == "generic.attack_damage":
        name = "minecraft:generic.attack_damage"
    if name == "armor" or name == "generic.armor":
        name = "minecraft:generic.armor"
    if name == "armor_toughness" or name == "generic.armor_toughness":
        name = "minecraft:generic.armor_toughness"
    if name == "attack_knockback" or name == "generic.attack_knockback":
        name = "minecraft:generic.attack_knockback"
    if name == "attack_speed" or name == "generic.attack_speed":
        name = "minecraft:generic.attack_speed"
    if name == "luck" or name == "generic.luck":
        name = "minecraft:generic.luck"
    if name == "jump_strength" or name == "horse.jump_strength":
        name = "minecraft:horse.jump_strength"
    if name == "flying_speed" or name == "generic.flying_speed":
        name = "minecraft:generic.flying_speed"
    if name == "zombie.spawn_reinforcements" or name == "zombie.spawn_reinforcements":
        name = "minecraft:zombie.spawn_reinforcements"
    return name

def upgrade_uuid_if_present(nbt_: TagCompound, regenerateUUIDs=False) -> None:
    if nbt_.has_path("OwnerUUID"):
        owneruuid = uuid.UUID(nbt_.at_path("OwnerUUID").value)
        nbt_.value["Owner"] = uuid_to_mc_uuid_tag_int_array(owneruuid)
        nbt_.value.pop("OwnerUUID")

    if nbt_.has_path("UUIDMost") or nbt_.has_path("UUIDLeast") or nbt_.has_path("UUID"):
        modifierUUID = None
        if not regenerateUUIDs:
            modifierUUID = get_entity_uuid(nbt_)
        if modifierUUID is None:
            modifierUUID = uuid.uuid4()

        if nbt_.has_path("UUIDMost"):
            nbt_.value.pop("UUIDMost")
        if nbt_.has_path("UUIDLeast"):
            nbt_.value.pop("UUIDLeast")
        nbt_.value["UUID"] = uuid_to_mc_uuid_tag_int_array(modifierUUID)

    # Somehow this attribute is still missing a UUID - fix it
    if nbt_.has_path("AttributeName") and not nbt_.has_path("UUID"):
        modifierUUID = uuid.uuid4()
        nbt_.value["UUID"] = uuid_to_mc_uuid_tag_int_array(modifierUUID)

def upgrade_attributes(attributes_nbt: TagCompound, regenerateUUIDs=False) -> None:
    for attribute in attributes_nbt.value:
        if attribute.has_path("Name"):
            mod = attribute.at_path("Name")
            mod.value = translate_attribute_name(mod.value)

        if attribute.has_path("AttributeName"):
            mod = attribute.at_path("AttributeName")
            mod.value = translate_attribute_name(mod.value)

        if attribute.has_path("Modifiers"):
            upgrade_attributes(attribute.at_path("Modifiers"), regenerateUUIDs=regenerateUUIDs)

        upgrade_uuid_if_present(attribute, regenerateUUIDs=regenerateUUIDs)

enchant_id_map = {
    0:"minecraft:protection",
    1:"minecraft:fire_protection",
    2:"minecraft:feather_falling",
    3:"minecraft:blast_protection",
    4:"minecraft:projectile_protection",
    5:"minecraft:respiration",
    6:"minecraft:aqua_affinity",
    7:"minecraft:thorns",
    8:"minecraft:depth_strider",
    9:"minecraft:frost_walker",
    10:"minecraft:binding_curse",
    16:"minecraft:sharpness",
    17:"minecraft:smite",
    18:"minecraft:bane_of_arthropods",
    19:"minecraft:knockback",
    20:"minecraft:fire_aspect",
    21:"minecraft:looting",
    22:"minecraft:sweeping",
    32:"minecraft:efficiency",
    33:"minecraft:silk_touch",
    34:"minecraft:unbreaking",
    35:"minecraft:fortune",
    48:"minecraft:power",
    49:"minecraft:punch",
    50:"minecraft:flame",
    51:"minecraft:infinity",
    61:"minecraft:luck_of_the_sea",
    62:"minecraft:lure",
    65:"minecraft:loyalty",
    66:"minecraft:impaling",
    67:"minecraft:riptide",
    68:"minecraft:channeling",
    70:"minecraft:mending",
    71:"minecraft:vanishing_curse",
}

potion_id_map = {
    1: "minecraft:speed",
    2: "minecraft:slowness",
    3: "minecraft:haste",
    4: "minecraft:mining_fatigue",
    5: "minecraft:strength",
    6: "minecraft:instant_health",
    7: "minecraft:instant_damage",
    8: "minecraft:jump_boost",
    9: "minecraft:nausea",
    10: "minecraft:regeneration",
    11: "minecraft:resistance",
    12: "minecraft:fire_resistance",
    13: "minecraft:water_breathing",
    14: "minecraft:invisibility",
    15: "minecraft:blindness",
    16: "minecraft:night_vision",
    17: "minecraft:hunger",
    18: "minecraft:weakness",
    19: "minecraft:poison",
    20: "minecraft:wither",
    21: "minecraft:health_boost",
    22: "minecraft:absorption",
    23: "minecraft:saturation",
    24: "minecraft:glowing",
    25: "minecraft:levitation",
    26: "minecraft:luck",
    27: "minecraft:unluck",
    28: "minecraft:slow_falling",
    29: "minecraft:conduit_power",
    30: "minecraft:dolphins_grace",
    31: "minecraft:bad_omen",
    32: "minecraft:hero_of_the_village",
    33: "minecraft:darkness",
}

cat_variant_id_map = (
    "minecraft:tabby",
    "minecraft:black",
    "minecraft:red",
    "minecraft:siamese",
    "minecraft:british_shorthair",
    "minecraft:calico",
    "minecraft:persian",
    "minecraft:ragdoll",
    "minecraft:white",
    "minecraft:jellie",
    "minecraft:all_black",
)

def rename_key(nbt_: TagCompound, from_: str, to: str) -> None:
    if nbt_.has_path(from_):
        nbt_.value[to] = nbt_.at_path(from_)
        nbt_.value.pop(from_)

def v1_20_4_convert_legacy_effect(nbt_: TagCompound, legacy_path: str, new_path: str ) -> None:
    if not nbt_.has_path(legacy_path):
        return
    new_id = potion_id_map[nbt_.at_path(legacy_path).value]
    nbt_.value.pop(legacy_path)
    nbt_.value[new_path] = TagString(new_id)

def v1_20_4_convert_mob_effect(nbt_: TagCompound) -> None:
    v1_20_4_convert_legacy_effect(nbt_, "Id", "id")
    v1_20_4_convert_legacy_effect(nbt_, "EffectId", "id")
    rename_key(nbt_, "Ambient", "ambient")
    rename_key(nbt_, "Amplifier", "amplifier")
    rename_key(nbt_, "Duration", "duration")
    rename_key(nbt_, "EffectDuration", "duration")
    rename_key(nbt_, "ShowParticles", "show_particles")
    rename_key(nbt_, "ShowIcon", "show_icon")
    rename_key(nbt_, "FactorCalculationData", "factor_calculation_data")
    rename_key(nbt_, "HiddenEffect", "hidden_effect")
    rename_key(nbt_, "Trident", "item")
    rename_key(nbt_, "Fuse", "fuse")

    if nbt_.has_path("hidden_effect"):
        v1_20_4_convert_mob_effect(nbt_.at_path("hidden_effect"))

def v1_20_4_convert_mob_effect_list(nbt_: TagCompound, old_path: str, new_path: str) -> None:
    if not nbt_.has_path(old_path):
        return

    for entry in nbt_.at_path(old_path).value:
        v1_20_4_convert_mob_effect(entry)

    rename_key(nbt_, old_path, new_path)

def v1_20_4_convert_stew(nbt_: TagCompound) -> TagList:
    c = TagCompound({})
    c.value["id"] = TagString(potion_id_map[nbt_.at_path("EffectId").value])
    c.value["duration"] = nbt_.at_path("EffectDuration")

    nbt_.value.pop("EffectId")
    nbt_.value.pop("EffectDuration")

    l = TagList([])
    l.value.push(c)
    return l

def update_1_20_4(nbt_: TagCompound) -> None:
    # beacon
    v1_20_4_convert_legacy_effect(nbt_, "Primary", "primary_effect")
    v1_20_4_convert_legacy_effect(nbt_, "Secondary", "secondary_effect")
    # area_effect_cloud
    v1_20_4_convert_mob_effect_list(nbt_, "Effects", "effects")
    v1_20_4_convert_mob_effect_list(nbt_, "ActiveEffects", "active_effects")
    # arrow, item
    v1_20_4_convert_mob_effect_list(nbt_, "CustomPotionEffects", "custom_potion_effects")

    if nbt_.has_path("EffectId") and nbt_.has_path("EffectDuration"):
        nbt_.value["stew_effects"] = v1_20_4_convert_stew(nbt_)

def upgrade_entity(nbt_: TagCompound, regenerateUUIDs=False, tagsToRemove: list = [], remove_non_plain_display=False) -> None:
    if not isinstance(nbt_, TagCompound):
        raise ValueError(f"Expected TagCompound, got {type(nbt_)}")

    for junk in tagsToRemove:
        if junk in nbt_.value:
            nbt_.value.pop(junk)

    if nbt_.has_path("id"):
        nbt_.at_path("id").value = nbt_.at_path("id").value.replace("zombie_pigman", "zombified_piglin")

    if nbt_.has_path("CatType"):
        cat_type = nbt_.at_path("CatType").value % len(cat_variant_id_map)
        variant = cat_variant_id_map[cat_type]
        del nbt_.value["CatType"]
        nbt_.value["variant"] = TagString(variant)

    # Upgrade infinite potion effects (suspicious stew)
    if nbt_.has_path("Effects"):
        custom_effects = nbt_.at_path("Effects")
        if isinstance(custom_effects, TagList): # This should only ever be a list
            for custom_effect in custom_effects.value:
                if isinstance(custom_effect, TagCompound): # This should only ever be a compound
                    if custom_effect.has_path("EffectDuration"):
                        duration = custom_effect.at_path("EffectDuration").value
                        if isinstance(duration, int) and duration >= 100000:
                            # Infinite potion effects have a duration of -1
                            custom_effect.at_path("EffectDuration").value = -1

    # Upgrade infinite potion effects (mob active effects)
    if nbt_.has_path("ActiveEffects"):
        custom_effects = nbt_.at_path("ActiveEffects")
        if isinstance(custom_effects, TagList): # This should only ever be a list
            for custom_effect in custom_effects.value:
                if isinstance(custom_effect, TagCompound): # This should only ever be a compound
                    if custom_effect.has_path("Duration"):
                        duration = custom_effect.at_path("Duration").value
                        if isinstance(duration, int) and duration >= 100000:
                            # Infinite potion effects have a duration of -1
                            custom_effect.at_path("Duration").value = -1

    # Upgrade infinite potion effects (potions)
    if nbt_.has_path("CustomPotionEffects"):
        custom_effects = nbt_.at_path("CustomPotionEffects")
        if isinstance(custom_effects, TagList): # This should only ever be a list
            for custom_effect in custom_effects.value:
                if isinstance(custom_effect, TagCompound): # This should only ever be a compound
                    if custom_effect.has_path("Duration"):
                        duration = custom_effect.at_path("Duration").value
                        if isinstance(duration, int) and duration >= 100000:
                            # Infinite potion effects have a duration of -1
                            custom_effect.at_path("Duration").value = -1

    # Upgrade potions
    if nbt_.has_path("Potion"):
        if isinstance(nbt_.at_path("Potion"), TagCompound):
            nbt_.value["Item"] = nbt_.at_path("Potion")
            nbt_.value.pop("Potion")
        elif isinstance(nbt_.at_path("Potion"), TagString):
            nbt_.at_path("Potion").value = nbt_.at_path("Potion").value.replace("empty", "mundane") # .replace("awkward", "mundane")

    # Upgrade UUIDMost/UUIDLeast -> UUID
    upgrade_uuid_if_present(nbt_, regenerateUUIDs=regenerateUUIDs)

    # Upgrade AttributeModifiers (value name change & UUID)
    if nbt_.has_path("AttributeModifiers"):
        upgrade_attributes(nbt_.at_path("AttributeModifiers"), regenerateUUIDs=regenerateUUIDs)
    if nbt_.has_path("Attributes"):
        upgrade_attributes(nbt_.at_path("Attributes"), regenerateUUIDs=regenerateUUIDs)

    # Rename "ench" -> "Enchantments"
    if nbt_.has_path("ench"):
        nbt_.value["Enchantments"] = nbt_.at_path("ench")
        nbt_.value.pop("ench")

    # Clean up Enchantments
    if "Enchantments" in nbt_.value:
        ench_list = nbt_.at_path("Enchantments")
        for enchant in ench_list.value:
            if not "lvl" in enchant.value:
                raise KeyError("Item enchantment does not contain 'lvl'")
            if not "id" in enchant.value:
                raise KeyError("Item enchantment does not contain 'id'")

            # Upgrade numeric enchants to strings
            if isinstance(enchant.at_path("id").value, int):
                enchant.value["id"] = TagString(enchant_id_map[enchant.at_path("id").value])

            # Make sure the enchantment is namespaced
            if not ":" in enchant.at_path("id").value:
                enchant.at_path("id").value = "minecraft:" + enchant.at_path("id").value

            # Make sure the tags are in the correct order and of the correct type
            enchant_id = enchant.at_path("id").value
            enchant_lvl = enchant.at_path("lvl").value
            enchant.value.pop("id")
            enchant.value.pop("lvl")
            enchant.value["lvl"] = TagShort(enchant_lvl)
            enchant.value["id"] = TagString(enchant_id)

    # Fix unicode section symbols and quotes in display names
    if nbt_.has_path("display.Name"):
        name_possibly_json = nbt_.at_path("display.Name").value
        name_possibly_json = name_possibly_json.replace("\\u0027", "'")
        name_possibly_json = name_possibly_json.replace("\\u00a7", "§")
        nbt_.at_path("display.Name").value = name_possibly_json

    if nbt_.has_path("display.Lore"):
        new_lore_list = []
        for lore_nbt in nbt_.at_path("display.Lore").value:
            lore_text_possibly_json = translate_lore(lore_nbt.value)
            try:
                json.loads(lore_text_possibly_json)
                new_lore_list.append(TagString(lore_text_possibly_json))
            except Exception:
                json_data = {"text": lore_text_possibly_json}
                json_str = json.dumps(json_data, ensure_ascii=False, separators=(',', ':'))
                new_lore_list.append(TagString(json_str))
        nbt_.at_path("display.Lore").value = new_lore_list

    # Upgrade items the entity is carrying
    for location in _single_item_locations:
        if nbt_.has_path(location):
            upgrade_entity(nbt_.at_path(location), regenerateUUIDs=regenerateUUIDs, tagsToRemove=tagsToRemove, remove_non_plain_display=remove_non_plain_display)
    for location in _list_item_locations:
        if nbt_.has_path(location):
            for item in nbt_.at_path(location).value:
                upgrade_entity(item, regenerateUUIDs=regenerateUUIDs, tagsToRemove=tagsToRemove, remove_non_plain_display=remove_non_plain_display)
    if nbt_.has_path("Offers.Recipes"):
        for item in nbt_.at_path("Offers.Recipes").value:
            if item.has_path("buy"):
                upgrade_entity(item.at_path("buy"), regenerateUUIDs=regenerateUUIDs, tagsToRemove=tagsToRemove, remove_non_plain_display=remove_non_plain_display)
            if item.has_path("buyB"):
                upgrade_entity(item.at_path("buyB"), regenerateUUIDs=regenerateUUIDs, tagsToRemove=tagsToRemove, remove_non_plain_display=remove_non_plain_display)
            if item.has_path("sell"):
                upgrade_entity(item.at_path("sell"), regenerateUUIDs=regenerateUUIDs, tagsToRemove=tagsToRemove, remove_non_plain_display=remove_non_plain_display)

    # Upgrade skull items
    if nbt_.has_path("SkullOwner.Id"):
        if isinstance(nbt_.at_path("SkullOwner.Id"), TagString):
            nbt_.at_path("SkullOwner").value["Id"] = uuid_to_mc_uuid_tag_int_array(uuid.UUID(nbt_.at_path("SkullOwner.Id").value))

    # Recurse over list tags
    for recurse_tag in ["Passengers", "SpawnPotentials"]:
        if nbt_.has_path(recurse_tag):
            for entry in nbt_.at_path(recurse_tag).value:
                upgrade_entity(entry, regenerateUUIDs=regenerateUUIDs, tagsToRemove=tagsToRemove, remove_non_plain_display=remove_non_plain_display)

    # Recurse over non-list tags
    for recurse_tag in ["SelectedItem", "tag", "SpawnData", "Entity"]:
        if nbt_.has_path(recurse_tag):
            upgrade_entity(nbt_.at_path(recurse_tag), regenerateUUIDs=regenerateUUIDs, tagsToRemove=tagsToRemove, remove_non_plain_display=remove_non_plain_display)

    # Recurse over Command block contents
    if nbt_.has_path("Command"):
        # TODO: This probably should be plumbed through, not just set to auto
        nbt_.at_path("Command").value = upgrade_text_containing_mojangson(nbt_.at_path("Command").value, convert_checks_to_plain="auto")

    # Once all the inner upgrading is done, build the `plain` tag from the display tag
    update_plain_tag(nbt_)

    if remove_non_plain_display:
        if nbt_.has_path("display"):
            display = nbt_.at_path("display")
            if display.has_path("Name"):
                display.value.pop("Name")
            if display.has_path("Lore"):
                display.value.pop("Lore")
            if len(display.value) <= 0:
                nbt_.value.pop("display")
    update_1_20_4(nbt_)

def upgrade_text_containing_mojangson(line: str, convert_checks_to_plain: str = "never", regenerateUUIDs=False) -> str:
    """
    Takes in a line and parses/upgrades all the NBT contained in that line
    """

    # Don't upgrade comments
    if line.startswith("#"):
        return line

    reader = StringReader(line)
    result_line = ''

    while reader.can_read():
        if reader.peek() == '{' and not result_line.endswith("scores=") and not result_line.endswith("advancements="):
            cursor = reader.get_cursor()
            try:
                data = nbt.MojangsonParser(reader).parse_compound()

                # Even though this parsed correctly as an NBT compound, it might actually have been a JSON compound.
                # This is often used in tellraws like:
                #    tellraw @s [{text:"Achievement Get:",bold:1b,color:"blue"},{text:" Fisherman I",color:"white"}]
                # Super annoying. Don't want to mangle the JSON by converting it to mojangson.
                # So - try to parse this same string as JSON instead
                embedded_fragment = line[cursor:reader.get_cursor()]
                embedded_json = None
                try:
                    embedded_json = json.loads(embedded_fragment)
                except Exception:
                    try:
                        embedded_json = json.loads(embedded_fragment.replace(r"""\'""", r"""'""").replace(r'''\\\\''', r'''\\'''))
                    except Exception:
                        pass

                if embedded_json is not None:
                    # This is actually a JSON string!
                    # Even more annoyingly, sometimes we have mojangson embedded within the JSON...
                    embedded_json = upgrade_json_walk(embedded_json, convert_checks_to_plain=convert_checks_to_plain, regenerateUUIDs=regenerateUUIDs)
                    result_line += json.dumps(embedded_json, ensure_ascii=False, sort_keys=False, separators=(',', ':'))
                    # Conveniently, the string reader is already pointed at the ending } in the original string
                else:
                    # Not a JSON string
                    remove_non_plain_display = False
                    if convert_checks_to_plain == "always":
                        remove_non_plain_display = True
                    elif convert_checks_to_plain == "auto":
                        if "clear " in result_line or result_line.endswith("nbt=") or result_line.endswith("nbt=!"):
                            remove_non_plain_display = True
                        if "execute " in result_line and " run " not in result_line[result_line.rfind("execute "):]:
                            remove_non_plain_display = True
                        if re.match(".*fill .* replace [^{]+$", result_line):
                            remove_non_plain_display = True

                    upgrade_entity(data, remove_non_plain_display=remove_non_plain_display, regenerateUUIDs=regenerateUUIDs)

                    result_line += data.to_mojangson()
            except Exception as e:
                # These prints are incredibly noisy - lots of things have { but don't parse as mojangson. Ignore them.
                #print("Failed to parse, skipping:", e)
                #print("Line:", line)
                result_line += '{'
                reader.set_cursor(cursor + 1)
        else:
            result_line += reader.peek()
            reader.skip()

    return result_line

def upgrade_json_walk(obj: Union[str, dict, list, int, bool], convert_checks_to_plain: str = "never", regenerateUUIDs=False) -> Union[str, dict, list, int, bool]:
    if isinstance(obj, str):
        return upgrade_text_containing_mojangson(obj, convert_checks_to_plain, regenerateUUIDs=regenerateUUIDs)
    if isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            if k == "conditions" and convert_checks_to_plain == "auto":
                # If we're recursing into a conditions block, do convert any checks it finds to plain checks
                new_obj[k] = upgrade_json_walk(v, convert_checks_to_plain="always", regenerateUUIDs=regenerateUUIDs)
            else:
                new_obj[k] = upgrade_json_walk(v, convert_checks_to_plain, regenerateUUIDs=regenerateUUIDs)
        return new_obj
    if isinstance(obj, list):
        new_obj = []
        for v in obj:
            new_obj.append(upgrade_json_walk(v, convert_checks_to_plain, regenerateUUIDs=regenerateUUIDs))
        return new_obj
    return obj

def upgrade_json_file(path: str, convert_checks_to_plain: str = "never", regenerateUUIDs=False):
    json_file = jsonFile(path)
    json_file.dict = upgrade_json_walk(json_file.dict, convert_checks_to_plain, regenerateUUIDs=regenerateUUIDs)
    json_file.save()

def upgrade_mcfunction_file(path: str, convert_checks_to_plain: str = "never", regenerateUUIDs=False):
    lines = []
    with open(path, 'r') as fp:
        lines = fp.readlines()
    newlines = []
    for line in lines:
        newlines.append(upgrade_text_containing_mojangson(line, convert_checks_to_plain, regenerateUUIDs=regenerateUUIDs))
    with open(path, 'w') as fp:
        fp.writelines(newlines)
