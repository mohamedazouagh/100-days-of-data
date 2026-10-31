# Day 31 - Conditional columns in pandas: np.where, np.select, map, where/mask, clip and apply

Most derived columns are "if this, then that": free shipping above a threshold, a size label,
a region looked up from a country code, a value capped at a maximum. The tempting way is a
Python `if` inside `df.apply(func, axis=1)`, which calls the function once per row. pandas and
NumPy have column-wide tools that do the same in one go and are far faster on large tables.

Key points:
- `np.where(cond, a, b)` picks `a` where the condition is true and `b` elsewhere, for the whole
  column at once. It returns a NumPy array; assign it to a column to keep the index aligned.
- `np.select(conditions, choices, default=...)` handles more than two outcomes. Conditions are
  checked in order and the first match wins, so put the most specific one first (a refund
  check before "amount >= 50").
- `Series.map(dict)` replaces each value by its dictionary entry. Anything missing from the
  dict becomes `NaN`: count or fill those explicitly so unknown codes do not disappear.
- `s.where(cond, other)` keeps values where the condition holds and replaces the rest;
  `s.mask(cond, other)` replaces where it holds. `s.clip(lower, upper)` caps values into a
  range, a quick way to tame outliers or negative quantities.
- Conditions combine with `&`, `|` and `~`, each comparison in its own brackets:
  `(df["a"] > 0) & (df["b"] == "NL")`. Python's `and`/`or` raise an error on a Series.
- `apply(axis=1)` is the fallback for logic that really needs several columns in a way the
  tools above cannot express. On 120,000 rows the lesson shows it gives the same result as
  `np.where`, only much slower.

Requires pandas (NumPy comes with it): `python -m pip install -r requirements.txt`

Run it: `python day31/lesson.py`

## Exercise
`solution.py` builds a fictional delivery table (fixed seed): order amount, weight, country
code and delivery days for a few hundred parcels, including some negative amounts (refunds),
unknown country codes and extreme weights.
1. add a `shipping` fee with `np.select`: refunds pay 0, orders of 75 or more ship free,
   parcels above 20 kg pay a heavy-parcel fee, everything else the standard fee;
2. map country codes to a zone with `Series.map`, putting unknown codes in an `"other"` zone
   and listing which codes were unknown;
3. cap weights into 0.1–30 kg with `clip` and replace negative delivery days by `NaN` with
   `where`;
4. flag late parcels (more days than the zone's promise) with one vectorised comparison;
5. compute the same columns with `apply(axis=1)` and a plain Python loop and check that all
   three agree.
Solution: `day31/solution.py`.
