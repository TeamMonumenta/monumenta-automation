"""Iterator abstraction layer to aid upgrades."""

import math

from minecraft.world import World

def _new_chunk_iterator(world, min_x, min_y, min_z, max_x, max_y, max_z, autosave=False):
    for region in world.iter_regions():
        if (
            512*region.rx + 512 <= min_x or
            512*region.rx       >  max_x or
            512*region.rz + 512 <= min_z or
            512*region.rz       >  max_z
        ):
            continue

        for chunk in region.iter_chunks():
            if (
                16*chunk.cx + 16 <= min_x or
                16*chunk.cx      >  max_x or
                16*chunk.cz + 16 <= min_z or
                16*chunk.cz      >  max_z
            ):
                continue

            yield chunk

            if autosave:
                region.save_chunk(chunk)

def base_chunk_entity_iterator(world, pos1=None, pos2=None, readonly=True):
    if pos1 is not None and pos2 is not None:
        min_x = min(pos1[0],pos2[0])
        min_y = min(pos1[1],pos2[1])
        min_z = min(pos1[2],pos2[2])

        max_x = max(pos1[0],pos2[0])
        max_y = max(pos1[1],pos2[1])
        max_z = max(pos1[2],pos2[2])
    else:
        min_x = -math.inf
        min_y = -math.inf
        min_z = -math.inf

        max_x = math.inf
        max_y = math.inf
        max_z = math.inf

    if isinstance(world, str):
        world = World(world)
    elif not isinstance(world, World):
        world = World(world.path)

    for chunk in _new_chunk_iterator(world, min_x, min_y, min_z, max_x, max_y, max_z, autosave=(not readonly)):
        for block_entity in chunk.iter_block_entities(min_x, min_y, min_z, max_x, max_y, max_z):
            yield block_entity.nbt
        for entity in chunk.iter_entities(min_x, min_y, min_z, max_x, max_y, max_z):
            yield entity.nbt

def item_iterator(world, pos1=None, pos2=None, readonly=True, no_players=False, players_only=False):
    if pos1 is not None and pos2 is not None:
        min_x = min(pos1[0],pos2[0])
        min_y = min(pos1[1],pos2[1])
        min_z = min(pos1[2],pos2[2])

        max_x = max(pos1[0],pos2[0])
        max_y = max(pos1[1],pos2[1])
        max_z = max(pos1[2],pos2[2])
    else:
        min_x = -math.inf
        min_y = -math.inf
        min_z = -math.inf

        max_x = math.inf
        max_y = math.inf
        max_z = math.inf

    if isinstance(world, str):
        world = World(world)
    elif not isinstance(world, World):
        world = World(world.path)

    if not no_players:
        for player in world.iter_players(autosave=(not readonly)):
            for item in player.recursive_iter_items():
                yield item.nbt, item.root_entity.pos, item.get_legacy_debug()

    if not players_only:
        for chunk in _new_chunk_iterator(world, min_x, min_y, min_z, max_x, max_y, max_z, autosave=(not readonly)):
            for item in chunk.recursive_iter_items(min_x, min_y, min_z, max_x, max_y, max_z):
                yield item.nbt, item.root_entity.pos, item.get_legacy_debug()

def recursive_entity_iterator(world, pos1=None, pos2=None, readonly=True, no_players=False, players_only=False):
    if pos1 is not None and pos2 is not None:
        min_x = min(pos1[0],pos2[0])
        min_y = min(pos1[1],pos2[1])
        min_z = min(pos1[2],pos2[2])

        max_x = max(pos1[0],pos2[0])
        max_y = max(pos1[1],pos2[1])
        max_z = max(pos1[2],pos2[2])
    else:
        min_x = -math.inf
        min_y = -math.inf
        min_z = -math.inf

        max_x = math.inf
        max_y = math.inf
        max_z = math.inf

    if isinstance(world, str):
        world = World(world)
    elif not isinstance(world, World):
        world = World(world.path)

    if not no_players:
        for player in world.iter_players(autosave=(not readonly)):
            for block_entity in player.recursive_iter_block_entities():
                yield block_entity.nbt, block_entity.pos, block_entity.get_legacy_debug()
            for entity in player.recursive_iter_entities():
                yield entity.nbt, entity.pos, entity.get_legacy_debug()

    if not players_only:
        for chunk in _new_chunk_iterator(world, min_x, min_y, min_z, max_x, max_y, max_z, autosave=(not readonly)):
            for block_entity in chunk.recursive_iter_block_entities(min_x, min_y, min_z, max_x, max_y, max_z):
                yield block_entity.nbt, block_entity.pos, block_entity.get_legacy_debug()
            for entity in chunk.recursive_iter_entities(min_x, min_y, min_z, max_x, max_y, max_z):
                yield entity.nbt, entity.pos, entity.get_legacy_debug()
