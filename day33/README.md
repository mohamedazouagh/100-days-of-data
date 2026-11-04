# Day 33 - The index and MultiIndex: set_index, loc, xs, IndexSlice and alignment

Until now the row index was mostly the default 0, 1, 2, ... and we called `reset_index` to get
rid of anything else. But the index is more than a row number: it is the set of labels pandas
uses to select rows and to line up two tables in arithmetic. When data has a natural key, like
(city, museum, month), putting that key in the index makes lookups short and makes
comparisons between tables match by label instead of by position.

Key points:
- `df.set_index(["city", "museum", "month"])` moves columns into a **MultiIndex**: every row
  is labelled by a tuple. Call `sort_index()` afterwards; slicing a MultiIndex needs it sorted.
- `df.loc["Delft"]` or `df.loc[("Breda", "Kasteel")]` selects by the outer level(s) and drops
  those levels from the result. A full tuple plus a column name gives a single cell.
- `df.xs("2026-10", level="month")` selects on an inner level without naming the outer ones.
- `pd.IndexSlice` slices several levels at once: `df.loc[idx[:, ["A", "B"], "2026-09"], :]`
  means "any city, these two museums, September".
- `unstack("month")` turns an index level into columns (a wide view, good for per-row growth
  rates); `stack` goes back. `groupby(level="city")` groups by an index level directly.
- Arithmetic between two Series or DataFrames **aligns on the index**: rows are matched by
  label, whatever their order, and a label missing on one side gives `NaN` (step 7). That is
  usually what you want, but it also means a mistyped key silently becomes `NaN`.
- `reset_index()` turns the levels back into ordinary columns before saving or plotting.

Requires pandas: `python -m pip install -r requirements.txt`

Run it: `python day33/lesson.py`

## Exercise
`solution.py` builds a fictional weekly sales table for a few shops and products (fixed seed)
and a separate target table in a shuffled order with one shop-product pair missing.
1. index the sales by (shop, product, week) and look up: one shop's rows, one exact cell, and
   all shops for one week with `xs`;
2. use `IndexSlice` to get two products over the last two weeks for every shop;
3. `unstack` the weeks and compute each shop-product's change from the first to the last week;
4. compare total sales per (shop, product) with the shuffled targets by index alignment, list
   the pairs without a target, and check every number against a plain Python dict version.
Solution: `day33/solution.py`.
