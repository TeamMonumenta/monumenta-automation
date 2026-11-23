"""The fixed priorities and complexities, the same for every instance.

Labels differ between instances and change with `addlabel` / `dellabel`, so they
live in the database. Priorities and complexities have never changed, so they
are constants here. Order matters: abbreviations are matched in this order, and
`stats` prints rows in it.
"""

PRIORITIES = ["N/A", "Critical", "High", "Medium", "Low", "Zero"]

# name -> the emoji shown after an entry's header
COMPLEXITIES = {
    "easy": ":green_circle:",
    "moderate": ":orange_circle:",
    "hard": ":red_circle:",
    "unknown": ":white_circle:",
}

# How a closed entry ended (`fix`, `reject`, `dupe`), in the order statistics show them
FIXED = "fixed"
REJECTED = "rejected"
DUPLICATE = "duplicate"
RESOLUTION_ORDER = (FIXED, REJECTED, DUPLICATE)

DEFAULT_PRIORITY = "N/A"
DEFAULT_COMPLEXITY = "unknown"
# Every instance has this label; entries filed without a label get it
DEFAULT_LABEL = "misc"

# The old bot's sort order for priority x complexity. Unknown combinations sort
# after all of these, in id order.
PRIORITY_RANK: dict[tuple[str, str], int] = {
    ("Critical", "easy"): 1, ("Critical", "moderate"): 2, ("Critical", "hard"): 3,
    ("Critical", "unknown"): 4, ("High", "easy"): 5, ("High", "moderate"): 6,
    ("Medium", "easy"): 7, ("High", "hard"): 8, ("High", "unknown"): 9,
    ("Medium", "moderate"): 10, ("Low", "easy"): 11, ("N/A", "easy"): 12,
    ("Medium", "hard"): 13, ("Medium", "unknown"): 14, ("Low", "moderate"): 15,
    ("N/A", "moderate"): 16, ("Zero", "easy"): 17, ("N/A", "unknown"): 18,
    ("N/A", "hard"): 19, ("Low", "hard"): 20, ("Low", "unknown"): 21,
    ("Zero", "moderate"): 22, ("Zero", "hard"): 23, ("Zero", "unknown"): 24,
}
UNKNOWN_RANK = 99


def priority_rank(priority: str, complexity: str) -> int:
    return PRIORITY_RANK.get((priority, complexity), UNKNOWN_RANK)
