import pandas as pd

# The same kind of fictional shop table as Day 22, with one missing quantity
df = pd.DataFrame({
    "order_id": [101, 102, 103, 104, 105, 106, 107, 108],
    "city": ["Breda", "Utrecht", "Breda", "Gouda", "Utrecht", "Breda", "Gouda", "Utrecht"],
    "product": ["tea", "coffee", "coffee", "tea", "cocoa", "tea", "coffee", "tea"],
    "qty": [2, 1, 5, 3, 4, 1, None, 2],
    "price": [3.5, 4.0, 4.0, 3.5, 2.75, 3.5, 4.0, 3.5],
})
df["revenue"] = df["qty"] * df["price"]
print(df)
print()

# 1. Split-apply-combine: one key, one column, one function -> a Series indexed by the key
print(df.groupby("city")["revenue"].sum())
print()

# 2. size() counts ROWS per group, count() counts NON-MISSING values per column
print(df.groupby("city").size().to_dict())
print(df.groupby("city")["qty"].count().to_dict())
print()

# 3. Several functions at once with agg(); named aggregation gives clean column names
summary = df.groupby("city").agg(
    orders=("order_id", "count"),
    units=("qty", "sum"),          # sum() skips NaN
    revenue=("revenue", "sum"),
    avg_price=("price", "mean"),
)
print(summary)
print()

# 4. Two keys -> a MultiIndex; as_index=False (or reset_index) keeps them as normal columns
by_two = df.groupby(["city", "product"], as_index=False)["revenue"].sum()
print(by_two)
print()

# Gouda/coffee shows 0.0 although its only revenue is missing: the sum of nothing is 0.
# min_count=1 says "need at least one real value", so that group stays NaN instead.
print(df.groupby(["city", "product"])["revenue"].sum(min_count=1).loc[("Gouda", "coffee")])
print()

# 5. Groups come out sorted by key; sort=False keeps first-seen order instead
print(df.groupby("product").size().index.tolist())
print(df.groupby("product", sort=False).size().index.tolist())
print()

# 6. Rows with a missing key are dropped by default; dropna=False keeps them as their own group
df.loc[len(df)] = [109, None, "tea", 1, 3.5, 3.5]
print(df.groupby("city")["revenue"].sum().to_dict())
print(df.groupby("city", dropna=False)["revenue"].sum().to_dict())
print()

# 7. Filter on the aggregated result, then sort: cities with more than 15 in revenue
totals = df.groupby("city")["revenue"].sum()
print(totals[totals > 15].sort_values(ascending=False))
