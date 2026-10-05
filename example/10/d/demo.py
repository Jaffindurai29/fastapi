"""Fire 5 concurrent requests at each endpoint and print the wall time.

Start the server first (in another terminal):

    uvicorn main:app

then:

    python demo.py
    python demo.py --base-url http://127.0.0.1:8765

Only the standard library is used, so nothing to install.
"""

import argparse
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

N = 5


def fetch(url: str) -> float:
    """GET url, return how long it took in seconds."""
    start = time.perf_counter()
    with urllib.request.urlopen(url, timeout=30) as resp:
        resp.read()
    return time.perf_counter() - start


def burst(url: str, n: int = N) -> float:
    """Send n requests to url at the same time; return total wall time."""
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=n) as pool:
        list(pool.map(fetch, [url] * n))
    return time.perf_counter() - start


def ping_during(base: str, path: str) -> float:
    """Start a burst on `path`, then time one /ping sent while it runs."""
    with ThreadPoolExecutor(max_workers=N + 1) as pool:
        for _ in range(N):
            pool.submit(fetch, base + path)
        time.sleep(0.2)  # let the burst reach the server first
        return pool.submit(fetch, base + "/ping").result()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    base = parser.parse_args().base_url.rstrip("/")

    fetch(base + "/ping")  # warm-up: fails fast if the server isn't running

    print(f"{N} concurrent requests per endpoint against {base}\n")
    for path in ["/sync-sleep", "/async-sleep", "/async-blocking"]:
        print(f"  {path:<16} {burst(base + path):5.2f} s total")

    print("\nOne /ping sent while each burst is running:\n")
    for path in ["/sync-sleep", "/async-sleep", "/async-blocking"]:
        print(f"  during {path:<16} /ping took {ping_during(base, path):5.2f} s")


if __name__ == "__main__":
    main()
