from fastapi.testclient import TestClient

from app.storage.memory import MemoryStore
from tests.conftest import bearer
from tests.factories import contestant, season

OWNER = bearer(sub="auth0|owner")
FRIEND = bearer(sub="auth0|friend")
STRANGER = bearer(sub="auth0|stranger")


def seed(store: MemoryStore) -> None:
    store.put_season(season("s49"))
    for cid in ("amy", "bob", "cal", "dee"):
        store.put_contestant(contestant(cid))


def create(client: TestClient, **overrides: object) -> dict[str, object]:
    body = {"season_id": "s49", "name": "Jeff's League", "display_name": "Jeff", **overrides}
    response = client.post("/leagues", json=body, headers=OWNER)
    assert response.status_code == 201, response.text
    result: dict[str, object] = response.json()
    return result


def test_create_league_makes_owner_a_member(client: TestClient, store: MemoryStore) -> None:
    seed(store)

    league = create(client)

    assert str(league["id"]).startswith("jeff-s-league-")
    assert league["is_owner"] is True
    assert isinstance(league["join_code"], str) and len(league["join_code"]) == 8
    assert league["roster_size"] == 3 and league["draft_open"] is True

    mine = client.get("/leagues", headers=OWNER).json()
    assert [lg["id"] for lg in mine] == [league["id"]]
    members = client.get(f"/leagues/{league['id']}/members", headers=OWNER).json()
    assert members == [
        {
            "league_id": league["id"],
            "user_id": "auth0|owner",
            "display_name": "Jeff",
            "contestant_ids": [],
        }
    ]


def test_create_requires_existing_season(client: TestClient, store: MemoryStore) -> None:
    body = {"season_id": "nope", "name": "X", "display_name": "Jeff"}
    assert client.post("/leagues", json=body, headers=OWNER).status_code == 404


def test_leagues_are_private_to_members(client: TestClient, store: MemoryStore) -> None:
    seed(store)
    league_id = create(client)["id"]

    for path in ("", "/members", "/leaderboard", "/scoring-rules"):
        response = client.get(f"/leagues/{league_id}{path}", headers=STRANGER)
        assert response.status_code == 403, path
    assert client.get("/leagues", headers=STRANGER).json() == []
    assert client.get("/leagues/does-not-exist", headers=STRANGER).status_code == 404


def test_join_with_code_hides_code_from_members(client: TestClient, store: MemoryStore) -> None:
    seed(store)
    league = create(client)
    url = f"/leagues/{league['id']}/members"

    wrong = client.post(url, json={"join_code": "NOPE", "display_name": "F"}, headers=FRIEND)
    assert wrong.status_code == 403

    joined = client.post(
        url, json={"join_code": league["join_code"], "display_name": "Friend"}, headers=FRIEND
    )
    assert joined.status_code == 200
    assert joined.json()["display_name"] == "Friend"

    # Joining twice keeps the existing membership (and roster).
    again = client.post(
        url, json={"join_code": league["join_code"], "display_name": "Renamed"}, headers=FRIEND
    )
    assert again.json()["display_name"] == "Friend"

    seen = client.get(f"/leagues/{league['id']}", headers=FRIEND).json()
    assert seen["is_owner"] is False and seen["join_code"] is None
    assert [lg["id"] for lg in client.get("/leagues", headers=FRIEND).json()] == [league["id"]]


