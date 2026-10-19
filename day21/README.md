# Day 21 - pandas basics: Series and DataFrame

Phase 2 starts here. Everything from Phase 1 (lists of dicts, loops, `statistics`, joins by
hand) still works, but pandas stores a table column by column, so one line of code runs over
every row at once and missing values are handled for you. Today is only about the two core
objects and about looking at data before touching it.

Key points:
- A `Series` is one labelled column: values plus an index. Select by label with `s["tue"]`
  and by position with `s.iloc[0]`; the two are different as soon as the index is not 0..n-1.
- A `DataFrame` is a set of Series sharing one index. Build it from records
  (`pd.DataFrame(list_of_dicts)`) or from columns (`pd.DataFrame({"col": [...]})`).
- Inspect first: `shape`, `dtypes`, `isna().sum()`, `head()`. Most later bugs are a wrong
  dtype (numbers or dates stored as text) that these four calls would have shown.
- Convert types explicitly: `pd.to_datetime` for dates, `pd.to_numeric` for numbers read as
  text. pandas will not guess for you.
- `df["col"]` returns a Series, `df[["a", "b"]]` a DataFrame.
- Arithmetic and comparisons are vectorised (`df["t"] * 9 / 5 + 32`, `df["rain"] > 0`), and
  aggregations such as `mean()` and `count()` skip missing values (NaN) by default.
- `describe()` summarises every numeric (and datetime) column in one call.

Requires pandas: `python -m pip install -r requirements.txt`

Run it: `python day21/lesson.py`

## Exercise
`solution.py` gets 200 fictional sensor readings as a list of dicts (station, timestamp as
text, temperature, humidity), where a few temperatures and humidities are missing.
1. build a DataFrame and report its shape, dtypes and missing values per column;
2. convert the timestamp column to datetimes and report the first and last reading;
3. add a temperature-in-Fahrenheit column and a `humid` flag (humidity above 80%);
4. compute count, mean, min and max of temperature and humidity with pandas;
5. check every number from step 4 against a plain-Python computation on the original
   records (skipping missing values), so the pandas version is proven to match Phase 1.
Solution: `day21/solution.py`.
