import axios from "axios";

// Where the FastAPI backend (14/a) is running.
export const API_URL = "http://127.0.0.1:8000";

// Tokens live in localStorage so a page reload doesn't log you out.
// (Any script on this page could read them; fine for learning, but real
// apps often use httpOnly cookies instead.)
export const tokenStore = {
  get() {
    try {
      return JSON.parse(localStorage.getItem("tokens"));
    } catch {
      return null;
    }
  },
  set(tokens) {
    localStorage.setItem("tokens", JSON.stringify(tokens));
  },
  clear() {
    localStorage.removeItem("tokens");
  },
};

// Every page uses this instead of plain axios, so they never have to
// think about tokens.
const api = axios.create({ baseURL: API_URL });

// 1) Before each request: attach the access token.
api.interceptors.request.use((config) => {
  const tokens = tokenStore.get();
  if (tokens) config.headers.Authorization = `Bearer ${tokens.access_token}`;
  return config;
});

// 2) After each response: if it's 401 (access token expired), swap the
// refresh token for a new access token and repeat the request once.
let refreshing = null; // shared, so 3 requests failing at once cause only 1 refresh
let onSessionExpired = () => {};

export function setOnSessionExpired(fn) {
  onSessionExpired = fn;
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const request = error.config;
    const tokens = tokenStore.get();
    if (error.response?.status !== 401 || request._retried || !tokens) throw error;
    request._retried = true;

    try {
      refreshing ??= axios
        .post(`${API_URL}/refresh`, { refresh_token: tokens.refresh_token })
        .finally(() => {
          refreshing = null;
        });
      const res = await refreshing;
      tokenStore.set(res.data);
    } catch {
      // The refresh token expired too: the session is over.
      tokenStore.clear();
      onSessionExpired();
      throw error;
    }
    return api(request);
  },
);

// FastAPI puts the reason in `detail`: a string for our own errors, a
// list for validation errors.
export function errorText(error) {
  const detail = error.response?.data?.detail;
  if (Array.isArray(detail)) return detail.map((d) => d.msg).join(", ");
  return detail || "Cannot reach the server";
}

export function money(value) {
  return `$${Number(value).toFixed(2)}`;
}

export default api;
