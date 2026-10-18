# Day 20 - Joining datasets by key with dicts

Most analysis questions need two tables at once: orders and customers, readings and
stations, sales and prices. A join matches rows on a shared key. Writing joins by hand with
dicts shows exactly what pandas `merge` (Phase 2) and SQL `JOIN` (Phase 3) do, and why the
classic join bugs happen: rows that disappear, rows that multiply, and keys that never match.

Key points:
- Build an index of the "one" side first: `{row[key]: row}`. Each lookup is then O(1), so the
  join is O(n + m) instead of a nested loop's O(n * m).
- Check that the index key is unique. A duplicate on the "one" side silently overwrites in a
  dict (and multiplies rows in pandas/SQL), so fail loudly instead.
- Inner join: keep only rows that match on both sides. Left join: keep every left row and fill
  the right-hand fields with `None` when there is no match (`index.get(k, empty)`).
- Anti join: rows with *no* match (`k not in right_keys`) - the quickest way to find orphans
  such as orders for unknown customers or customers without orders.
- One-to-many: group the "many" side with `defaultdict(list)` and aggregate per key; keys
  with no rows should give 0, not vanish.
- Sanity-check every join: a left join on a unique key must return exactly as many rows as
  the left table; compare totals before and after.

Run it: `python day20/lesson.py`

## Exercise
`solution.py` gets three fictional tables: 40 products (with one duplicated product id that
must be detected and resolved), 300 sales lines (a few with product ids that do not exist)
and a list of category targets.
1. build a unique product index, reporting the duplicate id and keeping its first row;
2. left-join the sales lines onto the products and count lines with an unknown product;
3. list products that never sold (anti join) and sales for unknown products;
4. compute revenue per category (one-to-many) and compare it with the targets, flagging
   categories below target;
5. check that the left join kept every sales line and every unit sold, and that the
   per-category revenue adds up to the revenue of all lines with a known product (unknown
   products have no price, so they are reported by quantity instead).
Solution: `day20/solution.py`.
