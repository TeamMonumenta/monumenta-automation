"""The /api/* routes through Quart's test client."""

from typing import Any, Optional

import pytest
from quart import Quart

from conftest import ALICE, BOB, HELPER, LEAD, OUTSIDER, TEAM, Harness
from taskbot.api import create_app
from taskbot.tokens import mint_token

DESC = "the quest npc refuses to talk to me"


class Api:
    def __init__(self, h: Harness):
        self.h = h
        self.app: Quart = create_app(h.service, h.port, h.charts)
        self.tokens: dict[int, str] = {}

    def token(self, user_id: int, scope: str = "write") -> str:
        key = user_id if scope == "write" else -user_id
        if key not in self.tokens:
            self.tokens[key] = mint_token(self.h.service, user_id, 24, scope)[0]
        return self.tokens[key]

    async def call(self, method: str, path: str, user: Optional[int] = TEAM, json: Any = None,
                   scope: str = "write", **query: Any) -> tuple[int, Any]:
        client = self.app.test_client()
        headers = {"Authorization": f"Bearer {self.token(user, scope)}"} if user else {}
        resp = await client.open(path, method=method, headers=headers, json=json,
                                 query_string=query or None)
        if resp.mimetype == "application/json":
            return resp.status_code, await resp.get_json()
        return resp.status_code, await resp.get_data()


@pytest.fixture
def api(h: Harness) -> Api:
    return Api(h)


async def test_health_needs_no_token(api: Api) -> None:
    assert await api.call("GET", "/api/health", user=None) == (200, {"ok": True})


async def test_auth_failures(api: Api) -> None:
    status, body = await api.call("GET", "/api/info", user=None)
    assert status == 401 and body["error"] == "missing Authorization: Bearer token"
    client = api.app.test_client()
    resp = await client.get("/api/info", headers={"Authorization": "Bearer nope"})
    assert resp.status_code == 401 and resp.headers["WWW-Authenticate"] == "Bearer"
    status, body = await api.call("GET", "/api/info", user=OUTSIDER)
    assert status == 403
    # Only the team (privilege 2) uses the API; players reach it through the game plugin
    for user in (ALICE, HELPER):
        status, body = await api.call("GET", "/api/info", user=user)
        assert status == 403 and "team members" in body["error"]
    # Expired
    tok = api.token(BOB)
    api.h.clock.advance(25 * 3600)
    resp = await client.get("/api/info", headers={"Authorization": f"Bearer {tok}"})
    assert resp.status_code == 401
    # Revoked
    api.h.clock.advance(-25 * 3600)
    api.h.store.revoke_tokens(BOB)
    resp = await client.get("/api/info", headers={"Authorization": f"Bearer {tok}"})
    assert resp.status_code == 401
    # Errors are JSON, unknown routes too
    status, body = await api.call("GET", "/api/whatever")
    assert status == 404 and "error" in body


async def test_only_hash_is_stored(api: Api) -> None:
    tok = api.token(ALICE)
    rows = api.h.store.conn.execute("SELECT token_hash FROM api_tokens").fetchall()
    assert tok not in repr(rows) and len(rows) == 1


async def test_info(api: Api) -> None:
    status, body = await api.call("GET", "/api/info", user=TEAM)
    assert status == 200
    assert body["descriptor"]["plural"] == "bugs" and body["me"]["privilege"] == 2
    assert body["labels"][0] == "boss" and "backlog" in body["charts"]
    assert body["resolutions"] == {"fixed": "fixed", "rejected": "rejected", "duplicate": "duplicate"}


async def test_create_list_get(api: Api) -> None:
    status, body = await api.call("POST", "/api/entries", json={"description": DESC, "labels": ["qu"]})
    assert status == 201 and body["id"] == 1 and body["labels"] == ["quest"]
    assert body["author"] == {"kind": "discord", "id": str(TEAM), "name": "Teammate"} and body["status"] == "open"
    status, body = await api.call("POST", "/api/entries", json={"description": "too short"})
    assert status == 400
    status, body = await api.call("POST", "/api/entries", json={"description": DESC + " @everyone"})
    assert status == 400 and "pings" in body["error"]
    await api.call("POST", "/api/entries", json={"description": DESC + " two", "labels": "boss"})

    status, body = await api.call("GET", "/api/entries")
    assert status == 200 and body["total"] == 2 and [e["id"] for e in body["entries"]] == [1, 2]
    status, body = await api.call("GET", "/api/entries", label="boss")
    assert [e["id"] for e in body["entries"]] == [2]
    status, body = await api.call("GET", "/api/entries", q="TWO")
    assert [e["id"] for e in body["entries"]] == [2]
    status, body = await api.call("GET", "/api/entries", author="me", limit=1, order="desc")
    assert body["total"] == 2 and [e["id"] for e in body["entries"]] == [2]
    status, body = await api.call("GET", "/api/entries", label="nonsense")
    assert status == 400 and "unknown label" in body["error"]
    status, body = await api.call("GET", "/api/entries", sort="bogus")
    assert status == 400

    status, body = await api.call("GET", "/api/entries/1", text="1")
    assert status == 200 and body["text"].startswith("`#1 [quest - N/A] Teammate`")
    status, body = await api.call("GET", "/api/entries/99")
    assert status == 404 and body == {"error": "Bug #99 not found"}


