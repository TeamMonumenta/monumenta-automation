"""Chart data: the backlog's stacking, closes, intake and closers."""

import pytest

from conftest import ALICE, TEAM, Harness

from taskbot.charts import CHARTS, ChartError, parse_options

DESC = "the map crashes when opened in the northern regions"
DAY = 86400


async def entries(h: Harness) -> None:
    """Four entries over four days; #1 and #2 closed by TEAM on day 3."""
    for i in range(4):
        await h.say(ALICE, f"~bug add quest {DESC} {i}")
        h.clock.advance(DAY)
    h.store.update(1, complexity="hard", priority="High")
    h.store.update(2, complexity="easy", priority="Low")
    h.store.update(3, complexity="hard")
    for n in (1, 2):
        await h.say(TEAM, f"~bug fix {n}")
    h.clock.advance(60)


async def test_backlog_stacks_by_complexity(h: Harness) -> None:
    await entries(h)
    data = h.charts.data("backlog", parse_options(["day", "all"]))
    assert data["stacked"] == "area" and list(data["series"]) == ["unknown", "easy", "hard"]
    totals = [sum(v) for v in zip(*data["series"].values())]
    assert totals[-1] == 2  # #3 and #4 still open
    assert data["series"]["hard"][-1] == 1 and data["series"]["easy"][-1] == 0
    assert data["times"][-1] == int(h.clock.now)  # the last point is now
    assert data["colors"]["unknown"] != data["colors"]["easy"]

    data = h.charts.data("backlog", parse_options(["priority", "day", "all"]))
    assert list(data["series"]) == ["N/A", "Low", "High"]  # bottom to top


async def test_backlog_for_one_label(h: Harness) -> None:
    await entries(h)
    h.store.set_labels(3, ["misc", "plugin"])
    opts = h.charts.parse_options(["Plugin", "day", "all"])
    assert opts.label == "plugin"
    data = h.charts.data("backlog", opts)
    assert data["title"].startswith("Open bugs labeled plugin by complexity")
    assert {k: v[-1] for k, v in data["series"].items()} == {"hard": 1}


async def test_closers(h: Harness) -> None:
    await entries(h)
    data = h.charts.data("closers", parse_options([]))
    assert data["series"] == {"fixed": [2.0]} and data["notes"] == []
    assert h.charts.render("closers", parse_options([]))[:4] == b"\x89PNG"
    # Renamed resolutions keep their colors
    h.config.resolution_names = {"fixed": "implemented"}
    for name in ("closes", "closers"):
        data = h.charts.data(name, parse_options(["all"]))
        assert list(data["series"]) == ["implemented"] and "implemented" in data["colors"]


async def test_closes_and_intake(h: Harness) -> None:
    await entries(h)
    closes = h.charts.data("closes", parse_options([]))
    assert closes["bucket"] == "month" and {k: sum(v) for k, v in closes["series"].items()} == {"fixed": 2}
    # misc only counts when there is no other label
    h.store.set_labels(1, ["misc", "plugin"])
    h.store.set_labels(2, ["misc"])
    intake = h.charts.data("intake", parse_options(["day", "all"]))
    assert {k: sum(v) for k, v in intake["series"].items()} == {"quest": 2, "plugin": 1, "misc": 1}


def test_options_a_chart_doesnt_take(h: Harness) -> None:
    # Only the backlog takes a split or a label
    for name, option, error in (("intake", "complexity", "can't be split by complexity"),
                                ("closes", "complexity", "can't be split by complexity"),
                                ("closers", "priority", "can't be split by priority"),
                                ("closes", "plugin", "Only the backlog")):
        with pytest.raises(ChartError, match=error):
            h.charts.data(name, h.charts.parse_options([option]))
    for word in ("label", "none", "resolution", "light"):
        with pytest.raises(ChartError):
            parse_options([word])


async def test_every_chart_and_grouping_renders(h: Harness) -> None:
    await entries(h)
    for name, spec in CHARTS.items():
        for by in spec.by or ("",):
            png = h.charts.render(name, parse_options([by, "all"]))
            assert png[:4] == b"\x89PNG", (name, by)


async def test_periods_are_whole_buckets_and_bounded(h: Harness) -> None:
    await entries(h)
    data = h.charts.data("intake", parse_options(["2d", "week"]))
    # Two days back is part way through a week: the chart starts at that week's start
    assert sum(sum(v) for v in data["series"].values()) == 4
    with pytest.raises(ChartError, match="100 years"):
        parse_options(["1000y"])
    with pytest.raises(ChartError, match="more than 1000 days"):
        h.charts.data("backlog", parse_options(["10y", "day"]))
