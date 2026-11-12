# Day 37 - Nearest-key joins with merge_asof: direction, tolerance and by

Two time series rarely share exact timestamps: orders and exchange rates, sensor readings and
calibrations, GPS pings and stops. A normal `merge` on the time column finds almost nothing.
What you usually want is "the latest row on the other side at or before this moment", which is
exactly what `pd.merge_asof` does.

Key points:
- Both frames must be **sorted by the `on` key**; an unsorted key raises
  `left keys must be sorted` instead of quietly matching the wrong rows.
- The default `direction="backward"` takes the last right-hand row with key <= the left key.
  That is the safe choice for prices and states, because it never uses information from the
  future. Rows before the first right-hand row get `NaN`, not a guess.
- `tolerance=pd.Timedelta("1h")` refuses matches that are too far away, so a rate from three
  hours ago shows up as missing instead of stale. Always count those gaps.
- `direction="forward"` takes the next row, `"nearest"` the closest in either direction (ties
  go backward). Useful for matching events to the next check-in, but they leak the future
  into anything you would later use as a model feature.
- `by="sensor"` (or a list of columns) first matches exactly on the group, then asof on the
  key within it: each reading gets the latest calibration of its *own* sensor.
- `allow_exact_matches=False` makes the match strictly earlier, e.g. "the rate before this
  trade, not the one published at the same second".
- The result keeps every left row in left order, like a left join with at most one match each.

Requires pandas: `python -m pip install -r requirements.txt`

Run it: `python day37/lesson.py`

## Exercise
`solution.py` builds a fictional parcel log (fixed seed): scan events per van with a timestamp,
and a separate stream of GPS fixes per van that arrive at irregular moments.
1. attach to every scan the latest GPS fix of the **same van** at or before the scan, with
   `merge_asof(..., by="van")`;
2. add a 10-minute tolerance and list the scans left without a fresh fix, per van;
3. compute how old the used fix was for each scan (scan time minus fix time) and the
   median age per van;
4. show that `direction="nearest"` would pick a *later* fix for some scans and count them;
5. check every match against a plain Python version using `bisect` on per-van sorted lists.
Solution: `day37/solution.py`.
