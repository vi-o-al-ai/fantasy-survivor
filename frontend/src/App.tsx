import { Route, Routes } from "react-router-dom";
import { ApiProvider } from "@/api/ApiProvider";
import { AuthProvider } from "@/auth/AuthProvider";
import { RequireAuth } from "@/auth/RequireAuth";
import { Layout } from "@/components/Layout";
import { LeaguePage } from "@/pages/League";
import { LeaguesPage } from "@/pages/Leagues";
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
                  <LeaguesPage />
                </RequireAuth>
              }
            />
            <Route
              path="/leagues/:leagueId"
              element={
                <RequireAuth>
                  <LeaguePage />
                </RequireAuth>
              }
            />
            <Route
              path="/seasons"
              element={
                <RequireAuth>
                  <SeasonsPage />
                </RequireAuth>
              }
            />
          </Route>
        </Routes>
      </ApiProvider>
    </AuthProvider>
  );
}
