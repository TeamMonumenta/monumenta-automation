#!/usr/bin/env python3

import os
import sys
from collections import namedtuple

from minecraft.chunk_format.schematic import Schematic
from minecraft.chunk_format.structure import Structure
from minecraft.world import World

NamespacedKey = namedtuple('NamespacedKey', ['namespace', 'key'])

schematics_path = '/home/epic/project_epic/server_config/data/structures'
structures_path = '/home/epic/project_epic/server_config/data/generated'
structures_path_template = structures_path + '/{}/structures/{}.nbt'

unverified_names = set()


def register_structure_name_from_block(names, block_entity, ignored_names=None):
    if block_entity.id != 'minecraft:structure_block':
        return
    if not block_entity.nbt.has_path('name'):
        return
    structure_name = block_entity.nbt.at_path('name').value
    if structure_name == '' or structure_name.count(':') > 1:
        return
    if ':' not in structure_name:
        structure_name = 'minecraft:' + structure_name
    namespace, key = structure_name.split(':')
    name = NamespacedKey(namespace, key)
    if ignored_names and name in ignored_names:
        return
    names.add(name)

if __name__ == '__main__':
    print('Scanning for used structure blocks...')


    print('Scanning shards...')
    for shard in sorted(os.listdir('/home/epic/project_epic')):
        world_path = f'/home/epic/project_epic/{shard}/Project_Epic-{shard}'
        world = None
        try:
            os.listdir(os.path.join(world_path, 'region'))
            world = World(world_path)
        except Exception:
            continue
        print(f'Scanning {shard} shard...')
        for region in world.iter_regions(read_only=True):
            for chunk in region.iter_chunks():
                for block_entity in chunk.recursive_iter_block_entities():
                    register_structure_name_from_block(unverified_names, block_entity)

    print('Scanning schematics...')
    for dirpath, subdirs, files in os.walk(schematics_path):
        for fname in files:
            if fname.endswith(".schematic"):
                schem = Schematic(os.path.join(dirpath, fname))
                for block_entity in schem.recursive_iter_block_entities():
                    register_structure_name_from_block(unverified_names, block_entity)

    structure_names = set()
    seen_names = set()
    missing_names = set()
    bad_names = set()
    good_names = set()

    while len(unverified_names) > 0:
        verifying_names = unverified_names
        seen_names |= verifying_names
        unverified_names = set()

        for structure_name in set(verifying_names):
            namespace, key = structure_name

            structure_path = structures_path_template.format(namespace, key)
            if not os.path.isfile(structure_path):
                missing_names.add(structure_name)
                continue

            try:
                struct = Structure(structure_path)
                for block_entity in struct.recursive_iter_block_entities():
                    register_structure_name_from_block(unverified_names, block_entity, seen_names)
                good_names.add(structure_name)
            except Exception:
                bad_names.add(structure_name)

    print('Scanning for unused structures...')
    unused_names = set()
    for namespace in os.listdir(structures_path):
        top = f'{structures_path}/{namespace}/structures'
        for dirpath, subdirs, files in os.walk(top):
            key_folder = ''
            if dirpath != top:
                key_folder = dirpath[len(top)+1:]

            for file in files:
                if not file.endswith('.nbt'):
                    continue

                name = NamespacedKey(namespace, os.path.join(key_folder, file[:-len('.nbt')]))
                if name in seen_names:
                    continue
                unused_names.add(name)

    print('Good structures:')
    for name in sorted(good_names):
        print(f'- {name.namespace}:{name.key}')
    print('')

    print('Missing structures:')
    for name in sorted(missing_names):
        print(f'- {name.namespace}:{name.key}')
    print('')

    print('Bad structures:')
    for name in sorted(bad_names):
        print(f'- {name.namespace}:{name.key}')
    print('')

    print('Unused structures:')
    for name in sorted(unused_names):
        print(f'- {name.namespace}:{name.key}')
