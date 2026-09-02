import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useApi } from "@/api/context";
import { errorMessage } from "@/api/client";
import type { components } from "@/api/schema";

type Entry = components["schemas"]["LeaderboardEntryOut"];

export function LeaderboardPage() {
  const { seasonId = "" } = useParams();
  const api = useApi();
  const [entries, setEntries] = useState<Entry[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    void api
      .GET("/seasons/{season_id}/leaderboard", { params: { path: { season_id: seasonId } } })
      .then(({ data, error }) => {
        if (cancelled) return;
        if (error) setError(errorMessage(error));
        else setEntries(data);
      });
    return () => {
      cancelled = true;
    };
  }, [api, seasonId]);

  if (error) return <p role="alert">{error}</p>;
  if (!entries) return <p role="status">Loading leaderboard…</p>;

  return (
    <section>
      <h1>Leaderboard</h1>
      {entries.length === 0 ? (
        <p>No rosters yet.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Player</th>
              <th>Points</th>
              <th>Picks</th>
            </tr>
          </thead>
          <tbody>
            {entries.map((entry) => (
              <tr key={entry.user_id}>
                <td>{entry.rank}</td>
                <td>{entry.display_name}</td>
                <td>{entry.points}</td>
                <td>
                  {Object.entries(entry.contestant_points)
                    .map(([id, points]) => `${id} (${String(points)})`)
                    .join(", ")}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
