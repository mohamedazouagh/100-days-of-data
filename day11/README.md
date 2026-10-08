# Day 11 - Handling bad data with exceptions and validation

Real exports contain blanks, typos and impossible values. A pipeline that crashes on row 4,812
is useless, and one that silently skips rows is worse. The pattern: parse each row inside
`try`/`except`, keep the good rows, and collect the bad ones *with a reason* so you can report them.

Key points:
- Catch the specific error you expect (`ValueError`, `KeyError`), never a bare `except:`.
- `int("")`, `float("abc")` and `date.fromisoformat("2026-13-01")` all raise `ValueError`.
- `raise ValueError("message")` from your own checks so parse errors and rule violations look the same.
- `try / except / else / finally`: `else` runs only when nothing failed, `finally` always runs.
- Collect rejects as `(line_number, reason)`; count them and fail loudly above a threshold.
- `str(exc)` gives the message; `type(exc).__name__` gives the error class for summaries.

Run it: `python day11/lesson.py`

## Exercise
`RAW` in `solution.py` holds fictional order lines as strings (id, date, quantity, unit price).
1. write `parse_order(row)` that returns a clean dict or raises `ValueError` with a clear reason
   (missing field, bad number, bad date, quantity must be positive, price must not be negative);
2. split the rows into `good` and `rejected` (`(line, reason)` pairs, line numbers from 1);
3. compute total revenue from the good rows only;
4. count rejects per reason category and stop with an error if more than 40% of rows are bad.
Solution: `day11/solution.py`.
