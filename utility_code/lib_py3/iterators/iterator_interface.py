"""Iterator abstraction layer to aid upgrades."""

import math

from minecraft.chunk_format.block_entity import BlockEntity
from minecraft.chunk_format.entity import Entity
from minecraft.world import World

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

    for chunk in world.iter_chunks(min_x, min_y, min_z, max_x, max_y, max_z, autosave=(not readonly)):
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
        for chunk in world.iter_chunks(min_x, min_y, min_z, max_x, max_y, max_z, autosave=(not readonly)):
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
            for obj in player.recursive_iter_all_types():
                if isinstance(obj, (BlockEntity, Entity)):
                    yield obj.nbt, obj.pos, obj.get_legacy_debug()

    if not players_only:
        for chunk in world.iter_chunks(min_x, min_y, min_z, max_x, max_y, max_z, autosave=(not readonly)):
            for obj in chunk.recursive_iter_all_types():
                if isinstance(obj, (BlockEntity, Entity)):
                    yield obj.nbt, obj.pos, obj.get_legacy_debug()
