import pandas as pd

# Fictional orders from a small web shop: one row per order.
orders = pd.DataFrame({
    "order_id": [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
    "customer": ["ana", "ben", "ana", "cas", "ben", "ana", "dee", "cas", "ben", "ana"],
    "date": pd.to_datetime(["2026-10-01", "2026-10-02", "2026-10-04", "2026-10-05", "2026-10-07",
                            "2026-10-09", "2026-10-10", "2026-10-12", "2026-10-15", "2026-10-20"]),
    "amount": [30.0, 12.5, 45.0, 80.0, 12.5, 15.0, 22.0, 20.0, 60.0, 45.0],
})
g = orders.groupby("customer")

# 1. agg shrinks: one row per group.
print(g["amount"].agg(["count", "sum"]).to_string(), "\n")

# 2. transform keeps the shape: one value per original row, aligned on the index,
#    so a group statistic can sit next to each row without a merge.
orders["cust_total"] = g["amount"].transform("sum")
orders["share"] = (orders["amount"] / orders["cust_total"]).round(3)
orders["vs_cust_avg"] = orders["amount"] - g["amount"].transform("mean")
print(orders[["order_id", "customer", "amount", "cust_total", "share", "vs_cust_avg"]].to_string(), "\n")

# 3. A lambda in transform gets each group as a Series; it must return the same length
#    (or a scalar, which is broadcast). Here: z-score within the customer.
z = g["amount"].transform(lambda s: (s - s.mean()) / s.std(ddof=0) if len(s) > 1 else 0.0)
print("z-scores:", z.round(2).tolist(), "\n")

# 4. cumcount numbers rows inside each group (0, 1, 2, ...) in the current row order,
#    so sort first. cumsum/diff give running values per group the same way.
orders = orders.sort_values(["customer", "date"])
orders["nth_order"] = orders.groupby("customer").cumcount() + 1
orders["running_spend"] = orders.groupby("customer")["amount"].cumsum()
orders["days_since_prev"] = orders.groupby("customer")["date"].diff().dt.days
print(orders[["customer", "date", "amount", "nth_order", "running_spend", "days_since_prev"]].to_string(), "\n")

# 5. filter drops whole groups based on a group-level condition and keeps the original rows.
repeat = orders.groupby("customer").filter(lambda d: len(d) >= 3)
print("customers with 3+ orders:", sorted(repeat["customer"].unique()), "->", len(repeat), "rows\n")

# 6. First / n-th row per group, and the row holding the group maximum.
by_cust = orders.groupby("customer")
print("first order per customer:", by_cust.head(1)["order_id"].tolist())
print("second order (nth(1)):   ", by_cust.nth(1)["order_id"].tolist())  # 1-order customers are skipped
top = orders.loc[by_cust["amount"].idxmax(), ["customer", "order_id", "amount"]]
print("biggest order per customer (first one on ties):")
print(top.to_string(index=False))
