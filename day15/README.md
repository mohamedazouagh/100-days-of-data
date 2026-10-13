# Day 15 - Exact money maths with decimal

Floats are binary fractions, so most amounts with cents (0.10, 0.20, 2.675) cannot be stored
exactly. For averages and charts that tiny error is harmless, but for invoices, VAT and
reconciliations it shows up as totals that are off by a cent. `decimal.Decimal` stores
base-10 digits exactly and lets you choose how to round.

Key points:
- `0.1 + 0.2 == 0.3` is False with floats; with `Decimal("0.1") + Decimal("0.2")` it is True.
- Build decimals from **strings** (`Decimal("19.99")`), not floats: `Decimal(19.99)` copies the float's error.
- `amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)` rounds to cents the way most invoices expect.
  The default, `ROUND_HALF_EVEN` (banker's rounding), is what Python's `round()` uses: `round(2.5) == 2`.
- `round(2.675, 2)` gives `2.67` because the float is really 2.67499999...; the Decimal version gives `2.68`.
- Round each line *or* round the total: the two can differ by a cent, so pick one rule and document it.
- Splitting money (e.g. 100.00 over 3) leaves a remainder cent; hand it out explicitly so the parts add up.
- `sum()` works on Decimals (start value `Decimal("0")` keeps the type even for an empty list).
- Mixing `Decimal` and `float` in arithmetic raises `TypeError`, which is a feature: it catches silent float leaks.

Run it: `python day15/lesson.py`

## Exercise
`solution.py` holds a fictional shop invoice: lines with a unit price (string), a quantity and a VAT rate (21 % or 9 %).
1. compute each line's net amount and VAT, rounded to cents with `ROUND_HALF_UP`;
2. print the invoice net, VAT per rate and grand total, and show how a naive float script (no per-line rounding) ends up a cent off;
3. compare "round per line" with "round the total" for the VAT and report the difference in cents;
4. split the grand total over 3 people so the shares differ by at most one cent and add up exactly.
Solution: `day15/solution.py`.
