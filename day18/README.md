# Day 18 - Function tools: partial, reduce, operator and lru_cache

Data cleaning code tends to grow into many small one-off lambdas. The `functools` and `operator`
modules let you build those steps out of small, named, reusable functions instead, and
`lru_cache` makes repeated slow lookups (an API, a big file, a heavy calculation) almost free.

Key points:
- `partial(func, arg=value)` returns a new function with some arguments already filled in,
  e.g. `partial(int, base=16)` is a hex parser.
- Small single-purpose functions can be chained into a pipeline; `compose(str.strip, str.lower, str.title)`
  in the lesson applies them left to right.
- `reduce(func, items, start)` folds a sequence into one value. `sum`, `max` and `min` are
  special cases; reach for `reduce` when the accumulator is something else, like a dict of totals.
- `operator.itemgetter("a", "b")` and `attrgetter("x")` replace `lambda r: (r["a"], r["b"])`
  and are handy as `key=` for `sorted`, `max` and `groupby`.
- `@lru_cache` stores results by argument. Only use it on **pure** functions (same input,
  same output, no side effects) with **hashable** arguments (a list raises `TypeError`).
- `func.cache_info()` shows hits and misses, `func.cache_clear()` empties the cache;
  `maxsize=None` never evicts, a number keeps only the most recently used results.

Run it: `python day18/lesson.py`

## Exercise
`solution.py` gets a fictional list of 2,000 delivery records with messy postcodes
(`" 4811ab"`, `"4811 AB"`, `"4811-ab"`) and amounts as strings.
1. build a `normalise_postcode` function by composing small steps (strip, upper-case, drop
   spaces and dashes, validate the `1234AB` shape) and use `partial` to make a
   `parse_amount` that turns strings like `"12,50"` into floats with a decimal comma;
2. total the amount per postcode area (first 4 digits) with `reduce`, and list the top 3 areas
   using `itemgetter` as the sort key;
3. wrap a deliberately slow `area_to_region` lookup in `lru_cache` and show from
   `cache_info()` that one call per valid record caused only one miss per distinct area;
4. check that cached and uncached results are identical and that invalid postcodes are
   counted, not silently dropped.
Solution: `day18/solution.py`.
