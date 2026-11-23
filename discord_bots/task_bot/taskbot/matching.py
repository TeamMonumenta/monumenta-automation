"""Prefix matching and text splitting, behaving exactly as in the original bot.

Users have typed abbreviated commands, labels and priorities for years
(`~bug f 123`, `~bug search quest hi`), so these functions keep the old
behavior to the letter, including its order sensitivity.
"""

from collections.abc import Iterable
from typing import Optional


def get_list_match(item: str, lst: Iterable[str]) -> Optional[str]:
    """Case-insensitive prefix match of item against lst.

    Returns the exact match if one is reached first, the single prefix match if
    there is exactly one, and None when nothing matches or a second prefix match
    is found before an exact one. Order matters: with ['fixa', 'fixb', 'fix'],
    'fix' returns None because the ambiguity is found first.
    """
    tmpitem = item.lower()

    match: Optional[str] = None
    for x in lst:
        if x.lower().startswith(tmpitem):
            if x.lower() == tmpitem:
                return x
            if match is None:
                match = x
            else:
                return None
    return match


MAX_CHUNK = 1950


def split_string(text: str, n: int = MAX_CHUNK) -> list[str]:
    """Split text into chunks of at most n characters, on line boundaries where possible."""
    result: list[str] = []
    cur: Optional[str] = None
    for line in text.splitlines():
        while True:
            if cur is None and len(line) <= n:
                cur = line
                break
            if cur is None:
                # One very long line: hard split it.
                result.append(line[:n])
                line = line[n:]
                continue
            if len(cur) + len(line) < n:
                cur = cur + "\n" + line
                break
            result.append(cur)
            cur = None

    if cur is not None:
        result.append(cur)

    return result
