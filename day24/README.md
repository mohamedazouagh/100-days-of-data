# Day 24 - Missing values and duplicates in pandas

Day 11 handled bad data row by row with `try`/`except` and validation. Real exports are rarely
clean, and in pandas most of the cleanup is a few column-wide calls. Today covers the two
problems you meet first: values that are missing (or only look present) and rows that appear
more than once.

Key points:
- pandas marks a missing number as `NaN` and a missing object as `None`/`NaN`. `isna()` gives a
  True/False table; `df.isna().sum()` counts gaps per column and `df.isna().any(axis=1)` finds
  the rows that have at least one.
- Placeholders are **not** missing until you convert them: an empty or whitespace-only string,
  `"n/a"`, `"-"` or `0` used as "unknown" all pass `isna()`. Strip and `replace(..., np.nan)`
  first, otherwise every count and average afterwards is wrong.
- `dropna()` drops rows with a gap anywhere; `subset=[...]` only looks at the columns that matter
  for the question, and `thresh=n` keeps rows with at least `n` filled values.
- `fillna({...})` takes one fill value per column. Use a label such as `"unknown"` for text and a
  statistic (median is robust to outliers) for numbers, and only when the fill makes sense for
  the analysis.
- Statistics such as `mean()` skip NaN. Filling with `0` is a different claim ("no orders")
  than leaving it missing ("we don't know") and pulls the average down.
- `duplicated()` flags repeats of earlier rows. Without arguments only identical rows count;
  `subset=["customer_id"]` treats the same id as a duplicate even when other columns changed.
- `drop_duplicates(subset=..., keep="first" | "last")` chooses which copy survives. When the
  later row is the newer export, `keep="last"` keeps the up-to-date values.

Requires pandas: `python -m pip install -r requirements.txt`

Run it: `python day24/lesson.py`

## Exercise
`solution.py` builds a fictional customer export (fixed seed) where some customers appear twice
with an updated order count, some emails are blank or whitespace, cities use `"n/a"` and `"-"`
as placeholders, and some ages and order counts are missing.
1. count the missing values per column before and after turning placeholders into real NaN;
2. drop repeated customer ids, keeping the last (newest) row, and check that every id is now
   unique and that each kept row is the last one of its id;
3. count the customers that can be emailed (`dropna(subset=["email"])`);
4. fill missing cities with `"unknown"` and missing ages with the median age, and leave missing
   order counts alone;
5. compare the average order count with NaN skipped against NaN filled with 0;
6. check every result against the same cleanup written with plain Python on the list of dicts.
Solution: `day24/solution.py`.
