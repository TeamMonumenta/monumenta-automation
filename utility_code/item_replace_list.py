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

    ####################################
    # Boots

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
            "nbt", "replace", ur'''{display:{Name:"§aNarsen Anvil"}}'''
        ]
    ],

    ############################################################################
    # Event items:
    ############################################################################

    ########################################
    # 2017 Halloween Plague:
    [
            {
                    "id":"minecraft:pumpkin",
                    "name":u'''Plague Bearer's Head''',
            },
            [
                    "nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:2s,id:5s},{lvl:10s,id:7s}],display:{Lore:["* Unique Event Item *","§2Halloween 2017"],Name:"§2§lPlague Bearer's Head"},AttributeModifiers:[{UUIDMost:288139l,UUIDLeast:25869l,Amount:-4d,Slot:"head",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"},{UUIDMost:737075l,UUIDLeast:622094l,Amount:1d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
            ]
    ],
    [
            {
                    "id":"minecraft:leather_chestplate",
                    "name":u'''Plague Bearer's Tunic''',
            },
            [
                    "nbt", "replace", ur'''{ench:[{lvl:4s,id:34s},{lvl:2s,id:3s}],display:{Lore:["§bLeather Armor","* Unique Event Item *","§2Halloween 2017"],color:8252160,Name:"§2§lPlague Bearer's Tunic"},AttributeModifiers:[{UUIDMost:-2864634781938629890l,UUIDLeast:-4853618912971704644l,Amount:3.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"},{UUIDMost:6775590779125908083l,UUIDLeast:-4834564711714845847l,Amount:0.35d,Slot:"chest",AttributeName:"generic.attackDamage",Operation:1,Name:"Modifier"},{UUIDMost:-3135663898049493017l,UUIDLeast:-5638735112125366694l,Amount:-4.0d,Slot:"chest",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"}]}'''
            ]
    ],
    [
            {
                    "id":"minecraft:leather_leggings",
                    "name":u'''Plague Bearer's Soiled Trousers''',
            },
            [
                    "nbt", "replace", ur'''{ench:[{lvl:2s,id:4s},{lvl:4s,id:34s}],display:{Lore:["§bLeather Armor","* Unique Event Item *","§2Halloween 2017"],color:13070852,Name:"§2§lPlague Bearer's Soiled Trousers"},AttributeModifiers:[{UUIDMost:1644902849549979627l,UUIDLeast:-6334696171190229818l,Amount:-4.0d,Slot:"legs",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"},{UUIDMost:2348010706303338053l,UUIDLeast:-6411594601520431420l,Amount:0.4d,Slot:"legs",AttributeName:"generic.attackSpeed",Operation:1,Name:"Modifier"},{UUIDMost:2225618996942884003l,UUIDLeast:-6129754164345949662l,Amount:2.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
            ]
    ],
    [
            {
                    "id":"minecraft:leather_boots",
                    "name":u'''Plague Bearer's Boots''',
            },
            [
                    "nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:4s,id:34s}],display:{Lore:["§bLeather Armor","* Unique Event Item *","§2Halloween 2017"],color:675072,Name:"§2§lPlague Bearer's Boots"},AttributeModifiers:[{UUIDMost:-1640941516099861248l,UUIDLeast:-6326317583102562813l,Amount:-4.0d,Slot:"feet",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"},{UUIDMost:-2914598640505769820l,UUIDLeast:-7162398802439954937l,Amount:0.12d,Slot:"feet",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"},{UUIDMost:4035352220502543838l,UUIDLeast:-6384754459282382086l,Amount:1.0d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"Modifier"},{UUIDMost:1151211762335105703l,UUIDLeast:-8899502024825300851l,Amount:0.6d,Slot:"feet",AttributeName:"generic.knockbackResistance",Operation:0,Name:"Modifier"}]}'''
            ]
    ],
    [
            {
                    "id":"minecraft:stone_hoe",
                    "name":u'''Pumpkin Spythe''',
            },
            [
                    "nbt", "replace", ur'''{ench:[{lvl:4s,id:16s},{lvl:2s,id:17s},{lvl:1s,id:18s},{lvl:3s,id:34s}],HideFlags:2,display:{Lore:["* Event Item *","§2Halloween 2017","§7","§7When in main hand:","§7 2 Attack Speed","§7 5.5 Attack Damage"],Name:"§2§lPumpkin Spythe"},AttributeModifiers:[{UUIDMost:6433490404641818817l,UUIDLeast:-8593178968434576189l,Amount:-2.0d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"Modifier"},{UUIDMost:3288944914052894654l,UUIDLeast:-5839775210248136997l,Amount:2.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}'''
            ]
    ],

    ########################################
    # 2017 Winter with Nivalis
    [
            {
                    "id":"minecraft:stick",
                    "name":u'''Prehensile Stick''',
            },
            [
                    "nbt", "replace", ur'''{ench:[{lvl:1s,id:51s}],HideFlags:1,display:{Lore:["* Event Item *","§9Winter 2017"],Name:"§6§lPrehensile Stick"}}'''
            ]
    ],
    [
            {
                    "id":"minecraft:coal",
                    "name":u'''Animated Coal''',
            },
            [
                    "nbt", "replace", ur'''{ench:[{lvl:1s,id:51s}],HideFlags:1,display:{Lore:["* Event Item *","§9Winter 2017"],Name:"§6§lAnimated Coal"}}'''
            ]
    ],
    [
            {
                    "id":"minecraft:carrot",
                    "name":u'''Olfactory Carrot''',
            },
            [
                    "nbt", "replace", ur'''{ench:[{lvl:1s,id:51s}],HideFlags:1,display:{Lore:["* Event Item *","§9Winter 2017"],Name:"§6§lOlfactory Carrot"}}'''
            ]
    ],
    [
            {
                    "id":"minecraft:snowball",
                    "name":u'''Everlasting Snow''',
            },
            [
                    "nbt", "replace", ur'''{ench:[{lvl:1s,id:51s}],HideFlags:1,display:{Lore:["* Event Item *","§9Winter 2017"],Name:"§6§lEverlasting Snow"}}'''
            ]
    ],
    [
            {
                    "id":"minecraft:leather_boots",
                    "name":u'''Snegovik Boots''',
            },
            [
                    "nbt", "replace", ur'''{ench:[{lvl:3s,id:0s},{lvl:4s,id:34s},{lvl:3s,id:2s}],display:{Lore:["§bLeather Armor","* Unique Event Item *","§9Winter 2017"],color:16383998,Name:"§9§lSnegovik Boots"},AttributeModifiers:[{UUIDMost:-5978105780621458805l,UUIDLeast:-8700344539718369213l,Amount:-0.25d,Slot:"feet",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"},{UUIDMost:3187109101431704271l,UUIDLeast:-6731613508922955815l,Amount:0.25d,Slot:"feet",AttributeName:"generic.knockbackResistance",Operation:0,Name:"Modifier"},{UUIDMost:-287479839887832961l,UUIDLeast:-4828764350438371832l,Amount:3.0d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
            ]
    ],
    [
            {
                    "id":"minecraft:leather_leggings",
                    "name":u'''Snegovik Greaves''',
            },
            [
                    "nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:3s,id:1s},{lvl:4s,id:34s}],display:{Lore:["§bLeather Armor","* Unique Event Item *","§9Winter 2017"],color:16383998,Name:"§9§lSnegovik Greaves"},AttributeModifiers:[{UUIDMost:-6341046020925667044l,UUIDLeast:-6457955953871678720l,Amount:-0.25d,Slot:"legs",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"},{UUIDMost:-7631271266390487651l,UUIDLeast:-7348755354350928744l,Amount:0.25d,Slot:"legs",AttributeName:"generic.knockbackResistance",Operation:0,Name:"Modifier"},{UUIDMost:-5436134608155098067l,UUIDLeast:-8350436639202330222l,Amount:3.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
            ]
    ],
    [
            {
                    "id":"minecraft:leather_chestplate",
                    "name":u'''Snegovik Cuirass''',
            },
            [
                    "nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:4s,id:34s},{lvl:3s,id:3s}],display:{Lore:["§bLeather Armor","* Unique Event Item *","§9Winter 2017"],color:16383998,Name:"§9§lSnegovik Cuirass"},AttributeModifiers:[{UUIDMost:-4287348896770604697l,UUIDLeast:-6859886905264673929l,Amount:-0.25d,Slot:"chest",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"},{UUIDMost:4129461185357693856l,UUIDLeast:-6077279240674996299l,Amount:0.25d,Slot:"chest",AttributeName:"generic.knockbackResistance",Operation:0,Name:"Modifier"},{UUIDMost:179710638715454523l,UUIDLeast:-5179097180515627721l,Amount:3.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
            ]
    ],
    [
            {
                    "id":"minecraft:leather_helmet",
                    "name":u'''Snegovik Helm''',
            },
            [
                    "nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:3s,id:4s},{lvl:4s,id:34s}],display:{Lore:["§bLeather Armor","* Unique Event Item *","§9Winter 2017"],color:16383998,Name:"§9§lSnegovik Helm"},AttributeModifiers:[{UUIDMost:-7121844074788926637l,UUIDLeast:-7125048144545132342l,Amount:-0.25d,Slot:"head",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"},{UUIDMost:-3760667262727925946l,UUIDLeast:-6993157342267378714l,Amount:0.25d,Slot:"head",AttributeName:"generic.knockbackResistance",Operation:0,Name:"Modifier"},{UUIDMost:-1237906264110972440l,UUIDLeast:-5382957932985185645l,Amount:3.0d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
            ]
    ],
    [
            {
                    "id":"minecraft:wooden_sword",
                    "name":u'''Rod of the Onodrim''',
            },
            [
                    "nbt", "replace", ur'''{ench:[{lvl:3s,id:32s},{lvl:1s,id:70s}],display:{Lore:["* Unique Event Item *","§9Winter 2017"],Name:"§9§lRod of the Onodrim"},AttributeModifiers:[{UUIDMost:2512866317016583848l,UUIDLeast:-8695731667534274344l,Amount:-0.4d,Slot:"offhand",AttributeName:"generic.attackSpeed",Operation:1,Name:"Modifier"},{UUIDMost:2801717605841978307l,UUIDLeast:-4821070712928009977l,Amount:-0.2d,Slot:"offhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"},{UUIDMost:5435604988355234856l,UUIDLeast:-7278734017423574959l,Amount:0.6d,Slot:"offhand",AttributeName:"generic.attackDamage",Operation:1,Name:"Modifier"}]}'''
            ]
    ],
    [
            {
                    "id":"minecraft:leather_chestplate",
                    "name":u'''Ebola Shirt''',
            },
            [
                    "nbt", "replace", ur'''{Unbreakable:1,display:{Lore:["§bLeather Armor","* Unique Event Item *","* Stylish *","§cWe are small, but our legend spreads like Ebola.","§4Uganda 2018"],color:16711680,Name:"§c§lEbola Shirt"}}'''
            ]
    ],

    # Fix all loot table items on both build and play servers
    KingsValleyLootTables,
])

KingsValleyDungeon = item_replace.ReplaceItems([],[
    # Remove all items
    ############################################################################
    # Stuff that players shouldn't have had:
    ############################################################################

    KingsValleyBuild,

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


