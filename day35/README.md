# Day 35 - Group-wise operations beyond agg: transform, cumcount, filter, nth and idxmax

Day 23's `groupby(...).agg(...)` answers "one number per group": it shrinks the table to one
row per key. Many real questions need the group result *back on every row*: what share of the
customer's spend is this order, is it their 1st or 4th order, how many days since their last
one, which order was their biggest. Doing that with `agg` plus a `merge` works, but groupby
has methods that keep the original rows and index, so the answer lines up automatically.

Key points:
- `g["amount"].transform("sum")` returns one value per **original row** (same index), so it can
  be assigned straight into a new column: shares, deviations from the group mean, ranks.
- A function passed to `transform` receives each group as a Series and must return a Series of
  the same length or a scalar (broadcast). Guard small groups (a std of one value is 0 or NaN).
- `cumcount()` numbers rows within each group 0, 1, 2, ... **in the current row order**, so
  `sort_values` first. `cumsum()`, `cummax()` and `diff()` on a grouped column work the same way
  and restart at every new key (the first `diff` per group is NaN).
- `filter(func)` keeps or drops **whole groups** based on a condition on the group, and returns
  the original rows, not one row per group.
- `head(n)` and `nth(k)` pick rows by position inside each group, keeping the original index;
  groups with fewer rows are simply skipped by `nth`.
- `idxmax()` per group gives the index label of the max row; `df.loc[...]` with those labels
  pulls out the whole row. On ties it returns the first occurrence.

Requires pandas: `python -m pip install -r requirements.txt`

Run it: `python day35/lesson.py`

## Exercise
`solution.py` builds a fictional log of gym visits (fixed seed): member, date, minutes.
1. add each visit's share of the member's total minutes and its difference from the member's
   average, using `transform`;
2. number every member's visits in date order with `cumcount`, add the running total of minutes
   and the gap in days since the previous visit;
3. keep only members with at least 4 visits using `filter` and report the longest gap any of
   them had between two visits;
4. find each member's longest visit with `idxmax` and their first visit with `head(1)`;
5. check every result against a plain Python version built with dicts and sorted lists.
Solution: `day35/solution.py`.
