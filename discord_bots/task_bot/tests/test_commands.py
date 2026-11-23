"""Text commands, end to end against the fake Discord pieces."""

from collections import Counter
from typing import Optional

import pytest

from conftest import ALICE, BOB, HELPER, LEAD, OWNER, TEAM, Harness, make_config

from taskbot.models import Reaction
from taskbot.service import UserError
from taskbot.stats import CloserStats, format_closer_stats

DESC = "the quest npc refuses to talk to me"


async def test_add_with_label_and_image(h: Harness) -> None:
    replies = await h.say(ALICE, f"~bug add quest {DESC}", ["https://cdn.discordapp.com/attachments/1/2/a.png"])
    assert replies == ["#1 created successfully"]
    e = h.store.get(1)
    assert e is not None
    assert e.labels == ["quest"] and e.description == DESC and e.author_id == ALICE
    assert [i.attachment_id for i in e.images] == [2]
    assert e.priority == "N/A" and e.complexity == "unknown"
    assert e.message_id is not None and h.port.synced == [1]
    assert [ev.kind for ev in h.store.events_for(1)] == ["created"]


@pytest.mark.parametrize("typed,labels,description", [
    ("zzz " + DESC, ["misc"], "zzz " + DESC),           # no label: misc, and all of it is text
    ("qu,PLUG " + DESC, ["quest", "plugin"], DESC),     # prefixes, any case, several
    ("quest,nope " + DESC, None, None),                 # one unknown: refused
])
async def test_add_labels(h: Harness, typed: str, labels: Optional[list[str]], description: Optional[str]) -> None:
    replies = await h.say(ALICE, "~bug add " + typed)
    e = h.store.get(1)
    if labels is None:
        assert replies[0].startswith("Labels must be one of: [boss,class,") and e is None
    else:
        assert e is not None and e.labels == labels and e.description == description


async def test_add_validation_messages(h: Harness) -> None:
    assert (await h.say(ALICE, "~bug add"))[0].startswith("How to submit a bug:")
    assert await h.say(ALICE, "~bug add too few words here") == ["Description must contain at least 5 words"]
    # The labels don't count as words of the description
    assert await h.say(ALICE, "~bug add quest one two three four") == \
        ["Description must contain at least 5 words"]
    assert await h.say(ALICE, "~bug add quest") == ["Description must contain at least 5 words"]
    assert await h.say(ALICE, "~bug add hey @everyone look at this bug") == \
        ["Please do not include pings in your bug"]
    replies = await h.say(ALICE, "~bug add quest " + "word " * 400)
    assert replies[0].startswith("Please limit your bug to 1600 characters")


async def test_report_alias_and_prefix_rules(h: Harness) -> None:
    assert await h.say(ALICE, "~bug report quest " + DESC) == ["#1 created successfully"]
    # Prefix shorter than 4 characters gets usage, unrelated text is ignored
    assert (await h.say(ALICE, "~bu get 1"))[0].startswith("\n**Commands everyone can use:**")
    assert await h.say(ALICE, "hello there") == []
    assert (await h.say(ALICE, "~BUG"))[0].startswith("\n**Commands everyone can use:**")
    # Unknown or ambiguous command gets usage
    assert (await h.say(ALICE, "~bug s"))[0].startswith("\n**Commands")


async def test_usage_depends_on_privilege(h: Harness) -> None:
    player = "".join(await h.say(ALICE, "~bug"))
    team_first = "".join(await h.say(TEAM, "~bug"))
    team = "".join(await h.say(TEAM, "~bug help team"))
    owner = "".join(await h.say(OWNER, "~bug help team"))
    # Everyone's first view is the players' commands; the team's own are one command away
    assert team_first == "".join(await h.say(TEAM, "~bug help"))
    assert team_first.replace("\nTeam members: `~bug help team` lists the team's commands.\n", "") == player
    assert await h.say(ALICE, "~bug help team") == ["These commands are for team members"]
    assert "**Commands team members can use:**" not in player
    assert "**Commands team members can use:**" in team and "only leads" not in team
    assert "only you can use" in owner and "~bug repost" in owner
    assert "~bug dupe" in player
    assert "~bug chart" not in player and "~bug history" not in player and "~bug cstats" not in player
    assert "~bug chart" in team and "~bug history" in team and "~bug redact" in team
    assert "~bug purge" in owner and "~bug purge" not in team


