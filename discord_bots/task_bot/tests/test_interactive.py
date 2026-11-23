"""isearch / iroulette sessions."""

from conftest import ALICE, BOB, TEAM, Harness

DESC = "the quest npc refuses to talk to me"


async def _setup(h: Harness) -> None:
    for i in range(4):
        await h.add(ALICE, f"quest item {i} " + DESC)


async def test_walk_and_act(h: Harness) -> None:
    await _setup(h)
    replies = await h.say(TEAM, "~bug isearch quest")
    assert replies[0] == "Started interactive session with 4 entries"
    assert replies[1].startswith("`#1 ")
    assert (await h.say(TEAM, "next"))[0].startswith("`#2 ")
    assert (await h.say(TEAM, "n 2"))[0].startswith("`#4 ")
    assert (await h.say(TEAM, "prev"))[0].startswith("`#3 ")
    replies = await h.say(TEAM, "fix all good now")
    assert replies[-1] == "Bug #3 marked as fixed"
    e = h.store.get(3)
    assert e is not None and e.close_reason == "all good now"
    # Going back shows the entry as it is now, not as it was when the session started
    await h.say(TEAM, "next")
    replies = await h.say(TEAM, "prev")
    assert replies[0].startswith("~~`#3 ")
    await h.say(TEAM, "next")
    assert (await h.say(TEAM, "dupe 1"))[-1] == "Bug #4 closed as a duplicate of #1"
    assert await h.say(TEAM, "stop") == ["Iteration aborted"]
    assert h.handler.sessions == []


async def test_other_users_and_help_prompts(h: Harness) -> None:
    await _setup(h)
    await h.say(TEAM, "~bug isearch quest")
    # Someone else's messages are not taken by the session
    assert (await h.say(BOB, "next")) == []
    replies = await h.say(TEAM, "what")
    assert replies == ["Valid responses are: ```reject edit append fix unfix assign unassign help next prev stop dupe```"]
    replies = await h.say(TEAM, "huh")
    assert replies[-1] == "To see these options again, use 'help'"
    assert await h.say(TEAM, "huh") == []
    # Normal commands still work while a session is open
    replies = await h.say(TEAM, "~bug get 2")
    assert replies[0].startswith("`#2 ")


async def test_end_of_list_and_timeout(h: Harness) -> None:
    await _setup(h)
    await h.say(TEAM, "~bug isearch quest")
    assert await h.say(TEAM, "next 10") == ["No more results to display"]
    assert h.handler.sessions == []
    await h.say(TEAM, "~bug isearch quest")
    h.clock.advance(6 * 3600 + 1)
    replies = await h.say(TEAM, "next")
    assert replies == ["Interactive session aborted due to inactivity"]
    assert h.handler.sessions == []


async def test_iroulette_starts_a_session(h: Harness) -> None:
    await _setup(h)
    replies = await h.say(TEAM, "~bug iroulette")
    assert replies[0] == "Started interactive session with 4 entries"
    assert await h.say(TEAM, "prev") == ["Nothing to go back to"]
