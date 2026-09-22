# 7 — React + MySQL + CRUD

Connecting a real React frontend to the full-CRUD MySQL backend from
[topic 6](../6) — CORS on the FastAPI side, the same add/list/
reach/edit/delete UI as [topic 5](../5) on the React side, now backed
by a real database instead of an in-memory array.

| Sub-topic | What it covers |
|---|---|
| [7/a — MySQL backend, full CRUD + CORS](a) | All five verbs from topic 6, combined into one app, plus `CORSMiddleware`. |
| [7/react — React frontend](react) | Same UI as 5/react, pointed at a real database — uses each row's `id` instead of an array index. |

Each folder above has its own **README.md** (how to run it) and
**STEPS.md** (line-by-line — `7/react`'s calls out exactly what's
different from `5/react`, step by step).

## How to run this topic

This one needs the same database setup as topic 6, **plus** both
backend and frontend running at once:

1. **One-time database setup** (identical to [topic 6](../6) — skip if
   already done):

   ```bash
   pip install -r ../../requirements.txt
   ```

   ```sql
   CREATE DATABASE fastapi_learn;
   ```

   ```bash
   export MYSQL_HOST=127.0.0.1
   export MYSQL_PORT=3306
   export MYSQL_USER=root
   export MYSQL_PASSWORD=your-password
   export MYSQL_DB=fastapi_learn
   ```

   ...or `cp example/7/a/.env.example example/7/a/.env` and edit that
   instead — `database.py` loads it automatically. Skipping both is
   also fine; the defaults above are already baked in.

   No MySQL handy? `export DATABASE_URL="sqlite:///./test.db"` instead.

2. **Terminal 1 — backend:**

   ```bash
   cd example/7/a
   uvicorn main:app --reload
   ```

3. **Terminal 2 — frontend:**

   ```bash
   cd example/7/react
   npm install
   npm run dev
   ```

4. Open the URL Vite prints (usually
   [http://localhost:5173](http://localhost:5173)).

Start the backend before the frontend, same as topic 5 — every button
in the UI calls it directly.
