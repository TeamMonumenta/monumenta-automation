"""Recognizing a close reason that says the entry is a duplicate ("dupe of 2360").

`dupe` is newer than the habit of rejecting with "dupe of #123", so `fix` and `reject`
read the reason and close as a duplicate when it says so. The patterns were tuned on the
old feed channels' closes.
"""

import re
from typing import Optional

_DUPLICATE_RE = re.compile(
    r"^\s*(dupe?|duplicate|merged|merging|combined|combining|double posted|repeat|"
    r"already reported|same (issue )?as)\b"
    r"|\b((dupe?|dub|duplicate) of|merged (into|with)|combined (into|with)|tracked by|"
    r"same issue as)\b"
    # Mid-sentence, a bare "same as" is usually a comparison ("works the same as vanilla"),
    # so it counts only when an entry number follows: right after it ("same as 2360"), or a
    # few words on with a # ("same as issue #55")
    r"|\bsame as(?:[\s:]*#?\d{1,6}\b(?!\.\d)|(?:[\s:(,/.+-]+[a-z']+){0,3}[\s:(,/.+-]+#\d)",
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


def says_duplicate(reason: str) -> bool:
    return _DUPLICATE_RE.search(reason.strip()) is not None


def duplicate_target(reason: str) -> Optional[int]:
    """The number of the original a duplicate's close reason names, if any."""
    for target_re in _TARGET_RES:
        m = target_re.search(reason)
        if m:
            if _OTHER_TRACKER_RE.search(reason[:m.start(1)]):
                return None
            return int(m.group(1))
    return None
