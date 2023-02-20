#!/usr/bin/env python3

"""A tool to manipulate scores saved to entities themselves"""

import argparse
import json
import sys
from pathlib import Path
from lib_py3.entity_scores import get_entity_scores
from lib_py3.entity_scores import set_entity_scores
from lib_py3.common import equal_if_uuid_str
from lib_py3.scoreboard import Scoreboard
from minecraft.world import World


def test_entity_scores(world):
    """Prints the locations and number of scores for all entities in a world."""
    for region in world.iter_regions():
        for chunk in region.iter_chunks():
            for entity in chunk.recursive_iter_entities():
                scores = get_entity_scores(entity)
                if len(scores) > 0:
                    print(f'{entity.uuid} {entity.get_debug_str()!s:>40}: {len(scores)} scores')


def delete_entity_scores(world):
    """Prints the locations and number of scores for all entities in a world."""
    for region in world.iter_regions():
        for chunk in region.iter_chunks(autosave=True):
            for entity in chunk.recursive_iter_entities():
                set_entity_scores(entity, {})


def export_entity_scores_json(world):
    """Exports the entity scores as json."""
    result = {}

    print(f'Exporting scores from {world.path}')
    for region in world.iter_regions():
        for chunk in region.iter_chunks():
            for entity in chunk.recursive_iter_entities():
                scores = get_entity_scores(entity)
                if len(scores) > 0:
                    result[str(entity.uuid)] = scores

    print(f'Found {len(result)} entities with scores in {world.path}')
    return result


def import_entity_scores_json(world, all_entity_scores):
    """Imports the entity scores from json."""
    result = {}

    print(f'Importing scores to {world.path}')
    import_count = 0
    for region in world.iter_regions():
        for chunk in region.iter_chunks(autosave=True):
            for entity in chunk.recursive_iter_entities():
                scores = all_entity_scores.get(str(entity.uuid), {})
                set_entity_scores(entity, scores)
                import_count += len(scores)

    print(f'Imported {import_count} scores to {world.path}')
    return result


def main():
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument('world_path', type=Path, nargs='+')
    arg_parser.add_argument('--test', action='store_true',
        help="Display the number of scores for each entity that has any")
    arg_parser.add_argument('--delete', action='store_true',
        help="Deletes the scores of all entities in a world")
    arg_parser.add_argument('--export', type=Path, nargs='?',
        help="Exports the scores of the entities in a world as json")
    arg_parser.add_argument('--import', type=Path, nargs='?', dest='import_',
        help="Imports the scores of the entities in a world from json")
    args = arg_parser.parse_args()

    test = args.test
    delete = args.delete
    export_ = args.export
    import_ = args.import_

    if sum([
        test,
        delete,
        export_ is not None,
        import_ is not None,
    ]) != 1:
        print('Select only one operating mode (test, delete, export, import)',
            file=sys.stderr, flush=True)
        sys.exit('Invalid mode selection')

    world_paths = args.world_path
    got_bad_path = False
    for world_path in world_paths:
        if not (world_path / 'level.dat').is_file():
            got_bad_path = True
            print(f'{world_path} is not a world', file=sys.stderr, flush=True)
    if got_bad_path:
        sys.exit('Not all world paths are worlds.')

    if test:
        for world_path in world_paths:
            world = World(world_path)
            test_entity_scores(world)

    elif delete:
        for world_path in world_paths:
            print(f'Deleting scores from entities in {world_path}')
            world = World(world_path)
            delete_entity_scores(world)
        print('Done')

    elif export_ is not None:
        result = {}
        for world_path in world_paths:
            world = World(world_path)
            for entity, scores in export_entity_scores_json(world).items():
                result[entity] = scores
        with open(export_, 'w', encoding='utf-8') as export_file:
            json.dump(result, export_file, ensure_ascii=False, indent=2)

    elif import_ is not None:
        all_scores = {}
        with open(import_, 'r', encoding='utf-8') as import_file:
            contents = import_file.read()
            if contents[0] == chr(0xfeff):
                contents = contents[1:]
            all_scores = json.loads(contents)
        
        for world_path in world_paths:
            world = World(world_path)
            import_entity_scores_json(world, all_scores)


if __name__ == '__main__':
    main()
