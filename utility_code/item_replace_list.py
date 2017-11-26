#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lib_monumenta import item_replace

blockReplacements = (
    ("minecraft:iron_block", "air"),
    ("minecraft:iron_ore", "air"),
    ("minecraft:hopper", "air"),
    #("minecraft:gold_block", "air"), # probably fine
    #("minecraft:gold_ore", "air"),
    ("minecraft:diamond_block", "air"),
    ("minecraft:diamond_ore", "air"),
    #("minecraft:emerald_block", "air"), # probably fine
    #("minecraft:emerald_ore", "air"),

    ("minecraft:beacon", "air"),
    ("minecraft:anvil", "air"),

    # Not sure about this section
    #("enchanting_Table", "air"),
    #("quartz_ore", "air"),
)

"""
Item replacement list - this MUST be mutable!

This is an ordered list of replacement definitions
Each replacement definition is a list that contains a
    pattern matching list and a list of actions to perform

Pattern matching lists appear like so:
    Match stone and its variants:
    {"id":"minecraft:stone"}

    Match smooth andesite by damage:
    {"id":"minecraft:stone","damage":6}

    Match certain damage values:
    {"id":"minecraft:wool","damage":[4,7,12,13]}

    Match colored beds with NBT:
    {"id":"bed","nbt":"{color:14}"}
    This will not check if the NBT matches perfectly,
    only if the specified NBT matches. Other tags are
    ignored.

    To specify strict NBT:
    {"id":"bed","nbt":"{color:14}","nbtStrict":True}
    This matches NBT exactly as specified.

    To specify no NBT:
    {"id":"minecraft:log","nbt":None}
    This matches NBT exactly as specified.

    To specify an item count:
    {"id":"minecraft:stick","count":5}

    To specify an item count range:
    {"id":"minecraft:stick","count":range(12,24+1)}

Action lists appear like so:
    Action lists are lists that contain actions, and
    are run from top to bottom. They look like this:
    [
    ["damage", "-", 7, "min", 2],
    ["nbt", "update", "{display:{Name:"§o§6Resurrected Pheonix"}}"],
    ]

    Valid actions include:
        id - change the item's ID to a new value

        count - alter an item stack's count
            = - set count
            + - increase count
            - - decrease count
            * - multiplies count (integer)
            / - divides count (integer)
            % - set count to ( oldCount % arg ) - always positive
            max - set count to max if max is exceeded
            min - set count to min if min is exceeded

        damage - alter an item's damage
            = - set damage
            + - increase damage
            - - decrease damage
            * - multiplies damage (integer)
            / - divides damage (integer)
            % - set damage to ( oldDamage % arg ) - always positive
            max - set damage to max if max is exceeded
            min - set damage to min if min is exceeded

        nbt - alter an item's nbt - only clear is implemented
            replace - replace an item's NBT data entirely
            update - update specified NBT without altering other NBT;
                existing lists and compounds will not have items removed;
                type conflicts will cause crashes to occur
            clear - remove all NBT from the item

        scoreboard - if on a player, in an ender chest, or in a shulker box
                    in one of those places, affect that player's scoreboard
                    (NYI)

                    @s - the player to target
                    @i - item's details

                    @i's scores:
                        count
                        damage
            accepted arguments:
                set, add, remove, reset, enable, operation
            example:
                "scoreboard", "operation", "@s", "iron_confiscated", "+=", "@i", "count"


        remove - delete the item

So, for example:
itemReplacements = [
    # Replace light gray wool with five cyan stained terracotta blocks
    [
        {"id":"wool","damage":8},
        [
            "id","stained_hardened_clay",
            "count","=",5,
            "damage","+",1,
        ]
    ],
    # Replace Pheonix Armor Ash (gunpowder) with Pheonix Armor
    [
        {
            "id":"minecraft:gunpowder",
            "damage":0,
            "count":5,
            "nbt":ur'''{display:{Name:"§6Pheonix Armor Ash",Lore:["§eLike a pheonix,","§ethis too shall rise"]}}''',
        },
        [
            "id","leather_helmet",
            "count","=","1",
            "nbt","replace",ur'''{ench:[{lvl:2s,id:1s},{lvl:1s,id:10s}],display:{color:16381908,Name:"§6Pheonix Cap",Lore:["§eLike a pheonix,","§ereborn from the ashes"]}}''',
        ]
    ],
    [
        {
            "id":"minecraft:gunpowder",
            "damage":0,
            "count":8,
            "nbt":ur'''{display:{Name:"§6Pheonix Armor Ash",Lore:["§eLike a pheonix,","§ethis too shall rise"]}}''',
        },
        [
            "id","leather_chestplate",
            "count","=","1",
            "nbt","replace",ur'''{ench:[{lvl:2s,id:1s},{lvl:1s,id:10s}],display:{color:16314131,Name:"§6Pheonix Tunic",Lore:["§eLike a pheonix,","§ereborn from the ashes"]}}''',
        ]
    ],
    [
        {
            "id":"minecraft:gunpowder",
            "damage":0,
            "count":7,
            "nbt":ur'''{display:{Name:"§6Pheonix Armor Ash",Lore:["§eLike a pheonix,","§ethis too shall rise"]}}''',
        },
        [
            "id","leather_leggings",
            "count","=","1",
            "nbt","replace",ur'''{ench:[{lvl:2s,id:1s},{lvl:1s,id:10s}],display:{color:16747314,Name:"§6Pheonix Pants",Lore:["§eLike a pheonix,","§ereborn from the ashes"]}}''',
        ]
    ],
    [
        {
            "id":"minecraft:gunpowder",
            "damage":0,
            "count":4,
            "nbt":ur'''{display:{Name:"§6Pheonix Armor Ash",Lore:["§eLike a pheonix,","§ethis too shall rise"]}}''',
        },
        [
            "id","leather_boots",
            "count","=","1",
            "nbt","replace",ur'''{ench:[{lvl:2s,id:1s},{lvl:1s,id:10s}],display:{color:12189696,Name:"§6Pheonix Boots",Lore:["§eLike a pheonix,","§ereborn from the ashes"]}}''',
        ]
    ],
]
"""

""" Items that aren't going in this list (for now at least)
    # Remove any gold ore that is present
    [
        {"id":"minecraft:gold_ore"},
        [
            "name","set",u"Decayed Item",
        ]
    ],
    # Remove any gold nuggets that are present
    [
        {"id":"minecraft:gold_nugget"},
        [
            "name","set",u"Decayed Item",
        ]
    ],
    # Remove any gold ingots that are present
    [
        {"id":"minecraft:gold_ingot"},
        [
            "name","set",u"Decayed Item",
        ]
    ],
    # Remove any gold blocks that are present
    [
        {"id":"minecraft:gold_block"},
        [
            "name","set",u"Decayed Item",
        ]
    ],
    # Remove any emerald ore that is present
    [
        {"id":"minecraft:emerald_ore"},
        [
            "name","set",u"Decayed Item",
        ]
    ],
    # Remove any emeralds that are present
    [
        {"id":"minecraft:emerald"},
        [
            "name","set",u"Decayed Item",
        ]
    ],
    # Remove any emerald blocks that are present
    [
        {"id":"minecraft:emerald_block"},
        [
            "name","set",u"Decayed Item",
        ]
    ],
"""

