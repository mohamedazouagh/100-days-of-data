# Day 30 - Window calculations in pandas: rolling, expanding, diff, pct_change and rank

Day 27 used `shift` to look one row back and `resample` to change the time grain. Many
reports need something in between: a value computed over a *window* of nearby rows, such as
a 7-day average, a running total or "best day so far". pandas has three window types:
`rolling` (a moving window of fixed size), `expanding` (from the first row up to now) and
`ewm` (exponentially weighted, not used today).

Key points:
- `s.rolling(3).mean()` averages the current row and the two before it. The first two results
  are NaN because the window is not full; `min_periods=1` computes them from whatever rows are
  there. Any aggregation works: `sum`, `max`, `std`, `median`, or `.agg([...])`.
- `center=True` puts the window around the row. That is fine for smoothing a chart, but it
  uses a future row, so never use it for anything that pretends to predict.
- A window of `n` rows is only "n days" if no day is missing. With a sorted `DatetimeIndex`
  use a time span instead: `rolling("7D")` covers the last 7 calendar days, however many rows
  that is.
- `expanding()` grows from the start: `expanding().sum()` is a running total (same as
  `cumsum`), `expanding().max()` the best value so far (same as `cummax`), and
  `expanding().mean()` a running average, which has no `cum*` shortcut.
- `df.groupby("key")["col"].rolling(3).mean()` keeps the windows inside each group. The result
  has the group key as an extra index level; `reset_index(level=0, drop=True)` lines it up
  with the original rows again.
- `diff()` is the change from the previous row, `pct_change()` the relative change (watch out
  for a previous value of 0, which gives `inf`), and `rank(ascending=False, method="min")`
  numbers rows from best to worst with ties sharing the better rank.

Requires pandas: `python -m pip install -r requirements.txt`

Run it: `python day30/lesson.py`

## Exercise
`solution.py` builds a fictional daily visitor log (fixed seed) for three shop branches over
five weeks, with a few days missing per branch because the counter was offline.
1. per branch, compute a 7-calendar-day rolling average of visitors (`rolling("7D")`) and show
   how it differs from a plain 7-row window around a gap;
2. add a running total and a "best day so far" column per branch with `expanding`;
3. compute the day-over-day change and % change per branch, keeping a 0-visitor day from
   producing `inf`;
4. rank each branch's days from busiest to quietest, and list each branch's top 3 days;
5. check every number against plain Python loops over the original records.
Solution: `day30/solution.py`.
