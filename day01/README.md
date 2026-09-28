# Day 01 — Python types for data work

The four types you'll use constantly before pandas: `int`, `float`, `str`, `bool`, plus the containers `list` and `dict`.

Key points:
- `0.1 + 0.2 != 0.3` — floats are approximate. Compare with `math.isclose`, or round money.
- A list of dicts is the "table" of plain Python. Each dict is a row.
- `sum()`, `min()`, `max()` with a generator expression answer most simple questions.

Run it: `python day01/lesson.py`

## Exercise
Using the `sales` list in `lesson.py`, find the total revenue per city (price × qty).
Solution: `day01/solution.py`.
