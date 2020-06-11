#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))

from quarry.types import nbt

def test_fail(test_str):
    err = False
    try:
        print(nbt.TagCompound.from_mojangson(test_str))
    except SyntaxError as e:
        print("Got expected error:", e)
        err = True
    if not err:
        raise Exception("Negative test case succeeded instead of failing: ", test_str)

def test(test_str):
    print(nbt.TagCompound.from_mojangson(test_str))
    val = nbt.TagCompound.from_mojangson(test_str)
    nop = val.to_mojangson()
    nop = val.to_bytes()
    val.tree()

print("\n\nFail test 1")
test_fail('''x''')
print("\n\nFail test 2")
test_fail('''{xaoeu''')
print("\n\nFail test 3")
test_fail('''{xaoeu:w''')

print("\n\nBasic compound test")
test(r'''{xaoeu:"aoeu"}''')

print("\n\nItem test")
test(r'''{display:{Lore:['{"text":"§9Cloth Armor"}','{"text":"§8King\'s Valley : §6Patron Made"}','{"text":"§1§oA cobalt blue shift"}'],color:37355,Name:"{\"text\":\"§3§lCobaltean Cape\"}"},Enchantments:[{lvl:2s,id:"minecraft:feather_falling"},{lvl:1s,id:"minecraft:mending"},{lvl:1s,id:"minecraft:protection"},{lvl:1s,id:"minecraft:fire_protection"}],AttributeModifiers:[{UUIDMost:-6264657341144218168L,UUIDLeast:-8082316997105348303L,Amount:1.5d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"},{UUIDMost:3502922254951270786L,UUIDLeast:-6810533993790190373L,Amount:-0.1d,Slot:"chest",AttributeName:"generic.maxHealth",Operation:1,Name:"Modifier"},{UUIDMost:-5333876828708518262L,UUIDLeast:-6396568730443630460L,Amount:0.18d,Slot:"chest",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}''')

print("\n\nItem test with spaces")
test(r'''{display: {Lore: ['{"text":"§9Cloth Armor"}', '{"text":"§8King\'s Valley : §6Patron Made"}', '{"text":"§1§oA cobalt blue shift"}'], color: 37355, Name: "{\"text\":\"§3§lCobaltean Cape\"}"}, Enchantments: [{lvl: 1s, id: "minecraft:protection"}, {lvl: 1s, id: "minecraft:fire_protection"}, {lvl: 2s, id: "minecraft:feather_falling"}, {lvl: 1s, id: "minecraft:mending"}], Damage: 0, AttributeModifiers: [{UUIDMost: -6264657341144218168L, UUIDLeast: -8082316997105348303L, Amount: 1.5d, Slot: "chest", AttributeName: "generic.armor", Operation: 0, Name: "Modifier"}, {UUIDMost: 3502922254951270786L, UUIDLeast: -6810533993790190373L, Amount: -0.1d, Slot: "chest", AttributeName: "generic.maxHealth", Operation: 1, Name: "Modifier"}, {UUIDMost: -5333876828708518262L, UUIDLeast: -6396568730443630460L, Amount: 0.18d, Slot: "chest", AttributeName: "generic.movementSpeed", Operation: 1, Name: "Modifier"}]}''')

print("\n\nFirework test")
test(r'''{display:{Lore:['{"text":"§9To signal that you\'re"}','{"text":"§9ready to party!"}'],Name:"{\"text\":\"§5§lSignal Flare - Party Rocket\"}"},Fireworks:{Flight:1b,Explosions:[{Type:2b,Colors:[I;16711680],FadeColors:[I;16738063]},{Type:2b,Colors:[I;526591],FadeColors:[I;15138563]},{Type:2b,Colors:[I;1310467],FadeColors:[I;754951]}]}}''')

print("\n\nBook test / nested quotes")
test(r'''{display:{Name:'{"text":"§2§lNecronomicon"}',Lore:['{"text":"§8Monumenta : §6Patron Made"}','{"text":"§8The lexicon of forbidden knowledge comes"}','{"text":"§8in many forms, some are even cute."}','{"text":"§r"}','{"text":"§7When in main hand:"}','{"text":"§eRight click to spend 10 levels worth"}','{"text":"§eof EXP and remove Poison and Nausea."}']}}''')

print("\n\nFrom mojangson -> to bytes")
test(r'''{display:{Lore:["{\"text\":\"\\u00a78Celsian Isles : \\u00a75Unique\"}","{\"text\":\"\\u00a78A firework enchanted by Ebonee.\"}"],Name:"{\"text\":\"§e§lBewitched Firework\"}"},Enchantments:[{lvl:1s,id:"minecraft:flame"}],Fireworks:{Explosions:[{Type:2b,Trail:1b,Colors:[I;14706431],Flicker:1b,FadeColors:[I;8913151]}]}}''')


# Test that serialization is reverse of deserialization
print("\n\nSerialize/Deserialize test:")
rawinput = r'''{display:{Lore:['{"text":"§9To signal that you\'re"}','{"text":"§9ready to party!"}'],Name:"{\"text\":\"§5§lSignal Flare - Party Rocket\"}"},Fireworks:{Flight:1b,Explosions:[{Type:2b,Colors:[I;16711680],FadeColors:[I;16738063]},{Type:2b,Colors:[I;526591],FadeColors:[I;15138563]},{Type:2b,Colors:[I;1310467],FadeColors:[I;754951]}]}}'''
deserial = nbt.TagCompound.from_mojangson(rawinput)
serial = deserial.to_mojangson()
deserial2 = nbt.TagCompound.from_mojangson(serial)
if not deserial.__eq__(deserial2):
    print("Original deserialized copy:")
    deserial.tree()
    print("")
    print("New deserialized copy:")
    deserial2.tree()
    print("")
    print("Re-serialized intermediate:")
    print(serial)
else:
    print("Same!")
