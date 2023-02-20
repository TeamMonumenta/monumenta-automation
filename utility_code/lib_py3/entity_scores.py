"""Helper methods to get/set scores stored directly on entities."""

import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../quarry"))
from quarry.types import nbt


def get_entity_scores(entity):
    """Returns a map of {objective:value} stored on the entity, such as {"Foo": 3, "Bar": 7}."""
    if not entity.nbt.has_path('BukkitValues."monumenta:entity_scores"'):
        return {}

    return json.loads(entity.nbt.at_path('BukkitValues."monumenta:entity_scores"').value)


def set_entity_scores(entity, score_map):
    """Stores scores to an entity.

    Scores must be in the format {"objective": value}, such as {"Foo": 3, "Bar": 7}
    All scores may be deleted by passing an empty map.
    """
    if len(score_map) == 0:
        if entity.nbt.has_path('BukkitValues."monumenta:entity_scores"'):
            del entity.nbt.at_path('BukkitValues').value["monumenta:entity_scores"]
            if len(entity.nbt.at_path('BukkitValues').value) == 0:
                del entity.nbt.value['BukkitValues']
        return

    json_str = json.dumps(score_map, ensure_ascii=False, indent=None, separators=(',', ':'))
    if not entity.nbt.has_path('BukkitValues'):
        entity.nbt.value['BukkitValues'] = nbt.TagCompound({})
    entity.nbt.at_path('BukkitValues').value["monumenta:entity_scores"] = nbt.TagString(json_str)
