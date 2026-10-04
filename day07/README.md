# Day 07 - Summary statistics with the statistics module

Before any chart or model, you describe a column with a handful of numbers: where the centre is,
how spread out the values are, and whether a few extreme values distort the picture. The standard
library's `statistics` module covers all of this without pandas.

Key points:
- Clean first: `mean`, `median` and friends do not skip `None`. Filter missing values out on purpose (and count how many you dropped).
- **Centre:** `mean` uses every value, so one outlier drags it; `median` is the middle value and is robust to outliers. A big gap between the two is a hint to look at the data.
- **Spread:** `stdev` is the sample standard deviation (divides by n - 1), `pstdev` the population version (divides by n). Use `stdev` when your data is a sample of something larger.
- `quantiles(data, n=4)` returns the three quartile cut points Q1, Q2 (= median), Q3. The **IQR** = Q3 - Q1 is the spread of the middle half.
- A common outlier rule: values below Q1 - 1.5·IQR or above Q3 + 1.5·IQR. It is a flag to investigate, not a reason to delete.
- Empty input raises `statistics.StatisticsError`; `stdev` needs at least two values.

Run it: `python day07/lesson.py`

## Exercise
`STEPS` in `solution.py` holds a fictional team's daily step counts for ten days, with `None` for
days the tracker was not worn. For each person:
1. compute the number of recorded days, mean, median and sample standard deviation;
2. flag outlier days with the 1.5·IQR rule (report the day number and value);
3. print a table ranked by median, highest first, and name the person whose mean and median differ most.
Solution: `day07/solution.py`.
