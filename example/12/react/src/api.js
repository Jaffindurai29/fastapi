import axios from "axios";

// Where the FastAPI backend (12/j) is running.
export const API_URL = "http://127.0.0.1:8000";

// ---------------------------------------------------------------------------
// Token storage
//
// Access token: kept in a plain module variable, i.e. in memory only. It
// disappears on page reload, and that's fine: it only lives 15 minutes
// anyway, and we can get a fresh one with the refresh token.
//
// Refresh token: kept in localStorage so a page reload doesn't log you out.
// Trade-off: any JavaScript running on this page can read localStorage, so
// an XSS bug (e.g. rendering untrusted HTML) could steal it. The stronger
// option is an httpOnly cookie, which JavaScript can't read at all, but
// that needs the backend to set/read cookies and to defend against CSRF
// (cookies are sent automatically, even by other sites' forms). For a
// learning app, localStorage + rotation on the backend is a reasonable
// middle ground.
// ---------------------------------------------------------------------------

const REFRESH_KEY = "refresh_token";
let accessToken = null;

export function saveTokens({ access_token, refresh_token }) {
  accessToken = access_token;
  localStorage.setItem(REFRESH_KEY, refresh_token);
}

export function clearTokens() {
  accessToken = null;
  localStorage.removeItem(REFRESH_KEY);
}

// For the demo button in App.jsx: replace the access token with junk so
// the next request gets a 401 and you can watch the refresh happen.
export function breakAccessToken() {
  accessToken = "not-a-real-token";
}

export function hasRefreshToken() {
  return localStorage.getItem(REFRESH_KEY) !== null;
}

// App.jsx registers a function here so the API layer can tell the UI
// "you've been logged out" when a refresh fails.
let onLogout = () => {};
export function setOnLogout(callback) {
  onLogout = callback;
}

// One axios instance for the whole app. Every call goes through the two
// interceptors below.
export const api = axios.create({ baseURL: API_URL });

// ---- Request interceptor: attach the access token ------------------------
// Runs before every request. Saves writing the header by hand on every call.
api.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

// ---- Refresh: one at a time ---------------------------------------------
// If three requests fail with 401 at the same moment, we must NOT call
// /refresh three times: the backend rotates refresh tokens, so the 2nd
// and 3rd calls would be using an already-used token and fail. Instead,
// the first 401 starts a refresh and the others wait on the same promise.
let refreshPromise = null;

function refreshTokens() {
  if (!refreshPromise) {
    const refresh_token = localStorage.getItem(REFRESH_KEY);
    refreshPromise = api
      .post("/refresh", { refresh_token })
      .then((response) => {
        saveTokens(response.data);
        return response.data.access_token;
      })
      .finally(() => {
        refreshPromise = null; // the next expiry starts a fresh refresh
      });
  }
  return refreshPromise;
}

// Restore a session after a page reload: we have a refresh token in
// localStorage but no access token in memory yet.
export async function restoreSession() {
  if (!hasRefreshToken()) return false;
  try {
    await refreshTokens();
    return true;
  } catch {
    clearTokens();
    return false;
  }
}

// ---- Response interceptor: refresh on 401, retry once --------------------
api.interceptors.response.use(
  (response) => response, // 2xx: pass straight through
  async (error) => {
    const original = error.config;
    const url = original?.url ?? "";

    const shouldRefresh =
      error.response?.status === 401 &&
      !original._retried && // only retry each request once, or we could loop forever
      url !== "/token" && // a 401 from login means "wrong password", not "expired"
      url !== "/refresh" && // a 401 from refresh means the session is over
      hasRefreshToken();

    if (!shouldRefresh) {
      return Promise.reject(error); // 403, 404, 429, ... go to the caller as-is
    }

    original._retried = true;
    try {
      const newAccessToken = await refreshTokens();
      original.headers.Authorization = `Bearer ${newAccessToken}`;
      return api(original); // replay the request that failed
    } catch (refreshError) {
      // Refresh token expired, revoked or reused: the session is over.
      clearTokens();
      onLogout();
      return Promise.reject(refreshError);
    }
  },
);
