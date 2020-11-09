import sys
import os
import uuid
import json
from lib_py3.common import parse_name_possibly_json, get_entity_uuid, uuid_to_mc_uuid_tag_int_array

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))

from quarry.types import nbt
from quarry.types.nbt import TagCompound, TagString
from quarry.types.text_format import unformat_text

_single_item_locations = (
    "ArmorItem",
    "Book",
    "ChargedProjectiles", # Crossbows
    "Item",
    "RecordItem",
    "SaddleItem",
    "Trident",
)

_list_item_locations = (
    "ArmorItems",
    "EnderItems",
    "HandItems",
    "Inventory",
    "Items",
)

def update_plain_tag(item_nbt: TagCompound) -> None:
    """Given a Minecraft item's tag, (re)generate tag.plain.

    tag.plain stores the unformatted version of formatted text on items.
    """
    if item_nbt.has_tag('plain'):
        item_nbt.value.pop('plain')
    for formatted_path, plain_subpath_parts, is_multipath in (
        ('display.Name', ['display', 'Name'], False),
        ('display.Lore[]', ['display', 'Lore'], True),
        #('pages[]', ['pages'], True),
    ):
        if item_nbt.count_multipath(formatted_path) > 0:
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
                    plain_subtag.at_path(plain_subpath).value.append(nbt.TagString(plain_str))

            else: # Single path, not multipath
                formatted = item_nbt.at_path(formatted_path)
                formatted_str = formatted.value
                plain_str = parse_name_possibly_json(formatted_str, remove_color=True)
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


def upgrade_entity(nbt: TagCompound, regenerateUUIDs: bool, tagsToRemove: list) -> None:
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
            upgrade_entity(nbt.at_path(location), regenerateUUIDs, tagsToRemove)
    for location in _list_item_locations:
        if nbt.has_path(location):
            for item in nbt.at_path(location).value:
                upgrade_entity(item, regenerateUUIDs, tagsToRemove)
    if nbt.has_path("Offers.Recipes"):
        for item in nbt.at_path("Offers.Recipes").value:
            if item.has_path("buy"):
                upgrade_entity(item.at_path("buy"), regenerateUUIDs, tagsToRemove)
            if item.has_path("buyB"):
                upgrade_entity(item.at_path("buyB"), regenerateUUIDs, tagsToRemove)
            if item.has_path("sell"):
                upgrade_entity(item.at_path("sell"), regenerateUUIDs, tagsToRemove)

    # Upgrade skull items
    if nbt.has_path("SkullOwner.Id"):
        if type(nbt.at_path("SkullOwner.Id")) is TagString:
            nbt.at_path("SkullOwner").value["Id"] = uuid_to_mc_uuid_tag_int_array(uuid.UUID(nbt.at_path("SkullOwner.Id").value))

    # Recurse over passengers
    if nbt.has_path("Passengers"):
        for passenger in nbt.at_path("Passengers").value:
            upgrade_entity(passenger, regenerateUUIDs, tagsToRemove)

    # Recurse over item tags
    if nbt.has_path("tag"):
        upgrade_entity(nbt.at_path("tag"), regenerateUUIDs, tagsToRemove)

    # Once all the inner upgrading is done, build the `plain` tag from the display tag
    update_plain_tag(nbt)
