# Day 19 - Reshaping records: rows, columns and nested data

The same table can be stored as a list of rows (one dict per record, what CSV readers and
JSON APIs return) or as columns (one list per field, how pandas stores a DataFrame). Real
data also arrives nested: dicts inside dicts and lists inside records. Being able to move
between these shapes with plain Python makes the jump to pandas (`DataFrame(rows)`,
`json_normalize`, `explode`) much easier to understand.

Key points:
- Rows -> columns: `{k: [r.get(k) for r in rows] for k in keys}`. Collect the union of keys
  with `dict.fromkeys(...)` so a field missing from some rows becomes `None` instead of an error.
- Columns -> rows: `[dict(zip(cols, vals)) for vals in zip(*cols.values())]`.
- `zip(*matrix)` transposes a list of lists.
- `zip` silently stops at the shortest input; `zip(..., strict=True)` (Python 3.10+) raises
  `ValueError` instead, which is what you want when columns must line up.
- Flatten nested dicts into dotted names (`meta.lat`) with a small recursive function.
- "Explode" a nested list into one row per item and copy the parent's fields onto each row
  with `{**parent, **item}`. Decide explicitly what happens to an empty list (drop the record
  or keep one row with `None`).

Run it: `python day19/lesson.py`

## Exercise
`solution.py` gets a fictional API response: a list of 150 orders, each with nested
`customer` info and a list of `items` (some orders have no items, some lack `customer.city`).
1. flatten each order (without its items) into dotted keys and turn the flat rows into
   columns, filling missing fields with `None`;
2. explode the orders into one row per item (order fields copied onto each line) and keep
   orders without items as a single row with `sku=None`;
3. rebuild the rows from the columns and check the round trip gives the same data;
4. check the totals: the sum of `qty * price` over the item rows equals the sum over the
   nested orders, and the number of item rows equals the number of items plus empty orders.
Solution: `day19/solution.py`.
