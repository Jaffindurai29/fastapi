# 5/a — Array backend, full CRUD + CORS, step by step

Every route here is identical to its counterpart in
[topic 4](../../4) (4/a=GET, 4/b=POST, 4/c=PUT, 4/d=PATCH, 4/e=DELETE) —
just combined into one app instead of five separate ones, since a real
frontend needs every operation available on the same running server.
This file only covers what's new: CORS.

1. **Import the middleware:**

   ```python
   from fastapi.middleware.cors import CORSMiddleware
   ```

2. **List the frontend origins allowed to read responses:**

   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. **Register it once, right after creating `app`** — no changes needed
   in any of the five routes below it.

4. **Why this is needed:** without it, the server still answers every
   request correctly — `curl` proves that. What's missing is one
   response header that tells the *browser* it's allowed to hand the
   response to JavaScript from a different origin. This is exactly what
   lets the [React frontend](../react) actually call this API.