async def test_get_renders_old_format(h: Harness) -> None:
    await h.add(ALICE, "quest " + DESC)
    h.store.set_reactions(1, [])
    replies = await h.say(BOB, "~bug get 1")
    assert replies == [f"`#1 [quest - N/A] Alice` :white_circle:\n{DESC}"]
    assert await h.say(BOB, "~bug get 99999999999999999999") == ["Bug #99999999999999999999 not found!"]
    assert await h.say(BOB, "~bug get 99") == ["Bug #99 not found!"]
    assert await h.say(BOB, "~bug get abc") == ["'abc' is not a number"]


async def test_edit_permissions_and_notification_rules(h: Harness) -> None:
    await h.add(ALICE, "quest " + DESC)
    # Another player can't edit
    assert await h.say(BOB, "~bug edit 1 description new text here") == \
        ["You do not have permission to edit description for entry #1"]
    # The author can edit the description but not priority
    replies = await h.say(ALICE, "~bug edit 1 desc a better description")
    assert replies[-1] == "Bug #1 updated successfully"
    assert await h.say(ALICE, "~bug edit 1 priority high") == \
        ["You do not have permission to edit priority for entry #1"]
    e = h.store.get(1)
    assert e is not None and not e.pending_notification
    # Team edits set the notification; label-only edits leave it alone
    await h.say(TEAM, "~bug edit 1 priority hi")
    e = h.store.get(1)
    assert e is not None and e.priority == "High" and e.pending_notification
    h.store.update(1, pending_notification=False)
    await h.say(TEAM, "~bug edit 1 label boss,mob")
    e = h.store.get(1)
    assert e is not None and e.labels == ["boss", "mob"] and not e.pending_notification
    await h.say(TEAM, "~bug edit 1 complexity mod")
    e = h.store.get(1)
    assert e is not None and e.complexity == "moderate"
    kinds = [ev.kind for ev in h.store.events_for(1)]
    assert kinds == ["created", "description", "priority", "labels", "complexity"]


async def test_edits_that_change_nothing_are_not_recorded(h: Harness) -> None:
    await h.add(ALICE, "quest " + DESC)
    h.store.clear_dirty(1)
    for command in ("label quest", "priority n/a", "complexity unknown", f"description  {DESC} "):
        replies = await h.say(TEAM, f"~bug edit 1 {command}")
        assert replies[-1] == "Bug #1 updated successfully"
    e = h.store.get(1)
    assert e is not None and not e.pending_notification and 1 not in h.store.dirty_entry_ids()
    assert [ev.kind for ev in h.store.events_for(1)] == ["created"]


async def test_edit_errors(h: Harness) -> None:
    await h.add(ALICE, "quest " + DESC)
    assert (await h.say(TEAM, "~bug edit 1 priority"))[0].startswith("\n__Available Priorities:__")
    assert await h.say(TEAM, "~bug edit 1 priority bogus") == \
        ["Priority must be one of: [N/A,Critical,High,Medium,Low,Zero]"]
    assert await h.say(TEAM, "~bug edit 1 complexity") == \
        ["Available complexities: [easy,moderate,hard,unknown]"]
    assert await h.say(TEAM, "~bug edit 1 image") == ["You need to attach an image"]
    assert await h.say(TEAM, "~bug edit 1 color red") == \
        ["Item to edit must be 'description', 'label', 'image', 'author', 'priority' or 'complexity'"]
    assert (await h.say(TEAM, "~bug edit 1"))[0].startswith("How to edit a bug:")


