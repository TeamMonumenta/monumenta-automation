#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

while True:
    raw = input("Paste /give command here:")
    split = raw.split()

    if len(split) < 6:
        print("Too few split components")
        continue

    item_type = split[2]
    damage = split[4]
    nbt = raw[raw.index(split[5]):]

    if "minecraft:" not in item_type:
        print("item type does not contain 'minecraft:'")
        continue

    if "display:" not in nbt:
        print("nbt does not contain 'display:'")
        continue

    display = nbt[nbt.index('display:'):]
    display = re.sub('§[a-z0-9]', '', display)
    display = re.sub("'", '', display)
    display = ''.join([i if ord(i) < 128 else '' for i in display])

    if "Name:" not in display:
        print("display does not contain 'Name:'")
        continue

    namefrag = display[display.index('Name:'):]
    name = re.findall(r'"(.*?)"', namefrag)[0]
    name = name.lower()
    name = re.sub(" +", "_", name)

    outfile = open('./{}.json'.format(name), 'w')
    outfile.write('''{
  "pools": [
    {
      "rolls": 1,
      "entries": [
        {
          "type": "item",
          "name": "''' + item_type + '''",
          "weight": 1,
          "functions": [
''')
    if int(damage) != 0:
        outfile.write('''            {
              "function": "set_data",
              "data": ''' + damage + '''
            },
''')

    outfile.write('''            {
              "function": "set_nbt",
              "tag": "''' + nbt + '''"
            }
          ]
        }
      ]
    }
  ]
}
''')
    outfile.close()
