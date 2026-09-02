import { useCallback, useEffect, useState } from "react";
import { errorMessage } from "@/api/client";

interface Result<T> {
  data?: T;
  error?: unknown;
}

/**
 * Run an async loader on mount (and whenever it changes), with cancellation
 * on unmount and a `reload` for after mutations. Loader results follow the
 * openapi-fetch `{ data, error }` shape so pages stay thin.
 */
export function useAsync<T>(loader: () => Promise<Result<T>>) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tick, setTick] = useState(0);

  useEffect(() => {
    let cancelled = false;
    loader().then(
      (result) => {
        if (cancelled) return;
        if (result.error !== undefined) setError(errorMessage(result.error));
        else setData(result.data ?? null);
      },
      (reason: unknown) => {
        if (!cancelled) setError(errorMessage(reason));
      },
    );
    return () => {
      cancelled = true;
    };
  }, [loader, tick]);

  const reload = useCallback(() => {
    setTick((t) => t + 1);
  }, []);

  return { data, error, reload };
}
