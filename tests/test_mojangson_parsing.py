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
    nbt.TagCompound.from_mojangson(test_str).tree()

print("\n\nFail test 1")
test_fail('''x''')
print("\n\nFail test 2")
test_fail('''{xaoeu''')
print("\n\nFail test 3")
test_fail('''{xaoeu:w''')

# Simple test
print("\n\nBasic compound test")
test(r'''{xaoeu:"aoeu"}''')
# Item test
print("\n\nItem test")
test(r'''{display:{Lore:["§9Cloth Armor","§8King's Valley : §6Patron Made","§1§oA cobalt blue shift"],color:37355,Name:"{\"text\":\"§3§lCobaltean Cape\"}"},Enchantments:[{lvl:2s,id:"minecraft:feather_falling"},{lvl:1s,id:"minecraft:mending"},{lvl:1s,id:"minecraft:protection"},{lvl:1s,id:"minecraft:fire_protection"}],AttributeModifiers:[{UUIDMost:-6264657341144218168L,UUIDLeast:-8082316997105348303L,Amount:1.5d,Slot:"chest",AttributeName:"generic.armor",Operation:0,Name:"Modifier"},{UUIDMost:3502922254951270786L,UUIDLeast:-6810533993790190373L,Amount:-0.1d,Slot:"chest",AttributeName:"generic.maxHealth",Operation:1,Name:"Modifier"},{UUIDMost:-5333876828708518262L,UUIDLeast:-6396568730443630460L,Amount:0.18d,Slot:"chest",AttributeName:"generic.movementSpeed",Operation:1,Name:"Modifier"}]}''')
# Item test with spaces
print("\n\nItem test with spaces")
test(r'''{display: {Lore: ["§9Cloth Armor", "§8King's Valley : §6Patron Made", "§1§oA cobalt blue shift"], color: 37355, Name: "{\"text\":\"§3§lCobaltean Cape\"}"}, Enchantments: [{lvl: 1s, id: "minecraft:protection"}, {lvl: 1s, id: "minecraft:fire_protection"}, {lvl: 2s, id: "minecraft:feather_falling"}, {lvl: 1s, id: "minecraft:mending"}], Damage: 0, AttributeModifiers: [{UUIDMost: -6264657341144218168L, UUIDLeast: -8082316997105348303L, Amount: 1.5d, Slot: "chest", AttributeName: "generic.armor", Operation: 0, Name: "Modifier"}, {UUIDMost: 3502922254951270786L, UUIDLeast: -6810533993790190373L, Amount: -0.1d, Slot: "chest", AttributeName: "generic.maxHealth", Operation: 1, Name: "Modifier"}, {UUIDMost: -5333876828708518262L, UUIDLeast: -6396568730443630460L, Amount: 0.18d, Slot: "chest", AttributeName: "generic.movementSpeed", Operation: 1, Name: "Modifier"}]}''')

# Firework test
print("\n\nFirework test")
test(r'''{display:{Lore:["§9To signal that you're","§9ready to party!"],Name:"{\"text\":\"§5§lSignal Flare - Party Rocket\"}"},Fireworks:{Flight:1b,Explosions:[{Type:2b,Colors:[I;16711680],FadeColors:[I;16738063]},{Type:2b,Colors:[I;526591],FadeColors:[I;15138563]},{Type:2b,Colors:[I;1310467],FadeColors:[I;754951]}]}}''')

# Test that serialization is reverse of deserialization
print("\n\nSerialize/Deserialize test:")
rawinput = r'''{display:{Lore:["§9To signal that you're","§9ready to party!"],Name:"{\"text\":\"§5§lSignal Flare - Party Rocket\"}"},Fireworks:{Flight:1b,Explosions:[{Type:2b,Colors:[I;16711680],FadeColors:[I;16738063]},{Type:2b,Colors:[I;526591],FadeColors:[I;15138563]},{Type:2b,Colors:[I;1310467],FadeColors:[I;754951]}]}}'''
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
