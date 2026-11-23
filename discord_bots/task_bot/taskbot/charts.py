# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownVariableType=false
"""Server-side chart rendering (matplotlib, Agg backend, no pyplot).

The same renderer serves the `chart` text command and GET /api/charts/<name>.png,
so a chart looks identical wherever it is requested. Data is gathered on the
caller's thread (it reads the database); only the drawing runs in an executor,
behind a lock, since matplotlib is not thread-safe.
"""

import asyncio
import datetime
import io
import re
import threading
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any, Optional

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.dates import AutoDateLocator, ConciseDateFormatter
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

from .config import InstanceConfig
from .stats import (
    BUCKETS, RESOLUTION_ORDER, Series, age_histogram, backlog_series, bucket_start, closer_rows,
    closer_stats, closes_series, identity_name, intake_series, resolution_name,
)
from .store import TaskStore


class ChartError(Exception):
    pass


# Categorical slots in fixed order (validated reference palette, dark steps)
_CATEGORICAL = ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#0ca30c", "#9085e9", "#e66767"]
_SURFACE, _TEXT, _MUTED, _GRID, _OTHER = "#1a1a19", "#f0efec", "#c3c2b7", "#3a3a37", "#77766f"
# Fixed colors, so a resolution, complexity or priority looks the same on every chart. Complexity
# follows the emoji on tracking messages.
_GROUP_COLORS = {
    "resolution": {"fixed": "#3987e5", "rejected": "#d95926", "duplicate": "#199e70"},
    "complexity": {"unknown": _OTHER, "easy": "#199e70", "moderate": "#c98500", "hard": "#e66767"},
    "priority": {"N/A": _OTHER, "Critical": "#d55181", "High": "#d95926", "Medium": "#c98500",
                 "Low": "#3987e5", "Zero": "#9085e9"},
}

_PERIOD_RE = re.compile(r"^(\d+)([dwmy])$")
_PERIOD_DAYS = {"d": 1, "w": 7, "m": 30, "y": 365}
_GROUPINGS = ("priority", "complexity")
MAX_PERIOD_DAYS = 100 * 365
MAX_BUCKETS = 1000      # bars or points on one chart; more is unreadable, and slow to draw
_BUCKET_DAYS = {"day": 1, "week": 7, "month": 30, "year": 365}


@dataclass
class ChartOptions:
    bucket: Optional[str] = None      # day | week | month | year
    period_days: Optional[int] = None  # None: chart default; 0: all time
    by: Optional[str] = None          # grouping; which ones a chart takes is in its spec
    label: Optional[str] = None       # only entries with this label (backlog)
    top: Optional[int] = None


@dataclass
class ChartSpec:
    name: str
    summary: str
    default_bucket: Optional[str]
    default_period_days: int         # 0 = all time
    by: tuple[str, ...] = ()         # groupings it takes, the default first


CHARTS: dict[str, ChartSpec] = {
    "backlog": ChartSpec("backlog", "open {plural} over time, stacked by complexity (or priority); "
                         "a label name limits it to that label",
                         "month", 0, ("complexity", "priority")),
    "intake": ChartSpec("intake", "new {plural} per month by label", "month", 0),
    "closes": ChartSpec("closes", "closed {plural} per month by resolution", "month", 0),
    "closers": ChartSpec("closers", "who closed the most {plural} by resolution (default last 90 days, top 15)",
                         None, 90),
    "age": ChartSpec("age", "open {plural} by age", None, 0),
    "labels": ChartSpec("labels", "open {plural} by label", None, 0),
}


