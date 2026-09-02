import { Link, Outlet } from "react-router-dom";
import { useAuth } from "@/auth/useAuth";

export function Layout() {
  const { isAuthenticated, user, loginWithRedirect, logout } = useAuth();
  return (
    <div className="app">
      <header className="app-header">
        <Link to="/" className="brand">
          Fantasy Survivor
        </Link>
        <nav>
          {isAuthenticated ? (
            <>
              <Link to="/">Leagues</Link>
              <Link to="/seasons">Seasons</Link>
              <span className="muted">{user?.name ?? user?.email}</span>
              <button
                type="button"
                onClick={() => {
                  void logout({ logoutParams: { returnTo: window.location.origin } });
                }}
              >
                Log out
              </button>
            </>
          ) : (
            <button
              type="button"
              onClick={() => {
                void loginWithRedirect();
              }}
            >
              Log in
            </button>
          )}
        </nav>
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  );
}
