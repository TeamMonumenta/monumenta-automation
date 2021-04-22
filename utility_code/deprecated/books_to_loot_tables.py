#!/usr/bin/env python3

import hashlib
import json
import os
import re
import sys

from collections import OrderedDict
from datetime import datetime, timedelta

from lib_py3.common import parse_name_possibly_json
from minecraft.world import World

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../quarry"))
from quarry.types import nbt
from quarry.types.text_format import unformat_text

LOOT_TABLE_DIR = '/home/epic/5_SCRATCH/tim/book_test'
RE_PATH_UNSAFE = re.compile('[^0-9a-z._-]+')

status_info = {
    'start_time': datetime.now(),
    'display_every': timedelta(seconds=10),

    'step': 'Starting up...',
    'step_start_time': datetime.now(),
    'step_last_update': datetime(1970, 1, 1),
}


def timedelta_str(delta_t, multiplier=1.0, divisor=1.0):
    seconds_left = int(delta_t.total_seconds() * multiplier / divisor)
    minutes_left, seconds_left = divmod(seconds_left, 60)
    hours_left, minutes_left = divmod(minutes_left, 60)

    if hours_left > 999 or hours_left < 0:
        return '!!!:!!:!!'
    else:
        return f'{hours_left:>3}:{minutes_left:02}:{seconds_left:02}'


def show_progress(status_info, step, message):
    now = datetime.now()
    start_time = status_info['start_time']
    display_every = status_info['display_every']

    if step != status_info['step']:
        status_info['step'] = step
        status_info['step_start_time'] = now
        status_info['step_last_update'] = datetime(1970, 1, 1)
    step_start_time = status_info['step_start_time']
    step_last_update = status_info['step_last_update']

    last_update_elapsed = now - step_last_update
    if last_update_elapsed < display_every:
        return

    step_elapsed = now - step_last_update
    step_elapsed_str = timedelta_str(step_elapsed)

    total_elapsed = now - start_time
    total_elapsed_str = timedelta_str(total_elapsed)

    print(f'[{total_elapsed_str} {step} {step_elapsed_str}] {message}')
    status_info['step_last_update'] = now


def title_sort_key(title):
    unsorted_prefixes = sorted((
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
    ), key=len, reverse=True)

    # Move articles/titles to the end
    while True:
        found_prefix = False
        for unsorted_prefix in unsorted_prefixes:
            if not title.lower().startswith(unsorted_prefix.lower()):
                continue
            found_prefix = True
            title = f'{title[len(unsorted_prefix):]}, {title[:len(unsorted_prefix)]}'

        if not found_prefix:
            break

    return (title.lower(), title)


def save_loot_table(path, item):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    pool = OrderedDict()
    pool["rolls"] = 1
    pool["entries"] = [item.to_loot_table_entry(weight=10),]

    loot_table = OrderedDict()
    loot_table["pools"] = [pool,]

    with open(path, 'w') as fp:
        json.dump(loot_table, fp, ensure_ascii=False, indent=2)


'''
books[title]['minecraft:written_book{...}'] = {
    'shard': 'dungeon',
    'item': Item(...),
    'first_location': '/tp @s 1 2 3',
}
'''
books = {}
num_book_titles = 0
num_unique = 0
num_conflicting = 0

for shard in sorted(os.listdir('/home/epic/project_epic')):
    world_path = os.path.join('/home/epic/project_epic', shard, f'Project_Epic-{shard}')
    if not os.path.isdir(world_path):
        continue

    world = World(world_path, name=shard)
    for region in world.iter_regions(read_only=True):
        for chunk in region.iter_chunks():
            for item in chunk.recursive_iter_items():
                show_progress(status_info, f'Scanning for {shard} books...', f'{num_book_titles} titles, {num_unique} unique, {num_conflicting} conflicting')

                if item.id != 'minecraft:written_book':
                    continue
                if not item.tag.has_path('title'):
                    continue
                if unformat_text(item.tag.at_path('title').value).startswith('Book of Souls'):
                    continue

                if item.tag.has_path('display.Name'):
                    formatted_title = parse_name_possibly_json(item.tag.at_path('display.Name').value)
                elif item.tag.has_path('title'):
                    formatted_title = item.tag.at_path('title').value
                else:
                    continue

                title = unformat_text(formatted_title)
                if len(title) == 0:
                    continue
                command_part = item.to_command_format()

                if title not in books:
                    num_book_titles += 1
                    num_unique += 1
                    books[title] = {}
                if command_part in books[title]:
                    continue
                elif len(books[title]) == 1:
                    num_unique -= 1
                    num_conflicting += 1

                pos = item.pos

                books[title][command_part] = {
                    'shard': shard,
                    'item': item,
                    'first_location': f'/tp @s {pos[0]} {pos[1]} {pos[2]}',
                }


show_progress(status_info, 'Sorting book titles...', 'Please wait...')
book_titles = sorted(books.keys(), key=title_sort_key)
num_book_titles = len(book_titles)

for i, title in enumerate(book_titles):
    show_progress(status_info, 'Generating loot tables...', f'{i} of {num_book_titles}: {title}')

    safe_title = RE_PATH_UNSAFE.sub('', title_sort_key(title)[0].replace(' ', '_'))
    title_path = os.path.join(safe_title[0], safe_title)
    path = os.path.join(LOOT_TABLE_DIR, title_path)

    variants = books[title]
    if len(variants) == 1:
        item = list(variants.values())[0]['item']
        save_loot_table(f'{path}.json', item)

    else:
        path = path + '_conflict'
        for command, item_data in variants.items():
            cmd_hash = hashlib.md5(command.encode()).hexdigest()

            shard = item_data['shard']
            first_location = item_data['first_location']
            item = item_data['item']

            conflict_dir = os.path.join(path, cmd_hash)
            save_loot_table(os.path.join(conflict_dir, f'{safe_title}.move_and_rename_to_json'), item)
            with open(os.path.join(conflict_dir, 'location.txt'), 'w') as fp:
                print(shard, file=fp)
                print(first_location, file=fp)

show_progress(status_info, 'Done', f'{num_book_titles} titles, {num_unique} unique, {num_conflicting} conflicting')
