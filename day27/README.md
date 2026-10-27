# Day 27 - Dates and time series in pandas: to_datetime, .dt, resample and shift

Day 05 handled dates one value at a time with `datetime`. In pandas a whole column of dates
becomes a `datetime64` column, and once it is the index you can slice by date strings, fill
in missing days and regroup daily data into weeks or months in one call. The trap is that
"the previous row" and "the previous day" are only the same when no day is missing.

Key points:
- `pd.to_datetime(col, format="%Y-%m-%d")` parses text to `datetime64`. Passing `format`
  keeps it fast and stops pandas from guessing (and silently swapping day and month).
- The `.dt` accessor works on a datetime column: `.dt.day_name()`, `.dt.month`,
  `.dt.isocalendar().week`, `.dt.date`, ... The same calendar parts as `datetime`, vectorised.
- With a `DatetimeIndex`, `s.loc["2026-10"]` selects a whole month and
  `s.loc["2026-09-30":"2026-10-02"]` a range. Unlike integer slicing, both ends are included.
- `asfreq("D")` reindexes to every calendar day. Days that were never recorded show up as NaN
  instead of being invisible.
- `resample(rule)` is a `groupby` on time buckets: `"W-SUN"` gives weeks ending on Sunday
  (labelled by that Sunday), `"MS"` calendar months labelled by their first day. Use `.sum()`,
  `.mean()` or `.agg([...])`; `count` shows how many days actually fed each bucket.
- `shift(1)`, `diff()` and `pct_change()` compare each row with the row above it. On a series
  with gaps that row may be two days back; call `asfreq("D")` first if you mean "yesterday".

Requires pandas: `python -m pip install -r requirements.txt`

Run it: `python day27/lesson.py`

## Exercise
`solution.py` builds a fictional log of daily step counts from a fitness tracker (fixed seed)
for September and October 2026, with the dates stored as text and a few days missing.
1. parse the dates, set them as the index and list the missing calendar days with `asfreq`;
2. total and average steps per ISO week (weeks ending Sunday) with `resample`, plus how many
   days each week actually has;
3. monthly totals and the busiest weekday on average, using `.dt.day_name()`;
4. the biggest day-over-day jump, once over rows (`diff` on the raw series) and once over real
   consecutive days (`diff` after `asfreq("D")`), and show where they differ;
5. check every number against plain Python loops over the original records.
Solution: `day27/solution.py`.
