from collections import Counter, defaultdict

readings = [
    {"date": "2026-09-26", "city": "Breda", "temp": 20.6},
    {"date": "2026-09-26", "city": "Tilburg", "temp": 20.1},
    {"date": "2026-09-27", "city": "Breda", "temp": 22.1},
    {"date": "2026-09-27", "city": "Eindhoven", "temp": 22.8},
    {"date": "2026-09-28", "city": "Breda", "temp": 21.4},
    {"date": "2026-09-28", "city": "Tilburg", "temp": 21.0},
    {"date": "2026-09-28", "city": "Eindhoven", "temp": 21.9},
]

if __name__ == "__main__":
    # 1. Counting by hand with dict.get
    counts: dict[str, int] = {}
    for r in readings:
        counts[r["city"]] = counts.get(r["city"], 0) + 1
    print(counts)

    # 2. The same with Counter, plus the most common keys
    city_counts = Counter(r["city"] for r in readings)
    print(city_counts.most_common(2))

    # 3. Grouping rows: city -> list of temperatures
    by_city: defaultdict[str, list[float]] = defaultdict(list)
    for r in readings:
        by_city[r["city"]].append(r["temp"])
    print(dict(by_city))

    # 4. A lookup table: (date, city) -> temp, for O(1) access
    lookup = {(r["date"], r["city"]): r["temp"] for r in readings}
    print(lookup[("2026-09-27", "Eindhoven")])
    print(lookup.get(("2026-09-27", "Tilburg"), "missing"))
