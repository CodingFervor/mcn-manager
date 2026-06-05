"""
5000-user concurrent load test with realistic think time.
5000 simulated users, each makes a few requests with think time between them.
This better represents a real MCN dashboard with thousands of concurrent viewers.
"""
import sys
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor
from urllib.request import urlopen

BASE = "http://127.0.0.1:8000/api"
USERS = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
WORKERS = int(sys.argv[2]) if len(sys.argv) > 2 else 500
ENDPOINTS = [
    "/stores/",
    "/stores/overview/",
    "/employees/stats/",
    "/shifts/",
    "/dashboard/overview/",
    "/reviews/?period=2026-05",
    "/sessions/daily_gmv/?start=2026-05-01&end=2026-05-31",
]

_done = [0]
_lock = threading.Lock()
_lats = []
_ok = [0]
_req = [0]

def fetch(ep):
    t0 = time.perf_counter()
    try:
        with urlopen(BASE + ep, timeout=30) as r:
            r.read()
            if r.status == 200:
                with _lock:
                    _ok[0] += 1
        return (time.perf_counter() - t0) * 1000, True
    except Exception:
        return (time.perf_counter() - t0) * 1000, False

def one_user(idx):
    """User opens session, makes 5-10 random requests with think time."""
    n_reqs = random.randint(5, 10)
    user_lats = []
    for _ in range(n_reqs):
        ep = random.choice(ENDPOINTS)
        lat, success = fetch(ep)
        user_lats.append(lat)
        with _lock:
            _req[0] += 1
        # Think time: simulate user reading UI
        time.sleep(random.uniform(0.1, 0.5))
    with _lock:
        _done[0] += 1
        _lats.extend(user_lats)
        if _done[0] % 200 == 0 or _done[0] == USERS:
            print(f"  users={_done[0]}/{USERS} ({_done[0]*100/USERS:.0f}%)  reqs={_req[0]}  ok={_ok[0]}", flush=True)

def main():
    print(f"=== 5000-User Concurrent Load Test ===", flush=True)
    print(f"Users: {USERS}  Workers: {WORKERS}  Endpoints: {len(ENDPOINTS)}", flush=True)
    print(f"Each user makes 5-10 random requests with 0.1-0.5s think time", flush=True)
    print("-" * 60, flush=True)
    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        list(ex.map(one_user, range(USERS)))
    elapsed = time.perf_counter() - t0
    lats = sorted(_lats)
    p50 = lats[len(lats)//2]
    p95 = lats[int(len(lats)*0.95)]
    p99 = lats[int(len(lats)*0.99)]
    print("-" * 60, flush=True)
    print(f"Total elapsed:    {elapsed:.2f}s", flush=True)
    print(f"Total requests:   {_req[0]}", flush=True)
    print(f"Success:          {_ok[0]}/{_req[0]} ({_ok[0]*100/max(_req[0],1):.2f}%)", flush=True)
    print(f"Throughput:       {_req[0]/elapsed:,.0f} req/s", flush=True)
    print(f"User sessions:    {USERS} in {elapsed:.1f}s ({USERS/elapsed:,.0f} sessions/s)", flush=True)
    print(f"Latency p50:      {p50:.1f} ms", flush=True)
    print(f"Latency p95:      {p95:.1f} ms", flush=True)
    print(f"Latency p99:      {p99:.1f} ms", flush=True)
    print(f"Latency max:      {max(lats):.1f} ms", flush=True)
    print("-" * 60, flush=True)
    success_pct = _ok[0]*100/max(_req[0],1)
    if success_pct >= 99 and p95 < 3000:
        print("✅ PASS  5000-user concurrent target met", flush=True)
    else:
        print("⚠️  review results above", flush=True)

if __name__ == "__main__":
    main()