async def test_append(h: Harness) -> None:
    await h.add(ALICE, "quest " + DESC)
    replies = await h.say(ALICE, "~bug append 1 also on tuesdays")
    assert replies[-1] == "Bug #1 edited"
    e = h.store.get(1)
    assert e is not None and e.description == DESC + "\nalso on tuesdays"
    assert await h.say(BOB, "~bug append 1 me too") == ["You do not have permission to append to #1"]
    assert await h.say(ALICE, "~bug append 1 hi @here") == ["Please do not include pings in your bug"]


async def test_fix_reject_unfix(h: Harness) -> None:
    await h.add(ALICE, "quest " + DESC)
    await h.say(TEAM, "~bug assign 1")
    replies = await h.say(TEAM, "~bug fix 1")
    assert replies[-1] == "Bug #1 marked as fixed"
    assert replies[0].startswith("~~`#1 [quest - N/A] Alice`") and replies[0].endswith("~~\nClosed: Fixed")
    e = h.store.get(1)
    assert e is not None and e.is_closed and e.resolution == "fixed" and e.closed_by == TEAM
    assert e.assignee_id is None and e.pending_notification and e.closed_at == int(h.clock.now)

    replies = await h.say(TEAM, "~bug unfix 1")
    assert replies[-1] == "Bug #1 unmarked as fixed"
    e = h.store.get(1)
    assert e is not None and not e.is_closed and e.resolution is None and e.close_reason is None

    # Authors may reject their own; others may not
    assert await h.say(BOB, "~bug reject 1 nope") == ["You do not have permission to reject #1"]
    assert await h.say(ALICE, "~bug reject 1") == ["Usage: ~bug reject <number> <required explanation>"]
    replies = await h.say(ALICE, "~bug reject 1 my mistake")
    assert replies[-1] == "Bug #1 rejected"
    e = h.store.get(1)
    assert e is not None and e.resolution == "rejected" and not e.pending_notification

    assert await h.say(TEAM, "~bug unfix 1 extra") == ["Usage: ~bug unfix <number>"]
    kinds = [ev.kind for ev in h.store.events_for(1)]
    assert kinds == ["created", "assigned", "unassigned", "closed", "reopened", "closed"]


async def test_dupe(h: Harness) -> None:
    await h.add(ALICE, "quest " + DESC)
    await h.add(BOB, "quest " + DESC + " again")
    replies = await h.say(HELPER, "~bug dupe 2 #1 same thing")
    assert replies[-1] == "Bug #2 closed as a duplicate of #1"
    e = h.store.get(2)
    assert e is not None and e.resolution == "duplicate" and e.duplicate_of == 1
    assert e.close_reason == "Duplicate of #1: same thing"
    assert await h.say(TEAM, "~bug dupe 1 1") == ["Bug #1 can not be a duplicate of itself"]
    assert await h.say(BOB, "~bug dupe 1 2") == ["You do not have permission to mark as duplicate #1"]


@pytest.mark.parametrize("command,resolution,original,reply", [
    ("~bug reject 2 dupe of #1", "duplicate", 1, "Bug #2 closed as a duplicate of #1"),
    ("~bug reject 2 same issue as described in 1", "duplicate", 1, "Bug #2 closed as a duplicate of #1"),
    ("~bug reject 2 duplicate", "duplicate", None, "Bug #2 closed as a duplicate"),
    ("~bug reject 2 dupe of 999", "duplicate", None, "Bug #2 closed as a duplicate"),   # no such entry
    ("~bug reject 2 dupe of #2", "duplicate", None, "Bug #2 closed as a duplicate"),    # itself
    ("~bug reject 2 works as intended in 1.20", "rejected", None, "Bug #2 rejected"),
    ("~bug fix 2 fixed, dupe of 1", "duplicate", 1, "Bug #2 closed as a duplicate of #1"),
    ("~bug fix 2 dupe, fixed in the patch", "fixed", None, "Bug #2 marked as fixed"),  # no original named
])
async def test_fix_and_reject_reasons_that_say_duplicate(h: Harness, command: str, resolution: str,
                                                        original: Optional[int], reply: str) -> None:
    await h.add(ALICE, "quest " + DESC)
    await h.add(BOB, "quest " + DESC + " again")
    assert (await h.say(TEAM, command))[-1] == reply
    e = h.store.get(2)
    assert e is not None and e.resolution == resolution and e.duplicate_of == original
    assert e.close_reason == command.split(maxsplit=3)[3]   # the reason is kept as typed


