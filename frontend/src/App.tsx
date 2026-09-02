import { Route, Routes } from "react-router-dom";
import { ApiProvider } from "@/api/ApiProvider";
import { AuthProvider } from "@/auth/AuthProvider";
import { RequireAuth } from "@/auth/RequireAuth";
import { Layout } from "@/components/Layout";
import { LeaderboardPage } from "@/pages/Leaderboard";
import { SeasonsPage } from "@/pages/Seasons";

export function App() {
  return (
    <AuthProvider>
      <ApiProvider>
        <Routes>
          <Route element={<Layout />}>
            <Route
              index
              element={
                <RequireAuth>
                  <SeasonsPage />
                </RequireAuth>
              }
            />
            <Route
              path="/seasons/:seasonId"
              element={
                <RequireAuth>
                  <LeaderboardPage />
                </RequireAuth>
              }
            />
          </Route>
        </Routes>
      </ApiProvider>
    </AuthProvider>
  );
}
