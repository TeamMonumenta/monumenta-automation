"""In-game reporting through a service token: players, context, notices."""

from typing import Any, Optional

import pytest
from quart import Quart

from conftest import ALICE, BOB, HELPER, LEAD, TEAM, Harness
from taskbot import tokens
from taskbot.api import create_app
from taskbot.tokens import mint_service_token, mint_token
from taskbot.identity import NoLinks, is_author
from taskbot.models import Actor
from taskbot.service import UserError

DESC = "the quest npc refuses to talk to me"
STEVE = "11111111-2222-3333-4444-555555555555"
ALEX = "66666666-7777-8888-9999-000000000000"
CONTEXT = {"location": {"server": "valley", "world": "Project_Epic-valley", "x": 1.5, "y": 64, "z": -3,
                        "yaw": 90, "pitch": 0}, "client": {"gamemode": "SURVIVAL"}}


class Game:
    """The game plugin's side: a service token, and requests made for players."""

    def __init__(self, h: Harness, max_privilege: int = 4):
        self.h = h
        self.app: Quart = create_app(h.service, h.port, h.charts, internal=True)
        self.token = mint_service_token(h.service, "shards-play", max_privilege, 3650)[0]

    async def call(self, method: str, path: str, player: Optional[str] = STEVE, name: str = "Steve",
                   privilege: int = 0, json: Any = None, token: Optional[str] = None,
                   **query: Any) -> tuple[int, Any]:
        headers = {"Authorization": f"Bearer {token or self.token}"}
        if player:
            headers.update({"X-Taskbot-Player": player, "X-Taskbot-Player-Name": name,
                            "X-Taskbot-Privilege": str(privilege)})
        resp = await self.app.test_client().open(path, method=method, headers=headers, json=json,
                                                 query_string=query or None)
        return resp.status_code, await resp.get_json()


@pytest.fixture
def game(h: Harness) -> Game:
    return Game(h)


async def test_player_reports_with_context(h: Harness, game: Game) -> None:
    status, body = await game.call("POST", "/api/entries",
                                   json={"description": DESC, "labels": ["quest"], "context": CONTEXT})
    assert status == 201
    assert body["author"] == {"kind": "minecraft", "uuid": STEVE, "name": "Steve"}
    e = h.store.get(body["id"])
    assert e is not None and e.author_id == 0 and e.author_mc_uuid == STEVE
    # The tracking channel shows the player's name; context stays out of it
    replies = await h.say(BOB, f"~bug get {e.id}")
    assert replies[0].startswith("`#1 [quest - N/A] Steve (in-game)`") and "valley" not in replies[0]
    sections = h.store.context_for(e.id)
    assert [s.section for s in sections] == ["location", "client"]
    assert sections[0].data["world"] == "Project_Epic-valley" and sections[0].source == "service:shards-play"
    ev = h.store.events_for(e.id)[0]
    assert ev.actor_id is None and ev.actor_mc_uuid == STEVE and ev.source == "api"


async def test_context_is_team_only(h: Harness, game: Game) -> None:
    await game.call("POST", "/api/entries", json={"description": DESC, "context": CONTEXT})
    status, _ = await game.call("GET", "/api/entries/1/context")             # a player
    assert status == 403
    status, body = await game.call("GET", "/api/entries/1/context", privilege=2)  # granted in game
    assert status == 200 and body["context"][0]["data"]["x"] == 1.5
    # Discord users: team yes, players no
    tok_team = mint_token(h.service, TEAM, 1, "write")[0]
    tok_bob = mint_token(h.service, BOB, 1, "write")[0]
    client = create_app(h.service, h.port, h.charts).test_client()
    assert (await client.get("/api/entries/1/context", headers={"Authorization": f"Bearer {tok_team}"})).status_code == 200
    assert (await client.get("/api/entries/1/context", headers={"Authorization": f"Bearer {tok_bob}"})).status_code == 403
    # Never in the feed channel: the text command points to the ephemeral slash command
    replies = await h.say(TEAM, "~bug context 1")
    assert replies == ["Context can include where players were, so it is only shown privately: "
                       "use `/bug context 1`"]
    assert await h.say(BOB, "~bug context 1") == ["You do not have permission to use this command"]
    team = Actor(id=TEAM, name="t", privilege=2)
    text = h.handler.context_text(team, "1")
    assert text[0].startswith("Context for bug #1:") and "Project_Epic-valley" in text[0]
    with pytest.raises(UserError):
        h.handler.context_text(Actor(id=BOB, name="b", privilege=0), "1")


