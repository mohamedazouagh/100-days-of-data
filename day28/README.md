# Day 28 - Text columns in pandas: the .str accessor

Day 02 cleaned strings one at a time and day 09 pulled data out of text with `re`. In pandas
a whole text column is cleaned in one expression: every `str` method has a vectorised twin
under `.str`, regexes work on the whole column, and missing values are carried along instead
of raising `AttributeError: 'NoneType' object has no attribute 'strip'`.

Key points:
- Text columns use the string dtype (`StringDtype`, the default since pandas 3). Missing
  values stay missing through every `.str` call, so a chain never crashes on a gap.
- `.str.strip()`, `.str.lower()`, `.str.replace(pattern, repl, regex=True)`: chain them to
  normalise spelling. A regex replace like `r"\s+"` -> `" "` collapses repeated spaces, and
  groups (`r"\1\2"`) let you rewrite formats such as `"1 l"` -> `"1l"`.
- `.str.contains(...)` returns a boolean mask. Pass `na=False` (or `True`) to decide what a
  missing value counts as, otherwise the mask itself has gaps and cannot filter.
- `.str.split(sep, expand=True)` turns the parts into columns; `.str.extract(regex)` does the
  same with named groups `(?P<name>...)` that become column names. Rows that do not match
  get NaN, which makes bad codes easy to find.
- Extracted parts are still text: convert with `.astype(int)` before comparing, so `"0012"`
  and `"12"` become the same number, and pad back with `.str.zfill(n)` for a clean key.
- `.str.len()` and `.str[:3]` work like `len()` and slicing. With missing values the length
  comes back as float (NaN is a float).

Requires pandas: `python -m pip install -r requirements.txt`

Run it: `python day28/lesson.py`

## Exercise
`solution.py` builds a fictional, messy product price list (fixed seed) as it might come out
of several suppliers: names with odd case and spacing, codes in two styles, prices as text
with a euro sign and a decimal comma, and pack sizes in ml, cl or l.
1. normalise the names (strip, lower case, single spaces) and count the distinct products;
2. turn every code into one key `GROUP-NNNN` with `.str.extract`, and list rows whose code
   does not match the pattern;
3. parse the price text (`"€ 1,89"`, `"1.89 EUR"`, ...) into a float column;
4. convert every pack size to millilitres and compute a price per litre;
5. check every number against plain Python loops over the original records.
Solution: `day28/solution.py`.
