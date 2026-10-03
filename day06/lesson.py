import json

# What an API typically sends back: one JSON string with nested objects and lists
RAW = """
{
  "city": "Breda",
  "days": [
    {"date": "2026-09-30", "temp": {"max": 24.8, "min": 17.8}, "rain_mm": 1.2, "tags": ["humid"]},
    {"date": "2026-10-01", "temp": {"max": 21.0, "min": 14.4}, "rain_mm": 2.2, "tags": []},
    {"date": "2026-10-02", "temp": {"max": 19.5, "min": null}, "tags": ["clear", "windy"]}
  ]
}
"""


def flatten(day, city):
    """Turn one nested day object into a flat row (a dict of plain values)."""
    temp = day.get("temp", {})
    return {
        "city": city,
        "date": day["date"],
        "temp_max": temp.get("max"),
        "temp_min": temp.get("min"),  # JSON null -> Python None
        "rain_mm": day.get("rain_mm"),  # key may be missing: keep None, "not reported" is not 0 mm
        "tags": ";".join(day.get("tags", [])),
    }


if __name__ == "__main__":
    # 1. json.loads: text -> Python dicts / lists / str / float / None
    data = json.loads(RAW)
    print(type(data).__name__, list(data))
    print(type(data["days"]).__name__, len(data["days"]), "days")

    # 2. Reach into nested structures with keys and indexes
    print("first max:", data["days"][0]["temp"]["max"])

    # 3. Missing keys and nulls: .get() with a default avoids KeyError
    last = data["days"][-1]
    print("rain on last day:", last.get("rain_mm", "not reported"))
    print("min on last day:", last["temp"]["min"])

    # 4. Flatten into a list of rows - the shape csv.DictWriter and pandas want
    rows = [flatten(d, data["city"]) for d in data["days"]]
    for row in rows:
        print(row)

    # 5. json.dumps: Python -> text (indent for humans, sort_keys for stable diffs)
    print(json.dumps(rows[0], indent=2, sort_keys=True))

    # 6. Round trip: what you write is what you read back
    assert json.loads(json.dumps(rows)) == rows
