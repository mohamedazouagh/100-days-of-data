# Day 32 - Method chaining in pandas: assign, query, pipe and eval

After a few days of pandas, analysis scripts tend to look like a long list of `df = ...` and
`df["x"] = ...` lines. Each one changes the same variable, so it gets hard to see which step
produced what, and re-running a notebook cell twice can quietly apply a step twice. Method
chaining writes the whole transformation as one expression that reads top to bottom, starting
from the raw table and never changing it.

Key points:
- `df.assign(new=lambda d: ...)` returns a **new** DataFrame with the extra column. The lambda
  gets the frame as it is at that point in the chain, so it sees earlier filters and columns.
  Later keyword arguments in the same `assign` call can use columns made by earlier ones.
- `df.query("qty > 0 and shop != 'Gouda'")` filters with a string expression. Use `@name` for a
  Python variable and backticks for column names with spaces: ``query("`unit price` > 2")``.
- `df.pipe(func, *args)` is `func(df, *args)`, so your own functions slot into the chain. A tiny
  "tap" function that prints the shape and returns the frame unchanged is a handy debugger.
- `df.eval("qty * unit_price")` computes column arithmetic from a string; good for short
  formulas, while `assign` with a lambda stays readable when the logic grows.
- Wrap the chain in brackets and put one step per line, so steps can be commented out.
- The trap: inside `assign`, always use the lambda's argument `d`, not the original variable.
  After a filter plus `reset_index` the row labels no longer match, and values from the
  original table land on the wrong rows without any error (step 7 of the lesson shows it).

Requires pandas: `python -m pip install -r requirements.txt`

Run it: `python day32/lesson.py`

## Exercise
`solution.py` builds a fictional web-shop order log (fixed seed) with order lines, a few
cancelled orders, zero quantities, voucher codes and a column name with a space.
1. clean the log in one chain: drop cancelled orders and zero quantities with `query`, and
   add `gross`, `voucher_off` and `net` columns with a single `assign`;
2. write two small functions, `add_order_size` (bins orders into small / medium / large by
   order total) and `tap` (prints the shape), and use them with `pipe`;
3. build a per-category summary (orders, units, net revenue, average net per order) at the end
   of the same chain, sorted by revenue;
4. check that the chain leaves the raw log untouched and gives exactly the same numbers as the
   step-by-step version and a plain Python loop over the records.
Solution: `day32/solution.py`.
