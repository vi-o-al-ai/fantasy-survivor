import { useAuth0 } from "@auth0/auth0-react";
import { Link, Outlet } from "react-router-dom";

export function Layout() {
  const { isAuthenticated, user, loginWithRedirect, logout } = useAuth0();
  return (
    <div className="app">
      <header className="app-header">
        <Link to="/" className="brand">
          Fantasy Survivor
        </Link>
        <nav>
          {isAuthenticated ? (
            <>
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
