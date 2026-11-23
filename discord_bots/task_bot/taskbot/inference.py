"""Heuristics to recover what the legacy JSON never recorded.

Two things are recovered when importing: what kind of close each closed entry
was (the old bot stored only free text), and roughly when each entry was
created (from Discord snowflakes). Nothing in the database marks them as guesses;
README.md ("Cutover") says how good they are.
"""

import re
from collections.abc import Sequence
from typing import Optional

from .vocab import DUPLICATE, FIXED, REJECTED

DISCORD_EPOCH_MS = 1420070400000

# Not a resolution: what classification says of an entry its users redacted by hand
REDACTED = "redacted"


def snowflake_time(snowflake: int) -> float:
    """Epoch seconds at which a Discord snowflake id was generated."""
    return ((snowflake >> 22) + DISCORD_EPOCH_MS) / 1000.0


def time_to_snowflake(epoch_seconds: float) -> int:
    return (int(epoch_seconds * 1000) - DISCORD_EPOCH_MS) << 22


# ---------------------------------------------------------------------------
# Close reason classification
# ---------------------------------------------------------------------------

_DUPLICATE_RE = re.compile(
    r"^\s*(dupe?|duplicate|merged|merging|combined|combining|double posted|repeat|"
    r"already reported|same (issue )?as)\b"
    r"|\b((dupe?|dub|duplicate) of|merged (into|with)|combined (into|with)|tracked by|"
    r"same issue as|same as)\b",
    re.IGNORECASE,
)
# The original's number: after "into" (`combined 6048 & 6007 into 6114`), else after the
# duplicate phrase, with a few words between at most ("dupe suggestion of #145", "same issue
# as described in #9092"). Never part of a version number ("1.20"), and not "bug 123", which
# in the suggestion tracker is the other tracker's.
_NUM = r"#?(\d{1,6})(?!\d|\.\d)"
_WORDS = r"(?:[\s:(,/.+-]+[a-z']+){0,%d}[\s:(,/.+-]+"
_TARGET_RES = [
    re.compile(r"\binto" + _WORDS % 3 + _NUM, re.IGNORECASE),
    re.compile(r"\b(?:dupe?|dub|duplicate|merged|merging|combined|combining|tracked|repeat|reported|same(?: issue)?)"
               + _WORDS % 6 + _NUM, re.IGNORECASE),
]
_OTHER_TRACKER_RE = re.compile(r"\b(bug|sug|suggestion)s?[\s:,-]*#?$", re.IGNORECASE)


def duplicate_target(reason: str) -> Optional[int]:
    """The number of the original a duplicate's close reason names, if any."""
    for target_re in _TARGET_RES:
        m = target_re.search(reason)
        if m:
            if _OTHER_TRACKER_RE.search(reason[:m.start(1)]):
                return None
            return int(m.group(1))
    return None


_FIXED_RE = re.compile(
    r"\b(fixed|hotfix|hotfixed|implemented|added|done|resolved|reworked|"
    r"accomplished|addressed|solved)\b",
    re.IGNORECASE,
)
# Phrases that turn a "fixed"-sounding reason into a refusal.
_NEGATION_RE = re.compile(
    r"\b(not|no|never|won'?t|unlikely|can'?t|cannot|isn'?t|wasn'?t|wouldn'?t|"
    r"shouldn'?t|nope|nah|unfeasible|difficult|if you want)\b|n't\b",
    re.IGNORECASE,
)
# Fixed-sounding phrases that stay fixed even with a negation word nearby.
_FIXED_DESPITE_NEGATION_RE = re.compile(
    r"not really a bug but fixed|no longer (an issue|a bug|happens|occurs)|"
    r"should no longer be an issue|was fixed but not closed",
    re.IGNORECASE,
)


def classify_close_reason(reason: str, description: str = "") -> tuple[str, Optional[int]]:
    """Guess (resolution, duplicate_of) for a legacy close reason.

    The old `fix` command defaulted the reason to "Fixed" and `reject` required
    free text, so most fixes are recognizable. Anything that doesn't read as a
    fix or a duplicate counts as rejected.
    """
    text = reason.strip()
    if description.strip().lower() in ("redacted", "[redacted]"):
        return REDACTED, None

    if _DUPLICATE_RE.search(text):
        # "dupe of bug 123" in the suggestion tracker points at the other tracker, and
        # names no number right after the phrase, so it gets no link
        return DUPLICATE, duplicate_target(text)

    if _FIXED_DESPITE_NEGATION_RE.search(text):
        return FIXED, None
    if _FIXED_RE.search(text) and not _NEGATION_RE.search(text):
        return FIXED, None

    return REJECTED, None


# ---------------------------------------------------------------------------
# Creation time estimation
# ---------------------------------------------------------------------------

def estimate_creation_times(
    ids: Sequence[int], upper_bounds: Sequence[Optional[float]]
) -> list[Optional[float]]:
    """Estimate a non-decreasing creation time for each entry id.

    `ids` must be sorted ascending; `upper_bounds[i]` is the earliest timestamp
    known to be at or after entry ids[i] was created (its tracking message or an
    image attachment), or None.

    Entry numbers are handed out in time order, so creation time never
    decreases with id. A bound on a later entry therefore also bounds every
    earlier one, and the tightest bound for entry i is the minimum over all
    bounds at or after it (a suffix minimum). Entries whose own bound equals
    that minimum are taken as anchors, and entries between two anchors are
    interpolated linearly by id. Entries after the last bound take the time of the
    entry before them (entries are filed nearly every day, so it is close); only
    with no bounds at all is the result None.
    """
    n = len(ids)
    suffix: list[Optional[float]] = [None] * n
    best: Optional[float] = None
    for i in range(n - 1, -1, -1):
        b = upper_bounds[i]
        if b is not None and (best is None or b < best):
            best = b
        suffix[i] = best

    anchors = [i for i in range(n)
               if upper_bounds[i] is not None and upper_bounds[i] == suffix[i]]

    result: list[Optional[float]] = list(suffix)
    for a, b in zip(anchors, anchors[1:]):
        ta = suffix[a]
        tb = suffix[b]
        assert ta is not None and tb is not None
        span = ids[b] - ids[a]
        for i in range(a + 1, b):
            frac = (ids[i] - ids[a]) / span
            result[i] = ta + (tb - ta) * frac
    # Before the first anchor there is nothing earlier to interpolate from, so the
    # suffix minimum (the first anchor's time) stands. After the last bound there is
    # nothing later, so each entry takes the previous one's time.
    for i in range(1, n):
        if result[i] is None:
            result[i] = result[i - 1]
    return result
