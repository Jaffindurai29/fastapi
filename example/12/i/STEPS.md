# 12/i — Rate limiting login, step by step

`database.py`, `models.py`, `config.py`, `security.py`, `crud.py` and
`dependencies.py` are the same as [12/c](../c/STEPS.md). Everything new
is at the top of `main.py` and on the `/token` route.

1. **Why limit login.** Without a limit, a script can try thousands of
   passwords a minute against `alice` (**brute force**), or try the most
   common passwords against every username (**password spraying**). A
   limit of 5 a minute turns "thousands per minute" into 7,200 a day,
   and the most common passwords are the first ones tried, so pair this
   with a minimum password length like 12/a's.

2. **`main.py` — one limiter for the app:**

   ```python
   limiter = Limiter(key_func=get_remote_address, headers_enabled=True)

   app = FastAPI()
   app.state.limiter = limiter
   app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
   ```

   - `key_func` decides **who** is being counted. `get_remote_address`
     uses the client's IP address, so every request from one machine
     shares one counter.
   - `app.state.limiter` is where slowapi looks for it at request time.
   - When a limit is hit, slowapi raises `RateLimitExceeded`. The
     built-in handler turns it into a `429` with
     `{"error": "Rate limit exceeded: 5 per 1 minute"}`. (Note the key is
     `error`, not FastAPI's usual `detail`. Write your own handler if your
     client expects `detail`.)
   - `headers_enabled=True` adds `X-RateLimit-Limit`,
     `X-RateLimit-Remaining` and `X-RateLimit-Reset` to responses, and
     `Retry-After` to the `429`. It's off by default.

3. **The route — decorator under the route decorator:**

   ```python
   @app.post("/token", response_model=Token, responses={
       401: {"description": "Incorrect username or password"},
       429: {"description": "Too many login attempts"},
   })
   @limiter.limit("5/minute")
   def login(request: Request, response: Response,
             form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
   ```

   - `@limiter.limit` must sit **below** `@app.post`, so FastAPI
     registers the already-limited function.
   - `"5/minute"` can also be `"100/hour"`, `"5/minute;20/hour"`, and so on.
   - `request: Request` is **required**, and must be named `request`.
     slowapi reads the IP from it, and refuses to start without it
     (`No "request" or "websocket" argument on function ...`), even
     though the route body never uses it.
   - `response: Response` is required only because of
     `headers_enabled`. This route returns a dict, not a `Response`, so
     slowapi needs FastAPI's `response` object to put its headers on.
     Leave it out and every successful login becomes a `500`, with
     "parameter `response` must be an instance of
     starlette.responses.Response" in the server log.

4. **What counts.** Every request to `/token` counts, right password or
   wrong: the limiter runs **before** the route body, so it can't know
   the outcome. That's fine for login; a real user rarely needs more
   than 5 tries a minute. Only `/token` is limited; `/users/me` isn't a
   password-guessing target and the token check there is cheap.

5. **Reading the headers.** On a successful login:

   ```
   x-ratelimit-limit: 5
   x-ratelimit-remaining: 4
   x-ratelimit-reset: 1791196147.93
   ```

   and on the `429`, also `retry-after: 60` (seconds to wait). A
   well-behaved client reads `Retry-After` and waits instead of
   retrying in a loop. One gap: the `401` for a wrong password has
   **no** rate-limit headers. It's raised as an exception before slowapi
   gets to decorate the response.

6. **In-memory storage, and why production needs Redis.** By default the
   counters live in a Python dict inside the server process. That means:
   - **Restart = reset.** Every `--reload` gives everyone a fresh 5.
   - **Not shared between workers.** `uvicorn main:app --workers 4` (or
     4 containers behind a load balancer) gives each worker its own
     counters, so the real limit becomes 20 a minute, depending on which
     worker answers.

   The fix is one argument, pointing every worker at the same store:

   ```python
   limiter = Limiter(key_func=get_remote_address, storage_uri="redis://localhost:6379")
   ```

   (slowapi uses the `limits` library underneath, which also supports
   Memcached and MongoDB.)

7. **Limits of limiting by IP.**
   - Behind a reverse proxy (nginx, a cloud load balancer), every
     request arrives from the **proxy's** IP, so everybody shares one
     counter. Run uvicorn with `--proxy-headers` and
     `--forwarded-allow-ips` set to your proxy so the real client IP
     (from `X-Forwarded-For`) is used. Only trust that header from your
     own proxy; anyone can send a fake one.
   - Many users behind one office or mobile-carrier IP share a limit.
   - An attacker with thousands of IPs (a botnet) gets 5 a minute from
     each. Defences there include also limiting per **username** (a
     custom `key_func` reading the form field), temporary account
     lockouts, CAPTCHAs, and multi-factor login.

8. **Testing.** FastAPI's `TestClient` reports its address as
   `"testclient"`, so all test requests share one counter: the 6th login
   in a test returns `429`. The counters also persist between tests in
   the same process; call `limiter.reset()` between tests that each
   expect a fresh budget.
