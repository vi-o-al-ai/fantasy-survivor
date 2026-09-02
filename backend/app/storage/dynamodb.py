"""DynamoDB single-table store.

Key design (one table, ``PK``/``SK`` strings, no GSIs yet):

    Item          PK                 SK
    ------------  -----------------  ----------------------------
    Season        SEASONS            SEASON#<season_id>
    Contestant    SEASON#<sid>       CONTESTANT#<contestant_id>
    EpisodeStat   SEASON#<sid>       STAT#EP<episode:03d>#<contestant_id>
    Roster        SEASON#<sid>       ROSTER#<user_id>

Everything for a season shares one partition, so "load the season" is one
query and per-type listings are ``begins_with`` on the sort key. Episode
numbers are zero-padded so stats sort in air order. Entity fields are
stored flat next to the keys, plus a ``type`` attribute for debugging.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

import boto3
from boto3.dynamodb.conditions import Key
from pydantic import BaseModel

from app.domain.models import Contestant, EpisodeStat, Roster, Season

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import Table

M = TypeVar("M", bound=BaseModel)

SEASONS_PK = "SEASONS"
KEY_SCHEMA: list[dict[str, str]] = [
    {"AttributeName": "PK", "KeyType": "HASH"},
    {"AttributeName": "SK", "KeyType": "RANGE"},
]
ATTRIBUTE_DEFINITIONS: list[dict[str, str]] = [
    {"AttributeName": "PK", "AttributeType": "S"},
    {"AttributeName": "SK", "AttributeType": "S"},
]


def season_pk(season_id: str) -> str:
    return f"SEASON#{season_id}"


def stat_sk(episode: int, contestant_id: str) -> str:
    return f"STAT#EP{episode:03d}#{contestant_id}"


class DynamoDBStore:
    def __init__(self, table_name: str, *, region: str, endpoint_url: str | None = None) -> None:
        resource = boto3.resource("dynamodb", region_name=region, endpoint_url=endpoint_url)
        self._table: Table = resource.Table(table_name)

    # --- helpers ----------------------------------------------------------

    def _put(self, pk: str, sk: str, entity: BaseModel) -> None:
        item: dict[str, Any] = {
            "PK": pk,
            "SK": sk,
            "type": type(entity).__name__,
            **entity.model_dump(mode="json"),
        }
        self._table.put_item(Item=item)

    def _get(self, pk: str, sk: str, model: type[M]) -> M | None:
        response = self._table.get_item(Key={"PK": pk, "SK": sk})
        item = response.get("Item")
        return _to_model(item, model) if item else None

    def _query(self, pk: str, sk_prefix: str, model: type[M]) -> list[M]:
        condition = Key("PK").eq(pk) & Key("SK").begins_with(sk_prefix)
        items: list[Any] = []
        kwargs: dict[str, Any] = {"KeyConditionExpression": condition}
        while True:
            response = self._table.query(**kwargs)
            items.extend(response.get("Items", []))
            last = response.get("LastEvaluatedKey")
            if not last:
                break
            kwargs["ExclusiveStartKey"] = last
        return [_to_model(item, model) for item in items]

    # --- seasons ----------------------------------------------------------

    def list_seasons(self) -> list[Season]:
        return self._query(SEASONS_PK, "SEASON#", Season)

    def get_season(self, season_id: str) -> Season | None:
        return self._get(SEASONS_PK, f"SEASON#{season_id}", Season)

    def put_season(self, season: Season) -> None:
        self._put(SEASONS_PK, f"SEASON#{season.id}", season)

    # --- contestants ------------------------------------------------------

    def list_contestants(self, season_id: str) -> list[Contestant]:
        return self._query(season_pk(season_id), "CONTESTANT#", Contestant)

    def get_contestant(self, season_id: str, contestant_id: str) -> Contestant | None:
        return self._get(season_pk(season_id), f"CONTESTANT#{contestant_id}", Contestant)

    def put_contestant(self, contestant: Contestant) -> None:
        self._put(season_pk(contestant.season_id), f"CONTESTANT#{contestant.id}", contestant)

    # --- episode stats ----------------------------------------------------

    def list_episode_stats(self, season_id: str, episode: int | None = None) -> list[EpisodeStat]:
        prefix = "STAT#" if episode is None else f"STAT#EP{episode:03d}#"
        return self._query(season_pk(season_id), prefix, EpisodeStat)

    def put_episode_stat(self, stat: EpisodeStat) -> None:
        self._put(season_pk(stat.season_id), stat_sk(stat.episode, stat.contestant_id), stat)

    # --- rosters ----------------------------------------------------------

    def list_rosters(self, season_id: str) -> list[Roster]:
        return self._query(season_pk(season_id), "ROSTER#", Roster)

    def get_roster(self, season_id: str, user_id: str) -> Roster | None:
        return self._get(season_pk(season_id), f"ROSTER#{user_id}", Roster)

    def put_roster(self, roster: Roster) -> None:
        self._put(season_pk(roster.season_id), f"ROSTER#{roster.user_id}", roster)


def _to_model(item: Any, model: type[M]) -> M:
    data = {k: v for k, v in dict(item).items() if k not in ("PK", "SK", "type")}
    return model.model_validate(data)
