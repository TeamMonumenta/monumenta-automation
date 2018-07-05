#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
Partially complete potion replacements - do not use. The goal is to standardize
the base potion and give each potion a unique name. Any potions not in this
list when done are player-brewed, and questionably allowed.
"""

from lib_monumenta import item_replace

KingsValleyPotions = item_replace.ReplaceItems([],[
  [
    {
      'id':'minecraft:potion',
      'nbt':ur'''{CustomPotionColor:49151,CustomPotionEffects:[{Ambient:1b,ShowParticles:1b,Duration:4800,Id:16b,Amplifier:0b},{Ambient:1b,ShowParticles:1b,Duration:4800,Id:13b,Amplifier:0b}],Potion:"minecraft:empty",display:{Name:"§fNereid Essence"}}''',
    },
    [
      'name', 'set', ur'''Nereid Essence'''
    ]
  ],
  [
    {
      'id':'minecraft:potion',
      'nbt':ur'''{CustomPotionColor:0,CustomPotionEffects:[{Ambient:1b,ShowParticles:1b,Duration:2400,Id:1b,Amplifier:1b},{Ambient:1b,ShowParticles:1b,Duration:2400,Id:22b,Amplifier:0b}],Potion:"minecraft:empty",display:{Name:"§fEnderblood"}}''',
    },
    [
      'name', 'set', ur'''Enderblood'''
    ]
  ],
  [
    {
      'id':'minecraft:splash_potion',
      'nbt':ur'''{CustomPotionColor:4239424,CustomPotionEffects:[{Ambient:1b,ShowParticles:1b,Duration:40,Id:10b,Amplifier:2b},{Ambient:1b,ShowParticles:1b,Duration:30,Id:19b,Amplifier:2b}],Potion:"minecraft:empty",display:{Lore:["§7Removes Poison II and lower"],Name:"§fAntidote"}}''',
    },
    [
      'name', 'set', ur'''Antidote'''
    ]
  ],
  [
    {
      'id':'minecraft:splash_potion',
      'nbt':ur'''{CustomPotionColor:13947904,CustomPotionEffects:[{Ambient:0b,ShowParticles:0b,Duration:600,Id:22b,Amplifier:1b},{Ambient:1b,ShowParticles:1b,Duration:100,Id:10b,Amplifier:1b}],Potion:"minecraft:mundane",display:{Name:"§fPotion of Salvation"}}''',
    },
    [
      'name', 'set', ur'''Potion of Salvation''',
      'nbt', 'update', ur'''{Potion:"minecraft:empty"}''',
    ]
  ],
  [
    {
      'id':'minecraft:potion',
      'nbt':ur'''{CustomPotionColor:255,CustomPotionEffects:[{Ambient:1b,ShowParticles:1b,Duration:3600,Id:16b,Amplifier:0b}],Potion:"minecraft:empty",display:{Name:"§fPotion of Night Vision"}}''',
    },
    [
      'name', 'set', ur'''Potion of Night Vision'''
    ]
  ],
  [
    {
      'id':'minecraft:lingering_potion',
      'nbt':ur'''{CustomPotionColor:160,CustomPotionEffects:[{Ambient:1b,ShowParticles:1b,Duration:400,Id:2b,Amplifier:4b},{Ambient:1b,ShowParticles:1b,Duration:400,Id:4b,Amplifier:0b},{Ambient:1b,ShowParticles:1b,Duration:400,Id:19b,Amplifier:0b}],Potion:"minecraft:empty",display:{Name:"§aStrong Barrier Potion"}}''',
    },
    [
      'name', 'set', ur'''Strong Barrier Potion'''
    ]
  ],
  [
    {
      'id':'minecraft:lingering_potion',
      'nbt':ur'''{CustomPotionColor:16744576,CustomPotionEffects:[{Ambient:1b,ShowParticles:1b,Duration:240,Id:10b,Amplifier:2b},{Ambient:1b,ShowParticles:1b,Duration:900,Id:22b,Amplifier:0b}],Potion:"minecraft:empty",display:{Name:"§aStrong Sanctify Potion"}}''',
    },
    [
      'name', 'set', ur'''Strong Sanctify Potion'''
    ]
  ],
  [
    {
      'id':'minecraft:splash_potion',
      'nbt':ur'''{CustomPotionColor:12058624,CustomPotionEffects:[{Ambient:0b,ShowParticles:0b,Duration:20,Id:6b,Amplifier:2b}],Potion:"minecraft:mundane",display:{Name:"§aRevenant's Potion"}}''',
    },
    [
      'name', 'set', ur'''Revenant's Potion''',
      'nbt', 'update', ur'''{Potion:"minecraft:empty"}''',
    ]
  ],
  [
    {
      'id':'minecraft:splash_potion',
      'nbt':ur'''{CustomPotionColor:16318241,CustomPotionEffects:[{Ambient:0b,ShowParticles:0b,Duration:1800,Id:22b,Amplifier:1b}],Potion:"minecraft:mundane",display:{Name:"§aPotion of Protection"}}''',
    },
    [
      'name', 'set', ur'''Potion of Protection''',
      'nbt', 'update', ur'''{Potion:"minecraft:empty"}''',
    ]
  ],
  [
    {
      'id':'minecraft:potion',
      'nbt':ur'''{CustomPotionColor:255,CustomPotionEffects:[{Ambient:1b,ShowParticles:1b,Duration:9600,Id:16b,Amplifier:0b}],Potion:"minecraft:empty",display:{Name:"§fPotion of Night Vision"}}''',
    },
    [
      'name', 'set', ur'''Extended Potion of Night Vision'''
    ]
  ],
  [
    {
      'id':'minecraft:potion',
      'nbt':ur'''{CustomPotionColor:16449532,CustomPotionEffects:[{Ambient:0b,ShowParticles:1b,Duration:21600,Id:10b,Amplifier:0b},{Ambient:0b,ShowParticles:1b,Duration:21600,Id:16b,Amplifier:0b},{Ambient:0b,ShowParticles:1b,Duration:21600,Id:24b,Amplifier:0b}],Potion:"minecraft:empty",display:{Lore:["§8King's Valley : §eRare","§cEphemeral Corridors"],Name:"§f§lEssence of the Spirits"}}''',
    },
    [
      'name', 'set', ur'''Essence of the Spirits'''
    ]
  ],
  [
    {
      'id':'minecraft:potion',
      'nbt':ur'''{CustomPotionColor:255,CustomPotionEffects:[{Ambient:1b,ShowParticles:1b,Duration:19200,Id:11b,Amplifier:0b},{Ambient:1b,ShowParticles:1b,Duration:19200,Id:16b,Amplifier:0b},{Ambient:1b,ShowParticles:1b,Duration:19200,Id:13b,Amplifier:0b}],Potion:"minecraft:empty",display:{Lore:["§8King's Valley : §eRare","§cEphemeral Corridors"],Name:"§3§lEssence of Water"}}''',
    },
    [
      'name', 'set', ur'''Essence of Water'''
    ]
  ],
  [
    {
      'id':'minecraft:potion',
      'nbt':ur'''{CustomPotionColor:15438662,CustomPotionEffects:[{Ambient:0b,ShowParticles:1b,Duration:9600,Id:5b,Amplifier:0b},{Ambient:0b,ShowParticles:1b,Duration:9600,Id:22b,Amplifier:0b},{Ambient:0b,ShowParticles:1b,Duration:9600,Id:12b,Amplifier:0b}],Potion:"minecraft:empty",display:{Lore:["§8King's Valley : §eRare","§cEphemeral Corridors"],Name:"§c§lEssence of Flame"}}''',
    },
    [
      'name', 'set', ur'''Essence of Flame'''
    ]
  ],
  [
    {
      'id':'minecraft:potion',
      'nbt':ur'''{CustomPotionColor:7000823,CustomPotionEffects:[{Ambient:0b,ShowParticles:1b,Duration:24000,Id:2b,Amplifier:0b},{Ambient:0b,ShowParticles:1b,Duration:24000,Id:10b,Amplifier:0b},{Ambient:0b,ShowParticles:1b,Duration:24000,Id:21b,Amplifier:2b}],Potion:"minecraft:empty",display:{Lore:["§8King's Valley : §eRare","§cEphemeral Corridors"],Name:"§b§lEssence of Frost"}}''',
    },
    [
      'name', 'set', ur'''Essence of Frost'''
    ]
  ],
  [
    {
      'id':'minecraft:potion',
      'nbt':ur'''{CustomPotionColor:2490368,CustomPotionEffects:[{Ambient:0b,ShowParticles:1b,Duration:14400,Id:1b,Amplifier:0b},{Ambient:0b,ShowParticles:1b,Duration:14400,Id:3b,Amplifier:1b},{Ambient:0b,ShowParticles:1b,Duration:14400,Id:8b,Amplifier:1b}],Potion:"minecraft:empty",display:{Lore:["§8King's Valley : §eRare","§cEphemeral Corridors"],Name:"§8§lEssence of Arachnid"}}''',
    },
    [
      'name', 'set', ur'''Essence of Arachnid'''
    ]
  ],
  [
    {
      'id':'minecraft:potion',
      'nbt':ur'''{CustomPotionColor:11050584,CustomPotionEffects:[{Ambient:0b,ShowParticles:0b,Duration:20,Id:6b,Amplifier:2b},{Ambient:0b,ShowParticles:1b,Duration:19200,Id:11b,Amplifier:0b},{Ambient:0b,ShowParticles:1b,Duration:19200,Id:22b,Amplifier:1b},{Ambient:0b,ShowParticles:1b,Duration:19200,Id:24b,Amplifier:0b}],Potion:"minecraft:empty",display:{Lore:["§8King's Valley : §eRare","§cEphemeral Corridors"],Name:"§6§lEssence of Sand"}}''',
    },
    [
      'name', 'set', ur'''Essence of Sand'''
    ]
  ],
  [
    {
      'id':'minecraft:potion',
      'nbt':ur'''{CustomPotionColor:11976507,CustomPotionEffects:[{Ambient:0b,ShowParticles:1b,Duration:4800,Id:1b,Amplifier:0b},{Ambient:0b,ShowParticles:1b,Duration:2400,Id:8b,Amplifier:3b},{Ambient:0b,ShowParticles:1b,Duration:100,Id:26b,Amplifier:0b}],Potion:"minecraft:empty",display:{Lore:["§8King's Valley : §5Unique Event","§eEaster 2018"],Name:"§e§lFluffy's Blessing"}}''',
    },
    [
      'name', 'set', ur'''Fluffy's Blessing'''
    ]
  ],
  [
    {
      'id':'minecraft:potion',
      'nbt':ur'''{CustomPotionEffects:[{Ambient:0b,ShowParticles:0b,Duration:4800,Id:5b,Amplifier:0b},{Ambient:0b,ShowParticles:0b,Duration:4800,Id:22b,Amplifier:2b},{Ambient:0b,ShowParticles:0b,Duration:4800,Id:3b,Amplifier:0b}],Potion:"minecraft:empty",display:{Lore:["§8King's Valley : §5Unique"],Name:"§6§lElixir of the Jaguar"}}''',
    },
    [
      'name', 'set', ur'''Elixir of the Jaguar'''
    ]
  ],
  [
    {
      'id':'minecraft:lingering_potion',
      'nbt':ur'''{CustomPotionColor:16744576,CustomPotionEffects:[{Ambient:1b,ShowParticles:1b,Duration:300,Id:10b,Amplifier:0b}],Potion:"minecraft:empty",display:{Name:"§fWeak Sanctify Potion"}}''',
    },
    [
      'name', 'set', ur'''Weak Sanctify Potion'''
    ]
  ],
  [
    {
      'id':'minecraft:lingering_potion',
      'nbt':ur'''{CustomPotionColor:16744576,CustomPotionEffects:[{Ambient:1b,ShowParticles:1b,Duration:300,Id:10b,Amplifier:1b},{Ambient:1b,ShowParticles:1b,Duration:600,Id:22b,Amplifier:0b}],Potion:"minecraft:empty",display:{Name:"§fSanctify Potion"}}''',
    },
    [
      'name', 'set', ur'''Sanctify Potion'''
    ]
  ],
  [
    {
      'id':'minecraft:lingering_potion',
      'nbt':ur'''{CustomPotionColor:160,CustomPotionEffects:[{Ambient:1b,ShowParticles:1b,Duration:300,Id:2b,Amplifier:2b}],Potion:"minecraft:empty",display:{Name:"§fWeak Barrier Potion"}}''',
    },
    [
      'name', 'set', ur'''Weak Barrier Potion'''
    ]
  ],
  [
    {
      'id':'minecraft:lingering_potion',
      'nbt':ur'''{CustomPotionColor:160,CustomPotionEffects:[{Ambient:1b,ShowParticles:1b,Duration:360,Id:2b,Amplifier:3b},{Ambient:1b,ShowParticles:1b,Duration:360,Id:4b,Amplifier:0b}],Potion:"minecraft:empty",display:{Name:"§fBarrier Potion"}}''',
    },
    [
      'name', 'set', ur'''Barrier Potion'''
    ]
  ],
  [
    {
      'id':'minecraft:splash_potion',
      'nbt':ur'''{CustomPotionColor:16756736,CustomPotionEffects:[{Ambient:1b,ShowParticles:1b,Duration:200,Id:12b,Amplifier:0b}],Potion:"minecraft:empty",display:{Name:"§fExtinguisher"}}''',
    },
    [
      'name', 'set', ur'''Extinguisher'''
    ]
  ],
  [
    {
      'id':'minecraft:potion',
      'nbt':ur'''{CustomPotionColor:16056315,CustomPotionEffects:[{Ambient:1b,ShowParticles:1b,Duration:6000,Id:5b,Amplifier:1b},{Ambient:1b,ShowParticles:1b,Duration:6000,Id:11b,Amplifier:1b},{Ambient:1b,ShowParticles:1b,Duration:6000,Id:2b,Amplifier:1b}],Potion:"minecraft:empty",display:{Lore:["§8King's Valley : §5Unique Event","§9Winter 2017"],Name:"§9§lFangorn Draught"}}''',
    },
    [
      'name', 'set', ur'''Fangorn Draught'''
    ]
  ],
])