async def test_original_lists_its_duplicates(h: Harness) -> None:
    for _ in range(4):
        await h.add(ALICE, "quest " + DESC)
    h.store.clear_dirty(1)
    await h.say(HELPER, "~bug dupe 3 1")
    await h.say(HELPER, "~bug dupe 2 1")
    # The original's tracking message is published again, now listing both
    assert 1 in h.store.dirty_entry_ids()
    assert (await h.say(ALICE, "~bug get 1"))[0].endswith(f"{DESC}\n`Duplicates: #2, #3`")
    # Reopened, re-duped elsewhere or purged: gone from the list, and published again
    for command, listed in (("~bug unfix 3", "#2"), ("~bug dupe 2 4", None)):
        h.store.clear_dirty(1)
        await h.say(TEAM, command)
        assert 1 in h.store.dirty_entry_ids()
        shown = (await h.say(ALICE, "~bug get 1"))[0]
        assert shown.endswith(f"`Duplicates: {listed}`") if listed else "Duplicates" not in shown
    h.store.clear_dirty(4)
    await h.say(LEAD, "~bug purge 2 confirm")
    assert 4 in h.store.dirty_entry_ids()
    assert "Duplicates" not in (await h.say(ALICE, "~bug get 4"))[0]


def test_duplicates_line_only_where_it_fits(h: Harness) -> None:
    from taskbot.formatting import format_entry  # pylint: disable=import-outside-toplevel
    from taskbot.models import Entry  # pylint: disable=import-outside-toplevel
    entry = Entry(1, "x" * 1960, ALICE, "N/A", "unknown", ["quest"])
    def render(**kwargs: object) -> str:
        return format_entry(entry, h.config, lambda _: "alice", **kwargs)  # type: ignore[arg-type]
    assert render(duplicates=[5]) == render() and len(render()) <= 2000
    assert "x" * 1960 in render()   # the description isn't shortened to make room
    entry.description = "short"
    assert render(duplicates=[5, 6]).endswith("short\n`Duplicates: #5, #6`")


async def test_redact_hides_from_everyone_but_the_team(h: Harness) -> None:
    await h.add(ALICE, "quest secret exploit steps are here", ["https://cdn.discordapp.com/attachments/1/2/a.png"])
    await h.say(ALICE, "~bug append 1 more secret details")
    await h.say(TEAM, "~bug reject 1 this reveals the secret")
    assert await h.say(BOB, "~bug redact 1") == ["You do not have permission to use this command"]
    replies = await h.say(HELPER, "~bug redact 1")
    assert replies == ["Bug #1 redacted; only the team can see its text. You still need to manually "
                       "delete any messages related to this in other channels."]
    assert await h.say(HELPER, "~bug redact 1") == ["Bug #1 is already redacted"]
    e = h.store.get(1)
    assert e is not None and e.description == "redacted" and e.close_reason == "" and e.redacted
    assert e.images == [] and e.resolution == "rejected"
    dump = repr(h.store.conn.execute("SELECT * FROM events").fetchall())
    assert "secret" not in dump
    assert all("secret" not in r for r in await h.say(TEAM, "~bug history 1"))
    assert await h.say(BOB, "~bug dsearch secret") == ["0 bugs found matching secret"]

    # The team can still read it, privately (through the service: the API and slash commands)
    team, helper = h.actor(TEAM), h.actor(HELPER)
    hidden = h.service.redacted_content(team, e)
    assert "secret exploit steps are here" in str(hidden["description"])
    assert hidden["close_reason"] == "this reveals the secret"
    assert hidden["images"] == ["https://cdn.discordapp.com/attachments/1/2/a.png"]
    assert any(ev["kind"] == "appended" and ev["new"] == "more secret details" for ev in hidden["events"])
    with pytest.raises(UserError):
        h.service.redacted_content(helper, e)

    # An open entry stays open, as before
    await h.add(ALICE, "quest " + DESC)
    await h.say(TEAM, "~bug redact 2")
    e = h.store.get(2)
    assert e is not None and not e.is_closed and e.redacted