def parse_options(tokens: Sequence[str], labels: Sequence[str] = ()) -> ChartOptions:
    """Options as typed after the chart name: `month`, `2y`/`90d`/`all`, `priority`, `10`,
    or one of `labels` (exact name)."""
    known_labels = {x.lower(): x for x in labels}
    opts = ChartOptions()
    for raw in tokens:
        tok = raw.strip().lower()
        if not tok:
            continue
        if tok in BUCKETS or tok.rstrip("s") in BUCKETS or tok in ("daily", "weekly", "monthly", "yearly"):
            opts.bucket = {"daily": "day", "weekly": "week", "monthly": "month",
                           "yearly": "year"}.get(tok, tok.rstrip("s"))
        elif tok == "all":
            opts.period_days = 0
        elif m := _PERIOD_RE.match(tok):
            opts.period_days = int(m.group(1)) * _PERIOD_DAYS[m.group(2)]
            if opts.period_days > MAX_PERIOD_DAYS:
                raise ChartError("A period can be at most 100 years; `all` covers everything")
        elif tok in _GROUPINGS or (tok.endswith("s") and tok[:-1] in _GROUPINGS):
            opts.by = tok if tok in _GROUPINGS else tok[:-1]
        elif tok in known_labels:
            opts.label = known_labels[tok]
        elif tok.isdigit():
            opts.top = max(1, min(50, int(tok)))
        else:
            raise ChartError(f"Unknown chart option {raw!r}. Options: a period like 90d, 12w or 2y "
                             "(or all); day, week, month or year; priority or complexity, or a "
                             "label name, for the backlog; a number for the top N closers")
    return opts


class ChartRenderer:
    def __init__(self, store: TaskStore, config: InstanceConfig, clock: Callable[[], int]):
        self.store = store
        self.config = config
        self.clock = clock
        self._lock = threading.Lock()
        # Set by the bot so charts can show user names
        self.name_lookup: Optional[Callable[[int], Optional[str]]] = None

    def names(self) -> list[str]:
        return list(CHARTS)

    def describe_all(self, prefix: str) -> str:
        lines = [f"Available charts (`{prefix} chart <name> [options]`):"]
        for spec in CHARTS.values():
            lines.append(f"`{spec.name}`: {spec.summary.format(plural=self.config.descriptor_plural)}")
        lines.append("Options: a period like `90d`, `12w`, `2y` or `all`; `week`, `month` or `year` "
                     "buckets; for the backlog, `priority` to stack by priority and a label name to "
                     "limit it to that label; a number for the top N closers.")
        return "\n".join(lines)

    def parse_options(self, tokens: Sequence[str]) -> ChartOptions:
        return parse_options(tokens, self.store.labels(include_inactive=True))

    # ------------------------------------------------------------------
    # Data (also served as JSON by the API)
    # ------------------------------------------------------------------

    def data(self, name: str, opts: ChartOptions) -> dict[str, Any]:
        spec = CHARTS.get(name)
        if spec is None:
            raise ChartError(f"Unknown chart {name!r}")
        if opts.by is not None and opts.by not in spec.by:
            raise ChartError(f"The {name} chart can't be split by {opts.by}"
                             + (f"; it takes {', '.join(spec.by)}" if spec.by else ""))
        if opts.label is not None and name != "backlog":
            raise ChartError("Only the backlog chart can be limited to a label")
        by = opts.by or (spec.by[0] if spec.by else None)
        now = self.clock()
        period = spec.default_period_days if opts.period_days is None else opts.period_days
        since = now - period * 86400 if period else None
        bucket = opts.bucket or spec.default_bucket or "month"
        plural = self.config.descriptor_plural
        title_period = f"last {_fmt_days(period)}" if period else "all time"
        rows = self.store.stat_rows()

        if name in ("backlog", "intake", "closes"):
            series: Series
            group = by
            first = since if since is not None else min(
                (r.created_at for r in rows if r.created_at), default=now)
            if (now - first) / 86400 / _BUCKET_DAYS[bucket] > MAX_BUCKETS:
                raise ChartError(f"That would be more than {MAX_BUCKETS} {bucket}s; "
                                 "pick a bigger bucket or a shorter period")
            if since is not None:
                # Whole buckets only: a first bucket cut part way through looks like a dip
                since = bucket_start(since, bucket)
            if name == "backlog":
                assert by is not None
                labelled = ""
                if opts.label is not None:
                    with_label = set(self.store.entries_with_label(opts.label))
                    rows = [r for r in rows if r.id in with_label]
                    labelled = f" labeled {opts.label}"
                series = backlog_series(rows, bucket=bucket, since=since, until=now, by=by)
                title = f"Open {plural}{labelled} by {by} ({title_period})"
            elif name == "intake":
                series = intake_series(rows, bucket=bucket, since=since, until=now,
                                       labels=self.store.labels_by_entry())
                title = f"New {plural} per {bucket} by label ({title_period})"
            else:
                group = "resolution"
                series = closes_series(rows, bucket=bucket, since=since, until=now)
                title = f"Closed {plural} per {bucket} by resolution ({title_period})"
            colors = self._colors(group, list(series.series))
            if group == "resolution":
                series.series = {resolution_name(self.config, k): v for k, v in series.series.items()}
                colors = {resolution_name(self.config, k): v for k, v in colors.items()}
            out = series.to_json()
            out.update(kind="timeseries", title=title, colors=colors,
                       stacked="area" if name == "backlog" else "bars")
            return out

        if name == "closers":
            stats = closer_stats(self.store, since=since)
            rows_ = closer_rows(stats)[:opts.top or 15]
            names = self._names()
            groups = [g for g in RESOLUTION_ORDER if any(cnt.get(g) for _, cnt in rows_)]
            # Closes with no recorded closer (old ones) are left out without comment
            notes = [f"{stats.self_closes} closed by their own authors are not counted"] if stats.self_closes else []
            return {
                "kind": "hbar_stacked", "name": name,
                "title": f"Who closed the most {plural} ({title_period})",
                "categories": [identity_name(c, names, self.store.player_name) for c, _ in rows_],
                "series": {resolution_name(self.config, g): [float(cnt.get(g, 0)) for _, cnt in rows_]
                           for g in groups},
                "colors": {resolution_name(self.config, g): c for g, c in self._colors("resolution", groups).items()},
                "notes": notes,
            }

        if name == "age":
            hist = age_histogram(rows, now)
            return {"kind": "bar", "name": name, "title": f"Open {plural} by age",
                    "categories": list(hist), "values": [float(v) for v in hist.values()], "notes": []}

        counts = self.store.open_counts_by_label()
        return {"kind": "hbar", "name": name, "title": f"Open {plural} by label",
                "categories": list(counts), "values": [float(v) for v in counts.values()],
                "notes": ["an entry with several labels counts once for each"]}

    @staticmethod
    def _colors(by: Optional[str], keys: list[str]) -> dict[str, str]:
        fixed = _GROUP_COLORS.get(by or "", {})
        out: dict[str, str] = {}
        slot = 0
        for key in keys:
            if key in fixed:
                out[key] = fixed[key]
            elif key == "other":
                out[key] = _OTHER
            else:
                out[key] = _CATEGORICAL[slot % len(_CATEGORICAL)]
                slot += 1
        return out

    def _names(self) -> Callable[[int], Optional[str]]:
        return self.name_lookup if self.name_lookup is not None else (lambda _uid: None)

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def render(self, name: str, opts: ChartOptions) -> bytes:
        return self.draw(self.data(name, opts))

    async def render_async(self, name: str, opts: ChartOptions) -> bytes:
        data = self.data(name, opts)
        return await asyncio.get_running_loop().run_in_executor(None, self.draw, data)

    def draw(self, data: dict[str, Any]) -> bytes:
        with self._lock:
            return _draw(data)


