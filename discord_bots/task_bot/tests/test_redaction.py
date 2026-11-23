"""Redaction holds up while other commands are part way through, and can be repeated."""

from conftest import ALICE, BOB, HELPER, LEAD, TEAM, Harness

DESC = "the quest npc refuses to talk to me"
SECRET = "secret exploit: do x then y then z"


async def test_listing_shows_entries_as_they_are_when_sent(h: Harness) -> None:
    await h.add(ALICE, "quest " + DESC)
    await h.add(ALICE, "quest " + SECRET)
    # #2 is redacted while the bot is still sending #1 (results are sorted by number here)
    h.port.during_refresh.append(lambda: None)
    h.port.during_refresh.append(lambda: h.service.redact(h.actor(HELPER), h.service.get_entry(2)))
    replies = await h.say(BOB, "~bug search quest")
    assert not any("secret" in r for r in replies)
    assert any("redacted" in r for r in replies)


async def test_notifications_use_the_entry_as_it_is_when_sent(h: Harness) -> None:
    await h.add(ALICE, "quest " + DESC)
    await h.add(ALICE, "quest " + SECRET)
    await h.add(ALICE, "quest " + DESC + " again")
    for n in (1, 2, 3):
        await h.say(TEAM, f"~bug edit {n} priority high")

    def redact_two_purge_three() -> None:
        h.service.redact(h.actor(HELPER), h.service.get_entry(2))
        h.service.purge(h.actor(LEAD), h.service.get_entry(3))
    h.port.during_refresh.append(redact_two_purge_three)
    replies = await h.say(TEAM, "~bug send_notifications")
    assert not any("secret" in r for r in replies)
    pings = [s for s in h.log if s.text.startswith("<@")]
    assert len(pings) == 1 and pings[0].mentions == (ALICE,)
    assert replies[-1].startswith("1 notifications processed successfully")
    assert h.store.pending_notification_ids() == []


async def test_redacting_again_hides_what_was_added_since(h: Harness) -> None:
    await h.add(ALICE, "quest " + SECRET)
    await h.say(HELPER, "~bug redact 1")
    assert await h.say(HELPER, "~bug redact 1") == ["Bug #1 is already redacted"]
    await h.say(ALICE, "~bug append 1 the steps again: x y z")
    await h.say(ALICE, "~bug reject 1 because x y z")
    await h.say(HELPER, "~bug redact 1")
    e = h.store.get(1)
    assert e is not None and e.description == "redacted" and e.close_reason == ""
    assert "x y z" not in repr(h.store.conn.execute("SELECT * FROM events").fetchall())
    hidden = h.service.redacted_content(h.actor(TEAM), e)
    assert SECRET in hidden["description"] and "the steps again" in hidden["description"]
    assert hidden["close_reason"] == "because x y z"


async def test_redaction_removes_in_game_notices(h: Harness) -> None:
    await h.add(ALICE, "quest " + SECRET)
    player = "00000000-0000-0000-0000-000000000001"
    h.store.add_notice(player, 1, f"Your bug #1 was closed (rejected): {SECRET}", 0)
    await h.say(HELPER, "~bug redact 1")
    assert h.store.pending_notices(player) == []


async def test_prune_skips_an_entry_reopened_meanwhile(h: Harness) -> None:
    await h.add(ALICE, "quest " + DESC)
    await h.add(ALICE, "quest " + DESC)
    await h.say(TEAM, "~bug fix 1")
    await h.say(TEAM, "~bug fix 2")
    delete = h.port.delete_tracking_message

    async def reopen_two_during_first_delete(message_id: int) -> bool:
        if h.store.get(2) is not None and h.store.get(2).is_closed:  # type: ignore[union-attr]
            h.service.reopen(h.actor(TEAM), h.service.get_entry(2))
        return await delete(message_id)
    h.port.delete_tracking_message = reopen_two_during_first_delete  # type: ignore[method-assign]
    replies = await h.say(LEAD, "~bug prune")
    assert replies[-1] == "1 entries pruned successfully"
    two = h.store.get(2)
    assert two is not None and not two.is_closed and two.message_id is not None


async def test_reopening_an_open_entry_changes_nothing(h: Harness) -> None:
    await h.add(ALICE, "quest " + DESC)
    assert await h.say(TEAM, "~bug unfix 1") == ["Bug #1 is not closed"]
    e = h.store.get(1)
    assert e is not None and not e.pending_notification


async def test_an_entry_reopened_while_prune_deletes_its_message_is_posted_again(h: Harness) -> None:
    await h.add(ALICE, "quest " + DESC)
    await h.say(TEAM, "~bug fix 1")
    delete = h.port.delete_tracking_message

    async def reopen_meanwhile(message_id: int) -> bool:
        h.service.reopen(h.actor(TEAM), h.service.get_entry(1))
        h.store.clear_dirty(1)   # the publisher edited the message that is about to go
        return await delete(message_id)
    h.port.delete_tracking_message = reopen_meanwhile  # type: ignore[method-assign]
    await h.say(LEAD, "~bug prune")
    assert h.store.dirty_entry_ids() == [1]
