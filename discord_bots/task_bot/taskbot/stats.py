"""Statistics and time series, shared by text commands, charts and the API.

Every closed entry has a close time: the cutover estimated the ones the old bot never
recorded (README, "Imported history"). Closers are only known for closes made through
this version of the bot or recovered from the old feed channel; the rest are counted as
"unknown" rather than guessed.
"""

import bisect
import datetime
import unicodedata
from collections import Counter, defaultdict
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any, Optional

from .config import InstanceConfig
from .identity import identity_key
from .store import StatRow, TaskStore
from .vocab import COMPLEXITIES, DEFAULT_LABEL, DUPLICATE, FIXED, PRIORITIES, REJECTED, RESOLUTION_ORDER
_DEFAULT_NAMES = {FIXED: "fixed", REJECTED: "rejected", DUPLICATE: "duplicate"}

BUCKETS = ("day", "week", "month", "year")

# Stacking order (bottom first) for the backlog's groupings
COMPLEXITY_ORDER = ("unknown", "easy", "moderate", "hard")
assert set(COMPLEXITY_ORDER) == set(COMPLEXITIES)
PRIORITY_ORDER = ("N/A", "Zero", "Low", "Medium", "High", "Critical")
assert set(PRIORITY_ORDER) == set(PRIORITIES)
GROUP_ORDER: dict[str, Sequence[str]] = {"complexity": COMPLEXITY_ORDER, "priority": PRIORITY_ORDER}


def resolution_name(config: InstanceConfig, resolution: str) -> str:
    return config.resolution_names.get(resolution) or _DEFAULT_NAMES.get(resolution, resolution)


def group_value(row: StatRow, by: str) -> str:
    if by == "priority":
        return row.priority
    if by == "complexity":
        return row.complexity
    raise ValueError(f"unknown grouping {by!r}")


# ---------------------------------------------------------------------------
# Closers
# ---------------------------------------------------------------------------

@dataclass
class CloserStats:
    # closer identity_key -> resolution -> count, excluding authors closing their own entries
    by_closer: dict[str, Counter[str]] = field(default_factory=dict[str, Counter[str]])
    self_closes: int = 0          # authors closing their own entries
    unknown_closer: int = 0       # closed before the new bot, closer not recorded
    since: Optional[int] = None


def closer_stats(store: TaskStore, since: Optional[int] = None, until: Optional[int] = None) -> CloserStats:
    stats = CloserStats(since=since)
    for row in store.stat_rows():
        if row.status != "closed" or row.closed_at is None:
            continue
        if (since is not None and row.closed_at < since) or (until is not None and row.closed_at >= until):
            continue
        closer = identity_key(row.closed_by, row.closed_by_mc_uuid)
        if closer is None:
            stats.unknown_closer += 1
        elif closer == identity_key(row.author_id, row.author_mc_uuid):
            stats.self_closes += 1
        else:
            stats.by_closer.setdefault(closer, Counter())[str(row.resolution)] += 1
    return stats


def identity_name(key: str, names: Callable[[int], Optional[str]],
                  player_name: Callable[[str], Optional[str]]) -> str:
    """Display name for an identity_key ('discord:<id>' or 'mc:<uuid>')."""
    kind, _, ref = key.partition(":")
    if kind == "discord":
        return names(int(ref)) or ref
    return f"{player_name(ref) or ref[:8]} (in-game)"


def closer_rows(stats: CloserStats) -> list[tuple[str, Counter[str]]]:
    return sorted(stats.by_closer.items(), key=lambda kv: (-sum(kv[1].values()), kv[0]))


def _char_width(c: str) -> int:
    """Columns a character takes in a monospace font: 0 for combining marks and other
    invisible characters, 2 for wide ones (CJK, most emoji)."""
    if unicodedata.category(c) in ("Mn", "Me", "Cf"):
        return 0
    return 2 if unicodedata.east_asian_width(c) in ("W", "F") else 1


def _pad(text: str, width: int) -> str:
    """Cut or pad text to `width` columns, so names with emoji line up."""
    out, used = "", 0
    for c in text:
        w = _char_width(c)
        if used + w > width:
            break
        out, used = out + c, used + w
    return out + " " * (width - used)


