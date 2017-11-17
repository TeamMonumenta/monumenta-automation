#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This is in development; suggestions are more than welcome!
# Looking for:
#   additional item matching pattens
#   additional actions
#   better notation
#   whatever else

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
            "remove",
        ]
    ],
    # Remove any gold nuggets that are present
    [
        {"id":"minecraft:gold_nugget"},
        [
            "remove",
        ]
    ],
    # Remove any gold ingots that are present
    [
        {"id":"minecraft:gold_ingot"},
        [
            "remove",
        ]
    ],
    # Remove any gold blocks that are present
    [
        {"id":"minecraft:gold_block"},
        [
            "remove",
        ]
    ],
    # Remove any emerald ore that is present
    [
        {"id":"minecraft:emerald_ore"},
        [
            "remove",
        ]
    ],
    # Remove any emeralds that are present
    [
        {"id":"minecraft:emerald"},
        [
            "remove",
        ]
    ],
    # Remove any emerald blocks that are present
    [
        {"id":"minecraft:emerald_block"},
        [
            "remove",
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
itemReplacements = item_replace.ReplaceItems(["global count"],[
    ############################################################################
    # Remove dungeon key items on weekly terrain resets:
    # (key items within dungeons, not keys to enter dungeons)
    ############################################################################

    # Simbelmynë
    [
        {
            "id":"minecraft:red_flower",
            "nbt":ur'''{ench:[{lvl:1s,id:34s}],display:{Lore:["§fSimbelmynë is a rare flower, and it is said to","§fonly grow on the burial mounds of Royalty...","§e§lTaking this item outside of the dungeon","§e§lwill result in its destruction.","* D4 Key 1 *"],Name:"§9§lSimbelmynë"}}''',
        },
        ["remove"]
    ],

    # Ancient Mortar
    [
        {
            "id":"minecraft:bowl",
            "nbt":ur'''{ench:[{lvl:1s,id:34s}],display:{Lore:["§fA Mortar perfect for mashing ingredients...","§e§lTaking this item outside of the dungeon","§e§lwill result in its destruction.","* D4 Key 2 *"],Name:"§9§lAncient Mortar"}}''',
        },
        ["remove"]
    ],

    # Aquanis Lily
    [
        {
            "id":"minecraft:red_flower",
            "nbt":ur'''{ench:[{lvl:1s,id:34s}],display:{Lore:["§fAn uncommon flower generally found near Hot Springs...","§e§lTaking this item outside of the dungeon","§e§lwill result in its destruction.","* D4 Key 3 *"],Name:"§9§lAquanis Lily"}}''',
        },
        ["remove"]
    ],

    ############################################################################
    # Update items that have changed:
    ############################################################################

    ####################################
    # Head items

    ################
    # leather

    # Kismet's Blessing
    [
        {
            "id":"minecraft:leather_helmet",
            "nbt":ur'''{display:{Name:"§b§lKismet's Blessing"},AttributeModifiers:[{AttributeName:"generic.luck"}]}''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:3s,id:34s}],display:{Lore:["§bLeather Armor","§eKing's Valley : Rare","§6The luck has decayed into health"],color:65493,Name:"§b§lKismet's Blessing"},AttributeModifiers:[{UUIDMost:-6900745281224160306L,UUIDLeast:-4828553848378685989L,Amount:3.0d,Slot:"head",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"},{UUIDMost:1116995255491055008L,UUIDLeast:-6766107056483247837L,Amount:1.0d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
        ]
    ],

    # Topaz Cap
    [
        {
            "id":"minecraft:leather_helmet",
            "nbt":ur'''{display:{Name:"§6§lTopaz Cap"},AttributeModifiers:[{AttributeName:"generic.luck"}]}''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:1s,id:34s}],display:{Lore:["§9Cloth Armor","* Unique Item *","§6The luck has decayed into health"],color:16776960,Name:"§6§lTopaz Cap"},AttributeModifiers:[{UUIDMost:-4372966254504623356L,UUIDLeast:-5757139819161180185L,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"Modifier"},{UUIDMost:-6920208193525167582L,UUIDLeast:-9012692505744652313L,Amount:2.0d,Slot:"head",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"}]}'''
        ]
    ],

    # Topaz Cap <- Amber Cap
    [
        {
            "id":"minecraft:leather_helmet",
            "nbt":ur'''{display:{Name:"§6§lAmber Cap"},AttributeModifiers:[{AttributeName:"generic.luck"}]}''',
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
            "nbt":ur'''{display:{Name:"§d§lJeweled Tiara"},AttributeModifiers:[{AttributeName:"generic.luck"}]}''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:2s,id:34s}],display:{Lore:["* Unique Item *","§6The luck has decayed into health"],Name:"§d§lJeweled Tiara"},AttributeModifiers:[{UUIDMost:992743L,UUIDLeast:9295615L,Amount:1.0d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:2252054273775257919L,UUIDLeast:-6258579311022731853L,Amount:2.0d,Slot:"head",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"}]}'''
        ]
    ],

    ################
    # skull

    # G3po -> g3p0 (items only for now I'm afraid)
    [
        {
            "id":"minecraft:skull",
            "damage":3,
            "nbt":ur'''{SkullOwner:{Name:"G3po"}}''',
        },
        [
            "nbt", "replace", ur'''{SkullOwner:{Id:"bead93a4-fe1a-44d3-a02b-16b2f1f6f110",Properties:{textures:[{Signature:"ig9KhREcJcglVDIOtGxBbjQRmYN28g1s3J+g7WTe9AujWXIDoYyigB8NXWQw/dkWXX2oTHsRrxd8MNxX2TNPsvd+6C21J1p50LkMu1pZoyRSTDfQ6y0FmEnbg+TuRtfg5YZ6K5WBpRpTfivi51+NViIhbKTAm5KuACtMsCgGiKxCmDnt9S7uQSYd9W/tq1VV6w9ocw+34W1hujIt8ETN4GBAie98a7GBFlK5Mnmf1VEr8HeNqQkBpx29FR4CHTGNtWTdW7S1Q55jXcXVtM2tmp1JVshB5OHQ8s/U0KWkLOupYEfTIHqijKFXnTNfrPvdxXl/rAO93nwO75AUk7MVlPg4BTbjJn6Tece+G8fv3Xskn2lUeXrTiH+IDZYIrsPIKk+Nm6bg254aShIc2IIImwPR26BxLurT4iM+GNOJc7FuBcs12/0hZZSnEmapqlKdBhxegpCTUq5evJ8uR9Gp7Rs3l9qLueAlQ+5fiWTRWJDJ4yPwVDArK38Jmdc8yUPPimvZnYM3GxUtmjUyu8VRt3okbmGl4ttb//casujbFIoBDY3ngKsdQKMQyh8feSle78/+YyWLFfkWjpyZym+FRhNjLIuUgZMBxz9i72PUdOigvhJPGB+LChq81MtLVL5bt6cH8FoXCWiz9KJtOP5sfuERu/59qY4aVw1eYdhI570=",Value:"eyJ0aW1lc3RhbXAiOjE1MTAxMjU4NDA0MDIsInByb2ZpbGVJZCI6ImJlYWQ5M2E0ZmUxYTQ0ZDNhMDJiMTZiMmYxZjZmMTEwIiwicHJvZmlsZU5hbWUiOiJnM3AwIiwic2lnbmF0dXJlUmVxdWlyZWQiOnRydWUsInRleHR1cmVzIjp7IlNLSU4iOnsidXJsIjoiaHR0cDovL3RleHR1cmVzLm1pbmVjcmFmdC5uZXQvdGV4dHVyZS85OTExNzJhZjUzMmUxMmQ3MjRmNzEyZDA2N2YxYWFhNWQyZjMwMzUzZWZlNzViYTJkYjNhYjdmODliNWQxMSJ9fX0="}]},Name:"g3p0"}}'''
        ]
    ],

    ####################################
    # Shield items

    # Arcane H0plon
    [
        {
            "id":"minecraft:shield",
            "nbt":ur'''{display:{Name:"§a§lArcane H0plon"}}''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:1s,id:17s},{lvl:1s,id:34s},{lvl:1s,id:19s}],HideFlags:2,BlockEntityTag:{id:"Shield",Patterns:[{Pattern:"cbo",Color:10},{Pattern:"tts",Color:0},{Pattern:"bts",Color:0},{Pattern:"mr",Color:10},{Pattern:"sc",Color:0},{Pattern:"flo",Color:0}],Base:0},display:{Lore:["§8* Magic Wand *","§8King's Valley : §6Patron Made","§8St0mp them down with your magic","§8","§7When in main hand:","§7 2.0 Attack Speed","§7 4 Attack Damage"],Name:"§a§lArcane H0plon"},AttributeModifiers:[{UUIDMost:-2117986151759854833L,UUIDLeast:-5593014839057914980L,Amount:-2.0d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"Modifier"},{UUIDMost:-8899225606506198748L,UUIDLeast:-7900000780697794749L,Amount:3.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}'''
        ]
    ],

    # Spellready Buckler
    [
        {
            "id":"minecraft:shield",
            "nbt":ur'''{display:{Name:"§aSpellready Buckler"}}''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:1s,id:17s},{lvl:1s,id:19s}],HideFlags:2,BlockEntityTag:{id:"Shield",Patterns:[{Pattern:"tt",Color:0},{Pattern:"bt",Color:0},{Pattern:"flo",Color:0}],Base:10},display:{Lore:["§8King's Valley : Uncommon","§f","§7When in main hand:","§7 2 Attack Speed","§7 4 Attack Damage"],Name:"§aSpellready Buckler"},AttributeModifiers:[{UUIDMost:6962219233119978799L,UUIDLeast:-7099076830009706309L,Amount:3.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}'''
        ]
    ],

    # Spiked Buckler
    [
        {
            "id":"minecraft:shield",
            "nbt":ur'''{display:{Name:"§fSpiked Buckler"}}''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:1s,id:19s}],HideFlags:2,display:{Lore:["§8King's Valley : Tier IV","§8","§7When in main hand:","§7 2.0 Attack Speed","§7 4 Attack Damage"],Name:"§fSpiked Buckler"},AttributeModifiers:[{UUIDMost:6962219233119978799L,UUIDLeast:-7099076830009706309L,Amount:3.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}'''
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
            "nbt":ur'''{display:{Name:"§6§lAngelic Sword"}}''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:2s,id:17s},{lvl:5s,id:34s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§8","§7When in main hand:","§7 1.6 Attack Speed","§7 5 Attack Damage","§9 +1 Armor"],Name:"§6§lAngelic Sword"},AttributeModifiers:[{UUIDMost:699422,UUIDLeast:76466,Amount:5,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:230886,UUIDLeast:58454,Amount:1,Slot:"mainhand",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:891666,UUIDLeast:498692,Amount:-2.4d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
        ]
    ],

    # Ashheart Dagger
    [
        {
            "id":"minecraft:stone_sword",
            "nbt":ur'''{display:{Name:"§8§lAshheart Dagger"}}''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:2s,id:34s},{lvl:4s,id:20s},{lvl:2s,id:22s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§f","§7When in main hand:","§7 1.6 Attack Speed","§7 5 Attack Damage","§9 +2 Max Health"],Name:"§8§lAshheart Dagger"},AttributeModifiers:[{UUIDMost:6203368885045579351L,UUIDLeast:-5502292298614332755L,Amount:2.0d,Slot:"mainhand",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"},{UUIDMost:1770737273186633355L,UUIDLeast:-7632807259696268977L,Amount:4,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"},{UUIDMost:-925442460826187303L,UUIDLeast:-5209611670608876751L,Amount:-2.4d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"Modifier"}]}'''
        ]
    ],

    # Earthbound Runeblade
    [
        {
            "id":"minecraft:stone_sword",
            "nbt":ur'''{display:{Name:"§2§lEarthbound Runeblade"}}''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:2s,id:34s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§6","§7When in main hand:","§7 1.6 Attack Speed","§7 6.5 Attack Damage","§9 +2 Armor"],Name:"§2§lEarthbound Runeblade"},AttributeModifiers:[{UUIDMost:789959,UUIDLeast:382503,Amount:4,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:217190,UUIDLeast:148481,Amount:2,Slot:"mainhand",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:905023,UUIDLeast:621272,Amount:-2.4d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
        ]
    ],

    # Iceborn Runeblade
    [
        {
            "id":"minecraft:stone_sword",
            "nbt":ur'''{display:{Name:"§b§lIceborn Runeblade"}}''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:5s,id:16s},{lvl:1s,id:17s},{lvl:3s,id:34s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§7","§7When in main hand:"," §71.2 Attack Speed"," §78 Attack Damage"," §c-10% Speed"],Name:"§b§lIceborn Runeblade"},AttributeModifiers:[{UUIDMost:3111,UUIDLeast:62113,Amount:-0.1d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:789959,UUIDLeast:382503,Amount:4,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:905023,UUIDLeast:621272,Amount:-2.8d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
        ]
    ],

    # Poison Ivy
    [
        {
            "id":"minecraft:stone_sword",
            "nbt":ur'''{display:{Name:"§2§lPoison Ivy"}}''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:5s,id:16s},{lvl:2s,id:18s},{lvl:2s,id:34s},{lvl:2s,id:22s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§7","§7When in main hand:","§7 1.6 Attack Speed","§7 8 Attack Damage","§c -3 Armor"],Name:"§2§lPoison Ivy"},AttributeModifiers:[{UUIDMost:689233,UUIDLeast:494460,Amount:4,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:176274,UUIDLeast:250428,Amount:-3,Slot:"mainhand",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:426734,UUIDLeast:486418,Amount:-2.4d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
        ]
    ],

    # Shadow Spike
    [
        {
            "id":"minecraft:stone_sword",
            "nbt":ur'''{display:{Name:"§4§lShadow Spike"}}''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:4s,id:16s},{lvl:2s,id:34s},{lvl:1s,id:19s},{lvl:1s,id:20s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§8","§7When in main hand:","§7 1.6 Attack Speed","§7 7.5 Attack Damage","§c -3 Armor"],Name:"§4§lShadow Spike"},AttributeModifiers:[{UUIDMost:473183,UUIDLeast:222857,Amount:4,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:223351,UUIDLeast:686496,Amount:-3,Slot:"mainhand",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:188583,UUIDLeast:588437,Amount:-2.4d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
        ]
    ],

    # Stormborn Runeblade
    [
        {
            "id":"minecraft:stone_sword",
            "nbt":ur'''{display:{Name:"§3§lStormborn Runeblade"}}''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:1s,id:34s},{lvl:2s,id:19s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§l","§7When in main hand:","§7 2 Attack Speed","§7 6.5 Attack Damage","§9 +10% Speed"],Name:"§3§lStormborn Runeblade"},AttributeModifiers:[{UUIDMost:3111,UUIDLeast:62113,Amount:0.1d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:789959,UUIDLeast:382503,Amount:4,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:905023,UUIDLeast:621272,Amount:-2,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
        ]
    ],

    # Telum Immoriel
    [
        {
            "id":"minecraft:stone_sword",
            "nbt":ur'''{display:{Name:"§6§lTelum Immoriel"}}''',
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
            "nbt":ur'''{display:{Name:"§6§lGeomantic Dagger"}}''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:2s,id:17s},{lvl:5s,id:34s}],HideFlags:2,display:{Lore:["* Unique Item *","§8","§7When in main hand:","§7 1.6 Attack Speed","§7 5.5 Attack Damage","§9 +3 Armor"],Name:"§6§lGeomantic Dagger"},AttributeModifiers:[{UUIDMost:749364,UUIDLeast:739930,Amount:3,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:787340,UUIDLeast:172309,Amount:3,Slot:"mainhand",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:728374,UUIDLeast:661477,Amount:-2.4d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
        ]
    ],

    ####################################
    # Axe items

    ################
    # stone

    # Giant's Axe
    [
        {
            "id":"minecraft:stone_axe",
            "nbt":ur'''{display:{Name:"§6§lGiant's Axe"}}''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:2s,id:34s},{lvl:1s,id:19s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§7","§7When in main hand:","§7 0.6 Attack Speed","§7 15 Attack Damage"," §c-8% Speed"],Name:"§6§lGiant's Axe"},AttributeModifiers:[{UUIDMost:3111,UUIDLeast:62113,Amount:-0.08d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:789959,UUIDLeast:382503,Amount:14,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:905023,UUIDLeast:621272,Amount:-3.4d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
        ]
    ],

    # Mithril Cleaver
    [
        {
            "id":"minecraft:stone_axe",
            "nbt":ur'''{display:{Name:"§3§lMithril Cleaver"}}''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:1s,id:16s},{lvl:2s,id:34s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§8","§7When in main hand:","§7 1.2 Attack Speed","§7 10 Attack Damage","§9 +12% Speed"],Name:"§3§lMithril Cleaver"},AttributeModifiers:[{UUIDMost:580907,UUIDLeast:714721,Amount:0.12d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:891666,UUIDLeast:498692,Amount:-2.8d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"},{UUIDMost:699422,UUIDLeast:16466,Amount:8,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"}]}'''
        ]
    ],

    # Searing Wrath
    [
        {
            "id":"minecraft:stone_axe",
            "nbt":ur'''{display:{Name:"§4§lSearing Wrath"}}''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:5s,id:16s},{lvl:2s,id:34s},{lvl:2s,id:19s},{lvl:2s,id:20s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§8","§7When in main hand:","§7 0.8 Attack Speed","§7 12 Attack Damage","§c -3 Armor"],Name:"§4§lSearing Wrath"},AttributeModifiers:[{UUIDMost:797401,UUIDLeast:849310,Amount:8,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:205397,UUIDLeast:267554,Amount:-3,Slot:"mainhand",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:589373,UUIDLeast:600470,Amount:-3.2d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
        ]
    ],

    # Soulcrusher
    [
        {
            "id":"minecraft:stone_axe",
            "nbt":ur'''{display:{Name:"§6§lSoulcrusher"}}''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:6s,id:16s},{lvl:3s,id:34s}],RepairCost:1,HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§f","§7When in main hand:","§7 0.8 Attack Speed","§7 12.5 Attack Damage","§c -20% Speed"],Name:"§6§lSoulcrusher"},AttributeModifiers:[{UUIDMost:591080,UUIDLeast:153443,Amount:-0.2d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:949514,UUIDLeast:324160,Amount:8,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:21574,UUIDLeast:844732,Amount:-3.2d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
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
            "nbt":ur'''{display:{Name:"§5§lEnderwrath"}}''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:7s,id:16s},{lvl:5s,id:34s},{lvl:1s,id:19s},{lvl:2s,id:20s},{lvl:2s,id:21s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","","§7When in main hand:","§7 2 Attack Speed","§7 5 Attack Damage","§9 +15% Speed"],Name:"§5§lEnderwrath"},AttributeModifiers:[{UUIDMost:905415,UUIDLeast:796247,Amount:0.15d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:840609,UUIDLeast:663888,Amount:-2,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
        ]
    ],

    ####################################
    # Other items

    # Ponderous Stone
    [
        {
            "id":"minecraft:clay_ball",
            "damage":0,
            "nbt":ur'''{display:{Name:"§6§lPonderous Stone"}}''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:1s,id:51s}],HideFlags:1,display:{Lore:["§8King's Valley : Uncommon"],Name:"§6§lPonderous Stone"},AttributeModifiers:[{UUIDMost:-8784931189073293981L,UUIDLeast:-5336435319922077366L,Amount:1.0d,Slot:"offhand",AttributeName:"generic.knockbackResistance",Operation:0,Name:"Modifier"},{UUIDMost:-3784013313986900216L,UUIDLeast:-9150198598510123427L,Amount:-0.25d,Slot:"offhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"},{UUIDMost:-2473186416011490271L,UUIDLeast:-6797638087243652569L,Amount:-4.0d,Slot:"offhand",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"}]}'''
        ]
    ],

    # Tome of Arcane Horrors
    [
        {
            "id":"minecraft:book",
            "nbt":ur'''{display:{Name:"§5§lTome of Arcane Horrors"}}''',
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
            "nbt":ur'''{display:{Name:"§2§lPlague Bearer's Boots"}}''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:4s,id:34s}],display:{Lore:["§bLeather Armor","* Unique Event Item *","Halloween 2017"],Name:"§2§lPlague Bearer's Boots"},AttributeModifiers:[{UUIDMost:-1640941516099861248L,UUIDLeast:-6326317583102562813L,Amount:-4.0d,Slot:"feet",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"},{UUIDMost:-2914598640505769820L,UUIDLeast:-7162398802439954937L,Amount:0.12d,Slot:"feet",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"},{UUIDMost:4035352220502543838L,UUIDLeast:-6384754459282382086L,Amount:1.0d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"Modifier"},{UUIDMost:1151211762335105703L,UUIDLeast:-8899502024825300851L,Amount:0.6d,Slot:"feet",AttributeName:"generic.knockbackResistance",Operation:0,Name:"Modifier"}]}'''
        ]
    ],

    # Pumpkin Spythe
    [
        {
            "id":"minecraft:stone_hoe",
            "nbt":ur'''{display:{Name:"§2§lPumpkin Scythe"}}''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:8s,id:16s},{lvl:2s,id:17s},{lvl:2s,id:34s},{lvl:1s,id:18s}],display:{Lore:["* Unique Event Item *","Halloween 2017"],Name:"§2§lPumpkin Spythe"}}'''
        ]
    ],

    # Tribal Chisel
    [
        {
            "id":"minecraft:stone_pickaxe",
            "nbt":ur'''{display:{Name:"§2§lTribal Chisel"}}''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:4s,id:32s},{lvl:1s,id:34s}],display:{Lore:["* Irreparable *","§eKing's Valley : Rare"],Name:"§2§lTribal Chisel"}}'''
        ]
    ],

    ############################################################################
    # Stuff that players shouldn't have had:
    ############################################################################

    # Iron:
    [ {"id":"minecraft:iron_ore"}, ["remove"] ],
    [ {"id":"minecraft:iron_nugget"}, ["remove"] ],
    [ {"id":"minecraft:iron_ingot"}, ["remove"] ],
    [ {"id":"minecraft:iron_block"}, ["remove"] ],
    [ {"id":"minecraft:iron_helmet"}, ["remove"] ],
    [ {"id":"minecraft:iron_chestplate"}, ["remove"] ],
    [ {"id":"minecraft:iron_leggings"}, ["remove"] ],
    [ {"id":"minecraft:iron_boots"}, ["remove"] ],
    [ {"id":"minecraft:iron_axe"}, ["remove"] ],
    [ {"id":"minecraft:iron_hoe"}, ["remove"] ],
    [ {"id":"minecraft:iron_pickaxe"}, ["remove"] ],
    [ {"id":"minecraft:iron_shovel"}, ["remove"] ],
    [ {"id":"minecraft:iron_sword"}, ["remove"] ],

    # Diamond:
    [ {"id":"minecraft:diamond_ore"}, ["remove"] ],
    [ {"id":"minecraft:diamond"}, ["remove"] ],
    [ {"id":"minecraft:diamond_block"}, ["remove"] ],
    [ {"id":"minecraft:diamond_helmet"}, ["remove"] ],
    [ {"id":"minecraft:diamond_chestplate"}, ["remove"] ],
    [ {"id":"minecraft:diamond_leggings"}, ["remove"] ],
    [ {"id":"minecraft:diamond_boots"}, ["remove"] ],
    [ {"id":"minecraft:diamond_axe"}, ["remove"] ],
    [ {"id":"minecraft:diamond_hoe"}, ["remove"] ],
    [ {"id":"minecraft:diamond_pickaxe"}, ["remove"] ],
    [ {"id":"minecraft:diamond_shovel"}, ["remove"] ],
    [ {"id":"minecraft:diamond_sword"}, ["remove"] ],

    # Other:
    [ {"id":"minecraft:anvil"}, ["remove"] ],
    [ {"id":"minecraft:hopper"}, ["remove"] ],
    [ {"id":"minecraft:hopper_minecart"}, ["remove"] ],
    [ {"id":"minecraft:beacon"}, ["remove"] ],
    [ {"id":"minecraft:nether_star"}, ["remove"] ],

    [ {"id":"minecraft:bucket"}, ["remove"] ],
    [ {"id":"minecraft:water_bucket"}, ["remove"] ],
    [ {"id":"minecraft:lava_bucket"}, ["remove"] ],
    [ {"id":"minecraft:milk_bucket"}, ["remove"] ],

    # Wither skeleton skulls - allowed now that wither spawns are canceled
    #[ {"id":"minecraft:skull", "damage":1}, ["remove"] ],

    ############################################################################
    # Other:

    # Luck items
    [
        {"nbt":ur'''{AttributeModifiers:[{AttributeName:"generic.luck"}]}'''},
        ["remove"]
    ],

    ############################################################################
    # Replace removed items with a notice:
    ############################################################################
    [
        {
            "count":0,
        },
        [
            "id","minecraft:rotten_flesh",
            "count","=",1,
            "damage","=",0,
            "nbt","replace",ur'''{ench:[{lvl:1s,id:71s}],display:{Name:"§cDecayed Item",Lore:["You had something","you shouldn't have,","didn't you?"]}}''',
        ]
    ],
])

