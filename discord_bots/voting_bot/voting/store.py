# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Byron Marohn
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Optional, cast

import yaml

logger = logging.getLogger(__name__)


def _str_list() -> list[str]:
    return []


@dataclass
class VoteData:
    message_id: str
    channel_id: str
    creator_id: str
    created_at: int
    message: str
    show_counts: bool
    concluded: bool
    concluded_by: Optional[str]
    concluded_at: Optional[int]
    thumbsup: list[str] = field(default_factory=_str_list)
    thumbsdown: list[str] = field(default_factory=_str_list)


class VoteStore:
    def __init__(self, data_dir: str) -> None:
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

    def _path(self, message_id: str) -> str:
        return os.path.join(self.data_dir, f"{message_id}.yml")

    def load(self, message_id: str) -> Optional[VoteData]:
        path = self._path(message_id)
        if not os.path.exists(path):
            return None
        try:
            with open(path, encoding='utf-8') as f:
                raw = yaml.safe_load(f)
            if not isinstance(raw, dict):
                raise ValueError(f"Expected a YAML mapping, got {type(raw).__name__}")
            data: dict[str, Any] = cast(dict[str, Any], raw)
            return VoteData(
                message_id=str(data['message_id']),
                channel_id=str(data['channel_id']),
                creator_id=str(data['creator_id']),
                created_at=int(data['created_at']),
                message=str(data['message']),
                show_counts=bool(data['show_counts']),
                concluded=bool(data.get('concluded', False)),
                concluded_by=str(data['concluded_by']) if data.get('concluded_by') else None,
                concluded_at=int(data['concluded_at']) if data.get('concluded_at') else None,
                thumbsup=[str(x) for x in cast(list[Any], data.get('thumbsup') or [])],
                thumbsdown=[str(x) for x in cast(list[Any], data.get('thumbsdown') or [])],
            )
        except (yaml.YAMLError, KeyError, TypeError, ValueError):
            logger.exception("Corrupted vote file, skipping: %s", path)
            return None

    def save(self, vote: VoteData) -> None:
        path = self._path(vote.message_id)
        data: dict[str, Any] = {
            'message_id': vote.message_id,
            'channel_id': vote.channel_id,
            'creator_id': vote.creator_id,
            'created_at': vote.created_at,
            'message': vote.message,
            'show_counts': vote.show_counts,
            'concluded': vote.concluded,
            'concluded_by': vote.concluded_by,
            'concluded_at': vote.concluded_at,
            'thumbsup': vote.thumbsup,
            'thumbsdown': vote.thumbsdown,
        }
        with open(path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True)

    def list_active(self) -> list[VoteData]:
        result: list[VoteData] = []
        if not os.path.isdir(self.data_dir):
            return result
        for fname in os.listdir(self.data_dir):
            if not fname.endswith('.yml'):
                continue
            vote = self.load(fname[:-4])
            if vote and not vote.concluded:
                result.append(vote)
        return result
