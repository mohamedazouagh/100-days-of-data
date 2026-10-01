# Day 04 - Reading and writing CSV with the csv module

CSV is the most common format you'll receive data in. Splitting lines on `","` by hand breaks
as soon as a field contains a comma or quotes, so use the standard library's `csv` module.

Key points:
- `csv.DictReader` turns each row into a dict keyed by the header, so code reads `row["temp"]` instead of `row[2]`.
- Every value comes back as a **string**: convert numbers yourself, and decide what an empty field means (often `None`).
- `csv.DictWriter(f, fieldnames=[...])` + `writeheader()` + `writerows()` writes dicts back out; quoting is handled for you.
- Open files with `newline=""` and an explicit `encoding="utf-8"`, otherwise Windows adds blank lines between rows.
- `io.StringIO` behaves like a file in memory - handy for trying things out and for tests.

Run it: `python day04/lesson.py`

## Exercise
`RAW` in `solution.py` holds a small export with a missing temperature and a city name
containing a comma. Parse it, drop rows without a temperature, add a `temp_f` column
(Fahrenheit, 1 decimal) and write the cleaned rows back to CSV text with the columns
`date,city,temp_c,temp_f`. Print the result.
Solution: `day04/solution.py`.
