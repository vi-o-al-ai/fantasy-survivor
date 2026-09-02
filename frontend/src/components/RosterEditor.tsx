import { useState } from "react";
import { useApi } from "@/api/context";
import { errorMessage } from "@/api/client";
import type { components } from "@/api/schema";

type League = components["schemas"]["LeagueOut"];
type Member = components["schemas"]["LeagueMember"];
type Contestant = components["schemas"]["Contestant"];

export function RosterEditor({
  league,
  me,
  contestants,
  onSaved,
}: {
  league: League;
  me: Member;
  contestants: Contestant[];
  onSaved: () => void;
}) {
  const api = useApi();
  const [picks, setPicks] = useState<string[]>(me.contestant_ids ?? []);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);
  const [busy, setBusy] = useState(false);

  function toggle(id: string) {
    setSaved(false);
    setPicks((current) =>
      current.includes(id) ? current.filter((c) => c !== id) : [...current, id],
    );
  }

  async function submit() {
    setBusy(true);
    setError(null);
    const { error } = await api.PUT("/leagues/{league_id}/members/me/roster", {
      params: { path: { league_id: league.id } },
      body: { contestant_ids: picks },
    });
    setBusy(false);
    if (error) {
      setError(errorMessage(error));
      return;
    }
    setSaved(true);
    onSaved();
  }

  const full = picks.length >= league.roster_size;

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        void submit();
      }}
      aria-labelledby="roster-heading"
    >
      <h2 id="roster-heading">My roster</h2>
      {!league.draft_open ? <p className="muted">The draft is closed; picks are locked.</p> : null}
      <p className="muted">
        Pick {league.roster_size}. Selected {picks.length}/{league.roster_size}.
      </p>
      <ul className="picks">
        {contestants.map((c) => {
          const checked = picks.includes(c.id);
          return (
            <li key={c.id}>
              <label>
                <input
                  type="checkbox"
                  checked={checked}
                  disabled={!league.draft_open || (!checked && full)}
                  onChange={() => {
                    toggle(c.id);
                  }}
                />{" "}
                {c.name}
                {c.tribe ? <span className="muted"> · {c.tribe}</span> : null}
                {c.status === "eliminated" ? <span className="badge">out</span> : null}
              </label>
            </li>
          );
        })}
      </ul>
      <button type="submit" disabled={busy || !league.draft_open}>
        Save roster
      </button>
      {saved ? <p role="status">Roster saved.</p> : null}
      {error ? <p role="alert">{error}</p> : null}
    </form>
  );
}