async def test_privileges_match_discord(api: Api) -> None:
    await api.h.add(ALICE, "quest " + DESC)
    status, body = await api.call("PATCH", "/api/entries/1", user=TEAM,
                                  json={"priority": "high", "complexity": "hard", "labels": "boss,mob"})
    assert status == 200 and body["priority"] == "High" and body["labels"] == ["boss", "mob"]
    assert body["pending_notification"]
    status, body = await api.call("POST", "/api/entries/1/reject", user=TEAM, json={"reason": "no"})
    assert status == 200 and body["resolution"] == "rejected" and body["closed_by"]["id"] == str(TEAM)
    status, body = await api.call("POST", "/api/entries/1/reopen", user=TEAM)
    assert status == 200 and body["status"] == "open"
    status, body = await api.call("POST", "/api/entries/1/assign", user=TEAM, json={"user": "bobb"})
    assert status == 200 and body["assignee"]["id"] == str(BOB)
    status, body = await api.call("POST", "/api/entries/1/unassign", user=TEAM)
    assert status == 200
    status, body = await api.call("POST", "/api/entries/1/unassign", user=TEAM)
    assert status == 409


async def test_read_only_tokens(api: Api) -> None:
    await api.call("POST", "/api/entries", user=TEAM, json={"description": DESC})
    status, _ = await api.call("GET", "/api/entries/1", user=TEAM, scope="read")
    assert status == 200
    status, body = await api.call("POST", "/api/entries/1/fix", user=TEAM, scope="read")
    assert status == 403 and body["error"] == "This API token is read-only"


async def test_dupe_redact_and_events(api: Api) -> None:
    await api.call("POST", "/api/entries", json={"description": DESC})
    await api.call("POST", "/api/entries", json={"description": DESC + " again"})
    status, body = await api.call("POST", "/api/entries/2/dupe", user=TEAM, json={"of": "#1"})
    assert status == 200 and body["duplicate_of"] == 1 and body["close_reason"] == "Duplicate of #1"
    status, body = await api.call("POST", "/api/entries/1/redact", user=TEAM)
    assert status == 200 and body["redacted"] and body["description"] == "redacted"
    status, body = await api.call("GET", "/api/entries/1/redacted", user=TEAM, scope="read")
    assert status == 200 and body["description"] == DESC and body["redacted_by"] == TEAM
    status, body = await api.call("GET", "/api/entries/2/redacted", user=TEAM)
    assert status == 404
    status, body = await api.call("GET", "/api/entries/2/events")
    assert [e["kind"] for e in body["events"]] == ["created", "closed"]
    assert body["events"][1]["source"] == "api" and body["events"][1]["actor"]["id"] == str(TEAM)
    status, body = await api.call("GET", "/api/events", kind="closed")
    assert len(body["events"]) == 1


async def test_stats_and_closers(api: Api) -> None:
    await api.h.add(ALICE, "quest " + DESC)
    await api.h.add(ALICE, "quest " + DESC)
    await api.call("POST", "/api/entries", json={"description": DESC})
    await api.call("POST", "/api/entries/1/fix", user=TEAM)
    await api.call("POST", "/api/entries/2/fix", user=LEAD)
    await api.call("POST", "/api/entries/3/reject", user=TEAM, json={"reason": "oops"})
    status, body = await api.call("GET", "/api/stats")
    assert status == 200 and body["open"] == 0 and body["closed"] == 3 and body["closed_by_resolution"]["fixed"] == 2
    status, body = await api.call("GET", "/api/stats/closers", days=7)
    assert {c["user"]["id"] for c in body["closers"]} == {str(TEAM), str(LEAD)}
    assert body["self_closes"] == 1
    status, body = await api.call("GET", "/api/stats/authors")
    assert body["authors"][0]["total"] == 2


