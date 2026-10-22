# Day 23 - Grouping and aggregating with groupby

Day 3 counted and grouped with dictionaries: loop over the rows, pick a key, add to a running
total. `groupby` is the same idea in one line. pandas calls it split-apply-combine: split the
rows by a key, apply a function to each group, combine the results into a new table.

Key points:
- `df.groupby("city")["revenue"].sum()` returns a Series indexed by the key, one value per
  group. Without picking a column first, the function runs on every column it can.
- `size()` counts **rows** per group; `count()` counts **non-missing values** per column. They
  differ as soon as a column has gaps, which makes the pair a quick missing-data check.
- `agg()` runs several functions in one pass. Named aggregation,
  `agg(units=("qty", "sum"), avg_price=("price", "mean"))`, gives the output columns readable
  names instead of a two-level header.
- Grouping by two keys gives a MultiIndex. `as_index=False` (or `.reset_index()` afterwards)
  keeps the keys as ordinary columns, which is usually what you want for further work.
- `sum()` skips NaN, so a group whose values are *all* missing sums to `0.0`, not NaN. Use
  `sum(min_count=1)` when "no data" must stay distinguishable from "zero".
- Groups come out sorted by key; `sort=False` keeps the order in which keys first appear.
- Rows whose key is missing are dropped silently. `dropna=False` keeps them as their own group,
  so totals still add up to the grand total.
- Filter on the aggregated result like any Series (`totals[totals > 15]`) and sort it with
  `sort_values`.

Requires pandas: `python -m pip install -r requirements.txt`

Run it: `python day23/lesson.py`

## Exercise
`solution.py` reuses the fictional webshop order lines from Day 22 (fixed seed) and adds a few
rows with a missing country.
1. compute total value per country with `groupby().sum()` and check the per-country totals add
   up to the grand total only when `dropna=False` is used;
2. build one summary table per category with named aggregation: number of order lines, units,
   total value, average unit price and the share of cancelled lines;
3. show the difference between `size()` and `count()` on a column with missing values;
4. total value per country and status with `as_index=False`, and the best-selling category per
   country;
5. find the categories whose average order value is above the overall average;
6. check every result against the same grouping done with plain dictionaries on the original
   list of dicts.
Solution: `day23/solution.py`.
