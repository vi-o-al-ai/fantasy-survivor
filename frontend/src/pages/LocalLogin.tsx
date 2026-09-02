import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useLocalLogin } from "@/auth/localAuth";

/** Dev/test stand-in for the Auth0 hosted login page. */
export function LocalLoginPage() {
  const login = useLocalLogin();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const [token, setToken] = useState("");
  const returnTo = params.get("returnTo") ?? "/";

  return (
    <section>
      <h1>Local login</h1>
      <p className="muted">
        Auth0 is bypassed in local auth mode. Paste a token from{" "}
        <code>python scripts/mint_dev_token.py</code>.
      </p>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          login(token.trim());
          void navigate(returnTo, { replace: true });
        }}
      >
        <label>
          Access token
          <textarea
            value={token}
            onChange={(e) => {
              setToken(e.target.value);
            }}
            rows={4}
            required
          />
        </label>
        <button type="submit">Log in</button>
      </form>
    </section>
  );
}
