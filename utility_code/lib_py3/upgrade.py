import sys
import os
import uuid
import json
import traceback
import re
from typing import Union
from lib_py3.common import parse_name_possibly_json, get_entity_uuid, uuid_to_mc_uuid_tag_int_array
from lib_py3.json_file import jsonFile

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))

from quarry.types import nbt
from quarry.types.nbt import TagCompound, TagString, TagShort
from quarry.types.text_format import unformat_text
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

# https://catonmat.net/my-favorite-regex
# Matches all printable ascii characters, from ' ' to '~'
non_plain_regex=re.compile('[^ -~]')

def update_plain_tag(item_nbt: TagCompound) -> None:
    """Given a Minecraft item's tag, (re)generate tag.plain.

    tag.plain stores the unformatted version of formatted text on items.
    """
    for formatted_path, plain_subpath_parts, is_multipath in (
        ('display.Name', ['display', 'Name'], False),
        ('CustomName', ['CustomName',], False),
        ('display.Lore[]', ['display', 'Lore'], True),
        #('pages[]', ['pages'], True),
    ):
        if item_nbt.count_multipath(formatted_path) > 0:
            if item_nbt.has_path("id") and "command_block" in item_nbt.at_path("id").value:
                # Don't store plain names for command blocks
                continue

            plain_subpath_parts = ['plain'] + plain_subpath_parts
            plain_subtag = item_nbt
            for plain_subpath in plain_subpath_parts[:-1]:
                if not plain_subtag.has_path(plain_subpath):
                    plain_subtag.value[plain_subpath] = nbt.TagCompound({})
                plain_subtag = plain_subtag.at_path(plain_subpath)
            plain_subpath = plain_subpath_parts[-1]

            if is_multipath:
                plain_subtag.value[plain_subpath] = nbt.TagList([])
                for formatted in item_nbt.iter_multipath(formatted_path):
                    formatted_str = formatted.value
                    plain_str = parse_name_possibly_json(formatted_str, remove_color=True)
                    plain_str = non_plain_regex.sub('', plain_str).strip()
                    plain_subtag.at_path(plain_subpath).value.append(nbt.TagString(plain_str))

            else: # Single path, not multipath
                formatted = item_nbt.at_path(formatted_path)
                formatted_str = formatted.value
                plain_str = parse_name_possibly_json(formatted_str, remove_color=True)
                plain_str = non_plain_regex.sub('', plain_str).strip()
                plain_subtag.value[plain_subpath] = nbt.TagString(plain_str)

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
    return name

def upgrade_uuid_if_present(nbt: TagCompound, regenerateUUIDs = False) -> None:
    if nbt.has_path("OwnerUUID"):
        owneruuid = uuid.UUID(nbt.at_path("OwnerUUID").value)
        nbt.value["Owner"] = uuid_to_mc_uuid_tag_int_array(owneruuid)
        nbt.value.pop("OwnerUUID")

    if nbt.has_path("UUIDMost") or nbt.has_path("UUIDLeast") or nbt.has_path("UUID"):
        modifierUUID = None
        if not regenerateUUIDs:
            modifierUUID = get_entity_uuid(nbt)
        if modifierUUID is None:
            modifierUUID = uuid.uuid4()

        if nbt.has_path("UUIDMost"):
            nbt.value.pop("UUIDMost")
        if nbt.has_path("UUIDLeast"):
            nbt.value.pop("UUIDLeast")
        nbt.value["UUID"] = uuid_to_mc_uuid_tag_int_array(modifierUUID)

def upgrade_attributes(attributes_nbt: TagCompound, regenerateUUIDs = False) -> None:
    for attribute in attributes_nbt.value:
        if attribute.has_path("Name"):
            mod = attribute.at_path("Name")
            mod.value = translate_attribute_name(mod.value)

        if attribute.has_path("AttributeName"):
            mod = attribute.at_path("AttributeName")
            mod.value = translate_attribute_name(mod.value)

        if attribute.has_path("Modifiers"):
            upgrade_attributes(attribute.at_path("Modifiers"))

        upgrade_uuid_if_present(attribute, regenerateUUIDs)

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

