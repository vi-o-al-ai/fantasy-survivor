import type { components } from "@/api/schema";

type Entry = components["schemas"]["LeaderboardEntryOut"];

export function Leaderboard({ entries }: { entries: Entry[] }) {
  return (
    <section aria-labelledby="leaderboard-heading">
      <h2 id="leaderboard-heading">Leaderboard</h2>
      {entries.length === 0 ? (
        <p>No members yet.</p>
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
                    .join(", ") || "no picks yet"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
