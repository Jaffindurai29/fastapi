# 5/react — React frontend, full CRUD

A React app (Vite + axios, no TypeScript) covering all five verbs from
[5/a](../a): add, list, reach-by-index, edit (PUT or PATCH), and
delete. See [STEPS.md](STEPS.md) for how `App.jsx` is built up, one
operation at a time.

```
react/
├── src/App.jsx    # the whole UI: form + list + edit + delete + "reach"
└── src/main.jsx
```

## 1. Run the backend

```bash
cd example/5/a
uvicorn main:app --reload
```

## 2. Run the frontend

In a separate terminal:

```bash
cd example/5/react
npm install
npm run dev
```

Open the URL Vite prints (usually
[http://localhost:5173](http://localhost:5173)).

## What it does

- **Create** — the form at the top `POST`s a new value onto the array.
- **Read** — the page loads the full array with `GET /items` on open,
  and refreshes after every change.
- **Reach** — clicking a row's **Reach** button calls
  `GET /items/{index}` for that exact row and shows the result — a live
  fetch, not just what's already in state.
- **Update** — clicking **Edit** turns a row into an input box with two
  save buttons: **Save (PUT)** and **Save (PATCH)**. Both send the same
  body here (this item only has one field), but call different HTTP
  methods — `saveEdit(index, method)` in `App.jsx` takes the method as
  a parameter for exactly this reason.
- **Delete** — the **Delete** button calls `DELETE /items/{index}` and
  refreshes the list.

Every one of those is a single [axios](https://axios-http.com) call in
[src/App.jsx](src/App.jsx) against the five routes from
[5/a](../a/README.md) — no state management library, just
`useState`/`useEffect`. axios parses JSON responses, serializes JSON
request bodies, and throws on `4xx`/`5xx` so errors land in one
`catch` (see Step 0 in [STEPS.md](STEPS.md)). `npm install` picks it up
from `package.json`.
