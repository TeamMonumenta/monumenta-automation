#!/usr/bin/env python3

import os
import re

from lib_py3.loot_table_manager import LootTableManager


RE_PATH_UNSAFE = re.compile('[^0-9a-z._-]+')
RE_DOUBLE_UNDERSCORE = re.compile('__+')


UNSORTED_PREFIXES = tuple([s.lower() for s in (
    # Tlaxan
    "C'",
    "R'",
    "Ta'",
    "T'",
    "Z'",

    # English articles
    "An ",
    "A ",
    "The ",

    # English honorifics (wikipedia)
    # Common titles
    "Master ",
    "Mr ",
    "Mr. ",
    "Mister ", # For some reason not explicitly listed
    "Miss ",
    "Mrs ",
    "Mrs. ",
    "Ms ",
    "Ms. ",
    "Mx ",
    "Mx. ",

    # Formal titles
    "Sir ",
    "Gentleman ",
    "Sire ",
    "Mistress ",
    "Madam ",
    "Ma'am ",
    "Dame ",
    "Lord ",
    "Baron ",
    "Viscount ",
    "Count ",
    "Earl ",
    "Marquess ",
    "Lady ",
    "Baroness ",
    "Viscountess ",
    "Countess ",
    "Marchioness ",
    "Esq ",
    "Excellency ",
    "His Honour ",
    "Her Honour ",
    "The Honourable ",
    "The Right Honourable ",
    "The Most Honourable ",

    # Academic and professional titles
    "Dr ",
    "Dr. ",
    "Doctor ",
    "Doc ",
    "PhD ",
    "Ph.D. ",
    "DPhil ",
    "MD ",
    "M.D. ",
    "Professor ",
    "Prof ",
    "Cl ",
    "SCl ",
    "Chancellor ",
    "Vice-Chancellor ",
    "Principal ",
    "Vice-Principal ",
    "President ",
    "Vice-President ",
    "Master ",
    "Warden ",
    "Dean ",
    "Regent ",
    "Rector ",
    "Provost ",
    "Director ",
    "Chief Executive ",

    # Skipping the religious ones because this is already kinda long, thanks...

    # How are these not listed?
    "King ",
    "Queen ",
    "Duchess ",
)])


def move_prefixes_to_end(text):
    """Assumes text is already lowercase"""
    result = []
    while True:
        found_prefix = False
        for unsorted_prefix in UNSORTED_PREFIXES:
            if not text.startswith(unsorted_prefix):
                continue
            found_prefix = True
            result.append(text[:len(unsorted_prefix)].rstrip(' '))
            text = text[len(unsorted_prefix):]

        if not found_prefix:
            break

    return ", ".join([text] + result)


def main():
    mgr = LootTableManager()
    mgr.load_loot_tables_subdirectories("/home/epic/project_epic/server_config/data/datapacks")

    for item_id, next_map in sorted(mgr.item_map.items()):
        for item_name in sorted(next_map.keys()):
            print(f'{item_id} named {item_name}')


if __name__ == '__main__':
    main()
