# Day 10 - Sorting, ranking and top-N

"Top 5 products", "rank stores by revenue", "latest order per customer": most reports start
with an ordering. Python's `sorted` plus a good `key` function covers almost all of it before
pandas' `sort_values` and `rank` (phase 2) take over.

Key points:
- `sorted(rows, key=...)` returns a new list; `list.sort()` sorts in place and returns `None`.
- `key` is called once per item; `operator.itemgetter("col")` is the readable, fast choice for dict rows.
- Sorting is stable: rows with equal keys keep their input order, so you can sort in passes.
- Sort on several fields with a tuple key; negate numbers (`-units`) to mix ascending and descending.
- `heapq.nlargest(n, rows, key=...)` / `nsmallest` give the top-N without sorting everything.
- `max`/`min` with `key` return the whole row, not just the winning value.
- Ranking ties: *dense* rank (1, 1, 2) vs *competition* rank (1, 1, 3) - decide which your report needs.

Run it: `python day10/lesson.py`

## Exercise
`RESULTS` in `solution.py` holds fictional quiz results (name, team, score, seconds taken).
1. build the leaderboard: score high to low, then faster time first, then name A-Z;
2. assign *competition* ranks (ties on score and time share a rank, the next rank skips);
3. return the top 2 per team using `heapq.nlargest`, best first;
4. find the team with the highest average score (ties broken by team name A-Z).
Solution: `day10/solution.py`.
