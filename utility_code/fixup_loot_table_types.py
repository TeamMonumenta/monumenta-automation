#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
from tempfile import mkstemp
from shutil import move
from os import fdopen, remove
import demjson
import collections
import traceback

replacements = [
        ("UUIDLeast", "l"),
        ("UUIDMost", "l"),
        ("Amount", "d"),
        ("lvl", "s"),
        ("id", "s"),
        ("Ambient", "b"),
        ("ShowParticles", "b"),
        ("Duration", ""),
        ("Id", "b"),
        ("Amplifier", "b"),
        ("Operation", ""),
        ("color", ""),
    ]

# The order of enchants when applied to items from loot tables
# Ordering is very important
enchantLookup = collections.OrderedDict()
enchantLookup[6]  = "Aqua Affinity",
enchantLookup[8]  = "Depth Strider",
enchantLookup[32] = "Efficiency",
enchantLookup[9]  = "Frost Walker",
enchantLookup[61] = "Luck of the Sea",
enchantLookup[62] = "Lure",
enchantLookup[0]  = "Protection",
enchantLookup[1]  = "Fire Protection",
enchantLookup[4]  = "Projectile Protection",
enchantLookup[48] = "Power",
enchantLookup[49] = "Punch",
enchantLookup[50] = "Flame",
enchantLookup[5]  = "Respiration",
enchantLookup[16] = "Sharpness",
enchantLookup[33] = "Silk Touch",
enchantLookup[17] = "Smite",
enchantLookup[18] = "Bane of Arthropods",
enchantLookup[34] = "Unbreaking",
enchantLookup[3]  = "Blast Protection",
enchantLookup[19] = "Knockback",
enchantLookup[35] = "Fortune",
enchantLookup[2]  = "Feather Falling",
enchantLookup[10] = "Curse of Binding",
enchantLookup[70] = "Mending",
enchantLookup[7]  = "Thorns",
enchantLookup[20] = "Fire Aspect",
enchantLookup[21] = "Looting",
enchantLookup[22] = "Sweeping Edge",
enchantLookup[51] = "Infinity",
enchantLookup[71] = "Curse of Vanishing",

# The list of overrides for the ordering above - some enchantment combinations
# don't follow that hierarchy for some reason
#
# If an item has these specific enchantments they are re-ordered to match the ordering here
# Again, ordering is very important
enchantOverride = [
    # Fire Aspect / Knockback
    (20, 19),

    # Fire Aspect / Unbreaking
    (20, 34),

    # Warlock Gear - Fire Prot / Unbreaking / Binding / Blast / Projectile
    (1, 34, 10, 3, 4),

    # Explorer's Cap - Prot / Respiration / Aqua Affinity
    (0, 5, 6),

    # Phantom's Hood
    (1, 3, 4),

    # Gem Encrusted Manpance
    (0, 8, 5, 70),

    # Cerulean Mage Robes
    (0, 4, 34),

    # Busty's Hot / Hotter Pants
    (1, 70, 3),

    # Scalawag's Hatchet
    (16, 32, 34),

    # Nereid Gear
    # Prot / Unbreaking / Proj Prot / Respiration / Aqua Affinity
    (0, 34, 4, 5, 6),
    # Depth Strider / Prot / Unbreaking / Proj Prot / Respiration
    (8, 0, 34, 4, 5),
    # Depth Strider / Prot / Unbreaking / Proj Prot
    (8, 0, 34, 4),

    # Archmage's Vestment - Prot / Fire Prot / Unbreaking / Blast / Projectile
    (0, 1, 34, 3, 4)
]

def sort_ench(ench):
    s = set()
    for i in ench:
        s.add(i["id"])

    # Check each override list to see if this is enchant combination requires a special case
    for override in enchantOverride:
        overSet = set(override)
        if (overSet == s):
            # Yes, this is a special case
            #print "Sets equal!"
            #print s

            # Re-order the list of enchants to match the override
            retlist = [];
            for targetId in override:
                for i in ench:
                    if (i["id"] == targetId):
                        retlist += [i,]

            #print retlist
            return retlist

    # No special case found, sort based on the enchant keys
    return sorted(ench, key=lambda x: enchantLookup.keys().index(int(x["id"])))

