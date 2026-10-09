import { createContext, useContext, useEffect, useState } from "react";
import axios from "axios";
import api, { API_URL, setOnSessionExpired, tokenStore } from "./api";

const AuthContext = createContext(null);

// Holds the logged-in user ({ id, username, role }) for the whole app.
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  // If tokens were saved from last time, ask /me who we are before
  // deciding whether to show the login page.
  const [checking, setChecking] = useState(() => tokenStore.get() !== null);

  useEffect(() => {
    setOnSessionExpired(() => setUser(null));
    if (!tokenStore.get()) return;
    api
      .get("/me")
      .then((res) => setUser(res.data))
      .catch(() => tokenStore.clear())
      .finally(() => setChecking(false));
  }, []);

  async function login(username, password) {
    tokenStore.clear();
    const res = await axios.post(`${API_URL}/login`, { username, password });
    tokenStore.set(res.data);
    // The role comes from /me (the database), not from decoding the token.
    const me = await api.get("/me");
    setUser(me.data);
    return me.data;
  }

  function logout() {
    tokenStore.clear();
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, checking, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}

// Where each role lands after logging in.
export function homeFor(user) {
  return user.role === "admin" ? "/admin/products" : "/products";
}
