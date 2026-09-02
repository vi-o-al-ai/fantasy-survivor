import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useApi } from "@/api/context";
import { errorMessage } from "@/api/client";
import type { components } from "@/api/schema";

type Season = components["schemas"]["Season"];

export function SeasonsPage() {
  const api = useApi();
  const [seasons, setSeasons] = useState<Season[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    void api.GET("/seasons").then(({ data, error }) => {
      if (cancelled) return;
      if (error) setError(errorMessage(error));
      else setSeasons(data);
    });
    return () => {
      cancelled = true;
    };
  }, [api]);

  if (error) return <p role="alert">{error}</p>;
  if (!seasons) return <p role="status">Loading seasons…</p>;
  if (seasons.length === 0) return <p>No seasons yet. Ask your commissioner to create one.</p>;

  return (
    <section>
      <h1>Seasons</h1>
      <ul>
        {seasons.map((season) => (
          <li key={season.id}>
            <Link to={`/seasons/${season.id}`}>{season.name}</Link>
            {season.draft_open ? <span className="badge">draft open</span> : null}
          </li>
        ))}
      </ul>
    </section>
  );
}