async def test_discord_users_cannot_attach_context(h: Harness, game: Game) -> None:
    tok = mint_token(h.service, BOB, 1, "write")[0]
    resp = await game.app.test_client().post(
        "/api/entries", headers={"Authorization": f"Bearer {tok}"},
        json={"description": DESC, "context": {"location": {"x": 1}}})
    assert resp.status_code == 403


async def test_player_owns_their_reports(h: Harness, game: Game) -> None:
    await game.call("POST", "/api/entries", json={"description": DESC})
    # Another player can't append or reject it
    status, body = await game.call("POST", "/api/entries/1/append", player=ALEX, name="Alex",
                                   json={"text": "me too"})
    assert status == 403
    # The author can, without any granted privilege
    status, body = await game.call("POST", "/api/entries/1/append", json={"text": "also at night"})
    assert status == 200 and body["description"].endswith("also at night")
    status, body = await game.call("POST", "/api/entries/1/reject", json={"reason": "my mistake"})
    assert status == 200 and body["closed_by"] == {"kind": "minecraft", "uuid": STEVE, "name": "Steve"}
    assert not body["pending_notification"]
    e = h.store.get(1)
    assert e is not None and e.closed_by_mc_uuid == STEVE and e.closed_at is not None


async def test_privilege_is_capped_by_the_token(h: Harness) -> None:
    game = Game(h, max_privilege=1)
    await game.call("POST", "/api/entries", json={"description": DESC})
    status, _ = await game.call("POST", "/api/entries/1/fix", player=ALEX, name="Alex", privilege=4)
    assert status == 200  # 4 capped to 1, and level 1 may close
    await game.call("POST", "/api/entries", json={"description": DESC})
    status, _ = await game.call("PATCH", "/api/entries/2", player=ALEX, name="Alex", privilege=4,
                                json={"priority": "high"})
    assert status == 403  # priority needs level 2, the token allows at most 1


async def test_service_without_player_acts_as_itself(game: Game) -> None:
    status, body = await game.call("GET", "/api/info", player=None)
    # On its own behalf a service only reads: no privilege
    assert status == 200 and body["me"]["name"] == "shards-play" and body["me"]["privilege"] == 0
    status, _ = await game.call("GET", "/api/info", player="not-a-uuid")
    assert status == 400


async def test_my_reports_filter(game: Game) -> None:
    await game.call("POST", "/api/entries", json={"description": DESC})
    await game.call("POST", "/api/entries", player=ALEX, name="Alex", json={"description": DESC})
    _, body = await game.call("GET", "/api/entries", author_player="me")
    assert [e["id"] for e in body["entries"]] == [1]
    _, body = await game.call("GET", "/api/entries", author_player="alex")
    assert [e["id"] for e in body["entries"]] == [2]


async def test_in_game_notices(h: Harness, game: Game) -> None:
    await game.call("POST", "/api/entries", json={"description": DESC})
    await game.call("POST", "/api/entries", player=ALEX, name="Alex", json={"description": DESC})
    status, _ = await game.call("POST", f"/api/players/{ALEX}/settings", player=ALEX,
                                json={"notifications": False})
    assert status == 200
    await h.say(TEAM, "~bug fix 1 thanks")
    await h.say(TEAM, "~bug fix 2")
    replies = await h.say(TEAM, "~bug send_notifications")
    assert replies[-1] == ("2 notifications processed successfully, 1 of which were suppressed by user "
                           "opt-out, 0 of which could not find a user to ping, 1 of which were queued "
                           "for in-game delivery")
    # One player's request can't take another's notices
    status, _ = await game.call("POST", f"/api/players/{STEVE}/notices/take", player=ALEX, name="Alex")
    assert status == 403
    status, body = await game.call("POST", f"/api/players/{STEVE}/notices/take")
    assert status == 200 and [n["text"] for n in body["notices"]] == ["Your bug #1 was closed (fixed): thanks"]
    # Taken once: they are delivered
    _, body = await game.call("POST", f"/api/players/{STEVE}/notices/take")
    assert body["notices"] == []
    _, body = await game.call("POST", f"/api/players/{ALEX}/notices/take", player=ALEX, name="Alex")
    assert body["notices"] == []  # Alex opted out
    # Player routes are for services only
    tok = mint_token(h.service, TEAM, 1, "write")[0]
    resp = await game.app.test_client().post(f"/api/players/{STEVE}/notices/take",
                                              headers={"Authorization": f"Bearer {tok}"})
    assert resp.status_code == 403


