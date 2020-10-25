#!/usr/bin/env python3

import sys
import os
from pprint import pprint
from lib_py3.common import parse_name_possibly_json
from lib_py3.schematic import Schematic
from lib_py3.library_of_souls import LibraryOfSouls
from lib_py3.world import World

los = LibraryOfSouls("/home/epic/project_epic/mobs/plugins/LibraryOfSouls/souls_database.json")
los.upgrade_all()
los.save()
