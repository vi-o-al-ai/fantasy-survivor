"""DynamoDB single-table store.

Key design (one table, ``PK``/``SK`` strings, no GSIs yet):

    Item          PK                 SK
    ------------  -----------------  ----------------------------
    Season        SEASONS            SEASON#<season_id>
    Contestant    SEASON#<sid>       CONTESTANT#<contestant_id>
    EpisodeStat   SEASON#<sid>       STAT#EP<episode:03d>#<contestant_id>
    League        LEAGUE#<lid>       META
    LeagueMember  LEAGUE#<lid>       MEMBER#<user_id>
    (pointer)     USER#<user_id>     LEAGUE#<lid>

Everything for a season (or a league) shares one partition, so loading it
is one query and per-type listings are ``begins_with`` on the sort key.
Episode numbers are zero-padded so stats sort in air order. Entity fields
are stored flat next to the keys, plus a ``type`` attribute for debugging.
The pointer item under the user's partition answers "which leagues am I
in?" without a GSI; it is written alongside every member put.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

import boto3
from boto3.dynamodb.conditions import Key
from pydantic import BaseModel

from app.domain.models import Contestant, EpisodeStat, League, LeagueMember, Season

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


def league_pk(league_id: str) -> str:
    return f"LEAGUE#{league_id}"


def user_pk(user_id: str) -> str:
    return f"USER#{user_id}"


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

    # --- leagues ----------------------------------------------------------

    def get_league(self, league_id: str) -> League | None:
        return self._get(league_pk(league_id), "META", League)

    def put_league(self, league: League) -> None:
        self._put(league_pk(league.id), "META", league)

    def list_members(self, league_id: str) -> list[LeagueMember]:
        return self._query(league_pk(league_id), "MEMBER#", LeagueMember)

    def get_member(self, league_id: str, user_id: str) -> LeagueMember | None:
        return self._get(league_pk(league_id), f"MEMBER#{user_id}", LeagueMember)

    def put_member(self, member: LeagueMember) -> None:
        self._put(league_pk(member.league_id), f"MEMBER#{member.user_id}", member)
        self._table.put_item(
            Item={
                "PK": user_pk(member.user_id),
                "SK": f"LEAGUE#{member.league_id}",
                "type": "LeaguePointer",
                "league_id": member.league_id,
            }
        )

    def list_league_ids_for_user(self, user_id: str) -> list[str]:
        condition = Key("PK").eq(user_pk(user_id)) & Key("SK").begins_with("LEAGUE#")
        response = self._table.query(KeyConditionExpression=condition)
        return [str(item["league_id"]) for item in response.get("Items", [])]


def _to_model(item: Any, model: type[M]) -> M:
    data = {k: v for k, v in dict(item).items() if k not in ("PK", "SK", "type")}
    return model.model_validate(data)
