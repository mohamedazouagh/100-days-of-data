# Day 08 - Lazy pipelines with generators and itertools

Data files are often bigger than you want to hold in memory at once. Generators let you process
them one row at a time: each step pulls the next item only when it is needed. `itertools` adds the
building blocks (slicing, grouping, chaining) that work on any iterable, without pandas.

Key points:
- A function with `yield` is a **generator**: calling it returns an iterator and runs no code yet. Each `next()` resumes it until the next `yield`.
- Generators are **single-use**. Once exhausted they yield nothing; call the function again for a fresh one.
- Generator expressions `(x for x in ... if ...)` are the lazy twin of list comprehensions and feed straight into `sum`, `max`, `min`, `any`.
- `itertools.islice(it, n)` takes the first n items of any iterable - handy for peeking at a large file.
- `itertools.groupby(it, key=...)` groups **consecutive** items with the same key. Sort by the key first, or a key that appears twice gives two groups.
- `itertools.pairwise` (3.10+) yields neighbouring pairs, ideal for differences; `chain` glues iterables together.

Run it: `python day08/lesson.py`

## Exercise
`LOG` in `solution.py` holds a fictional web server's access log (time, path, status, milliseconds),
with comment lines and one malformed line. Using generators and `itertools` (no lists of the whole log):
1. write a generator that parses the log, skipping comments and counting malformed lines it drops;
2. per status class (2xx, 4xx, 5xx), report the number of requests and the average response time;
3. find the longest run of consecutive requests that were slower than 200 ms, with its start time;
4. print the first three requests to `/api/` paths using `islice`.
Solution: `day08/solution.py`.
