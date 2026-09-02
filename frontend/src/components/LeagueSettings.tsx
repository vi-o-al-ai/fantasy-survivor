import { useEffect, useState } from "react";
import { useApi } from "@/api/context";
import { errorMessage } from "@/api/client";
import type { components } from "@/api/schema";

type League = components["schemas"]["LeagueOut"];
type EventType = components["schemas"]["EventType"];
type Points = Record<EventType, number>;

/** Owner-only panel: invite code, draft state, and this league's point values. */
export function LeagueSettings({ league, onSaved }: { league: League; onSaved: () => void }) {
  const api = useApi();
  const [defaults, setDefaults] = useState<Points | null>(null);
  const [points, setPoints] = useState<Points | null>(null);
  const [draftOpen, setDraftOpen] = useState(league.draft_open);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    void api.GET("/scoring-rules").then(({ data, error }) => {
      if (error) {
        setError(errorMessage(error));
        return;
      }
      const base = data.points as Points;
      setDefaults(base);
      setPoints({ ...base, ...(league.scoring_overrides as Partial<Points>) });
    });
  }, [api, league.scoring_overrides]);

  async function submit() {
    if (!points || !defaults) return;
    setError(null);
    const overrides = Object.fromEntries(
      (Object.keys(points) as EventType[])
        .filter((k) => points[k] !== defaults[k])
        .map((k) => [k, points[k]]),
    ) as Partial<Points>;
    const { error } = await api.PATCH("/leagues/{league_id}", {
      params: { path: { league_id: league.id } },
      body: { draft_open: draftOpen, scoring_overrides: overrides },
    });
    if (error) {
      setError(errorMessage(error));
      return;
    }
    setSaved(true);
    onSaved();
  }

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        void submit();
      }}
      aria-labelledby="settings-heading"
    >
      <h2 id="settings-heading">League settings</h2>
      <p>
        Invite friends with league id <code>{league.id}</code> and join code{" "}
        <code data-testid="join-code">{league.join_code}</code>.
      </p>
      <label>
        <input
          type="checkbox"
          checked={draftOpen}
          onChange={(e) => {
            setSaved(false);
            setDraftOpen(e.target.checked);
          }}
        />{" "}
        Draft open (members can change rosters)
      </label>
      <h3>Point values</h3>
      <p className="muted">Recorded events are shared by every league; these values are yours.</p>
      {points && defaults ? (
        <table>
          <tbody>
            {(Object.keys(defaults) as EventType[]).map((event) => (
              <tr key={event}>
                <td>
                  <label htmlFor={`pts-${event}`}>{event.replaceAll("_", " ")}</label>
                </td>
                <td>
                  <input
                    id={`pts-${event}`}
                    type="number"
                    value={points[event]}
                    onChange={(e) => {
                      setSaved(false);
                      setPoints({ ...points, [event]: Number(e.target.value) });
                    }}
                  />
                  {points[event] !== defaults[event] ? (
                    <span className="muted"> (default {defaults[event]})</span>
                  ) : null}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p role="status">Loading point values…</p>
      )}
      <button type="submit" disabled={!points}>
        Save settings
      </button>
      {saved ? <p role="status">Settings saved.</p> : null}
      {error ? <p role="alert">{error}</p> : null}
    </form>
  );
}