async def test_purge(h: Harness) -> None:
    await h.add(ALICE, "quest " + DESC)
    await h.add(ALICE, "quest " + DESC)
    await h.say(TEAM, "~bug dupe 2 1")
    message_id = h.store.get(1).message_id  # type: ignore[union-attr]
    assert await h.say(TEAM, "~bug purge 1 confirm") == ["You do not have permission to use this command"]
    assert "can't be undone" in (await h.say(LEAD, "~bug purge 1"))[0]
    assert h.store.get(1) is not None
    replies = await h.say(LEAD, "~bug purge 1 confirm")
    assert replies[0].startswith("Bug #1 purged.")
    assert h.store.get(1) is None and message_id in h.port.deleted
    assert h.store.conn.execute("SELECT COUNT(*) FROM events WHERE entry_id = 1").fetchone()[0] == 0
    dup = h.store.get(2)
    assert dup is not None and dup.duplicate_of is None
    assert await h.say(BOB, "~bug get 1") == ["Bug #1 not found!"]
    await h.add(ALICE, "quest " + DESC)
    assert h.store.get(3) is not None   # numbers are never reused


async def test_search_grammar(h: Harness) -> None:
    for i in range(12):
        await h.add(ALICE, f"quest number {i} " + DESC)
    await h.say(TEAM, "~bug edit 3 priority high")
    await h.say(TEAM, "~bug edit 4 priority zero")
    await h.say(TEAM, "~bug edit 5 complexity hard")
    replies = await h.say(BOB, "~bug search quest")
    assert replies[0] == "Limiting to top 10 results"
    assert replies[1].startswith("`#3 [quest - High] Alice`")  # High sorts first
    assert replies[-1] == "11 bugs found matching labels=quest priorities=N/A,Critical,High,Medium,Low complexities="
    replies = await h.say(BOB, "~bug search quest hard 5")
    assert replies[-1] == "1 bugs found matching labels=quest priorities=N/A,Critical,High,Medium,Low complexities=hard"
    replies = await h.say(BOB, "~bug search zero")
    assert replies[-1].startswith("1 bugs found") and "#4" in replies[0]
    assert await h.say(BOB, "~bug search wat") == ["No priority, label, complexity, or 'assigned' matching 'wat'"]
    assert await h.say(BOB, "~bug search 5") == ["Must specify something to search for"]
    # Search results include links
    replies = await h.say(BOB, "~bug search quest high")
    assert "https://discord.com/channels/10/30/" in replies[0]


async def test_dsearch_and_asearch(h: Harness) -> None:
    await h.add(ALICE, "quest the Ücase thing breaks here sometimes")
    await h.add(BOB, "quest another unrelated report goes here")
    await h.say(TEAM, "~bug fix 2")
    replies = await h.say(BOB, "~bug dsearch ücase,BREAKS")
    assert replies[0] == "1 bugs found matching ücase,BREAKS"
    replies = await h.say(BOB, "~bug dsearch here 1")
    assert replies[0] == "1 bugs found matching here 1"
    replies = await h.say(ALICE, "~bug asearch")
    assert replies[-1] == "1 open bugs of 1 total from author Alice in Guild"
    replies = await h.say(ALICE, "~bug asearch bobb")
    assert replies[-1] == "0 open bugs of 1 total from author Bob"