def test_only_owner_updates_settings(client: TestClient, store: MemoryStore) -> None:
    seed(store)
    league = create(client)
    client.post(
        f"/leagues/{league['id']}/members",
        json={"join_code": league["join_code"], "display_name": "Friend"},
        headers=FRIEND,
    )

    denied = client.patch(f"/leagues/{league['id']}", json={"name": "Hijacked"}, headers=FRIEND)
    assert denied.status_code == 403

    updated = client.patch(
        f"/leagues/{league['id']}",
        json={"name": "Renamed", "roster_size": 2, "scoring_overrides": {"sole_survivor": 100}},
        headers=OWNER,
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Renamed"
    assert updated.json()["roster_size"] == 2
    assert updated.json()["scoring_overrides"] == {"sole_survivor": 100}

    rules = client.get(f"/leagues/{league['id']}/scoring-rules", headers=FRIEND).json()
    assert rules["points"]["sole_survivor"] == 100
    assert rules["points"]["individual_immunity"] == 10

    bad = client.patch(f"/leagues/{league['id']}", json={"owner_id": "me"}, headers=OWNER)
    assert bad.status_code == 422


def test_roster_rules(client: TestClient, store: MemoryStore) -> None:
    seed(store)
    league = create(client)
    url = f"/leagues/{league['id']}/members/me/roster"

    assert client.put(url, json={"contestant_ids": ["amy"]}, headers=STRANGER).status_code == 403

    too_few = client.put(url, json={"contestant_ids": ["amy"]}, headers=OWNER)
    assert too_few.status_code == 409 and "exactly 3" in too_few.json()["detail"]

    unknown = client.put(url, json={"contestant_ids": ["amy", "bob", "zed"]}, headers=OWNER)
    assert unknown.status_code == 409
    assert unknown.json() == {"detail": "unknown contestants: zed"}

    duplicate = client.put(url, json={"contestant_ids": ["amy", "amy", "bob"]}, headers=OWNER)
    assert duplicate.status_code == 422

    ok = client.put(url, json={"contestant_ids": ["amy", "bob", "cal"]}, headers=OWNER)
    assert ok.status_code == 200
    assert ok.json()["contestant_ids"] == ["amy", "bob", "cal"]
    me = client.get(f"/leagues/{league['id']}/members/me", headers=OWNER).json()
    assert me["contestant_ids"] == ["amy", "bob", "cal"]

    client.patch(f"/leagues/{league['id']}", json={"draft_open": False}, headers=OWNER)
    closed = client.put(url, json={"contestant_ids": ["amy", "bob", "dee"]}, headers=OWNER)
    assert closed.status_code == 409
    assert closed.json() == {"detail": "the draft for this league is closed"}


def test_leaderboard_uses_league_rules_over_shared_truth(
    client: TestClient, store: MemoryStore, admin_headers: dict[str, str]
) -> None:
    seed(store)
    standard = create(client, name="Standard")
    custom = create(client, name="Custom", scoring_overrides={"individual_immunity": 50})
    for lg in (standard, custom):
        client.put(
            f"/leagues/{lg['id']}/members/me/roster",
            json={"contestant_ids": ["amy", "bob", "cal"]},
            headers=OWNER,
        )
        client.post(
            f"/leagues/{lg['id']}/members",
            json={"join_code": lg["join_code"], "display_name": "Friend"},
            headers=FRIEND,
        )
    client.put(
        f"/leagues/{standard['id']}/members/me/roster",
        json={"contestant_ids": ["bob", "cal", "dee"]},
        headers=FRIEND,
    )
    # One truth, entered once by the commissioner.
    client.put(
        "/seasons/s49/episodes/1/stats/amy",
        json={"events": {"survived_episode": 1, "individual_immunity": 1}},
        headers=admin_headers,
    )
    client.put(
        "/seasons/s49/episodes/1/stats/dee",
        json={"events": {"voted_out": 1}},
        headers=admin_headers,
    )

    standard_board = client.get(f"/leagues/{standard['id']}/leaderboard", headers=FRIEND).json()
    assert standard_board == [
        {
            "rank": 1,
            "user_id": "auth0|owner",
            "display_name": "Jeff",
            "points": 12,
            "contestant_points": {"amy": 12, "bob": 0, "cal": 0},
        },
        {
            "rank": 2,
            "user_id": "auth0|friend",
            "display_name": "Friend",
            "points": -5,
            "contestant_points": {"bob": 0, "cal": 0, "dee": -5},
        },
    ]

    custom_board = client.get(f"/leagues/{custom['id']}/leaderboard", headers=OWNER).json()
    assert custom_board[0]["points"] == 52  # 2 survived + 50 immunity under this league's rules
    assert custom_board[1] == {
        "rank": 2,
        "user_id": "auth0|friend",
        "display_name": "Friend",
        "points": 0,
        "contestant_points": {},
    }

    shared = client.get("/seasons/s49/points", headers=FRIEND).json()
    assert shared == {"points": {"amy": 12, "dee": -5}}
