# 12/react — Login, tokens and interceptors, step by step

[7/react](../../7/react/STEPS.md) called the API with plain
`axios.get(...)` and the full URL every time, and nobody had to log in.
Now every request needs a token, tokens expire, and a `401` might mean
"just refresh" instead of "you're out". Putting that logic in every
button handler would be a mess, so it all lives in one file,
`src/api.js`. `App.jsx` then looks almost like 7/react again.

## Part 1 — `src/api.js`

### Step 1 — One axios instance

```js
export const API_URL = "http://127.0.0.1:8000";
...
export const api = axios.create({ baseURL: API_URL });
```

`axios.create` makes a separate copy of axios with its own settings.
With `baseURL` set, calls get shorter (`api.get("/notes")` instead of
`` axios.get(`${API_URL}/notes`) ``), and, more importantly, this copy
can have its own **interceptors**: functions that run on every request
and every response that goes through `api`.

### Step 2 — Where the tokens live

```js
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
```

Two tokens, two places, on purpose:

- **Access token in memory** (a plain module variable). It's sent with
  every request, so it's the one most worth protecting. A variable
  disappears on reload, which is fine: it only lives 15 minutes and can
  be replaced using the refresh token.
- **Refresh token in `localStorage`**, so reloading the page doesn't
  log you out.

The trade-off, also written in the code: **any JavaScript on the page
can read `localStorage`**. If the app ever had an XSS bug (rendering
untrusted HTML, a compromised npm package), the refresh token could be
stolen. The stronger option is an **httpOnly cookie**, which JavaScript
can't read at all. But that needs the backend to set and read cookies,
and cookies are sent automatically, even by forms on other websites, so
the backend then also needs CSRF protection. For learning,
`localStorage` plus the backend's refresh-token rotation
([12/j step 7](../j/STEPS.md)) is a reasonable middle ground. React
also helps: `{note.title}` is always rendered as text, never as HTML.

### Step 3 — Request interceptor: attach the token

```js
api.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});
```

Runs just before every request leaves the browser. `config` is the
request about to be sent. We add the header and hand it back. No
component in `App.jsx` ever mentions `Authorization`.

### Step 4 — Response interceptor: when to refresh

```js
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
```

The first function handles successes (do nothing). The second handles
every error. Only one kind of error is worth a refresh: a `401` on a
normal request. Each condition rules out a trap:

- **`_retried`**: we mark a request once we've retried it. If the retry
  *also* gets `401`, we give up instead of refreshing forever.
- **`/token`**: a `401` there means wrong password. Refreshing makes no
  sense.
- **`/refresh`**: if refreshing itself returns `401`, trying to refresh
  the refresh would loop.
- **`403`** is never refreshed: a new token won't make Alice the owner
  of Bob's note. It goes straight back to `App.jsx` to show a message.

### Step 5 — Refresh, then replay

```js
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
```

`error.config` is the exact request that failed, so `api(original)`
sends it again with the new token. Whatever the retry returns becomes
the result of the **original** `await api.get(...)` in `App.jsx`. From
the component's point of view, the request just took a little longer.

If the refresh fails, the session really is over: forget the tokens and
call `onLogout`. `api.js` knows nothing about React state, so `App.jsx`
hands it a callback with `setOnLogout(...)`.

### Step 6 — One refresh at a time

```js
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
```

Picture the page loading three things at once after the token expired:
three `401`s arrive together. If each one called `/refresh` itself, the
first would succeed, and the backend would **revoke** that refresh token
(rotation). The other two would send the now-used token, get `401`,
and log you out. Bad.

So the first caller starts the refresh and stores the promise. Anyone
who arrives while it's in flight gets **the same promise** and waits
for the same new token. Once it settles, `finally` clears it so the
*next* expiry, 15 minutes later, starts a new one.

### Step 7 — Restoring a session on reload

```js
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
```

After a reload, `accessToken` is `null` but `localStorage` still has a
refresh token. Trading it in right away gets us a fresh access token
before the first real request. (In development, React's `StrictMode`
runs effects twice, so this is called twice. The shared promise from
step 6 means it still only calls `/refresh` once.)

## Part 2 — `src/App.jsx`