def format_closer_stats(stats: CloserStats, config: InstanceConfig,
                        names: Callable[[int], Optional[str]], days: Optional[int],
                        player_name: Callable[[str], Optional[str]] = lambda _uuid: None,
                        minimum: int = 1, limit: int = 1900) -> list[str]:
    """The cstats reply as messages of at most `limit` characters, each table part in its
    own code block. Closers with fewer than `minimum` closes are only counted."""
    period = f"in the last {days} days" if days else "overall"
    header = f"Who has closed the most {config.descriptor_plural} {period}:"
    cols = [resolution_name(config, r).capitalize() for r in RESOLUTION_ORDER]
    title = f"{'' : <22}" + "".join(f"{c : <11}" for c in cols) + "Total"
    lines: list[str] = []
    hidden = 0
    for closer, counts in closer_rows(stats):
        if sum(counts.values()) < minimum:
            hidden += 1
            continue
        name = _pad(identity_name(closer, names, player_name), 20)
        lines.append(f"{name}  " + "".join(f"{counts.get(r, 0) : <11}" for r in RESOLUTION_ORDER)
                     + str(sum(counts.values())))
    if not lines and not hidden:
        lines.append("(no closes recorded yet)")
    notes: list[str] = []
    if hidden:
        notes.append(f"{hidden} more with fewer than {minimum} closes each")
    if stats.self_closes:
        notes.append(f"{stats.self_closes} closed by their own authors, not counted above")
    if stats.unknown_closer and not days:
        notes.append(f"{stats.unknown_closer} closed with no recorded closer")

    messages: list[str] = []
    block = [title]
    first = header + "\n"
    fence = len("```\n") + len("\n```")
    for line in lines:
        if len(first) + fence + len("\n".join(block + [line])) > limit:
            messages.append(first + "```\n" + "\n".join(block) + "\n```")
            block, first = [], ""
        block.append(line)
    messages.append(first + "```\n" + "\n".join(block) + "\n```")
    if notes:
        tail = "\n".join(notes)
        if len(messages[-1]) + 1 + len(tail) <= limit:
            messages[-1] += "\n" + tail
        else:
            messages.append(tail)
    return messages


# ---------------------------------------------------------------------------
# Time series
# ---------------------------------------------------------------------------

