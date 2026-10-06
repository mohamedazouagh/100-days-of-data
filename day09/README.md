# Day 09 - Extracting data from text with regular expressions

Real datasets hide structured values inside free text: order numbers in comments, amounts in
email bodies, dates in log lines. String methods (day 02) handle fixed patterns; the `re` module
handles "a letter, a dash, then four digits" style patterns in one line.

Key points:
- Always write patterns as raw strings `r"..."` so `\d` and `\s` reach `re` unchanged.
- `re.compile` once, reuse many times. The compiled pattern has the same methods as the module.
- `search` finds the first match anywhere and returns `None` if there is none; check before calling `.group()`.
- `findall` returns all captures as strings; `finditer` yields match objects (with `.span()`) lazily.
- Named groups `(?P<name>...)` make patterns readable: `m["name"]` or `m.groupdict()`.
- `fullmatch` is for validation: the *whole* string must match, unlike `search`.
- `sub` rewrites matches and can reuse captures with `\g<name>`; `re.VERBOSE` lets long patterns carry comments.
- `re.IGNORECASE` also makes character classes like `[A-Z]` match lowercase letters.

Run it: `python day09/lesson.py`

## Exercise
`TICKETS` in `solution.py` holds fictional support-ticket subject lines with messy formatting.
Using only `re` (no manual `split`/`find` parsing):
1. extract every ticket ID (`TCK-` plus 4 digits, any case) and return them upper-cased, without duplicates, in first-seen order;
2. extract amounts written as `EUR 12.50`, `€12,50` or `12.50 EUR` and convert each to integer cents;
3. normalise dates written as `2026-10-03` or `03/10/2026` (day first) to ISO `YYYY-MM-DD`;
4. validate a list of product codes (`ABC-123`: 3 capital letters, dash, 3 digits) with `fullmatch`.
Solution: `day09/solution.py`.
