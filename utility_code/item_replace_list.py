#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lib_monumenta import item_replace
from item_replace_list_loot_tables import KingsValleyLootTables

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

    # We had a happy fix in lib_monumenta/common.py

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
    {"id":"bed","nbt":"strict{color:14}"}
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
#KingsValleyBuild = item_replace.ReplaceItems(["init","global count"],[
KingsValleyBuild = item_replace.ReplaceItems([],[
    ############################################################################
    # Oh dear, these shouldn't be in the build world...

    # You see nothing!
    [{"id":"minecraft:elytra",},["remove",]],

    [
        {"any":[
            {"name":u"How the fuck did you get back here?"},
            {"name":u"Well, you've fucked up"},
            {"name":u"The Great Penis"},
        ]},
        [
            "print","check here",
            "location"
        ]
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
            "print", "G3po -> g3p0 still needed",
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
            "print", "G3po -> g3p0 by IGN still needed",
            "nbt", "replace", ur'''{SkullOwner:{Id:"bead93a4-fe1a-44d3-a02b-16b2f1f6f110",Properties:{textures:[{Signature:"ig9KhREcJcglVDIOtGxBbjQRmYN28g1s3J+g7WTe9AujWXIDoYyigB8NXWQw/dkWXX2oTHsRrxd8MNxX2TNPsvd+6C21J1p50LkMu1pZoyRSTDfQ6y0FmEnbg+TuRtfg5YZ6K5WBpRpTfivi51+NViIhbKTAm5KuACtMsCgGiKxCmDnt9S7uQSYd9W/tq1VV6w9ocw+34W1hujIt8ETN4GBAie98a7GBFlK5Mnmf1VEr8HeNqQkBpx29FR4CHTGNtWTdW7S1Q55jXcXVtM2tmp1JVshB5OHQ8s/U0KWkLOupYEfTIHqijKFXnTNfrPvdxXl/rAO93nwO75AUk7MVlPg4BTbjJn6Tece+G8fv3Xskn2lUeXrTiH+IDZYIrsPIKk+Nm6bg254aShIc2IIImwPR26BxLurT4iM+GNOJc7FuBcs12/0hZZSnEmapqlKdBhxegpCTUq5evJ8uR9Gp7Rs3l9qLueAlQ+5fiWTRWJDJ4yPwVDArK38Jmdc8yUPPimvZnYM3GxUtmjUyu8VRt3okbmGl4ttb//casujbFIoBDY3ngKsdQKMQyh8feSle78/+YyWLFfkWjpyZym+FRhNjLIuUgZMBxz9i72PUdOigvhJPGB+LChq81MtLVL5bt6cH8FoXCWiz9KJtOP5sfuERu/59qY4aVw1eYdhI570=",Value:"eyJ0aW1lc3RhbXAiOjE1MTAxMjU4NDA0MDIsInByb2ZpbGVJZCI6ImJlYWQ5M2E0ZmUxYTQ0ZDNhMDJiMTZiMmYxZjZmMTEwIiwicHJvZmlsZU5hbWUiOiJnM3AwIiwic2lnbmF0dXJlUmVxdWlyZWQiOnRydWUsInRleHR1cmVzIjp7IlNLSU4iOnsidXJsIjoiaHR0cDovL3RleHR1cmVzLm1pbmVjcmFmdC5uZXQvdGV4dHVyZS85OTExNzJhZjUzMmUxMmQ3MjRmNzEyZDA2N2YxYWFhNWQyZjMwMzUzZWZlNzViYTJkYjNhYjdmODliNWQxMSJ9fX0="}]},Name:"g3p0"}}'''
        ]
    ],

    [ # Wrangler's Disguise
        {
            "id":"minecraft:skull",
            "damage":4,
            "name":u'''Wrangler's Disguise''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:2s,id:3s}],display:{Lore:["§8King's Valley : Tier IV"],Name:"§fWrangler's Disguise"},AttributeModifiers:[{UUIDMost:7228445873160669085L,UUIDLeast:-4704669888939619595L,Amount:2.0d,Slot:"head",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"}]}'''
        ]
    ],

    ####################################
    # Helmets

    ################
    # leather

    # Topaz Cap
    [
        {
            "id":"minecraft:leather_helmet",
            "name":u'''Topaz Cap''',
            "nbt":ur'''{AttributeModifiers:[{AttributeName:"generic.luck"}]}''',
        },
        [
            "print", "Lucky Topaz Cap still needed",
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
            "print", "Lucky Amber Cap still needed",
            "nbt", "replace", ur'''{ench:[{lvl:1s,id:34s}],display:{Lore:["§9Cloth Armor","* Unique Item *","§6The luck has decayed into health"],color:16776960,Name:"§6§lTopaz Cap"},AttributeModifiers:[{UUIDMost:-4372966254504623356L,UUIDLeast:-5757139819161180185L,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"Modifier"},{UUIDMost:-6920208193525167582L,UUIDLeast:-9012692505744652313L,Amount:2.0d,Slot:"head",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"}]}'''
        ]
    ],

    # Fedora
    [
        {
            "id":"minecraft:leather_helmet",
            "name":u'''Fedora''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:1s,id:70s}],HideFlags:35,display:{Lore:["§8King's Valley : Uncommon","§8Nice guys finish last...","§8M' Lady... ( ͡° ͜ʖ ͡°)","§7","§7When on head:","§9 +10% Coolness","§9 +25% Neckbeard","§c -10% Speed"],color:0,Name:"§8§lFedora"},AttributeModifiers:[{UUIDMost:5639012561410475226L,UUIDLeast:-7926585099207054512L,Amount:-20.0d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"Modifier"},{UUIDMost:2236652158341825249L,UUIDLeast:-6720137306445331011L,Amount:-0.1d,Slot:"head",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"},{UUIDMost:-7196473041523228034L,UUIDLeast:-7435759153258789866L,Amount:-50.0d,Slot:"head",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}'''
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
            "print", "Lucky Jeweled Tiara still needed",
            "nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:2s,id:34s}],display:{Lore:["* Unique Item *","§6The luck has decayed into health"],Name:"§d§lJeweled Tiara"},AttributeModifiers:[{UUIDMost:992743L,UUIDLeast:9295615L,Amount:1.0d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:2252054273775257919L,UUIDLeast:-6258579311022731853L,Amount:2.0d,Slot:"head",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"}]}'''
        ]
    ],

    ####################################
    # Chestplates

    ####################################
    # Leggings

    # Steelscale Leggings
    [
        {
            "id":"minecraft:chainmail_leggings",
            "name":u'''Steelscale Leggings''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:1s,id:4s},{lvl:2s,id:34s}],display:{Lore:["§eKing's Valley : §lEnhanced Rare"],Name:"§9§lSteelscale Leggings"},AttributeModifiers:[{UUIDMost:-2327598243755965121l,UUIDLeast:-7295240752476775997l,Amount:4.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"Modifier"},{UUIDMost:-1961662591581338036l,UUIDLeast:-7158710234379227327l,Amount:3.0d,Slot:"legs",AttributeName:"generic.armorToughness",Operation:0,Name:"Modifier"}]}'''
        ]
    ],

    ####################################
    # Boots

    # Boots of Vigor
    [
        {
            "id":"minecraft:leather_boots",
            "name":u'''Boots of Vigor''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:5s,id:34s}],display:{Lore:["§bLeather Armor","§eKing's Valley : §lEnhanced Rare"],color:4521728,Name:"§2§lBoots of Vigor"},AttributeModifiers:[{UUIDMost:4275084912512485263l,UUIDLeast:-5640926957255110802l,Amount:3.0d,Slot:"feet",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"},{UUIDMost:2935233553126737342l,UUIDLeast:-8942942613933079309l,Amount:1.0d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
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

    # Spellready Buckler
    [
        {
            "id":"minecraft:shield",
            "name":u'''Spellready Buckler''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:1s,id:17s},{lvl:1s,id:19s}],HideFlags:2,BlockEntityTag:{id:"Shield",Patterns:[{Pattern:"tt",Color:0},{Pattern:"bt",Color:0},{Pattern:"flo",Color:0}],Base:10},display:{Lore:["§8King's Valley : Uncommon","§f","§7When in main hand:","§7 2 Attack Speed","§7 4 Attack Damage"],Name:"§aSpellready Buckler"},AttributeModifiers:[{UUIDMost:-211798659854833L,UUIDLeast:-559301457914980L,Amount:-2.0d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"Modifier"}, {UUIDMost:6962219233119978799L,UUIDLeast:-7099076830009706309L,Amount:3.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}'''
        ]
    ],

    # Sanctifying Guard
    [
        {
            "id":"minecraft:shield",
            "name":u'''Sanctifying Guard''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:2s,id:34s},{lvl:2s,id:19s}],HideFlags:32,BlockEntityTag:{Base:10,Patterns:[{Color:15,Pattern:"bo"},{Color:15,Pattern:"mr"},{Color:6,Pattern:"flo"},{Color:7,Pattern:"tts"},{Color:7,Pattern:"bts"}]},display:{Lore:["* Mainhand Regeneration *","§8King's Valley : §6Patron Made","§8Made with Sage wisdom"],Name:"§a§lSanctifying Guard"},AttributeModifiers:[{UUIDMost:1287381409643709352l,UUIDLeast:-7880782928783714372l,Amount:4.0d,Slot:"mainhand",AttributeName:"generic.armor",Operation:0,Name:"Modifier"},{UUIDMost:4065928328244447087l,UUIDLeast:-8906003175754769214l,Amount:2.0d,Slot:"mainhand",AttributeName:"generic.armorToughness",Operation:0,Name:"Modifier"},{UUIDMost:2452519509611594002l,UUIDLeast:-9038091112074494442l,Amount:-0.1d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}'''
        ]
    ],

    ####################################
    # Sword items

    ################
    # stone

    # Rosethorn Blade
    [
        {
            "id":"minecraft:stone_sword",
            "name":u'''Rosethorn Blade''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:6s,id:16s},{lvl:2s,id:18s},{lvl:3s,id:34s},{lvl:1s,id:7s},{lvl:2s,id:22s}],HideFlags:2,display:{Lore:["§eKing's Valley : §lEnhanced Rare","§7","§7When in main hand:","§7 1.6 Attack Speed","§7 8.5 Attack Damge","§c -1 Armor"],Name:"§2§lRosethorn Blade"},AttributeModifiers:[{UUIDMost:-4030115003770974645l,UUIDLeast:-8624436179929330760l,Amount:-2.4d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"Modifier"},{UUIDMost:-6097606032756880319l,UUIDLeast:-6935384686738106924l,Amount:4.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"},{UUIDMost:4535675750486917643l,UUIDLeast:-6071361771643014893l,Amount:-1.0d,Slot:"mainhand",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
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

    # The Annihilator
    [
        {
            "id":"minecraft:stone_axe",
            "name":u'''The Annihilator''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:4s,id:16s},{lvl:4s,id:34s},{lvl:3s,id:19s},{lvl:2s,id:20s}],display:{Lore:["§eKing's Valley : §lEnhanced Rare"],Name:"§3§lThe Annihilator"}}'''
        ]
    ],

    ####################################
    # Hoe items
    
    # Pumpkin Spythe
    [
        {
            "id":"minecraft:stone_hoe",
            "name":u'''Pumpkin Spythe''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:8s,id:16s},{lvl:2s,id:17s},{lvl:2s,id:34s},{lvl:1s,id:18s}],display:{Lore:["* Unique Event Item *","Halloween 2017"],Name:"§2§lPumpkin Spythe"}}'''
        ]
    ],

    ####################################
    # Potions

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

    # Sharpened Holy Feather
    [
        {
            "id":"minecraft:feather",
            "name":u'''Sharpened Holy Feather''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:7s,id:16s}],display:{Lore:["§8* Magic Wand *","§8King's Valley : §6Patron Made","§8A feather from the holy Rayven"],Name:"§f§lSharpened Holy Feather"},AttributeModifiers:[{UUIDMost:8148793466415236557L,UUIDLeast:-5911602864794772103L,Amount:0.07d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}'''
        ]
    ],

    # Mobile Repair Station (need to update anvils that were placed and picked up anyways probably)
    [
        {
            "id":"minecraft:anvil",
        },
        [
            "nbt", "replace", ur'''{display:{Name:"§aMobile Repair Station"}}'''
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

    # Fix all loot table items on both build and play servers
    KingsValleyLootTables,
])

KingsValley = item_replace.ReplaceItems([],[
    # Remove all items
    ############################################################################
    # Stuff that players shouldn't have had:
    ############################################################################

    KingsValleyBuild,

    [
        {"any":[
            # Dungeon keys
            {"nbt":ur'''{display:{Lore:["§e§lThis item will be deleted if attempted","§e§lto be taken out of dungeon!!!"]}}''',},
            {"nbt":ur'''{display:{Lore:["§e§lTaking this item outside of the dungeon","§e§lwill result in its destruction."]}}''',},

            # Iron:
            {"id":"minecraft:iron_ore"},
            {"id":"minecraft:iron_nugget"},
            {"id":"minecraft:iron_ingot"},
            {"id":"minecraft:iron_block"},
            {"id":"minecraft:iron_helmet"},
            {"id":"minecraft:iron_chestplate"},
            {"id":"minecraft:iron_leggings"},
            {"id":"minecraft:iron_boots"},
            {"id":"minecraft:iron_axe"},
            {"id":"minecraft:iron_hoe"},
            {"id":"minecraft:iron_pickaxe"},
            {"id":"minecraft:iron_shovel"},
            {"id":"minecraft:iron_sword"},

            # Diamond:
            {"id":"minecraft:diamond_ore"},
            {"id":"minecraft:diamond"},
            {"id":"minecraft:diamond_block"},
            {"id":"minecraft:diamond_helmet"},
            {"id":"minecraft:diamond_chestplate"},
            {"id":"minecraft:diamond_leggings"},
            {"id":"minecraft:diamond_boots"},
            {"id":"minecraft:diamond_axe"},
            {"id":"minecraft:diamond_hoe"},
            {"id":"minecraft:diamond_pickaxe"},
            {"id":"minecraft:diamond_shovel"},
            {"id":"minecraft:diamond_sword"},

            # Other
            {"id":"minecraft:hopper"},
            {"id":"minecraft:hopper_minecart"},
            {"id":"minecraft:beacon"},
            {"id":"minecraft:nether_star"},

            # Buckets
            {"id":"minecraft:bucket"},
            {"id":"minecraft:water_bucket"},
            {"id":"minecraft:lava_bucket"},
            {"id":"minecraft:milk_bucket"},

            # Luck items
            {"nbt":ur'''{AttributeModifiers:[{AttributeName:"generic.luck"}]}'''},
        ]},
        [
            "id","minecraft:rotten_flesh",
            "damage","=",0,
            "nbt","replace",ur'''{ench:[{lvl:1s,id:71s}],display:{Name:"§cDecayed Item",Lore:["You had something","you shouldn't have,","didn't you?"]}}''',
        ]
    ],
])


