# Day 17 - Sampling and reproducibility with random

Data work uses randomness all the time: picking a sample to check by hand, splitting rows into
train and test sets, simulating data, or estimating how much a statistic could wobble. The
standard library `random` module covers all of this, as long as you make the results
reproducible so a rerun gives the same sample.

Key points:
- `random.seed(n)` makes the module-level functions repeat the same sequence on every run.
- Prefer your own `rng = random.Random(n)`: it is reproducible and other code calling `random.*`
  cannot shift your sequence.
- `rng.sample(items, k)` draws **without** replacement (no repeats, `k` cannot exceed the size);
  `rng.choices(items, k=k)` draws **with** replacement and accepts `weights=`.
- `rng.shuffle(lst)` shuffles in place and returns `None`; copy the list first if you need the original order.
- A reproducible train/test split is just "shuffle a copy with a fixed seed, then slice".
- Small samples scatter: the mean of 25 values can land several units away from the population mean.
  Resampling many times shows how big that scatter is (the idea behind the bootstrap).
- `random` is for simulations and sampling, not security: use `secrets` for tokens and passwords.

Run it: `python day17/lesson.py`

## Exercise
`solution.py` builds a fictional table of 1,000 orders across three regions with an order amount.
1. draw a reproducible simple random sample of 50 orders and compare its mean amount with the full table;
2. draw a **stratified** sample of 10 % per region, so each region keeps its share, and check the region counts;
3. estimate a 95 % bootstrap confidence interval for the mean amount of the 50-order sample
   (resample with replacement 2,000 times, take the 2.5th and 97.5th percentiles of the means);
4. show that running the whole thing twice with the same seed gives identical results.
Solution: `day17/solution.py`.
