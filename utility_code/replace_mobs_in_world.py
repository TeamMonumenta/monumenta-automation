#!/usr/bin/env python3

# For interactive shell
import readline
import code

import sys
import os
import getopt
import re
from pprint import pprint

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt

from lib_py3.iterators.recursive_entity_iterator import get_debug_string_from_entity_path
from lib_py3.common import eprint
from lib_py3.world import World

mobs_to_replace = [
    {
        'rules': {
            'id': 'minecraft:zombie_pigman'
            'name': 'Kreepa Kultist'
        },
        'nbt': r'''{Anger:9999s,CustomName:"{\"text\":\"Kreepa Kultist\"}",Health:40.0f,ArmorItems:[{id:"minecraft:iron_boots",Count:1b,tag:{display:{Name:"{\"text\":\"§bKreepaIronBoots\"}"}}},{id:"minecraft:iron_leggings",Count:1b,tag:{display:{Name:"{\"text\":\"§bKreepaIronPants\"}"}}},{id:"minecraft:leather_chestplate",Count:1b,tag:{display:{color:8398884,Name:"{\"text\":\"§bKreepaChest\"}"}}},{id:"minecraft:creeper_head",Count:1b,tag:{display:{Name:"{\"text\":\"§bKreepaHead\"}"}}}],Attributes:[{Base:40.0d,Name:"generic.maxHealth"}],id:"minecraft:zombie_pigman",HandItems:[{id:"minecraft:stone_sword",Count:1b,tag:{display:{Name:"{\"text\":\"§bPoison Ivy\"}"},Enchantments:[{lvl:1s,id:"minecraft:knockback"}],AttributeModifiers:[{UUIDMost:-3110836741443598160L,UUIDLeast:-9119148225133807228L,Amount:7.0d,Slot:"mainhand",AttributeName:"generic.attackDamage",Operation:0,Name:"Modifier"}]}},{}]}''',
    },
]

def usage():
    sys.exit("Usage: {} <--world /path/to/world> [--logfile <stdout|stderr|path>] [--dry-run] [--interactive]".format(sys.argv[0]))

try:
    opts, args = getopt.getopt(sys.argv[1:], "w:l:di", ["world=", "logfile=", "dry-run", "interactive"])
except getopt.GetoptError as err:
    eprint(str(err))
    usage()

world_path = None
logfile = 'stdout'
dry_run = False
interactive = False

for o, a in opts:
    if o in ("-w", "--world"):
        world_path = a
    elif o in ("-l", "--logfile"):
        logfile = a
    elif o in ("-d", "--dry-run"):
        dry_run = True
    elif o in ("-i", "--interactive"):
        interactive = True
    else:
        eprint("Unknown argument: {}".format(o))
        usage()

if world_path is None:
    eprint("--world must be specified!")
    usage()

pprint(mobs_to_replace_dict)
