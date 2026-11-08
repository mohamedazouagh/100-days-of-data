# Day 36 - Dtypes and memory: to_numeric, nullable Int64/boolean, category and memory_usage

Data often arrives as text: a CSV with one `n/a` in a number column, JSON with numbers in
quotes, a spreadsheet export with `yes`/`no` flags. Until the columns have the right dtype,
sums, comparisons and sorting either fail or silently work on strings (`"10" < "9"`). Getting
the dtypes right is also the cheapest way to make a frame smaller and faster.

Key points:
- `astype(float)` is strict: a single bad cell raises. `pd.to_numeric(s, errors="coerce")`
  turns every unparsable cell into `NaN` instead, so always list what was lost
  (`raw[converted.isna() & raw.notna()]`) rather than dropping it blindly. Fix known formats,
  like a decimal comma, before converting.
- A classic `int64` column can't hold missing values, so pandas falls back to `float64` and
  `3` becomes `3.0`. The nullable `"Int64"` dtype (capital I) keeps integers and shows gaps as
  `<NA>`; `sum()` and `mean()` skip them.
- The nullable `"boolean"` dtype does the same for flags: map known text to `True`/`False`
  and anything else stays `<NA>` instead of quietly counting as `False`.
- Columns with few distinct labels (country, sensor id, status) are much smaller as
  `"category"`: each row stores a small integer code plus one shared list of labels.
- `pd.to_numeric(..., downcast="float")` or `downcast="integer"` picks the smallest type that
  fits; only worth it for big frames, and float32 has ~7 significant digits.
- `df.memory_usage(deep=True)` measures the real size including the strings. Without
  `deep=True` object columns count only their 8-byte pointers and look far too small.
- pandas 3 stores text columns as the `str` dtype by default (older versions show `object`);
  the conversions above work the same on both.

Requires pandas: `python -m pip install -r requirements.txt`

Run it: `python day36/lesson.py`
