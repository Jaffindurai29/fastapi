# 10/d — `async def` vs `def`, step by step

No database, no `models.py`/`crud.py`: just `main.py` and `demo.py`.

1. **Two ways FastAPI runs a route.** Uvicorn runs one **event loop**:
   a single thread that switches between requests whenever one of them
   is waiting. What FastAPI does with your function depends on how you
   wrote it:
   - `async def` → called **directly on the event loop**. FastAPI
     trusts you to `await` whenever you wait, so the loop can switch.
   - `def` → sent to a **threadpool** (about 40 worker threads by
     default). The function can block as long as it likes; it only
     blocks its own thread.

2. **`/sync-sleep` — `def` with a blocking call:**

   ```python
   @app.get("/sync-sleep")
   def sync_sleep():
       time.sleep(1)  # a blocking call, like a SQLAlchemy query or requests.get()
       return {"endpoint": "sync-sleep", "slept": 1}
   ```

   Five requests arrive together, FastAPI hands them to five worker
   threads, all five sleep at the same time, and all five answer after
   about **1 second**. The event loop never blocks, so `/ping` stays
   instant.

3. **`/async-sleep` — `async def` with an async wait:**

   ```python
   @app.get("/async-sleep")
   async def async_sleep():
       await asyncio.sleep(1)
       return {"endpoint": "async-sleep", "slept": 1}
   ```

   `await asyncio.sleep(1)` means "wake me in a second, serve others
   meanwhile". The loop starts all five, parks them, answers `/ping`
   in between, and finishes all five after about **1 second**. No
   threads involved.

4. **`/async-blocking` — the mistake:**

   ```python
   @app.get("/async-blocking")
   async def async_blocking():
       time.sleep(1)
       return {"endpoint": "async-blocking", "slept": 1}
   ```

   It's `async def`, so it runs on the event loop. But `time.sleep`
   isn't awaitable: it holds the loop's only thread for a full second,
   and the loop can't switch to anything else. The five requests run
   strictly one after another, **about 5 seconds** in total, and every
   other request to the server, `/ping` included, queues behind them.

   Nothing warns you about this. The code runs, a single request takes
   1 second as expected, and it only shows up under load.

5. **`demo.py` — measuring it.** Only the standard library:

   ```python
   def burst(url: str, n: int = N) -> float:
       """Send n requests to url at the same time; return total wall time."""
       start = time.perf_counter()
       with ThreadPoolExecutor(max_workers=n) as pool:
           list(pool.map(fetch, [url] * n))
       return time.perf_counter() - start
   ```

   `ThreadPoolExecutor` sends the five `urllib.request` calls from five
   threads at once; `burst` returns how long until the last one came
   back. `ping_during` starts a burst, then times one `/ping` sent
   while the burst is in flight, which is what shows the freeze.
   `--base-url` (default `http://127.0.0.1:8000`) picks the server.

6. **The rule:**

   > If the library you call is sync (SQLAlchemy `Session`, `requests`,
   > `time.sleep`) → use `def`. Only use `async def` when everything
   > you await is async.

   "Async" libraries are the ones whose calls you `await`: `asyncio`,
   `httpx.AsyncClient`, SQLAlchemy's `AsyncSession`, `aiomysql`. If you
   aren't writing `await` in front of the slow call, it isn't async.

   When in doubt, `def` is the safe choice. A `def` route that could
   have been `async def` costs a thread; an `async def` route that
   blocks costs the whole server.

7. **Why every database route in this repo is plain `def`.** Since
   [topic 6](../../6/a/STEPS.md), each route does
   `db: Session = Depends(get_db)` and calls things like
   `db.query(...)` and `db.commit()`. That's the **sync** SQLAlchemy
   `Session`: it waits for MySQL the way `time.sleep` waits, blocking
   its thread. As `def` routes, those waits happen in worker threads.
   Change one to `async def` and it becomes `/async-blocking`: correct
   on your laptop, frozen under real traffic. Going async for real
   means switching the whole stack (async engine, `AsyncSession`, an
   async driver, `await` on every query), not just the keyword.

8. **Dependencies follow the same rule.** `get_db` from
   [10/b](../b/STEPS.md) is a plain `def` with `yield`, so FastAPI runs
   it in the threadpool too. It's fine for a `def` route to use `def`
   dependencies, and for an `async def` route to use them; FastAPI
   runs each piece in the right place.
