# Day 26 - Reshaping tables: melt, pivot, pivot_table and stack

Day 19 reshaped plain records between rows and columns by hand. Spreadsheet exports usually
arrive "wide" (one column per month or per product), while filtering, grouping and joining
are easiest on "long" data (one row per observation). pandas converts between the two in one
call each way; the traps are duplicates and the column types you end up with.

Key points:
- `df.melt(id_vars=..., var_name=..., value_name=...)` turns wide into long: the `id_vars`
  columns are repeated and every other column becomes a `(variable, value)` pair. Rows in =
  rows out times the number of melted columns, NaN cells included.
- Long data needs no special code for gaps: a missing month is just a NaN row that
  `dropna(subset=...)` removes, and `groupby` works on any column.
- `pivot(index, columns, values)` turns long back into wide. It refuses to guess and raises
  `ValueError` if any `(index, column)` pair appears more than once.
- `pivot_table(...)` is pivot plus an aggregation (`aggfunc="sum"`, `"mean"`, ...), so it
  accepts duplicates. `fill_value=` fills empty cells and `margins=True` adds row/column
  totals. Beware: `fill_value=0` hides the difference between "zero" and "not reported".
- `stack()` moves the columns into the index (wide -> a long Series with a MultiIndex, NaN
  dropped); `unstack(level)` moves an index level back into the columns, which is also an
  easy way to transpose one dimension.
- After `melt` the old column headers are text. Parse them (`pd.to_datetime(..., format=)`)
  before sorting or resampling by date, otherwise "2026-10" vs "2026-9" sorts as strings.
- Integer columns with a NaN become floats; convert back with `astype("Int64")` if needed.

Requires pandas: `python -m pip install -r requirements.txt`

Run it: `python day26/lesson.py`

## Exercise
`solution.py` builds a fictional monthly sales sheet (fixed seed) in wide format: one row per
store and product, one column per month, with a few months not reported.
1. melt it to long format, parse the month column to dates and drop the unreported cells;
2. pivot back to a store x month table of total sales with `pivot_table` and margins, and
   check that the grand total equals the sum of the long table;
3. show that `pivot` on store x month raises `ValueError` (several products per store) while
   `pivot` on (store, product) x month round-trips to the original sheet;
4. find each store's best month with `stack`/`idxmax`;
5. check every number against plain Python loops over the original rows.
Solution: `day26/solution.py`.
