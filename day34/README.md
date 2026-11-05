# Day 34 - Reading messy CSVs with read_csv: separators, decimals, missing markers and chunks

So far every DataFrame was built from Python lists and dicts. Real data mostly arrives as a
CSV export, and exports are rarely "comma-separated with a dot as decimal mark". A Dutch till
system or Excel in a Dutch locale writes semicolons, decimal commas and dots as thousands
separators, adds a title line and a total line, and spells "missing" in its own way. The fix
is not cleaning strings afterwards but telling `read_csv` what the file looks like.

Key points:
- A plain `pd.read_csv(path)` on such a file either fails with a `ParserError` (step 1) or,
  worse, reads everything as text. Look at the first lines of the raw file before reading.
- `sep=";"` sets the field separator, `decimal=","` and `thousands="."` turn `1.188,00` into
  `1188.0`. `skiprows=1` skips lines above the header; `skipfooter=1` drops trailing lines
  but only works with `engine="python"`.
- `na_values=["n/a", "-"]` adds markers that mean missing on top of the defaults (empty,
  `NA`, `NaN`, ...).
- `dtype=` fixes types up front: `"string"` keeps codes like `0042` with their leading zeros,
  `"Int64"` keeps whole numbers as integers even with gaps (otherwise they become `float64`).
  In pandas 3 text columns get the `str` dtype by default.
- Parse dates with an explicit format, `pd.to_datetime(col, format="%d-%m-%Y")`: day-first
  dates like `03-11-2026` are ambiguous and a guess can silently swap day and month.
- `usecols=[...]` reads only the columns you need; `chunksize=N` returns an iterator of
  DataFrames so a file bigger than memory can be aggregated piece by piece. `skipfooter`
  can't be combined with chunks, so filter the total line inside the loop.
- Quirk seen in pandas 3.0: the default C parser does not apply `thousands=` when a column is
  read straight into `Int64` (`TypeError`), so the chunked read in step 5 uses the python engine.
- The sum of an all-missing `Int64` group is `0`, not missing (Gouda in step 5): check counts
  when that difference matters.
- `to_csv(sep=";", decimal=",", index=False, date_format=...)` writes a file the same tools can
  read back.

Requires pandas: `python -m pip install -r requirements.txt`

Run it: `python day34/lesson.py`

## Exercise
`solution.py` generates a fictional bank-style export (fixed seed) with a two-line preamble,
semicolons, decimal commas, thousands dots, day-first dates, IBAN-like account codes with
leading zeros, `"--"` for missing amounts and a closing balance line.
1. read it in one `read_csv` call with the right options and check the dtypes;
2. parse the dates and report the totals of debits and credits per month;
3. read it again with `chunksize` and get the same per-month totals without loading it at once;
4. check every number against a plain `csv`-module parse of the same text.
Solution: `day34/solution.py`.
