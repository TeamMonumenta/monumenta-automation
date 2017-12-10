#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lib_monumenta import item_replace

KingsValleyLootTables = item_replace.ReplaceItems([],[
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§fDreamweave Boots"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:2s,id:34s}],display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:9996207,Name:"§fDreamweave Boots"},AttributeModifiers:[{UUIDMost:5840032731679968491l,UUIDLeast:-5925179597771680270l,Amount:0.25d,Slot:"feet",AttributeName:"generic.armorToughness",Operation:0,Name:"Modifier"},{UUIDMost:5130243554775353937l,UUIDLeast:-4887393657455007104l,Amount:1.0d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§fDreamweave Leggings"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:2s,id:34s}],display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:9996207,Name:"§fDreamweave Leggings"},AttributeModifiers:[{UUIDMost:-3762157896363391533l,UUIDLeast:-6628974842915319782l,Amount:0.5d,Slot:"legs",AttributeName:"generic.armorToughness",Operation:0,Name:"Modifier"},{UUIDMost:-3156447900251632748l,UUIDLeast:-8292570592664441147l,Amount:2.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§fDreamweave Vest"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:2s,id:34s}],display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:9996207,Name:"§fDreamweave Vest"},AttributeModifiers:[{UUIDMost:-6626524806288357618l,UUIDLeast:-5712193159269540521l,Amount:0.5d,Slot:"chest",AttributeName:"generic.armorToughness",Operation:0,Name:"Modifier"},{UUIDMost:8578755222984674511l,UUIDLeast:-8594943706278003695l,Amount:3.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§fDreamweave Hat"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:2s,id:34s}],display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:9996207,Name:"§fDreamweave Hat"},AttributeModifiers:[{UUIDMost:-5628909352928327594l,UUIDLeast:-8785474820517141515l,Amount:0.25d,Slot:"head",AttributeName:"generic.armorToughness",Operation:0,Name:"Modifier"},{UUIDMost:-7357832829855448226l,UUIDLeast:-8504893191372429428l,Amount:1.0d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:skull",
			"nbt":ur'''{display:{Name:"§5§lEnder Eyes"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s}],SkullOwner:{Id:"40ffb372-12f6-4678-b3f2-2176bf56dd4b",Properties:{textures:[{Signature:"yBts7gxjhzU2wRkYNhrKffQl07Y3RGCABJqNKsIg4AqKyKdRC4Mi72Yo4GZLSxbnlefQF8mzkAtZO5VZJyOwVGtyDm0kdV3lKWQAcQft1tsng+RzuezdxCyySwZBCuxkqg6WCAO4EvTT3AUCyrIkme3i8ch1gWSas56SZeIC60fdr1ZaQUua65+RG8/b7Xk8h6ANQpOQNKwgMKBDWXTyVyTgAEqX65HymK793I30Jee+KYi43QLLilZ2l3i+YI5r915c+mtHeXOwYSjywnJ6nXdKQS9LorjxT+3fNrX4AAckU4liRppDiXk0tuaz5Y2qFGIobgJa9u4aEis2KfjIabKwAMx0IAWOKW5eBUDHAAHriWAJg8knWbF/N3mH8y3s/ksU1N3Y76zTyCh577LEpcqdK7KoBnWLek1hswf1Ria+ydXLFxw/YJqy2zEOK60Hb5qc4HX1pqdFRY4utTSAqyaElZGKMBcitkGtGRCW7CmJReWoREWaoTkI6kmm2YN2Ogm6QRHiMTwu2tMQxOjZWnnUc5PsqtrmkS0w6DwcZnRNHb/op30wxfEztpOoY7QBPivG0WMZq+cj+4ncPm+r604d4dUz7nfA95NNr81SSSRh4IqBjqnnq1A5dnlnlipfWcspo8oiDqvO+59+SZet9Y67j0qG1o2iI8jmMQDfFwk=",Value:"eyJ0aW1lc3RhbXAiOjE1MDc0NzA1NTU2OTksInByb2ZpbGVJZCI6IjQwZmZiMzcyMTJmNjQ2NzhiM2YyMjE3NmJmNTZkZDRiIiwicHJvZmlsZU5hbWUiOiJNSEZfRW5kZXJtYW4iLCJzaWduYXR1cmVSZXF1aXJlZCI6dHJ1ZSwidGV4dHVyZXMiOnsiU0tJTiI6eyJ1cmwiOiJodHRwOi8vdGV4dHVyZXMubWluZWNyYWZ0Lm5ldC90ZXh0dXJlLzdhNTliYjBhN2EzMjk2NWIzZDkwZDhlYWZhODk5ZDE4MzVmNDI0NTA5ZWFkZDRlNmI3MDlhZGE1MGI5Y2YifX19"}]},Name:"MHF_Enderman"},display:{Lore:["* Darksight *","§eKing's Valley : Rare","§8Grants Night Vision when worn"],Name:"§5§lEnder Eyes"},AttributeModifiers:[{UUIDMost:-6943906489819969946l,UUIDLeast:-8870601153493074758l,Amount:1.0d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_hoe",
			"nbt":ur'''{display:{Name:"§5§lEnderwrath"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:7s,id:16s},{lvl:5s,id:34s},{lvl:1s,id:19s},{lvl:2s,id:20s},{lvl:2s,id:21s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","","§7When in main hand:","§7 2 Attack Speed","§7 5 Attack Damage","§9 +15% Speed"],Name:"§5§lEnderwrath"},AttributeModifiers:[{UUIDMost:905415l,UUIDLeast:796247l,Amount:0.15d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:840609l,UUIDLeast:663888l,Amount:-2d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§9§lBluescale Torso"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:1s,id:10s},{lvl:1s,id:70s}],display:{Lore:["§bLeather Armor","§eKing's Valley : Rare"],color:33023,Name:"§9§lBluescale Torso"},AttributeModifiers:[{UUIDMost:-3888183692021970616l,UUIDLeast:-7298771026915334773l,Amount:3.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"},{UUIDMost:1823759277950324534l,UUIDLeast:-5479529971549225026l,Amount:0.05d,Slot:"chest",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"},{UUIDMost:-6247294425327582144l,UUIDLeast:-8706916085520107217l,Amount:0.08d,Slot:"chest",AttributeName:"generic.attackSpeed",Operation:1,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:chainmail_leggings",
			"nbt":ur'''{display:{Name:"§9§lIronscale Leggings"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:2s,id:34s},{lvl:2s,id:3s}],display:{Lore:["§eKing's Valley : Rare"],Name:"§9§lIronscale Leggings"},AttributeModifiers:[{UUIDMost:46932015782064460l,UUIDLeast:34304226943201925l,Amount:4d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:42035034178315847l,UUIDLeast:15455365629951484l,Amount:2d,Slot:"legs",AttributeName:"generic.armorToughness",Operation:0,Name:"generic.armorToughness"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"nbt":ur'''{display:{Name:"§b§lFrostbite"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:34s}],HideFlags:1,display:{Lore:["§eKing's Valley : Rare"],Name:"§b§lFrostbite"},AttributeModifiers:[{UUIDMost:15904589298271559l,UUIDLeast:15892098128867088l,Amount:0.5d,Slot:"offhand",AttributeName:"generic.knockbackResistance",Operation:0,Name:"generic.knockbackResistance"},{UUIDMost:5519348956124230l,UUIDLeast:71245373947163486l,Amount:-0.1d,Slot:"offhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:26919752762697285l,UUIDLeast:9565821765701568l,Amount:0.3d,Slot:"offhand",AttributeName:"generic.attackDamage",Operation:1,Name:"generic.attackDamage"},{UUIDMost:70946014956938317l,UUIDLeast:59970257892856718l,Amount:3.0d,Slot:"offhand",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:59337689937702222l,UUIDLeast:43829378243568899l,Amount:-0.15d,Slot:"offhand",AttributeName:"generic.attackSpeed",Operation:1,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:shield",
			"nbt":ur'''{display:{Name:"§4§lMagmahide Shield"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:5s,id:16s},{lvl:1s,id:34s},{lvl:2s,id:19s},{lvl:2s,id:20s}],HideFlags:34,BlockEntityTag:{Patterns:[{Pattern:"gra",Color:0},{Pattern:"cbo",Color:1},{Pattern:"tts",Color:1},{Pattern:"bts",Color:1},{Pattern:"mc",Color:14},{Pattern:"flo",Color:1}],Base:14},display:{Lore:["§eKing's Valley : Rare"],Name:"§4§lMagmahide Shield"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_shovel",
			"nbt":ur'''{display:{Name:"§9§lGreyskull's Spellcaster"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:7s,id:16s},{lvl:2s,id:34s},{lvl:2s,id:19s}],display:{Lore:["§8* Magic Wand *","§eKing's Valley : Rare"],Name:"§9§lGreyskull's Spellcaster"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"nbt":ur'''{display:{Name:"§2§lPoison Ivy"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:5s,id:16s},{lvl:2s,id:18s},{lvl:2s,id:34s},{lvl:2s,id:22s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§7","§7When in main hand:","§7 1.6 Attack Speed","§7 8 Attack Damage","§c -3 Armor"],Name:"§2§lPoison Ivy"},AttributeModifiers:[{UUIDMost:8412449719562827l,UUIDLeast:45136191579064328l,Amount:4d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:68056669774727247l,UUIDLeast:599809216906588l,Amount:-3d,Slot:"mainhand",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:66546952320709442l,UUIDLeast:65370556181348047l,Amount:-2.4d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:bow",
			"nbt":ur'''{display:{Name:"§2§lSoulvenom Bow"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:48s},{lvl:1s,id:34s}],display:{Lore:["§eKing's Valley : Rare"],Name:"§2§lSoulvenom Bow"},AttributeModifiers:[{UUIDMost:8010304009546188909l,UUIDLeast:-7217374297783679577l,Amount:-2.0d,Slot:"mainhand",AttributeName:"generic.armor",Operation:0,Name:"Modifier"},{UUIDMost:-6047426008321601721l,UUIDLeast:-5163245617767258819l,Amount:-2.0d,Slot:"offhand",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:shield",
			"nbt":ur'''{display:{Name:"§fRusty Shield"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fRusty Shield"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§fCloth Cap"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:803793l,UUIDMost:260399l,Slot:"head"}],display:{Name:"§fCloth Cap",color:16768959,Lore:["§9Cloth Armor"]}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§fCloth Shirt"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.5d,Operation:0,UUIDLeast:903793l,UUIDMost:270399l,Slot:"chest"}],display:{Name:"§fCloth Shirt",color:16768959,Lore:["§9Cloth Armor"]}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§fCloth Pants"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.0d,Operation:0,UUIDLeast:1003793l,UUIDMost:280399l,Slot:"legs"}],display:{Name:"§fCloth Pants",color:16768959,Lore:["§9Cloth Armor"]}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§fCloth Shoes"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:1103793l,UUIDMost:290399l,Slot:"feet"}],display:{Name:"§fCloth Shoes",color:16768959,Lore:["§9Cloth Armor"]}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"nbt":ur'''{display:{Name:"§fIronwood Blade"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fIronwood Blade",Lore:["§8King's Valley : Tier I"]},ench:[{id:34s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"nbt":ur'''{display:{Name:"§fCarved Dagger"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fCarved Dagger",Lore:["§8King's Valley : Tier I"]},ench:[{id:16s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"nbt":ur'''{display:{Name:"§fOaken Broadsword"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fOaken Broadsword",Lore:["§8King's Valley : Tier I"]},ench:[{id:22s,lvl:1s},{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"nbt":ur'''{display:{Name:"§fScorching Splinter"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fScorching Splinter",Lore:["§8King's Valley : Tier I"]},ench:[{id:20s,lvl:1s},{id:19s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"nbt":ur'''{display:{Name:"§fFlensing Knife"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fFlensing Knife",Lore:["§8King's Valley : Tier I"]},ench:[{id:18s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"nbt":ur'''{display:{Name:"§fHunter's Stake"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fHunter's Stake",Lore:["§8King's Valley : Tier I"]},ench:[{id:17s,lvl:1s},{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"nbt":ur'''{display:{Name:"§fSerrated Shiv"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:51s}],HideFlags:1,display:{Lore:["§8King's Valley : Tier I"],Name:"§fSerrated Shiv"},AttributeModifiers:[{UUIDMost:298381l,UUIDLeast:495523l,Amount:0.1d,Slot:"offhand",AttributeName:"generic.attackDamage",Operation:1,Name:"generic.attackDamage"}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_axe",
			"nbt":ur'''{display:{Name:"§fSwiftwood Axe"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fSwiftwood Axe",Lore:["§8King's Valley : Tier I"]},ench:[{id:32s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_axe",
			"nbt":ur'''{display:{Name:"§fSquire's Hammer"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fSquire's Hammer",Lore:["§8King's Valley : Tier I"]},ench:[{id:16s,lvl:2s},{id:19s,lvl:1s},{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_axe",
			"nbt":ur'''{display:{Name:"§fSmoldering Hatchet"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fSmoldering Hatchet",Lore:["§8King's Valley : Tier I"]},ench:[{id:20s,lvl:1s},{id:19s,lvl:1s},{id:34s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_pickaxe",
			"nbt":ur'''{display:{Name:"§fSwiftwood Pickaxe"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fSwiftwood Pickaxe",Lore:["§8King's Valley : Tier I"]},ench:[{id:32s,lvl:1s},{id:34s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_pickaxe",
			"nbt":ur'''{display:{Name:"§fLucky Pick"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fLucky Pick",Lore:["§8King's Valley : Tier I"]},ench:[{id:35s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_pickaxe",
			"nbt":ur'''{display:{Name:"§fIronwood Pick"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fIronwood Pick",Lore:["§8King's Valley : Tier I"]},ench:[{id:34s,lvl:3s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_shovel",
			"nbt":ur'''{display:{Name:"§fSwiftwood Shovel"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fSwiftwood Shovel",Lore:["§8King's Valley : Tier I"]},ench:[{id:32s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:fishing_rod",
			"nbt":ur'''{display:{Name:"§fNovice's Fishing Rod"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fNovice's Fishing Rod",Lore:["§8King's Valley : Tier I"]},ench:[{id:34s,lvl:1s},{id:62s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stick",
			"nbt":ur'''{display:{Name:"§fWeak Wand"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fWeak Wand",Lore:["§8* Magic Wand *","§8King's Valley : Tier I"]},ench:[{id:19s,lvl:1s},{id:20s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:shield",
			"nbt":ur'''{display:{Name:"§fWeak Shield"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fWeak Shield",Lore:["§8King's Valley : Tier I"]}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§fSturdy Cloth Cap"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:803793l,UUIDMost:260399l,Slot:"head"}],display:{Name:"§fSturdy Cloth Cap",color:16768959,Lore:["§9Cloth Armor","§8King's Valley : Tier I"]},ench:[{id:34s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§fSturdy Cloth Shirt"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.5d,Operation:0,UUIDLeast:903793l,UUIDMost:270399l,Slot:"chest"}],display:{Name:"§fSturdy Cloth Shirt",color:16768959,Lore:["§9Cloth Armor","§8King's Valley : Tier I"]},ench:[{id:34s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§fSturdy Cloth Pants"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.0d,Operation:0,UUIDLeast:1003793l,UUIDMost:280399l,Slot:"legs"}],display:{Name:"§fSturdy Cloth Pants",color:16768959,Lore:["§9Cloth Armor","§8King's Valley : Tier I"]},ench:[{id:34s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§fSturdy Cloth Shoes"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:1103793l,UUIDMost:290399l,Slot:"feet"}],display:{Name:"§fSturdy Cloth Shoes",color:16768959,Lore:["§9Cloth Armor","§8King's Valley : Tier I"]},ench:[{id:34s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§fInfused Cloth Helm"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:803793l,UUIDMost:260399l,Slot:"head"}],display:{Name:"§fInfused Cloth Helm",color:16752543,Lore:["§9Cloth Armor","§8King's Valley : Tier I"]},ench:[{id:0s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§fInfused Cloth Cloak"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.5d,Operation:0,UUIDLeast:903793l,UUIDMost:270399l,Slot:"chest"}],display:{Name:"§fInfused Cloth Cloak",color:16752543,Lore:["§9Cloth Armor","§8King's Valley : Tier I"]},ench:[{id:0s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§fInfused Cloth Leggings"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.0d,Operation:0,UUIDLeast:1003793l,UUIDMost:280399l,Slot:"legs"}],display:{Name:"§fInfused Cloth Leggings",color:16752543,Lore:["§9Cloth Armor","§8King's Valley : Tier I"]},ench:[{id:0s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§fInfused Cloth Shoes"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:1103793l,UUIDMost:290399l,Slot:"feet"}],display:{Name:"§fInfused Cloth Shoes",color:16752543,Lore:["§9Cloth Armor","§8King's Valley : Tier I"]},ench:[{id:0s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§fPadded Cloth Coif"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:803793l,UUIDMost:260399l,Slot:"head"}],display:{Name:"§fPadded Cloth Coif",color:10461087,Lore:["§9Cloth Armor","§8King's Valley : Tier I"]},ench:[{id:4s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§fPadded Cloth Tunic"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.5d,Operation:0,UUIDLeast:903793l,UUIDMost:270399l,Slot:"chest"}],display:{Name:"§fPadded Cloth Tunic",color:10461087,Lore:["§9Cloth Armor","§8King's Valley : Tier I"]},ench:[{id:4s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§fPadded Cloth Trousers"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.0d,Operation:0,UUIDLeast:1003793l,UUIDMost:280399l,Slot:"legs"}],display:{Name:"§fPadded Cloth Trousers",color:10461087,Lore:["§9Cloth Armor","§8King's Valley : Tier I"]},ench:[{id:4s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§fPadded Cloth Boots"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:1103793l,UUIDMost:290399l,Slot:"feet"}],display:{Name:"§fPadded Cloth Boots",color:10461087,Lore:["§9Cloth Armor","§8King's Valley : Tier I"]},ench:[{id:4s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§fLeafweave Veil"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:803793l,UUIDMost:260399l,Slot:"head"}],display:{Name:"§fLeafweave Veil",color:12582847,Lore:["§9Cloth Armor","§8King's Valley : Tier I"]},ench:[{id:1s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§fLeafweave Vest"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.5d,Operation:0,UUIDLeast:903793l,UUIDMost:270399l,Slot:"chest"}],display:{Name:"§fLeafweave Vest",color:12582847,Lore:["§9Cloth Armor","§8King's Valley : Tier I"]},ench:[{id:1s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§fLeafweave Trousers"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.0d,Operation:0,UUIDLeast:1003793l,UUIDMost:280399l,Slot:"legs"}],display:{Name:"§fLeafweave Trousers",color:12582847,Lore:["§9Cloth Armor","§8King's Valley : Tier I"]},ench:[{id:1s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§fLeafweave Sandals"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:1103793l,UUIDMost:290399l,Slot:"feet"}],display:{Name:"§fLeafweave Sandals",color:12582847,Lore:["§9Cloth Armor","§8King's Valley : Tier I"]},ench:[{id:1s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§fBinding Coif"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:803793l,UUIDMost:260399l,Slot:"head"}],display:{Name:"§fBinding Coif",color:4194304,Lore:["§9Cloth Armor","§8King's Valley : Tier I"]},ench:[{id:0s,lvl:1s},{id:4s,lvl:1s},{id:10s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§fBinding Robes"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.5d,Operation:0,UUIDLeast:903793l,UUIDMost:270399l,Slot:"chest"}],display:{Name:"§fBinding Robes",color:4194304,Lore:["§9Cloth Armor","§8King's Valley : Tier I"]},ench:[{id:0s,lvl:1s},{id:4s,lvl:1s},{id:10s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§fBinding Robes"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.0d,Operation:0,UUIDLeast:1003793l,UUIDMost:280399l,Slot:"legs"}],display:{Name:"§fBinding Robes",color:4194304,Lore:["§9Cloth Armor","§8King's Valley : Tier I"]},ench:[{id:0s,lvl:1s},{id:4s,lvl:1s},{id:10s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§fBinding Boots"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:1103793l,UUIDMost:290399l,Slot:"feet"}],display:{Name:"§fBinding Boots",color:4194304,Lore:["§9Cloth Armor","§8King's Valley : Tier I"]},ench:[{id:0s,lvl:1s},{id:4s,lvl:1s},{id:10s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§fHobnailed Helm"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:803793l,UUIDMost:260399l,Slot:"head"}],display:{Name:"§fHobnailed Helm",color:7393328,Lore:["§9Cloth Armor","§8King's Valley : Tier I"]},ench:[{id:3s,lvl:1s},{id:7s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§fHobnailed Vest"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.5d,Operation:0,UUIDLeast:903793l,UUIDMost:270399l,Slot:"chest"}],display:{Name:"§fHobnailed Vest",color:7393328,Lore:["§9Cloth Armor","§8King's Valley : Tier I"]},ench:[{id:3s,lvl:1s},{id:7s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§fHobnailed Leggings"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.0d,Operation:0,UUIDLeast:1003793l,UUIDMost:280399l,Slot:"legs"}],display:{Name:"§fHobnailed Leggings",color:7393328,Lore:["§9Cloth Armor","§8King's Valley : Tier I"]},ench:[{id:3s,lvl:1s},{id:7s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§fHobnailed Boots"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:1103793l,UUIDMost:290399l,Slot:"feet"}],display:{Name:"§fHobnailed Boots",color:7393328,Lore:["§9Cloth Armor","§8King's Valley : Tier I"]},ench:[{id:3s,lvl:1s},{id:7s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"nbt":ur'''{display:{Name:"§fTempered Ironwood Blade"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fTempered Ironwood Blade",Lore:["§8King's Valley : Tier II"]},ench:[{id:34s,lvl:2s},{id:16s,lvl:1s},{id:21s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"nbt":ur'''{display:{Name:"§fSculpted Dagger"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fSculpted Dagger",Lore:["§8King's Valley : Tier II"]},ench:[{id:16s,lvl:3s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"nbt":ur'''{display:{Name:"§fAshen Broadsword"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fAshen Broadsword",Lore:["§8King's Valley : Tier II"]},ench:[{id:22s,lvl:2s},{id:20s,lvl:1s},{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"nbt":ur'''{display:{Name:"§fPriest's Stake"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fPriest's Stake",Lore:["§8King's Valley : Tier II"]},ench:[{id:34s,lvl:3s},{id:17s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"nbt":ur'''{display:{Name:"§fVersatile Knife"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fVersatile Knife",Lore:["§8King's Valley : Tier II"]},ench:[{id:16s,lvl:1s},{id:18s,lvl:2s},{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"nbt":ur'''{display:{Name:"§fSearing Gladius"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fSearing Gladius",Lore:["§8King's Valley : Tier II"]},ench:[{id:20s,lvl:1s},{id:19s,lvl:2s},{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"nbt":ur'''{display:{Name:"§fBurning Rapier"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fBurning Rapier",Lore:["§8King's Valley : Tier II"]},ench:[{id:20s,lvl:1s},{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"nbt":ur'''{display:{Name:"§fSoldier's Blade"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fSoldier's Blade",Lore:["§8King's Valley : Tier II"]},ench:[{id:16s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"nbt":ur'''{display:{Name:"§fGranite Sabre"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fGranite Sabre",Lore:["§8King's Valley : Tier II"]},ench:[{id:34s,lvl:3s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"nbt":ur'''{display:{Name:"§fRogue's Knife"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:51s}],HideFlags:1,display:{Lore:["§8King's Valley : Tier II"],Name:"§fRogue's Knife"},AttributeModifiers:[{UUIDMost:912265l,UUIDLeast:500295l,Amount:0.2d,Slot:"offhand",AttributeName:"generic.attackSpeed",Operation:1,Name:"generic.attackSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"nbt":ur'''{display:{Name:"§fSurvivalist's Sword"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:51s}],HideFlags:1,display:{Lore:["§8King's Valley : Tier II"],Name:"§fSurvivalist's Sword"},AttributeModifiers:[{UUIDMost:637136l,UUIDLeast:234308l,Amount:2d,Slot:"offhand",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"nbt":ur'''{display:{Name:"§fWarhammer"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fWarhammer",Lore:["§8King's Valley : Tier II"]},ench:[{id:19s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"nbt":ur'''{display:{Name:"§fMasterwork Axe"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fMasterwork Axe",Lore:["§8King's Valley : Tier II"]},ench:[{id:32s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_axe",
			"nbt":ur'''{display:{Name:"§fHoned Swiftwood Axe"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fHoned Swiftwood Axe",Lore:["§8King's Valley : Tier II"]},ench:[{id:32s,lvl:3s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_axe",
			"nbt":ur'''{display:{Name:"§fVersatile Axe"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fVersatile Axe",Lore:["§8King's Valley : Tier II"]},ench:[{id:34s,lvl:2s},{id:16s,lvl:1s},{id:32s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_axe",
			"nbt":ur'''{display:{Name:"§fSmoldering Mace"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fSmoldering Mace",Lore:["§8King's Valley : Tier II"]},ench:[{id:17s,lvl:1s},{id:34s,lvl:1s},{id:20s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_pickaxe",
			"nbt":ur'''{display:{Name:"§fBluefell Chisel"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fBluefell Chisel",Lore:["§8King's Valley : Tier II"]},ench:[{id:32s,lvl:2s},{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_pickaxe",
			"nbt":ur'''{display:{Name:"§fMiner's Pick"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fMiner's Pick",Lore:["§8King's Valley : Tier II"]},ench:[{id:35s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_pickaxe",
			"nbt":ur'''{display:{Name:"§fGranite Pickaxe"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fGranite Pickaxe",Lore:["§8King's Valley : Tier II"]},ench:[{id:34s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_shovel",
			"nbt":ur'''{display:{Name:"§fGrassbane"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fGrassbane",Lore:["§8King's Valley : Tier II"]},ench:[{id:32s,lvl:3s},{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stick",
			"nbt":ur'''{display:{Name:"§fStudent's Wand"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fStudent's Wand",Lore:["§8* Magic Wand *","§8King's Valley : Tier II"]},ench:[{id:19s,lvl:1s},{id:20s,lvl:1s},{id:16s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:blaze_rod",
			"nbt":ur'''{display:{Name:"§fFlame Wand"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fFlame Wand",Lore:["§8* Magic Wand *","§8King's Valley : Tier II"]},ench:[{id:19s,lvl:2s},{id:20s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_hoe",
			"nbt":ur'''{display:{Name:"§fPeasant's Scythe"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fPeasant's Scythe",Lore:["§8King's Valley : Tier II"]},ench:[{id:16s,lvl:3s},{id:17s,lvl:1s},{id:21s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:bow",
			"nbt":ur'''{display:{Name:"§fIronwood Bow"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fIronwood Bow",Lore:["§8King's Valley : Tier II"]},ench:[{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:bow",
			"nbt":ur'''{display:{Name:"§fLongbow"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fLongbow",Lore:["§8King's Valley : Tier II"]},ench:[{id:49s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§fBandit's Cap"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:803793l,UUIDMost:260399l,Slot:"head"}],display:{Name:"§fBandit's Cap",color:5197647,Lore:["§9Cloth Armor","§8King's Valley : Tier II"]},ench:[{id:4s,lvl:2s},{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§fBandit's Tunic"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.5d,Operation:0,UUIDLeast:903793l,UUIDMost:270399l,Slot:"chest"}],display:{Name:"§fBandit's Tunic",color:5197647,Lore:["§9Cloth Armor","§8King's Valley : Tier II"]},ench:[{id:4s,lvl:2s},{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§fBandit's Trousers"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.0d,Operation:0,UUIDLeast:1003793l,UUIDMost:280399l,Slot:"legs"}],display:{Name:"§fBandit's Trousers",color:5197647,Lore:["§9Cloth Armor","§8King's Valley : Tier II"]},ench:[{id:4s,lvl:2s},{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§fBandit's Boots"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:1103793l,UUIDMost:290399l,Slot:"feet"}],display:{Name:"§fBandit's Boots",color:5197647,Lore:["§9Cloth Armor","§8King's Valley : Tier II"]},ench:[{id:4s,lvl:2s},{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§fCrimson Mage Hat"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:803793l,UUIDMost:260399l,Slot:"head"}],display:{Name:"§fCrimson Mage Hat",color:12517599,Lore:["§9Cloth Armor","§8King's Valley : Tier II"]},ench:[{id:0s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§fCrimson Mage Robes"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.5d,Operation:0,UUIDLeast:903793l,UUIDMost:270399l,Slot:"chest"}],display:{Name:"§fCrimson Mage Robes",color:12517599,Lore:["§9Cloth Armor","§8King's Valley : Tier II"]},ench:[{id:0s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§fCrimson Mage Robes"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.0d,Operation:0,UUIDLeast:1003793l,UUIDMost:280399l,Slot:"legs"}],display:{Name:"§fCrimson Mage Robes",color:12517599,Lore:["§9Cloth Armor","§8King's Valley : Tier II"]},ench:[{id:0s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§fCrimson Mage Robes"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:1103793l,UUIDMost:290399l,Slot:"feet"}],display:{Name:"§fCrimson Mage Robes",color:12517599,Lore:["§9Cloth Armor","§8King's Valley : Tier II"]},ench:[{id:0s,lvl:1s},{id:2s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§fThornskin Veil"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:803793l,UUIDMost:260399l,Slot:"head"}],display:{Name:"§fThornskin Veil",color:4185951,Lore:["§9Cloth Armor","§8King's Valley : Tier II"]},ench:[{id:7s,lvl:3s},{id:34s,lvl:3s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§fThornskin Robe"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.5d,Operation:0,UUIDLeast:903793l,UUIDMost:270399l,Slot:"chest"}],display:{Name:"§fThornskin Robe",color:4185951,Lore:["§9Cloth Armor","§8King's Valley : Tier II"]},ench:[{id:7s,lvl:3s},{id:34s,lvl:3s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§fThornskin Robe"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.0d,Operation:0,UUIDLeast:1003793l,UUIDMost:280399l,Slot:"legs"}],display:{Name:"§fThornskin Robe",color:4185951,Lore:["§9Cloth Armor","§8King's Valley : Tier II"]},ench:[{id:7s,lvl:3s},{id:34s,lvl:3s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§fThornskin Shoes"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:1103793l,UUIDMost:290399l,Slot:"feet"}],display:{Name:"§fThornskin Shoes",color:4185951,Lore:["§9Cloth Armor","§8King's Valley : Tier II"]},ench:[{id:7s,lvl:3s},{id:34s,lvl:3s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§fAlchemist's Helm"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:803793l,UUIDMost:260399l,Slot:"head"}],display:{Name:"§fAlchemist's Helm",color:16776960,Lore:["§9Cloth Armor","§8King's Valley : Tier II"]},ench:[{id:1s,lvl:2s},{id:3s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§fAlchemist's Apron"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:1s},{lvl:1s,id:3s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier II"],color:16776960,Name:"§fAlchemist's Apron"},AttributeModifiers:[{UUIDMost:270399l,UUIDLeast:903793l,Amount:1.5d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§fAlchemist's Robe"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.0d,Operation:0,UUIDLeast:1003793l,UUIDMost:280399l,Slot:"legs"}],display:{Name:"§fAlchemist's Robe",color:16776960,Lore:["§9Cloth Armor","§8King's Valley : Tier II"]},ench:[{id:1s,lvl:2s},{id:3s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§fAlchemist's Boots"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:1103793l,UUIDMost:290399l,Slot:"feet"}],display:{Name:"§fAlchemist's Boots",color:16776960,Lore:["§9Cloth Armor","§8King's Valley : Tier II"]},ench:[{id:1s,lvl:2s},{id:3s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§fTurtle Helm"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:803793l,UUIDMost:260399l,Slot:"head"}],display:{Name:"§fTurtle Helm",color:36912,Lore:["§9Cloth Armor","§8King's Valley : Tier II"]},ench:[{id:5s,lvl:1s},{id:3s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§fTurtle Vest"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.5d,Operation:0,UUIDLeast:903793l,UUIDMost:270399l,Slot:"chest"}],display:{Name:"§fTurtle Vest",color:36912,Lore:["§9Cloth Armor","§8King's Valley : Tier II"]},ench:[{id:6s,lvl:1s},{id:3s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§fTurtle Pants"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.0d,Operation:0,UUIDLeast:1003793l,UUIDMost:280399l,Slot:"legs"}],display:{Name:"§fTurtle Pants",color:36912,Lore:["§9Cloth Armor","§8King's Valley : Tier II"]},ench:[{id:8s,lvl:1s},{id:3s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§fTurtle Flippers"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:1103793l,UUIDMost:290399l,Slot:"feet"}],display:{Name:"§fTurtle Flippers",color:36912,Lore:["§9Cloth Armor","§8King's Valley : Tier II"]},ench:[{id:8s,lvl:1s},{id:3s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§fPuresilk Coif"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:803793l,UUIDMost:260399l,Slot:"head"},{UUIDMost:260399l,UUIDLeast:803793l,Amount:0.02d,Slot:"head",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}],display:{Name:"§fPuresilk Coif",color:12636415,Lore:["§9Cloth Armor","§8King's Valley : Tier II"]},ench:[{id:0s,lvl:1s},{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§fPuresilk Tunic"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.5d,Operation:0,UUIDLeast:903793l,UUIDMost:270399l,Slot:"chest"},{UUIDMost:270399l,UUIDLeast:903793l,Amount:0.02d,Slot:"chest",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}],display:{Name:"§fPuresilk Tunic",color:12636415,Lore:["§9Cloth Armor","§8King's Valley : Tier II"]},ench:[{id:0s,lvl:1s},{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§fPuresilk Leggings"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.0d,Operation:0,UUIDLeast:1003793l,UUIDMost:280399l,Slot:"legs"},{UUIDMost:280399l,UUIDLeast:1003793l,Amount:0.02d,Slot:"legs",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}],display:{Name:"§fPuresilk Leggings",color:12636415,Lore:["§9Cloth Armor","§8King's Valley : Tier II"]},ench:[{id:0s,lvl:1s},{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§fPuresilk Slippers"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:1103793l,UUIDMost:290399l,Slot:"feet"},{UUIDMost:290399l,UUIDLeast:1103793l,Amount:0.02d,Slot:"feet",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}],display:{Name:"§fPuresilk Slippers",color:12636415,Lore:["§9Cloth Armor","§8King's Valley : Tier II"]},ench:[{id:0s,lvl:1s},{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"nbt":ur'''{display:{Name:"§fLiving Thorn"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fLiving Thorn",Lore:["§8King's Valley : Tier III"]},ench:[{id:16s,lvl:1s},{id:70s,lvl:1s},{id:18s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"nbt":ur'''{display:{Name:"§fCrusader's Sword"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fCrusader's Sword",Lore:["§8King's Valley : Tier III"]},ench:[{id:34s,lvl:1s},{id:17s,lvl:3s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"nbt":ur'''{display:{Name:"§fLight Scimitar"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fLight Scimitar",Lore:["§8King's Valley : Tier III"]},ench:[{id:34s,lvl:1s},{id:16s,lvl:2s},{id:22s,lvl:3s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"nbt":ur'''{display:{Name:"§fFlamewreath Splinter"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fFlamewreath Splinter",Lore:["§8King's Valley : Tier III"]},ench:[{id:20s,lvl:3s},{id:19s,lvl:2s},{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"nbt":ur'''{display:{Name:"§fThief's Dagger"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fThief's Dagger",Lore:["§8King's Valley : Tier III"]},ench:[{id:16s,lvl:2s},{id:34s,lvl:1s},{id:21s,lvl:4s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"nbt":ur'''{display:{Name:"§fBrigand's Rapier"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fBrigand's Rapier",Lore:["§8King's Valley : Tier III"]},ench:[{id:20s,lvl:2s},{id:21s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"nbt":ur'''{display:{Name:"§fHoned Claymore"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fHoned Claymore",Lore:["§8King's Valley : Tier III"]},ench:[{id:22s,lvl:1s},{id:34s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"nbt":ur'''{display:{Name:"§fRitual Knife"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fRitual Knife",Lore:["§8King's Valley : Tier III"]},ench:[{id:34s,lvl:1s},{id:17s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"nbt":ur'''{display:{Name:"§fTrusty Dagger"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fTrusty Dagger",Lore:["§8King's Valley : Tier III"]},ench:[{id:34s,lvl:1s},{id:16s,lvl:1s},{id:18s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"nbt":ur'''{display:{Name:"§fScoundrel's Rapier"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:51s}],HideFlags:1,display:{Lore:["§8King's Valley : Tier III"],Name:"§fScoundrel's Rapier"},AttributeModifiers:[{UUIDMost:157078l,UUIDLeast:786990l,Amount:2d,Slot:"offhand",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"nbt":ur'''{display:{Name:"§fPoisoned Shank"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:51s}],HideFlags:1,display:{Lore:["§8King's Valley : Tier III"],Name:"§fPoisoned Shank"},AttributeModifiers:[{UUIDMost:298381l,UUIDLeast:495523l,Amount:0.15d,Slot:"offhand",AttributeName:"generic.attackDamage",Operation:1,Name:"generic.attackDamage"}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_axe",
			"nbt":ur'''{display:{Name:"§fMeteor Hammer"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fMeteor Hammer",Lore:["§8King's Valley : Tier III"]},ench:[{id:20s,lvl:2s},{id:16s,lvl:4s},{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_axe",
			"nbt":ur'''{display:{Name:"§fTempered Mace"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fTempered Mace",Lore:["§8King's Valley : Tier III"]},ench:[{id:16s,lvl:2s},{id:34s,lvl:2s},{id:19s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"nbt":ur'''{display:{Name:"§fWoodsman's Axe"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fWoodsman's Axe",Lore:["§8King's Valley : Tier III"]},ench:[{id:32s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"nbt":ur'''{display:{Name:"§fHeavy Warhammer"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fHeavy Warhammer",Lore:["§8King's Valley : Tier III"]},ench:[{id:19s,lvl:1s},{id:16s,lvl:1s},{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"nbt":ur'''{display:{Name:"§fJagged Cleaver"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fJagged Cleaver",Lore:["§8King's Valley : Tier III"]},ench:[{id:16s,lvl:2s},{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"nbt":ur'''{display:{Name:"§fInferno Axe"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fInferno Axe",Lore:["§8King's Valley : Tier III"]},ench:[{id:32s,lvl:1s},{id:20s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_pickaxe",
			"nbt":ur'''{display:{Name:"§fSapper's Tool"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fSapper's Tool",Lore:["§8King's Valley : Tier III"]},ench:[{id:32s,lvl:2s},{id:34s,lvl:2s},{id:19s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_pickaxe",
			"nbt":ur'''{display:{Name:"§fMasterwork Pickaxe"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fMasterwork Pickaxe",Lore:["§8King's Valley : Tier III"]},ench:[{id:32s,lvl:1s},{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_pickaxe",
			"nbt":ur'''{display:{Name:"§fRunic Pickaxe"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fRunic Pickaxe",Lore:["§8King's Valley : Tier III"]},ench:[{id:35s,lvl:2s},{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_pickaxe",
			"nbt":ur'''{display:{Name:"§fResiliant Pickaxe"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fResiliant Pickaxe",Lore:["§8King's Valley : Tier III"]},ench:[{id:34s,lvl:5s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_shovel",
			"nbt":ur'''{display:{Name:"§fArrowmeld"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fArrowmeld",Lore:["§8King's Valley : Tier III"]},ench:[{id:35s,lvl:3s},{id:34s,lvl:3s}]}'''
		]
	],
	[
		{
			"id":"minecraft:shield",
			"nbt":ur'''{display:{Name:"§fHardened Shield"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fHardened Shield",Lore:["§8King's Valley : Tier III"]},ench:[{id:34s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:bow",
			"nbt":ur'''{display:{Name:"§fHawk's Talon"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fHawk's Talon",Lore:["§8King's Valley : Tier III"]},ench:[{id:48s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:bow",
			"nbt":ur'''{display:{Name:"§fCrossbow"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fCrossbow",Lore:["§8King's Valley : Tier III"]},ench:[{id:49s,lvl:1s},{id:34s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:bow",
			"nbt":ur'''{display:{Name:"§fSearing Bow"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fSearing Bow",Lore:["§8King's Valley : Tier III"]},ench:[{id:50s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:fishing_rod",
			"nbt":ur'''{display:{Name:"§fAngler's Rod"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fAngler's Rod",Lore:["§8King's Valley : Tier III"]},ench:[{id:34s,lvl:2s},{id:62s,lvl:3s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stick",
			"nbt":ur'''{display:{Name:"§fApprentice's Wand"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fApprentice's Wand",Lore:["§8* Magic Wand *","§8King's Valley : Tier III"]},ench:[{id:19s,lvl:1s},{id:20s,lvl:1s},{id:16s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stick",
			"nbt":ur'''{display:{Name:"§fConsecrated Wand"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fConsecrated Wand",Lore:["§8* Magic Wand *","§8King's Valley : Tier III"]},ench:[{id:17s,lvl:2s},{id:19s,lvl:1s},{id:21s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_hoe",
			"nbt":ur'''{display:{Name:"§fRuffian's Scythe"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fRuffian's Scythe",Lore:["§8King's Valley : Tier III"]},ench:[{id:16s,lvl:4s},{id:17s,lvl:1s},{id:21s,lvl:1s},{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§fSky Mage Coif"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:803793l,UUIDMost:260399l,Slot:"head"}],display:{Name:"§fSky Mage Coif",color:10531071,Lore:["§9Cloth Armor","§8King's Valley : Tier III"]},ench:[{id:0s,lvl:1s},{id:34s,lvl:2s},{id:2s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§fSky Mage Cloak"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.5d,Operation:0,UUIDLeast:903793l,UUIDMost:270399l,Slot:"chest"}],display:{Name:"§fSky Mage Cloak",color:10531071,Lore:["§9Cloth Armor","§8King's Valley : Tier III"]},ench:[{id:0s,lvl:1s},{id:34s,lvl:2s},{id:2s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§fSky Mage Robe"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.0d,Operation:0,UUIDLeast:1003793l,UUIDMost:280399l,Slot:"legs"}],display:{Name:"§fSky Mage Robe",color:10531071,Lore:["§9Cloth Armor","§8King's Valley : Tier III"]},ench:[{id:0s,lvl:1s},{id:34s,lvl:2s},{id:2s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§fSky Mage Slippers"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:1103793l,UUIDMost:290399l,Slot:"feet"}],display:{Name:"§fSky Mage Slippers",color:10531071,Lore:["§9Cloth Armor","§8King's Valley : Tier III"]},ench:[{id:0s,lvl:1s},{id:34s,lvl:2s},{id:2s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§fScoundrel's Hood"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:803793l,UUIDMost:260399l,Slot:"head"}],display:{Name:"§fScoundrel's Hood",color:2109472,Lore:["§9Cloth Armor","§8King's Valley : Tier III"]},ench:[{id:4s,lvl:3s},{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§fScoundrel's Tunic"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.5d,Operation:0,UUIDLeast:903793l,UUIDMost:270399l,Slot:"chest"}],display:{Name:"§fScoundrel's Tunic",color:2109472,Lore:["§9Cloth Armor","§8King's Valley : Tier III"]},ench:[{id:4s,lvl:3s},{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§fScoundrel's Trousers"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.0d,Operation:0,UUIDLeast:1003793l,UUIDMost:280399l,Slot:"legs"}],display:{Name:"§fScoundrel's Trousers",color:2109472,Lore:["§9Cloth Armor","§8King's Valley : Tier III"]},ench:[{id:4s,lvl:3s},{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§fScoundrel's Slippers"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:1103793l,UUIDMost:290399l,Slot:"feet"}],display:{Name:"§fScoundrel's Slippers",color:2109472,Lore:["§9Cloth Armor","§8King's Valley : Tier III"]},ench:[{id:4s,lvl:3s},{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§fSpellweave Hat"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:803793l,UUIDMost:260399l,Slot:"head"}],display:{Name:"§fSpellweave Hat",color:11555008,Lore:["§9Cloth Armor","§8King's Valley : Tier III"]},ench:[{id:0s,lvl:2s},{id:34s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§fSpellweave Tunic"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.5d,Operation:0,UUIDLeast:903793l,UUIDMost:270399l,Slot:"chest"}],display:{Name:"§fSpellweave Tunic",color:11555008,Lore:["§9Cloth Armor","§8King's Valley : Tier III"]},ench:[{id:0s,lvl:2s},{id:34s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§fSpellweave Trousers"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.0d,Operation:0,UUIDLeast:1003793l,UUIDMost:280399l,Slot:"legs"}],display:{Name:"§fSpellweave Trousers",color:11555008,Lore:["§9Cloth Armor","§8King's Valley : Tier III"]},ench:[{id:0s,lvl:2s},{id:34s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§fSpellweave Shoes"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:1103793l,UUIDMost:290399l,Slot:"feet"}],display:{Name:"§fSpellweave Shoes",color:11555008,Lore:["§9Cloth Armor","§8King's Valley : Tier III"]},ench:[{id:0s,lvl:2s},{id:34s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§fBlast Visor"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fBlast Visor",color:5597999,Lore:["§bLeather Armor","§8King's Valley : Tier III"]},ench:[{id:3s,lvl:2s},{id:34s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§fBlast Vest"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fBlast Vest",color:5597999,Lore:["§bLeather Armor","§8King's Valley : Tier III"]},ench:[{id:3s,lvl:2s},{id:34s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§fBlast Apron"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fBlast Apron",color:5597999,Lore:["§bLeather Armor","§8King's Valley : Tier III"]},ench:[{id:3s,lvl:2s},{id:34s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§fBlast Boots"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fBlast Boots",color:5597999,Lore:["§bLeather Armor","§8King's Valley : Tier III"]},ench:[{id:3s,lvl:2s},{id:34s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§fBurnt Helm"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fBurnt Helm",color:7352328,Lore:["§bLeather Armor","§8King's Valley : Tier III"]},ench:[{id:1s,lvl:3s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§fBurnt Cloak"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fBurnt Cloak",color:7352328,Lore:["§bLeather Armor","§8King's Valley : Tier III"]},ench:[{id:1s,lvl:3s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§fBurnt Leggings"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fBurnt Leggings",color:7352328,Lore:["§bLeather Armor","§8King's Valley : Tier III"]},ench:[{id:1s,lvl:3s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§fBurnt Boots"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fBurnt Boots",color:7352328,Lore:["§bLeather Armor","§8King's Valley : Tier III"]},ench:[{id:1s,lvl:3s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§fWarlock Helm"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:803793l,UUIDMost:260399l,Slot:"head"}],display:{Name:"§fWarlock Helm",color:14725264,Lore:["§9Cloth Armor","§8King's Valley : Tier III"]},ench:[{lvl:1s,id:1s},{lvl:4s,id:34s},{lvl:1s,id:10s},{lvl:1s,id:3s},{lvl:1s,id:4s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§fWarlock Robe"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.5d,Operation:0,UUIDLeast:903793l,UUIDMost:270399l,Slot:"chest"}],display:{Name:"§fWarlock Robe",color:14725264,Lore:["§9Cloth Armor","§8King's Valley : Tier III"]},ench:[{lvl:1s,id:1s},{lvl:4s,id:34s},{lvl:1s,id:10s},{lvl:1s,id:3s},{lvl:1s,id:4s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§fWarlock Robe"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.0d,Operation:0,UUIDLeast:1003793l,UUIDMost:280399l,Slot:"legs"}],display:{Name:"§fWarlock Robe",color:14725264,Lore:["§9Cloth Armor","§8King's Valley : Tier III"]},ench:[{lvl:1s,id:1s},{lvl:4s,id:34s},{lvl:1s,id:10s},{lvl:1s,id:3s},{lvl:1s,id:4s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§fWarlock Boots"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:1103793l,UUIDMost:290399l,Slot:"feet"}],display:{Name:"§fWarlock Boots",color:14725264,Lore:["§9Cloth Armor","§8King's Valley : Tier III"]},ench:[{lvl:1s,id:1s},{lvl:4s,id:34s},{lvl:1s,id:10s},{lvl:1s,id:3s},{lvl:1s,id:4s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"nbt":ur'''{display:{Name:"§fVicious Thorn"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fVicious Thorn",Lore:["§8King's Valley : Tier IV"]},ench:[{id:16s,lvl:2s},{id:70s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"nbt":ur'''{display:{Name:"§fGodwood Sword"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fGodwood Sword",Lore:["§8King's Valley : Tier IV"]},ench:[{id:34s,lvl:2s},{id:20s,lvl:2s},{id:17s,lvl:2s},{id:19s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"nbt":ur'''{display:{Name:"§fDruidic Broadsword"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fDruidic Broadsword",Lore:["§8King's Valley : Tier IV"]},ench:[{id:34s,lvl:2s},{id:20s,lvl:2s},{id:22s,lvl:2s},{id:16s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"nbt":ur'''{display:{Name:"§fPonderous Branch"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fPonderous Branch",Lore:["§8King's Valley : Tier IV"]},ench:[{id:16s,lvl:1s},{id:19s,lvl:2s},{id:34s,lvl:4s},{id:17s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"nbt":ur'''{display:{Name:"§fNest's Bane"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fNest's Bane",Lore:["§8King's Valley : Tier IV"]},ench:[{id:17s,lvl:1s},{id:34s,lvl:1s},{id:16s,lvl:1s},{id:32s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"nbt":ur'''{display:{Name:"§fOfficer's Blade"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fOfficer's Blade",Lore:["§8King's Valley : Tier IV"]},ench:[{id:22s,lvl:1s},{id:16s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"nbt":ur'''{display:{Name:"§fInfernal Dagger"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fInfernal Dagger",Lore:["§8King's Valley : Tier IV"]},ench:[{id:20s,lvl:2s},{id:19s,lvl:1s},{id:17s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"nbt":ur'''{display:{Name:"§fMasterwork Sabre"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fMasterwork Sabre",Lore:["§8King's Valley : Tier IV"]},ench:[{id:16s,lvl:1s},{id:34s,lvl:5s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"nbt":ur'''{display:{Name:"§fDuelist's Sword"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:51s}],HideFlags:1,display:{Lore:["§8King's Valley : Tier IV"],Name:"§fDuelist's Sword"},AttributeModifiers:[{UUIDMost:298381l,UUIDLeast:495523l,Amount:0.05d,Slot:"offhand",AttributeName:"generic.attackDamage",Operation:1,Name:"generic.attackDamage"},{UUIDMost:157078l,UUIDLeast:786990l,Amount:2d,Slot:"offhand",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"nbt":ur'''{display:{Name:"§fAssassin's Dagger"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:51s}],HideFlags:1,display:{Lore:["§8King's Valley : Tier IV"],Name:"§fAssassin's Dagger"},AttributeModifiers:[{UUIDMost:743378l,UUIDLeast:575520l,Amount:0.15d,Slot:"offhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_axe",
			"nbt":ur'''{display:{Name:"§fFalling Comet"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fFalling Comet",Lore:["§8King's Valley : Tier IV"]},ench:[{id:20s,lvl:3s},{id:16s,lvl:3s},{id:34s,lvl:2s},{id:17s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_axe",
			"nbt":ur'''{display:{Name:"§fDeforester"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fDeforester",Lore:["§8King's Valley : Tier IV"]},ench:[{id:32s,lvl:4s},{id:34s,lvl:3s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"nbt":ur'''{display:{Name:"§fCutter"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fCutter",Lore:["§8King's Valley : Tier IV"]},ench:[{id:34s,lvl:2s},{id:32s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"nbt":ur'''{display:{Name:"§fDivine Cleaver"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fDivine Cleaver",Lore:["§8King's Valley : Tier IV"]},ench:[{id:21s,lvl:1s},{id:17s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"nbt":ur'''{display:{Name:"§fBattle Axe"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fBattle Axe",Lore:["§8King's Valley : Tier IV"]},ench:[{id:34s,lvl:3s},{id:16s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_pickaxe",
			"nbt":ur'''{display:{Name:"§fBluescourge Chisel"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fBluescourge Chisel",Lore:["§8King's Valley : Tier IV"]},ench:[{id:32s,lvl:3s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_pickaxe",
			"nbt":ur'''{display:{Name:"§fCoal Devourer"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fCoal Devourer",Lore:["§8King's Valley : Tier IV"]},ench:[{id:35s,lvl:4s},{id:34s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_pickaxe",
			"nbt":ur'''{display:{Name:"§fBalanced Adze"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fBalanced Adze",Lore:["§8King's Valley : Tier IV"]},ench:[{id:32s,lvl:2s},{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_pickaxe",
			"nbt":ur'''{display:{Name:"§fBountiful Chisel"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fBountiful Chisel",Lore:["§8King's Valley : Tier IV"]},ench:[{id:35s,lvl:3s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_hoe",
			"nbt":ur'''{display:{Name:"§fRebel's Scythe"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fRebel's Scythe",Lore:["§8King's Valley : Tier IV"]},ench:[{id:16s,lvl:5s},{id:17s,lvl:1s},{id:21s,lvl:2s},{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:shield",
			"nbt":ur'''{display:{Name:"§aIronwrought Shield"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.knockbackResistance",Name:"generic.knockbackResistance",Amount:0.25d,Operation:0,UUIDLeast:816028l,UUIDMost:477084l,Slot:"offhand"}],display:{Name:"§aIronwrought Shield",Lore:["§8King's Valley : Tier IV"]}}'''
		]
	],
	[
		{
			"id":"minecraft:shield",
			"nbt":ur'''{display:{Name:"§fSpiked Buckler"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:19s}],HideFlags:2,display:{Lore:["§8King's Valley : Tier IV","§8","§7When in main hand:","§7 2.0 Attack Speed","§7 4 Attack Damage"],Name:"§fSpiked Buckler"},AttributeModifiers:[{UUIDMost:6962219233119978799l,UUIDLeast:-7099076830009706309l,Amount:3.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:bow",
			"nbt":ur'''{display:{Name:"§fPyromancer's Bow"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fPyromancer's Bow",Lore:["§8King's Valley : Tier IV"]},ench:[{id:50s,lvl:1s},{id:34s,lvl:3s}]}'''
		]
	],
	[
		{
			"id":"minecraft:bow",
			"nbt":ur'''{display:{Name:"§fComposite Bow"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fComposite Bow",Lore:["§8King's Valley : Tier IV"]},ench:[{id:48s,lvl:1s},{id:49s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_shovel",
			"nbt":ur'''{display:{Name:"§fGardener"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fGardener",Lore:["§8King's Valley : Tier IV"]},ench:[{id:32s,lvl:3s},{id:34s,lvl:3s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stick",
			"nbt":ur'''{display:{Name:"§fJourneyman's Staff"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fJourneyman's Staff",Lore:["§8* Magic Wand *","§8King's Valley : Tier IV"]},ench:[{id:19s,lvl:1s},{id:20s,lvl:2s},{id:16s,lvl:3s}]}'''
		]
	],
	[
		{
			"id":"minecraft:bone",
			"nbt":ur'''{display:{Name:"§fShaman's Staff"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fShaman's Staff",Lore:["§8* Magic Wand *","§8King's Valley : Tier IV"]},ench:[{id:18s,lvl:2s},{id:19s,lvl:1s},{id:16s,lvl:4s},{id:71s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§fCerulean Mage Hat"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:803793l,UUIDMost:260399l,Slot:"head"}],display:{Name:"§fCerulean Mage Hat",color:5214175,Lore:["§9Cloth Armor","§8King's Valley : Tier IV"]},ench:[{id:0s,lvl:2s},{id:34s,lvl:1s},{id:1s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§fCerulean Mage Robes"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.5d,Operation:0,UUIDLeast:903793l,UUIDMost:270399l,Slot:"chest"}],display:{Name:"§fCerulean Mage Robes",color:5214175,Lore:["§9Cloth Armor","§8King's Valley : Tier IV"]},ench:[{id:0s,lvl:2s},{id:34s,lvl:1s},{id:4s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§fCerulean Mage Robes"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.0d,Operation:0,UUIDLeast:1003793l,UUIDMost:280399l,Slot:"legs"}],display:{Name:"§fCerulean Mage Robes",color:5214175,Lore:["§9Cloth Armor","§8King's Valley : Tier IV"]},ench:[{id:0s,lvl:2s},{id:34s,lvl:1s},{id:3s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§fCerulean Mage Robes"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:1103793l,UUIDMost:290399l,Slot:"feet"}],display:{Name:"§fCerulean Mage Robes",color:5214175,Lore:["§9Cloth Armor","§8King's Valley : Tier IV"]},ench:[{id:0s,lvl:2s},{id:34s,lvl:1s},{id:2s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§fMolten Hood"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:803793l,UUIDMost:260399l,Slot:"head"}],display:{Name:"§fMolten Hood",color:16756736,Lore:["§9Cloth Armor","§8King's Valley : Tier IV"]},ench:[{id:1s,lvl:5s},{id:34s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§fMolten Cloak"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.5d,Operation:0,UUIDLeast:903793l,UUIDMost:270399l,Slot:"chest"}],display:{Name:"§fMolten Cloak",color:16756736,Lore:["§9Cloth Armor","§8King's Valley : Tier IV"]},ench:[{id:1s,lvl:5s},{id:34s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§fMolten Pants"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.0d,Operation:0,UUIDLeast:1003793l,UUIDMost:280399l,Slot:"legs"}],display:{Name:"§fMolten Pants",color:16756736,Lore:["§9Cloth Armor","§8King's Valley : Tier IV"]},ench:[{id:1s,lvl:5s},{id:34s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§fMolten Boots"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:1103793l,UUIDMost:290399l,Slot:"feet"}],display:{Name:"§fMolten Boots",color:16756736,Lore:["§9Cloth Armor","§8King's Valley : Tier IV"]},ench:[{id:1s,lvl:5s},{id:34s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§fCholeric Helm"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:803793l,UUIDMost:260399l,Slot:"head"}],display:{Name:"§fCholeric Helm",color:6356736,Lore:["§9Cloth Armor","§8King's Valley : Tier IV"]},ench:[{id:0s,lvl:2s},{id:34s,lvl:4s},{id:7s,lvl:5s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§fCholeric Cloak"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.5d,Operation:0,UUIDLeast:903793l,UUIDMost:270399l,Slot:"chest"}],display:{Name:"§fCholeric Cloak",color:6356736,Lore:["§9Cloth Armor","§8King's Valley : Tier IV"]},ench:[{id:0s,lvl:2s},{id:34s,lvl:4s},{id:7s,lvl:5s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§fCholeric Leggings"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.0d,Operation:0,UUIDLeast:1003793l,UUIDMost:280399l,Slot:"legs"}],display:{Name:"§fCholeric Leggings",color:6356736,Lore:["§9Cloth Armor","§8King's Valley : Tier IV"]},ench:[{id:0s,lvl:2s},{id:34s,lvl:4s},{id:7s,lvl:5s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§fCholeric Boots"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:1103793l,UUIDMost:290399l,Slot:"feet"}],display:{Name:"§fCholeric Boots",color:6356736,Lore:["§9Cloth Armor","§8King's Valley : Tier IV"]},ench:[{id:0s,lvl:2s},{id:34s,lvl:4s},{id:7s,lvl:5s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§fHeavy Leather Cap"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:4s,id:34s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier IV"],Name:"§fHeavy Leather Cap"},AttributeModifiers:[{UUIDMost:1199056757440006902l,UUIDLeast:-5031645011434854220l,Amount:0.12d,Slot:"head",AttributeName:"generic.knockbackResistance",Operation:0,Name:"Modifier"},{UUIDMost:-5675263151546941074l,UUIDLeast:-7630602400151360780l,Amount:1.0d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§fHeavy Leather Tunic"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:4s,id:34s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier IV"],Name:"§fHeavy Leather Tunic"},AttributeModifiers:[{UUIDMost:-7851645031876899907l,UUIDLeast:-7264920938634085936l,Amount:0.12d,Slot:"chest",AttributeName:"generic.knockbackResistance",Operation:0,Name:"Modifier"},{UUIDMost:-6308125112336758355l,UUIDLeast:-6141357313852679154l,Amount:3.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§fHeavy Leather Pants"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:4s,id:34s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier IV"],Name:"§fHeavy Leather Pants"},AttributeModifiers:[{UUIDMost:-5282638418670238374l,UUIDLeast:-7237081583653115127l,Amount:0.12d,Slot:"legs",AttributeName:"generic.knockbackResistance",Operation:0,Name:"Modifier"},{UUIDMost:-2983299289300778334l,UUIDLeast:-4622743005847896684l,Amount:2.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§fHeavy Leather Boots"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:4s,id:34s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier IV"],Name:"§fHeavy Leather Boots"},AttributeModifiers:[{UUIDMost:-6971162542843608331l,UUIDLeast:-9087580478696796047l,Amount:0.12d,Slot:"feet",AttributeName:"generic.knockbackResistance",Operation:0,Name:"Modifier"},{UUIDMost:1131969840074081731l,UUIDLeast:-7625908944711840236l,Amount:1.0d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§fBrigand's Coif"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fBrigand's Coif",color:8425600,Lore:["§bLeather Armor","§8King's Valley : Tier IV"]},ench:[{id:34s,lvl:1s},{id:4s,lvl:3s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§fBrigand's Tunic"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fBrigand's Tunic",color:8425600,Lore:["§bLeather Armor","§8King's Valley : Tier IV"]},ench:[{id:34s,lvl:1s},{id:4s,lvl:3s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§fBrigand's Trousers"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fBrigand's Trousers",color:8425600,Lore:["§bLeather Armor","§8King's Valley : Tier IV"]},ench:[{id:34s,lvl:1s},{id:4s,lvl:3s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§fBrigand's Shoes"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fBrigand's Shoes",color:8425600,Lore:["§bLeather Armor","§8King's Valley : Tier IV"]},ench:[{id:34s,lvl:1s},{id:4s,lvl:3s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§fGemcrust Coif"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fGemcrust Coif",color:16711935,Lore:["§bLeather Armor","§8King's Valley : Tier IV"]},ench:[{lvl:2s,id:0s},{lvl:1s,id:1s},{lvl:1s,id:71s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§fGemcrust Vest"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fGemcrust Vest",color:16711935,Lore:["§bLeather Armor","§8King's Valley : Tier IV"]},ench:[{lvl:2s,id:0s},{lvl:1s,id:1s},{lvl:1s,id:71s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§fGemcrust Pants"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fGemcrust Pants",color:16711935,Lore:["§bLeather Armor","§8King's Valley : Tier IV"]},ench:[{lvl:2s,id:0s},{lvl:1s,id:1s},{lvl:1s,id:71s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§fGemcrust Shoes"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fGemcrust Shoes",color:16711935,Lore:["§bLeather Armor","§8King's Valley : Tier IV"]},ench:[{lvl:2s,id:0s},{lvl:1s,id:1s},{lvl:1s,id:71s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"nbt":ur'''{display:{Name:"§aBloody Thorn"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§aBloody Thorn",Lore:["§8King's Valley : Tier V"]},ench:[{id:16s,lvl:2s},{id:19s,lvl:1s},{id:70s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"nbt":ur'''{display:{Name:"§aEternal Crescent"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§aEternal Crescent",Lore:["§8King's Valley : Tier V"]},ench:[{id:16s,lvl:1s},{id:22s,lvl:3s},{id:70s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"nbt":ur'''{display:{Name:"§fMacuahuitl"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fMacuahuitl",Lore:["§8King's Valley : Tier V"]},ench:[{id:16s,lvl:5s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"nbt":ur'''{display:{Name:"§fReliable Longsword"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fReliable Longsword",Lore:["§8King's Valley : Tier V"]},ench:[{id:34s,lvl:1s},{id:22s,lvl:2s},{id:16s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"nbt":ur'''{display:{Name:"§aVersatile Cutlass"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§aVersatile Cutlass",Lore:["§8King's Valley : Tier V"]},ench:[{id:17s,lvl:1s},{id:18s,lvl:1s},{id:22s,lvl:1s},{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"nbt":ur'''{display:{Name:"§aMolten Rapier"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§aMolten Rapier",Lore:["§8King's Valley : Tier V"]},ench:[{id:16s,lvl:1s},{id:20s,lvl:2s},{id:17s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"nbt":ur'''{display:{Name:"§aPolished Gladius"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§aPolished Gladius",Lore:["§8King's Valley : Tier V"]},ench:[{id:16s,lvl:1s},{id:34s,lvl:3s},{id:19s,lvl:3s}]}'''
		]
	],
	[
		{
			"id":"minecraft:golden_sword",
			"nbt":ur'''{display:{Name:"§aEldritch Blade"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:51s}],HideFlags:1,display:{Lore:["§8King's Valley : Tier V"],Name:"§aEldritch Blade"},AttributeModifiers:[{UUIDMost:81922l,UUIDLeast:79311l,Amount:0.15d,Slot:"offhand",AttributeName:"generic.knockbackResistance",Operation:0,Name:"generic.knockbackResistance"},{UUIDMost:298381l,UUIDLeast:495523l,Amount:0.2d,Slot:"offhand",AttributeName:"generic.attackDamage",Operation:1,Name:"generic.attackDamage"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"nbt":ur'''{display:{Name:"§aScout's Companion"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:51s}],HideFlags:1,display:{Lore:["§8King's Valley : Tier V"],Name:"§aScout's Companion"},AttributeModifiers:[{UUIDMost:637136l,UUIDLeast:234308l,Amount:2d,Slot:"offhand",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"},{UUIDMost:743378l,UUIDLeast:575520l,Amount:0.1d,Slot:"offhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"nbt":ur'''{display:{Name:"§fBlessed Axe"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fBlessed Axe",Lore:["§8King's Valley : Tier V"]},ench:[{id:32s,lvl:3s},{id:34s,lvl:4s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"nbt":ur'''{display:{Name:"§aCrushing Mace"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§aCrushing Mace",Lore:["§8King's Valley : Tier V"]},ench:[{id:16s,lvl:2s},{id:17s,lvl:1s},{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"nbt":ur'''{display:{Name:"§fPhoenix Axe"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fPhoenix Axe",Lore:["§8King's Valley : Tier V"]},ench:[{id:19s,lvl:2s},{id:20s,lvl:3s},{id:34s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"nbt":ur'''{display:{Name:"§aSoulhammer"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§aSoulhammer",Lore:["§8King's Valley : Tier V"]},ench:[{id:16s,lvl:1s},{id:19s,lvl:1s},{id:70s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_pickaxe",
			"nbt":ur'''{display:{Name:"§aEvanescent"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§aEvanescent",Lore:["§8King's Valley : Tier V"]},ench:[{id:32s,lvl:4s},{id:71s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_pickaxe",
			"nbt":ur'''{display:{Name:"§aUndying Chisel"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§aUndying Chisel",Lore:["§8King's Valley : Tier V"]},ench:[{id:32s,lvl:1s},{id:70s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_pickaxe",
			"nbt":ur'''{display:{Name:"§fTruerune Pick"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fTruerune Pick",Lore:["§8King's Valley : Tier V"]},ench:[{id:35s,lvl:4s},{id:34s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_shovel",
			"nbt":ur'''{display:{Name:"§fUndying Trowel"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fUndying Trowel",Lore:["§8King's Valley : Tier V"]},ench:[{id:32s,lvl:3s},{id:70s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_hoe",
			"nbt":ur'''{display:{Name:"§fExecutioner's Scythe"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fExecutioner's Scythe",Lore:["§8King's Valley : Tier V"]},ench:[{id:16s,lvl:5s},{id:17s,lvl:2s},{id:21s,lvl:2s},{id:34s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:shield",
			"nbt":ur'''{display:{Name:"§aSwiftwood Buckler"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{UUIDMost:3799174595893871670l,UUIDLeast:-8604776829862673178l,Amount:0.05d,Slot:"offhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}],display:{Name:"§aSwiftwood Buckler",Lore:["§8King's Valley : Tier V"]}}'''
		]
	],
	[
		{
			"id":"minecraft:bow",
			"nbt":ur'''{display:{Name:"§fBlazing Crossbow"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fBlazing Crossbow",Lore:["§8King's Valley : Tier V"]},ench:[{id:49s,lvl:2s},{id:50s,lvl:1s},{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:bow",
			"nbt":ur'''{display:{Name:"§aKorbaran Shortbow"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§aKorbaran Shortbow",Lore:["§8King's Valley : Tier V"]},ench:[{id:48s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:fishing_rod",
			"nbt":ur'''{display:{Name:"§aMermaid's Touch"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§aMermaid's Touch",Lore:["§8King's Valley : Tier V"]},ench:[{id:70s,lvl:1s},{id:62s,lvl:4s}]}'''
		]
	],
	[
		{
			"id":"minecraft:blaze_rod",
			"nbt":ur'''{display:{Name:"§aPyromancer's Staff"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§aPyromancer's Staff",Lore:["§8* Magic Wand *","§8King's Valley : Tier V"]},ench:[{id:17s,lvl:1s},{id:20s,lvl:3s},{id:16s,lvl:3s}]}'''
		]
	],
	[
		{
			"id":"minecraft:stick",
			"nbt":ur'''{display:{Name:"§aWand of Storms"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:16s},{lvl:3s,id:19s},{lvl:1s,id:20s}],display:{Name:"§aWand of Storms",Lore:["§8* Magic Wand *","§8King's Valley : Tier V"]},AttributeModifiers:[{UUIDMost:120619l,UUIDLeast:372763l,Amount:0.07d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§fNereid Cap"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fNereid Cap",color:1073407,Lore:["§bLeather Armor","§8King's Valley : Tier V"]},ench:[{id:0s,lvl:2s},{id:4s,lvl:1s},{id:6s,lvl:1s},{id:5s,lvl:1s},{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§fNereid Tunic"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fNereid Tunic",color:1073407,Lore:["§bLeather Armor","§8King's Valley : Tier V"]},ench:[{id:0s,lvl:2s},{id:4s,lvl:1s},{id:8s,lvl:1s},{id:5s,lvl:1s},{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§fNereid Leggings"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fNereid Leggings",color:1073407,Lore:["§bLeather Armor","§8King's Valley : Tier V"]},ench:[{id:0s,lvl:2s},{id:4s,lvl:1s},{id:8s,lvl:1s},{id:5s,lvl:1s},{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§fNereid Sandals"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fNereid Sandals",color:1073407,Lore:["§bLeather Armor","§8King's Valley : Tier V"]},ench:[{id:0s,lvl:2s},{id:4s,lvl:1s},{id:8s,lvl:2s},{id:34s,lvl:1s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§fHardened Leather Cap"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fHardened Leather Cap",color:10506272,Lore:["§bLeather Armor","§8King's Valley : Tier V"]},ench:[{id:0s,lvl:1s},{id:3s,lvl:3s},{id:34s,lvl:3s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§fHardened Leather Tunic"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fHardened Leather Tunic",color:10506272,Lore:["§bLeather Armor","§8King's Valley : Tier V"]},ench:[{id:0s,lvl:1s},{id:3s,lvl:3s},{id:34s,lvl:3s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§fHardened Leather Pants"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fHardened Leather Pants",color:10506272,Lore:["§bLeather Armor","§8King's Valley : Tier V"]},ench:[{id:0s,lvl:1s},{id:3s,lvl:3s},{id:34s,lvl:3s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§fHardened Leather Boots"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§fHardened Leather Boots",color:10506272,Lore:["§bLeather Armor","§8King's Valley : Tier V"]},ench:[{id:0s,lvl:1s},{id:3s,lvl:3s},{id:34s,lvl:3s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§aScout's Leathers"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.movementSpeed",Name:"generic.movementSpeed",Amount:0.03d,Operation:1,UUIDLeast:277777l,UUIDMost:692165l,Slot:"head"},{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.0d,Operation:0,UUIDLeast:277777l,UUIDMost:692165l,Slot:"head"}],display:{Name:"§aScout's Leathers",color:10240,Lore:["§bLeather Armor","§8King's Valley : Tier V"]},ench:[{id:34s,lvl:1s},{id:0s,lvl:2s},{id:4s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§aScout's Leathers"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.movementSpeed",Name:"generic.movementSpeed",Amount:0.03d,Operation:1,UUIDLeast:297777l,UUIDMost:752165l,Slot:"chest"},{AttributeName:"generic.armor",Name:"generic.armor",Amount:3.0d,Operation:0,UUIDLeast:297777l,UUIDMost:752165l,Slot:"chest"}],display:{Name:"§aScout's Leathers",color:10240,Lore:["§bLeather Armor","§8King's Valley : Tier V"]},ench:[{id:34s,lvl:1s},{id:0s,lvl:2s},{id:4s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§aScout's Leathers"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.movementSpeed",Name:"generic.movementSpeed",Amount:0.03d,Operation:1,UUIDLeast:337777l,UUIDMost:732165l,Slot:"legs"},{AttributeName:"generic.armor",Name:"generic.armor",Amount:2.0d,Operation:0,UUIDLeast:337777l,UUIDMost:764261l,Slot:"legs"}],display:{Name:"§aScout's Leathers",color:10240,Lore:["§bLeather Armor","§8King's Valley : Tier V"]},ench:[{id:34s,lvl:1s},{id:0s,lvl:2s},{id:4s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§aScout's Leathers"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.movementSpeed",Name:"generic.movementSpeed",Amount:0.03d,Operation:1,UUIDLeast:237777l,UUIDMost:632165l,Slot:"feet"},{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.0d,Operation:0,UUIDLeast:237777l,UUIDMost:632165l,Slot:"feet"}],display:{Name:"§aScout's Leathers",color:10240,Lore:["§bLeather Armor","§8King's Valley : Tier V"]},ench:[{id:34s,lvl:1s},{id:0s,lvl:2s},{id:2s,lvl:3s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§aSoulleather Veil"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§aSoulleather Veil",color:16777215,Lore:["§bLeather Armor","§8King's Valley : Tier V"]},ench:[{id:70s,lvl:1s},{id:71s,lvl:1s},{id:0s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§aSoulleather Cloak"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§aSoulleather Cloak",color:16777215,Lore:["§bLeather Armor","§8King's Valley : Tier V"]},ench:[{id:70s,lvl:1s},{id:71s,lvl:1s},{id:0s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§aSoulleather Robe"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§aSoulleather Robe",color:16777215,Lore:["§bLeather Armor","§8King's Valley : Tier V"]},ench:[{id:70s,lvl:1s},{id:71s,lvl:1s},{id:0s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§aSoulleather Shoes"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Name:"§aSoulleather Shoes",color:16777215,Lore:["§bLeather Armor","§8King's Valley : Tier V"]},ench:[{id:70s,lvl:1s},{id:71s,lvl:1s},{id:0s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§aViridian Mage Hat"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:803793l,UUIDMost:260399l,Slot:"head"}],display:{Name:"§aViridian Mage Hat",color:1105920,Lore:["§9Cloth Armor","§8King's Valley : Tier V"]},ench:[{id:0s,lvl:3s},{id:34s,lvl:1s},{id:1s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§aViridian Mage Robes"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.5d,Operation:0,UUIDLeast:903793l,UUIDMost:270399l,Slot:"chest"}],display:{Name:"§aViridian Mage Robes",color:1105920,Lore:["§9Cloth Armor","§8King's Valley : Tier V"]},ench:[{id:0s,lvl:3s},{id:34s,lvl:1s},{id:4s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§aViridian Mage Robes"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:1.0d,Operation:0,UUIDLeast:1003793l,UUIDMost:280399l,Slot:"legs"}],display:{Name:"§aViridian Mage Robes",color:1105920,Lore:["§9Cloth Armor","§8King's Valley : Tier V"]},ench:[{id:0s,lvl:3s},{id:34s,lvl:1s},{id:3s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§aViridian Mage Robes"}}'''
		},
		[
			"nbt", "replace", ur'''{AttributeModifiers:[{AttributeName:"generic.armor",Name:"generic.armor",Amount:0.75d,Operation:0,UUIDLeast:1103793l,UUIDMost:290399l,Slot:"feet"}],display:{Name:"§aViridian Mage Robes",color:1105920,Lore:["§9Cloth Armor","§8King's Valley : Tier V"]},ench:[{id:0s,lvl:3s},{id:34s,lvl:1s},{id:2s,lvl:2s}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§aDualsun Hood"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:1s},{lvl:4s,id:34s},{lvl:1s,id:0s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier V"],color:16773120,Name:"§aDualsun Hood"},AttributeModifiers:[{UUIDMost:3410419544452450231l,UUIDLeast:-5482257300623082461l,Amount:1.0d,Slot:"head",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"},{UUIDMost:-7224057274751827505l,UUIDLeast:-6818848218977621316l,Amount:1.0d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§aDualsun Cloak"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:1s},{lvl:4s,id:34s},{lvl:1s,id:0s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier V"],color:16773120,Name:"§aDualsun Cloak"},AttributeModifiers:[{UUIDMost:-895514479119021132l,UUIDLeast:-6538819203639619634l,Amount:1.0d,Slot:"chest",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"},{UUIDMost:-845493126176553328l,UUIDLeast:-6934174944561962248l,Amount:3.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§aDualsun Robe"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:1s},{lvl:4s,id:34s},{lvl:1s,id:0s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier V"],color:16773120,Name:"§aDualsun Robe"},AttributeModifiers:[{UUIDMost:-3224490652004365870l,UUIDLeast:-8490984991565425765l,Amount:1.0d,Slot:"legs",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"},{UUIDMost:5309333526597813727l,UUIDLeast:-8167831153772325916l,Amount:2.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§aDualsun Shoes"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:1s},{lvl:4s,id:34s},{lvl:1s,id:0s}],display:{Lore:["§bLeather Armor","§8King's Valley : Tier V"],color:16773120,Name:"§aDualsun Shoes"},AttributeModifiers:[{UUIDMost:-1243331979226886434l,UUIDLeast:-7990746417674087296l,Amount:1.0d,Slot:"feet",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"},{UUIDMost:-5110990380665716018l,UUIDLeast:-5231967837950058796l,Amount:1.0d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§fOffering's Robe"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:1s,id:34s},{lvl:2s,id:4s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Uncommon"],color:16719872,Name:"§fOffering's Robe"},AttributeModifiers:[{UUIDMost:7895314803459967566l,UUIDLeast:-4684285381480027934l,Amount:0.75d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§fOffering's Robe"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:1s,id:34s},{lvl:2s,id:4s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Uncommon"],color:16719872,Name:"§fOffering's Robe"},AttributeModifiers:[{UUIDMost:2421209759494129265l,UUIDLeast:-7639468242547147097l,Amount:1.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§fOffering's Robe"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:1s,id:34s},{lvl:2s,id:4s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Uncommon"],color:16719872,Name:"§fOffering's Robe"},AttributeModifiers:[{UUIDMost:4172809477985159313l,UUIDLeast:-6315940985289442365l,Amount:1.5d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§fOffering's Hood"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:1s,id:34s},{lvl:2s,id:4s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Uncommon"],color:16719872,Name:"§fOffering's Hood"},AttributeModifiers:[{UUIDMost:-1020269136855678533l,UUIDLeast:-8988064621405004682l,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"nbt":ur'''{display:{Name:"§fSacrificial Blade"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:1s,id:20s}],display:{Lore:["§8King's Valley : Uncommon"],Name:"§fSacrificial Blade"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§fFur Boots"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:2s,id:1s}],display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:12486759,Name:"§fFur Boots"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§fFur Leggings"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:2s,id:1s}],display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:12486759,Name:"§fFur Leggings"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§fFur Tunic"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:2s,id:1s}],display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:12486759,Name:"§fFur Tunic"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§fFur Cap"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:2s,id:1s}],display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:12486759,Name:"§fFur Cap"}}'''
		]
	],
	[
		{
			"id":"minecraft:shield",
			"nbt":ur'''{display:{Name:"§fHide Shield"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:34s}],BlockEntityTag:{Patterns:[{Pattern:"mr",Color:14},{Pattern:"sku",Color:3}],Base:3},display:{Lore:["§8King's Valley : Uncommon"],Name:"§fHide Shield"},AttributeModifiers:[{UUIDMost:4829683371424304161l,UUIDLeast:-8495861702335545947l,Amount:0.15d,Slot:"mainhand",AttributeName:"generic.knockbackResistance",Operation:0,Name:"Modifier"},{UUIDMost:-660961315230563653l,UUIDLeast:-7651396858820480353l,Amount:0.15d,Slot:"offhand",AttributeName:"generic.knockbackResistance",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§fExplorer's Boots"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:8s},{lvl:1s,id:34s},{lvl:1s,id:0s}],display:{color:3445134,Name:"§fExplorer's Boots",Lore:["§bLeather Armor","§8King's Valley : Uncommon"]}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§fExplorer's Cap"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:5s},{lvl:1s,id:6s},{lvl:1s,id:0s}],display:{color:755048,Name:"§fExplorer's Cap",Lore:["§bLeather Armor","§8King's Valley : Uncommon"]}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§aPlaguehide Boots"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:675072,Name:"§aPlaguehide Boots"},AttributeModifiers:[{UUIDMost:19971159992297292l,UUIDLeast:11701631750427272l,Amount:2d,Slot:"feet",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"},{UUIDMost:50620023180411213l,UUIDLeast:56580625667548148l,Amount:0.05d,Slot:"feet",AttributeName:"generic.attackDamage",Operation:1,Name:"generic.attackDamage"},{UUIDMost:61536614628787790l,UUIDLeast:12067686387522583l,Amount:1d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§aPlaguehide Pants"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:675072,Name:"§aPlaguehide Pants"},AttributeModifiers:[{UUIDMost:7398196116790600l,UUIDLeast:33239325481073366l,Amount:2d,Slot:"legs",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"},{UUIDMost:61910509039675723l,UUIDLeast:13746144420287990l,Amount:0.05d,Slot:"legs",AttributeName:"generic.attackDamage",Operation:1,Name:"generic.attackDamage"},{UUIDMost:14165244533123147l,UUIDLeast:22637248009267620l,Amount:2d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§aPlaguehide Torso"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:675072,Name:"§aPlaguehide Torso"},AttributeModifiers:[{UUIDMost:71978911221471809l,UUIDLeast:25260044972271010l,Amount:2d,Slot:"chest",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"},{UUIDMost:19117308396094024l,UUIDLeast:9968568939286539l,Amount:0.05d,Slot:"chest",AttributeName:"generic.attackDamage",Operation:1,Name:"generic.attackDamage"},{UUIDMost:8440217748974405l,UUIDLeast:3552643124966103l,Amount:3d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§aPlaguehide Cap"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:675072,Name:"§aPlaguehide Cap"},AttributeModifiers:[{UUIDMost:22907356139724361l,UUIDLeast:55634361538278368l,Amount:2d,Slot:"head",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"},{UUIDMost:50813337862916683l,UUIDLeast:38856196263924788l,Amount:0.05d,Slot:"head",AttributeName:"generic.attackDamage",Operation:1,Name:"generic.attackDamage"},{UUIDMost:22347000550566221l,UUIDLeast:68212466135762333l,Amount:1d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§fGuardian Hide Boots"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:1s,id:70s},{lvl:3s,id:7s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Uncommon"],color:10599120,Name:"§fGuardian Hide Boots"},AttributeModifiers:[{UUIDMost:290399l,UUIDLeast:1103793l,Amount:0.75d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§fGuardian Hide Pants"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:1s,id:70s},{lvl:3s,id:7s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Uncommon"],color:10599120,Name:"§fGuardian Hide Pants"},AttributeModifiers:[{UUIDMost:280399l,UUIDLeast:1003793l,Amount:1.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§fGuardian Hide Vest"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:1s,id:70s},{lvl:3s,id:7s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Uncommon"],color:10599120,Name:"§fGuardian Hide Vest"},AttributeModifiers:[{UUIDMost:270399l,UUIDLeast:903793l,Amount:1.5d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§fGuardian Hide Helm"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:1s,id:70s},{lvl:3s,id:7s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Uncommon"],color:10599120,Name:"§fGuardian Hide Helm"},AttributeModifiers:[{UUIDMost:260399l,UUIDLeast:803793l,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§fThaumaturge's Robes"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:0s},{lvl:1s,id:8s}],display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:7833547,Name:"§fThaumaturge's Robes"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§fThaumaturge's Robes"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:0s}],display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:7833547,Name:"§fThaumaturge's Robes"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§fThaumaturge's Robes"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:0s}],display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:7833547,Name:"§fThaumaturge's Robes"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§fThaumaturge's Hood"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:0s},{lvl:2s,id:5s},{lvl:1s,id:6s}],display:{Lore:["§bLeather Armor","§8King's Valley : Uncommon"],color:7833547,Name:"§fThaumaturge's Hood"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"nbt":ur'''{display:{Name:"§6§lAngelic Sword"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:17s},{lvl:5s,id:34s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§8","§7When in main hand:","§7 1.6 Attack Speed","§7 5 Attack Damage","§9 +1 Armor"],Name:"§6§lAngelic Sword"},AttributeModifiers:[{UUIDMost:13921849192281677l,UUIDLeast:29424957165321736l,Amount:4d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:14771070297205314l,UUIDLeast:58375339796730923l,Amount:1d,Slot:"mainhand",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:69970127574793796l,UUIDLeast:64342718172429329l,Amount:-2.4d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"nbt":ur'''{display:{Name:"§3§lMithril Cleaver"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:16s},{lvl:2s,id:34s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§8","§7When in main hand:","§7 1.2 Attack Speed","§7 10 Attack Damage","§9 +12% Speed"],Name:"§3§lMithril Cleaver"},AttributeModifiers:[{UUIDMost:1317475486626126l,UUIDLeast:53226458093335048l,Amount:0.12d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:776403941688908l,UUIDLeast:11889093433774429l,Amount:-2.8d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"},{UUIDMost:30352855180673349l,UUIDLeast:58285458965911180l,Amount:8d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"}]}'''
		]
	],
	[
		{
			"id":"minecraft:blaze_rod",
			"nbt":ur'''{display:{Name:"§5§lHell's Fury"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:2s,id:19s},{lvl:5s,id:20s}],display:{Lore:["§8* Magic Wand *","§eKing's Valley : Rare"],Name:"§5§lHell's Fury"},AttributeModifiers:[{UUIDMost:69502167760309831l,UUIDLeast:25155512585813018l,Amount:0.08d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:golden_sword",
			"nbt":ur'''{display:{Name:"§2§lSoulvenom Dagger"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:34s}],HideFlags:1,display:{Lore:["§eKing's Valley : Rare"],Name:"§2§lSoulvenom Dagger"},AttributeModifiers:[{UUIDMost:848078l,UUIDLeast:702456l,Amount:-2d,Slot:"offhand",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"},{UUIDMost:521417l,UUIDLeast:238571l,Amount:0.08d,Slot:"offhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:783241l,UUIDLeast:758745l,Amount:0.3d,Slot:"offhand",AttributeName:"generic.attackDamage",Operation:1,Name:"generic.attackDamage"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_pickaxe",
			"nbt":ur'''{display:{Name:"§3§lObsidian Pickaxe"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:32s},{lvl:1s,id:34s}],display:{Lore:["§eKing's Valley : Rare"],Name:"§3§lObsidian Pickaxe"}}'''
		]
	],
	[
		{
			"id":"minecraft:shield",
			"nbt":ur'''{display:{Name:"§2§lKeeper of the Jungle"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:34s}],HideFlags:32,BlockEntityTag:{Patterns:[{Pattern:"ss",Color:2},{Pattern:"flo",Color:2},{Pattern:"bri",Color:2}],Base:3},display:{Lore:["§eKing's Valley : Rare"],Name:"§2§lKeeper of the Jungle"},AttributeModifiers:[{UUIDMost:9006655014927177l,UUIDLeast:4782782479127341l,Amount:1d,Slot:"offhand",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§6§lAngelic Pants"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:34s}],display:{Lore:["§bLeather Armor","§eKing's Valley : Rare"],color:14277081,Name:"§6§lAngelic Pants"},AttributeModifiers:[{UUIDMost:2767629973749578l,UUIDLeast:26549136928073536l,Amount:5d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"nbt":ur'''{display:{Name:"§b§lSpirit Blade"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:1s,id:70s}],display:{Lore:["§eKing's Valley : Rare"],Name:"§b§lSpirit Blade"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"nbt":ur'''{display:{Name:"§4§lShadow Spike"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:4s,id:16s},{lvl:2s,id:34s},{lvl:1s,id:19s},{lvl:1s,id:20s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§8","§7When in main hand:","§7 1.6 Attack Speed","§7 7.5 Attack Damage","§c -3 Armor"],Name:"§4§lShadow Spike"},AttributeModifiers:[{UUIDMost:24272506551626816l,UUIDLeast:3188629144429256l,Amount:4d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:68081597460234561l,UUIDLeast:58960188647077945l,Amount:-3d,Slot:"mainhand",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:40900807882193986l,UUIDLeast:13214525664118331l,Amount:-2.4d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:bow",
			"nbt":ur'''{display:{Name:"§b§lTempest Caller"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:48s},{lvl:1s,id:49s},{lvl:1s,id:34s}],display:{Lore:["§eKing's Valley : Rare"],Name:"§b§lTempest Caller"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§1§lShadowborn Boots"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:2s,id:2s},{lvl:2s,id:34s}],display:{Lore:["§bLeather Armor","§eKing's Valley : Rare"],color:0,Name:"§1§lShadowborn Boots"},AttributeModifiers:[{UUIDMost:27244509153028163l,UUIDLeast:28582544481897959l,Amount:0.1d,Slot:"feet",AttributeName:"generic.attackDamage",Operation:1,Name:"generic.attackDamage"},{UUIDMost:28562665029432653l,UUIDLeast:46011597873607935l,Amount:1d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§1§lVoidguard"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:0s},{lvl:2s,id:34s}],display:{Lore:["§bLeather Armor","§eKing's Valley : Rare"],color:3287104,Name:"§1§lVoidguard"},AttributeModifiers:[{UUIDMost:71061793700771916l,UUIDLeast:70921921889626742l,Amount:0.05d,Slot:"chest",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:5618170327124803l,UUIDLeast:67318597315435972l,Amount:3d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"nbt":ur'''{display:{Name:"§6§lTelum Immoriel"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:34s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§fAnother toy for Fangride to play with.","§8","§7When in main hand:","§7 0.8 Attack Speed","§7 12 Attack Damage"],Name:"§6§lTelum Immoriel"},AttributeModifiers:[{UUIDMost:962659l,UUIDLeast:90631l,Amount:11d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:345591l,UUIDLeast:876260l,Amount:-3.2d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:sapling",
			"nbt":ur'''{display:{Name:"§2§lChimarian Wand"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:16s},{lvl:2s,id:17s},{lvl:2s,id:18s},{lvl:1s,id:20s}],display:{Lore:["§eKing's Valley : Rare","§8* Magic Wand *","§fWe need more trees!"],Name:"§2§lChimarian Wand"}}'''
		]
	],
	[
		{
			"id":"minecraft:quartz",
			"nbt":ur'''{display:{Name:"§3§lRender's Ruthless Claw"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:8s,id:16s}],display:{Lore:["§eKing's Valley : Rare","§fSimplistic, but effective."],Name:"§3§lRender's Ruthless Claw"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_pickaxe",
			"nbt":ur'''{display:{Name:"§1§lHelician Spitzhacke"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:32s},{lvl:3s,id:34s}],HideFlags:3,display:{Lore:["§7Effizienz II","§7Unbreaking III","§eKing's Valley : Rare","§fNow with German Efficiency!","§8","§7When in main hand:","§7 1.2 Attack Speed","§7 3 Attack Damage","§9 +0.5 Knockback Resistance","§9 +3 Armor"],Name:"§1§lHelician Spitzhacke"},AttributeModifiers:[{UUIDMost:203618l,UUIDLeast:725165l,Amount:0.5d,Slot:"mainhand",AttributeName:"generic.knockbackResistance",Operation:0,Name:"generic.knockbackResistance"},{UUIDMost:961145l,UUIDLeast:133590l,Amount:3d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:670193l,UUIDLeast:659361l,Amount:3d,Slot:"mainhand",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:641625l,UUIDLeast:480595l,Amount:-2.8d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:red_flower",
			"nbt":ur'''{display:{Name:"§d§lTeewie's Eternal Tulip"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s}],HideFlags:1,display:{Lore:["§eKing's Valley : Rare","§fPart of the flower crown worn by Princess Teewie","§fmany centuries ago."],Name:"§d§lTeewie's Eternal Tulip"},AttributeModifiers:[{UUIDMost:-2576588526142208534l,UUIDLeast:-8215095133131934612l,Amount:3.0d,Slot:"offhand",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"},{UUIDMost:-7377653646270249488l,UUIDLeast:-4833595088129389224l,Amount:2.0d,Slot:"offhand",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§4§lBusty's Hot Pants"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:1s},{lvl:1s,id:70s},{lvl:2s,id:3s}],display:{Lore:["§bLeather Armor","§eKing's Valley : Rare","§fCaution: Highly combustible!"],color:14059296,Name:"§4§lBusty's Hot Pants"}}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§5§lBrown Corp Uniform"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:3s,id:34s}],display:{Lore:["§bLeather Armor","§eKing's Valley : Rare","§fWhat do they ever do besides hanging out?"],color:6704179,Name:"§5§lBrown Corp Uniform"},AttributeModifiers:[{UUIDMost:-395305911349064079l,UUIDLeast:-6975068402520238575l,Amount:2.0d,Slot:"chest",AttributeName:"generic.armorToughness",Operation:0,Name:"Modifier"},{UUIDMost:8894152384868271503l,UUIDLeast:-5148525816173331419l,Amount:3.0d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§b§lZephyric Sandals"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:7s,id:2s}],display:{Lore:["§9Cloth Armor","§eKing's Valley : Rare"],color:13684991,Name:"§b§lZephyric Sandals"},AttributeModifiers:[{UUIDMost:-519805393186370468l,UUIDLeast:-7058263731030477121l,Amount:0.75d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"Modifier"},{UUIDMost:-7658801990265518657l,UUIDLeast:-6575958443379293118l,Amount:0.05d,Slot:"feet",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§4§lAncient Robes"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:3s,id:34s}],display:{Lore:["§bLeather Armor","§eKing's Valley : Rare"],color:6299664,Name:"§4§lAncient Robes"},AttributeModifiers:[{UUIDMost:6974589633277084868l,UUIDLeast:-6904800762426278794l,Amount:2.0d,Slot:"legs",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"},{UUIDMost:583279600458681380l,UUIDLeast:-6719247825501452697l,Amount:2.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§6§lC'Zanil's Shroud"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:4s},{lvl:2s,id:34s}],display:{Lore:["§eKing's Valley : Rare","* Regeneration *","§7Grants Regeneration I","§7when worn"],color:41215,Name:"§6§lC'Zanil's Shroud"},AttributeModifiers:[]}'''
		]
	],
	[
		{
			"id":"minecraft:skull",
			"nbt":ur'''{display:{Name:"§3§lPhantom's Hood"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:1s},{lvl:1s,id:3s},{lvl:1s,id:4s},{lvl:1s,id:71s}],SkullOwner:{Id:"251ab4e3-c5f6-61e5-b664-59f78f131844",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvYWJlZGI4ZDRiMDZlZWI5NzllZTUxNWY3NzhmMzFiM2RlZWY5MmZiNTgxN2YzNDUyZjUxZmM1OGQ0ODEzNCJ9fX0="}]}},display:{Lore:["§eKing's Valley : Rare"],Name:"§3§lPhantom's Hood"},AttributeModifiers:[{UUIDMost:-1757382812970040601l,UUIDLeast:-8366606905223081447l,Amount:0.08d,Slot:"head",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:bone",
			"nbt":ur'''{display:{Name:"§6§lWand of C'Zanil"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:16s},{lvl:1s,id:20s}],display:{Lore:["§8* Magic Wand *","§eKing's Valley : Rare","* Regeneration *","§7Grants Regeneration I when","§7held in your off-hand"],Name:"§6§lWand of C'Zanil"}}'''
		]
	],
	[
		{
			"id":"minecraft:bow",
			"nbt":ur'''{display:{Name:"§3§lQuetzalcoatl's Wrath"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:48s},{lvl:1s,id:70s},{lvl:1s,id:71s}],display:{Lore:["§eKing's Valley : Rare"],Name:"§3§lQuetzalcoatl's Wrath"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"nbt":ur'''{display:{Name:"§8§lAshheart Dagger"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:34s},{lvl:4s,id:20s},{lvl:2s,id:22s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§f","§7When in main hand:","§7 1.6 Attack Speed","§7 5 Attack Damage","§9 +2 Max Health"],Name:"§8§lAshheart Dagger"},AttributeModifiers:[{UUIDMost:6203368885045579351l,UUIDLeast:-5502292298614332755l,Amount:2.0d,Slot:"mainhand",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"},{UUIDMost:1770737273186633355l,UUIDLeast:-7632807259696268977l,Amount:4d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"},{UUIDMost:-925442460826187303l,UUIDLeast:-5209611670608876751l,Amount:-2.4d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_pickaxe",
			"nbt":ur'''{display:{Name:"§8§lAshfloe Chisel"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:32s},{lvl:5s,id:35s}],display:{Lore:["§eKing's Valley : Rare"],Name:"§8§lAshfloe Chisel"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"nbt":ur'''{display:{Name:"§3§lThe Ravager"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:2s,id:19s},{lvl:2s,id:34s}],display:{Lore:["§eKing's Valley : Rare"],Name:"§3§lThe Ravager"}}'''
		]
	],
	[
		{
			"id":"minecraft:stick",
			"nbt":ur'''{display:{Name:"§2§lShapeshifter's Wand"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:16s},{lvl:1s,id:19s}],display:{Lore:["§8* Magic Wand *","§eKing's Valley : Rare"],Name:"§2§lShapeshifter's Wand"},AttributeModifiers:[{UUIDMost:-6875693728534016758l,UUIDLeast:-4803955762994063049l,Amount:0.15d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"},{UUIDMost:-8999057979425928886l,UUIDLeast:-6793904886171895238l,Amount:5.0d,Slot:"offhand",AttributeName:"generic.maxHealth",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§2§lBoots of Vitality"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:5s,id:34s}],display:{Lore:["§bLeather Armor","§eKing's Valley : Rare"],color:4521728,Name:"§2§lBoots of Vitality"},AttributeModifiers:[{UUIDMost:47288061869184321l,UUIDLeast:31209886326295287l,Amount:2d,Slot:"feet",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"},{UUIDMost:67642567772660032l,UUIDLeast:69671216077991960l,Amount:1d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§d§lCultist's Robe"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:1s,id:10s},{lvl:1s,id:70s}],display:{Lore:["§bLeather Armor","§eKing's Valley : Rare"],color:8857897,Name:"§d§lCultist's Robe"},AttributeModifiers:[{UUIDMost:42188985747894336l,UUIDLeast:58789894930970307l,Amount:3d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:26258638605899072l,UUIDLeast:65484620952030853l,Amount:0.1d,Slot:"chest",AttributeName:"generic.attackSpeed",Operation:1,Name:"generic.attackSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:quartz",
			"nbt":ur'''{display:{Name:"§9§lPurified Claw"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:17s},{lvl:1s,id:19s}],display:{Lore:["§eKing's Valley : Rare"],Name:"§9§lPurified Claw"},AttributeModifiers:[{UUIDMost:-7888225324843646806l,UUIDLeast:-6512244924204989927l,Amount:1.0d,Slot:"mainhand",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"nbt":ur'''{display:{Name:"§a§lWildthrasher"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:3s,id:34s},{lvl:1s,id:20s}],display:{Lore:["§eKing's Valley : Rare"],Name:"§a§lWildthrasher"}}'''
		]
	],
	[
		{
			"id":"minecraft:bow",
			"nbt":ur'''{display:{Name:"§f§lBonepiercer"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:48s},{lvl:1s,id:49s},{lvl:1s,id:50s},{lvl:1s,id:34s}],display:{Lore:["§eKing's Valley : Rare"],Name:"§f§lBonepiercer"}}'''
		]
	],
	[
		{
			"id":"minecraft:golden_axe",
			"nbt":ur'''{display:{Name:"§d§lArachnobane"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:4s,id:18s},{lvl:7s,id:34s},{lvl:1s,id:19s},{lvl:1s,id:20s}],display:{Lore:["§eKing's Valley : Rare"],Name:"§d§lArachnobane"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"nbt":ur'''{display:{Name:"§6§lSoulcrusher"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:6s,id:16s},{lvl:3s,id:34s}],RepairCost:1,HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§f","§7When in main hand:","§7 0.8 Attack Speed","§7 12.5 Attack Damage","§c -20% Speed"],Name:"§6§lSoulcrusher"},AttributeModifiers:[{UUIDMost:12446444898007617l,UUIDLeast:64791494739800248l,Amount:-0.2d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:19182804207771727l,UUIDLeast:44200783352792867l,Amount:8d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:1126358275258178l,UUIDLeast:50193448324688339l,Amount:-3.2d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"nbt":ur'''{display:{Name:"§6§lDoom's Edge"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:2s,id:34s},{lvl:4s,id:22s}],display:{Lore:["§eKing's Valley : Rare"],Name:"§6§lDoom's Edge"}}'''
		]
	],
	[
		{
			"id":"minecraft:golden_hoe",
			"nbt":ur'''{display:{Name:"§6§lReaper's Harvest"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:16s},{lvl:4s,id:17s},{lvl:1s,id:70s}],display:{Lore:["§eKing's Valley : Rare"],Name:"§6§lReaper's Harvest"}}'''
		]
	],
	[
		{
			"id":"minecraft:totem_of_undying",
			"nbt":ur'''{display:{Name:"§6§lIdol of Immortality"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["§eKing's Valley : Rare","§fWhen you are about to die, this item provides","§fAbsorption and Regeneration, destroying itself","§fin the process."],Name:"§6§lIdol of Immortality"},AttributeModifiers:[{UUIDMost:6936855416015769157l,UUIDLeast:-5146628686682897060l,Amount:3.0d,Slot:"offhand",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:shield",
			"nbt":ur'''{display:{Name:"§2§lTlaxan Bulwark"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:34s}],HideFlags:32,BlockEntityTag:{Patterns:[{Pattern:"gru",Color:0},{Pattern:"cre",Color:0},{Pattern:"flo",Color:0},{Pattern:"moj",Color:0},{Pattern:"tts",Color:0},{Pattern:"bts",Color:0}],Base:2},display:{Lore:["§eKing's Valley : Rare"],Name:"§2§lTlaxan Bulwark"},AttributeModifiers:[{UUIDMost:8279654741628239l,UUIDLeast:50644245966137402l,Amount:2d,Slot:"offhand",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§2§lBasilisk Scales"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:3s,id:34s}],display:{Lore:["§eKing's Valley : Rare"],color:54286,Name:"§2§lBasilisk Scales"},AttributeModifiers:[{UUIDMost:1217047145548364l,UUIDLeast:62197310443051283l,Amount:4d,Slot:"chest",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§2§lPlaguebringer"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:0s},{lvl:1s,id:34s},{lvl:1s,id:70s},{lvl:4s,id:7s}],display:{Lore:["§bLeather Armor","§eKing's Valley : Rare"],color:283658,Name:"§2§lPlaguebringer"}}'''
		]
	],
	[
		{
			"id":"minecraft:skull",
			"nbt":ur'''{display:{Name:"§4§lTlaxan Mask"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:10s},{lvl:4s,id:4s},{lvl:2s,id:5s}],SkullOwner:{Id:"c659cdd4-e436-4977-a6a7-d5518ebecfbb",Properties:{textures:[{Value:"eyJ0ZXh0dXJlcyI6eyJTS0lOIjp7InVybCI6Imh0dHA6Ly90ZXh0dXJlcy5taW5lY3JhZnQubmV0L3RleHR1cmUvMWFlMzg1NWY5NTJjZDRhMDNjMTQ4YTk0NmUzZjgxMmE1OTU1YWQzNWNiY2I1MjYyN2VhNGFjZDQ3ZDMwODEifX19"}]}},display:{Lore:["§eKing's Valley : Rare"],Name:"§4§lTlaxan Mask"},AttributeModifiers:[{UUIDMost:32937979772523592l,UUIDLeast:12523234267159625l,Amount:0.15d,Slot:"head",AttributeName:"generic.attackDamage",Operation:1,Name:"generic.attackDamage"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"nbt":ur'''{display:{Name:"§6§lPrismatic Blade"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:2s,id:17s},{lvl:3s,id:34s}],display:{Lore:["§eKing's Valley : Rare"],Name:"§6§lPrismatic Blade"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"nbt":ur'''{display:{Name:"§4§lSearing Wrath"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:5s,id:16s},{lvl:2s,id:34s},{lvl:2s,id:19s},{lvl:2s,id:20s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§8","§7When in main hand:","§7 0.8 Attack Speed","§7 12 Attack Damage","§c -3 Armor"],Name:"§4§lSearing Wrath"},AttributeModifiers:[{UUIDMost:797401l,UUIDLeast:849310l,Amount:8d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:205397l,UUIDLeast:267554l,Amount:-3d,Slot:"mainhand",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:589373l,UUIDLeast:600470l,Amount:-3.2d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:book",
			"nbt":ur'''{display:{Name:"§5§lTome of Arcane Horrors"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:20s},{lvl:3s,id:19s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§8","§7When in main hand:","§7 0.5 Attack Speed","§7 16 Attack Damage"],Name:"§5§lTome of Arcane Horrors"},AttributeModifiers:[{UUIDMost:495321l,UUIDLeast:169768l,Amount:15d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:564922l,UUIDLeast:574772l,Amount:-3.5d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:bow",
			"nbt":ur'''{display:{Name:"§9§lArcane Storm"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:48s},{lvl:3s,id:49s},{lvl:2s,id:34s}],display:{Lore:["§eKing's Valley : Rare"],Name:"§9§lArcane Storm"}}'''
		]
	],
	[
		{
			"id":"minecraft:stick",
			"nbt":ur'''{display:{Name:"§b§lThaumaturge's Greed"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:4s,id:17s},{lvl:1s,id:19s},{lvl:1s,id:20s},{lvl:2s,id:21s}],display:{Lore:["§8* Magic Wand *","§eKing's Valley : Rare"],Name:"§b§lThaumaturge's Greed"}}'''
		]
	],
	[
		{
			"id":"minecraft:chainmail_boots",
			"nbt":ur'''{display:{Name:"§4§lChains of the Damned"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:4s,id:0s},{lvl:1s,id:10s},{lvl:1s,id:70s}],display:{Lore:["§eKing's Valley : Rare"],Name:"§4§lChains of the Damned"},AttributeModifiers:[{UUIDMost:1354465141316075984l,UUIDLeast:-7619938869357070894l,Amount:-0.1d,Slot:"feet",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"},{UUIDMost:-8686196100279418339l,UUIDLeast:-7938211705147810854l,Amount:1.0d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§9§lBoreas Greaves"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:2s},{lvl:5s,id:34s},{lvl:3s,id:4s}],display:{Lore:["§bLeather Armor","§eKing's Valley : Rare"],color:13100779,Name:"§9§lBoreas Greaves"},AttributeModifiers:[{UUIDMost:459286l,UUIDLeast:392956l,Amount:0.1d,Slot:"legs",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:428915l,UUIDLeast:855359l,Amount:2d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:277302l,UUIDLeast:24984l,Amount:0.1d,Slot:"legs",AttributeName:"generic.attackSpeed",Operation:1,Name:"generic.attackSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§d§lArchmage's Vestment"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:0s},{lvl:2s,id:1s},{lvl:2s,id:34s},{lvl:2s,id:3s},{lvl:2s,id:4s}],display:{Lore:["§bLeather Armor","§eKing's Valley : Rare"],color:8201983,Name:"§d§lArchmage's Vestment"}}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"nbt":ur'''{display:{Name:"§3§lStormborn Runeblade"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:1s,id:34s},{lvl:2s,id:19s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§l","§7When in main hand:","§7 2 Attack Speed","§7 6.5 Attack Damage","§9 +10% Speed"],Name:"§3§lStormborn Runeblade"},AttributeModifiers:[{UUIDMost:44607095061251400l,UUIDLeast:17181972604100280l,Amount:0.1d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:32717593065480005l,UUIDLeast:13800488484714149l,Amount:4d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:18508304389737284l,UUIDLeast:65266891060907778l,Amount:-2d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"nbt":ur'''{display:{Name:"§2§lEarthbound Runeblade"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:2s,id:34s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§6","§7When in main hand:","§7 1.6 Attack Speed","§7 6.5 Attack Damage","§9 +2 Armor"],Name:"§2§lEarthbound Runeblade"},AttributeModifiers:[{UUIDMost:67445053026503759l,UUIDLeast:20777435665232169l,Amount:4d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:57037229736289856l,UUIDLeast:7096337185411272l,Amount:2d,Slot:"mainhand",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"},{UUIDMost:29541336158339146l,UUIDLeast:50859522055085541l,Amount:-2.4d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_sword",
			"nbt":ur'''{display:{Name:"§b§lIceborn Runeblade"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:5s,id:16s},{lvl:1s,id:17s},{lvl:3s,id:34s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§7","§7When in main hand:"," §71.2 Attack Speed"," §78 Attack Damage"," §c-10% Speed"],Name:"§b§lIceborn Runeblade"},AttributeModifiers:[{UUIDMost:68342020398380105l,UUIDLeast:18376432692088500l,Amount:-0.1d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:20792108251577155l,UUIDLeast:44880469650724553l,Amount:4d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:49556179849667657l,UUIDLeast:15931220204059978l,Amount:-2.8d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_axe",
			"nbt":ur'''{display:{Name:"§6§lGiant's Axe"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:34s},{lvl:1s,id:19s}],HideFlags:2,display:{Lore:["§eKing's Valley : Rare","§7","§7When in main hand:","§7 0.6 Attack Speed","§7 15 Attack Damage"," §c-8% Speed"],Name:"§6§lGiant's Axe"},AttributeModifiers:[{UUIDMost:50069596546217285l,UUIDLeast:52124018636176511l,Amount:-0.08d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:16684340706050887l,UUIDLeast:61729139377545821l,Amount:14d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"generic.attackDamage"},{UUIDMost:20258808824438599l,UUIDLeast:52420949332344389l,Amount:-3.4d,Slot:"mainhand",AttributeName:"generic.attackSpeed",Operation:0,Name:"generic.attackSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:stone_pickaxe",
			"nbt":ur'''{display:{Name:"§9§lPebblebane"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:32s}],display:{Lore:["§eKing's Valley : Rare","§7","§fNot quite as good as Rockbane!"],Name:"§9§lPebblebane"},AttributeModifiers:[{UUIDMost:251682l,UUIDLeast:651852l,Amount:0.15d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§3§lStormborn Boots"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:2s},{lvl:3s,id:34s},{lvl:2s,id:4s}],display:{Lore:["§eKing's Valley : Rare"],color:16775894,Name:"§3§lStormborn Boots"},AttributeModifiers:[{UUIDMost:8168110272590147l,UUIDLeast:66575962804257055l,Amount:0.05d,Slot:"feet",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:55068906034949703l,UUIDLeast:23695059647787143l,Amount:1d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§2§lEarthbound Pants"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:34s}],display:{Lore:["§eKing's Valley : Rare"],color:11753010,Name:"§2§lEarthbound Pants"},AttributeModifiers:[{UUIDMost:47478565729543745l,UUIDLeast:55464327090482055l,Amount:3d,Slot:"legs",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"},{UUIDMost:44980305394582344l,UUIDLeast:14485042704930583l,Amount:2d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§b§lIceborn Helmet"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:0s},{lvl:3s,id:34s},{lvl:2s,id:5s},{lvl:1s,id:4s}],display:{Lore:["§eKing's Valley : Rare"],color:9107455,Name:"§b§lIceborn Helmet"},AttributeModifiers:[{UUIDMost:46674431434570316l,UUIDLeast:29842133510151376l,Amount:-0.05d,Slot:"head",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"},{UUIDMost:10509373368372805l,UUIDLeast:27250250553169692l,Amount:1d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:shield",
			"nbt":ur'''{display:{Name:"§6§lImperial Bulwark"}}'''
		},
		[
			"nbt", "replace", ur'''{HideFlags:32,BlockEntityTag:{Patterns:[{Pattern:"bri",Color:7},{Pattern:"bo",Color:8},{Pattern:"mr",Color:8},{Pattern:"tts",Color:8},{Pattern:"bts",Color:8}],Base:15},display:{Lore:["§eKing's Valley : Rare"],Name:"§6§lImperial Bulwark"},AttributeModifiers:[{UUIDMost:20324l,UUIDLeast:596443l,Amount:0.4d,Slot:"offhand",AttributeName:"generic.knockbackResistance",Operation:0,Name:"generic.knockbackResistance"}]}'''
		]
	],
	[
		{
			"id":"minecraft:bow",
			"nbt":ur'''{display:{Name:"§4§lDemonbreath"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:48s},{lvl:1s,id:50s},{lvl:2s,id:19s},{lvl:1s,id:20s}],display:{Lore:["§eKing's Valley : Rare"],Name:"§4§lDemonbreath"},AttributeModifiers:[{UUIDMost:-7214717605117081503l,UUIDLeast:-8547664050005874273l,Amount:2.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:bone",
			"nbt":ur'''{display:{Name:"§9§lDeathchill Staff"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:5s,id:16s},{lvl:2s,id:17s}],display:{Lore:["§8* Magic Wand *","§eKing's Valley : Rare"],Name:"§9§lDeathchill Staff"},AttributeModifiers:[{UUIDMost:9215418588072772l,UUIDLeast:29013032778824963l,Amount:0.3d,Slot:"mainhand",AttributeName:"generic.knockbackResistance",Operation:0,Name:"generic.knockbackResistance"},{UUIDMost:15405034991318852l,UUIDLeast:13833242679511430l,Amount:-0.1d,Slot:"mainhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"generic.movementSpeed"}]}'''
		]
	],
	[
		{
			"id":"minecraft:golden_chestplate",
			"nbt":ur'''{display:{Name:"§b§l§nKing's Warden"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:3s,id:0s},{lvl:2s,id:3s},{lvl:1s,id:70s}],display:{Lore:["§6King's Valley : §lEPIC"],Name:"§b§l§nKing's Warden"},AttributeModifiers:[{UUIDMost:96224l,UUIDLeast:26892l,Amount:2d,Slot:"chest",AttributeName:"generic.maxHealth",Operation:0,Name:"generic.maxHealth"},{UUIDMost:348118l,UUIDLeast:433148l,Amount:5d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_boots",
			"nbt":ur'''{display:{Name:"§fTurtle Flippers"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:8s},{lvl:2s,id:3s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier II"],color:36912,Name:"§fTurtle Flippers"},AttributeModifiers:[{UUIDMost:290399l,UUIDLeast:1103793l,Amount:0.75d,Slot:"feet",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_leggings",
			"nbt":ur'''{display:{Name:"§fTurtle Pants"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:8s},{lvl:2s,id:3s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier II"],color:36912,Name:"§fTurtle Pants"},AttributeModifiers:[{UUIDMost:280399l,UUIDLeast:1003793l,Amount:1.0d,Slot:"legs",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_chestplate",
			"nbt":ur'''{display:{Name:"§fTurtle Vest"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:6s},{lvl:2s,id:3s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier II"],color:36912,Name:"§fTurtle Vest"},AttributeModifiers:[{UUIDMost:270399l,UUIDLeast:903793l,Amount:1.5d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:leather_helmet",
			"nbt":ur'''{display:{Name:"§fTurtle Helm"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:5s},{lvl:2s,id:3s}],display:{Lore:["§9Cloth Armor","§8King's Valley : Tier II"],color:36912,Name:"§fTurtle Helm"},AttributeModifiers:[{UUIDMost:260399l,UUIDLeast:803793l,Amount:0.75d,Slot:"head",AttributeName:"generic.armor",Operation:0,Name:"generic.armor"}]}'''
		]
	],
	[
		{
			"id":"minecraft:fishing_rod",
			"nbt":ur'''{display:{Name:"§fAngler's Rod"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:34s},{lvl:3s,id:62s}],display:{Lore:["§8King's Valley : Tier III"],Name:"§fAngler's Rod"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_sword",
			"nbt":ur'''{display:{Name:"§fLight Scimitar"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:1s,id:34s},{lvl:3s,id:22s}],display:{Lore:["§8King's Valley : Tier III"],Name:"§fLight Scimitar"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_axe",
			"nbt":ur'''{display:{Name:"§fTempered Mace"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:16s},{lvl:2s,id:34s},{lvl:2s,id:19s}],display:{Lore:["§8King's Valley : Tier III"],Name:"§fTempered Mace"}}'''
		]
	],
	[
		{
			"id":"minecraft:wooden_pickaxe",
			"nbt":ur'''{display:{Name:"§fSapper's Tool"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:2s,id:32s},{lvl:2s,id:34s},{lvl:1s,id:19s}],display:{Lore:["§8King's Valley : Tier III"],Name:"§fSapper's Tool"}}'''
		]
	],
	[
		{
			"id":"minecraft:potion",
			"nbt":ur'''{display:{Name:"§fNereid Essence"}}'''
		},
		[
			"nbt", "replace", ur'''{CustomPotionColor:49151,CustomPotionEffects:[{Ambient:1b,ShowParticles:1b,Duration:4800,Id:16b,Amplifier:0b},{Ambient:1b,ShowParticles:1b,Duration:4800,Id:13b,Amplifier:0b}],Potion:"minecraft:empty",display:{Name:"§fNereid Essence"}}'''
		]
	],
	[
		{
			"id":"minecraft:lever",
			"nbt":ur'''{display:{Name:"§fDamaged Hilt"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["§8Carved with elegant flowers"],Name:"§fDamaged Hilt"}}'''
		]
	],
	[
		{
			"id":"minecraft:fish",
			"nbt":ur'''{display:{Name:"§b§lMagic Fish"}}'''
		},
		[
			"nbt", "replace", ur'''{display:{Lore:["* Gills *","§7Gives water breathing to you and nearby","§7allies when held in your offhand"],Name:"§b§lMagic Fish"}}'''
		]
	],
	[
		{
			"id":"minecraft:shield",
			"nbt":ur'''{display:{Name:"§b§lTurtle Shield"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:34s}],BlockEntityTag:{Patterns:[{Pattern:"bri",Color:2}],Base:6},display:{Lore:["§8King's Valley : Uncommon"],Name:"§b§lTurtle Shield"},AttributeModifiers:[{UUIDMost:-2699735906624845463l,UUIDLeast:-6308071593572563623l,Amount:-0.05d,Slot:"offhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"},{UUIDMost:-407094390218668203l,UUIDLeast:-9013419339908919017l,Amount:0.4d,Slot:"offhand",AttributeName:"generic.knockbackResistance",Operation:0,Name:"Modifier"}]}'''
		]
	],
	[
		{
			"id":"minecraft:bow",
			"nbt":ur'''{display:{Name:"§b§lOncoming Tide"}}'''
		},
		[
			"nbt", "replace", ur'''{ench:[{lvl:1s,id:49s},{lvl:1s,id:70s}],display:{Lore:["§8King's Valley : Uncommon"],Name:"§b§lOncoming Tide"},AttributeModifiers:[{UUIDMost:1004903320127294777l,UUIDLeast:-6735527447459109365l,Amount:0.07d,Slot:"offhand",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}'''
		]
	],

])

