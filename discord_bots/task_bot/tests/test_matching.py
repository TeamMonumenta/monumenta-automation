"""Prefix matching keeps the old semantics, and new commands steal no abbreviation in use."""

from taskbot.commands import COMMAND_ORDER, LEGACY_COMMAND_ORDER, RETIRED_COMMANDS
from taskbot.interactive import SESSION_COMMANDS
from taskbot.matching import get_list_match, split_string

OLD_SESSION_COMMANDS = ("reject", "edit", "append", "fix", "unfix", "assign", "unassign",
                        "help", "next", "prev", "stop")


def test_order_decides_and_new_commands_have_short_forms() -> None:
    # Order sensitivity of the original implementation: an ambiguity found first wins
    assert get_list_match("fix", ["fixa", "fixb", "fix"]) is None
    assert get_list_match("fix", ["fixa", "fix", "fixb"]) == "fix"
    assert get_list_match("fi", ["fixa", "fixb"]) is None
    # The new commands' abbreviations
    for typed, command in (("du", "dupe"), ("h", "history"), ("ch", "chart"), ("cs", "cstats")):
        assert get_list_match(typed, COMMAND_ORDER) == command


def _all_prefixes(words: tuple[str, ...]) -> set[str]:
    return {w[:i] for w in words for i in range(1, len(w) + 1)}


def _assert_compatible(old: tuple[str, ...], new: tuple[str, ...], retired: tuple[str, ...] = ()) -> None:
    changed: list[str] = []
    for prefix in sorted(_all_prefixes(old)):
        before = get_list_match(prefix, old)
        after = get_list_match(prefix, new)
        if before in retired:
            continue
        if before != after:
            changed.append(f"{prefix!r}: {before} -> {after}")
    assert not changed, "abbreviations changed meaning:\n" + "\n".join(changed)


def test_every_old_command_abbreviation_still_means_the_same() -> None:
    _assert_compatible(LEGACY_COMMAND_ORDER, COMMAND_ORDER, RETIRED_COMMANDS)


def test_every_old_session_abbreviation_still_means_the_same() -> None:
    _assert_compatible(OLD_SESSION_COMMANDS, SESSION_COMMANDS)


def test_split_string() -> None:
    assert not split_string("")
    assert split_string("a\nb") == ["a\nb"]
    long = "x" * 4000
    chunks = split_string(long)
    assert [len(c) for c in chunks] == [1950, 1950, 100]
    lines = "\n".join(["y" * 100] * 50)
    assert all(len(c) <= 1950 for c in split_string(lines))
    assert "".join(split_string(lines)).replace("\n", "") == lines.replace("\n", "")