def upgrade_entity(nbt: TagCompound, regenerateUUIDs: bool = False, tagsToRemove: list = [], remove_non_plain_display: bool = False) -> None:
    if type(nbt) is not TagCompound:
        raise ValueError(f"Expected TagCompound, got {type(nbt)}")

    for junk in tagsToRemove:
        if junk in nbt.value:
            nbt.value.pop(junk)

    if nbt.has_path("id"):
        nbt.at_path("id").value = nbt.at_path("id").value.replace("zombie_pigman", "zombified_piglin")

    # Upgrade potions
    if nbt.has_path("Potion"):
        if type(nbt.at_path("Potion")) is TagCompound:
            nbt.value["Item"] = nbt.at_path("Potion")
            nbt.value.pop("Potion")
        elif type(nbt.at_path("Potion")) is TagString:
            nbt.at_path("Potion").value = nbt.at_path("Potion").value.replace("empty", "mundane").replace("awkward", "mundane")

    # Upgrade UUIDMost/UUIDLeast -> UUID
    upgrade_uuid_if_present(nbt, regenerateUUIDs)

    # Upgrade AttributeModifiers (value name change & UUID)
    if nbt.has_path("AttributeModifiers"):
        upgrade_attributes(nbt.at_path("AttributeModifiers"))
    if nbt.has_path("Attributes"):
        upgrade_attributes(nbt.at_path("Attributes"))

    # Rename "ench" -> "Enchantments"
    if nbt.has_path("ench"):
        nbt.value["Enchantments"] = nbt.at_path("ench")
        nbt.value.pop("ench")

    # Clean up Enchantments
    if "Enchantments" in nbt.value:
        ench_list = nbt.at_path("Enchantments")
        for enchant in ench_list.value:
            if not "lvl" in enchant.value:
                raise KeyError("Item enchantment does not contain 'lvl'")
            if not "id" in enchant.value:
                raise KeyError("Item enchantment does not contain 'id'")

            # Upgrade numeric enchants to strings
            if type(enchant.at_path("id").value) is int:
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
    if nbt.has_path("display.Name"):
        name_possibly_json = nbt.at_path("display.Name").value
        name_possibly_json = name_possibly_json.replace("\\u0027", "'")
        name_possibly_json = name_possibly_json.replace("\\u00a7", "§")
        nbt.at_path("display.Name").value = name_possibly_json

    if nbt.has_path("display.Lore"):
        new_lore_list = []
        for lore_nbt in nbt.at_path("display.Lore").value:
            lore_text_possibly_json = translate_lore(lore_nbt.value)
            try:
                json.loads(lore_text_possibly_json)
                new_lore_list.append(TagString(lore_text_possibly_json))
            except Exception:
                json_data = {"text": lore_text_possibly_json}
                json_str = json.dumps(json_data, ensure_ascii=False, separators=(',', ':'))
                new_lore_list.append(TagString(json_str))
        nbt.at_path("display.Lore").value = new_lore_list

    # Upgrade items the entity is carrying
    for location in _single_item_locations:
        if nbt.has_path(location):
            upgrade_entity(nbt.at_path(location), regenerateUUIDs, tagsToRemove, remove_non_plain_display)
    for location in _list_item_locations:
        if nbt.has_path(location):
            for item in nbt.at_path(location).value:
                upgrade_entity(item, regenerateUUIDs, tagsToRemove, remove_non_plain_display)
    if nbt.has_path("Offers.Recipes"):
        for item in nbt.at_path("Offers.Recipes").value:
            if item.has_path("buy"):
                upgrade_entity(item.at_path("buy"), regenerateUUIDs, tagsToRemove, remove_non_plain_display)
            if item.has_path("buyB"):
                upgrade_entity(item.at_path("buyB"), regenerateUUIDs, tagsToRemove, remove_non_plain_display)
            if item.has_path("sell"):
                upgrade_entity(item.at_path("sell"), regenerateUUIDs, tagsToRemove, remove_non_plain_display)

    # Upgrade skull items
    if nbt.has_path("SkullOwner.Id"):
        if type(nbt.at_path("SkullOwner.Id")) is TagString:
            nbt.at_path("SkullOwner").value["Id"] = uuid_to_mc_uuid_tag_int_array(uuid.UUID(nbt.at_path("SkullOwner.Id").value))

    # Recurse over passengers
    if nbt.has_path("Passengers"):
        for passenger in nbt.at_path("Passengers").value:
            upgrade_entity(passenger, regenerateUUIDs, tagsToRemove, remove_non_plain_display)

    # Recurse over item tags
    if nbt.has_path("tag"):
        upgrade_entity(nbt.at_path("tag"), regenerateUUIDs, tagsToRemove, remove_non_plain_display)

    # Recurse over Command block contents
    if nbt.has_path("Command"):
        # TODO: This probably should be plumbed through, not just set to auto
        nbt.at_path("Command").value = upgrade_text_containing_mojangson(nbt.at_path("Command").value, convert_checks_to_plain="auto")

    # Once all the inner upgrading is done, build the `plain` tag from the display tag
    update_plain_tag(nbt)

    if remove_non_plain_display:
        if nbt.has_path("display"):
            display = nbt.at_path("display")
            if display.has_path("Name"):
                display.value.pop("Name")
            if display.has_path("Lore"):
                display.value.pop("Lore")
            if len(display.value) <= 0:
                nbt.value.pop("display")

