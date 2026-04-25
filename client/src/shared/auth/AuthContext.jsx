import { createContext, useContext, useMemo, useState } from "react";
import { clearTokens, getAccessToken, setTokens } from "./tokenStorage";

const AuthContext = createContext(null);

function safeDecodeEmailFromJwt(token) {
  try {
    const [, payload] = token.split(".");
    const json = JSON.parse(atob(payload.replace(/-/g, "+").replace(/_/g, "/")));
    return json?.email || null;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }) {
  const [accessToken, setAccessToken] = useState(getAccessToken());

  const value = useMemo(() => {
    const email = accessToken ? safeDecodeEmailFromJwt(accessToken) : null;
    const isAuthenticated = Boolean(accessToken);

    return {
      isAuthenticated,
      email,
      accessToken,
      login: (tokens) => {
        setTokens(tokens);
        setAccessToken(tokens.access_token);
      },
      logout: () => {
        clearTokens();
        setAccessToken(null);
      },
    };
  }, [accessToken]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

