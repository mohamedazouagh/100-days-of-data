# Day 29 - Categories and binning in pandas: category dtype, cut and qcut

Day 27 grouped by dates and day 28 cleaned text. Many text columns only ever hold a handful
of labels (sizes, regions, ratings), and many numeric columns are easier to report as bands
(age groups, spend tiers). pandas has one dtype for both: `category`. It stores each label
once plus a small integer code per row, can carry a real order, and keeps empty groups
visible in reports.

Key points:
- `pd.CategoricalDtype([...], ordered=True)` fixes the allowed labels and their order.
  Sorting, `min`/`max` and comparisons like `size >= "L"` then follow that order instead of
  the alphabet (`"L" < "M" < "S" < "XL"` alphabetically).
- Labels outside the categories turn into NaN on conversion (newer pandas warns that this
  will raise). Check first with `~s.isin(dtype.categories)` and decide what to do with them.
- `pd.cut(values, bins=[...], labels=[...])` puts numbers into bands with edges you choose.
  Bins are `(low, high]` by default; `right=False` makes them `[low, high)`, which is what
  "18-29" usually means. Values outside all bins become NaN.
- `pd.qcut(values, q=4)` picks the edges from quantiles so every bin gets about the same
  number of rows. `retbins=True` also returns the edges, which you will want to report.
- Both return an ordered categorical. In `groupby`, `observed=False` keeps empty categories
  as rows with a count of 0 (the default since pandas 3 is `observed=True`, which drops them).
- With many rows and few distinct labels, `category` uses far less memory than text.

Requires pandas: `python -m pip install -r requirements.txt`

Run it: `python day29/lesson.py`

## Exercise
`solution.py` builds a fictional webshop order log (fixed seed) with a shirt size, a customer
age, a basket amount and a delivery time in hours for every order.
1. turn the sizes into an ordered category (`XS` < `S` < `M` < `L` < `XL`), list the rows with
   an unknown size, and count orders per size in size order, including sizes nobody bought;
2. band the ages with `pd.cut` into `<18`, `18-29`, `30-44`, `45-64`, `65+` (left-closed);
3. split the amounts into four equal-sized spend tiers with `pd.qcut` and report the edges;
4. band the delivery times into `same day` (< 24 h), `next day` (< 48 h) and `later`, and
   build an age band x delivery band count table that keeps empty combinations;
5. check every count and band against plain Python loops over the original records.
Solution: `day29/solution.py`.
