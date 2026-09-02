import { useCallback, useState } from "react";
import { Link } from "react-router-dom";
import { useApi } from "@/api/context";
import { errorMessage } from "@/api/client";
import type { components } from "@/api/schema";
import { useAsync } from "@/hooks/useAsync";

type League = components["schemas"]["LeagueOut"];
type Season = components["schemas"]["Season"];

export function LeaguesPage() {
  const api = useApi();
  const loader = useCallback(async () => {
    const mine = await api.GET("/leagues");
    if (mine.error) return { error: mine.error };
    const all = await api.GET("/seasons");
    return { data: { leagues: mine.data, seasons: all.data ?? [] } };
  }, [api]);
  const { data, error, reload } = useAsync<{ leagues: League[]; seasons: Season[] }>(loader);

  if (error) return <p role="alert">{error}</p>;
  if (!data) return <p role="status">Loading your leagues…</p>;
  const { leagues, seasons } = data;

  return (
    <section>
      <h1>My leagues</h1>
      {leagues.length === 0 ? (
        <p>You are not in any leagues yet. Create one or join with a code.</p>
      ) : (
        <ul>
          {leagues.map((league) => (
            <li key={league.id}>
              <Link to={`/leagues/${league.id}`}>{league.name}</Link>
              {league.is_owner ? <span className="badge">owner</span> : null}
              {league.draft_open ? <span className="badge">draft open</span> : null}
            </li>
          ))}
        </ul>
      )}
      <div className="forms">
        <CreateLeagueForm seasons={seasons} onCreated={reload} />
        <JoinLeagueForm onJoined={reload} />
      </div>
    </section>
  );
}

function CreateLeagueForm({ seasons, onCreated }: { seasons: Season[]; onCreated: () => void }) {
  const api = useApi();
  const [name, setName] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [seasonId, setSeasonId] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const season = seasonId !== "" ? seasonId : (seasons[0]?.id ?? "");

  async function submit() {
    setBusy(true);
    setError(null);
    const { error } = await api.POST("/leagues", {
      body: { season_id: season, name, display_name: displayName },
    });
    setBusy(false);
    if (error) {
      setError(errorMessage(error));
      return;
    }
    setName("");
    onCreated();
  }

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        void submit();
      }}
      aria-labelledby="create-heading"
    >
      <h2 id="create-heading">Create a league</h2>
      {seasons.length === 0 ? <p className="muted">No seasons available yet.</p> : null}
      <label>
        Season
        <select
          value={season}
          onChange={(e) => {
            setSeasonId(e.target.value);
          }}
          required
        >
          {seasons.map((s) => (
            <option key={s.id} value={s.id}>
              {s.name}
            </option>
          ))}
        </select>
      </label>
      <label>
        League name
        <input
          value={name}
          onChange={(e) => {
            setName(e.target.value);
          }}
          required
          maxLength={60}
        />
      </label>
      <label>
        Your name in the league
        <input
          value={displayName}
          onChange={(e) => {
            setDisplayName(e.target.value);
          }}
          required
          maxLength={50}
        />
      </label>
      <button type="submit" disabled={busy || seasons.length === 0}>
        Create
      </button>
      {error ? <p role="alert">{error}</p> : null}
    </form>
  );
}

function JoinLeagueForm({ onJoined }: { onJoined: () => void }) {
  const api = useApi();
  const [leagueId, setLeagueId] = useState("");
  const [joinCode, setJoinCode] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit() {
    setBusy(true);
    setError(null);
    const { error } = await api.POST("/leagues/{league_id}/members", {
      params: { path: { league_id: leagueId.trim() } },
      body: { join_code: joinCode.trim().toUpperCase(), display_name: displayName },
    });
    setBusy(false);
    if (error) {
      setError(errorMessage(error));
      return;
    }
    setLeagueId("");
    setJoinCode("");
    onJoined();
  }

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        void submit();
      }}
      aria-labelledby="join-heading"
    >
      <h2 id="join-heading">Join a league</h2>
      <label>
        League id
        <input
          value={leagueId}
          onChange={(e) => {
            setLeagueId(e.target.value);
          }}
          required
        />
      </label>
      <label>
        Join code
        <input
          value={joinCode}
          onChange={(e) => {
            setJoinCode(e.target.value);
          }}
          required
        />
      </label>
      <label>
        Your name in the league
        <input
          value={displayName}
          onChange={(e) => {
            setDisplayName(e.target.value);
          }}
          required
          maxLength={50}
        />
      </label>
      <button type="submit" disabled={busy}>
        Join
      </button>
      {error ? <p role="alert">{error}</p> : null}
    </form>
  );
}