def _fmt_days(days: int) -> str:
    if days % 365 == 0:
        n = days // 365
        return f"{n} year{'s' if n != 1 else ''}"
    if days % 30 == 0 and days >= 60:
        return f"{days // 30} months"
    if days % 7 == 0 and days >= 14:
        return f"{days // 7} weeks"
    return f"{days} days"


def _draw(data: dict[str, Any]) -> bytes:
    fig = Figure(figsize=(10, 5.2), dpi=110, facecolor=_SURFACE)
    FigureCanvasAgg(fig)
    ax = fig.add_subplot(1, 1, 1)
    ax.set_facecolor(_SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(_GRID)
    ax.tick_params(colors=_MUTED, labelsize=9)
    ax.set_title(data.get("title", ""), color=_TEXT, loc="left", fontsize=13, pad=12)
    given: dict[str, str] = data.get("colors") or {}

    def color_for(i: int, key: str) -> str:
        return given.get(key) or (_OTHER if key == "other" else _CATEGORICAL[i % len(_CATEGORICAL)])

    kind = data["kind"]
    if kind == "timeseries":
        _draw_timeseries(ax, data, color_for)
    elif kind == "hbar_stacked":
        cats: list[str] = data["categories"]
        left = [0.0] * len(cats)
        ypos = list(range(len(cats)))[::-1]
        for i, (key, values) in enumerate(data["series"].items()):
            ax.barh(ypos, values, left=left, height=0.6, color=color_for(i, key), label=key,
                    edgecolor=_SURFACE, linewidth=2)
            left = [a + b for a, b in zip(left, values)]
        ax.set_yticks(ypos, cats, color=_TEXT)
        for y, total in zip(ypos, left):
            ax.text(total, y, f" {int(total)}", va="center", color=_MUTED, fontsize=9)
        ax.grid(axis="x", color=_GRID, linewidth=0.6)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        if cats:
            _legend(ax)
    elif kind in ("bar", "hbar"):
        cats = data["categories"]
        values: list[float] = data["values"]
        if kind == "bar":
            ax.bar(cats, values, width=0.6, color=_CATEGORICAL[0], edgecolor=_SURFACE, linewidth=2)
            for x, v in enumerate(values):
                ax.text(x, v, f"{int(v)}", ha="center", va="bottom", color=_MUTED, fontsize=9)
            ax.grid(axis="y", color=_GRID, linewidth=0.6)
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        else:
            ypos = list(range(len(cats)))[::-1]
            ax.barh(ypos, values, height=0.6, color=_CATEGORICAL[0], edgecolor=_SURFACE, linewidth=2)
            ax.set_yticks(ypos, cats, color=_TEXT)
            for y, v in zip(ypos, values):
                ax.text(v, y, f" {int(v)}", va="center", color=_MUTED, fontsize=9)
            ax.grid(axis="x", color=_GRID, linewidth=0.6)
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_axisbelow(True)

    notes: list[str] = list(data.get("notes") or [])
    if notes:
        fig.text(0.01, 0.01, "\n".join(notes), color=_MUTED, fontsize=8, va="bottom")
        fig.subplots_adjust(bottom=0.12 + 0.035 * len(notes))
    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=_SURFACE, bbox_inches="tight", pad_inches=0.25)
    return buf.getvalue()


