# 12/react — Login UI, token storage, axios interceptors

A React frontend for the secure notes API in [12/j](../j). You log in,
get a pair of tokens, and from then on every request carries
`Authorization: Bearer ...` without any component having to think about
it. When the access token expires, the app quietly swaps the refresh
token for a new pair and retries the request. See
[STEPS.md](STEPS.md) for a step-by-step walkthrough of `api.js` and
`App.jsx`.

```
react/
├── src/api.js     # axios instance, token storage, the two interceptors
├── src/App.jsx    # login form + notes list + "try the security rules" buttons
└── src/main.jsx
```

## 1. Run the backend

```bash
cd example/12/j
uvicorn main:app --reload
```

## 2. Run the frontend

In a separate terminal:

```bash
cd example/12/react
npm install
npm run dev
```

Open the URL Vite prints (usually
[http://localhost:5173](http://localhost:5173)). It must be one of the
origins in the backend's `CORS_ORIGINS` (`localhost:5173` and
`127.0.0.1:5173` are allowed by default).

## What to try

| Do this | What you'll see |
|---|---|
| Log in as `alice` / `alice-password` | "Logged in as **alice** (user)" and her two notes |
| Add, edit, delete a note | Normal CRUD, every call authenticated by the interceptor |
| Click **Read note #3** as alice | `403`: "Not allowed: You don't own this note" (it's Bob's) |
| Click **Try admin route** as alice | `403`: "Not allowed: Not enough permissions" |
| Log in as `admin` / `admin-password` | An ADMIN badge, everyone's notes, and **Load all users** works |
| Click **Simulate expired access token** | The next request gets `401`, `api.js` refreshes and retries, the list still loads. Check the Network tab: `notes` (401), `refresh` (200), `notes` (200) |
| Reload the page while logged in | Still logged in: the refresh token in `localStorage` gets a new access token |
| Wrong password 6 times in a minute | "Too many login attempts. Wait a minute and try again." (`429`) |
| Log out | Both tokens forgotten; back to the login form |

All the backend routes, and why each rule exists, are in the
[12/j README](../j/README.md) and [12/j STEPS](../j/STEPS.md).
