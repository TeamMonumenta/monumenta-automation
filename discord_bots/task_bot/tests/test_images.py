"""Saved copies of images: what gets saved, redaction, reupload, purge and the API.

Downloading from and posting to Discord are not tested here (no fakes of Discord's CDN);
those were tried by hand against the test guild.
"""

import os

import pytest

from conftest import ALICE, BOB, HELPER, LEAD, TEAM, Harness
from taskbot.api import create_app
from taskbot.tokens import mint_service_token, mint_token
from taskbot.images import ImageArchive, file_name
from taskbot.models import ImageFile
from taskbot.service import Forbidden

DESC = "the quest npc refuses to talk to me"
IMG = "https://cdn.discordapp.com/attachments/20/111/shot.png?ex=1&is=2&hm=3"
IMG2 = "https://cdn.discordapp.com/attachments/20/222/other%20shot.PNG"


def save(h: Harness, entry_id: int, url: str, data: bytes = b"png") -> str:
    """Save an image as the bot's save loop does."""
    path = h.service.archive.relative_path(entry_id, url)
    h.service.archive.write(path, data)
    h.store.add_image_file(ImageFile(entry_id, url, path, len(data), h.service.now()))
    return path


def test_file_names() -> None:
    assert file_name(IMG) == "111-shot.png"
    assert file_name(IMG2) == "222-other_20shot.PNG"
    assert file_name("https://cdn.discordapp.com/ephemeral-attachments/9/333/image.png?ex=1") == "333-image.png"
    assert file_name("https://cdn.discordapp.com/attachments/1/2/..%2F..%2Fetc") == "2-2F.._2Fetc"
    archive = ImageArchive("/data/images")
    with pytest.raises(ValueError):
        archive.absolute("../tasks.db")


async def test_images_to_save(h: Harness) -> None:
    a = await h.add(ALICE, DESC, [IMG])
    b = await h.add(ALICE, DESC, [IMG2])
    c = await h.add(BOB, DESC, ["https://example.com/elsewhere.png"])
    # Only Discord attachments (not other hosts, nor Discord's proxy for outside images)
    proxied = await h.add(BOB, DESC, ["https://media.discordapp.net/external/abc/https/example.com/x.png"])
    assert c and proxied and h.store.images_to_save(10, h.service.now()) == [(b, IMG2), (a, IMG)]
    save(h, b, IMG2)
    # Found missing on Discord: not tried again
    h.store.add_image_file(ImageFile(a, IMG, None, None, h.service.now(), missing=True))
    assert not h.store.images_to_save(10, h.service.now())
    # Redacted images are still saved, for the team
    d = await h.add(BOB, DESC, [IMG2])
    await h.say(HELPER, f"~bug redact {d}")
    assert not h.store.get(d).images  # type: ignore[union-attr]
    assert h.store.images_to_save(10, h.service.now()) == [(d, IMG2)]


async def test_failed_downloads_wait_their_turn(h: Harness) -> None:
    old = await h.add(ALICE, DESC, [IMG])
    new = await h.add(ALICE, DESC, [IMG2])
    now = h.service.now()
    h.store.image_save_failed(new, IMG2, now)
    # Images never tried come first, so failing ones can't hold up the rest
    assert h.store.images_to_save(10, now) == [(old, IMG)]
    assert h.store.images_to_save(10, now + 3600) == [(old, IMG), (new, IMG2)]
    h.store.image_save_failed(new, IMG2, now + 3600)
    assert h.store.images_to_save(10, now + 2 * 3600) == [(old, IMG)]
    assert h.store.images_to_save(10, now + 3 * 3600) == [(old, IMG), (new, IMG2)]


async def test_redacted_images_are_never_posted(h: Harness) -> None:
    n = await h.add(ALICE, DESC, [IMG])
    path = save(h, n, IMG)
    h.service.check_postable(n)
    await h.say(HELPER, f"~bug redact {n}")
    with pytest.raises(Forbidden):
        h.service.check_postable(n)
    assert await h.say(TEAM, f"~bug reupload {n}") == [f"Bug #{n} is redacted, so its images are not posted"]
    # Redacted while a copy was being posted: refused, and the message is kept on the list
    # of the bot's messages to delete until Discord confirms
    assert not h.service.image_posted(n, IMG, "https://cdn.discordapp.com/attachments/20/9/x.png",
                                      path, 9)
    assert h.service.image_messages_to_delete() == [9]
    h.service.image_message_deleted(9)
    assert not h.service.image_messages_to_delete()
    # The team still sees them privately
    assert [f.url for f in h.service.redacted_images(h.actor(TEAM), h.store.get(n))] == [IMG]  # type: ignore[arg-type]
    with pytest.raises(Forbidden):
        h.service.redacted_images(h.actor(ALICE), h.store.get(n))  # type: ignore[arg-type]