def _legend(ax: Any, reverse: bool = False) -> None:
    handles, labels = ax.get_legend_handles_labels()
    if reverse:  # stacked: list the top of the stack first, as it is drawn
        handles, labels = handles[::-1], labels[::-1]
    leg = ax.legend(handles, labels, frameon=False, fontsize=9, loc="upper left", bbox_to_anchor=(1.0, 1.0))
    for text in leg.get_texts():
        text.set_color(_TEXT)


def _draw_timeseries(ax: Any, data: dict[str, Any], color_for: Callable[[int, str], str]) -> None:
    times = [datetime.datetime.fromtimestamp(x, datetime.timezone.utc) for x in data["times"]]
    series: dict[str, list[float]] = data["series"]
    if not times or not series:
        ax.text(0.5, 0.5, "No data in this range", transform=ax.transAxes, ha="center", color=_MUTED)
        return
    ax.grid(axis="y", color=_GRID, linewidth=0.6)
    stacked = data.get("stacked")
    if stacked == "bars":
        # One bar per bucket; width is a fraction of the bucket spacing
        if len(times) > 1:
            width = (times[1] - times[0]).total_seconds() / 86400 * 0.8
        else:
            width = 20.0
        bottom = [0.0] * len(times)
        for i, (key, values) in enumerate(series.items()):
            ax.bar(times, values, bottom=bottom, width=width, color=color_for(i, key), label=key,
                   edgecolor=_SURFACE, linewidth=0.8 if len(times) > 60 else 2, align="edge")
            bottom = [a + b for a, b in zip(bottom, values)]
    elif stacked == "area":
        keys = list(series)
        ax.stackplot(times, *[series[k] for k in keys], labels=keys,
                     colors=[color_for(i, k) for i, k in enumerate(keys)], alpha=0.85,
                     edgecolor=_SURFACE, linewidth=0.5)
        total = [sum(vals) for vals in zip(*series.values())]
        ax.plot(times, total, color=_TEXT, linewidth=2, label="total")
    else:
        for i, (key, values) in enumerate(series.items()):
            ax.plot(times, values, color=color_for(i, key), linewidth=2, label=key)
    if stacked:
        ax.set_ylim(bottom=0)  # bars and areas encode size, so they need a zero baseline
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    locator = AutoDateLocator(minticks=3, maxticks=9)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(ConciseDateFormatter(locator))
    if len(series) > 1 or stacked == "area":
        _legend(ax, reverse=bool(stacked))
