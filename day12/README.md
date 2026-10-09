# Day 12 - Typed records with dataclasses

Dicts are fine for a quick script, but `row["qyt"]` fails only at runtime and nothing tells you
which fields a record should have. A `@dataclass` gives each record a fixed set of named, typed
fields, a readable `repr`, equality and (optionally) ordering and immutability, without
writing any boilerplate.

Key points:
- `@dataclass` generates `__init__`, `__repr__` and `__eq__` from the annotated fields.
- Defaults go after required fields; use `field(default_factory=list)` for mutable defaults.
- `frozen=True` makes instances read-only (and hashable, so they can go in sets and dict keys).
- `order=True` compares records field by field in declaration order, so `sorted()` just works.
- `__post_init__` runs after `__init__`: the place to validate or derive values.
- A `@property` computes a value from other fields on demand (e.g. a line total).
- `dataclasses.asdict()` turns a record back into a dict, ready for `csv.DictWriter` or `json`.
- `dataclasses.replace(rec, field=...)` returns a modified copy of a frozen record.

Run it: `python day12/lesson.py`

## Exercise
`ROWS` in `solution.py` holds fictional stock movements as dicts of strings (sku, warehouse, date, change).
1. define a frozen, ordered `Movement` dataclass with a `from_row(row)` classmethod that converts
   the types and rejects a zero change with `ValueError`;
2. sort the movements (by sku, then warehouse, then date, via `order=True`);
3. compute the closing stock per `(sku, warehouse)` and list the pairs that went negative at any point;
4. write the sorted movements back out as CSV text with `asdict()` and `csv.DictWriter`.
Solution: `day12/solution.py`.