async def test_taking_notices_is_not_rate_limited(game: Game) -> None:
    for _ in range(25):   # more joins than the per-minute budget for changes
        status, _ = await game.call("POST", f"/api/players/{STEVE}/notices/take")
        assert status == 200
    status, _ = await game.call("POST", "/api/entries", json={"description": DESC})
    assert status == 201


async def test_in_game_players_in_statistics_and_history(h: Harness, game: Game) -> None:
    for _ in range(3):
        await h.add(ALICE, "quest " + DESC)
    await game.call("POST", "/api/entries", json={"description": DESC})
    await game.call("POST", "/api/entries/1/fix", player=ALEX, name="Alex", privilege=1)
    await game.call("POST", "/api/entries/2/fix", player=ALEX, name="Alex", privilege=1)
    await h.say(HELPER, "~bug fix 3")
    text = "".join(await h.say(TEAM, "~bug cstats 0 1"))
    line = next(line for line in text.splitlines() if line.startswith("Alex (in-game)"))
    assert line.split()[2:] == ["2", "0", "0", "2"]
    history = "\n".join(await h.say(TEAM, "~bug history 1"))
    assert "**Alex (in-game)** closed as **fixed**" in history and "(via api)" in history
    tok = mint_token(h.service, TEAM, 1, "write")[0]
    public = create_app(h.service, h.port, h.charts).test_client()
    resp = await public.get("/api/stats/authors", headers={"Authorization": f"Bearer {tok}"})
    users = [a["user"] for a in (await resp.get_json())["authors"]]
    assert {"kind": "minecraft", "uuid": STEVE, "name": "Steve"} in users


async def test_redaction_keeps_context_and_purge_removes_it(h: Harness, game: Game) -> None:
    await game.call("POST", "/api/entries", json={"description": DESC, "context": CONTEXT})
    await h.say(HELPER, "~bug redact 1")
    assert h.store.context_for(1) != []
    await h.say(LEAD, "~bug purge 1 confirm")
    assert h.store.conn.execute("SELECT COUNT(*) FROM entry_context").fetchone()[0] == 0


def test_identity_links_are_one_seam() -> None:
    """A future account link only has to implement LinkResolver."""
    class Linked(NoLinks):
        def discord_for_player(self, mc_uuid: str) -> Optional[int]:
            return ALICE if mc_uuid == STEVE else None

    from taskbot.models import Entry
    reported_in_game = Entry(id=1, description="x", author_id=0, priority="N/A", complexity="unknown",
                             labels=["misc"], author_mc_uuid=STEVE)
    alice_on_discord = Actor(id=ALICE, name="Alice", privilege=0)
    assert not is_author(alice_on_discord, reported_in_game, NoLinks())
    assert is_author(alice_on_discord, reported_in_game, Linked())
    reported_on_discord = Entry(id=2, description="x", author_id=ALICE, priority="N/A",
                                complexity="unknown", labels=["misc"])
    steve_in_game = Actor(id=0, name="Steve", privilege=0, mc_uuid=STEVE)
    assert is_author(steve_in_game, reported_on_discord, Linked())


def test_tokens_cli(h: Harness, capsys: pytest.CaptureFixture[str]) -> None:
    db = h.config.db_file
    assert tokens.main(["--db", db, "create", "shards-play", "--max-privilege", "2"]) == 0
    out, err = capsys.readouterr()
    assert out.startswith("tbs_") and "max privilege 2" in err
    tokens.main(["--db", db, "list"])
    assert "shards-play" in capsys.readouterr().out
    assert tokens.main(["--db", db, "create", "Bad Name"]) == 1
    tokens.main(["--db", db, "revoke", "shards-play"])
    assert "Revoked 1" in capsys.readouterr().out


async def test_service_tokens_refused_outside_the_cluster(h: Harness, game: Game) -> None:
    public = create_app(h.service, h.port, h.charts)  # what the ingress reaches
    resp = await public.test_client().get("/api/info", headers={"Authorization": f"Bearer {game.token}"})
    assert resp.status_code == 403
    assert "internal" in (await resp.get_json())["error"]
    # ... and Discord users' tokens only there
    tok = mint_token(h.service, TEAM, 1, "write")[0]
    resp = await public.test_client().get("/api/info", headers={"Authorization": f"Bearer {tok}"})
    assert resp.status_code == 200
    resp = await game.app.test_client().get("/api/info", headers={"Authorization": f"Bearer {tok}"})
    assert resp.status_code == 403 and "public port" in (await resp.get_json())["error"]


