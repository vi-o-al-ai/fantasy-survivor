import { useCallback } from "react";
import { useParams } from "react-router-dom";
import { useApi } from "@/api/context";
import type { components } from "@/api/schema";
import { useAsync } from "@/hooks/useAsync";
import { Leaderboard } from "@/components/Leaderboard";
import { LeagueSettings } from "@/components/LeagueSettings";
import { RosterEditor } from "@/components/RosterEditor";

type League = components["schemas"]["LeagueOut"];
type Member = components["schemas"]["LeagueMember"];
type Contestant = components["schemas"]["Contestant"];
type Entry = components["schemas"]["LeaderboardEntryOut"];

interface LeagueData {
  league: League;
  me: Member;
  contestants: Contestant[];
  entries: Entry[];
}

export function LeaguePage() {
  const { leagueId = "" } = useParams();
  const api = useApi();
  const loader = useCallback(async () => {
    const path = { params: { path: { league_id: leagueId } } };
    const league = await api.GET("/leagues/{league_id}", path);
    if (league.error) return { error: league.error };
    const me = await api.GET("/leagues/{league_id}/members/me", path);
    if (me.error) return { error: me.error };
    const contestants = await api.GET("/seasons/{season_id}/contestants", {
      params: { path: { season_id: league.data.season_id } },
    });
    if (contestants.error) return { error: contestants.error };
    const board = await api.GET("/leagues/{league_id}/leaderboard", path);
    if (board.error) return { error: board.error };
    const data: LeagueData = {
      league: league.data,
      me: me.data,
      contestants: contestants.data,
      entries: board.data,
    };
    return { data };
  }, [api, leagueId]);
  const { data, error, reload } = useAsync(loader);

  if (error) return <p role="alert">{error}</p>;
  if (!data) return <p role="status">Loading league…</p>;

  const { league, me, contestants, entries } = data;
  return (
    <section>
      <h1>{league.name}</h1>
      <p className="muted">
        Season {league.season_id} · rosters of {league.roster_size} ·{" "}
        {league.draft_open ? "draft open" : "draft closed"}
      </p>
      <Leaderboard entries={entries} />
      <RosterEditor league={league} me={me} contestants={contestants} onSaved={reload} />
      {league.is_owner ? <LeagueSettings league={league} onSaved={reload} /> : null}
    </section>
  );
}