def upgrade_text_containing_mojangson(line: str, convert_checks_to_plain: str = "never") -> str:
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
                except Exception as e:
                    try:
                        embedded_json = json.loads(embedded_fragment.replace(r"""\'""", r"""'""").replace(r'''\\\\''', r'''\\'''))
                    except Exception as e:
                        pass

                if embedded_json is not None:
                    # This is actually a JSON string!
                    # Even more annoyingly, sometimes we have mojangson embedded within the JSON...
                    embedded_json = upgrade_json_walk(embedded_json, convert_checks_to_plain=convert_checks_to_plain)
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

                    upgrade_entity(data, remove_non_plain_display=remove_non_plain_display)

                    result_line += data.to_mojangson()
            except Exception as e:
                print("Failed to parse, skipping:", e)
                print("Line:", line)
                result_line += '{'
                reader.set_cursor(cursor + 1)
        else:
            result_line += reader.peek()
            reader.skip()

    return result_line

def upgrade_json_walk(obj: Union[str, dict, list, int, bool], convert_checks_to_plain: str = "never") -> Union[str, dict, list, int, bool]:
    if isinstance(obj, str):
        return upgrade_text_containing_mojangson(obj, convert_checks_to_plain)
    elif isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            if k == "conditions" and convert_checks_to_plain == "auto":
                # If we're recursing into a conditions block, do convert any checks it finds to plain checks
                new_obj[k] = upgrade_json_walk(v, convert_checks_to_plain="always")
            else:
                new_obj[k] = upgrade_json_walk(v, convert_checks_to_plain)
        return new_obj
    elif isinstance(obj, list):
        new_obj = []
        for v in obj:
            new_obj.append(upgrade_json_walk(v, convert_checks_to_plain))
        return new_obj
    else:
        return obj

def upgrade_json_file(path: str, convert_checks_to_plain: str = "never"):
    json_file = jsonFile(path)
    json_file.dict = upgrade_json_walk(json_file.dict, convert_checks_to_plain)
    json_file.save()

def upgrade_mcfunction_file(path: str, convert_checks_to_plain: str = "never"):
    lines = []
    with open(path, 'r') as fp:
        lines = fp.readlines()
    newlines = []
    for line in lines:
        newlines.append(upgrade_text_containing_mojangson(line, convert_checks_to_plain))
    with open(path, 'w') as fp:
        fp.writelines(newlines)
