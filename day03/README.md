# Day 03 - Counting and grouping with dictionaries

Most questions about a table start with "how many per ..." or "what is the average per ...".
Before pandas' `groupby`, the plain-Python answer is a dictionary keyed by the group.

Key points:
- `d.get(key, 0) + 1` counts without a `KeyError` on the first occurrence.
- `collections.Counter` does the counting for you and adds `most_common(n)`.
- `collections.defaultdict(list)` creates an empty list the first time a key is used, so grouping is one `append`.
- Tuples are hashable, so `(date, city)` works as a composite key for fast lookups; use `.get(key, default)` when a combination may be missing.

Run it: `python day03/lesson.py`

## Exercise
Using `readings` from `lesson.py`, build a summary per city with the number of readings,
the average temperature (1 decimal) and the warmest date. Print one line per city, sorted by
average temperature from high to low.
Solution: `day03/solution.py`.