# Use this to replace nothing
itemReplacementsNone = item_replace.ReplaceItems()

# Use this to remove every item in the world
itemReplacementsRemoveAll = item_replace.ReplaceItems([],[
    # Remove all items
    [ { "any":None, }, ["remove"] ],
])

# Try "init" to show what this list does; you can even
# run this library as a script and skip the other stuff.
#itemReplacements = item_replace.ReplaceItems(["init","global count"],[
itemReplacements = item_replace.ReplaceItems([],[
    ############################################################################
    # Remove dungeon key items on weekly terrain resets:
    # (key items within dungeons, not keys to enter dungeons)
    ############################################################################

    # We really don't care what it is, just match the lore
    [
        {
            "nbt":ur'''{display:{Lore:["§e§lTaking this item outside of the dungeon","§e§lwill result in its destruction."]}}''',
        },
        ["remove"]
    ],

    ############################################################################
    # Update items that have changed:
    ############################################################################

    ####################################
    # skulls

    # G3po -> g3p0 (items only for now I'm afraid)
    [
        {
            "id":"minecraft:skull",
            "damage":3,
            "nbt":ur'''{SkullOwner:{Id:"8364a924-d1f2-4760-8db3-e4034fdcfe5b"}}''',
        },
        [
            "nbt", "replace", ur'''{SkullOwner:{Id:"bead93a4-fe1a-44d3-a02b-16b2f1f6f110",Properties:{textures:[{Signature:"ig9KhREcJcglVDIOtGxBbjQRmYN28g1s3J+g7WTe9AujWXIDoYyigB8NXWQw/dkWXX2oTHsRrxd8MNxX2TNPsvd+6C21J1p50LkMu1pZoyRSTDfQ6y0FmEnbg+TuRtfg5YZ6K5WBpRpTfivi51+NViIhbKTAm5KuACtMsCgGiKxCmDnt9S7uQSYd9W/tq1VV6w9ocw+34W1hujIt8ETN4GBAie98a7GBFlK5Mnmf1VEr8HeNqQkBpx29FR4CHTGNtWTdW7S1Q55jXcXVtM2tmp1JVshB5OHQ8s/U0KWkLOupYEfTIHqijKFXnTNfrPvdxXl/rAO93nwO75AUk7MVlPg4BTbjJn6Tece+G8fv3Xskn2lUeXrTiH+IDZYIrsPIKk+Nm6bg254aShIc2IIImwPR26BxLurT4iM+GNOJc7FuBcs12/0hZZSnEmapqlKdBhxegpCTUq5evJ8uR9Gp7Rs3l9qLueAlQ+5fiWTRWJDJ4yPwVDArK38Jmdc8yUPPimvZnYM3GxUtmjUyu8VRt3okbmGl4ttb//casujbFIoBDY3ngKsdQKMQyh8feSle78/+YyWLFfkWjpyZym+FRhNjLIuUgZMBxz9i72PUdOigvhJPGB+LChq81MtLVL5bt6cH8FoXCWiz9KJtOP5sfuERu/59qY4aVw1eYdhI570=",Value:"eyJ0aW1lc3RhbXAiOjE1MTAxMjU4NDA0MDIsInByb2ZpbGVJZCI6ImJlYWQ5M2E0ZmUxYTQ0ZDNhMDJiMTZiMmYxZjZmMTEwIiwicHJvZmlsZU5hbWUiOiJnM3AwIiwic2lnbmF0dXJlUmVxdWlyZWQiOnRydWUsInRleHR1cmVzIjp7IlNLSU4iOnsidXJsIjoiaHR0cDovL3RleHR1cmVzLm1pbmVjcmFmdC5uZXQvdGV4dHVyZS85OTExNzJhZjUzMmUxMmQ3MjRmNzEyZDA2N2YxYWFhNWQyZjMwMzUzZWZlNzViYTJkYjNhYjdmODliNWQxMSJ9fX0="}]},Name:"g3p0"}}'''
        ]
    ],

    [ # same, but by IGN instead
        {
            "id":"minecraft:skull",
            "damage":3,
            "nbt":ur'''{SkullOwner:{Name:"G3po"}}''',
        },
        [
            "nbt", "replace", ur'''{SkullOwner:{Id:"bead93a4-fe1a-44d3-a02b-16b2f1f6f110",Properties:{textures:[{Signature:"ig9KhREcJcglVDIOtGxBbjQRmYN28g1s3J+g7WTe9AujWXIDoYyigB8NXWQw/dkWXX2oTHsRrxd8MNxX2TNPsvd+6C21J1p50LkMu1pZoyRSTDfQ6y0FmEnbg+TuRtfg5YZ6K5WBpRpTfivi51+NViIhbKTAm5KuACtMsCgGiKxCmDnt9S7uQSYd9W/tq1VV6w9ocw+34W1hujIt8ETN4GBAie98a7GBFlK5Mnmf1VEr8HeNqQkBpx29FR4CHTGNtWTdW7S1Q55jXcXVtM2tmp1JVshB5OHQ8s/U0KWkLOupYEfTIHqijKFXnTNfrPvdxXl/rAO93nwO75AUk7MVlPg4BTbjJn6Tece+G8fv3Xskn2lUeXrTiH+IDZYIrsPIKk+Nm6bg254aShIc2IIImwPR26BxLurT4iM+GNOJc7FuBcs12/0hZZSnEmapqlKdBhxegpCTUq5evJ8uR9Gp7Rs3l9qLueAlQ+5fiWTRWJDJ4yPwVDArK38Jmdc8yUPPimvZnYM3GxUtmjUyu8VRt3okbmGl4ttb//casujbFIoBDY3ngKsdQKMQyh8feSle78/+YyWLFfkWjpyZym+FRhNjLIuUgZMBxz9i72PUdOigvhJPGB+LChq81MtLVL5bt6cH8FoXCWiz9KJtOP5sfuERu/59qY4aVw1eYdhI570=",Value:"eyJ0aW1lc3RhbXAiOjE1MTAxMjU4NDA0MDIsInByb2ZpbGVJZCI6ImJlYWQ5M2E0ZmUxYTQ0ZDNhMDJiMTZiMmYxZjZmMTEwIiwicHJvZmlsZU5hbWUiOiJnM3AwIiwic2lnbmF0dXJlUmVxdWlyZWQiOnRydWUsInRleHR1cmVzIjp7IlNLSU4iOnsidXJsIjoiaHR0cDovL3RleHR1cmVzLm1pbmVjcmFmdC5uZXQvdGV4dHVyZS85OTExNzJhZjUzMmUxMmQ3MjRmNzEyZDA2N2YxYWFhNWQyZjMwMzUzZWZlNzViYTJkYjNhYjdmODliNWQxMSJ9fX0="}]},Name:"g3p0"}}'''
        ]
    ],

    # Tlaxan Mask
    [
        {
            "id":"minecraft:skull",
            "damage":3,
            "nbt":ur'''{display:{Name:"§4§lTlaxan Mask"}}''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:1s,id:10s},{lvl:4s,id:4s},{lvl:2s,id:5s}],SkullOwner:{Id:"c659cdd4-e436-4977-a6a7-d5518ebecfbb",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvMWFlMzg1NWY5NTJjZDRhMDNjMTQ4YTk0NmUzZjgxMmE1OTU1YWQzNWNiY2I1MjYyN2VhNGFjZDQ3ZDMwODEifX19"}]}},display:{Lore:["§eKing's Valley : Rare"],Name:"§4§lTlaxan Mask"},AttributeModifiers:[{UUIDMost:32937979772523592L,UUIDLeast:12523234267159625L,Amount:0.15d,Slot:"head",AttributeName:"generic.attackDamage",Operation:1,Name:"generic.attackDamage"}]}'''
        ]
    ],

    ####################################
    # Helmets

    ################
    # leather

    # Brigand's Coif
    [
        {
            "id":"minecraft:leather_helmet",
            "name":u'''Brigand's Coif''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:3s,id:4s},{lvl:1s,id:34s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier IV"],color:8425600,Name:"§fBrigand's Coif"}}'''
        ]
    ],

    # Kismet's Blessing
    [
        {
            "id":"minecraft:leather_helmet",
            "name":u'''Kismet's Blessing''',
            "nbt":ur'''{AttributeModifiers:[{AttributeName:"generic.luck"}]}''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:3s,id:34s}],display:{Lore:["§bLeather Armor","§eKing's Valley : Rare","§6The luck has decayed into health"],color:65493,Name:"§b§lKismet's Blessing"},AttributeModifiers:[{UUIDMost:-6900745281224160306L,UUIDLeast:-4828553848378685989L,Amount:3.0d,Slot:"head",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"},{UUIDMost:1116995255491055008L,UUIDLeast:-6766107056483247837L,Amount:1.0d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
        ]
    ],

    # Iceborn Helmet
    [
        {
            "id":"minecraft:leather_helmet",
            "name":u'''Iceborn Helmet''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:3s,id:0s},{lvl:3s,id:34s},{lvl:1s,id:4s},{lvl:2s,id:5s}],display:{Lore:["§eKing's Valley : Rare"],color:9107455,Name:"§b§lIceborn Helmet"},AttributeModifiers:[{UUIDMost:46674431434570316L,UUIDLeast:29842133510151376L,Amount:-0.05d,Slot:"head",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:10509373368372805L,UUIDLeast:27250250553169692L,Amount:1,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
        ]
    ],

    # Plaguehide Cap
    [
        {
            "id":"minecraft:leather_helmet",
            "name":u'''Plaguehide Cap''',
        },
        [
            "nbt", "replace", ur'''{display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:675072,Name:"§aPlaguehide Cap"},AttributeModifiers:[{UUIDMost:22907356139724361L,UUIDLeast:55634361538278368L,Amount:2,Slot:"head",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"},{UUIDMost:50813337862916683L,UUIDLeast:38856196263924788L,Amount:0.05d,Slot:"head",AttributeName:"generic.attackDamage",Operation:1,Name:"generic.attackDamage"},{UUIDMost:22347000550566221L,UUIDLeast:68212466135762333L,Amount:1,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
        ]
    ],

    # Scout's Leathers
    [
        {
            "id":"minecraft:leather_helmet",
            "name":u'''Scout's Leathers''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:1s,id:34s},{lvl:2s,id:4s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier V"],color:10240,Name:"§aScout's Leathers"},AttributeModifiers:[{UUIDMost:692165,UUIDLeast:277777,Amount:0.03d,Slot:"head",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:692165,UUIDLeast:277777,Amount:1.0d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
        ]
    ],

    # Spellweave Hat
    [
        {
            "id":"minecraft:leather_helmet",
            "name":u'''Spellweave Hat''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:2s,id:34s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier III"],color:11555008,Name:"§fSpellweave Hat"},AttributeModifiers:[{UUIDMost:260399,UUIDLeast:803793,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
        ]
    ],

    # Topaz Cap
    [
        {
            "id":"minecraft:leather_helmet",
            "name":u'''Topaz Cap''',
            "nbt":ur'''{AttributeModifiers:[{AttributeName:"generic.luck"}]}''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:1s,id:34s}],display:{Lore:["§9Cloth Armor","* Unique Item *","§6The luck has decayed into health"],color:16776960,Name:"§6§lTopaz Cap"},AttributeModifiers:[{UUIDMost:-4372966254504623356L,UUIDLeast:-5757139819161180185L,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"Modifier"},{UUIDMost:-6920208193525167582L,UUIDLeast:-9012692505744652313L,Amount:2.0d,Slot:"head",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"}]}'''
        ]
    ],

    # Topaz Cap <- Amber Cap
    [
        {
            "id":"minecraft:leather_helmet",
            "name":u'''Amber Cap''',
            "nbt":ur'''{AttributeModifiers:[{AttributeName:"generic.luck"}]}''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:1s,id:34s}],display:{Lore:["§9Cloth Armor","* Unique Item *","§6The luck has decayed into health"],color:16776960,Name:"§6§lTopaz Cap"},AttributeModifiers:[{UUIDMost:-4372966254504623356L,UUIDLeast:-5757139819161180185L,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"Modifier"},{UUIDMost:-6920208193525167582L,UUIDLeast:-9012692505744652313L,Amount:2.0d,Slot:"head",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"}]}'''
        ]
    ],

    ################
    # gold

    # Jeweled Tiara
    [
        {
            "id":"minecraft:golden_helmet",
            "name":u'''Jeweled Tiara''',
            "nbt":ur'''{AttributeModifiers:[{AttributeName:"generic.luck"}]}''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:2s,id:34s}],display:{Lore:["* Unique Item *","§6The luck has decayed into health"],Name:"§d§lJeweled Tiara"},AttributeModifiers:[{UUIDMost:992743L,UUIDLeast:9295615L,Amount:1.0d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:2252054273775257919L,UUIDLeast:-6258579311022731853L,Amount:2.0d,Slot:"head",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"}]}'''
        ]
    ],

    ####################################
    # Chestplates

    ################
    # leather

    # Alchemist's Apron
    [
        {
            "id":"minecraft:leather_chestplate",
            "name":u'''Alchemist's Apron''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:2,id:1},{lvl:1,id:3}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier II"],color:16776960,Name:"§fAlchemist's Apron"},AttributeModifiers:[{UUIDMost:270399,UUIDLeast:903793,Amount:1.5d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
        ]
    ],

    # Basilisk Scales
    [
        {
            "id":"minecraft:leather_chestplate",
            "name":u'''Basilisk Scales''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:3s,id:34s}],display:{Lore:["§eKing's Valley : Rare"],color:54286,Name:"§2§lBasilisk Scales"},AttributeModifiers:[{UUIDMost:1217047145548364L,UUIDLeast:62197310443051283L,Amount:4,Slot:"chest",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"}]}'''
        ]
    ],

    # Brigand's Tunic
    [
        {
            "id":"minecraft:leather_chestplate",
            "name":u'''Brigand's Tunic''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:3s,id:4s},{lvl:1s,id:34s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier IV"],color:8425600,Name:"§fBrigand's Tunic"}}'''
        ]
    ],

    # Cultist's Robe
    [
        {
            "id":"minecraft:leather_chestplate",
            "name":u'''Cultist's Robe''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:1s,id:10s},{lvl:1s,id:70s}],display:{Lore:["§bLeather Armor","§eKing's Valley : Rare"],color:8857897,Name:"§d§lCultist's Robe"},AttributeModifiers:[{UUIDMost:42188985747894336L,UUIDLeast:58789894930970307L,Amount:3,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:26258638605899072L,UUIDLeast:65484620952030853L,Amount:0.1d,Slot:"chest",AttributeName:"generic.attackSpeed",Operation:1,Name:"generic.attackSpeed"}]}'''
        ]
    ],

    # Plaguehide Torso
    [
        {
            "id":"minecraft:leather_chestplate",
            "name":u'''Plaguehide Torso''',
        },
        [
            "nbt", "replace", ur'''{display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:675072,Name:"§aPlaguehide Torso"},AttributeModifiers:[{UUIDMost:71978911221471809L,UUIDLeast:25260044972271010L,Amount:2,Slot:"chest",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"},{UUIDMost:19117308396094024L,UUIDLeast:9968568939286539L,Amount:0.05d,Slot:"chest",AttributeName:"generic.attackDamage",Operation:1,Name:"generic.attackDamage"},{UUIDMost:8440217748974405L,UUIDLeast:3552643124966103L,Amount:3,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
        ]
    ],

    # Scout's Leathers
    [
        {
            "id":"minecraft:leather_chestplate",
            "name":u'''Scout's Leathers''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:1s,id:34s},{lvl:2s,id:4s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier V"],color:10240,Name:"§aScout's Leathers"},AttributeModifiers:[{UUIDMost:752165,UUIDLeast:297777,Amount:0.03d,Slot:"chest",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:752165,UUIDLeast:297777,Amount:3.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
        ]
    ],

    # Spellweave Tunic
    [
        {
            "id":"minecraft:leather_chestplate",
            "name":u'''Spellweave Tunic''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:2s,id:34s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier III"],color:11555008,Name:"§fSpellweave Tunic"},AttributeModifiers:[{UUIDMost:270399,UUIDLeast:903793,Amount:1.5d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
        ]
    ],

    # Voidguard
    [
        {
            "id":"minecraft:leather_chestplate",
            "name":u'''Voidguard''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:3s,id:0s},{lvl:2s,id:34s}],display:{Lore:["§bLeather Armor","§eKing's Valley : Rare"],color:3287104,Name:"§1§lVoidguard"},AttributeModifiers:[{UUIDMost:71061793700771916L,UUIDLeast:70921921889626742L,Amount:0.05d,Slot:"chest",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:5618170327124803L,UUIDLeast:67318597315435972L,Amount:3,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
        ]
    ],

    ####################################
    # Leggings

    ################
    # leather

    # Angelic Pants
    [
        {
            "id":"minecraft:leather_leggings",
            "name":u'''Angelic Pants''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:2s,id:34s}],display:{Lore:["§bLeather Armor","§eKing's Valley : Rare"],color:14277081,Name:"§6§lAngelic Pants"},AttributeModifiers:[{UUIDMost:2767629973749578L,UUIDLeast:26549136928073536L,Amount:5,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
        ]
    ],

    # Brigand's Trousers
    [
        {
            "id":"minecraft:leather_leggings",
            "name":u'''Brigand's Trousers''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:3s,id:4s},{lvl:1s,id:34s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier IV"],color:8425600,Name:"§fBrigand's Trousers"}}'''
        ]
    ],

    # Earthbound Pants
    [
        {
            "id":"minecraft:leather_leggings",
            "name":u'''Earthbound Pants''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:3s,id:34s}],display:{Lore:["§eKing's Valley : Rare"],color:11753010,Name:"§2§lEarthbound Pants"},AttributeModifiers:[{UUIDMost:47478565729543745L,UUIDLeast:55464327090482055L,Amount:3,Slot:"legs",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"},{UUIDMost:44980305394582344L,UUIDLeast:14485042704930583L,Amount:2,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
        ]
    ],

    # Plaguehide Pants
    [
        {
            "id":"minecraft:leather_leggings",
            "name":u'''Plaguehide Pants''',
        },
        [
            "nbt", "replace", ur'''{display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:675072,Name:"§aPlaguehide Pants"},AttributeModifiers:[{UUIDMost:7398196116790600L,UUIDLeast:33239325481073366L,Amount:2,Slot:"legs",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"},{UUIDMost:61910509039675723L,UUIDLeast:13746144420287990L,Amount:0.05d,Slot:"legs",AttributeName:"generic.attackDamage",Operation:1,Name:"generic.attackDamage"},{UUIDMost:14165244533123147L,UUIDLeast:22637248009267620L,Amount:2,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
        ]
    ],

    # Scout's Leathers
    [
        {
            "id":"minecraft:leather_leggings",
            "name":u'''Scout's Leathers''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:1s,id:34s},{lvl:2s,id:4s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier V"],color:10240,Name:"§aScout's Leathers"},AttributeModifiers:[{UUIDMost:732165,UUIDLeast:337777,Amount:0.03d,Slot:"legs",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:764261,UUIDLeast:337777,Amount:2.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
        ]
    ],

    # Spellweave Trousers
    [
        {
            "id":"minecraft:leather_leggings",
            "name":u'''Spellweave Trousers''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:2s,id:34s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier III"],color:11555008,Name:"§fSpellweave Trousers"},AttributeModifiers:[{UUIDMost:280399,UUIDLeast:1003793,Amount:1.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
        ]
    ],

    ################
    # chainmail

    # Ironscale Leggings
    [
        {
            "id":"minecraft:chainmail_leggings",
            "name":u'''Ironscale Leggings''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:2s,id:34s},{lvl:2s,id:3s}],display:{Lore:["§eKing's Valley : Rare"],Name:"§9§lIronscale Leggings"},AttributeModifiers:[{UUIDMost:46932015782064460L,UUIDLeast:34304226943201925L,Amount:4,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:42035034178315847L,UUIDLeast:15455365629951484L,Amount:2,Slot:"legs",AttributeName:"generic.armorToughness",Operation:0,Name:"generic.armorToughness"}]}'''
        ]
    ],

    ####################################
    # Boots

    ################
    # leather

    # Boots of Vitality
    [
        {
            "id":"minecraft:leather_boots",
            "name":u'''Boots of Vitality''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:5s,id:34s}],display:{Lore:["§bLeather Armor","§eKing's Valley : Rare"],color:4521728,Name:"§2§lBoots of Vitality"},AttributeModifiers:[{UUIDMost:47288061869184321L,UUIDLeast:31209886326295287L,Amount:2,Slot:"feet",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"},{UUIDMost:67642567772660032L,UUIDLeast:69671216077991960L,Amount:1,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
        ]
    ],

    # Brigand's Shoes
    [
        {
            "id":"minecraft:leather_boots",
            "name":u'''Brigand's Shoes''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:3s,id:4s},{lvl:1s,id:34s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier IV"],color:8425600,Name:"§fBrigand's Shoes"}}'''
        ]
    ],

    # Plaguehide Boots
    [
        {
            "id":"minecraft:leather_boots",
            "name":u'''Plaguehide Boots''',
        },
        [
            "nbt", "replace", ur'''{display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:675072,Name:"§aPlaguehide Boots"},AttributeModifiers:[{UUIDMost:19971159992297292L,UUIDLeast:11701631750427272L,Amount:2,Slot:"feet",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"},{UUIDMost:50620023180411213L,UUIDLeast:56580625667548148L,Amount:0.05d,Slot:"feet",AttributeName:"generic.attackDamage",Operation:1,Name:"generic.attackDamage"},{UUIDMost:61536614628787790L,UUIDLeast:12067686387522583L,Amount:1,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
        ]
    ],

    # Scout's Leathers
    [
        {
            "id":"minecraft:leather_boots",
            "name":u'''Scout's Leathers''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:1s,id:34s},{lvl:3s,id:2s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier V"],color:10240,Name:"§aScout's Leathers"},AttributeModifiers:[{UUIDMost:632165,UUIDLeast:237777,Amount:0.03d,Slot:"feet",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:632165,UUIDLeast:237777,Amount:1.0d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
        ]
    ],

    # Shadowborn Boots
    [
        {
            "id":"minecraft:leather_boots",
            "name":u'''Shadowborn Boots''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:2s,id:2s},{lvl:2s,id:34s}],display:{Lore:["§bLeather Armor","§eKing's Valley : Rare"],color:0,Name:"§1§lShadowborn Boots"},AttributeModifiers:[{UUIDMost:27244509153028163L,UUIDLeast:28582544481897959L,Amount:0.1d,Slot:"feet",AttributeName:"generic.attackDamage",Operation:1,Name:"generic.attackDamage"},{UUIDMost:28562665029432653L,UUIDLeast:46011597873607935L,Amount:1,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
        ]
    ],

    # Spellweave Shoes
    [
        {
            "id":"minecraft:leather_boots",
            "name":u'''Spellweave Shoes''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:2s,id:34s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier III"],color:11555008,Name:"§fSpellweave Shoes"},AttributeModifiers:[{UUIDMost:290399,UUIDLeast:1103793,Amount:0.75d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
        ]
    ],

    # Stormborn Boots
    [
        {
            "id":"minecraft:leather_boots",
            "name":u'''Stormborn Boots''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:2s,id:2s},{lvl:3s,id:34s},{lvl:2s,id:4s}],display:{Lore:["§eKing's Valley : Rare"],color:16775894,Name:"§3§lStormborn Boots"},AttributeModifiers:[{UUIDMost:8168110272590147L,UUIDLeast:66575962804257055L,Amount:0.05d,Slot:"feet",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:55068906034949703L,UUIDLeast:23695059647787143L,Amount:1,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
        ]
    ],

    ################
    # gold

    # King's Sabatons
    [
        {
            "id":"minecraft:golden_boots",
            "name":u'''King's Sabatons''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:3s,id:2s},{lvl:2s,id:4s},{lvl:1s,id:70s}],display:{Lore:["§6King's Valley : §lEPIC"],Name:"§b§l§nKing's Sabatons"},AttributeModifiers:[{UUIDMost:3501364431898363217L,UUIDLeast:-7168568964464722073L,Amount:0.15d,Slot:"feet",AttributeName:"generic.attackDamage",Operation:1,Name:"Modifier"},{UUIDMost:5805861576375026441L,UUIDLeast:-7198359331380377644L,Amount:2.0d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
        ]
    ],

    ####################################
    # Shield items

    # Arcane H0plon
    [
        {
            "id":"minecraft:shield",
            "name":u'''Arcane H0plon''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:1s,id:17s},{lvl:1s,id:34s},{lvl:1s,id:19s}],HideFlags:2,BlockEntityTag:{id:"Shield",Patterns:[{Pattern:"cbo",Color:10},{Pattern:"tts",Color:0},{Pattern:"bts",Color:0},{Pattern:"mr",Color:10},{Pattern:"sc",Color:0},{Pattern:"flo",Color:0}],Base:0},display:{Lore:["§8* Magic Wand *","§8King's Valley : §6Patron Made","§8St0mp them down with your magic","§8","§7When in main hand:","§7 2.0 Attack Speed","§7 4 Attack Damage"],Name:"§a§lArcane H0plon"},AttributeModifiers:[{UUIDMost:-2117986151759854833L,UUIDLeast:-5593014839057914980L,Amount:-2.0d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"Modifier"},{UUIDMost:-8899225606506198748L,UUIDLeast:-7900000780697794749L,Amount:3.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}'''
        ]
    ],

    # Keeper of the Jungle
    [
        {
            "id":"minecraft:shield",
            "name":u'''Keeper of the Jungle''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:2s,id:34s}],HideFlags:32,BlockEntityTag:{Patterns:[{Pattern:"ss",Color:2},{Pattern:"flo",Color:2},{Pattern:"bri",Color:2}],Base:3},display:{Lore:["§eKing's Valley : Rare"],Name:"§2§lKeeper of the Jungle"},AttributeModifiers:[{UUIDMost:9006655014927177L,UUIDLeast:4782782479127341L,Amount:1,Slot:"offhand",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
        ]
    ],

    # Spellready Buckler
    [
        {
            "id":"minecraft:shield",
            "name":u'''Spellready Buckler''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:1s,id:17s},{lvl:1s,id:19s}],HideFlags:2,BlockEntityTag:{id:"Shield",Patterns:[{Pattern:"tt",Color:0},{Pattern:"bt",Color:0},{Pattern:"flo",Color:0}],Base:10},display:{Lore:["§8King's Valley : Uncommon","§f","§7When in main hand:","§7 2 Attack Speed","§7 4 Attack Damage"],Name:"§aSpellready Buckler"},AttributeModifiers:[{UUIDMost:6962219233119978799L,UUIDLeast:-7099076830009706309L,Amount:3.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}'''
        ]
    ],

    # Spiked Buckler
    [
        {
            "id":"minecraft:shield",
            "name":u'''Spiked Buckler''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:1s,id:19s}],HideFlags:2,display:{Lore:["§8King's Valley : Tier IV","§8","§7When in main hand:","§7 2.0 Attack Speed","§7 4 Attack Damage"],Name:"§fSpiked Buckler"},AttributeModifiers:[{UUIDMost:6962219233119978799L,UUIDLeast:-7099076830009706309L,Amount:3.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}'''
        ]
    ],

    # Tlaxan Bulwark
    [
        {
            "id":"minecraft:shield",
            "name":u'''Tlaxan Bulwark''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:1s,id:34s}],HideFlags:32,BlockEntityTag:{Patterns:[{Pattern:"gru",Color:0},{Pattern:"cre",Color:0},{Pattern:"flo",Color:0},{Pattern:"moj",Color:0},{Pattern:"tts",Color:0},{Pattern:"bts",Color:0}],Base:2},display:{Lore:["§eKing's Valley : Rare"],Name:"§2§lTlaxan Bulwark"},AttributeModifiers:[{UUIDMost:8279654741628239L,UUIDLeast:50644245966137402L,Amount:2,Slot:"offhand",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"}]}'''
        ]
    ],

    ####################################
    # Sword items

    ################
    # stone

    # Angelic Sword
    [
        {
            "id":"minecraft:stone_sword",
            "name":u'''Angelic Sword''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:2s,id:17s},{lvl:5s,id:34s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§8","§7When in main hand:","§7 1.6 Attack Speed","§7 5 Attack Damage","§9 +1 Armor"],Name:"§6§lAngelic Sword"},AttributeModifiers:[{UUIDMost:13921849192281677L,UUIDLeast:29424957165321736L,Amount:4,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:14771070297205314L,UUIDLeast:58375339796730923L,Amount:1,Slot:"mainhand",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:69970127574793796L,UUIDLeast:64342718172429329L,Amount:-2.4d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
        ]
    ],

    # Ashheart Dagger
    [
        {
            "id":"minecraft:stone_sword",
            "name":u'''Ashheart Dagger''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:2s,id:34s},{lvl:4s,id:20s},{lvl:2s,id:22s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§f","§7When in main hand:","§7 1.6 Attack Speed","§7 5 Attack Damage","§9 +2 Max Health"],Name:"§8§lAshheart Dagger"},AttributeModifiers:[{UUIDMost:6203368885045579351L,UUIDLeast:-5502292298614332755L,Amount:2.0d,Slot:"mainhand",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"},{UUIDMost:1770737273186633355L,UUIDLeast:-7632807259696268977L,Amount:4,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"},{UUIDMost:-925442460826187303L,UUIDLeast:-5209611670608876751L,Amount:-2.4d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"Modifier"}]}'''
        ]
    ],

    # Earthbound Runeblade
    [
        {
            "id":"minecraft:stone_sword",
            "name":u'''Earthbound Runeblade''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:2s,id:34s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§6","§7When in main hand:","§7 1.6 Attack Speed","§7 6.5 Attack Damage","§9 +2 Armor"],Name:"§2§lEarthbound Runeblade"},AttributeModifiers:[{UUIDMost:67445053026503759L,UUIDLeast:20777435665232169L,Amount:4,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:57037229736289856L,UUIDLeast:7096337185411272L,Amount:2,Slot:"mainhand",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:29541336158339146L,UUIDLeast:50859522055085541L,Amount:-2.4d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
        ]
    ],

    # Frostbite
    [
        {
            "id":"minecraft:stone_sword",
            "name":u'''Frostbite''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:1s,id:34s}],HideFlags:1,display:{Lore:["§eKing's Valley : Rare"],Name:"§b§lFrostbite"},AttributeModifiers:[{UUIDMost:15904589298271559L,UUIDLeast:15892098128867088L,Amount:0.5d,Slot:"offhand",AttributeName:"generic.knockbackResistance",Operation:0,Name:"generic.knockbackResistance"},{UUIDMost:5519348956124230L,UUIDLeast:71245373947163486L,Amount:-0.1d,Slot:"offhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:26919752762697285L,UUIDLeast:9565821765701568L,Amount:0.3d,Slot:"offhand",AttributeName:"generic.attackDamage",Operation:1,Name:"generic.attackDamage"},{UUIDMost:70946014956938317L,UUIDLeast:59970257892856718L,Amount:3.0d,Slot:"offhand",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:59337689937702222L,UUIDLeast:43829378243568899L,Amount:-0.15d,Slot:"offhand",AttributeName:"generic.attackSpeed",Operation:1,Name:"Modifier"}]}'''
        ]
    ],

    # Iceborn Runeblade
    [
        {
            "id":"minecraft:stone_sword",
            "name":u'''Iceborn Runeblade''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:5s,id:16s},{lvl:1s,id:17s},{lvl:3s,id:34s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§7","§7When in main hand:"," §71.2 Attack Speed"," §78 Attack Damage"," §c-10% Speed"],Name:"§b§lIceborn Runeblade"},AttributeModifiers:[{UUIDMost:68342020398380105L,UUIDLeast:18376432692088500L,Amount:-0.1d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:20792108251577155L,UUIDLeast:44880469650724553L,Amount:4,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:49556179849667657L,UUIDLeast:15931220204059978L,Amount:-2.8d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
        ]
    ],

    # Poison Ivy
    [
        {
            "id":"minecraft:stone_sword",
            "name":u'''Poison Ivy''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:5s,id:16s},{lvl:2s,id:18s},{lvl:2s,id:34s},{lvl:2s,id:22s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§7","§7When in main hand:","§7 1.6 Attack Speed","§7 8 Attack Damage","§c -3 Armor"],Name:"§2§lPoison Ivy"},AttributeModifiers:[{UUIDMost:8412449719562827L,UUIDLeast:45136191579064328L,Amount:4,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:68056669774727247L,UUIDLeast:599809216906588L,Amount:-3,Slot:"mainhand",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:66546952320709442L,UUIDLeast:65370556181348047L,Amount:-2.4d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
        ]
    ],

    # Shadow Spike
    [
        {
            "id":"minecraft:stone_sword",
            "name":u'''Shadow Spike''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:4s,id:16s},{lvl:2s,id:34s},{lvl:1s,id:19s},{lvl:1s,id:20s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§8","§7When in main hand:","§7 1.6 Attack Speed","§7 7.5 Attack Damage","§c -3 Armor"],Name:"§4§lShadow Spike"},AttributeModifiers:[{UUIDMost:24272506551626816L,UUIDLeast:3188629144429256L,Amount:4,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:68081597460234561L,UUIDLeast:58960188647077945L,Amount:-3,Slot:"mainhand",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:40900807882193986L,UUIDLeast:13214525664118331L,Amount:-2.4d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
        ]
    ],

    # Stormborn Runeblade
    [
        {
            "id":"minecraft:stone_sword",
            "name":u'''Stormborn Runeblade''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:1s,id:34s},{lvl:2s,id:19s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§l","§7When in main hand:","§7 2 Attack Speed","§7 6.5 Attack Damage","§9 +10% Speed"],Name:"§3§lStormborn Runeblade"},AttributeModifiers:[{UUIDMost:44607095061251400L,UUIDLeast:17181972604100280L,Amount:0.1d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:32717593065480005L,UUIDLeast:13800488484714149L,Amount:4,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:18508304389737284L,UUIDLeast:65266891060907778L,Amount:-2,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
        ]
    ],

    # Telum Immoriel
    [
        {
            "id":"minecraft:stone_sword",
            "name":u'''Telum Immoriel''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:2s,id:34s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§fAnother toy for Fangride to play with.","§8","§7When in main hand:","§7 0.8 Attack Speed","§7 12 Attack Damage"],Name:"§6§lTelum Immoriel"},AttributeModifiers:[{UUIDMost:962659,UUIDLeast:90631,Amount:11,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:345591,UUIDLeast:876260,Amount:-3.2d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
        ]
    ],

    ################
    # gold

    # Geomantic Dagger
    [
        {
            "id":"minecraft:golden_sword",
            "name":u'''Geomantic Dagger''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:2s,id:17s},{lvl:5s,id:34s}],HideFlags:2,display:{Lore:["* Unique Item *","§8","§7When in main hand:","§7 1.6 Attack Speed","§7 5.5 Attack Damage","§9 +3 Armor"],Name:"§6§lGeomantic Dagger"},AttributeModifiers:[{UUIDMost:749364,UUIDLeast:739930,Amount:3,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:787340,UUIDLeast:172309,Amount:3,Slot:"mainhand",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:728374,UUIDLeast:661477,Amount:-2.4d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
        ]
    ],

    ####################################
    # Axe items

    ################
    # wood

    # Versatile Axe
    [
        {
            "id":"minecraft:wooden_axe",
            "name":u'''Versatile Axe''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:1s,id:16s},{lvl:1s,id:32s},{lvl:2s,id:34s}],display:{Lore:["§8King's Valley : Tier II"],Name:"§fVersatile Axe"}}'''
        ]
    ],

    ################
    # stone

    # Giant's Axe
    [
        {
            "id":"minecraft:stone_axe",
            "name":u'''Giant's Axe''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:2s,id:34s},{lvl:1s,id:19s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§7","§7When in main hand:","§7 0.6 Attack Speed","§7 15 Attack Damage"," §c-8% Speed"],Name:"§6§lGiant's Axe"},AttributeModifiers:[{UUIDMost:50069596546217285L,UUIDLeast:52124018636176511L,Amount:-0.08d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:16684340706050887L,UUIDLeast:61729139377545821L,Amount:14,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:20258808824438599L,UUIDLeast:52420949332344389L,Amount:-3.4d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
        ]
    ],

    # Mithril Cleaver
    [
        {
            "id":"minecraft:stone_axe",
            "name":u'''Mithril Cleaver''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:1s,id:16s},{lvl:2s,id:34s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§8","§7When in main hand:","§7 1.2 Attack Speed","§7 10 Attack Damage","§9 +12% Speed"],Name:"§3§lMithril Cleaver"},AttributeModifiers:[{UUIDMost:1317475486626126L,UUIDLeast:53226458093335048L,Amount:0.12d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:776403941688908L,UUIDLeast:11889093433774429L,Amount:-2.8d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"},{UUIDMost:30352855180673349L,UUIDLeast:58285458965911180L,Amount:8,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"}]}'''
        ]
    ],

    # Searing Wrath
    [
        {
            "id":"minecraft:stone_axe",
            "name":u'''Searing Wrath''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:5s,id:16s},{lvl:2s,id:34s},{lvl:2s,id:19s},{lvl:2s,id:20s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§8","§7When in main hand:","§7 0.8 Attack Speed","§7 12 Attack Damage","§c -3 Armor"],Name:"§4§lSearing Wrath"},AttributeModifiers:[{UUIDMost:797401,UUIDLeast:849310,Amount:8,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:205397,UUIDLeast:267554,Amount:-3,Slot:"mainhand",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:589373,UUIDLeast:600470,Amount:-3.2d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
        ]
    ],

    # Soulcrusher
    [
        {
            "id":"minecraft:stone_axe",
            "name":u'''Soulcrusher''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:6s,id:16s},{lvl:3s,id:34s}],RepairCost:1,HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§f","§7When in main hand:","§7 0.8 Attack Speed","§7 12.5 Attack Damage","§c -20% Speed"],Name:"§6§lSoulcrusher"},AttributeModifiers:[{UUIDMost:12446444898007617L,UUIDLeast:64791494739800248L,Amount:-0.2d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:19182804207771727L,UUIDLeast:44200783352792867L,Amount:8,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:1126358275258178L,UUIDLeast:50193448324688339L,Amount:-3.2d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
        ]
    ],

    ####################################
    # Hoe items

    ################
    # stone

    # Enderwrath
    [
        {
            "id":"minecraft:stone_hoe",
            "name":u'''Enderwrath''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:7s,id:16s},{lvl:5s,id:34s},{lvl:1s,id:19s},{lvl:2s,id:20s},{lvl:2s,id:21s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","","§7When in main hand:","§7 2 Attack Speed","§7 5 Attack Damage","§9 +15% Speed"],Name:"§5§lEnderwrath"},AttributeModifiers:[{UUIDMost:905415,UUIDLeast:796247,Amount:0.15d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:840609,UUIDLeast:663888,Amount:-2,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
        ]
    ],

    ####################################
    # Other items

    # Crystalized Water
    [
        {
            "id":"minecraft:packed_ice",
            "name":u'''Crystalized Water''',
        },
        [
            "nbt", "replace", ur'''{display:{Lore:["§fTurns into water when","§fplaced on a plot"],Name:"§b§lCrystalized Water"}}'''
        ]
    ],

    # Deathchill Staff
    [
        {
            "id":"minecraft:bone",
            "name":u'''Deathchill Staff''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:5s,id:16s},{lvl:2s,id:17s}],display:{Lore:["§8* Magic Wand *","§eKing's Valley : Rare"],Name:"§9§lDeathchill Staff"},AttributeModifiers:[{UUIDMost:9215418588072772L,UUIDLeast:29013032778824963L,Amount:0.3d,Slot:"mainhand",AttributeName:"generic.knockbackResistance",Operation:0,Name:"generic.knockbackResistance"},{UUIDMost:15405034991318852L,UUIDLeast:13833242679511430L,Amount:-0.1d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"}]}'''
        ]
    ],

    # Ender Chest
    [
        {
            "id":"minecraft:chest",
            "nbt":ur'''{BlockEntityTag:{CustomName:"Ender Chest",Lock:"lockedforever"},display:{Lore:["Place me and stand on top","Only works within a player or guild plot","Avoid placing next to a regular chest","Can only be placed once!"],Name:"Ender Chest"}}''',
        },
        [
            "id","minecraft:ender_chest",
            "nbt", "replace", ur'''{display:{Lore:["Can only be placed on a plot!"]}}''',
        ]
    ],

    # Hell's Fury
    [
        {
            "id":"minecraft:blaze_rod",
            "name":u'''Hell's Fury''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:2s,id:19s},{lvl:5s,id:20s}],display:{Lore:["§8* Magic Wand *","§eKing's Valley : Rare"],Name:"§5§lHell's Fury"},AttributeModifiers:[{UUIDMost:69502167760309831L,UUIDLeast:25155512585813018L,Amount:0.08d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"}]}'''
        ]
    ],

    # Ponderous Stone
    [
        {
            "id":"minecraft:clay_ball",
            "name":u'''Ponderous Stone''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:1s,id:51s}],HideFlags:1,display:{Lore:["§8King's Valley : Uncommon"],Name:"§6§lPonderous Stone"},AttributeModifiers:[{UUIDMost:-8784931189073293981L,UUIDLeast:-5336435319922077366L,Amount:1.0d,Slot:"offhand",AttributeName:"generic.knockbackResistance",Operation:0,Name:"Modifier"},{UUIDMost:-3784013313986900216L,UUIDLeast:-9150198598510123427L,Amount:-0.25d,Slot:"offhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"},{UUIDMost:-2473186416011490271L,UUIDLeast:-6797638087243652569L,Amount:-4.0d,Slot:"offhand",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"}]}'''
        ]
    ],

    # Tome of Arcane Horrors
    [
        {
            "id":"minecraft:book",
            "name":u'''Tome of Arcane Horrors''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:3s,id:20s},{lvl:3s,id:19s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§8","§7When in main hand:","§7 0.5 Attack Speed","§7 16 Attack Damage"],Name:"§5§lTome of Arcane Horrors"},AttributeModifiers:[{UUIDMost:495321,UUIDLeast:169768,Amount:15,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:564922,UUIDLeast:574772,Amount:-3.5d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
        ]
    ],

    ############################################################################
    # Event items:
    ############################################################################

    ############################################################################
    # 2017 Halloween Plague:

    # Plague Bearer's Boots
    [
        {
            "id":"minecraft:leather_boots",
            "name":u'''Plague Bearer's Boots''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:4s,id:34s}],display:{Lore:["§bLeather Armor","* Unique Event Item *","Halloween 2017"],color:675072,Name:"§2§lPlague Bearer's Boots"},AttributeModifiers:[{UUIDMost:-1640941516099861248L,UUIDLeast:-6326317583102562813L,Amount:-4.0d,Slot:"feet",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"},{UUIDMost:-2914598640505769820L,UUIDLeast:-7162398802439954937L,Amount:0.12d,Slot:"feet",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"},{UUIDMost:4035352220502543838L,UUIDLeast:-6384754459282382086L,Amount:1.0d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"Modifier"},{UUIDMost:1151211762335105703L,UUIDLeast:-8899502024825300851L,Amount:0.6d,Slot:"feet",AttributeName:"generic.knockbackResistance",Operation:0,Name:"Modifier"}]}'''
        ]
    ],

    # Pumpkin Spythe
    [
        {
            "id":"minecraft:stone_hoe",
            "name":u'''Pumpkin Scythe''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:8s,id:16s},{lvl:2s,id:17s},{lvl:2s,id:34s},{lvl:1s,id:18s}],display:{Lore:["* Unique Event Item *","Halloween 2017"],Name:"§2§lPumpkin Spythe"}}'''
        ]
    ],

    # Tribal Chisel
    [
        {
            "id":"minecraft:stone_pickaxe",
            "name":u'''Tribal Chisel''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:4s,id:32s},{lvl:1s,id:34s}],display:{Lore:["* Irreparable *","§eKing's Valley : Rare"],Name:"§2§lTribal Chisel"}}'''
        ]
    ],

    ############################################################################
    # Stuff that players shouldn't have had:
    ############################################################################

    # Iron:
    [ {"id":"minecraft:iron_ore"}, ["name","set",u"Decayed Item"] ],
    [ {"id":"minecraft:iron_nugget"}, ["name","set",u"Decayed Item"] ],
    [ {"id":"minecraft:iron_ingot"}, ["name","set",u"Decayed Item"] ],
    [ {"id":"minecraft:iron_block"}, ["name","set",u"Decayed Item"] ],
    [ {"id":"minecraft:iron_helmet"}, ["name","set",u"Decayed Item"] ],
    [ {"id":"minecraft:iron_chestplate"}, ["name","set",u"Decayed Item"] ],
    [ {"id":"minecraft:iron_leggings"}, ["name","set",u"Decayed Item"] ],
    [ {"id":"minecraft:iron_boots"}, ["name","set",u"Decayed Item"] ],
    [ {"id":"minecraft:iron_axe"}, ["name","set",u"Decayed Item"] ],
    [ {"id":"minecraft:iron_hoe"}, ["name","set",u"Decayed Item"] ],
    [ {"id":"minecraft:iron_pickaxe"}, ["name","set",u"Decayed Item"] ],
    [ {"id":"minecraft:iron_shovel"}, ["name","set",u"Decayed Item"] ],
    [ {"id":"minecraft:iron_sword"}, ["name","set",u"Decayed Item"] ],

    # Diamond:
    [ {"id":"minecraft:diamond_ore"}, ["name","set",u"Decayed Item"] ],
    [ {"id":"minecraft:diamond"}, ["name","set",u"Decayed Item"] ],
    [ {"id":"minecraft:diamond_block"}, ["name","set",u"Decayed Item"] ],
    [ {"id":"minecraft:diamond_helmet"}, ["name","set",u"Decayed Item"] ],
    [ {"id":"minecraft:diamond_chestplate"}, ["name","set",u"Decayed Item"] ],
    [ {"id":"minecraft:diamond_leggings"}, ["name","set",u"Decayed Item"] ],
    [ {"id":"minecraft:diamond_boots"}, ["name","set",u"Decayed Item"] ],
    [ {"id":"minecraft:diamond_axe"}, ["name","set",u"Decayed Item"] ],
    [ {"id":"minecraft:diamond_hoe"}, ["name","set",u"Decayed Item"] ],
    [ {"id":"minecraft:diamond_pickaxe"}, ["name","set",u"Decayed Item"] ],
    [ {"id":"minecraft:diamond_shovel"}, ["name","set",u"Decayed Item"] ],
    [ {"id":"minecraft:diamond_sword"}, ["name","set",u"Decayed Item"] ],

    # Other:
    [ {"id":"minecraft:anvil"}, ["name","set",u"Decayed Item"] ],
    [ {"id":"minecraft:hopper"}, ["name","set",u"Decayed Item"] ],
    [ {"id":"minecraft:hopper_minecart"}, ["name","set",u"Decayed Item"] ],
    [ {"id":"minecraft:beacon"}, ["name","set",u"Decayed Item"] ],
    [ {"id":"minecraft:nether_star"}, ["name","set",u"Decayed Item"] ],

    [ {"id":"minecraft:bucket"}, ["name","set",u"Decayed Item"] ],
    [ {"id":"minecraft:water_bucket"}, ["name","set",u"Decayed Item"] ],
    [ {"id":"minecraft:lava_bucket"}, ["name","set",u"Decayed Item"] ],
    [ {"id":"minecraft:milk_bucket"}, ["name","set",u"Decayed Item"] ],

    # Wither skeleton skulls - allowed now that wither spawns are canceled
    #[ {"id":"minecraft:skull", "damage":1}, ["name","set",u"Decayed Item"] ],

    ############################################################################
    # Other:

    # Luck items
    [
        {"nbt":ur'''{AttributeModifiers:[{AttributeName:"generic.luck"}]}'''},
        ["name","set",u"Decayed Item"]
    ],

    ############################################################################
    # Replace removed items with a notice:
    ############################################################################
    [
        {
            "name":u"Decayed Item",
        },
        [
            "id","minecraft:rotten_flesh",
            "damage","=",0,
            "nbt","replace",ur'''{ench:[{lvl:1s,id:71s}],display:{Name:"§cDecayed Item",Lore:["You had something","you shouldn't have,","didn't you?"]}}''',
        ]
    ],
])

