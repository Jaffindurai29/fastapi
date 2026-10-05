# 10/d — `async def` vs `def`

When should a route be `async def`, and when plain `def`? This app has
no database: just four tiny routes that each wait one second in a
different way, and a `demo.py` script that hits each one with 5
requests **at the same time** and times them. See
[STEPS.md](STEPS.md) for a line-by-line walkthrough.

No setup needed beyond `pip install -r ../../../requirements.txt`.
`demo.py` uses only the Python standard library.

## Files

```
10/d/
├── main.py    # /sync-sleep, /async-sleep, /async-blocking, /ping
└── demo.py    # 5 concurrent requests per endpoint, prints wall time
```

## Run it

Terminal 1:

```bash
cd example/10/d
uvicorn main:app
```

Terminal 2:

```bash
cd example/10/d
python demo.py
```

`demo.py --base-url http://127.0.0.1:8765` points it at a server on a
different port. Run uvicorn **without** `--reload` for this; the
reloader adds noise to timings.

| Route | How it waits | 1 request | 5 at once |
|---|---|---|---|
| `GET /sync-sleep` | `def` + `time.sleep(1)` | 1 s | **~1 s** (5 worker threads sleep side by side) |
| `GET /async-sleep` | `async def` + `await asyncio.sleep(1)` | 1 s | **~1 s** (the event loop juggles all 5) |
| `GET /async-blocking` | `async def` + `time.sleep(1)` | 1 s | **~5 s** (one after another, and the whole server is frozen meanwhile) |
| `GET /ping` | `def`, returns at once | instant | instant |

Real output from `demo.py`:

```
5 concurrent requests per endpoint against http://127.0.0.1:8765

  /sync-sleep       1.01 s total
  /async-sleep      1.01 s total
  /async-blocking   5.02 s total

One /ping sent while each burst is running:

  during /sync-sleep      /ping took  0.02 s
  during /async-sleep     /ping took  0.00 s
  during /async-blocking  /ping took  4.82 s
```

The last line is the important one: while `/async-blocking` runs, even
`/ping`, which does nothing, waits almost 5 seconds. Every user of
the app would see it hang.

## The rule

> If the library you call is sync (SQLAlchemy `Session`, `requests`,
> `time.sleep`) → use `def`. Only use `async def` when everything you
> await is async.

That's why **every database route in this repo is plain `def`**: they
all call a regular SQLAlchemy `Session`, which blocks while it waits
for MySQL. As `def` routes, each runs in its own worker thread and the
server stays responsive. Written as `async def`, every query would
freeze the whole server like `/async-blocking` does.

```bash
curl http://127.0.0.1:8000/sync-sleep

curl http://127.0.0.1:8000/async-sleep

curl http://127.0.0.1:8000/async-blocking

curl http://127.0.0.1:8000/ping
```

**Postman:** Method `GET`, URL `http://127.0.0.1:8000/sync-sleep` (or
any route above), no Headers or Body. Postman sends one request at a
time, so it can't show the difference; use `demo.py` for that.

Windows curl quoting, Postman basics, and "405 Method Not Allowed" are
covered generically in the [root README](../../../README.md).
