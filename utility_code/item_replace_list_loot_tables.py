#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lib_monumenta import item_replace

KingsValleyLootTables = item_replace.ReplaceItems([],[
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Turtle Flippers''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:8s},{lvl:2s,id:3s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier II"],color:36912,Name:"§fTurtle Flippers"},AttributeModifiers:[{UUIDMost:290399l,UUIDLeast:1103793l,Amount:0.75d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Turtle Pants''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:8s},{lvl:2s,id:3s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier II"],color:36912,Name:"§fTurtle Pants"},AttributeModifiers:[{UUIDMost:280399l,UUIDLeast:1003793l,Amount:1.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Turtle Vest''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:6s},{lvl:2s,id:3s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier II"],color:36912,Name:"§fTurtle Vest"},AttributeModifiers:[{UUIDMost:270399l,UUIDLeast:903793l,Amount:1.5d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Turtle Helm''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:5s},{lvl:2s,id:3s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier II"],color:36912,Name:"§fTurtle Helm"},AttributeModifiers:[{UUIDMost:260399l,UUIDLeast:803793l,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:fishing_rod",
			"name":u'''Angler's Rod''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:62s},{lvl:2s,id:34s}],display:{Lore:["§8King's Valley : Tier III"],Name:"§fAngler's Rod"}}'''
		]
	],
	[
		{
			"id":"minecraft:lever",
			"name":u'''Damaged Hilt''',
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["§8Carved with elegant flowers"],Name:"§fDamaged Hilt"}}'''
		]
	],
	[
		{
			"id":"minecraft:fish",
			"name":u'''Magic Fish''',
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["§dGills","§8King's Valley : Uncommon","§7Gives water breathing to you and nearby","§7allies when held in your offhand."],Name:"§b§lMagic Fish"}}'''
		]
	],
	[
		{
			"id":"minecraft:shield",
			"name":u'''Turtle Shield''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:34s}],BlockEntityTag:{Base:6,Patterns:[{Color:2,Pattern:"bri"}]},display:{Lore:["§8King's Valley : Uncommon"],Name:"§b§lTurtle Shield"},AttributeModifiers:[{UUIDMost:-2699735906624845463l,UUIDLeast:-6308071593572563623l,Amount:-0.05d,Slot:"offhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"},{UUIDMost:-407094390218668203l,UUIDLeast:-9013419339908919017l,Amount:0.4d,Slot:"offhand",AttributeName:"generic.knockbackResistance",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:bow",
			"name":u'''Oncoming Tide''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:49s},{lvl:1s,id:70s}],display:{Lore:["§8King's Valley : Uncommon"],Name:"§b§lOncoming Tide"},AttributeModifiers:[{UUIDMost:1004903320127294777l,UUIDLeast:-6735527447459109365l,Amount:0.07d,Slot:"offhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:cooked_fish",
			"name":u'''Regal Salmon''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:51s}],display:{Lore:["§d* Quest Item *","#Q16I02"],Name:"§6§lRegal Salmon"}}'''
		]
	],
	[
		{
			"id":"minecraft:rabbit",
			"name":u'''Zombie Meat''',
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fZombie Meat"}}'''
		]
	],
	[
		{
			"id":"minecraft:cooked_rabbit",
			"name":u'''Cooked Zombie Meat''',
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fCooked Zombie Meat"}}'''
		]
	],
	[
		{
			"id":"minecraft:splash_potion",
			"name":u'''Extinguisher''',
		},
		[
			"nbt", "replace", ur'''{CustomPotionColor:16756736,CustomPotionEffects:[{Ambient:1b,ShowParticles:1b,Duration:200,Id:12b,Amplifier:0b}],Potion:"minecraft:empty",display:{Name:"§fExtinguisher"}}'''
		]
	],
	[
		{
			"id":"minecraft:splash_potion",
			"name":u'''Antidote''',
		},
		[
			"nbt", "replace", ur'''{CustomPotionColor:4239424,CustomPotionEffects:[{Ambient:1b,ShowParticles:1b,Duration:40,Id:10b,Amplifier:2b},{Ambient:1b,ShowParticles:1b,Duration:30,Id:19b,Amplifier:2b}],Potion:"minecraft:empty",display:{Lore:["§7Removes Poison II and lower"],Name:"§fAntidote"}}'''
		]
	],
	[
		{
			"id":"minecraft:quartz",
			"name":u'''Bone Shard''',
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["§8Broken, but could be rebuilt"],Name:"§fBone Shard"}}'''
		]
	],
	[
		{
			"id":"minecraft:cooked_beef",
			"name":u'''Cooked Horse Meat''',
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fCooked Horse Meat"}}'''
		]
	],
	[
		{
			"id":"minecraft:beef",
			"name":u'''Horse Meat''',
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fHorse Meat"}}'''
		]
	],
	[
		{
			"id":"minecraft:splash_potion",
			"name":u'''Antidote''',
		},
		[
			"nbt", "replace", ur'''{CustomPotionColor:4239424,CustomPotionEffects:[{Ambient:1b,ShowParticles:1b,Duration:40,Id:10b,Amplifier:2b},{Ambient:1b,ShowParticles:1b,Duration:30,Id:19b,Amplifier:2b}],Potion:"minecraft:empty",display:{Lore:["§7Removes Poison II and lower"],Name:"§fAntidote"}}'''
		]
	],
	[
		{
			"id":"minecraft:splash_potion",
			"name":u'''Potion of Salvation''',
		},
		[
			"nbt", "replace", ur'''{CustomPotionColor:13947904,CustomPotionEffects:[{Ambient:0b,ShowParticles:0b,Duration:600,Id:22b,Amplifier:1b},{Ambient:1b,ShowParticles:1b,Duration:100,Id:10b,Amplifier:1b}],Potion:"minecraft:awkward",display:{Name:"§fPotion of Salvation"}}'''
		]
	],
	[
		{
			"id":"minecraft:sugar",
			"name":u'''Pulsating Dust''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:5s,id:48s}],display:{Lore:["Distilled power from strong items"],Name:"§b§lPulsating Dust"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"name":u'''Living Thorn''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:16s},{lvl:1s,id:18s},{lvl:1s,id:70s}],display:{Lore:["§8King's Valley : Tier III"],Name:"§fLiving Thorn"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"name":u'''Crusader's Sword''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:17s},{lvl:1s,id:34s}],display:{Lore:["§8King's Valley : Tier III"],Name:"§fCrusader's Sword"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"name":u'''Light Scimitar''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:1s,id:34s},{lvl:3s,id:22s}],display:{Lore:["§8King's Valley : Tier III"],Name:"§fLight Scimitar"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"name":u'''Flamewreath Splinter''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:34s},{lvl:2s,id:19s},{lvl:3s,id:20s}],display:{Lore:["§8King's Valley : Tier III"],Name:"§fFlamewreath Splinter"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"name":u'''Thief's Dagger''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:1s,id:34s},{lvl:4s,id:21s}],display:{Lore:["§8King's Valley : Tier III"],Name:"§fThief's Dagger"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"name":u'''Brigand's Rapier''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:20s},{lvl:2s,id:21s}],display:{Lore:["§8King's Valley : Tier III"],Name:"§fBrigand's Rapier"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"name":u'''Honed Claymore''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:34s},{lvl:1s,id:22s}],display:{Lore:["§8King's Valley : Tier III"],Name:"§fHoned Claymore"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"name":u'''Ritual Knife''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:17s},{lvl:1s,id:34s}],display:{Lore:["§8King's Valley : Tier III"],Name:"§fRitual Knife"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"name":u'''Trusty Dagger''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:16s},{lvl:1s,id:18s},{lvl:1s,id:34s}],display:{Lore:["§8King's Valley : Tier III"],Name:"§fTrusty Dagger"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"name":u'''Scoundrel's Rapier''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:51s}],HideFlags:1,display:{Lore:["§8King's Valley : Tier III"],Name:"§fScoundrel's Rapier"},AttributeModifiers:[{UUIDMost:157078l,UUIDLeast:786990l,Amount:2d,Slot:"offhand",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"name":u'''Poisoned Shank''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:51s}],HideFlags:1,display:{Lore:["§8King's Valley : Tier III"],Name:"§fPoisoned Shank"},AttributeModifiers:[{UUIDMost:298381l,UUIDLeast:495523l,Amount:0.15d,Slot:"offhand",AttributeName:"generic.attackDamage",Operation:1,Name:"generic.attackDamage"}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_axe",
			"name":u'''Meteor Hammer''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:4s,id:16s},{lvl:1s,id:34s},{lvl:2s,id:20s}],display:{Lore:["§8King's Valley : Tier III"],Name:"§fMeteor Hammer"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_axe",
			"name":u'''Tempered Mace''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:2s,id:34s},{lvl:2s,id:19s}],display:{Lore:["§8King's Valley : Tier III"],Name:"§fTempered Mace"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"name":u'''Woodsman's Axe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:32s}],display:{Lore:["§8King's Valley : Tier III"],Name:"§fWoodsman's Axe"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"name":u'''Heavy Warhammer''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:16s},{lvl:1s,id:34s},{lvl:1s,id:19s}],display:{Lore:["§8King's Valley : Tier III"],Name:"§fHeavy Warhammer"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"name":u'''Jagged Cleaver''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:1s,id:34s}],display:{Lore:["§8King's Valley : Tier III"],Name:"§fJagged Cleaver"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"name":u'''Inferno Axe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:32s},{lvl:2s,id:20s}],display:{Lore:["§8King's Valley : Tier III"],Name:"§fInferno Axe"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_pickaxe",
			"name":u'''Sapper's Tool''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:32s},{lvl:2s,id:34s},{lvl:1s,id:19s}],display:{Lore:["§8King's Valley : Tier III"],Name:"§fSapper's Tool"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_pickaxe",
			"name":u'''Masterwork Pickaxe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:32s},{lvl:1s,id:34s}],display:{Lore:["§8King's Valley : Tier III"],Name:"§fMasterwork Pickaxe"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_pickaxe",
			"name":u'''Runic Pickaxe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:34s},{lvl:2s,id:35s}],display:{Lore:["§8King's Valley : Tier III"],Name:"§fRunic Pickaxe"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_pickaxe",
			"name":u'''Resiliant Pickaxe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:5s,id:34s}],display:{Lore:["§8King's Valley : Tier III"],Name:"§fResiliant Pickaxe"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_shovel",
			"name":u'''Arrowmeld''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:34s},{lvl:3s,id:35s}],display:{Lore:["§8King's Valley : Tier III"],Name:"§fArrowmeld"}}'''
		]
	],
	[
		{
			"id":"minecraft:shield",
			"name":u'''Hardened Shield''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:34s}],display:{Lore:["§8King's Valley : Tier III"],Name:"§fHardened Shield"}}'''
		]
	],
	[
		{
			"id":"minecraft:bow",
			"name":u'''Hawk's Talon''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:48s}],display:{Lore:["§8King's Valley : Tier III"],Name:"§fHawk's Talon"}}'''
		]
	],
	[
		{
			"id":"minecraft:bow",
			"name":u'''Crossbow''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:49s},{lvl:2s,id:34s}],display:{Lore:["§8King's Valley : Tier III"],Name:"§fCrossbow"}}'''
		]
	],
	[
		{
			"id":"minecraft:bow",
			"name":u'''Searing Bow''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:50s}],display:{Lore:["§8King's Valley : Tier III"],Name:"§fSearing Bow"}}'''
		]
	],
	[
		{
			"id":"minecraft:fishing_rod",
			"name":u'''Angler's Rod''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:62s},{lvl:2s,id:34s}],display:{Lore:["§8King's Valley : Tier III"],Name:"§fAngler's Rod"}}'''
		]
	],
	[
		{
			"id":"minecraft:stick",
			"name":u'''Apprentice's Wand''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:1s,id:19s},{lvl:1s,id:20s}],display:{Lore:["§8* Magic Wand *","§8King's Valley : Tier III"],Name:"§fApprentice's Wand"}}'''
		]
	],
	[
		{
			"id":"minecraft:stick",
			"name":u'''Consecrated Wand''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:17s},{lvl:1s,id:19s},{lvl:1s,id:21s}],display:{Lore:["§8* Magic Wand *","§8King's Valley : Tier III"],Name:"§fConsecrated Wand"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_hoe",
			"name":u'''Ruffian's Scythe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:16s},{lvl:1s,id:17s},{lvl:1s,id:34s},{lvl:1s,id:21s}],HideFlags:2,display:{Lore:["§8King's Valley : Tier III","§8","§7When in main hand:","§7 2 Attack Speed","§7 4 Attack Damage"],Name:"§fRuffian's Scythe"},AttributeModifiers:[{UUIDMost:6433490404641818817l,UUIDLeast:-8593178968434576189l,Amount:-2.0d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"Modifier"},{UUIDMost:3288944914052894654l,UUIDLeast:-5839775210248136997l,Amount:2.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Sky Mage Coif''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:2s,id:34s},{lvl:2s,id:2s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier III"],color:10531071,Name:"§fSky Mage Coif"},AttributeModifiers:[{UUIDMost:260399l,UUIDLeast:803793l,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Sky Mage Cloak''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:2s,id:34s},{lvl:2s,id:2s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier III"],color:10531071,Name:"§fSky Mage Cloak"},AttributeModifiers:[{UUIDMost:270399l,UUIDLeast:903793l,Amount:1.5d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Sky Mage Robe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:2s,id:34s},{lvl:2s,id:2s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier III"],color:10531071,Name:"§fSky Mage Robe"},AttributeModifiers:[{UUIDMost:280399l,UUIDLeast:1003793l,Amount:1.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Sky Mage Slippers''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:2s,id:34s},{lvl:2s,id:2s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier III"],color:10531071,Name:"§fSky Mage Slippers"},AttributeModifiers:[{UUIDMost:290399l,UUIDLeast:1103793l,Amount:0.75d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Scoundrel's Hood''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:4s},{lvl:1s,id:34s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier III"],color:2109472,Name:"§fScoundrel's Hood"},AttributeModifiers:[{UUIDMost:260399l,UUIDLeast:803793l,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Scoundrel's Tunic''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:4s},{lvl:1s,id:34s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier III"],color:2109472,Name:"§fScoundrel's Tunic"},AttributeModifiers:[{UUIDMost:270399l,UUIDLeast:903793l,Amount:1.5d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Scoundrel's Trousers''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:4s},{lvl:1s,id:34s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier III"],color:2109472,Name:"§fScoundrel's Trousers"},AttributeModifiers:[{UUIDMost:280399l,UUIDLeast:1003793l,Amount:1.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Scoundrel's Slippers''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:4s},{lvl:1s,id:34s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier III"],color:2109472,Name:"§fScoundrel's Slippers"},AttributeModifiers:[{UUIDMost:290399l,UUIDLeast:1103793l,Amount:0.75d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Spellweave Hat''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:2s,id:34s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier III"],color:11555008,Name:"§fSpellweave Hat"},AttributeModifiers:[{UUIDMost:260399l,UUIDLeast:803793l,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Spellweave Tunic''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:2s,id:34s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier III"],color:11555008,Name:"§fSpellweave Tunic"},AttributeModifiers:[{UUIDMost:270399l,UUIDLeast:903793l,Amount:1.5d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Spellweave Trousers''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:2s,id:34s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier III"],color:11555008,Name:"§fSpellweave Trousers"},AttributeModifiers:[{UUIDMost:280399l,UUIDLeast:1003793l,Amount:1.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Spellweave Shoes''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:2s,id:34s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier III"],color:11555008,Name:"§fSpellweave Shoes"},AttributeModifiers:[{UUIDMost:290399l,UUIDLeast:1103793l,Amount:0.75d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Blast Visor''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:34s},{lvl:2s,id:3s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier III"],color:5597999,Name:"§fBlast Visor"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Blast Vest''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:34s},{lvl:2s,id:3s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier III"],color:5597999,Name:"§fBlast Vest"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Blast Apron''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:34s},{lvl:2s,id:3s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier III"],color:5597999,Name:"§fBlast Apron"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Blast Boots''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:34s},{lvl:2s,id:3s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier III"],color:5597999,Name:"§fBlast Boots"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Burnt Helm''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:1s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier III"],color:7352328,Name:"§fBurnt Helm"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Burnt Cloak''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:1s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier III"],color:7352328,Name:"§fBurnt Cloak"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Burnt Leggings''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:1s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier III"],color:7352328,Name:"§fBurnt Leggings"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Burnt Boots''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:1s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier III"],color:7352328,Name:"§fBurnt Boots"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Warlock Helm''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:1s},{lvl:4s,id:34s},{lvl:1s,id:10s},{lvl:1s,id:3s},{lvl:1s,id:4s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier III"],color:14725264,Name:"§fWarlock Helm"},AttributeModifiers:[{UUIDMost:260399l,UUIDLeast:803793l,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Warlock Robe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:1s},{lvl:4s,id:34s},{lvl:1s,id:10s},{lvl:1s,id:3s},{lvl:1s,id:4s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier III"],color:14725264,Name:"§fWarlock Robe"},AttributeModifiers:[{UUIDMost:270399l,UUIDLeast:903793l,Amount:1.5d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Warlock Robe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:1s},{lvl:4s,id:34s},{lvl:1s,id:10s},{lvl:1s,id:3s},{lvl:1s,id:4s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier III"],color:14725264,Name:"§fWarlock Robe"},AttributeModifiers:[{UUIDMost:280399l,UUIDLeast:1003793l,Amount:1.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Warlock Boots''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:1s},{lvl:4s,id:34s},{lvl:1s,id:10s},{lvl:1s,id:3s},{lvl:1s,id:4s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier III"],color:14725264,Name:"§fWarlock Boots"},AttributeModifiers:[{UUIDMost:290399l,UUIDLeast:1103793l,Amount:0.75d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Zephyric Sandals''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:1s,id:34s},{lvl:7s,id:2s}],display:{Lore:["§9Cloth Armor","§eKing's Valley : Rare","§fHalls of Wind and Blood","§8The power of ancient winds hum within","§8these sandals"],color:13684991,Name:"§b§lZephyric Sandals"},AttributeModifiers:[{UUIDMost:-519805393186370468l,UUIDLeast:-7058263731030477121l,Amount:0.75d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"Modifier"},{UUIDMost:-7658801990265518657l,UUIDLeast:-6575958443379293118l,Amount:0.05d,Slot:"feet",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Ancient Robes''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:3s,id:34s}],display:{Lore:["§bLeather Armor","§eKing's Valley : Rare","§fHalls of Wind and Blood","§8Flecks of blood stains these ancient","§8sacrificial robes."],color:6299664,Name:"§4§lAncient Robes"},AttributeModifiers:[{UUIDMost:6974589633277084868l,UUIDLeast:-6904800762426278794l,Amount:2.0d,Slot:"legs",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"},{UUIDMost:583279600458681380l,UUIDLeast:-6719247825501452697l,Amount:2.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''C'Zanil's Shroud''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:4s},{lvl:2s,id:34s}],display:{Lore:["§dRegeneration","§eKing's Valley : Rare","§fHalls of Wind and Blood","§8Even in death, C'Zanil's ritual lives on"],color:41215,Name:"§6§lC'Zanil's Shroud"},AttributeModifiers:[]}'''
		]
	],
	[
		{
			"id":"minecraft:skull",
			"name":u'''Phantom's Hood''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:1s},{lvl:1s,id:4s},{lvl:1s,id:3s},{lvl:1s,id:71s}],SkullOwner:{Id:"251ab4e3-c5f6-61e5-b664-59f78f131844",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvYWJlZGI4ZDRiMDZlZWI5NzllZTUxNWY3NzhmMzFiM2RlZWY5MmZiNTgxN2YzNDUyZjUxZmM1OGQ0ODEzNCJ9fX0="}]}},display:{Lore:["§eKing's Valley : Rare","§fHalls of Wind and Blood","§8The Phantoms were assassins of","§8the Tlaxans, able to eliminate","§8high-value targets at a whim."],Name:"§3§lPhantom's Hood"},AttributeModifiers:[{UUIDMost:-1757382812970040601l,UUIDLeast:-8366606905223081447l,Amount:0.08d,Slot:"head",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:bone",
			"name":u'''Wand of C'Zanil''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:16s},{lvl:1s,id:20s}],display:{Lore:["§dRegeneration","§8* Magic Wand *","§eKing's Valley : Rare","§fHalls of Wind and Blood","§8C'Zanil's wand still siphons souls from beyond"],Name:"§6§lWand of C'Zanil"}}'''
		]
	],
	[
		{
			"id":"minecraft:bow",
			"name":u'''Quetzalcoatl's Wrath''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:48s},{lvl:1s,id:70s},{lvl:1s,id:71s}],display:{Lore:["§eKing's Valley : Rare","§fHalls of Wind and Blood","§8The god looms large, power flowing from","§8his mouth."],Name:"§3§lQuetzalcoatl's Wrath"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"name":u'''Ashheart Dagger''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:34s},{lvl:4s,id:20s},{lvl:2s,id:22s},{lvl:1s,id:71s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§fHalls of Wind and Blood","§8Stab down, and take their soul","§8","§7When in main hand:","§7 1.6 Attack Speed","§7 5 Attack Damage","§9 +3 Armor"],Name:"§8§lAshheart Dagger"},AttributeModifiers:[{UUIDMost:1770737273186633355l,UUIDLeast:-7632807259696268977l,Amount:4.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"},{UUIDMost:-925442460826187303l,UUIDLeast:-5209611670608876751l,Amount:-2.4d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"Modifier"},{UUIDMost:6103634434368686082l,UUIDLeast:-7623905401435699878l,Amount:3.0d,Slot:"mainhand",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_pickaxe",
			"name":u'''Ashfloe Chisel''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:32s},{lvl:5s,id:35s}],display:{Lore:["§eKing's Valley : Rare","§fHalls of Wind and Blood","§8Used to clear chunks of magma from","§8important channels."],Name:"§8§lAshfloe Chisel"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Fur Boots''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:2s,id:1s}],display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:12486759,Name:"§fFur Boots"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Fur Leggings''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:2s,id:1s}],display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:12486759,Name:"§fFur Leggings"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Fur Tunic''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:2s,id:1s}],display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:12486759,Name:"§fFur Tunic"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Fur Cap''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:2s,id:1s}],display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:12486759,Name:"§fFur Cap"}}'''
		]
	],
	[
		{
			"id":"minecraft:shield",
			"name":u'''Hide Shield''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:34s}],BlockEntityTag:{Base:3,Patterns:[{Color:14,Pattern:"mr"},{Color:3,Pattern:"sku"}]},display:{Lore:["§8King's Valley : Uncommon"],Name:"§fHide Shield"},AttributeModifiers:[{UUIDMost:4829683371424304161l,UUIDLeast:-8495861702335545947l,Amount:0.15d,Slot:"mainhand",AttributeName:"generic.knockbackResistance",Operation:0,Name:"Modifier"},{UUIDMost:-660961315230563653l,UUIDLeast:-7651396858820480353l,Amount:0.15d,Slot:"offhand",AttributeName:"generic.knockbackResistance",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:rabbit_hide",
			"name":u'''Immaculate Hide''',
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["§8Delightfully fuzzy"],Name:"§fImmaculate Hide"}}'''
		]
	],
	[
		{
			"id":"minecraft:golden_chestplate",
			"name":u'''King's Warden''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:0s},{lvl:2s,id:3s},{lvl:1s,id:70s}],display:{Lore:["§6King's Valley : §lEPIC"],Name:"§b§l§nKing's Warden"},AttributeModifiers:[{UUIDMost:96224l,UUIDLeast:26892l,Amount:2d,Slot:"chest",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"},{UUIDMost:348118l,UUIDLeast:433148l,Amount:5d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"name":u'''Angelic Sword''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:17s},{lvl:5s,id:34s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§3King's Valley","","§7When in main hand:","§7 1.6 Attack Speed","§7 5 Attack Damage","§9 +1 Armor"],Name:"§6§lAngelic Sword"},AttributeModifiers:[{UUIDMost:13921849192281677l,UUIDLeast:29424957165321736l,Amount:4d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:14771070297205314l,UUIDLeast:58375339796730923l,Amount:1d,Slot:"mainhand",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:69970127574793796l,UUIDLeast:64342718172429329l,Amount:-2.4d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"name":u'''Mithril Cleaver''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:16s},{lvl:2s,id:34s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§3King's Valley","","§7When in main hand:","§7 1.2 Attack Speed","§7 10 Attack Damage","§9 +12% Speed"],Name:"§3§lMithril Cleaver"},AttributeModifiers:[{UUIDMost:1317475486626126l,UUIDLeast:53226458093335048l,Amount:0.12d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:776403941688908l,UUIDLeast:11889093433774429l,Amount:-2.8d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"},{UUIDMost:30352855180673349l,UUIDLeast:58285458965911180l,Amount:8d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"}]}'''
		]
	],
	[
		{
			"id":"minecraft:blaze_rod",
			"name":u'''Hell's Fury''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:2s,id:19s},{lvl:5s,id:20s}],display:{Lore:["§8* Magic Wand *","§eKing's Valley : Rare","§3King's Valley"],Name:"§5§lHell's Fury"},AttributeModifiers:[{UUIDMost:69502167760309831l,UUIDLeast:25155512585813018l,Amount:0.08d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:golden_sword",
			"name":u'''Soulvenom Dagger''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:34s}],HideFlags:1,display:{Lore:["§eKing's Valley : Rare","§3King's Valley"],Name:"§2§lSoulvenom Dagger"},AttributeModifiers:[{UUIDMost:848078l,UUIDLeast:702456l,Amount:-2d,Slot:"offhand",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"},{UUIDMost:521417l,UUIDLeast:238571l,Amount:0.08d,Slot:"offhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:783241l,UUIDLeast:758745l,Amount:0.3d,Slot:"offhand",AttributeName:"generic.attackDamage",Operation:1,Name:"generic.attackDamage"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_pickaxe",
			"name":u'''Obsidian Pickaxe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:32s},{lvl:1s,id:34s}],display:{Lore:["§eKing's Valley : Rare","§3King's Valley"],Name:"§3§lObsidian Pickaxe"}}'''
		]
	],
	[
		{
			"id":"minecraft:shield",
			"name":u'''Keeper of the Jungle''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:34s}],HideFlags:32,BlockEntityTag:{Base:3,Patterns:[{Color:2,Pattern:"ss"},{Color:2,Pattern:"flo"},{Color:2,Pattern:"bri"}]},display:{Lore:["§eKing's Valley : Rare","§3King's Valley"],Name:"§2§lKeeper of the Jungle"},AttributeModifiers:[{UUIDMost:9006655014927177l,UUIDLeast:4782782479127341l,Amount:1d,Slot:"offhand",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Angelic Pants''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:34s}],display:{Lore:["§bLeather Armor","§eKing's Valley : Rare","§3King's Valley"],color:14277081,Name:"§6§lAngelic Pants"},AttributeModifiers:[{UUIDMost:2767629973749578l,UUIDLeast:26549136928073536l,Amount:5d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:flower_pot",
			"name":u'''Ancient Relic''',
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["Uncommon Ingredient"],Name:"§b§lAncient Relic"}}'''
		]
	],
	[
		{
			"id":"minecraft:double_plant",
			"name":u'''Swiftwood Leaf''',
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["Uncommon Ingredient"],Name:"§b§lSwiftwood Leaf"}}'''
		]
	],
	[
		{
			"id":"minecraft:prismarine_crystals",
			"name":u'''Guardian Scales''',
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["Uncommon Ingredient"],Name:"§b§lGuardian Scales"}}'''
		]
	],
	[
		{
			"id":"minecraft:blaze_powder",
			"name":u'''Crystalized Fire''',
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["Uncommon Ingredient"],Name:"§b§lCrystalized Fire"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Explorer's Boots''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:8s},{lvl:1s,id:0s},{lvl:1s,id:34s}],display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:3445134,Name:"§fExplorer's Boots"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Explorer's Cap''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:2s,id:5s},{lvl:1s,id:6s}],display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:755048,Name:"§fExplorer's Cap"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Plaguehide Boots''',
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:675072,Name:"§aPlaguehide Boots"},AttributeModifiers:[{UUIDMost:19971159992297292l,UUIDLeast:11701631750427272l,Amount:2d,Slot:"feet",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"},{UUIDMost:50620023180411213l,UUIDLeast:56580625667548148l,Amount:0.05d,Slot:"feet",AttributeName:"generic.attackDamage",Operation:1,Name:"generic.attackDamage"},{UUIDMost:61536614628787790l,UUIDLeast:12067686387522583l,Amount:1d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Plaguehide Pants''',
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:675072,Name:"§aPlaguehide Pants"},AttributeModifiers:[{UUIDMost:7398196116790600l,UUIDLeast:33239325481073366l,Amount:2d,Slot:"legs",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"},{UUIDMost:61910509039675723l,UUIDLeast:13746144420287990l,Amount:0.05d,Slot:"legs",AttributeName:"generic.attackDamage",Operation:1,Name:"generic.attackDamage"},{UUIDMost:14165244533123147l,UUIDLeast:22637248009267620l,Amount:2d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Plaguehide Torso''',
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:675072,Name:"§aPlaguehide Torso"},AttributeModifiers:[{UUIDMost:71978911221471809l,UUIDLeast:25260044972271010l,Amount:2d,Slot:"chest",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"},{UUIDMost:19117308396094024l,UUIDLeast:9968568939286539l,Amount:0.05d,Slot:"chest",AttributeName:"generic.attackDamage",Operation:1,Name:"generic.attackDamage"},{UUIDMost:8440217748974405l,UUIDLeast:3552643124966103l,Amount:3d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Plaguehide Cap''',
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:675072,Name:"§aPlaguehide Cap"},AttributeModifiers:[{UUIDMost:22907356139724361l,UUIDLeast:55634361538278368l,Amount:2d,Slot:"head",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"},{UUIDMost:50813337862916683l,UUIDLeast:38856196263924788l,Amount:0.05d,Slot:"head",AttributeName:"generic.attackDamage",Operation:1,Name:"generic.attackDamage"},{UUIDMost:22347000550566221l,UUIDLeast:68212466135762333l,Amount:1d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:lingering_potion",
			"name":u'''Strong Barrier Potion''',
		},
		[
			"nbt", "replace", ur'''{CustomPotionColor:160,CustomPotionEffects:[{Ambient:1b,ShowParticles:1b,Duration:400,Id:2b,Amplifier:4b},{Ambient:1b,ShowParticles:1b,Duration:400,Id:4b,Amplifier:0b},{Ambient:1b,ShowParticles:1b,Duration:400,Id:19b,Amplifier:0b}],Potion:"minecraft:empty",display:{Name:"§aStrong Barrier Potion"}}'''
		]
	],
	[
		{
			"id":"minecraft:lingering_potion",
			"name":u'''Strong Sanctify Potion''',
		},
		[
			"nbt", "replace", ur'''{CustomPotionColor:16744576,CustomPotionEffects:[{Ambient:1b,ShowParticles:1b,Duration:240,Id:10b,Amplifier:2b},{Ambient:1b,ShowParticles:1b,Duration:900,Id:22b,Amplifier:0b}],Potion:"minecraft:empty",display:{Name:"§aStrong Sanctify Potion"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"name":u'''Prismatic Blade''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:2s,id:17s},{lvl:3s,id:34s}],display:{Lore:["§eKing's Valley : Rare","§3Arcane Rivalry","§8The blade glows with the colors of infinity"],Name:"§6§lPrismatic Blade"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"name":u'''Searing Wrath''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:5s,id:16s},{lvl:3s,id:34s},{lvl:2s,id:19s},{lvl:2s,id:20s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§3Arcane Rivalry","§8Flames and rage go hand in","§8hand, moreso magically.","§7","§7When in main hand:","§7 0.8 Attack Speed","§7 12 Attack Damage","§c -3 Armor"],Name:"§4§lSearing Wrath"},AttributeModifiers:[{UUIDMost:797401l,UUIDLeast:849310l,Amount:8.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:205397l,UUIDLeast:267554l,Amount:-3.0d,Slot:"mainhand",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:589373l,UUIDLeast:600470l,Amount:-3.2d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:book",
			"name":u'''Tome of Arcane Horrors''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:20s},{lvl:3s,id:19s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§3Arcane Rivalry","§8Some things were never meant to be read.","§7","§7When in main hand:","§7 0.5 Attack Speed","§7 16 Attack Damage"],Name:"§5§lTome of Arcane Horrors"},AttributeModifiers:[{UUIDMost:495321l,UUIDLeast:169768l,Amount:15.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:564922l,UUIDLeast:574772l,Amount:-3.5d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:bow",
			"name":u'''Arcane Storm''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:48s},{lvl:3s,id:49s},{lvl:2s,id:34s}],display:{Lore:["§eKing's Valley : Rare","§3Arcane Rivalry","§8Magic crackles around this","§8bow, stinging your hands."],Name:"§9§lArcane Storm"}}'''
		]
	],
	[
		{
			"id":"minecraft:stick",
			"name":u'''Thaumaturge's Greed''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:4s,id:17s},{lvl:1s,id:19s},{lvl:1s,id:20s},{lvl:2s,id:21s}],display:{Lore:["§8* Magic Wand *","§eKing's Valley : Rare","§3Arcane Rivalry","§8There are laws of equivalent","§8exchange for a reason."],Name:"§b§lThaumaturge's Greed"}}'''
		]
	],
	[
		{
			"id":"minecraft:chainmail_boots",
			"name":u'''Chains of the Damned''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:4s,id:0s},{lvl:1s,id:10s},{lvl:1s,id:70s}],display:{Lore:["§eKing's Valley : Rare","§3Arcane Rivalry","§8Chain them up. Forever"],Name:"§4§lChains of the Damned"},AttributeModifiers:[{UUIDMost:1354465141316075984l,UUIDLeast:-7619938869357070894l,Amount:-0.1d,Slot:"feet",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"},{UUIDMost:-8686196100279418339l,UUIDLeast:-7938211705147810854l,Amount:1.0d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Boreas Greaves''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:4s},{lvl:5s,id:34s},{lvl:2s,id:2s}],display:{Lore:["§bLeather Armor","§eKing's Valley : Rare","§3Arcane Rivalry","§8A cold wind blows..."],color:13100779,Name:"§9§lBoreas Greaves"},AttributeModifiers:[{UUIDMost:459286l,UUIDLeast:392956l,Amount:0.1d,Slot:"legs",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:428915l,UUIDLeast:855359l,Amount:2.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:277302l,UUIDLeast:24984l,Amount:0.1d,Slot:"legs",AttributeName:"generic.attackSpeed",Operation:1,Name:"generic.attackSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Archmage's Vestment''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:2s,id:1s},{lvl:2s,id:34s},{lvl:2s,id:3s},{lvl:2s,id:4s}],display:{Lore:["§bLeather Armor","§eKing's Valley : Rare","§3Arcane Rivalry","§8The mantle of Archmage is passed by death.","§8More specifically by killing the prior owner."],color:8201983,Name:"§d§lArchmage's Vestment"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"name":u'''Tempered Ironwood Blade''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:16s},{lvl:2s,id:34s},{lvl:2s,id:21s}],display:{Lore:["§8King's Valley : Tier II"],Name:"§fTempered Ironwood Blade"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"name":u'''Sculpted Dagger''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:16s}],display:{Lore:["§8King's Valley : Tier II"],Name:"§fSculpted Dagger"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"name":u'''Ashen Broadsword''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:34s},{lvl:1s,id:20s},{lvl:2s,id:22s}],display:{Lore:["§8King's Valley : Tier II"],Name:"§fAshen Broadsword"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"name":u'''Priest's Stake''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:17s},{lvl:3s,id:34s}],display:{Lore:["§8King's Valley : Tier II"],Name:"§fPriest's Stake"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"name":u'''Versatile Knife''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:16s},{lvl:2s,id:18s},{lvl:1s,id:34s}],display:{Lore:["§8King's Valley : Tier II"],Name:"§fVersatile Knife"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"name":u'''Searing Gladius''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:34s},{lvl:2s,id:19s},{lvl:1s,id:20s}],display:{Lore:["§8King's Valley : Tier II"],Name:"§fSearing Gladius"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"name":u'''Burning Rapier''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:20s},{lvl:1s,id:34s}],display:{Lore:["§8King's Valley : Tier II"],Name:"§fBurning Rapier"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"name":u'''Soldier's Blade''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:16s}],display:{Lore:["§8King's Valley : Tier II"],Name:"§fSoldier's Blade"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"name":u'''Granite Sabre''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:34s}],display:{Lore:["§8King's Valley : Tier II"],Name:"§fGranite Sabre"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"name":u'''Rogue's Knife''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:51s}],HideFlags:1,display:{Lore:["§8King's Valley : Tier II"],Name:"§fRogue's Knife"},AttributeModifiers:[{UUIDMost:912265l,UUIDLeast:500295l,Amount:0.1d,Slot:"offhand",AttributeName:"generic.attackSpeed",Operation:1,Name:"generic.attackSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"name":u'''Survivalist's Sword''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:51s}],HideFlags:1,display:{Lore:["§8King's Valley : Tier II"],Name:"§fSurvivalist's Sword"},AttributeModifiers:[{UUIDMost:637136l,UUIDLeast:234308l,Amount:2d,Slot:"offhand",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"name":u'''Warhammer''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:19s}],display:{Lore:["§8King's Valley : Tier II"],Name:"§fWarhammer"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"name":u'''Masterwork Axe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:32s}],display:{Lore:["§8King's Valley : Tier II"],Name:"§fMasterwork Axe"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_axe",
			"name":u'''Honed Swiftwood Axe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:32s}],display:{Lore:["§8King's Valley : Tier II"],Name:"§fHoned Swiftwood Axe"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_axe",
			"name":u'''Versatile Axe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:16s},{lvl:1s,id:32s},{lvl:2s,id:34s}],display:{Lore:["§8King's Valley : Tier II"],Name:"§fVersatile Axe"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_axe",
			"name":u'''Smoldering Mace''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:17s},{lvl:1s,id:34s},{lvl:1s,id:20s}],display:{Lore:["§8King's Valley : Tier II"],Name:"§fSmoldering Mace"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_pickaxe",
			"name":u'''Bluefell Chisel''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:32s},{lvl:1s,id:34s}],display:{Lore:["§8King's Valley : Tier II"],Name:"§fBluefell Chisel"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_pickaxe",
			"name":u'''Miner's Pick''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:35s}],display:{Lore:["§8King's Valley : Tier II"],Name:"§fMiner's Pick"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_pickaxe",
			"name":u'''Granite Pickaxe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:34s}],display:{Lore:["§8King's Valley : Tier II"],Name:"§fGranite Pickaxe"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_shovel",
			"name":u'''Grassbane''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:32s},{lvl:1s,id:34s}],display:{Lore:["§8King's Valley : Tier II"],Name:"§fGrassbane"}}'''
		]
	],
	[
		{
			"id":"minecraft:stick",
			"name":u'''Student's Wand''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:16s},{lvl:1s,id:19s},{lvl:1s,id:20s}],display:{Lore:["§8* Magic Wand *","§8King's Valley : Tier II"],Name:"§fStudent's Wand"}}'''
		]
	],
	[
		{
			"id":"minecraft:blaze_rod",
			"name":u'''Flame Wand''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:20s},{lvl:2s,id:19s}],display:{Lore:["§8* Magic Wand *","§8King's Valley : Tier II"],Name:"§fFlame Wand"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_hoe",
			"name":u'''Peasant's Scythe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:17s},{lvl:1s,id:34s},{lvl:1s,id:21s}],HideFlags:2,display:{Lore:["§8King's Valley : Tier II","§8","§7When in main hand:","§7 2 Attack Speed","§7 3 Attack Damage"],Name:"§fPeasant's Scythe"},AttributeModifiers:[{UUIDMost:6433490404641818817l,UUIDLeast:-8593178968434576189l,Amount:-2.0d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"Modifier"},{UUIDMost:3288944914052894654l,UUIDLeast:-5839775210248136997l,Amount:2.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:bow",
			"name":u'''Ironwood Bow''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:34s}],display:{Lore:["§8King's Valley : Tier II"],Name:"§fIronwood Bow"}}'''
		]
	],
	[
		{
			"id":"minecraft:bow",
			"name":u'''Longbow''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:49s}],display:{Lore:["§8King's Valley : Tier II"],Name:"§fLongbow"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Bandit's Cap''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:4s},{lvl:1s,id:34s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier II"],color:5197647,Name:"§fBandit's Cap"},AttributeModifiers:[{UUIDMost:260399l,UUIDLeast:803793l,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Bandit's Tunic''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:4s},{lvl:1s,id:34s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier II"],color:5197647,Name:"§fBandit's Tunic"},AttributeModifiers:[{UUIDMost:270399l,UUIDLeast:903793l,Amount:1.5d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Bandit's Trousers''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:4s},{lvl:1s,id:34s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier II"],color:5197647,Name:"§fBandit's Trousers"},AttributeModifiers:[{UUIDMost:280399l,UUIDLeast:1003793l,Amount:1.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Bandit's Boots''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:4s},{lvl:1s,id:34s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier II"],color:5197647,Name:"§fBandit's Boots"},AttributeModifiers:[{UUIDMost:290399l,UUIDLeast:1103793l,Amount:0.75d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Crimson Mage Hat''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier II"],color:12517599,Name:"§fCrimson Mage Hat"},AttributeModifiers:[{UUIDMost:260399l,UUIDLeast:803793l,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Crimson Mage Robes''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier II"],color:12517599,Name:"§fCrimson Mage Robes"},AttributeModifiers:[{UUIDMost:270399l,UUIDLeast:903793l,Amount:1.5d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Crimson Mage Robes''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier II"],color:12517599,Name:"§fCrimson Mage Robes"},AttributeModifiers:[{UUIDMost:280399l,UUIDLeast:1003793l,Amount:1.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Crimson Mage Robes''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:1s,id:2s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier II"],color:12517599,Name:"§fCrimson Mage Robes"},AttributeModifiers:[{UUIDMost:290399l,UUIDLeast:1103793l,Amount:0.75d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Thornskin Veil''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:34s},{lvl:3s,id:7s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier II"],color:4185951,Name:"§fThornskin Veil"},AttributeModifiers:[{UUIDMost:260399l,UUIDLeast:803793l,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Thornskin Robe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:34s},{lvl:3s,id:7s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier II"],color:4185951,Name:"§fThornskin Robe"},AttributeModifiers:[{UUIDMost:270399l,UUIDLeast:903793l,Amount:1.5d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Thornskin Robe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:34s},{lvl:3s,id:7s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier II"],color:4185951,Name:"§fThornskin Robe"},AttributeModifiers:[{UUIDMost:280399l,UUIDLeast:1003793l,Amount:1.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Thornskin Shoes''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:34s},{lvl:3s,id:7s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier II"],color:4185951,Name:"§fThornskin Shoes"},AttributeModifiers:[{UUIDMost:290399l,UUIDLeast:1103793l,Amount:0.75d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Alchemist's Helm''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:1s},{lvl:1s,id:3s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier II"],color:16776960,Name:"§fAlchemist's Helm"},AttributeModifiers:[{UUIDMost:260399l,UUIDLeast:803793l,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Alchemist's Apron''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:1s},{lvl:1s,id:3s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier II"],color:16776960,Name:"§fAlchemist's Apron"},AttributeModifiers:[{UUIDMost:270399l,UUIDLeast:903793l,Amount:1.5d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Alchemist's Robe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:1s},{lvl:1s,id:3s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier II"],color:16776960,Name:"§fAlchemist's Robe"},AttributeModifiers:[{UUIDMost:280399l,UUIDLeast:1003793l,Amount:1.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Alchemist's Boots''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:1s},{lvl:1s,id:3s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier II"],color:16776960,Name:"§fAlchemist's Boots"},AttributeModifiers:[{UUIDMost:290399l,UUIDLeast:1103793l,Amount:0.75d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Turtle Helm''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:5s},{lvl:2s,id:3s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier II"],color:36912,Name:"§fTurtle Helm"},AttributeModifiers:[{UUIDMost:260399l,UUIDLeast:803793l,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Turtle Vest''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:6s},{lvl:2s,id:3s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier II"],color:36912,Name:"§fTurtle Vest"},AttributeModifiers:[{UUIDMost:270399l,UUIDLeast:903793l,Amount:1.5d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Turtle Pants''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:8s},{lvl:2s,id:3s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier II"],color:36912,Name:"§fTurtle Pants"},AttributeModifiers:[{UUIDMost:280399l,UUIDLeast:1003793l,Amount:1.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Turtle Flippers''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:8s},{lvl:2s,id:3s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier II"],color:36912,Name:"§fTurtle Flippers"},AttributeModifiers:[{UUIDMost:290399l,UUIDLeast:1103793l,Amount:0.75d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Puresilk Coif''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:1s,id:34s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier II"],color:12636415,Name:"§fPuresilk Coif"},AttributeModifiers:[{UUIDMost:260399l,UUIDLeast:803793l,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:260399l,UUIDLeast:803793l,Amount:0.02d,Slot:"head",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Puresilk Tunic''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:1s,id:34s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier II"],color:12636415,Name:"§fPuresilk Tunic"},AttributeModifiers:[{UUIDMost:270399l,UUIDLeast:903793l,Amount:1.5d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:270399l,UUIDLeast:903793l,Amount:0.02d,Slot:"chest",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Puresilk Leggings''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:1s,id:34s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier II"],color:12636415,Name:"§fPuresilk Leggings"},AttributeModifiers:[{UUIDMost:280399l,UUIDLeast:1003793l,Amount:1.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:280399l,UUIDLeast:1003793l,Amount:0.02d,Slot:"legs",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Puresilk Slippers''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:1s,id:34s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier II"],color:12636415,Name:"§fPuresilk Slippers"},AttributeModifiers:[{UUIDMost:290399l,UUIDLeast:1103793l,Amount:0.75d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:290399l,UUIDLeast:1103793l,Amount:0.02d,Slot:"feet",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"name":u'''Telum Immoriel''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:34s},{lvl:1s,id:22s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§7The Black Willows","§8Another toy for Fangride to play with","§7","§7When in main hand:","§7 0.8 Attack Speed","§7 12 Attack Damage"],Name:"§6§lTelum Immoriel"},AttributeModifiers:[{UUIDMost:962659l,UUIDLeast:90631l,Amount:11.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:345591l,UUIDLeast:876260l,Amount:-3.2d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:sapling",
			"name":u'''Chimarian Wand''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:16s},{lvl:2s,id:17s},{lvl:2s,id:18s},{lvl:1s,id:20s}],display:{Lore:["§eKing's Valley : Rare","§7The Black Willows","§8We need more trees!","§8* Magic Wand *"],Name:"§2§lChimarian Wand"}}'''
		]
	],
	[
		{
			"id":"minecraft:quartz",
			"name":u'''Render's Ruthless Claw''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:8s,id:16s}],display:{Lore:["§eKing's Valley : Rare","§7The Black Willows","§8Simplistic, but effective"],Name:"§3§lRender's Ruthless Claw"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_pickaxe",
			"name":u'''Helician Spitzhacke''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:32s},{lvl:3s,id:34s}],HideFlags:3,display:{Lore:["§7Effizienz II","§7Unbreaking III","§eKing's Valley : Rare","§7The Black Willows","§8Now with German efficiency!","§7","§7When in main hand:","§7 1.2 Attack Speed","§7 3 Attack Damage","§9 +0.5 Knockback Resistance","§9 +3 Armor"],Name:"§1§lHelician Spitzhacke"},AttributeModifiers:[{UUIDMost:203618l,UUIDLeast:725165l,Amount:0.5d,Slot:"mainhand",AttributeName:"generic.knockbackResistance",Operation:0,Name:"generic.knockbackResistance"},{UUIDMost:961145l,UUIDLeast:133590l,Amount:3.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:670193l,UUIDLeast:659361l,Amount:3.0d,Slot:"mainhand",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:641625l,UUIDLeast:480595l,Amount:-2.8d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:red_flower",
			"name":u'''Teewie's Eternal Tulip''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s}],HideFlags:1,display:{Lore:["§eKing's Valley : Rare","§7The Black Willows","§8Part of the flower crown worn by Princess Teewie","§8many centuries ago"],Name:"§d§lTeewie's Eternal Tulip"},AttributeModifiers:[{UUIDMost:-2576588526142208534l,UUIDLeast:-8215095133131934612l,Amount:3.0d,Slot:"offhand",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"},{UUIDMost:-7377653646270249488l,UUIDLeast:-4833595088129389224l,Amount:2.0d,Slot:"offhand",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Busty's Hot Pants''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:1s},{lvl:1s,id:70s},{lvl:2s,id:3s}],display:{Lore:["§bLeather Armor","§eKing's Valley : Rare","§7The Black Willows","§8Caution: Highly Combustible!"],color:14059296,Name:"§4§lBusty's Hot Pants"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Brown Corp Uniform''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:3s,id:34s}],display:{Lore:["§bLeather Armor","§eKing's Valley : Rare","§7The Black Willows","§8What do they ever do besides hanging out?"],color:6704179,Name:"§5§lBrown Corp Uniform"},AttributeModifiers:[{UUIDMost:-395305911349064079l,UUIDLeast:-6975068402520238575l,Amount:2.0d,Slot:"chest",AttributeName:"generic.armorToughness",Operation:0,Name:"Modifier"},{UUIDMost:8894152384868271503l,UUIDLeast:-5148525816173331419l,Amount:3.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"name":u'''Stormborn Runeblade''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:1s,id:34s},{lvl:2s,id:19s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§6Rock's Little Casino","","§7When in main hand:","§7 2 Attack Speed","§7 6.5 Attack Damage","§9 +10% Speed"],Name:"§3§lStormborn Runeblade"},AttributeModifiers:[{UUIDMost:44607095061251400l,UUIDLeast:17181972604100280l,Amount:0.1d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:32717593065480005l,UUIDLeast:13800488484714149l,Amount:4d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:18508304389737284l,UUIDLeast:65266891060907778l,Amount:-2d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"name":u'''Earthbound Runeblade''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:2s,id:34s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§6Rock's Little Casino","","§7When in main hand:","§7 1.6 Attack Speed","§7 6.5 Attack Damage","§9 +2 Armor"],Name:"§2§lEarthbound Runeblade"},AttributeModifiers:[{UUIDMost:67445053026503759l,UUIDLeast:20777435665232169l,Amount:4d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:57037229736289856l,UUIDLeast:7096337185411272l,Amount:2d,Slot:"mainhand",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:29541336158339146l,UUIDLeast:50859522055085541l,Amount:-2.4d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"name":u'''Iceborn Runeblade''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:5s,id:16s},{lvl:1s,id:17s},{lvl:3s,id:34s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§6Rock's Little Casino","","§7When in main hand:"," §71.2 Attack Speed"," §78 Attack Damage"," §c-10% Speed"],Name:"§b§lIceborn Runeblade"},AttributeModifiers:[{UUIDMost:68342020398380105l,UUIDLeast:18376432692088500l,Amount:-0.1d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:20792108251577155l,UUIDLeast:44880469650724553l,Amount:4d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:49556179849667657l,UUIDLeast:15931220204059978l,Amount:-2.8d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"name":u'''Giant's Axe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:34s},{lvl:1s,id:19s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§6Rock's Little Casino","","§7When in main hand:","§7 0.6 Attack Speed","§7 15 Attack Damage"," §c-8% Speed"],Name:"§6§lGiant's Axe"},AttributeModifiers:[{UUIDMost:50069596546217285l,UUIDLeast:52124018636176511l,Amount:-0.08d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:16684340706050887l,UUIDLeast:61729139377545821l,Amount:14d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:20258808824438599l,UUIDLeast:52420949332344389l,Amount:-3.4d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_pickaxe",
			"name":u'''Pebblebane''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:32s}],display:{Lore:["§eKing's Valley : Rare","§6Rock's Little Casino","§fNot quite as good as Rockbane!"],Name:"§9§lPebblebane"},AttributeModifiers:[{UUIDMost:251682l,UUIDLeast:651852l,Amount:0.15d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Stormborn Boots''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:4s},{lvl:3s,id:34s},{lvl:2s,id:2s}],display:{Lore:["§eKing's Valley : Rare","§6Rock's Little Casino"],Name:"§3§lStormborn Boots"},AttributeModifiers:[{UUIDMost:8168110272590147l,UUIDLeast:66575962804257055l,Amount:0.05d,Slot:"feet",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:55068906034949703l,UUIDLeast:23695059647787143l,Amount:1d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Earthbound Pants''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:34s}],display:{Lore:["§eKing's Valley : Rare","§6Rock's Little Casino"],color:11753010,Name:"§2§lEarthbound Pants"},AttributeModifiers:[{UUIDMost:47478565729543745l,UUIDLeast:55464327090482055l,Amount:3d,Slot:"legs",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"},{UUIDMost:44980305394582344l,UUIDLeast:14485042704930583l,Amount:2d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Iceborn Helmet''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:0s},{lvl:1s,id:4s},{lvl:2s,id:5s},{lvl:3s,id:34s}],display:{Lore:["§eKing's Valley : Rare","§6Rock's Little Casino"],color:9107455,Name:"§b§lIceborn Helmet"},AttributeModifiers:[{UUIDMost:46674431434570316l,UUIDLeast:29842133510151376l,Amount:-0.05d,Slot:"head",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:10509373368372805l,UUIDLeast:27250250553169692l,Amount:1d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:shield",
			"name":u'''Imperial Bulwark''',
		},
		[
			"nbt", "replace", ur'''{HideFlags:32,BlockEntityTag:{Base:15,Patterns:[{Color:7,Pattern:"bri"},{Color:8,Pattern:"bo"},{Color:8,Pattern:"mr"},{Color:8,Pattern:"tts"},{Color:8,Pattern:"bts"}]},display:{Lore:["§eKing's Valley : Rare","§6Rock's Little Casino"],Name:"§6§lImperial Bulwark"},AttributeModifiers:[{UUIDMost:20324l,UUIDLeast:596443l,Amount:0.4d,Slot:"offhand",AttributeName:"generic.knockbackResistance",Operation:0,Name:"generic.knockbackResistance"}]}'''
		]
	],
	[
		{
			"id":"minecraft:bow",
			"name":u'''Demonbreath''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:48s},{lvl:1s,id:50s},{lvl:2s,id:19s},{lvl:1s,id:20s}],display:{Lore:["§eKing's Valley : Rare","§6Rock's Little Casino"],Name:"§4§lDemonbreath"},AttributeModifiers:[{UUIDMost:-7214717605117081503l,UUIDLeast:-8547664050005874273l,Amount:2.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:bone",
			"name":u'''Deathchill Staff''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:5s,id:16s},{lvl:2s,id:17s}],display:{Lore:["§8* Magic Wand *","§eKing's Valley : Rare","§6Rock's Little Casino"],Name:"§9§lDeathchill Staff"},AttributeModifiers:[{UUIDMost:9215418588072772l,UUIDLeast:29013032778824963l,Amount:0.3d,Slot:"mainhand",AttributeName:"generic.knockbackResistance",Operation:0,Name:"generic.knockbackResistance"},{UUIDMost:15405034991318852l,UUIDLeast:13833242679511430l,Amount:-0.1d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_hoe",
			"name":u'''Cryptkeeper's Scythe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:5s,id:16s},{lvl:2s,id:18s},{lvl:4s,id:34s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§6Rock's Little Casino","§7When in main hand:","§7 2 Attack Speed","§7 6 Attack Damage","§l","§7When in off hand:","§9 +2 Armor","§9 +1 Attack Damage"],Name:"§8§lCryptkeeper's Scythe"},AttributeModifiers:[{UUIDMost:6433490404641818817l,UUIDLeast:-8593178968434576189l,Amount:-2.0d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"Modifier"},{UUIDMost:3288944914052894654l,UUIDLeast:-5839775210248136997l,Amount:2.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"},{UUIDMost:-3549740715683920811l,UUIDLeast:-5007827127384468665l,Amount:2.0d,Slot:"offhand",AttributeName:"generic.armor",Operation:0,Name:"Modifier"},{UUIDMost:-309718873454917986l,UUIDLeast:-6703149036569285791l,Amount:1.0d,Slot:"offhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"name":u'''Spirit Blade''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:1s,id:70s}],display:{Lore:["§eKing's Valley : Rare","§3King's Valley"],Name:"§b§lSpirit Blade"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"name":u'''Shadow Spike''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:4s,id:16s},{lvl:2s,id:34s},{lvl:1s,id:19s},{lvl:1s,id:20s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§3King's Valley","","§7When in main hand:","§7 1.6 Attack Speed","§7 7.5 Attack Damage","§c -3 Armor"],Name:"§4§lShadow Spike"},AttributeModifiers:[{UUIDMost:24272506551626816l,UUIDLeast:3188629144429256l,Amount:4d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:68081597460234561l,UUIDLeast:58960188647077945l,Amount:-3d,Slot:"mainhand",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:40900807882193986l,UUIDLeast:13214525664118331l,Amount:-2.4d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:bow",
			"name":u'''Tempest Caller''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:48s},{lvl:1s,id:49s},{lvl:1s,id:34s}],display:{Lore:["§eKing's Valley : Rare","§3King's Valley"],Name:"§b§lTempest Caller"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Shadowborn Boots''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:2s,id:34s},{lvl:2s,id:2s}],display:{Lore:["§bLeather Armor","§eKing's Valley : Rare","§3King's Valley"],color:0,Name:"§1§lShadowborn Boots"},AttributeModifiers:[{UUIDMost:27244509153028163l,UUIDLeast:28582544481897959l,Amount:0.1d,Slot:"feet",AttributeName:"generic.attackDamage",Operation:1,Name:"generic.attackDamage"},{UUIDMost:28562665029432653l,UUIDLeast:46011597873607935l,Amount:1d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Voidguard''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:0s},{lvl:2s,id:34s}],display:{Lore:["§bLeather Armor","§eKing's Valley : Rare","§3King's Valley"],color:3287104,Name:"§1§lVoidguard"},AttributeModifiers:[{UUIDMost:71061793700771916l,UUIDLeast:70921921889626742l,Amount:0.05d,Slot:"chest",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:5618170327124803l,UUIDLeast:67318597315435972l,Amount:3d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Kismet's Blessing''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:3s,id:34s}],display:{Lore:["§bLeather Armor","§eKing's Valley : Rare","§3King's Valley"],color:65493,Name:"§b§lKismet's Blessing"},AttributeModifiers:[{UUIDMost:-6900745281224160306l,UUIDLeast:-4828553848378685989l,Amount:3.0d,Slot:"head",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"},{UUIDMost:1116995255491055008l,UUIDLeast:-6766107056483247837l,Amount:1.0d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_hoe",
			"name":u'''Brimstone Scythe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:5s,id:16s},{lvl:4s,id:34s},{lvl:2s,id:19s},{lvl:5s,id:20s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§3King's Valley","","§7When in main hand:","§7 2 Attack Speed","§7 6 Attack Damage"],Name:"§4§lBrimstone Scythe"},AttributeModifiers:[{UUIDMost:6433490404641818817l,UUIDLeast:-8593178968434576189l,Amount:-2.0d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"Modifier"},{UUIDMost:3288944914052894654l,UUIDLeast:-5839775210248136997l,Amount:2.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Guardian Hide Boots''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:1s,id:70s},{lvl:3s,id:7s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Uncommon"],color:10599120,Name:"§fGuardian Hide Boots"},AttributeModifiers:[{UUIDMost:290399l,UUIDLeast:1103793l,Amount:0.75d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Guardian Hide Pants''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:1s,id:70s},{lvl:3s,id:7s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Uncommon"],color:10599120,Name:"§fGuardian Hide Pants"},AttributeModifiers:[{UUIDMost:280399l,UUIDLeast:1003793l,Amount:1.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Guardian Hide Vest''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:1s,id:70s},{lvl:3s,id:7s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Uncommon"],color:10599120,Name:"§fGuardian Hide Vest"},AttributeModifiers:[{UUIDMost:270399l,UUIDLeast:903793l,Amount:1.5d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Guardian Hide Helm''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:1s,id:70s},{lvl:3s,id:7s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Uncommon"],color:10599120,Name:"§fGuardian Hide Helm"},AttributeModifiers:[{UUIDMost:260399l,UUIDLeast:803793l,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Offering's Robe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:2s,id:4s},{lvl:1s,id:34s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Uncommon"],color:16719872,Name:"§fOffering's Robe"},AttributeModifiers:[{UUIDMost:7895314803459967566l,UUIDLeast:-4684285381480027934l,Amount:0.75d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Offering's Robe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:2s,id:4s},{lvl:1s,id:34s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Uncommon"],color:16719872,Name:"§fOffering's Robe"},AttributeModifiers:[{UUIDMost:2421209759494129265l,UUIDLeast:-7639468242547147097l,Amount:1.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Offering's Robe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:2s,id:4s},{lvl:1s,id:34s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Uncommon"],color:16719872,Name:"§fOffering's Robe"},AttributeModifiers:[{UUIDMost:4172809477985159313l,UUIDLeast:-6315940985289442365l,Amount:1.5d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Offering's Hood''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:2s,id:4s},{lvl:1s,id:34s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Uncommon"],color:16719872,Name:"§fOffering's Hood"},AttributeModifiers:[{UUIDMost:-1020269136855678533l,UUIDLeast:-8988064621405004682l,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"name":u'''Sacrificial Blade''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:1s,id:20s}],display:{Lore:["§8King's Valley : Uncommon"],Name:"§fSacrificial Blade"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"name":u'''Vicious Thorn''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:1s,id:70s}],display:{Lore:["§8King's Valley : Tier IV"],Name:"§fVicious Thorn"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"name":u'''Godwood Sword''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:17s},{lvl:2s,id:34s},{lvl:1s,id:19s},{lvl:2s,id:20s}],display:{Lore:["§8King's Valley : Tier IV"],Name:"§fGodwood Sword"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"name":u'''Druidic Broadsword''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:2s,id:34s},{lvl:2s,id:20s},{lvl:2s,id:22s}],display:{Lore:["§8King's Valley : Tier IV"],Name:"§fDruidic Broadsword"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"name":u'''Ponderous Branch''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:16s},{lvl:1s,id:17s},{lvl:4s,id:34s},{lvl:2s,id:19s}],display:{Lore:["§8King's Valley : Tier IV"],Name:"§fPonderous Branch"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"name":u'''Nest's Bane''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:32s},{lvl:1s,id:16s},{lvl:1s,id:17s},{lvl:1s,id:34s}],display:{Lore:["§8King's Valley : Tier IV"],Name:"§fNest's Bane"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"name":u'''Officer's Blade''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:1s,id:22s}],display:{Lore:["§8King's Valley : Tier IV"],Name:"§fOfficer's Blade"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"name":u'''Infernal Dagger''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:17s},{lvl:1s,id:19s},{lvl:2s,id:20s}],display:{Lore:["§8King's Valley : Tier IV"],Name:"§fInfernal Dagger"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"name":u'''Masterwork Sabre''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:16s},{lvl:5s,id:34s}],display:{Lore:["§8King's Valley : Tier IV"],Name:"§fMasterwork Sabre"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"name":u'''Duelist's Sword''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:51s}],HideFlags:1,display:{Lore:["§8King's Valley : Tier IV"],Name:"§fDuelist's Sword"},AttributeModifiers:[{UUIDMost:298381l,UUIDLeast:495523l,Amount:0.05d,Slot:"offhand",AttributeName:"generic.attackDamage",Operation:1,Name:"generic.attackDamage"},{UUIDMost:157078l,UUIDLeast:786990l,Amount:2d,Slot:"offhand",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"name":u'''Assassin's Dagger''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:51s}],HideFlags:1,display:{Lore:["§8King's Valley : Tier IV"],Name:"§fAssassin's Dagger"},AttributeModifiers:[{UUIDMost:743378l,UUIDLeast:575520l,Amount:0.15d,Slot:"offhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_axe",
			"name":u'''Falling Comet''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:16s},{lvl:1s,id:17s},{lvl:2s,id:34s},{lvl:3s,id:20s}],display:{Lore:["§8King's Valley : Tier IV"],Name:"§fFalling Comet"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_axe",
			"name":u'''Deforester''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:4s,id:32s},{lvl:3s,id:34s}],display:{Lore:["§8King's Valley : Tier IV"],Name:"§fDeforester"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"name":u'''Cutter''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:32s},{lvl:2s,id:34s}],display:{Lore:["§8King's Valley : Tier IV"],Name:"§fCutter"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"name":u'''Divine Cleaver''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:17s},{lvl:1s,id:21s}],display:{Lore:["§8King's Valley : Tier IV"],Name:"§fDivine Cleaver"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"name":u'''Battle Axe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:3s,id:34s}],display:{Lore:["§8King's Valley : Tier IV"],Name:"§fBattle Axe"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_pickaxe",
			"name":u'''Bluescourge Chisel''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:32s}],display:{Lore:["§8King's Valley : Tier IV"],Name:"§fBluescourge Chisel"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_pickaxe",
			"name":u'''Coal Devourer''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:34s},{lvl:4s,id:35s}],display:{Lore:["§8King's Valley : Tier IV"],Name:"§fCoal Devourer"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_pickaxe",
			"name":u'''Balanced Adze''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:32s},{lvl:1s,id:34s}],display:{Lore:["§8King's Valley : Tier IV"],Name:"§fBalanced Adze"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_pickaxe",
			"name":u'''Bountiful Chisel''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:35s}],display:{Lore:["§8King's Valley : Tier IV"],Name:"§fBountiful Chisel"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_hoe",
			"name":u'''Rebel's Scythe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:16s},{lvl:1s,id:17s},{lvl:2s,id:34s},{lvl:2s,id:21s}],HideFlags:2,display:{Lore:["§8King's Valley : Tier IV","§8","§7When in main hand:","§7 2 Attack Speed","§7 4 Attack Damage"],Name:"§rRebel's Scythe"},AttributeModifiers:[{UUIDMost:6433490404641818817l,UUIDLeast:-8593178968434576189l,Amount:-2.0d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"Modifier"},{UUIDMost:3288944914052894654l,UUIDLeast:-5839775210248136997l,Amount:2.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_hoe",
			"name":u'''Salubric Scythe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:16s},{lvl:2s,id:18s},{lvl:2s,id:34s}],HideFlags:2,display:{Lore:["§8King's Valley : Tier IV","§8","§7When in main hand:","§7 2 Attack Speed","§7 4 Attack Damage","§9","§7When in off hand:","§9 +3 Max Health"],Name:"§fSalubric Scythe"},AttributeModifiers:[{UUIDMost:6433490404641818817l,UUIDLeast:-8593178968434576189l,Amount:-2.0d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"Modifier"},{UUIDMost:3288944914052894654l,UUIDLeast:-5839775210248136997l,Amount:2.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"},{UUIDMost:7295232332495012583l,UUIDLeast:-7792231053812809931l,Amount:3.0d,Slot:"offhand",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:shield",
			"name":u'''Ironwrought Shield''',
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["§8King's Valley : Tier IV"],Name:"§fIronwrought Shield"},AttributeModifiers:[{UUIDMost:477084l,UUIDLeast:816028l,Amount:0.25d,Slot:"offhand",AttributeName:"generic.knockbackResistance",Operation:0,Name:"generic.knockbackResistance"}]}'''
		]
	],
	[
		{
			"id":"minecraft:shield",
			"name":u'''Spiked Buckler''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:19s}],HideFlags:2,display:{Lore:["§8King's Valley : Tier IV","§8","§7When in main hand:","§7 2.0 Attack Speed","§7 4 Attack Damage"],Name:"§fSpiked Buckler"},AttributeModifiers:[{UUIDMost:6962219233119978799l,UUIDLeast:-7099076830009706309l,Amount:3.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"},{UUIDMost:-4645625362179865008l,UUIDLeast:-5457813405958071294l,Amount:-2.0d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:bow",
			"name":u'''Pyromancer's Bow''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:50s},{lvl:3s,id:34s}],display:{Lore:["§8King's Valley : Tier IV"],Name:"§fPyromancer's Bow"}}'''
		]
	],
	[
		{
			"id":"minecraft:bow",
			"name":u'''Composite Bow''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:48s},{lvl:1s,id:49s}],display:{Lore:["§8King's Valley : Tier IV"],Name:"§fComposite Bow"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_shovel",
			"name":u'''Gardener''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:32s},{lvl:3s,id:34s}],display:{Lore:["§8King's Valley : Tier IV"],Name:"§fGardener"}}'''
		]
	],
	[
		{
			"id":"minecraft:stick",
			"name":u'''Journeyman's Staff''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:16s},{lvl:1s,id:19s},{lvl:2s,id:20s}],display:{Lore:["§8* Magic Wand *","§8King's Valley : Tier IV"],Name:"§fJourneyman's Staff"}}'''
		]
	],
	[
		{
			"id":"minecraft:bone",
			"name":u'''Shaman's Staff''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:4s,id:16s},{lvl:2s,id:18s},{lvl:1s,id:19s},{lvl:1s,id:71s}],display:{Lore:["§8* Magic Wand *","§8King's Valley : Tier IV"],Name:"§fShaman's Staff"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Cerulean Mage Hat''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:2s,id:1s},{lvl:1s,id:34s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier IV"],color:5214175,Name:"§fCerulean Mage Hat"},AttributeModifiers:[{UUIDMost:260399l,UUIDLeast:803793l,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Cerulean Mage Robes''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:2s,id:4s},{lvl:1s,id:34s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier IV"],color:5214175,Name:"§fCerulean Mage Robes"},AttributeModifiers:[{UUIDMost:270399l,UUIDLeast:903793l,Amount:1.5d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Cerulean Mage Robes''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:1s,id:34s},{lvl:2s,id:3s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier IV"],color:5214175,Name:"§fCerulean Mage Robes"},AttributeModifiers:[{UUIDMost:280399l,UUIDLeast:1003793l,Amount:1.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Cerulean Mage Robes''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:1s,id:34s},{lvl:2s,id:2s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier IV"],color:5214175,Name:"§fCerulean Mage Robes"},AttributeModifiers:[{UUIDMost:290399l,UUIDLeast:1103793l,Amount:0.75d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Molten Hood''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:5s,id:1s},{lvl:2s,id:34s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier IV"],color:16756736,Name:"§fMolten Hood"},AttributeModifiers:[{UUIDMost:260399l,UUIDLeast:803793l,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Molten Cloak''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:5s,id:1s},{lvl:2s,id:34s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier IV"],color:16756736,Name:"§fMolten Cloak"},AttributeModifiers:[{UUIDMost:270399l,UUIDLeast:903793l,Amount:1.5d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Molten Pants''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:5s,id:1s},{lvl:2s,id:34s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier IV"],color:16756736,Name:"§fMolten Pants"},AttributeModifiers:[{UUIDMost:280399l,UUIDLeast:1003793l,Amount:1.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Molten Boots''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:5s,id:1s},{lvl:2s,id:34s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier IV"],color:16756736,Name:"§fMolten Boots"},AttributeModifiers:[{UUIDMost:290399l,UUIDLeast:1103793l,Amount:0.75d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Choleric Helm''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:4s,id:34s},{lvl:5s,id:7s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier IV"],color:6356736,Name:"§fCholeric Helm"},AttributeModifiers:[{UUIDMost:260399l,UUIDLeast:803793l,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Choleric Cloak''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:4s,id:34s},{lvl:5s,id:7s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier IV"],color:6356736,Name:"§fCholeric Cloak"},AttributeModifiers:[{UUIDMost:270399l,UUIDLeast:903793l,Amount:1.5d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Choleric Leggings''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:4s,id:34s},{lvl:5s,id:7s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier IV"],color:6356736,Name:"§fCholeric Leggings"},AttributeModifiers:[{UUIDMost:280399l,UUIDLeast:1003793l,Amount:1.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Choleric Boots''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:4s,id:34s},{lvl:5s,id:7s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier IV"],color:6356736,Name:"§fCholeric Boots"},AttributeModifiers:[{UUIDMost:290399l,UUIDLeast:1103793l,Amount:0.75d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Heavy Leather Cap''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:4s,id:34s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier IV"],Name:"§fHeavy Leather Cap"},AttributeModifiers:[{UUIDMost:1199056757440006902l,UUIDLeast:-5031645011434854220l,Amount:0.12d,Slot:"head",AttributeName:"generic.knockbackResistance",Operation:0,Name:"Modifier"},{UUIDMost:-5675263151546941074l,UUIDLeast:-7630602400151360780l,Amount:1.0d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Heavy Leather Tunic''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:4s,id:34s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier IV"],Name:"§fHeavy Leather Tunic"},AttributeModifiers:[{UUIDMost:-7851645031876899907l,UUIDLeast:-7264920938634085936l,Amount:0.12d,Slot:"chest",AttributeName:"generic.knockbackResistance",Operation:0,Name:"Modifier"},{UUIDMost:-6308125112336758355l,UUIDLeast:-6141357313852679154l,Amount:3.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Heavy Leather Pants''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:4s,id:34s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier IV"],Name:"§fHeavy Leather Pants"},AttributeModifiers:[{UUIDMost:-5282638418670238374l,UUIDLeast:-7237081583653115127l,Amount:0.12d,Slot:"legs",AttributeName:"generic.knockbackResistance",Operation:0,Name:"Modifier"},{UUIDMost:-2983299289300778334l,UUIDLeast:-4622743005847896684l,Amount:2.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Heavy Leather Boots''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:4s,id:34s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier IV"],Name:"§fHeavy Leather Boots"},AttributeModifiers:[{UUIDMost:-6971162542843608331l,UUIDLeast:-9087580478696796047l,Amount:0.12d,Slot:"feet",AttributeName:"generic.knockbackResistance",Operation:0,Name:"Modifier"},{UUIDMost:1131969840074081731l,UUIDLeast:-7625908944711840236l,Amount:1.0d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Brigand's Coif''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:4s},{lvl:1s,id:34s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier IV"],color:8425600,Name:"§fBrigand's Coif"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Brigand's Tunic''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:4s},{lvl:1s,id:34s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier IV"],color:8425600,Name:"§fBrigand's Tunic"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Brigand's Trousers''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:4s},{lvl:1s,id:34s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier IV"],color:8425600,Name:"§fBrigand's Trousers"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Brigand's Shoes''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:4s},{lvl:1s,id:34s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier IV"],color:8425600,Name:"§fBrigand's Shoes"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Gemcrust Coif''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:1s,id:1s},{lvl:1s,id:71s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier IV"],color:16711935,Name:"§fGemcrust Coif"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Gemcrust Vest''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:1s,id:1s},{lvl:1s,id:71s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier IV"],color:16711935,Name:"§fGemcrust Vest"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Gemcrust Pants''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:1s,id:1s},{lvl:1s,id:71s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier IV"],color:16711935,Name:"§fGemcrust Pants"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Gemcrust Shoes''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:1s,id:1s},{lvl:1s,id:71s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier IV"],color:16711935,Name:"§fGemcrust Shoes"}}'''
		]
	],
	[
		{
			"id":"minecraft:shield",
			"name":u'''Rusty Shield''',
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fRusty Shield"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Cloth Cap''',
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["§9Cloth Armor"],color:16768959,Name:"§fCloth Cap"},AttributeModifiers:[{UUIDMost:260399l,UUIDLeast:803793l,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Cloth Shirt''',
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["§9Cloth Armor"],color:16768959,Name:"§fCloth Shirt"},AttributeModifiers:[{UUIDMost:270399l,UUIDLeast:903793l,Amount:1.5d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Cloth Pants''',
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["§9Cloth Armor"],color:16768959,Name:"§fCloth Pants"},AttributeModifiers:[{UUIDMost:280399l,UUIDLeast:1003793l,Amount:1.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Cloth Shoes''',
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["§9Cloth Armor"],color:16768959,Name:"§fCloth Shoes"},AttributeModifiers:[{UUIDMost:290399l,UUIDLeast:1103793l,Amount:0.75d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"name":u'''The Ravager''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:2s,id:34s},{lvl:2s,id:19s}],display:{Lore:["§eKing's Valley : Rare","§6Fallen Menagerie","§8There is nothing more fierce","§8than a Jaguar enraged."],Name:"§3§lThe Ravager"}}'''
		]
	],
	[
		{
			"id":"minecraft:stick",
			"name":u'''Shapeshifter's Wand''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:16s},{lvl:1s,id:19s}],display:{Lore:["§8* Magic Wand *","§eKing's Valley : Rare","§6Fallen Menagerie","§8The Lunatics transform when","§8the time is right."],Name:"§2§lShapeshifter's Wand"},AttributeModifiers:[{UUIDMost:-6875693728534016758l,UUIDLeast:-4803955762994063049l,Amount:0.15d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"},{UUIDMost:-8999057979425928886l,UUIDLeast:-6793904886171895238l,Amount:5.0d,Slot:"offhand",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Boots of Vitality''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:5s,id:34s}],display:{Lore:["§bLeather Armor","§eKing's Valley : Rare","§6Fallen Menagerie","§8Worn by jailors to keep them healthy.","§8These boots exude an odd aura."],color:4521728,Name:"§2§lBoots of Vitality"},AttributeModifiers:[{UUIDMost:47288061869184321l,UUIDLeast:31209886326295287l,Amount:2.0d,Slot:"feet",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"},{UUIDMost:67642567772660032l,UUIDLeast:69671216077991960l,Amount:1.0d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Cultist's Robe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:1s,id:10s},{lvl:1s,id:70s}],display:{Lore:["§bLeather Armor","§eKing's Valley : Rare","§6Fallen Menagerie","§8Step into line. Join us..."],color:8857897,Name:"§d§lCultist's Robe"},AttributeModifiers:[{UUIDMost:42188985747894336l,UUIDLeast:58789894930970307l,Amount:3.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:26258638605899072l,UUIDLeast:65484620952030853l,Amount:0.1d,Slot:"chest",AttributeName:"generic.attackSpeed",Operation:1,Name:"generic.attackSpeed"},{UUIDMost:-7523851246731247303l,UUIDLeast:-6521249364252678471l,Amount:1.0d,Slot:"chest",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:quartz",
			"name":u'''Purified Claw''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:17s},{lvl:1s,id:19s}],display:{Lore:["§eKing's Valley : Rare","§6Fallen Menagerie","§8The claws of a Jaguar,","§8The soul of the Jungle."],Name:"§9§lPurified Claw"},AttributeModifiers:[{UUIDMost:-980822700820772406l,UUIDLeast:-6364738682707359156l,Amount:2.0d,Slot:"mainhand",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"name":u'''Wildthrasher''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:16s},{lvl:3s,id:34s},{lvl:1s,id:20s}],display:{Lore:["§eKing's Valley : Rare","§6Fallen Menagerie","§8Nature strikes back as the Beastmen howl"],Name:"§a§lWildthrasher"}}'''
		]
	],
	[
		{
			"id":"minecraft:bow",
			"name":u'''Bonepiercer''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:48s},{lvl:1s,id:49s},{lvl:1s,id:50s},{lvl:1s,id:34s}],display:{Lore:["§eKing's Valley : Rare","§6Fallen Menagerie","§8Pierce the flesh, and the bones will follow","§8 -Hawk Proverb"],Name:"§f§lBonepiercer"}}'''
		]
	],
	[
		{
			"id":"minecraft:golden_axe",
			"name":u'''Arachnobane''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:4s,id:18s},{lvl:7s,id:34s},{lvl:1s,id:19s},{lvl:1s,id:20s}],display:{Lore:["§eKing's Valley : Rare","§6Fallen Menagerie","§8It seems there's a reason there is","§8no Spider tribe."],Name:"§d§lArachnobane"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Thaumaturge's Robes''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:8s},{lvl:3s,id:0s}],display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:7833547,Name:"§fThaumaturge's Robes"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Thaumaturge's Robes''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:0s}],display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:7833547,Name:"§fThaumaturge's Robes"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Thaumaturge's Robes''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:0s}],display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:7833547,Name:"§fThaumaturge's Robes"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Thaumaturge's Hood''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:0s},{lvl:2s,id:5s},{lvl:1s,id:6s}],display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:7833547,Name:"§fThaumaturge's Hood"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"name":u'''Bloody Thorn''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:1s,id:19s},{lvl:1s,id:70s}],display:{Lore:["§8King's Valley : Tier V"],Name:"§aBloody Thorn"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"name":u'''Eternal Crescent''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:16s},{lvl:1s,id:70s},{lvl:3s,id:22s}],display:{Lore:["§8King's Valley : Tier V"],Name:"§aEternal Crescent"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"name":u'''Macuahuitl''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:5s,id:16s}],display:{Lore:["§8King's Valley : Tier V"],Name:"§aMacuahuitl"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"name":u'''Reliable Longsword''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:1s,id:34s},{lvl:2s,id:22s}],display:{Lore:["§8King's Valley : Tier V"],Name:"§aReliable Longsword"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"name":u'''Versatile Cutlass''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:17s},{lvl:1s,id:18s},{lvl:1s,id:34s},{lvl:1s,id:22s}],display:{Lore:["§8King's Valley : Tier V"],Name:"§aVersatile Cutlass"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"name":u'''Molten Rapier''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:16s},{lvl:1s,id:17s},{lvl:2s,id:20s}],display:{Lore:["§8King's Valley : Tier V"],Name:"§aMolten Rapier"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"name":u'''Polished Gladius''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:16s},{lvl:3s,id:34s},{lvl:3s,id:19s}],display:{Lore:["§8King's Valley : Tier V"],Name:"§aPolished Gladius"}}'''
		]
	],
	[
		{
			"id":"minecraft:golden_sword",
			"name":u'''Eldritch Blade''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:51s}],HideFlags:1,display:{Lore:["§8King's Valley : Tier V"],Name:"§aEldritch Blade"},AttributeModifiers:[{UUIDMost:81922l,UUIDLeast:79311l,Amount:0.15d,Slot:"offhand",AttributeName:"generic.knockbackResistance",Operation:0,Name:"generic.knockbackResistance"},{UUIDMost:298381l,UUIDLeast:495523l,Amount:0.2d,Slot:"offhand",AttributeName:"generic.attackDamage",Operation:1,Name:"generic.attackDamage"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"name":u'''Scout's Companion''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:51s}],HideFlags:1,display:{Lore:["§8King's Valley : Tier V"],Name:"§aScout's Companion"},AttributeModifiers:[{UUIDMost:637136l,UUIDLeast:234308l,Amount:2d,Slot:"offhand",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"},{UUIDMost:743378l,UUIDLeast:575520l,Amount:0.1d,Slot:"offhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"name":u'''Blessed Axe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:32s},{lvl:4s,id:34s}],display:{Lore:["§8King's Valley : Tier V"],Name:"§aBlessed Axe"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"name":u'''Crushing Mace''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:1s,id:17s},{lvl:1s,id:34s}],display:{Lore:["§8King's Valley : Tier V"],Name:"§aCrushing Mace"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"name":u'''Phoenix Axe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:34s},{lvl:2s,id:19s},{lvl:3s,id:20s}],display:{Lore:["§8King's Valley : Tier V"],Name:"§aPhoenix Axe"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"name":u'''Soulhammer''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:16s},{lvl:1s,id:19s},{lvl:1s,id:70s}],display:{Lore:["§8King's Valley : Tier V"],Name:"§aSoulhammer"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_pickaxe",
			"name":u'''Evanescent''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:4s,id:32s},{lvl:1s,id:71s}],display:{Lore:["§8King's Valley : Tier V"],Name:"§aEvanescent"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_pickaxe",
			"name":u'''Undying Chisel''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:32s},{lvl:1s,id:70s}],display:{Lore:["§8King's Valley : Tier V"],Name:"§aUndying Chisel"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_pickaxe",
			"name":u'''Truerune Pick''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:34s},{lvl:4s,id:35s}],display:{Lore:["§8King's Valley : Tier V"],Name:"§aTruerune Pick"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_shovel",
			"name":u'''Undying Trowel''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:32s},{lvl:1s,id:70s}],display:{Lore:["§8King's Valley : Tier V"],Name:"§aUndying Trowel"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_hoe",
			"name":u'''Executioner's Scythe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:16s},{lvl:2s,id:17s},{lvl:3s,id:34s},{lvl:2s,id:21s}],HideFlags:2,display:{Lore:["§8King's Valley : Tier V","§8","§7When in main hand:","§7 2 Attack Speed","§7 4 Attack Damage"],Name:"§aExecutioner's Scythe"},AttributeModifiers:[{UUIDMost:6433490404641818817l,UUIDLeast:-8593178968434576189l,Amount:-2.0d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"Modifier"},{UUIDMost:3288944914052894654l,UUIDLeast:-5839775210248136997l,Amount:2.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_hoe",
			"name":u'''Windborn Scythe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:16s},{lvl:2s,id:34s},{lvl:2s,id:19s}],HideFlags:2,display:{Lore:["§8King's Valley : Tier V","§8","§7When in main hand:","§7 2 Attack Speed","§7 5 Attack Damage","§l","§7When in off hand:","§9 +12% Speed"],Name:"§aWindborn Scythe"},AttributeModifiers:[{UUIDMost:6433490404641818817l,UUIDLeast:-8593178968434576189l,Amount:-2.0d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"Modifier"},{UUIDMost:3288944914052894654l,UUIDLeast:-5839775210248136997l,Amount:2.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"},{UUIDMost:4741036782941654280l,UUIDLeast:-8811754788537177381l,Amount:0.12d,Slot:"offhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:shield",
			"name":u'''Swiftwood Buckler''',
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["§8King's Valley : Tier V"],Name:"§aSwiftwood Buckler"},AttributeModifiers:[{UUIDMost:3799174595893871670l,UUIDLeast:-8604776829862673178l,Amount:0.05d,Slot:"offhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:shield",
			"name":u'''Soulguard''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:70s}],display:{Lore:["§8King's Valley : Tier V"],Name:"§aSoulguard"}}'''
		]
	],
	[
		{
			"id":"minecraft:bow",
			"name":u'''Blazing Crossbow''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:49s},{lvl:1s,id:50s},{lvl:1s,id:34s}],display:{Lore:["§8King's Valley : Tier V"],Name:"§aBlazing Crossbow"}}'''
		]
	],
	[
		{
			"id":"minecraft:bow",
			"name":u'''Korbaran Shortbow''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:48s}],display:{Lore:["§8King's Valley : Tier V"],Name:"§aKorbaran Shortbow"}}'''
		]
	],
	[
		{
			"id":"minecraft:fishing_rod",
			"name":u'''Mermaid's Touch''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:4s,id:62s},{lvl:1s,id:70s}],display:{Lore:["§8King's Valley : Tier V"],Name:"§aMermaid's Touch"}}'''
		]
	],
	[
		{
			"id":"minecraft:blaze_rod",
			"name":u'''Pyromancer's Staff''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:16s},{lvl:1s,id:17s},{lvl:3s,id:20s}],display:{Lore:["§8* Magic Wand *","§8King's Valley : Tier V"],Name:"§aPyromancer's Staff"}}'''
		]
	],
	[
		{
			"id":"minecraft:stick",
			"name":u'''Wand of Storms''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:16s},{lvl:3s,id:19s},{lvl:1s,id:20s}],display:{Lore:["§8* Magic Wand *","§8King's Valley : Tier V"],Name:"§aWand of Storms"},AttributeModifiers:[{UUIDMost:120619l,UUIDLeast:372763l,Amount:0.07d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Nereid Cap''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:1s,id:34s},{lvl:1s,id:4s},{lvl:1s,id:5s},{lvl:1s,id:6s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier V"],color:1073407,Name:"§aNereid Cap"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Nereid Tunic''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:8s},{lvl:2s,id:0s},{lvl:1s,id:34s},{lvl:1s,id:4s},{lvl:1s,id:5s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier V"],color:1073407,Name:"§aNereid Tunic"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Nereid Leggings''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:8s},{lvl:2s,id:0s},{lvl:1s,id:34s},{lvl:1s,id:4s},{lvl:1s,id:5s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier V"],color:1073407,Name:"§aNereid Leggings"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Nereid Sandals''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:8s},{lvl:2s,id:0s},{lvl:1s,id:34s},{lvl:1s,id:4s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier V"],color:1073407,Name:"§aNereid Sandals"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Hardened Leather Cap''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:3s,id:34s},{lvl:3s,id:3s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier V"],color:10506272,Name:"§aHardened Leather Cap"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Hardened Leather Tunic''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:3s,id:34s},{lvl:3s,id:3s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier V"],color:10506272,Name:"§aHardened Leather Tunic"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Hardened Leather Pants''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:3s,id:34s},{lvl:3s,id:3s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier V"],color:10506272,Name:"§aHardened Leather Pants"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Hardened Leather Boots''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:3s,id:34s},{lvl:3s,id:3s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier V"],color:10506272,Name:"§aHardened Leather Boots"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Scout's Leathers''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:2s,id:4s},{lvl:1s,id:34s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier V"],color:10240,Name:"§aScout's Leathers"},AttributeModifiers:[{UUIDMost:692165l,UUIDLeast:277777l,Amount:0.03d,Slot:"head",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:692165l,UUIDLeast:277777l,Amount:1.0d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Scout's Leathers''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:2s,id:4s},{lvl:1s,id:34s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier V"],color:10240,Name:"§aScout's Leathers"},AttributeModifiers:[{UUIDMost:752165l,UUIDLeast:297777l,Amount:0.03d,Slot:"chest",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:752165l,UUIDLeast:297777l,Amount:3.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Scout's Leathers''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:2s,id:4s},{lvl:1s,id:34s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier V"],color:10240,Name:"§aScout's Leathers"},AttributeModifiers:[{UUIDMost:732165l,UUIDLeast:337777l,Amount:0.03d,Slot:"legs",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:764261l,UUIDLeast:337777l,Amount:2.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Scout's Leathers''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:1s,id:34s},{lvl:3s,id:2s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier V"],color:10240,Name:"§aScout's Leathers"},AttributeModifiers:[{UUIDMost:632165l,UUIDLeast:237777l,Amount:0.03d,Slot:"feet",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:632165l,UUIDLeast:237777l,Amount:1.0d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Soulleather Veil''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:1s,id:70s},{lvl:1s,id:71s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier V"],color:16777215,Name:"§aSoulleather Veil"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Soulleather Cloak''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:1s,id:70s},{lvl:1s,id:71s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier V"],color:16777215,Name:"§aSoulleather Cloak"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Soulleather Robe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:1s,id:70s},{lvl:1s,id:71s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier V"],color:16777215,Name:"§aSoulleather Robe"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Soulleather Shoes''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:1s,id:70s},{lvl:1s,id:71s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier V"],color:16777215,Name:"§aSoulleather Shoes"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Viridian Mage Hat''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:0s},{lvl:2s,id:1s},{lvl:1s,id:34s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier V"],color:1105920,Name:"§aViridian Mage Hat"},AttributeModifiers:[{UUIDMost:260399l,UUIDLeast:803793l,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Viridian Mage Robes''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:0s},{lvl:2s,id:4s},{lvl:1s,id:34s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier V"],color:1105920,Name:"§aViridian Mage Robes"},AttributeModifiers:[{UUIDMost:270399l,UUIDLeast:903793l,Amount:1.5d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Viridian Mage Robes''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:0s},{lvl:1s,id:34s},{lvl:2s,id:3s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier V"],color:1105920,Name:"§aViridian Mage Robes"},AttributeModifiers:[{UUIDMost:280399l,UUIDLeast:1003793l,Amount:1.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Viridian Mage Robes''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:0s},{lvl:1s,id:34s},{lvl:2s,id:2s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier V"],color:1105920,Name:"§aViridian Mage Robes"},AttributeModifiers:[{UUIDMost:290399l,UUIDLeast:1103793l,Amount:0.75d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Dualsun Hood''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:2s,id:1s},{lvl:4s,id:34s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier V"],color:16773120,Name:"§aDualsun Hood"},AttributeModifiers:[{UUIDMost:3410419544452450231l,UUIDLeast:-5482257300623082461l,Amount:1.0d,Slot:"head",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"},{UUIDMost:-7224057274751827505l,UUIDLeast:-6818848218977621316l,Amount:1.0d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Dualsun Cloak''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:2s,id:1s},{lvl:4s,id:34s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier V"],color:16773120,Name:"§aDualsun Cloak"},AttributeModifiers:[{UUIDMost:-895514479119021132l,UUIDLeast:-6538819203639619634l,Amount:1.0d,Slot:"chest",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"},{UUIDMost:-845493126176553328l,UUIDLeast:-6934174944561962248l,Amount:3.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Dualsun Robe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:2s,id:1s},{lvl:4s,id:34s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier V"],color:16773120,Name:"§aDualsun Robe"},AttributeModifiers:[{UUIDMost:-3224490652004365870l,UUIDLeast:-8490984991565425765l,Amount:1.0d,Slot:"legs",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"},{UUIDMost:5309333526597813727l,UUIDLeast:-8167831153772325916l,Amount:2.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Dualsun Shoes''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:2s,id:1s},{lvl:4s,id:34s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier V"],color:16773120,Name:"§aDualsun Shoes"},AttributeModifiers:[{UUIDMost:-1243331979226886434l,UUIDLeast:-7990746417674087296l,Amount:1.0d,Slot:"feet",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"},{UUIDMost:-5110990380665716018l,UUIDLeast:-5231967837950058796l,Amount:1.0d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"name":u'''Ironwood Blade''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:34s}],display:{Lore:["§8King's Valley : Tier I"],Name:"§fIronwood Blade"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"name":u'''Carved Dagger''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:16s}],display:{Lore:["§8King's Valley : Tier I"],Name:"§fCarved Dagger"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"name":u'''Oaken Broadsword''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:34s},{lvl:1s,id:22s}],display:{Lore:["§8King's Valley : Tier I"],Name:"§fOaken Broadsword"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"name":u'''Scorching Splinter''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:20s},{lvl:1s,id:19s}],display:{Lore:["§8King's Valley : Tier I"],Name:"§fScorching Splinter"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"name":u'''Flensing Knife''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:18s}],display:{Lore:["§8King's Valley : Tier I"],Name:"§fFlensing Knife"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"name":u'''Hunter's Stake''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:17s},{lvl:1s,id:34s}],display:{Lore:["§8King's Valley : Tier I"],Name:"§fHunter's Stake"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"name":u'''Serrated Shiv''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:51s}],HideFlags:1,display:{Lore:["§8King's Valley : Tier I"],Name:"§fSerrated Shiv"},AttributeModifiers:[{UUIDMost:298381l,UUIDLeast:495523l,Amount:0.1d,Slot:"offhand",AttributeName:"generic.attackDamage",Operation:1,Name:"generic.attackDamage"}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_axe",
			"name":u'''Swiftwood Axe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:32s}],display:{Lore:["§8King's Valley : Tier I"],Name:"§fSwiftwood Axe"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_axe",
			"name":u'''Squire's Hammer''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:1s,id:34s},{lvl:1s,id:19s}],display:{Lore:["§8King's Valley : Tier I"],Name:"§fSquire's Hammer"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_axe",
			"name":u'''Smoldering Hatchet''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:34s},{lvl:1s,id:19s},{lvl:1s,id:20s}],display:{Lore:["§8King's Valley : Tier I"],Name:"§fSmoldering Hatchet"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_pickaxe",
			"name":u'''Swiftwood Pickaxe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:32s},{lvl:2s,id:34s}],display:{Lore:["§8King's Valley : Tier I"],Name:"§fSwiftwood Pickaxe"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_pickaxe",
			"name":u'''Lucky Pick''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:35s}],display:{Lore:["§8King's Valley : Tier I"],Name:"§fLucky Pick"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_pickaxe",
			"name":u'''Ironwood Pick''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:34s}],display:{Lore:["§8King's Valley : Tier I"],Name:"§fIronwood Pick"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_shovel",
			"name":u'''Swiftwood Shovel''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:32s}],display:{Lore:["§8King's Valley : Tier I"],Name:"§fSwiftwood Shovel"}}'''
		]
	],
	[
		{
			"id":"minecraft:fishing_rod",
			"name":u'''Novice's Fishing Rod''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:62s},{lvl:1s,id:34s}],display:{Lore:["§8King's Valley : Tier I"],Name:"§fNovice's Fishing Rod"}}'''
		]
	],
	[
		{
			"id":"minecraft:stick",
			"name":u'''Weak Wand''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:20s},{lvl:1s,id:19s}],display:{Lore:["§8* Magic Wand *","§8King's Valley : Tier I"],Name:"§fWeak Wand"}}'''
		]
	],
	[
		{
			"id":"minecraft:shield",
			"name":u'''Weak Shield''',
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["§8King's Valley : Tier I"],Name:"§fWeak Shield"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Sturdy Cloth Cap''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:34s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier I"],color:16768959,Name:"§fSturdy Cloth Cap"},AttributeModifiers:[{UUIDMost:260399l,UUIDLeast:803793l,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Sturdy Cloth Shirt''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:34s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier I"],color:16768959,Name:"§fSturdy Cloth Shirt"},AttributeModifiers:[{UUIDMost:270399l,UUIDLeast:903793l,Amount:1.5d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Sturdy Cloth Pants''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:34s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier I"],color:16768959,Name:"§fSturdy Cloth Pants"},AttributeModifiers:[{UUIDMost:280399l,UUIDLeast:1003793l,Amount:1.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Sturdy Cloth Shoes''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:34s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier I"],color:16768959,Name:"§fSturdy Cloth Shoes"},AttributeModifiers:[{UUIDMost:290399l,UUIDLeast:1103793l,Amount:0.75d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Infused Cloth Helm''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier I"],color:16752543,Name:"§fInfused Cloth Helm"},AttributeModifiers:[{UUIDMost:260399l,UUIDLeast:803793l,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Infused Cloth Cloak''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier I"],color:16752543,Name:"§fInfused Cloth Cloak"},AttributeModifiers:[{UUIDMost:270399l,UUIDLeast:903793l,Amount:1.5d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Infused Cloth Leggings''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier I"],color:16752543,Name:"§fInfused Cloth Leggings"},AttributeModifiers:[{UUIDMost:280399l,UUIDLeast:1003793l,Amount:1.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Infused Cloth Shoes''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier I"],color:16752543,Name:"§fInfused Cloth Shoes"},AttributeModifiers:[{UUIDMost:290399l,UUIDLeast:1103793l,Amount:0.75d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Padded Cloth Coif''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:4s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier I"],color:10461087,Name:"§fPadded Cloth Coif"},AttributeModifiers:[{UUIDMost:260399l,UUIDLeast:803793l,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Padded Cloth Tunic''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:4s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier I"],color:10461087,Name:"§fPadded Cloth Tunic"},AttributeModifiers:[{UUIDMost:270399l,UUIDLeast:903793l,Amount:1.5d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Padded Cloth Trousers''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:4s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier I"],color:10461087,Name:"§fPadded Cloth Trousers"},AttributeModifiers:[{UUIDMost:280399l,UUIDLeast:1003793l,Amount:1.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Padded Cloth Boots''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:4s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier I"],color:10461087,Name:"§fPadded Cloth Boots"},AttributeModifiers:[{UUIDMost:290399l,UUIDLeast:1103793l,Amount:0.75d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Leafweave Veil''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:1s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier I"],color:12582847,Name:"§fLeafweave Veil"},AttributeModifiers:[{UUIDMost:260399l,UUIDLeast:803793l,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Leafweave Vest''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:1s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier I"],color:12582847,Name:"§fLeafweave Vest"},AttributeModifiers:[{UUIDMost:270399l,UUIDLeast:903793l,Amount:1.5d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Leafweave Trousers''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:1s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier I"],color:12582847,Name:"§fLeafweave Trousers"},AttributeModifiers:[{UUIDMost:280399l,UUIDLeast:1003793l,Amount:1.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Leafweave Sandals''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:1s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier I"],color:12582847,Name:"§fLeafweave Sandals"},AttributeModifiers:[{UUIDMost:290399l,UUIDLeast:1103793l,Amount:0.75d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Binding Coif''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:1s,id:4s},{lvl:1s,id:10s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier I"],color:4194304,Name:"§fBinding Coif"},AttributeModifiers:[{UUIDMost:260399l,UUIDLeast:803793l,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Binding Robes''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:1s,id:4s},{lvl:1s,id:10s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier I"],color:4194304,Name:"§fBinding Robes"},AttributeModifiers:[{UUIDMost:270399l,UUIDLeast:903793l,Amount:1.5d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Binding Robes''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:1s,id:4s},{lvl:1s,id:10s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier I"],color:4194304,Name:"§fBinding Robes"},AttributeModifiers:[{UUIDMost:280399l,UUIDLeast:1003793l,Amount:1.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Binding Boots''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:1s,id:4s},{lvl:1s,id:10s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier I"],color:4194304,Name:"§fBinding Boots"},AttributeModifiers:[{UUIDMost:290399l,UUIDLeast:1103793l,Amount:0.75d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Hobnailed Helm''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:3s},{lvl:1s,id:7s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier I"],color:7393328,Name:"§fHobnailed Helm"},AttributeModifiers:[{UUIDMost:260399l,UUIDLeast:803793l,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Hobnailed Vest''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:3s},{lvl:1s,id:7s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier I"],color:7393328,Name:"§fHobnailed Vest"},AttributeModifiers:[{UUIDMost:270399l,UUIDLeast:903793l,Amount:1.5d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Hobnailed Leggings''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:3s},{lvl:1s,id:7s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier I"],color:7393328,Name:"§fHobnailed Leggings"},AttributeModifiers:[{UUIDMost:280399l,UUIDLeast:1003793l,Amount:1.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Hobnailed Boots''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:3s},{lvl:1s,id:7s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier I"],color:7393328,Name:"§fHobnailed Boots"},AttributeModifiers:[{UUIDMost:290399l,UUIDLeast:1103793l,Amount:0.75d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_hoe",
			"name":u'''Weak Scythe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:34s},{lvl:1s,id:21s}],HideFlags:2,display:{Lore:["§8King's Valley : Tier I","§8","§7When in main hand:","§7 2 Attack Speed","§7 3 Attack Damage"],Name:"§rWeak Scythe"},AttributeModifiers:[{UUIDMost:6433490404641818817l,UUIDLeast:-8593178968434576189l,Amount:-2.0d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"Modifier"},{UUIDMost:3288944914052894654l,UUIDLeast:-5839775210248136997l,Amount:2.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"name":u'''Soulcrusher''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:8s,id:16s},{lvl:3s,id:34s}],display:{Lore:["§eKing's Valley : Rare","§5Plagueroot Temple","§8Crush the body, crush the soul","§8crush the life that makes them whole."],Name:"§6§lSoulcrusher"}}'''
		]
	],
	[
		{
			"id":"minecraft:golden_sword",
			"name":u'''Doom's Edge''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:5s,id:16s},{lvl:2s,id:34s},{lvl:1s,id:70s},{lvl:4s,id:22s},{lvl:1s,id:71s}],display:{Lore:["§eKing's Valley : Rare","§5Plagueroot Temple","§8Those sent into the temple were","§8doomed from the start."],Name:"§6§lDoom's Edge"}}'''
		]
	],
	[
		{
			"id":"minecraft:golden_hoe",
			"name":u'''Reaper's Harvest''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:4s,id:17s},{lvl:1s,id:70s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§5Plagueroot Temple","§8Death stalked the halls of","§8the Plagueroot Temple.","§7","§7When in main hand:","§7 1 Attack Speed","§7 3 Attack Damage"],Name:"§6§lReaper's Harvest"},AttributeModifiers:[{UUIDMost:8976644567604022855l,UUIDLeast:-7318916035691686042l,Amount:-3.0d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"Modifier"},{UUIDMost:7551800705775586544l,UUIDLeast:-5250539558224500715l,Amount:2.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:totem_of_undying",
			"name":u'''Idol of Immortality''',
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["§eKing's Valley : Rare","§fWhen you are about to die, this item provides","§fAbsorption and Regeneration, destroying itself","§fin the process.","§5Plagueroot Temple","§8What good is eternal life when you cannot leave?"],Name:"§6§lIdol of Immortality"},AttributeModifiers:[{UUIDMost:6936855416015769157l,UUIDLeast:-5146628686682897060l,Amount:3.0d,Slot:"offhand",AttributeName:"generic.armor",Operation:0,Name:"Modifier"},{UUIDMost:-4476995786822302589l,UUIDLeast:-4856746282580489681l,Amount:1.0d,Slot:"offhand",AttributeName:"generic.armorToughness",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:shield",
			"name":u'''Tlaxan Bulwark''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:34s}],HideFlags:32,BlockEntityTag:{Base:2,Patterns:[{Color:0,Pattern:"gru"},{Color:0,Pattern:"cre"},{Color:0,Pattern:"flo"},{Color:0,Pattern:"moj"},{Color:0,Pattern:"tts"},{Color:0,Pattern:"bts"}]},display:{Lore:["§eKing's Valley : Rare","§5Plagueroot Temple","§8Shields are no good to the dead"],Name:"§2§lTlaxan Bulwark"},AttributeModifiers:[{UUIDMost:8279654741628239l,UUIDLeast:50644245966137402l,Amount:2.0d,Slot:"offhand",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Basilisk Scales''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:3s,id:34s}],display:{Lore:["§eKing's Valley : Rare","§5Plagueroot Temple","§8Hide of ancient beasts, wracked","§8with a sickness beyond death."],color:54286,Name:"§2§lBasilisk Scales"},AttributeModifiers:[{UUIDMost:1217047145548364l,UUIDLeast:62197310443051283l,Amount:4.0d,Slot:"chest",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Plaguebringer''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:1s,id:34s},{lvl:1s,id:70s},{lvl:4s,id:7s}],display:{Lore:["§bLeather Armor","§eKing's Valley : Rare","§5Plagueroot Temple","§8There is sickness in the depths.","§8Now it travels with you."],color:283658,Name:"§2§lPlaguebringer"}}'''
		]
	],
	[
		{
			"id":"minecraft:skull",
			"name":u'''Tlaxan Mask''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:4s,id:4s},{lvl:2s,id:5s},{lvl:1s,id:10s}],SkullOwner:{Id:"c659cdd4-e436-4977-a6a7-d5518ebecfbb",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvMWFlMzg1NWY5NTJjZDRhMDNjMTQ4YTk0NmUzZjgxMmE1OTU1YWQzNWNiY2I1MjYyN2VhNGFjZDQ3ZDMwODEifX19"}]}},display:{Lore:["§eKing's Valley : Rare","§5Plagueroot Temple","§8Even the Tlaxans fell to the sickness"],Name:"§4§lTlaxan Mask"},AttributeModifiers:[{UUIDMost:32937979772523592l,UUIDLeast:12523234267159625l,Amount:0.15d,Slot:"head",AttributeName:"generic.attackDamage",Operation:1,Name:"generic.attackDamage"}]}'''
		]
	],
	[
		{
			"id":"minecraft:chainmail_helmet",
			"name":u'''Hellborn Crown''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:3s,id:1s},{lvl:2s,id:34s}],display:{Lore:["§eKing's Valley : Rare","§cEphemeral Corridors","§8A crown for the Crimson King."],Name:"§4§lHellborn Crown"},AttributeModifiers:[{UUIDMost:379758l,UUIDLeast:617489l,Amount:0.05d,Slot:"head",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:282280l,UUIDLeast:923322l,Amount:2.0d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:-3581384299597379461l,UUIDLeast:-8581973643124513272l,Amount:1.0d,Slot:"head",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:bow",
			"name":u'''Heatwave''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:48s},{lvl:1s,id:49s},{lvl:1s,id:50s},{lvl:2s,id:34s}],display:{Lore:["§eKing's Valley : Rare","§cEphemeral Corridors","§8Firey passion sparks memories that","§8span generations."],Name:"§4§lHeatwave"},AttributeModifiers:[{UUIDMost:1953985229413762026l,UUIDLeast:-7788873909617989122l,Amount:0.05d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"},{UUIDMost:4460626849743783254l,UUIDLeast:-4613216353505383089l,Amount:1.0d,Slot:"mainhand",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:shield",
			"name":u'''Whispers of the Blizzard''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:34s},{lvl:3s,id:7s}],HideFlags:32,BlockEntityTag:{Base:15,Patterns:[{Color:12,Pattern:"gra"},{Color:15,Pattern:"gra"},{Color:12,Pattern:"bts"},{Color:15,Pattern:"bts"},{Color:12,Pattern:"tts"},{Color:15,Pattern:"tts"},{Color:15,Pattern:"flo"}]},display:{Lore:["§eKing's Valley : Rare","§cEphemeral Corridors","§8The voices call from the gusts of snow.","§8The only question is who they belonged to."],Name:"§f§lWhispers of the Blizzard"},AttributeModifiers:[{UUIDMost:2256773067886383020l,UUIDLeast:-5655061197444746948l,Amount:-0.1d,Slot:"offhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"},{UUIDMost:5849519655109806008l,UUIDLeast:-8335205912319506803l,Amount:-0.15d,Slot:"offhand",AttributeName:"generic.attackSpeed",Operation:1,Name:"Modifier"},{UUIDMost:8672913500936421533l,UUIDLeast:-5547658156596734111l,Amount:2.0d,Slot:"offhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"},{UUIDMost:-1341536773596754749l,UUIDLeast:-5380820354758116450l,Amount:2.0d,Slot:"offhand",AttributeName:"generic.armorToughness",Operation:0,Name:"Modifier"},{UUIDMost:-280597868914128454l,UUIDLeast:-6563374324551311180l,Amount:0.1d,Slot:"offhand",AttributeName:"generic.knockbackResistance",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_hoe",
			"name":u'''Frostbite Scythe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:5s,id:16s},{lvl:2s,id:17s},{lvl:4s,id:34s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§cEphemeral Corridors","§8Even beyond death, the bones remember","§8the chill.","§7","§7When in main hand:","§7 2 Attack Speed","§7 6 Attack Damage"],Name:"§b§lFrostbite Scythe"},AttributeModifiers:[{UUIDMost:6433490404641818817l,UUIDLeast:-8593178968434576189l,Amount:-2.0d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"Modifier"},{UUIDMost:3288944914052894654l,UUIDLeast:-5839775210248136997l,Amount:2.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:golden_sword",
			"name":u'''Arachnidruid Cutlass''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:16s},{lvl:5s,id:18s},{lvl:7s,id:34s},{lvl:2s,id:19s}],display:{Lore:["§eKing's Valley : Rare","§cEphemeral Corridors","§8It is perhaps fears that stick","§8 strongest in the mind."],Name:"§7§lArachnidruid Cutlass"}}'''
		]
	],
	[
		{
			"id":"minecraft:golden_boots",
			"name":u'''Imperial Boots''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:2s,id:4s},{lvl:3s,id:34s}],display:{Lore:["§eKing's Valley : Rare","§cEphemeral Corridors","§8Footwear from a long-forgotten Monarch."],Name:"§6§lImperial Boots"},AttributeModifiers:[{UUIDMost:1775669591734307443l,UUIDLeast:-6024546899061047350l,Amount:1.0d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"Modifier"},{UUIDMost:195460280784930720l,UUIDLeast:-7656255313218295407l,Amount:0.07d,Slot:"feet",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:tipped_arrow",
			"name":u'''Arrow of Decay''',
		},
		[
			"nbt", "replace", ur'''{HideFlags:35,CustomPotionColor:4849664,CustomPotionEffects:[{Duration:240,Id:20b,Amplifier:0b}],Potion:"minecraft:empty",display:{Lore:["§cWither (0:12)"],Name:"§rArrow of Decay"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Desert Explorer''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:3s,id:34s},{lvl:5s,id:2s}],display:{Lore:["§eKing's Valley : Rare","§cEphemeral Corridors","§8The Crimson King traveled far after his birth.","§8What he found in the world proved his cause."],color:12759680,Name:"§e§lDesert Explorer"},AttributeModifiers:[{UUIDMost:2367943038892720258l,UUIDLeast:-9218447296705209579l,Amount:0.25d,Slot:"legs",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"},{UUIDMost:-1681188778291804665l,UUIDLeast:-7635237611773886596l,Amount:-3.0d,Slot:"legs",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:golden_sword",
			"name":u'''Phoenix Spellblade''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:16s},{lvl:2s,id:34s},{lvl:2s,id:19s},{lvl:1s,id:70s},{lvl:5s,id:20s},{lvl:4s,id:22s}],HideFlags:2,display:{Lore:["§8* Magic Wand *","§eKing's Valley : Rare","§cEphemeral Corridors","§8Memories rise from the ashes,","§8but fade like embers in the night.","§7","§7When in main hand:","§7 1.6 Attack Speed","§7 6 Attack Damage"],Name:"§4§lPhoenix Spellblade"},AttributeModifiers:[{UUIDMost:1199492919208527277l,UUIDLeast:-8591107790182166399l,Amount:-2.4d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"Modifier"},{UUIDMost:-6641988833548811160l,UUIDLeast:-7903616741035893090l,Amount:3.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:skull",
			"name":u'''Ender Eyes''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s}],SkullOwner:{Id:"40ffb372-12f6-4678-b3f2-2176bf56dd4b",Name:"MHF_Enderman",Properties:{textures:[{Signature:"yBts7gxjhzU2wRkYNhrKffQl07Y3RGCABJqNKsIg4AqKyKdRC4Mi72Yo4GZLSxbnlefQF8mzkAtZO5VZJyOwVGtyDm0kdV3lKWQAcQft1tsng+RzuezdxCyySwZBCuxkqg6WCAO4EvTT3AUCyrIkme3i8ch1gWSas56SZeIC60fdr1ZaQUua65+RG8/b7Xk8h6ANQpOQNKwgMKBDWXTyVyTgAEqX65HymK793I30Jee+KYi43QLLilZ2l3i+YI5r915c+mtHeXOwYSjywnJ6nXdKQS9LorjxT+3fNrX4AAckU4liRppDiXk0tuaz5Y2qFGIobgJa9u4aEis2KfjIabKwAMx0IAWOKW5eBUDHAAHriWAJg8knWbF/N3mH8y3s/ksU1N3Y76zTyCh577LEpcqdK7KoBnWLek1hswf1Ria+ydXLFxw/YJqy2zEOK60Hb5qc4HX1pqdFRY4utTSAqyaElZGKMBcitkGtGRCW7CmJReWoREWaoTkI6kmm2YN2Ogm6QRHiMTwu2tMQxOjZWnnUc5PsqtrmkS0w6DwcZnRNHb/op30wxfEztpOoY7QBPivG0WMZq+cj+4ncPm+r604d4dUz7nfA95NNr81SSSRh4IqBjqnnq1A5dnlnlipfWcspo8oiDqvO+59+SZet9Y67j0qG1o2iI8jmMQDfFwk=",Value:"eyJ0aW1lc3RhbXAiOjE1MDc0NzA1NTU2OTksInByb2ZpbGVJZCI6IjQwZmZiMzcyMTJmNjQ2NzhiM2YyMjE3NmJmNTZkZDRiIiwicHJvZmlsZU5hbWUiOiJNSEZfRW5kZXJtYW4iLCJzaWduYXR1cmVSZXF1aXJlZCI6dHJ1ZSwidGV4dHVyZXMiOnsiU0tJTiI6eyJ1cmwiOiJodHRwOi8vdGV4dHVyZXMubWluZWNyYWZ0Lm5ldC90ZXh0dXJlLzdhNTliYjBhN2EzMjk2NWIzZDkwZDhlYWZhODk5ZDE4MzVmNDI0NTA5ZWFkZDRlNmI3MDlhZGE1MGI5Y2YifX19"}]}},display:{Lore:["§dDarksight","§eKing's Valley : Rare","§eVernal Nightmare","§8I SEE ALL"],Name:"§5§lEnder Eyes"},AttributeModifiers:[{UUIDMost:-6943906489819969946l,UUIDLeast:-8870601153493074758l,Amount:1.0d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_hoe",
			"name":u'''Enderwrath''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:16s},{lvl:5s,id:34s},{lvl:1s,id:19s},{lvl:2s,id:20s},{lvl:2s,id:21s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§eVernal Nightmare","§8The rage from below is a","§8pain beyond any other.","§7","§7When in main hand:","§7 2 Attack Speed","§7 5 Attack Damage","§9 +15% Speed"],Name:"§5§lEnderwrath"},AttributeModifiers:[{UUIDMost:6433490404641818817l,UUIDLeast:-8593178968434576189l,Amount:-2.0d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"Modifier"},{UUIDMost:3288944914052894654l,UUIDLeast:-5839775210248136997l,Amount:2.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"},{UUIDMost:-1699364481579463557l,UUIDLeast:-6029370082936163140l,Amount:0.15d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Bluescale Torso''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:1s,id:10s},{lvl:1s,id:70s}],display:{Lore:["§bLeather Armor","§eKing's Valley : Rare","§eVernal Nightmare","§8Formed from the scales of an","§8ancient beast, this chestplate repairs","§8itself magically."],color:33023,Name:"§9§lBluescale Torso"},AttributeModifiers:[{UUIDMost:-3888183692021970616l,UUIDLeast:-7298771026915334773l,Amount:3.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"},{UUIDMost:1823759277950324534l,UUIDLeast:-5479529971549225026l,Amount:0.05d,Slot:"chest",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"},{UUIDMost:-6247294425327582144l,UUIDLeast:-8706916085520107217l,Amount:0.08d,Slot:"chest",AttributeName:"generic.attackSpeed",Operation:1,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:chainmail_leggings",
			"name":u'''Ironscale Leggings''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:2s,id:34s}],display:{Lore:["§eKing's Valley : Rare","§eVernal Nightmare","§8Crafted from a strange metal, mostly","§8unseen in the King's Valley."],Name:"§9§lIronscale Leggings"},AttributeModifiers:[{UUIDMost:46932015782064460l,UUIDLeast:34304226943201925l,Amount:4.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:42035034178315847l,UUIDLeast:15455365629951484l,Amount:2.0d,Slot:"legs",AttributeName:"generic.armorToughness",Operation:0,Name:"generic.armorToughness"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"name":u'''Frostbite''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:34s}],HideFlags:1,display:{Lore:["§eKing's Valley : Rare","§eVernal Nightmare","§8The winter devours the summer's warmth"],Name:"§b§lFrostbite"},AttributeModifiers:[{UUIDMost:15904589298271559l,UUIDLeast:15892098128867088l,Amount:0.5d,Slot:"offhand",AttributeName:"generic.knockbackResistance",Operation:0,Name:"generic.knockbackResistance"},{UUIDMost:5519348956124230l,UUIDLeast:71245373947163486l,Amount:-0.1d,Slot:"offhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:26919752762697285l,UUIDLeast:9565821765701568l,Amount:0.3d,Slot:"offhand",AttributeName:"generic.attackDamage",Operation:1,Name:"generic.attackDamage"},{UUIDMost:70946014956938317l,UUIDLeast:59970257892856718l,Amount:3.0d,Slot:"offhand",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:59337689937702222l,UUIDLeast:43829378243568899l,Amount:-0.15d,Slot:"offhand",AttributeName:"generic.attackSpeed",Operation:1,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:shield",
			"name":u'''Magmahide Shield''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:5s,id:16s},{lvl:1s,id:34s},{lvl:2s,id:19s},{lvl:2s,id:20s}],HideFlags:34,BlockEntityTag:{Base:14,Patterns:[{Color:0,Pattern:"gra"},{Color:1,Pattern:"cbo"},{Color:1,Pattern:"tts"},{Color:1,Pattern:"bts"},{Color:14,Pattern:"mc"},{Color:1,Pattern:"flo"}]},display:{Lore:["§eKing's Valley : Rare","§eVernal Nightmare","§8The summer melts winter's hunger"],Name:"§4§lMagmahide Shield"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_shovel",
			"name":u'''Greyskull's Spellcaster''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:8s,id:16s},{lvl:4s,id:34s},{lvl:2s,id:19s}],display:{Lore:["§8* Magic Wand *","§eKing's Valley : Rare","§eVernal Nightmare","§8By the power of Greyskull!"],Name:"§9§lGreyskull's Spellcaster"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"name":u'''Poison Ivy''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:5s,id:16s},{lvl:2s,id:18s},{lvl:2s,id:34s},{lvl:2s,id:22s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§eVernal Nightmare","§8The spring and fall collude to create power","§7","§7When in main hand:","§7 1.6 Attack Speed","§7 8 Attack Damage","§c -3 Armor"],Name:"§2§lPoison Ivy"},AttributeModifiers:[{UUIDMost:8412449719562827l,UUIDLeast:45136191579064328l,Amount:4.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:68056669774727247l,UUIDLeast:599809216906588l,Amount:-3.0d,Slot:"mainhand",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:66546952320709442l,UUIDLeast:65370556181348047l,Amount:-2.4d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:bow",
			"name":u'''Soulvenom Bow''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:48s},{lvl:1s,id:34s}],display:{Lore:["§eKing's Valley : Rare","§eVernal Nightmare","§8The vile venom comes from","§8the user's soul."],Name:"§2§lSoulvenom Bow"},AttributeModifiers:[{UUIDMost:8010304009546188909l,UUIDLeast:-7217374297783679577l,Amount:-2.0d,Slot:"mainhand",AttributeName:"generic.armor",Operation:0,Name:"Modifier"},{UUIDMost:-6047426008321601721l,UUIDLeast:-5163245617767258819l,Amount:-2.0d,Slot:"offhand",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Dreamweave Boots''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:2s,id:34s}],display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:9996207,Name:"§fDreamweave Boots"},AttributeModifiers:[{UUIDMost:5840032731679968491l,UUIDLeast:-5925179597771680270l,Amount:0.25d,Slot:"feet",AttributeName:"generic.armorToughness",Operation:0,Name:"Modifier"},{UUIDMost:5130243554775353937l,UUIDLeast:-4887393657455007104l,Amount:1.0d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Dreamweave Leggings''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:2s,id:34s}],display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:9996207,Name:"§fDreamweave Leggings"},AttributeModifiers:[{UUIDMost:-3762157896363391533l,UUIDLeast:-6628974842915319782l,Amount:0.5d,Slot:"legs",AttributeName:"generic.armorToughness",Operation:0,Name:"Modifier"},{UUIDMost:-3156447900251632748l,UUIDLeast:-8292570592664441147l,Amount:2.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Dreamweave Vest''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:2s,id:34s}],display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:9996207,Name:"§fDreamweave Vest"},AttributeModifiers:[{UUIDMost:-6626524806288357618l,UUIDLeast:-5712193159269540521l,Amount:0.5d,Slot:"chest",AttributeName:"generic.armorToughness",Operation:0,Name:"Modifier"},{UUIDMost:8578755222984674511l,UUIDLeast:-8594943706278003695l,Amount:3.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Dreamweave Hat''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:2s,id:34s}],display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:9996207,Name:"§fDreamweave Hat"},AttributeModifiers:[{UUIDMost:-5628909352928327594l,UUIDLeast:-8785474820517141515l,Amount:0.25d,Slot:"head",AttributeName:"generic.armorToughness",Operation:0,Name:"Modifier"},{UUIDMost:-7357832829855448226l,UUIDLeast:-8504893191372429428l,Amount:1.0d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:shield",
			"name":u'''Meat Shield''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:34s},{lvl:2s,id:7s}],HideFlags:32,BlockEntityTag:{Base:3,id:"Shield",Patterns:[{Color:1,Pattern:"cr"},{Color:1,Pattern:"gru"},{Color:1,Pattern:"tts"}]},display:{Lore:["§8King's Valley : Uncommon"],Name:"§fMeat Shield"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Infernal Cap''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:2s,id:1s},{lvl:2s,id:34s},{lvl:2s,id:3s}],display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:16727040,Name:"§fInfernal Cap"},AttributeModifiers:[{UUIDMost:-2548352271945610225l,UUIDLeast:-8957479323877684809l,Amount:0.03d,Slot:"head",AttributeName:"generic.attackDamage",Operation:1,Name:"Modifier"},{UUIDMost:1388011465359118300l,UUIDLeast:-5041929405070948004l,Amount:1.0d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Infernal Tunic''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:2s,id:1s},{lvl:2s,id:34s},{lvl:2s,id:3s}],display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:16195840,Name:"§fInfernal Tunic"},AttributeModifiers:[{UUIDMost:-5339908050636355638l,UUIDLeast:-7972341520036710483l,Amount:3.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"},{UUIDMost:-8340305859777442085l,UUIDLeast:-6427377286379367189l,Amount:0.05d,Slot:"chest",AttributeName:"generic.attackDamage",Operation:1,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Infernal Pants''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:2s,id:1s},{lvl:2s,id:34s},{lvl:2s,id:3s}],display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:16195840,Name:"§fInfernal Pants"},AttributeModifiers:[{UUIDMost:258085l,UUIDLeast:964689l,Amount:0.05d,Slot:"legs",AttributeName:"generic.attackDamage",Operation:1,Name:"generic.attackDamage"},{UUIDMost:337397l,UUIDLeast:607978l,Amount:2d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Infernal Boots''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:2s,id:1s},{lvl:2s,id:34s},{lvl:2s,id:2s}],display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:16195840,Name:"§fInfernal Boots"},AttributeModifiers:[{UUIDMost:-6294016872395487012l,UUIDLeast:-6894791237121734080l,Amount:0.03d,Slot:"feet",AttributeName:"generic.attackDamage",Operation:1,Name:"Modifier"},{UUIDMost:-5499829519386392572l,UUIDLeast:-8456887575499756629l,Amount:1.0d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:prismarine_crystals",
			"name":u'''Fear Shard''',
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["§8It's a thing of Nightmares"],Name:"§fFear Shard"}}'''
		]
	],
	[
		{
			"id":"minecraft:rabbit_foot",
			"name":u'''Thumper's Paw''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:16s},{lvl:2s,id:19s}],display:{Lore:["* Event Item *","§eEaster 2018"],Name:"§e§lThumper's Paw"},AttributeModifiers:[{UUIDMost:2077553840456682437l,UUIDLeast:-7554520846310408001l,Amount:0.15d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:dragon_breath",
			"name":u'''Concentrated Experience''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:48s}],HideFlags:1,display:{Lore:["§7Worth 8 enchanting bottles"],Name:"§6Concentrated Experience"}}'''
		]
	],
	[
		{
			"id":"minecraft:magma_cream",
			"name":u'''Royal Crystal''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:51s}],HideFlags:1,display:{Lore:["§fA reward for completing","§fa King's Bounty"],Name:"§6§lRoyal Crystal"}}'''
		]
	],
	[
		{
			"id":"gold_nugget",
			"name":u'''Pulsating Gold''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:10s,id:48s}],display:{Lore:["§8Epic Crafting Ingredient"],Name:"§6§lPulsating Gold"}}'''
		]
	],
	[
		{
			"id":"minecraft:shield",
			"name":u'''Sanctifying Guard''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:34s},{lvl:2s,id:19s}],HideFlags:32,BlockEntityTag:{Base:10,Patterns:[{Color:15,Pattern:"bo"},{Color:15,Pattern:"mr"},{Color:6,Pattern:"flo"},{Color:7,Pattern:"tts"},{Color:7,Pattern:"bts"}]},display:{Lore:["§dMainhand Regeneration","§8King's Valley : §6Patron Made","§8Made with Sage wisdom"],Name:"§a§lSanctifying Guard"},AttributeModifiers:[{UUIDMost:1287381409643709352l,UUIDLeast:-7880782928783714372l,Amount:4.0d,Slot:"mainhand",AttributeName:"generic.armor",Operation:0,Name:"Modifier"},{UUIDMost:4065928328244447087l,UUIDLeast:-8906003175754769214l,Amount:2.0d,Slot:"mainhand",AttributeName:"generic.armorToughness",Operation:0,Name:"Modifier"},{UUIDMost:2452519509611594002l,UUIDLeast:-9038091112074494442l,Amount:-0.1d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"name":u'''Scalawag's Hatchet''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:16s},{lvl:1s,id:32s},{lvl:1s,id:34s}],display:{Lore:["* Unique Item *"],Name:"§b§lScalawag's Hatchet"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Tyrolean Boots''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:4s},{lvl:3s,id:34s}],display:{Lore:["§bLeather Armor","* Unique Item *"],Name:"§b§lTyrolean Boots"},AttributeModifiers:[{UUIDMost:515374l,UUIDLeast:447544l,Amount:0.1d,Slot:"feet",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:871280l,UUIDLeast:774709l,Amount:1d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"name":u'''Murano's Dagger''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:16s},{lvl:2s,id:34s},{lvl:1s,id:21s}],display:{Lore:["* Unique Item *"],Name:"§b§lMurano's Dagger"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"name":u'''Watcher's Sword''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:17s},{lvl:3s,id:34s}],display:{Lore:["* Unique Item *","§8Quis Custodeit Ipsos Custodets?"],Name:"§d§lWatcher's Sword"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Water Robe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:1s},{lvl:1s,id:70s}],HideFlags:2,display:{Lore:["§dRegeneration","§5King's Valley : Unique","§f","§7When on legs:","§c 0 Armor","§c -10% Speed"],color:10535167,Name:"§b§lWater Robe"},AttributeModifiers:[{UUIDMost:-5444563899986130921l,UUIDLeast:-6071829781889919167l,Amount:-0.1d,Slot:"legs",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:shield",
			"name":u'''Crushing Depths''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:70s}],HideFlags:32,BlockEntityTag:{Base:12,Patterns:[{Color:0,Pattern:"bt"},{Color:0,Pattern:"gru"},{Color:0,Pattern:"gru"},{Color:0,Pattern:"bts"}]},display:{Lore:["§dDarksight","§5King's Valley : Unique"],Name:"§b§lCrushing Depths"}}'''
		]
	],
	[
		{
			"id":"minecraft:shield",
			"name":u'''Morphic Shield''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:70s}],BlockEntityTag:{Base:13,Patterns:[{Color:0,Pattern:"gra"},{Color:15,Pattern:"mc"}]},display:{Lore:["* Unique Item *","§8As everlasting as a Memory"],Name:"§5§lMorphic Shield"},AttributeModifiers:[{UUIDMost:576781l,UUIDLeast:877205l,Amount:0.03d,Slot:"offhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:rotten_flesh",
			"name":u'''High-Quality Beef''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:71s}],display:{Lore:["§d* Quest Item *","#Q17I02"],Name:"§6§lHigh-Quality Beef"}}'''
		]
	],
	[
		{
			"id":"minecraft:bow",
			"name":u'''Highstorm''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:48s},{lvl:3s,id:34s},{lvl:1s,id:51s}],display:{Lore:["* Unique Item *","* Irreparable *"],Name:"§6§lHighstorm"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"name":u'''Silver Knight's Hammer''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:16s},{lvl:2s,id:17s},{lvl:1s,id:70s}],display:{Lore:["* Unique Item *","§8A mighty weapon of heroes past"],Name:"§b§lSilver Knight's Hammer"}}'''
		]
	],
	[
		{
			"id":"minecraft:feather",
			"name":u'''Holy Feather''',
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["§8Considered sacred by many"],Name:"§rHoly Feather"}}'''
		]
	],
	[
		{
			"id":"minecraft:feather",
			"name":u'''Sharpened Holy Feather''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:6s,id:16s}],display:{Lore:["§8* Magic Wand *","§8King's Valley : §6Patron Made","§8A feather from the holy Rayven"],Name:"§f§lSharpened Holy Feather"},AttributeModifiers:[{UUIDMost:8148793466415236557l,UUIDLeast:-5911602864794772103l,Amount:0.07d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:shield",
			"name":u'''Eventide''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:70s}],HideFlags:32,BlockEntityTag:{Base:5,Patterns:[{Color:0,Pattern:"bri"},{Color:0,Pattern:"bo"},{Color:0,Pattern:"gru"},{Color:0,Pattern:"gra"}]},display:{Lore:["§8King's Valley : §6Patron Made","§8Made from the hide of a War Pig"],Name:"§5§lEventide"},AttributeModifiers:[{UUIDMost:7520587670989783111l,UUIDLeast:-5102823209888792649l,Amount:0.3d,Slot:"offhand",AttributeName:"generic.knockbackResistance",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:dye",
			"name":u'''Water Gem''',
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["§8Sharded, but could be rebuilt"],Name:"§rWater Gem"}}'''
		]
	],
	[
		{
			"id":"minecraft:skull",
			"name":u'''Entropic Skull''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:3s,id:1s},{lvl:2s,id:4s},{lvl:1s,id:10s}],display:{Lore:["§8King's Valley : §6Patron Made","§8Alas poor skull, they got pwn4d"],Name:"§5§lEntropic Skull"},AttributeModifiers:[{UUIDMost:-3064219100859248973l,UUIDLeast:-8672896259970709443l,Amount:-0.08d,Slot:"head",AttributeName:"generic.attackSpeed",Operation:1,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_hoe",
			"name":u'''Ruby Scythe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:16s},{lvl:5s,id:34s},{lvl:1s,id:19s},{lvl:1s,id:20s}],HideFlags:2,display:{Lore:["§8King's Valley : Uncommon","§8Made of a gleaming Red Rock","§l","§7When in main hand:","§7 2 Attack Speed","§7 4 Attack Damage"],Name:"§c§lRuby Scythe"},AttributeModifiers:[{UUIDMost:-9180044814077834571l,UUIDLeast:-5198006168436150311l,Amount:2.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"},{UUIDMost:-3443662273770534894l,UUIDLeast:-8014295939910783312l,Amount:-2.0d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Gem Encrusted Manpance''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:3s,id:8s},{lvl:3s,id:5s},{lvl:1s,id:70s}],display:{Lore:["§cCurse of Vanishing?","§bLeather Armor","§8King's Valley : §6Patron Made","§8Forged with the sweetest Gems"],color:12571378,Name:"§9§lGem Encrusted Manpance"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather",
			"name":u'''Polar Bear Hide''',
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["§8A large cut of durable hide"],Name:"§fPolar Bear Hide"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Infernal Robe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:1s}],display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:11206656,Name:"§4§lInfernal Robe"},AttributeModifiers:[{UUIDMost:-3906240411837903389l,UUIDLeast:-7890992669234016346l,Amount:2.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"Modifier"},{UUIDMost:5753471876015473889l,UUIDLeast:-7352350150367536802l,Amount:0.1d,Slot:"legs",AttributeName:"generic.attackDamage",Operation:1,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:clay_ball",
			"name":u'''Ponderous Stone''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:51s}],HideFlags:1,display:{Lore:["§8King's Valley : Uncommon"],Name:"§6§lPonderous Stone"},AttributeModifiers:[{UUIDMost:-8784931189073293981l,UUIDLeast:-5336435319922077366l,Amount:1.0d,Slot:"offhand",AttributeName:"generic.knockbackResistance",Operation:0,Name:"Modifier"},{UUIDMost:-3784013313986900216l,UUIDLeast:-9150198598510123427l,Amount:-0.25d,Slot:"offhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"},{UUIDMost:-2473186416011490271l,UUIDLeast:-6797638087243652569l,Amount:-4.0d,Slot:"offhand",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:blaze_powder",
			"name":u'''Blazing Soul''',
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["§8King's Valley : Uncommon"],Name:"§4§lBlazing Soul"},AttributeModifiers:[{UUIDMost:828307l,UUIDLeast:820066l,Amount:1d,Slot:"offhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:716656l,UUIDLeast:252102l,Amount:0.08d,Slot:"offhand",AttributeName:"generic.attackSpeed",Operation:1,Name:"generic.attackSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:golden_sword",
			"name":u'''Lingering Flame''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:2s,id:34s},{lvl:2s,id:19s},{lvl:5s,id:20s}],display:{Lore:["§8King's Valley : Uncommon"],Name:"§6§lLingering Flame"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"name":u'''Oncoming Wave''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:8s},{lvl:1s,id:0s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Uncommon"],color:2162623,Name:"§b§lOncoming Wave"},AttributeModifiers:[{UUIDMost:290399l,UUIDLeast:1103793l,Amount:0.75d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:5672941998827654801l,UUIDLeast:-6706627889588372856l,Amount:0.05d,Slot:"feet",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:record_stal",
			"name":u'''Groovy Chakram''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:5s,id:16s}],display:{Lore:["§8King's Valley : Uncommon"],Name:"§f§lGroovy Chakram"},AttributeModifiers:[{UUIDMost:2601567444108069946l,UUIDLeast:-5216243073072645588l,Amount:3.0d,Slot:"mainhand",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"name":u'''Vermin's Scourge''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:32s},{lvl:3s,id:18s},{lvl:1s,id:34s}],display:{Lore:["§8King's Valley : Uncommon"],Name:"§2§lVermin's Scourge"}}'''
		]
	],
	[
		{
			"id":"minecraft:rabbit_foot",
			"name":u'''Raider's Charm''',
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["§8King's Valley : Uncommon"],Name:"§3§lRaider's Charm"},AttributeModifiers:[{UUIDMost:9079877381156259287l,UUIDLeast:-5393155205560440172l,Amount:0.125d,Slot:"offhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"},{UUIDMost:8287496261883872097l,UUIDLeast:-5825817392529307077l,Amount:1.0d,Slot:"offhand",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:bow",
			"name":u'''Swiftwood Shortbow''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:48s},{lvl:2s,id:34s}],display:{Lore:["§8King's Valley : Uncommon"],Name:"§3§lSwiftwood Shortbow"},AttributeModifiers:[{UUIDMost:-6988194619003155857l,UUIDLeast:-5808010696763356504l,Amount:0.05d,Slot:"offhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"},{UUIDMost:7252551692242076597l,UUIDLeast:-9043457864470459739l,Amount:0.1d,Slot:"offhand",AttributeName:"generic.attackSpeed",Operation:1,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:dye",
			"name":u'''Fangride's Cat Dung''',
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["§8 Why would I even want this?"],Name:"§rFangride's Cat Dung"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"name":u'''Fangridian Cattcrappe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:16s},{lvl:3s,id:34s}],display:{Lore:["§8King's Valley : Uncommon","§8You find this while rummaging around in the dung. Yuck!"],Name:"§e§lFangridian Cattcrappe"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"name":u'''Cutting Breeze''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:2s,id:34s},{lvl:2s,id:22s}],HideFlags:2,display:{Lore:["§8King's Valley : Uncommon","§7","§7When in main hand:","§7 1.6 Attack Speed","§7 5.5 Attack Damage","§9 +7.5% Speed"],Name:"§b§lCutting Breeze"},AttributeModifiers:[{UUIDMost:2533482495801970563l,UUIDLeast:-9003299790244515489l,Amount:3.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"},{UUIDMost:-5824020502991386004l,UUIDLeast:-6534476216028313182l,Amount:-2.4d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"Modifier"},{UUIDMost:5731965308627600231l,UUIDLeast:-6508277300744269122l,Amount:0.075d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"name":u'''Chitin Helmet''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:34s},{lvl:1s,id:3s}],display:{Lore:["§8King's Valley : Uncommon"],color:16772518,Name:"§7§lChitin Helmet"},AttributeModifiers:[{UUIDMost:333040l,UUIDLeast:702481l,Amount:2d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stick",
			"name":u'''Blackroot's Fury''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:5s,id:16s},{lvl:1s,id:19s}],display:{Lore:["§8* Magic Wand *","§8King's Valley : Uncommon"],Name:"§d§lBlackroot's Fury"},AttributeModifiers:[{UUIDMost:440231l,UUIDLeast:487582l,Amount:1d,Slot:"mainhand",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_hoe",
			"name":u'''Blighted Scythe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:3s,id:34s},{lvl:1s,id:19s},{lvl:1s,id:20s},{lvl:3s,id:21s}],HideFlags:2,display:{Lore:["§8King's Valley : Uncommon","§8","§7When in main hand:","§7 2 Attack Speed","§7 4.5 Attack Damage","§c -1 Armor"],Name:"§4§lBlighted Scythe"},AttributeModifiers:[{UUIDMost:6433490404641818817l,UUIDLeast:-8593178968434576189l,Amount:-2.0d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"Modifier"},{UUIDMost:3288944914052894654l,UUIDLeast:-5839775210248136997l,Amount:2.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"},{UUIDMost:-6247475251793607498l,UUIDLeast:-7993135500588112887l,Amount:-1.0d,Slot:"mainhand",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_hoe",
			"name":u'''Reaper's Scythe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:16s},{lvl:4s,id:17s},{lvl:5s,id:34s}],HideFlags:2,display:{Lore:["* Unique Item *","§8","§7When in main hand:","§7 2 Attack Speed","§7 3.5 Attack Damage"],Name:"§2§lReaper's Scythe"},AttributeModifiers:[{UUIDMost:6433490404641818817l,UUIDLeast:-8593178968434576189l,Amount:-2.0d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"Modifier"},{UUIDMost:3288944914052894654l,UUIDLeast:-5839775210248136997l,Amount:2.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_hoe",
			"name":u'''Highland Scythe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:17s},{lvl:3s,id:34s},{lvl:2s,id:19s}],HideFlags:2,display:{Lore:["* Unique Item *","§8","§7When in main hand:","§7 2 Attack Speed","§7 3 Attack Damage"],Name:"§d§lHighland Scythe"},AttributeModifiers:[{UUIDMost:6433490404641818817l,UUIDLeast:-8593178968434576189l,Amount:-2.0d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"Modifier"},{UUIDMost:3288944914052894654l,UUIDLeast:-5839775210248136997l,Amount:2.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Busty's Hotter Pants''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:4s,id:1s},{lvl:1s,id:70s},{lvl:4s,id:3s}],display:{Lore:["§bLeather Armor","§eKing's Valley : §lEnhanced Rare","§fThe legs are flaming with stress!"],color:14059296,Name:"§4§lBusty's Hotter Pants"}}'''
		]
	],
	[
		{
			"id":"minecraft:bone",
			"name":u'''Charm of C'Zanil''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:4s,id:16s},{lvl:2s,id:19s},{lvl:1s,id:20s}],display:{Lore:["§dRegeneration","§8* Magic Wand *","§eKing's Valley : §lEnhanced Rare"],Name:"§6§lCharm of C'Zanil"},AttributeModifiers:[{UUIDMost:-1371131983094264777l,UUIDLeast:-5382187275748050885l,Amount:2.0d,Slot:"offhand",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"},{UUIDMost:1147813372249458141l,UUIDLeast:-5241124910695973213l,Amount:0.05d,Slot:"offhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"},{UUIDMost:4237906884953785636l,UUIDLeast:-5624009317461119834l,Amount:0.05d,Slot:"offhand",AttributeName:"generic.attackSpeed",Operation:1,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:dye",
			"name":u'''Ephemeral Key Fragment''',
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["§7Shattered fragments of a dungeon key.","§7Maybe these could be reforged by someone?"],Name:"§c§lEphemeral Key Fragment"}}'''
		]
	],
	[
		{
			"id":"minecraft:bow",
			"name":u'''Swiftwood Longbow''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:48s},{lvl:2s,id:34s}],display:{Lore:["§8King's Valley : §lEnhanced Uncommon"],Name:"§3§lSwiftwood Longbow"},AttributeModifiers:[{UUIDMost:-8641871752849043493l,UUIDLeast:-7622612742186920344l,Amount:0.1d,Slot:"offhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"},{UUIDMost:3883145082035193920l,UUIDLeast:-7515329855548103219l,Amount:0.1d,Slot:"offhand",AttributeName:"generic.attackSpeed",Operation:1,Name:"Modifier"},{UUIDMost:-8670808613469731742l,UUIDLeast:-9047016488534870822l,Amount:2.0d,Slot:"offhand",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"name":u'''Slicing Wind''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:2s,id:34s},{lvl:1s,id:70s},{lvl:3s,id:22s}],HideFlags:2,display:{Lore:["§8King's Valley : §lEnhanced Uncommon","§7","§7When in main hand:","§7 1.6 Attack Speed","§7 5.5 Attack Damage","§9 +10% Speed"],Name:"§b§lSlicing Wind"},AttributeModifiers:[{UUIDMost:2533482495801970563l,UUIDLeast:-9003299790244515489l,Amount:3.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"},{UUIDMost:-5824020502991386004l,UUIDLeast:-6534476216028313182l,Amount:-2.4d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"Modifier"},{UUIDMost:-6771036207707566305l,UUIDLeast:-6537146721220613023l,Amount:0.1d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:record_stal",
			"name":u'''Far-Out Chakram''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:6s,id:16s}],display:{Lore:["§8King's Valley : §lEnhanced Uncommon"],Name:"§f§lFar-Out Chakram"},AttributeModifiers:[{UUIDMost:3654580523198464199l,UUIDLeast:-8443708639368984981l,Amount:1.0d,Slot:"mainhand",AttributeName:"generic.armorToughness",Operation:0,Name:"Modifier"},{UUIDMost:-8344933023111888536l,UUIDLeast:-6069473158666389222l,Amount:0.3d,Slot:"mainhand",AttributeName:"generic.knockbackResistance",Operation:0,Name:"Modifier"},{UUIDMost:2522124462433389080l,UUIDLeast:-6652562632949158686l,Amount:3.0d,Slot:"mainhand",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:blaze_powder",
			"name":u'''Soul of Conflagration''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:20s}],display:{Lore:["§8King's Valley : §lEnhanced Uncommon"],Name:"§4§lSoul of Conflagration"},AttributeModifiers:[{UUIDMost:-7769405553159353316l,UUIDLeast:-5980438255535144460l,Amount:0.16d,Slot:"offhand",AttributeName:"generic.attackSpeed",Operation:1,Name:"Modifier"},{UUIDMost:6881167597771049715l,UUIDLeast:-5128578317340387122l,Amount:1.5d,Slot:"offhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"name":u'''Firestorm Robe''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:3s,id:1s},{lvl:3s,id:34s}],display:{Lore:["§bLeather Armor","§8King's Valley : §lEnhanced Uncommon"],color:11206656,Name:"§4§lFirestorm Robe"},AttributeModifiers:[{UUIDMost:-3906240411837903389l,UUIDLeast:-7890992669234016346l,Amount:2.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"Modifier"},{UUIDMost:-5045052515200971090l,UUIDLeast:-8131580841934236396l,Amount:0.1d,Slot:"legs",AttributeName:"generic.attackDamage",Operation:1,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:rabbit_foot",
			"name":u'''Plunderer's Charm''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:33s}],display:{Lore:["§8King's Valley : §lEnhanced Uncommon"],Name:"§3§lPlunderer's Charm"},AttributeModifiers:[{UUIDMost:-317900719640657618l,UUIDLeast:-6343954015115936234l,Amount:0.15d,Slot:"offhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"},{UUIDMost:-7818994650597865844l,UUIDLeast:-7720542574073167446l,Amount:0.12d,Slot:"offhand",AttributeName:"generic.attackSpeed",Operation:1,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:clay_ball",
			"name":u'''Burdened Stone''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:32s},{lvl:1s,id:51s}],HideFlags:1,display:{Lore:["§8King's Valley : §lEnhanced Uncommon"],Name:"§6§lBurdened Stone"},AttributeModifiers:[{UUIDMost:1533226517562609431l,UUIDLeast:-6398042709746424447l,Amount:-0.1d,Slot:"offhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"},{UUIDMost:-8773735443779992269l,UUIDLeast:-8038567590932003071l,Amount:-2.0d,Slot:"offhand",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"},{UUIDMost:-1805071597428191759l,UUIDLeast:-8809138101270845723l,Amount:2.0d,Slot:"offhand",AttributeName:"generic.armor",Operation:0,Name:"Modifier"},{UUIDMost:-5381934911278069713l,UUIDLeast:-6206268774793144820l,Amount:0.8d,Slot:"offhand",AttributeName:"generic.knockbackResistance",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:record_mall",
			"name":u'''Obsidian Hits''',
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["§8King's Valley : Uncommon","§cEphemeral Corridors","§8A disc made out of solid obsidian.","§8It has a nice chime to it."],Name:"§5§lObsidian Hits"}}'''
		]
	],
	[
		{
			"id":"minecraft:record_ward",
			"name":u'''Embalmer's Mixtape''',
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["§8King's Valley : Uncommon","§cEphemeral Corridors","§8An old record for an old Embalmer.","§8Questionably eerie, yet soothing."],Name:"§2§lEmbalmer's Mixtape"}}'''
		]
	],
	[
		{
			"id":"minecraft:record_strad",
			"name":u'''Web-Covered Classics''',
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["§8King's Valley : Uncommon","§cEphemeral Corridors","§8Coated in a thick webbing,","§8this track is oddly upbeat."],Name:"§f§lWeb-Covered Classics"}}'''
		]
	],
	[
		{
			"id":"minecraft:record_13",
			"name":u'''Sandy-Smooth Jazz''',
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["§8King's Valley : Uncommon","§cEphemeral Corridors","§8The sand grains in the disc","§8add a pleasant metallic ring."],Name:"§6§lSandy-Smooth Jazz"}}'''
		]
	],
	[
		{
			"id":"minecraft:lingering_potion",
			"name":u'''Weak Sanctify Potion''',
		},
		[
			"nbt", "replace", ur'''{CustomPotionColor:16744576,CustomPotionEffects:[{Ambient:1b,ShowParticles:1b,Duration:300,Id:10b,Amplifier:0b}],Potion:"minecraft:empty",display:{Name:"§fWeak Sanctify Potion"}}'''
		]
	],
	[
		{
			"id":"minecraft:lingering_potion",
			"name":u'''Sanctify Potion''',
		},
		[
			"nbt", "replace", ur'''{CustomPotionColor:16744576,CustomPotionEffects:[{Ambient:1b,ShowParticles:1b,Duration:300,Id:10b,Amplifier:1b},{Ambient:1b,ShowParticles:1b,Duration:600,Id:22b,Amplifier:0b}],Potion:"minecraft:empty",display:{Name:"§fSanctify Potion"}}'''
		]
	],
	[
		{
			"id":"minecraft:lingering_potion",
			"name":u'''Weak Barrier Potion''',
		},
		[
			"nbt", "replace", ur'''{CustomPotionColor:160,CustomPotionEffects:[{Ambient:1b,ShowParticles:1b,Duration:300,Id:2b,Amplifier:2b}],Potion:"minecraft:empty",display:{Name:"§fWeak Barrier Potion"}}'''
		]
	],
	[
		{
			"id":"minecraft:lingering_potion",
			"name":u'''Barrier Potion''',
		},
		[
			"nbt", "replace", ur'''{CustomPotionColor:160,CustomPotionEffects:[{Ambient:1b,ShowParticles:1b,Duration:360,Id:2b,Amplifier:3b},{Ambient:1b,ShowParticles:1b,Duration:360,Id:4b,Amplifier:0b}],Potion:"minecraft:empty",display:{Name:"§fBarrier Potion"}}'''
		]
	],
	[
		{
			"id":"minecraft:splash_potion",
			"name":u'''Extinguisher''',
		},
		[
			"nbt", "replace", ur'''{CustomPotionColor:16756736,CustomPotionEffects:[{Ambient:1b,ShowParticles:1b,Duration:200,Id:12b,Amplifier:0b}],Potion:"minecraft:empty",display:{Name:"§fExtinguisher"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Ebola Shirt''',
		},
		[
			"nbt", "replace", ur'''{Unbreakable:1,display:{Lore:["§dStylish","§bLeather Armor","* Unique Event Item *","§cWe are small, but our legend spreads like Ebola.","§4Uganda 2018"],color:16711680,Name:"§c§lEbola Shirt"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"name":u'''Stylish Black Shirt''',
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["§dStylish","§9Cloth Armor","§7Emits smoke particles when worn"],color:1048592,Name:"§fStylish Black Shirt"},AttributeModifiers:[{UUIDMost:456904653548765814l,UUIDLeast:-4616658641294366570l,Amount:1.5d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:golden_sword",
			"name":u'''Light of Salvation''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:32s},{lvl:1s,id:19s},{lvl:1s,id:20s}],Unbreakable:1,HideFlags:2,display:{Lore:["§dRadiant","§4King's Valley : Artifact"],Name:"§e§l§nLight of Salvation"},AttributeModifiers:[{UUIDMost:4598269408375358984l,UUIDLeast:-7980334193493528635l,Amount:0.0d,AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:bow",
			"name":u'''Cupid's Bow''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:48s},{lvl:1s,id:7s}],display:{Lore:["§dRegeneration","§dMainhand Regeneration","* Unique Event Item *","§dValentine's 2018"],Name:"§d§lCupid's Bow"}}'''
		]
	],
	[
		{
			"id":"minecraft:coal",
			"name":u'''Animated Coal''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:51s}],HideFlags:1,display:{Lore:["* Event Item *","Winter 2017"],Name:"§6§lAnimated Coal"}}'''
		]
	],
	[
		{
			"id":"minecraft:stick",
			"name":u'''Prehensile Stick''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:51s}],HideFlags:1,display:{Lore:["* Event Item *","Winter 2017"],Name:"§6§lPrehensile Stick"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"name":u'''Rod of the Onodrim''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:32s},{lvl:1s,id:70s}],display:{Lore:["* Unique Event Item *","Winter 2017"],Name:"§9§lRod of the Onodrim"},AttributeModifiers:[{UUIDMost:2512866317016583848l,UUIDLeast:-8695731667534274344l,Amount:-0.4d,Slot:"offhand",AttributeName:"generic.attackSpeed",Operation:1,Name:"Modifier"},{UUIDMost:2801717605841978307l,UUIDLeast:-4821070712928009977l,Amount:-0.2d,Slot:"offhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"},{UUIDMost:5435604988355234856l,UUIDLeast:-7278734017423574959l,Amount:0.6d,Slot:"offhand",AttributeName:"generic.attackDamage",Operation:1,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:carrot",
			"name":u'''Olfactory Carrot''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:51s}],HideFlags:1,display:{Lore:["* Event Item *","Winter 2017"],Name:"§6§lOlfactory Carrot"}}'''
		]
	],
	[
		{
			"id":"minecraft:snowball",
			"name":u'''Everlasting Snow''',
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:51s}],HideFlags:1,display:{Lore:["* Event Item *","Winter 2017"],Name:"§6§lEverlasting Snow"}}'''
		]
	],
])

