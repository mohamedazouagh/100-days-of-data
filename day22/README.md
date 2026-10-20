# Day 22 - Selecting, filtering and sorting rows in pandas

Day 21 was about looking at a DataFrame. Today is about getting the rows and columns you
want out of it. In Phase 1 that was a list comprehension with an `if`; in pandas it is a
boolean mask, and the same mask can also be used to change only the matching rows.

Key points:
- `loc` selects by **label** (index values, column names); `iloc` by **position**.
  `df.loc[102:104]` includes 104, `df.iloc[1:3]` stops before position 3, like a list slice.
- A comparison on a column (`df["qty"] >= 2`) gives a boolean Series, one value per row.
  `df[mask]` keeps the rows where it is True.
- Combine masks with `&` (and), `|` (or) and `~` (not), with parentheses around each part:
  `(df["city"] == "Breda") & (df["qty"] >= 2)`. Python's `and`/`or` raise an error here.
- `isin([...])` means "one of these values", `between(lo, hi)` is an inclusive range.
- `query("city != 'Gouda' and qty >= @min_qty")` is the same filter as a string; `@name`
  pulls in a Python variable. Handy for long conditions, but typos only fail at run time.
- `df.loc[mask, ["a", "b"]]` filters rows and picks columns in one step. Assigning through it
  (`df.loc[mask, "price"] = 3.25`) changes only those rows and avoids the
  "chained assignment" trap of `df[mask]["price"] = ...`, which edits a temporary copy.
- Columns are stored values, not spreadsheet formulas: after changing `price`, a `revenue`
  column computed earlier keeps its old numbers until you recompute it.
- `sort_values(["city", "revenue"], ascending=[True, False])` sorts by several keys with
  mixed directions; `nlargest(n, col)` / `nsmallest` are quick top-N shortcuts.

Requires pandas: `python -m pip install -r requirements.txt`

Run it: `python day22/lesson.py`

## Exercise
`solution.py` builds 300 fictional webshop order lines (order id, date, country, category,
quantity, unit price, status) from a fixed seed.
1. select with `loc` and `iloc` and show that a label slice includes its end while a position
   slice does not;
2. find all shipped orders from NL or BE worth at least 50 (quantity × price) with a boolean
   mask, and get the same rows with `query()`;
3. list the orders placed in the first week of October with `between()` on the dates;
4. mark every cancelled order's quantity as 0 through `loc`, recompute the line value and
   show that only the cancelled rows changed;
5. sort by country (A-Z) then value (high to low) and show the top 3 orders per country;
6. check every result against the same filter written in plain Python on the original list
   of dicts.
Solution: `day22/solution.py`.