def fixup_tag(tag):
    # Remove type specifiers
    tag = re.sub(r'(:[-\.0-9]+)[lLsSbBfFdD]*', r'\1', tag)
    #print tag

    # May throw exception
    decoded = demjson.decode(tag)
    #print decoded

    # Create a new JSON object here from the original with the correct ordering
    ordered = collections.OrderedDict()

    if ("ench" in decoded):
        #print "ENCHANT:", decoded["ench"]

        ordered["ench"] = []
        for x in decoded["ench"]:
            ordered["ench"] += [collections.OrderedDict({"lvl": x["lvl"], "id": x["id"]}),]

        # Sort by special "correct" order loot tables apply enchants
        ordered["ench"] = sort_ench(ordered["ench"])

        del decoded["ench"]
        #print "AFTER:  ", ordered["ench"]

    if ("Unbreakable" in decoded):
        ordered["Unbreakable"] = decoded["Unbreakable"]
        del decoded["Unbreakable"]

    if ("HideFlags" in decoded):
        ordered["HideFlags"] = decoded["HideFlags"]
        del decoded["HideFlags"]

    if ("SkullOwner" in decoded):
        # TODO: This tag is more complicated than this, not sure if ordering matters
        ordered["SkullOwner"] = decoded["SkullOwner"]
        del decoded["SkullOwner"]

    if ("BlockEntityTag" in decoded):
        # TODO: This tag is more complicated than this, not sure if ordering matters
        ordered["BlockEntityTag"] = decoded["BlockEntityTag"]
        del decoded["BlockEntityTag"]

    if ("CustomPotionColor" in decoded):
        ordered["CustomPotionColor"] = decoded["CustomPotionColor"]
        del decoded["CustomPotionColor"]

    if ("CustomPotionEffects" in decoded):
        #print "ATTRIBUTE:", decoded["CustomPotionEffects"]

        ordered["CustomPotionEffects"] = []
        for x in decoded["CustomPotionEffects"]:
            new = collections.OrderedDict()

            if ("Ambient" in x):
                new["Ambient"] = x["Ambient"]
            if ("ShowParticles" in x):
                new["ShowParticles"] = x["ShowParticles"]
            if ("Duration" in x):
                new["Duration"] = x["Duration"]
            if ("Id" in x):
                new["Id"] = x["Id"]
            if ("Amplifier" in x):
                new["Amplifier"] = x["Amplifier"]

            ordered["CustomPotionEffects"] += [new,]

        del decoded["CustomPotionEffects"]
        #print "AFTER:  ", ordered["display"]

    if ("Potion" in decoded):
        ordered["Potion"] = decoded["Potion"]
        del decoded["Potion"]

    if ("display" in decoded):
        #print "DISPLAY:", decoded["display"]

        ordered["display"] = collections.OrderedDict()
        if "Lore" in decoded["display"]:
            ordered["display"]["Lore"] = decoded["display"]["Lore"];

        if "color" in decoded["display"]:
            ordered["display"]["color"] = decoded["display"]["color"];

        if "Name" in decoded["display"]:
            ordered["display"]["Name"] = decoded["display"]["Name"];

        del decoded["display"]
        #print "AFTER:  ", ordered["display"]

    if ("AttributeModifiers" in decoded):
        #print "ATTRIBUTE:", decoded["AttributeModifiers"]

        ordered["AttributeModifiers"] = []
        for x in decoded["AttributeModifiers"]:
            new = collections.OrderedDict()

            if ("UUIDMost" in x):
                new["UUIDMost"] = x["UUIDMost"]
            if ("UUIDLeast" in x):
                new["UUIDLeast"] = x["UUIDLeast"]
            if ("Amount" in x):
                new["Amount"] = x["Amount"]
            if ("Slot" in x):
                new["Slot"] = x["Slot"]
            if ("AttributeName" in x):
                new["AttributeName"] = x["AttributeName"]
            if ("Operation" in x):
                new["Operation"] = x["Operation"]
            if ("Name" in x):
                new["Name"] = x["Name"]

            ordered["AttributeModifiers"] += [new,]

        del decoded["AttributeModifiers"]
        #print "AFTER:  ", ordered["display"]

    for x in decoded:
        raise ValueError("Found unsupported dictionary entry:" + x)

    encoded = demjson.encode(ordered, sort_keys=demjson.SORT_PRESERVE)

    # Re-add section symbols
    encoded = encoded.replace(u"\\u00a7", u"§")
    # Remove quotes from keys
    encoded = re.sub(r'"(\w+)"\s*:', r'\1:', encoded)
    # Re-escape remaining quotes
    encoded = encoded.replace(r'"', r'\"')

    # Re-add the type specifiers
    for repl in replacements:
        #print "Fixing: " + repl[0]
        encoded = re.sub(r"(" + repl[0] + r":)([-\.0-9]+)[lLsSbBfFdD]*", r"\1\2" + repl[1], encoded)

    return encoded


# Apply NBT tag fixups to all NBT strings found in a loot table file
def fixup_file(filePath):
    # Create temp file
    fh, abs_path = mkstemp()
    with fdopen(fh,'w') as new_file:
        with open(filePath) as old_file:
            for line in old_file:
                # Read lines from original file, modify them, and write them to the new file

                # Only operate on tag strings
                m = re.search(r'(^\s*"tag":\s*")(\{.*})"\s*$', line)
                if m:
                    preamble = m.group(1)
                    tag = m.group(2)

                    # Remove backslashes
                    tag = tag.replace("\\", "")

                    try:
                        tag = fixup_tag(tag)

                    except Exception:
                        print "Skipping file: " + filePath
                        print "Failing tag was: '" + tag + "'"
                        traceback.print_exc()
                        print
                        print
                        return

                    tag = preamble + tag + '"\n'
                    line = tag.encode('utf8')
                    #print tag

                new_file.write(line)

    #Remove original file
    remove(filePath)

    #Move new file
    move(abs_path, filePath)


if ((len(sys.argv) != 2) or (not os.path.isdir(sys.argv[1]))):
    sys.exit("Usage: " + sys.argv[0] + " </path/to/loot_tables>")

lootPath = sys.argv[1]

for root, dirs, files in os.walk(lootPath):
    for file in files:
        if file.endswith(".json"):
             filePath = os.path.join(root, file)
             #print(filePath)
             fixup_file(filePath)

sys.exit("Done")