### Step 8 — Wiring up on page load

```jsx
useEffect(() => {
  setOnLogout(() => {
    resetState();
    setError("Your session expired. Please log in again.");
  });
  restoreSession().then((ok) => {
    if (ok) loadUserAndNotes();
  });
}, []);
```

Tell `api.js` what "logged out" means for this UI, then try to resume a
session from the saved refresh token.

### Step 9 — Logging in with a form body

```jsx
const body = new URLSearchParams({ username, password });
const response = await api.post("/token", body);
saveTokens(response.data);
```

OAuth2's password flow says the login body is a **form**
(`username=alice&password=...`), not JSON. That's why `/token` uses
`OAuth2PasswordRequestForm` on the backend. When axios is given a
`URLSearchParams`, it sends exactly that, with
`Content-Type: application/x-www-form-urlencoded`. Sending
`{ username, password }` as JSON would get a `422`.

After saving the tokens, `loadUserAndNotes()` calls `GET /users/me` to
learn who we are and our role. The frontend doesn't decode the JWT to
find the role. The payload doesn't even contain one
([12/j step 8](../j/STEPS.md)).

### Step 10 — The CRUD calls barely changed

```jsx
const response = await api.get("/notes");
...
await api.post("/notes", { title, body: "" });
...
await api.put(`/notes/${note.id}`, { title: editTitle, body: note.body });
...
await api.delete(`/notes/${id}`);
```

Compare these to [7/react](../../7/react/STEPS.md): `axios` became
`api`, the URL lost its `${API_URL}` prefix, and that's it. No tokens,
no headers, no refresh logic. Also notice `POST /notes` sends no
`owner_id`. The backend takes the owner from the token, so a client
couldn't create a note "as" someone else even if it tried.

### Step 11 — Showing 401, 403 and 429 nicely

```jsx
function errorMessage(action, err) {
  const status = err.response?.status;
  const detail = err.response?.data?.detail;
  if (status === 429) return "Too many login attempts. Wait a minute and try again.";
  if (status === 403) return `Not allowed: ${detail ?? "forbidden"}`;
  if (status && typeof detail === "string") return `Failed to ${action}: ${detail}`;
  return status ? `Failed to ${action} (status ${status})` : `Failed to ${action}: ${err.message}`;
}
```

Same helper as 7/react, grown up a little. By the time an error gets
here, the interceptor has already dealt with expired tokens, so what's
left are real answers:

- **`429`** from the rate-limited `/token`. slowapi's body has no
  `detail`, so we write our own message.
- **`403`** shows the backend's reason: "You don't own this note" or
  "Not enough permissions". It's not a login problem, so we don't send
  the user to the login form.
- **`401` from `/token`** shows "Incorrect username or password". The
  backend deliberately uses the same message for a wrong username and a
  wrong password.

### Step 12 — Admin vs. user UI

```jsx
const isAdmin = user.role === "admin";
...
{isAdmin ? (
  <button onClick={loadAdminUsers}>Load all users (admin)</button>
) : (
  <button onClick={loadAdminUsers}>Try admin route</button>
)}
```

The admin badge and button label come from `user.role`. **Hiding a
button is not security.** Anyone can open the browser console and call
`/admin/users` themselves. That's exactly why non-admins get a "Try
admin route" button here: click it and the **backend** answers `403`.
The UI is for convenience; `require_role("admin")` on the server is the
real lock.

### Step 13 — Watching the refresh happen

```jsx
async function simulateExpiredToken() {
  breakAccessToken();
  await loadNotes();
  setInfo("Access token was invalid, so api.js refreshed it and retried. You didn't notice a thing.");
}
```

Waiting 15 minutes for a real expiry is boring, so this button swaps
the in-memory access token for junk. Open the browser's Network tab and
click it: `notes` → `401`, `refresh` → `200`, `notes` → `200`.
`loadNotes()` itself never saw the `401`.

### Step 14 — Logging out

```jsx
function logout() {
  clearTokens();
  resetState();
  ...
}
```

The frontend forgets both tokens. The backend has no session to end:
an access token stays valid until it expires (at most 15 minutes),
which is the reason it's kept short. A fuller version would also tell
the backend to revoke the refresh token.