async def test_rsearch_reads_reaction_table(h: Harness) -> None:
    for _ in range(3):
        await h.add(ALICE, "quest " + DESC)
    h.store.set_reactions(1, [Reaction("👍", 2)])
    h.store.adjust_reaction(2, "👍", 1)
    for _ in range(4):
        h.store.adjust_reaction(3, "👍", 1)
    replies = await h.say(BOB, "~bug rsearch 👍")
    # #2 and #3 only have live reaction events so far, never a full read: say so
    assert replies[-1].startswith("Reaction counts are still being loaded from Discord (2 messages")
    replies = replies[:-1]
    assert [r.split("]")[0] for r in replies] == ["`#3 [quest - N/A", "`#1 [quest - N/A", "`#2 [quest - N/A"]
    assert replies[0].endswith("👍 4    ")
    for entry_id in (2, 3):
        h.store.mark_reactions_checked(entry_id)
    assert await h.say(BOB, "~bug rsearch 🎉") == ["No entries with reaction '🎉'"]


async def test_stats_and_astats(h: Harness) -> None:
    await h.add(ALICE, "quest " + DESC)
    await h.add(ALICE, "quest " + DESC)
    await h.add(BOB, "quest " + DESC)
    await h.say(TEAM, "~bug edit 1 priority high")
    await h.say(TEAM, "~bug fix 3")
    stats = (await h.say(BOB, "~bug stats"))[0]
    assert stats.startswith("Current bug stats:```             Easy      Moderate  Hard      Unknown   Total")
    assert "\nHigh       | 0         0         0         1         1         " in stats
    assert stats.endswith("Total Open : 2\nClosed     : 1```")
    replies = await h.say(BOB, "~bug astats")
    assert replies == ["Current bug author stats:",
                       "```python\nAlice                : 2\nBob                  : 1```"]


async def test_cstats(h: Harness) -> None:
    await h.add(ALICE, "quest " + DESC)
    await h.add(ALICE, "quest " + DESC)
    await h.add(ALICE, "quest " + DESC)
    await h.say(TEAM, "~bug fix 1")
    await h.say(TEAM, "~bug reject 2 not a bug")
    await h.say(ALICE, "~bug reject 3 my mistake")
    assert await h.say(HELPER, "~bug cstats") == ["You do not have permission to use this command"]
    text = "".join(await h.say(TEAM, "~bug cstats"))
    assert "Teammate" not in text and "1 more with fewer than 20 closes each" in text
    text = "".join(await h.say(TEAM, "~bug cstats 0 1"))
    assert "Teammate" in text and "1 closed by their own authors" in text
    line = next(line for line in text.splitlines() if line.startswith("Teammate"))
    assert line.split()[1:] == ["1", "1", "0", "2"]
    assert "Teammate" in "".join(await h.say(TEAM, "~bug cstats 30"))
    assert (await h.say(TEAM, "~bug cstats x"))[0] == "Usage: ~bug cstats [days] [minimum]"


def test_cstats_splits_into_whole_code_blocks() -> None:
    stats = CloserStats(by_closer={f"discord:{i}": Counter(fixed=100 - i) for i in range(80)})
    messages = format_closer_stats(stats, make_config(), lambda _id: None, None)
    assert len(messages) > 1
    for m in messages:
        assert len(m) <= 1900 and m.count("```") == 2
    assert messages[0].startswith("Who has closed the most bugs overall:")
    # The notes go in their own message when they don't fit after the last block
    stats.self_closes, stats.unknown_closer = 2000, 22000
    for limit in range(150, 400, 7):
        messages = format_closer_stats(stats, make_config(), lambda _id: None, None, limit=limit)
        assert all(len(m) <= limit for m in messages)
        assert all(m.count("```") in (0, 2) for m in messages) and "22000 closed with no recorded closer" in messages[-1]


