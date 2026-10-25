# Day 25 - Combining tables with merge and concat

Day 20 joined two lists of records by key with a dictionary. In pandas the same job is one
`merge` call, and stacking several exports with the same columns is one `concat` call. The
hard part is not the syntax but knowing which rows you keep and noticing when a join quietly
adds or drops rows.

Key points:
- `left.merge(right, on="key", how=...)` matches rows on equal key values. `how="inner"`
  (the default) keeps keys present in both tables, `"left"` keeps every left row, `"right"`
  every right row and `"outer"` everything. Unmatched cells become NaN.
- A left join that finds no match still keeps the row, so check for NaN in a column from the
  right table to find orphans (orders for products that don't exist).
- `indicator=True` adds a `_merge` column (`both`, `left_only`, `right_only`) that shows where
  each row came from: the quickest way to audit an outer join.
- If the key is repeated on the "one" side, every match is duplicated and totals grow without
  any error. `validate="many_to_one"` (or `"one_to_one"`, `"one_to_many"`) raises
  `MergeError` instead. Compare row counts before and after any join.
- NaN appearing in an integer column turns it into floats (see `order_id` in the outer join).
- When the key columns have different names use `left_on=` / `right_on=`; both columns are
  kept, so drop the extra one afterwards.
- `pd.concat([a, b])` stacks tables with the same columns. The original indexes are kept, so
  pass `ignore_index=True` for a fresh 0..n-1 index, or `keys=[...]` to remember which table
  each row came from.

Requires pandas: `python -m pip install -r requirements.txt`

Run it: `python day25/lesson.py`

## Exercise
`solution.py` builds a fictional webshop (fixed seed): a customer table, a product table with
one discontinued product, and two monthly order exports. Some orders point at a customer id or
SKU that does not exist.
1. stack the two monthly exports with `concat`, keeping the month as a column, and check the
   row count;
2. join orders to products with a left join and `validate="many_to_one"`, count the orders
   with an unknown SKU and compute revenue per order;
3. use an outer join with `indicator=True` to list products that were never ordered;
4. join customers to get revenue per city (inner join, so orphan orders drop out) and check
   that the row count only fell by the orphan orders;
5. show that duplicating one product row makes the plain merge return more rows and makes
   `validate` raise `MergeError`;
6. check every result against the same joins written with plain dicts.
Solution: `day25/solution.py`.
