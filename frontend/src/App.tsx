import { Route, Routes } from "react-router-dom";
import { ApiProvider } from "@/api/ApiProvider";
import { AuthProvider } from "@/auth/AuthProvider";
import { RequireAuth } from "@/auth/RequireAuth";
import { LOCAL_LOGIN_PATH } from "@/auth/localAuth";
import { Layout } from "@/components/Layout";
import { config } from "@/config";
import { LeaguePage } from "@/pages/League";
import { LeaguesPage } from "@/pages/Leagues";
import { LocalLoginPage } from "@/pages/LocalLogin";
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
            {config.authMode === "local" ? (
              <Route path={LOCAL_LOGIN_PATH} element={<LocalLoginPage />} />
            ) : null}
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
