from collections import defaultdict

from lesson import readings


def summarise(rows: list[dict]) -> dict[str, dict]:
    """city -> {"n": count, "avg": mean temp (1 decimal), "warmest": date of max temp}."""
    groups: defaultdict[str, list[dict]] = defaultdict(list)
    for r in rows:
        groups[r["city"]].append(r)
    summary = {}
    for city, items in groups.items():
        temps = [r["temp"] for r in items]
        warmest = max(items, key=lambda r: r["temp"])
        summary[city] = {
            "n": len(items),
            "avg": round(sum(temps) / len(temps), 1),
            "warmest": warmest["date"],
        }
    return summary


if __name__ == "__main__":
    summary = summarise(readings)
    for city, s in sorted(summary.items(), key=lambda kv: kv[1]["avg"], reverse=True):
        print(f"{city:<10} n={s['n']}  avg={s['avg']:.1f}  warmest={s['warmest']}")

    assert summary["Breda"] == {"n": 3, "avg": 21.4, "warmest": "2026-09-27"}
    assert summary["Eindhoven"]["n"] == 2