async def test_charts(api: Api) -> None:
    await api.call("POST", "/api/entries", json={"description": DESC})
    status, png = await api.call("GET", "/api/charts/intake.png", options="week 30d")
    assert status == 200 and png[:4] == b"\x89PNG"
    status, body = await api.call("GET", "/api/charts/closers.json")
    assert status == 200 and body["kind"] == "hbar_stacked"
    status, body = await api.call("GET", "/api/charts/nope.png")
    assert status == 404
    status, body = await api.call("GET", "/api/charts/intake.png", options="sideways")
    assert status == 400
    status, body = await api.call("GET", "/api/charts/backlog.json", options="plugin priority")
    assert status == 200 and body["title"].startswith("Open bugs labeled plugin by priority")
    status, body = await api.call("GET", "/api/charts/closes.json", options="plugin")
    assert status == 400


async def test_resolution_filter_by_display_name(api: Api) -> None:
    api.h.config.resolution_names = {"fixed": "implemented"}
    api.app = create_app(api.h.service, api.h.port, api.h.charts)
    await api.call("POST", "/api/entries", json={"description": DESC})
    await api.call("POST", "/api/entries/1/fix", user=TEAM)
    for word in ("implemented", "imp", "fixed"):
        status, body = await api.call("GET", "/api/entries", status="all", resolution=word)
        assert status == 200 and body["total"] == 1, word
        assert body["entries"][0]["resolution_name"] == "implemented"
    status, body = await api.call("GET", "/api/entries", resolution="nah")
    assert status == 400 and "implemented" in body["error"]


async def test_stored_users_must_exist(api: Api) -> None:
    await api.call("POST", "/api/entries", json={"description": DESC})
    status, body = await api.call("PATCH", "/api/entries/1", user=TEAM, json={"author": "999"})
    assert status == 400 and "not found" in body["error"]
    status, _ = await api.call("POST", "/api/entries/1/assign", user=TEAM, json={"user": "0"})
    assert status == 400
    # Filters still accept ids of users Discord doesn't know (old authors who left)
    status, body = await api.call("GET", "/api/entries", author="999")
    assert status == 200 and body["total"] == 0


async def test_reclose_needs_force(api: Api) -> None:
    await api.call("POST", "/api/entries", json={"description": DESC})
    await api.call("POST", "/api/entries/1/fix", user=TEAM)
    status, body = await api.call("POST", "/api/entries/1/reject", user=LEAD, json={"reason": "no"})
    assert status == 409 and "already closed" in body["error"]
    status, body = await api.call("POST", "/api/entries/1/reject", user=LEAD,
                                  json={"reason": "no", "force": True})
    assert status == 200 and body["closed_by"]["id"] == str(LEAD)
    status, _ = await api.call("POST", "/api/entries/1/fix", user=LEAD, json={"force": "false"})
    assert status == 400


async def test_bad_input_is_refused_and_changes_nothing(api: Api) -> None:
    await api.call("POST", "/api/entries", json={"description": DESC})
    for path, body in (("/api/entries", {"description": DESC, "labels": 5}),
                       ("/api/entries", {"description": 7}),
                       ("/api/entries", {"description": DESC + " \x1b]52;c;ZXZpbA==\x07"}),
                       ("/api/entries/1/fix", {"reason": "x" * 1001}),
                       ("/api/entries/1/dupe", {"of": "99999999999999999999"})):
        status, _ = await api.call("POST", path, json=body)
        assert status in (400, 404), (path, body, status)
    # One field refused: none of them change
    status, _ = await api.call("PATCH", "/api/entries/1", json={"priority": "high", "description": "x" * 2000})
    assert status == 400
    _, entry = await api.call("GET", "/api/entries/1")
    assert entry["priority"] == "N/A" and [ev.kind for ev in api.h.store.events_for(1)] == ["created"]


async def test_assignment_events_name_users(api: Api) -> None:
    await api.call("POST", "/api/entries", json={"description": DESC})
    await api.call("POST", "/api/entries/1/assign", user=TEAM, json={"user": "bobb"})
    _, body = await api.call("GET", "/api/entries/1/events")
    assert body["events"][-1]["new_user"] == {"kind": "discord", "id": str(BOB), "name": "Bob"}
