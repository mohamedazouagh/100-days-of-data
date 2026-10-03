# Day 06 - Reading and writing JSON with the json module

APIs and config files speak **JSON**: nested objects and lists, not a flat table. Before you can
count, average or write a CSV, you parse the text into Python objects and **flatten** each record
into one row of plain values.

Key points:
- `json.loads(text)` turns JSON into Python: objects → `dict`, arrays → `list`, `null` → `None`, `true` → `True`. `json.load(f)` does the same from an open file.
- Walk nested data with chained keys and indexes: `data["days"][0]["temp"]["max"]`.
- Real payloads are inconsistent: a key can be missing (`KeyError`) or present with `null`. Use `.get(key, default)` and decide on purpose whether "missing" means `None` or a real default - missing rain is *not reported*, not 0 mm.
- Flatten each nested record into a dict of plain values; a list of flat dicts is exactly what `csv.DictWriter` (Day 04) and later pandas expect.
- `json.dumps(obj, indent=2, sort_keys=True)` writes readable, diff-friendly output; `json.dump(obj, f)` writes to a file.

Run it: `python day06/lesson.py`

## Exercise
`PAYLOAD` in `solution.py` is a JSON string from a fictional bike-sharing API: stations, each with a
nested list of hourly counts, some with missing or `null` values. Parse it, then:
1. flatten it into one row per station and hour (`station`, `hour`, `rentals`), skipping `null` counts;
2. print the total rentals per station, busiest first;
3. print the station names that have at least one missing or `null` hour;
4. write the totals back out as JSON with sorted keys and check the round trip.
Solution: `day06/solution.py`.