async def test_labels_add_and_remove(h: Harness) -> None:
    await h.add(ALICE, "quest,boss " + DESC)
    await h.add(ALICE, "boss " + DESC)
    assert await h.say(TEAM, "~bug addlabel gui") == ["You do not have permission to use this command"]
    assert await h.say(LEAD, "~bug addlabel gui") == ["Label gui added successfully"]
    assert (await h.say(LEAD, "~bug dellabel misc"))[0].startswith("misc can't be removed")
    assert await h.say(LEAD, "~bug addlabel qu") == ["Can not add label qu because it matches quest"]
    assert (await h.say(LEAD, "~bug addlabel bad1"))[0].startswith("Usage: ~bug addlabel <label>")
    assert await h.say(LEAD, "~bug dellabel boss") == ["Label boss removed successfully from 2 bugs"]
    e1, e2 = h.store.get(1), h.store.get(2)
    assert e1 is not None and e2 is not None
    assert e1.labels == ["quest"] and e2.labels == ["misc"]
    assert "boss" not in h.store.labels() and "boss" in h.store.labels(include_inactive=True)
    # Re-adding a removed label works
    assert await h.say(LEAD, "~bug addlabel boss") == ["Label boss added successfully"]
    assert h.store.labels()[-1] == "boss"


async def test_assignment(h: Harness) -> None:
    await h.add(ALICE, "quest " + DESC)
    assert await h.say(ALICE, "~bug assign 1") == ["You do not have permission to use this command"]
    replies = await h.say(TEAM, "~bug assign 1")
    assert replies[-1] == "Bug #1 assigned to Team Nick"
    assert "`Assigned: Teammate`" in replies[0]
    replies = await h.say(TEAM, "~bug assign 1 bobb")
    assert replies[-1] == "Bug #1 assigned to Bob"
    assert (await h.say(TEAM, "~bug assign 1 b"))[0].startswith("Multiple users match 'b'")
    replies = await h.say(TEAM, "~bug list_assigned all")
    assert replies[-1] == "1 total assigned bugs found"
    replies = await h.say(TEAM, "~bug list_assigned bobb")
    assert replies[-1] == "1 assigned bugs found for user Bob"
    replies = await h.say(LEAD, "~bug ping_assigned 777")
    assert replies[-1] == "1 total assigned bugs mentioned in channel other-channel"
    other = [s for s in h.log if s.channel == "other"]
    assert other and f"<@{BOB}>" in other[0].text and other[0].mentions
    assert (await h.say(TEAM, "~bug unassign 1"))[-1] == "Bug #1 unassigned"
    assert await h.say(TEAM, "~bug unassign 1") == ["Bug #1 is already unassigned"]


async def test_notifications(h: Harness) -> None:
    await h.add(ALICE, "quest " + DESC)
    await h.add(BOB, "quest " + DESC)
    await h.say(BOB, "~bug notify off")
    await h.say(TEAM, "~bug fix 1")
    await h.say(TEAM, "~bug fix 2")
    replies = await h.say(TEAM, "~bug send_notifications")
    assert replies[0] == "Notification process started..."
    assert replies[1].startswith(f"<@{ALICE}> Your bug was updated:\n    ~~`#1")
    assert replies[-1] == ("2 notifications processed successfully, 1 of which were suppressed by "
                           "user opt-out, 0 of which could not find a user to ping")
    assert h.store.pending_notification_ids() == []
    replies = await h.say(BOB, "~bug notify")
    assert replies[0].startswith("You will __not__ be notified of changes to your bugs.")
    assert await h.say(BOB, "~bug notify maybe") == ["Argument to ~bug notify must be 'on' or 'off'"]


