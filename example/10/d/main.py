import asyncio
import time

from fastapi import FastAPI

app = FastAPI()


# Plain `def`: FastAPI runs it in a worker thread (a threadpool), so
# while this thread sleeps, the event loop keeps serving other requests.
# 5 requests at once -> 5 threads sleeping side by side -> about 1 s.
@app.get("/sync-sleep")
def sync_sleep():
    time.sleep(1)  # a blocking call, like a SQLAlchemy query or requests.get()
    return {"endpoint": "sync-sleep", "slept": 1}


# `async def` + `await`: runs on the event loop itself. `await` hands
# control back to the loop while waiting, so it serves others meanwhile.
# 5 requests at once -> about 1 s.
@app.get("/async-sleep")
async def async_sleep():
    await asyncio.sleep(1)
    return {"endpoint": "async-sleep", "slept": 1}


# THE MISTAKE: `async def` + a blocking call. There's no `await`, so the
# event loop is stuck inside time.sleep for a full second and can do
# nothing else — not even /ping. 5 requests at once -> about 5 s.
@app.get("/async-blocking")
async def async_blocking():
    time.sleep(1)
    return {"endpoint": "async-blocking", "slept": 1}


# Instant. Used by demo.py to show whether the server is still responsive.
@app.get("/ping")
def ping():
    return {"pong": True}
