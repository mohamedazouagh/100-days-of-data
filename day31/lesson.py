import time

import numpy as np
import pandas as pd

# A small fictional order table
orders = pd.DataFrame({
    "order_id": [101, 102, 103, 104, 105, 106],
    "country": ["NL", "BE", "DE", "NL", "FR", "XX"],
    "amount": [18.0, 64.5, 120.0, -5.0, 35.0, 250.0],
    "items": [1, 3, 6, 1, 2, 9],
})

# 1. Two outcomes: np.where(condition, if_true, if_false) works on the whole column at once
orders["shipping"] = np.where(orders["amount"] >= 50, 0.0, 4.95)
print(orders["shipping"].tolist())
print()

# 2. More than two outcomes: np.select checks the conditions in order, first match wins,
#    default for the rest. Order matters: put the most specific condition first.
conditions = [orders["amount"] < 0, orders["amount"] >= 100, orders["amount"] >= 50]
choices = ["refund", "large", "medium"]
orders["size"] = np.select(conditions, choices, default="small")
print(orders["size"].tolist())
print()

# 3. Lookups: Series.map(dict) replaces each value by its entry; values that are not in
#    the dict become NaN, so fill them explicitly instead of hiding the problem.
region = {"NL": "Benelux", "BE": "Benelux", "DE": "DACH", "FR": "West"}
orders["region"] = orders["country"].map(region)
print(orders["region"].tolist())
print(orders["region"].fillna("unknown").tolist())
print()

# 4. Keep or replace values: where keeps rows where the condition holds and replaces the
#    rest; mask is the opposite. clip caps values into a range.
print(orders["amount"].where(orders["amount"] >= 0, 0.0).tolist())
print(orders["amount"].mask(orders["amount"] > 200, 200.0).tolist())
print(orders["items"].clip(lower=1, upper=5).tolist())
print()

# 5. apply(axis=1) calls a Python function once per row. It works for anything, but it is
#    much slower than the column-wide versions above on a big table.
def ship_row(row):
    return 0.0 if row["amount"] >= 50 else 4.95

big = pd.concat([orders] * 20_000, ignore_index=True)
t0 = time.perf_counter()
slow = big.apply(ship_row, axis=1)
t1 = time.perf_counter()
fast = pd.Series(np.where(big["amount"] >= 50, 0.0, 4.95))
t2 = time.perf_counter()
print(len(big), "rows, same result:", slow.equals(fast))
print("apply is slower:", (t1 - t0) > (t2 - t1))
