# 7/react — React frontend, MySQL-backed

Same UI as [5/react](../../5/react), pointed at the MySQL backend from
[7/a](../a) instead of the plain array from topic 5 — the only real
change is using each row's real database `id` instead of an array
index to reach/edit/delete it. See [STEPS.md](STEPS.md) for exactly
what changed, step by step, compared to 5/react.

```
react/
├── src/App.jsx    # the whole UI: form + list + edit + delete + "reach"
└── src/main.jsx
```

## 1. Run the backend

```bash
cd example/7/a
uvicorn main:app --reload
```

## 2. Run the frontend

In a separate terminal:

```bash
cd example/7/react
npm install
npm run dev
```

Open the URL Vite prints (usually
[http://localhost:5173](http://localhost:5173)).

## What it does

Identical feature set to [5/react](../../5/react) — create, read,
reach-by-id, update (PUT/PATCH), delete — just against a real MySQL
table. One visible difference: after deleting a row, the remaining
rows keep their original `#id` numbers instead of shifting down, since
a database ID is a stable identity, not a position in a list.
