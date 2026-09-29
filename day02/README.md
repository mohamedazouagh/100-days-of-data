# Day 02 - Cleaning text with string methods

Real data arrives as messy strings: extra spaces, mixed case, European decimal commas, currency signs.
Before any analysis you turn those strings into clean, comparable values.

Key points:
- `strip()` removes surrounding whitespace, `lower()` / `title()` normalise case, so `" breda "` and `"Breda"` become the same key.
- `split(sep)` breaks a line into fields; `sep.join(parts)` puts them back together.
- `replace()` fixes formats: `"1.234,50"` -> remove the thousands dot, turn the comma into a point -> `float("1234.50")`.
- Wrap conversions in a small function so the cleaning rule lives in one place and can be tested.

Run it: `python day02/lesson.py`

## Exercise
`raw_prices` in `lesson.py` holds prices typed by hand (`"€ 12,50"`, `" 7.99 "`, `"1.020,00"`, ...).
Write `parse_price(text) -> float` that handles all of them, then print the average price rounded to 2 decimals.
Skip entries that are empty or `"n/a"`.
Solution: `day02/solution.py`.
