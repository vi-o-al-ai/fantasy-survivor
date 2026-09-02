from fastapi.testclient import TestClient

from app.storage.memory import MemoryStore
from tests.conftest import bearer
from tests.factories import contestant, season

SEASON = {"name": "Survivor 49", "number": 49}


def test_seasons_require_auth(client: TestClient) -> None:
    assert client.get("/seasons").status_code == 401


def test_player_cannot_manage_seasons(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.put("/seasons/s49", json=SEASON, headers=auth_headers)

    assert response.status_code == 403
    assert response.json() == {"detail": "requires manage:seasons"}


def test_admin_creates_and_lists_seasons(
    client: TestClient, admin_headers: dict[str, str], auth_headers: dict[str, str]
) -> None:
    created = client.put("/seasons/s49", json=SEASON, headers=admin_headers)
    assert created.status_code == 200
    assert created.json() == {
        "id": "s49",
        "name": "Survivor 49",
        "number": 49,
        "roster_size": 3,
        "draft_open": True,
    }

    listed = client.get("/seasons", headers=auth_headers)
    assert [s["id"] for s in listed.json()] == ["s49"]
    assert client.get("/seasons/s49", headers=auth_headers).json()["name"] == "Survivor 49"


def test_unknown_season_is_404(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.get("/seasons/nope", headers=auth_headers)

    assert response.status_code == 404
    assert response.json() == {"detail": "season 'nope' not found"}


def test_season_id_must_be_slug(client: TestClient, admin_headers: dict[str, str]) -> None:
    assert client.put("/seasons/Bad Id", json=SEASON, headers=admin_headers).status_code == 422


def test_body_rejects_unknown_fields(client: TestClient, admin_headers: dict[str, str]) -> None:
    body = {**SEASON, "id": "sneaky"}
    assert client.put("/seasons/s49", json=body, headers=admin_headers).status_code == 422


def test_contestants(client: TestClient, store: MemoryStore, admin_headers: dict[str, str]) -> None:
    store.put_season(season("s49"))

    missing_season = client.put(
        "/seasons/s48/contestants/bob", json={"name": "Bob"}, headers=admin_headers
    )
    assert missing_season.status_code == 404

    created = client.put(
        "/seasons/s49/contestants/bob", json={"name": "Bob", "tribe": "Vati"}, headers=admin_headers
    )
    assert created.status_code == 200
    assert created.json()["status"] == "active"

    listed = client.get("/seasons/s49/contestants", headers=admin_headers)
    assert [c["id"] for c in listed.json()] == ["bob"]


def test_contestant_points_and_rules(
    client: TestClient, store: MemoryStore, auth_headers: dict[str, str]
) -> None:
    store.put_season(season("s49"))
    store.put_contestant(contestant("bob"))

    rules = client.get("/scoring-rules", headers=auth_headers)
    assert rules.status_code == 200
    assert rules.json()["points"]["sole_survivor"] == 30

    points = client.get("/seasons/s49/points", headers=auth_headers)
    assert points.status_code == 200
    assert points.json() == {"points": {}}


def test_permission_scoping_is_per_permission(client: TestClient, store: MemoryStore) -> None:
    store.put_season(season("s49"))
    store.put_contestant(contestant("bob"))
    stats_only = bearer(sub="auth0|scorer", permissions=["write:stats"])

    assert client.put("/seasons/s49", json=SEASON, headers=stats_only).status_code == 403
    ok = client.put("/seasons/s49/episodes/1/stats/bob", json={"events": {}}, headers=stats_only)
    assert ok.status_code == 200
