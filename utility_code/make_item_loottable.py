#!/usr/bin/env python3

import re
import json

while True:
    raw = input("Paste /give command here:")

    # Strip the /give <selector>
    raw = re.sub('^[^ ]* [^ ]* ', '', raw.strip())

    # Strip the count
    raw = re.sub('}[^}]*$', '}', raw.strip())

    item_type = re.sub('{.*$', '', raw)
    nbt = re.sub('^[^{]*{', '{', raw)

    escaped_nbt = json.dumps(nbt, ensure_ascii=False)

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
    # Name:"{\"text\":\"
    name = re.sub(r'Name:"{\\"text\\":\\"', '', namefrag)
    name = re.sub(r'\\.*$', '', name)
    name = name.lower()
    name = re.sub(" +", "_", name)

    #print("item_type:", item_type)
    #print("nbt:", nbt)
    #print("escaped_nbt:", escaped_nbt)
    #print("display:", display)
    #print("namefrag:", namefrag)
    #print("name:", name)

    outfile = open('./{}.json'.format(name), 'w')
    outfile.write('''{
    "pools": [
        {
            "rolls": 1,
            "entries": [
                {
                    "type": "item",
                    "weight": 1,
                    "name": "''' + item_type + '''",
                    "functions": [
                        {
                            "function": "set_nbt",
                            "tag": ''' + escaped_nbt + '''
                        }
                    ]
                }
            ]
        }
    ]
}
''')
    outfile.close()