async def test_bare_service_token_cannot_change_anything(h: Harness, game: Game) -> None:
    await h.add(ALICE, "quest " + DESC)
    status, _ = await game.call("POST", "/api/entries/1/redact", player=None)
    assert status == 403
    status, _ = await game.call("POST", "/api/entries/1/fix", player=None)
    assert status == 403
    status, _ = await game.call("POST", "/api/entries", player=None, json={"description": DESC})
    assert status == 403 and h.store.get(2) is None


async def test_context_only_on_own_reports(game: Game) -> None:
    await game.call("POST", "/api/entries", player=ALEX, name="Alex", json={"description": DESC})
    status, _ = await game.call("POST", "/api/entries/1/context", json={"extra": {"a": 1}})
    assert status == 403  # Steve, on Alex's report
    status, _ = await game.call("POST", "/api/entries/1/context", player=ALEX, name="Alex",
                                json={"extra": {"a": 1}})
    assert status == 201
    status, body = await game.call("POST", "/api/entries/1/context", player=ALEX, name="Alex",
                                   json={"bad": [1, 2]})
    assert status == 400 and "JSON object" in body["error"]


async def test_context_size_is_capped_per_entry(game: Game) -> None:
    await game.call("POST", "/api/entries", json={"description": DESC})
    blob = {"data": "x" * 6_000_000}  # 6 MB
    status, _ = await game.call("POST", "/api/entries/1/context", json={"a": blob})
    assert status == 201
    status, body = await game.call("POST", "/api/entries/1/context", json={"b": blob})
    assert status == 400 and "MB (bytes of JSON) of context" in body["error"]


async def test_reassigning_author_removes_in_game_owner(h: Harness, game: Game) -> None:
    await game.call("POST", "/api/entries", json={"description": DESC})
    await h.say(TEAM, "~bug edit 1 author alice")
    e = h.store.get(1)
    assert e is not None and e.author_id == ALICE and e.author_mc_uuid is None
    status, _ = await game.call("POST", "/api/entries/1/append", json={"text": "still mine?"})
    assert status == 403


async def test_me_for_players(game: Game) -> None:
    await game.call("POST", "/api/entries", json={"description": DESC})
    await game.call("POST", "/api/entries", player=ALEX, name="Alex", json={"description": DESC})
    _, body = await game.call("GET", "/api/entries", author="me")
    assert [e["id"] for e in body["entries"]] == [1]
    status, _ = await game.call("GET", "/api/entries", closed_by="me")
    assert status == 400
    status, _ = await game.call("POST", "/api/entries/1/assign", privilege=2)
    assert status == 400


async def test_reads_do_not_rename_and_read_only_cannot_change_settings(h: Harness, game: Game) -> None:
    await game.call("POST", "/api/entries", json={"description": DESC})
    await game.call("GET", "/api/entries/1", name="Notch")
    assert h.store.player_name(STEVE) == "Steve"
    ro = mint_service_token(h.service, "reader", 2, 1, "read")[0]
    status, _ = await game.call("POST", f"/api/players/{STEVE}/settings", token=ro,
                                json={"notifications": False})
    assert status == 403


async def test_player_write_rate_limit(h: Harness, game: Game) -> None:
    await game.call("POST", "/api/entries", json={"description": DESC})
    statuses = [(await game.call("POST", "/api/entries/1/append", json={"text": f"note {i}"}))[0]
                for i in range(25)]
    assert statuses.count(429) >= 5 and statuses[0] == 200
    h.clock.advance(61)
    assert (await game.call("POST", "/api/entries/1/append", json={"text": "later"}))[0] == 200


async def test_discord_users_dont_own_in_game_reports(h: Harness, game: Game) -> None:
    await game.call("POST", "/api/entries", json={"description": DESC})
    assert await h.say(ALICE, "~bug append 1 more about it") == ["You do not have permission to append to #1"]
    assert await h.say(ALICE, "~bug reject 1 nevermind") == ["You do not have permission to reject #1"]
    assert (await game.call("POST", "/api/entries/1/append", json={"text": "more about it"}))[0] == 200
