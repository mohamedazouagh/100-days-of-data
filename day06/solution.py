import json

# Fictional bike-sharing API response
PAYLOAD = """
{
  "generated": "2026-10-03T08:00:00Z",
  "stations": [
    {"name": "Station Square", "hours": [
      {"hour": 7, "rentals": 12}, {"hour": 8, "rentals": 30}, {"hour": 9, "rentals": 18}
    ]},
    {"name": "Park Gate", "hours": [
      {"hour": 7, "rentals": 4}, {"hour": 8, "rentals": null}, {"hour": 9, "rentals": 9}
    ]},
    {"name": "Harbour", "hours": [
      {"hour": 7, "rentals": 7}, {"hour": 8}, {"hour": 9, "rentals": 41}
    ]}
  ]
}
"""


def flatten(data):
    """One row per station and hour; hours without a usable count are skipped."""
    rows = []
    for station in data["stations"]:
        for h in station["hours"]:
            rentals = h.get("rentals")  # missing key and null both give None
            if rentals is not None:
                rows.append({"station": station["name"], "hour": h["hour"], "rentals": rentals})
    return rows


def totals_by_station(rows):
    totals = {}
    for r in rows:
        totals[r["station"]] = totals.get(r["station"], 0) + r["rentals"]
    return dict(sorted(totals.items(), key=lambda kv: (-kv[1], kv[0])))


def stations_with_gaps(data):
    return [s["name"] for s in data["stations"] if any(h.get("rentals") is None for h in s["hours"])]


if __name__ == "__main__":
    data = json.loads(PAYLOAD)
    rows = flatten(data)
    totals = totals_by_station(rows)
    gaps = stations_with_gaps(data)

    print(len(rows), "rows, first:", rows[0])
    for name, total in totals.items():
        print(f"{name:<15} {total:>4}")
    print("stations with gaps:", gaps)

    text = json.dumps(totals, indent=2, sort_keys=True)
    print(text)

    assert len(rows) == 7  # 9 station-hours minus one null and one missing key
    assert list(totals.items()) == [("Station Square", 60), ("Harbour", 48), ("Park Gate", 13)]
    assert gaps == ["Park Gate", "Harbour"]
    assert json.loads(text) == totals