async def test_prune(h: Harness) -> None:
    await h.add(ALICE, "quest " + DESC)
    await h.add(ALICE, "quest " + DESC)
    await h.say(TEAM, "~bug fix 1")
    replies = await h.say(LEAD, "~bug prune")
    assert replies[0] == "Prune started, this will take some time..."
    assert replies[-1] == "1 entries pruned successfully"
    e = h.store.get(1)
    assert e is not None and e.message_id is None
    assert [ev.kind for ev in h.store.events_for(1)][-1] == "closed"  # prune leaves no event


async def test_history(h: Harness) -> None:
    await h.add(ALICE, "quest " + DESC)
    await h.say(TEAM, "~bug edit 1 priority high")
    await h.say(TEAM, "~bug fix 1 done")
    assert await h.say(HELPER, "~bug history 1") == ["You do not have permission to use this command"]
    text = "\n".join(await h.say(TEAM, "~bug history 1"))
    assert text.startswith("History of bug #1:")
    assert "**Alice** created" in text and "set priority N/A -> High" in text
    assert "closed as **fixed**: done" in text


async def test_roulette(h: Harness) -> None:
    assert await h.say(BOB, "~bug roulette") == ["No bugs found matching those search terms"]
    await h.add(ALICE, "quest " + DESC)
    replies = await h.say(BOB, "~bug roulette quest")
    assert replies[0].startswith("`#1 [quest")


async def test_discussion_mentions(h: Harness) -> None:
    for _ in range(5):
        await h.add(ALICE, "quest " + DESC)
    start = len(h.log)
    await h.handler.handle_discussion_message("see bug-2 please", h.responder)
    assert "https://discord.com/channels/10/30/" in h.log[start].text and h.log[start].text.startswith("`#2")
    start = len(h.log)
    await h.handler.handle_discussion_message("bug-1 BUG-99 bug-3", h.responder)
    assert h.log[start].text.count("https://") == 2  # unknown #99 skipped, not fatal
    start = len(h.log)
    await h.handler.handle_discussion_message("bug-1 bug-2 bug-3 bug-4", h.responder)
    assert h.log[start].text.startswith("Here are the links to the bugs you mentioned, limited to 3 links:")


async def test_unexpected_error_posts_traceback(h: Harness, monkeypatch: pytest.MonkeyPatch) -> None:
    async def boom(*_args: object) -> None:
        raise RuntimeError("kaboom")
    monkeypatch.setitem(h.handler.commands, "stats", boom)
    replies = await h.say(ALICE, "~bug stats")
    assert replies[0] == f"<@{ALICE}>" and replies[1] == "**ERROR**: ```kaboom```"
    assert "RuntimeError" in replies[2]


async def test_chart_command(h: Harness) -> None:
    await h.add(ALICE, "quest " + DESC)
    assert await h.say(HELPER, "~bug chart") == ["You do not have permission to use this command"]
    replies = await h.say(TEAM, "~bug chart")
    assert replies[0].startswith("Available charts")
    await h.say(TEAM, "~bug chart intake week 90d")
    sent = h.log[-1]
    assert sent.file is not None and sent.file.data.startswith(b"\x89PNG")
    assert await h.say(TEAM, "~bug chart nope") == \
        ["Unknown chart 'nope'. Available: backlog, intake, closes, closers, age, labels"]
    assert (await h.say(TEAM, "~bug chart intake sideways"))[0].startswith("Unknown chart option 'sideways'")


async def test_long_entries_fit_in_one_message(h: Harness) -> None:
    await h.add(ALICE, "quest " + "word " * 315)
    replies = await h.say(ALICE, "~bug append 1 " + "more " * 20)
    assert "exceeds the 1600 character maximum" in replies[0]
    await h.say(TEAM, "~bug assign 1 bobb")
    assert (await h.say(TEAM, "~bug reject 1 " + "because " * 130))[0].startswith("Please keep the reason to 1000")
    await h.say(TEAM, "~bug reject 1 " + "because " * 120)
    e = h.store.get(1)
    assert e is not None and e.is_closed
    text = h.handler.render(e, include_reactions=True)
    assert len(text) <= 2000 and text.endswith("because")
