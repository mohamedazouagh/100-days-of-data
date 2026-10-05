import itertools as it

# A tiny "log file": one line per sensor reading, already sorted by sensor
LINES = [
    "2026-10-01T08:00,s1,21.4",
    "2026-10-01T09:00,s1,22.0",
    "# maintenance window",
    "2026-10-01T10:00,s1,",
    "2026-10-01T08:00,s2,18.9",
    "2026-10-01T09:00,s2,19.4",
    "2026-10-01T10:00,s2,20.1",
]


def parse(lines):
    """Generator: yields one dict per valid line, skipping comments and blanks."""
    for line in lines:
        if not line or line.startswith("#"):
            continue
        ts, sensor, value = line.split(",")
        yield {"ts": ts, "sensor": sensor, "value": float(value) if value else None}


if __name__ == "__main__":
    # 1. A generator does no work until you iterate it
    rows = parse(LINES)
    print(type(rows).__name__)

    # 2. next() pulls one item; the generator remembers where it stopped
    print(next(rows))

    # 3. Generators are single-use: after list() it is exhausted
    print(len(list(rows)), "more rows,", len(list(rows)), "after that")

    # 4. Generator expressions chain into a lazy pipeline (nothing in memory but one row)
    values = (r["value"] for r in parse(LINES) if r["value"] is not None)
    print("max value:", max(values))

    # 5. islice: take only the first n items of any iterable (great for peeking at big files)
    print([r["ts"][-5:] for r in it.islice(parse(LINES), 2)])

    # 6. groupby groups *consecutive* items with the same key - sort by the key first
    for sensor, group in it.groupby(parse(LINES), key=lambda r: r["sensor"]):
        vals = [r["value"] for r in group if r["value"] is not None]
        print(sensor, len(vals), "readings, mean", round(sum(vals) / len(vals), 2))

    # 7. Unsorted input splits a group in two - the classic groupby bug
    keys = ["a", "b", "a"]
    print([(k, len(list(g))) for k, g in it.groupby(keys)])

    # 8. chain joins iterables, pairwise gives neighbours (for differences)
    s2 = [r["value"] for r in parse(LINES) if r["sensor"] == "s2"]
    print([round(b - a, 1) for a, b in it.pairwise(s2)])
    print(list(it.chain([1, 2], (3, 4), range(5, 7))))
