#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from lib_monumenta import item_replace
from item_replace_list_loot_tables import KingsValleyLootTables

blockReplacements = (
    "minecraft:iron_block",
    "minecraft:iron_ore",
    #"minecraft:hopper",
    (154,0), # Hopper
    (154,2), # Hopper
    (154,3), # Hopper
    (154,4), # Hopper
    (154,5), # Hopper
    (154,8), # Hopper
    (154,10), # Hopper
    (154,11), # Hopper
    (154,12), # Hopper
    (154,13), # Hopper
    "minecraft:diamond_block",
    "minecraft:diamond_ore",

    "minecraft:beacon",
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

    # Unlucky Topaz Cap
    [
        {
            "id":"minecraft:leather_helmet",
            "name":u'''Unlucky Topaz Cap''',
            "nbt":ur'''{display:{Lore:["§6The luck has decayed into health"]}}''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:1s,id:34s}],display:{Lore:["§9Cloth Armor","§8King's Valley : §5Unique","§6The luck has decayed into health"],color:16776960,Name:"§6§lFaded Topaz Cap"},AttributeModifiers:[{UUIDMost:-4372966254504623356L,UUIDLeast:-5757139819161180185L,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"Modifier"},{UUIDMost:-6920208193525167582L,UUIDLeast:-9012692505744652313L,Amount:2.0d,Slot:"head",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"}]}'''
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
            "name":u'''Unlucky Jeweled Tiara''',
            "nbt":ur'''{display:{Lore:["§6The luck has decayed into health"]}}''',
        },
        [
            "nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:2s,id:34s}],display:{Lore:["§8King's Valley : §5Unique","§6The luck has decayed into health"],Name:"§d§lFaded Jeweled Tiara"},AttributeModifiers:[{UUIDMost:992743L,UUIDLeast:9295615L,Amount:1.0d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:2252054273775257919L,UUIDLeast:-6258579311022731853L,Amount:2.0d,Slot:"head",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"}]}'''
        ]
    ],

    ####################################
    # Chestplates

    ####################################
    # Leggings

    ####################################
    # Boots

    ################
    # gold

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

    ####################################
    # Sword items

    ################
    # stone

    ################
    # gold

    ####################################
    # Axe items

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

    # Mobile Repair Station (need to update anvils that were placed and picked up anyways probably)
    [
        {
            "id":"minecraft:anvil",
        },
        [
            "nbt", "replace", ur'''{display:{Name:"§aNarsen Anvil"}}'''
        ]
    ],

    # Fix all loot table items on both build and play servers
    KingsValleyLootTables,
])

ArenaItems = item_replace.ReplaceItems([],[
    # Remove all overpowered / unobtainable arena items

    [
        {"any":[
            {'id':'minecraft:golden_axe','name':u'''Soul Devouring Axe'''},
            {'id':'minecraft:bow','name':u'''Bound Bow'''},
            {'id':'minecraft:dye','name':u'''Ice Charm'''},
            {'id':'minecraft:stone_shovel','name':u'''Advanced Booper'''},
            {'id':'minecraft:dye','name':u'''Fire Charm'''},
            {'id':'minecraft:stone_shovel','name':u'''Basic Booper'''},
            {'id':'minecraft:dye','name':u'''Supreme Speed Charm'''},
            {'id':'minecraft:dye','name':u'''Superior Blood Charm'''},
            {'id':'minecraft:sign','name':u'''Battlesign'''},
            {'id':'minecraft:leather_helmet','name':u'''Crown of the Forbidden Yew'''},
            {'id':'minecraft:leather_boots','name':u'''Galoshes of the Waves and Winds'''},
            {'id':'minecraft:golden_shovel','name':u'''Soul Devouring Booper'''},
            {'id':'minecraft:dye','name':u'''Hope Charm'''},
            {'id':'minecraft:leather_leggings','name':u'''Starshine Pants'''},
            {'id':'minecraft:leather_chestplate','name':u'''Uniform of the Arena Champion'''},
            {'id':'minecraft:stone_sword','name':u'''Advanced Stone Sword'''},
            {'id':'minecraft:sign','name':u'''Advanced Battlesign'''},
            {'id':'minecraft:stone_axe','name':u'''Advanced Stone Axe'''},
            {'id':'minecraft:stone_sword','name':u'''Broken Ancient Blade'''},
            {'id':'minecraft:golden_sword','name':u'''Soul Devouring Sword'''},
            {'id':'minecraft:dye','name':u'''Agility Charm'''},
        ]},
        [
            "id","minecraft:rotten_flesh",
            "damage","=",0,
            "nbt","replace",ur'''{ench:[{lvl:1s,id:71s}],display:{Name:"§cDecayed Item",Lore:["You had something","you shouldn't have,","didn't you?"]}}''',
        ]
    ],
])

KingsValleyDungeon = item_replace.ReplaceItems([],[
    # Remove all items
    ############################################################################
    # Stuff that players shouldn't have had:
    ############################################################################

    KingsValleyBuild,
    ArenaItems,

    # Remove Void Apple potions (there was a typo that caused an error last reset)
    [
        {
            "id":"minecraft:potion",
            "name":u'''Void Apple''',
        },
        [
            "id", "minecraft:potion",
            "nbt", "replace", ur'''{display:{Name:"§5Void Potion",Lore:["§4A potion infused with Void itself","§4Consuming it causes instant and unpreventable death"]},Potion:"minecraft:empty",CustomPotionEffects:[{Id:7b,Amplifier:9b,Duration:1s,Ambient:0b,ShowParticles:1b}]}''',
            "count", "=", 1
        ]
    ],

    [
        {"any":[
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

KingsValley = item_replace.ReplaceItems([],[
    # Remove all items
    ############################################################################
    # Stuff that players shouldn't have had:
    ############################################################################

    KingsValleyDungeon,

    [
        {"any":[
            # Dungeon keys
            {"nbt":ur'''{display:{Lore:["§e§lThis item will be deleted if attempted","§e§lto be taken out of dungeon!!!"]}}''',},
            {"nbt":ur'''{display:{Lore:["§e§lTaking this item outside of the dungeon","§e§lwill result in its destruction."]}}''',},
        ]},
        [
            "id","minecraft:rotten_flesh",
            "damage","=",0,
            "nbt","replace",ur'''{ench:[{lvl:1s,id:71s}],display:{Name:"§cDecayed Item",Lore:["You had something","you shouldn't have,","didn't you?"]}}''',
        ]
    ],
])