def bucket_start(ts: int, bucket: str) -> int:
    d = datetime.datetime.fromtimestamp(ts, datetime.timezone.utc)
    if bucket == "day":
        d = d.replace(hour=0, minute=0, second=0, microsecond=0)
    elif bucket == "week":
        d = (d - datetime.timedelta(days=d.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    elif bucket == "month":
        d = d.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif bucket == "year":
        d = d.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        raise ValueError(f"unknown bucket {bucket!r}")
    return int(d.timestamp())


def next_bucket(ts: int, bucket: str) -> int:
    d = datetime.datetime.fromtimestamp(ts, datetime.timezone.utc)
    if bucket == "day":
        d += datetime.timedelta(days=1)
    elif bucket == "week":
        d += datetime.timedelta(days=7)
    elif bucket == "month":
        d = d.replace(year=d.year + (d.month // 12), month=d.month % 12 + 1)
    else:
        d = d.replace(year=d.year + 1)
    return int(d.timestamp())


def bucket_range(start: int, end: int, bucket: str) -> list[int]:
    out: list[int] = []
    t = bucket_start(start, bucket)
    while t <= end:
        out.append(t)
        t = next_bucket(t, bucket)
    return out


@dataclass
class Series:
    """A set of named series over shared time buckets."""
    name: str
    bucket: str
    times: list[int]
    series: dict[str, list[float]]
    notes: list[str] = field(default_factory=list[str])

    def to_json(self) -> dict[str, Any]:
        return {"name": self.name, "bucket": self.bucket, "times": self.times,
                "series": self.series, "notes": self.notes}


def _ordered(groups: set[str], by: str) -> list[str]:
    """Known values in their fixed order, then any others."""
    order = list(GROUP_ORDER[by])
    return [g for g in order if g in groups] + sorted(groups - set(order))


def intake_series(rows: Sequence[StatRow], *, bucket: str, since: Optional[int], until: int,
                  labels: dict[int, list[str]], top: int = 5) -> Series:
    """New entries per bucket, split by label: the top few, the rest as "other". Each
    entry counts once, under its first label other than the default (misc), so that
    misc only counts entries with nothing more specific."""
    def label_of(r: StatRow) -> str:
        return next((x for x in labels.get(r.id, ()) if x != DEFAULT_LABEL), DEFAULT_LABEL)

    rows = [r for r in rows if r.created_at is not None
            and (since is None or r.created_at >= since) and r.created_at < until]
    if not rows:
        return Series("intake", bucket, [], {}, ["no entries in range"])
    start = since if since is not None else min(int(r.created_at or 0) for r in rows)
    times = bucket_range(start, until - 1, bucket)
    index = {t: i for i, t in enumerate(times)}
    order = [k for k, _ in Counter(label_of(r) for r in rows).most_common(top)]
    keep = set(order)
    series: dict[str, list[float]] = defaultdict(lambda: [0.0] * len(times))
    for r in rows:
        g = label_of(r)
        g = g if g in keep else "other"
        i = index.get(bucket_start(int(r.created_at or 0), bucket))
        if i is not None:
            series[g][i] += 1
    order += ["other"] if "other" in series else []
    return Series("intake", bucket, times, {g: series[g] for g in order if g in series})


def closes_series(rows: Sequence[StatRow], *, bucket: str, since: Optional[int], until: int) -> Series:
    """Closes per bucket by resolution."""
    rows = [r for r in rows if r.status == "closed" and r.closed_at is not None
            and (since is None or r.closed_at >= since) and r.closed_at < until]
    if not rows:
        return Series("closes", bucket, [], {}, ["no closes in range"])
    start = since if since is not None else min(int(r.closed_at or 0) for r in rows)
    times = bucket_range(start, until - 1, bucket)
    index = {t: i for i, t in enumerate(times)}
    series: dict[str, list[float]] = {g: [0.0] * len(times) for g in RESOLUTION_ORDER}
    for r in rows:
        i = index.get(bucket_start(int(r.closed_at or 0), bucket))
        if i is not None and r.resolution in series:
            series[str(r.resolution)][i] += 1
    return Series("closes", bucket, times, {g: v for g, v in series.items() if any(v)})


def backlog_series(rows: Sequence[StatRow], *, bucket: str, since: Optional[int], until: int,
                   by: str) -> Series:
    """Open entries at the end of each bucket (the last point is now), split by priority
    or complexity. An entry counts as open from its creation until its close; priority and
    complexity are what it has now, not what it had then."""
    rows = [r for r in rows if r.created_at is not None and (r.status == "open" or r.closed_at is not None)]
    if not rows:
        return Series("backlog", bucket, [], {}, ["no entries"])
    start = since if since is not None else min(int(r.created_at or 0) for r in rows)
    ends = [min(next_bucket(t, bucket), until) for t in bucket_range(start, until - 1, bucket)]

    def group_of(r: StatRow) -> str:
        return group_value(r, by)

    order = _ordered({group_of(r) for r in rows}, by)
    created: dict[str, list[int]] = {g: [] for g in order}
    closed: dict[str, list[int]] = {g: [] for g in order}
    for r in rows:
        created[group_of(r)].append(int(r.created_at or 0))
        if r.status == "closed":
            closed[group_of(r)].append(int(r.closed_at or 0))
    series: dict[str, list[float]] = {}
    for g in order:
        c, d = sorted(created[g]), sorted(closed[g])
        series[g] = [float(bisect.bisect_left(c, end) - bisect.bisect_left(d, end)) for end in ends]
    return Series("backlog", bucket, ends, series)


def age_histogram(rows: Sequence[StatRow], now: int) -> dict[str, int]:
    """Open entries by age."""
    edges = [(30, "< 1 month"), (90, "1-3 months"), (180, "3-6 months"), (365, "6-12 months"),
             (730, "1-2 years"), (1095, "2-3 years"), (1825, "3-5 years")]
    out: dict[str, int] = {label: 0 for _, label in edges}
    out["5+ years"] = 0
    out["unknown"] = 0
    for r in rows:
        if r.status != "open":
            continue
        if r.created_at is None:
            out["unknown"] += 1
            continue
        days = (now - r.created_at) / 86400
        for limit, label in edges:
            if days < limit:
                out[label] += 1
                break
        else:
            out["5+ years"] += 1
    if not out["unknown"]:
        del out["unknown"]
    return out
