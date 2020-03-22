#!/usr/bin/env python3

# A usage idea:
# find datapacks scriptedquests -name '*.json' > jsonfiles.txt
# while read line; do python3 json_pretty.py $line; done < jsonfiles.txt
# find . -type f -name '*.json' -o -name '*.mcfunction' -exec dos2unix {} \;

import json
import sys

if len(sys.argv) != 2:
    sys.exit("Usage: filename.json")

filename = sys.argv[1]


try:
    with open(filename, "r") as fin:
        data = json.load(fin)
    with open(filename, "w") as fout:
        json.dump(data, fout, ensure_ascii=False, sort_keys=False, indent=4, separators=(',', ': '))
        fout.write('\n')
except Exception as ex:
    print("{}: {}".format(filename, ex));