async def test_redaction_deletes_the_bots_image_messages(h: Harness) -> None:
    n = await h.add(ALICE, DESC, [IMG])
    save(h, n, IMG)
    await h.say(TEAM, f"~bug reupload {n}")
    assert not h.service.image_messages_to_delete()
    await h.say(HELPER, f"~bug redact {n}")
    posted = [f.message_id for f in h.store.image_files(n) if f.message_id]
    assert posted and h.service.image_messages_to_delete() == posted


async def test_reupload(h: Harness) -> None:
    n = await h.add(ALICE, DESC, [IMG, IMG2])
    save(h, n, IMG)
    assert await h.say(ALICE, f"~bug reupload {n}") == ["You do not have permission to use this command"]
    replies = await h.say(TEAM, f"~bug reupload {n}")
    assert replies == [f"Image 2 of bug #{n} has no saved copy", f"Reuploaded 1 image of bug #{n}"]
    entry = h.store.get(n)
    assert entry is not None
    new_url = entry.images[0].url
    assert new_url != IMG and entry.images[1].url == IMG2
    # The copy points at the same file, and the change is in the history
    files = {f.url: f for f in h.store.image_files(n)}
    assert files[new_url].path == files[IMG].path and files[new_url].message_id is not None
    # ... and is listed once
    assert len(h.service.saved_images(h.actor(TEAM), entry)) == 1
    events = [e for e in h.store.events_for(n) if e.kind == "image"]
    assert len(events) == 1 and events[0].actor_id == TEAM


async def test_purge_deletes_files_and_image_messages(h: Harness) -> None:
    n = await h.add(ALICE, DESC, [IMG])
    path = save(h, n, IMG)
    await h.say(TEAM, f"~bug reupload {n}")
    image_message = next(f.message_id for f in h.store.image_files(n) if f.message_id)
    assert os.path.exists(h.service.archive.absolute(path))
    await h.say(LEAD, f"~bug purge {n} confirm")
    assert not os.path.exists(h.service.archive.absolute(str(n)))
    assert image_message in h.port.deleted
    assert not h.store.image_files(n)


async def test_api_images(h: Harness) -> None:
    n = await h.add(ALICE, DESC, [IMG])
    save(h, n, IMG, b"\x89PNG data")
    client = create_app(h.service, h.port, h.charts).test_client()
    headers = {"Authorization": f"Bearer {mint_token(h.service, TEAM, 24, 'read')[0]}"}
    resp = await client.get(f"/api/entries/{n}/images", headers=headers)
    body = await resp.get_json()
    assert body["images"] == [{"name": "111-shot.png", "url": IMG, "size": 9, "saved_at": h.service.now()}]
    resp = await client.get(f"/api/entries/{n}/images/111-shot.png", headers=headers)
    assert resp.status_code == 200 and await resp.get_data() == b"\x89PNG data"
    resp = await client.get(f"/api/entries/{n}/images/..%2Ftasks.db", headers=headers)
    assert resp.status_code == 404


async def test_a_redacted_entrys_images_are_for_the_team(h: Harness) -> None:
    n = await h.add(ALICE, DESC, [IMG])
    save(h, n, IMG, b"\x89PNG data")
    # A player through the game plugin, at the privilege the plugin grants
    client = create_app(h.service, h.port, h.charts, internal=True).test_client()
    token = mint_service_token(h.service, "shards-play", 2, 30)[0]

    async def statuses(privilege: int) -> list[int]:
        headers = {"Authorization": f"Bearer {token}", "X-Taskbot-Privilege": str(privilege),
                   "X-Taskbot-Player": "11111111-2222-3333-4444-555555555555"}
        return [(await client.get(path, headers=headers)).status_code
                for path in (f"/api/entries/{n}/images", f"/api/entries/{n}/images/111-shot.png")]
    assert await statuses(0) == [200, 200]
    await h.say(HELPER, f"~bug redact {n}")
    assert await statuses(0) == [403, 403]
    assert await statuses(2) == [200, 200]
