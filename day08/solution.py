import itertools as it

# Fictional access log: time, path, HTTP status, response time in ms
LOG = """\
# server: demo-01
09:00:01,/,200,35
09:00:02,/api/items,200,120
09:00:04,/api/items/7,404,15
09:00:05,/api/search,200,240
09:00:07,/api/search,200,310
09:00:08,/static/app.js,200,250
09:00:09,/login,500,900
09:00:11,/api/items,200,90
09:00:12,/api/items,BAD,
# restart
09:00:20,/api/report,200,410
09:00:21,/,200,220
09:00:22,/missing,404,12
""".splitlines()


def parse(lines, dropped):
    """Yield dicts for valid lines; append malformed lines to ``dropped``."""
    for line in lines:
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split(",")
        try:
            time, path, status, ms = parts
            yield {"time": time, "path": path, "status": int(status), "ms": int(ms)}
        except ValueError:
            dropped.append(line)


def by_status_class(rows):
    """{'2xx': (count, avg ms), ...} using groupby on the sorted status class."""
    keyed = sorted(rows, key=lambda r: r["status"] // 100)
    out = {}
    for cls, group in it.groupby(keyed, key=lambda r: r["status"] // 100):
        ms = [r["ms"] for r in group]
        out[f"{cls}xx"] = (len(ms), sum(ms) / len(ms))
    return out


def longest_slow_run(rows, limit=200):
    """(length, start time) of the longest run of consecutive requests slower than ``limit`` ms."""
    best = (0, None)
    for slow, group in it.groupby(rows, key=lambda r: r["ms"] > limit):
        if slow:
            group = list(group)
            if len(group) > best[0]:
                best = (len(group), group[0]["time"])
    return best


if __name__ == "__main__":
    dropped = []
    classes = by_status_class(parse(LOG, dropped))
    for cls, (n, avg) in classes.items():
        print(f"{cls}: {n} requests, avg {avg:.0f} ms")
    print("dropped:", dropped)

    run = longest_slow_run(parse(LOG, []))
    print(f"longest slow run: {run[0]} requests from {run[1]}")

    api = (r for r in parse(LOG, []) if r["path"].startswith("/api/"))
    first3 = [f"{r['time']} {r['path']}" for r in it.islice(api, 3)]
    print("first /api/ calls:", first3)

    assert classes == {"2xx": (8, 1675 / 8), "4xx": (2, 13.5), "5xx": (1, 900.0)}
    assert dropped == ["09:00:12,/api/items,BAD,"]
    assert run == (4, "09:00:05")
    assert first3 == ["09:00:02 /api/items", "09:00:04 /api/items/7", "09:00:05 /api/search"]
