# Day 14 - Comparing datasets with sets

A lot of data work is comparing two lists: which customers are in the CRM but not in billing,
which product codes appeared this week, which IDs are duplicated. A `set` stores unique,
hashable values and answers "is this in here?" in constant time, so these questions become
one-line set operations instead of nested loops.

Key points:
- `set(values)` drops duplicates; `x in s` is O(1) on average, `x in some_list` is O(n).
- `a | b` union (in either), `a & b` intersection (in both), `a - b` difference (only in a),
  `a ^ b` symmetric difference (in exactly one).
- `a <= b` asks "is a a subset of b?"; `a.isdisjoint(b)` is True when nothing is shared.
- Sets have no order: `sorted(s)` before printing or writing, so output is reproducible.
- Normalise before comparing (`strip().lower()`): `"Ann@x.nl "` and `"ann@x.nl"` are different set members.
- To dedupe but keep the first-seen order, use `list(dict.fromkeys(values))`.
- Only hashable values go in a set: strings, numbers, tuples. Use a tuple for composite keys like `(date, sku)`.
- Jaccard similarity `len(a & b) / len(a | b)` gives one number (0 to 1) for how much two sets overlap.

Run it: `python day14/lesson.py`

## Exercise
Two fictional systems export customer e-mail addresses: `CRM` and `BILLING` in `solution.py`.
The exports are messy (different case, stray spaces, duplicates, blank values).
1. normalise both lists (strip, lowercase, drop blanks) and dedupe them while keeping the first-seen order;
2. report customers only in the CRM, only in billing, and in both (sorted);
3. find e-mail addresses that appear more than once in the raw CRM export (after normalising);
4. compute the Jaccard overlap of the two systems, and the share of billing customers that are known to the CRM.
Solution: `day14/solution.py`.
