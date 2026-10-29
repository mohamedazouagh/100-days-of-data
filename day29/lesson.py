import pandas as pd

# A small fictional set of customer orders
orders = pd.DataFrame({
    "size": ["M", "S", "XL", "M", "L", "S", "M", "XL"],
    "amount": [12.5, 4.0, 88.0, 23.0, 41.5, 7.25, 19.0, 150.0],
    "age": [23, 35, 41, 19, 58, 66, 30, 47],
})

# 1. Sorting text gives alphabetical order, which is wrong for sizes
print(orders.sort_values("size")["size"].tolist())

# 2. An ordered categorical knows the real order: sorting and comparisons follow it
sizes = pd.CategoricalDtype(["S", "M", "L", "XL"], ordered=True)
orders["size"] = orders["size"].astype(sizes)
print(orders.sort_values("size")["size"].tolist())
print((orders["size"] >= "L").tolist())
print(orders["size"].cat.codes.tolist())   # stored as small integers
print()

# 3. Check for unknown labels before converting: values outside the categories would turn
#    into NaN (and newer pandas warns that this will raise)
incoming = pd.Series(["S", "XXL", "M"])
print(incoming[~incoming.isin(sizes.categories)].tolist())
print()

# 4. pd.cut: bins with edges you choose; right=False makes them [low, high)
orders["age_band"] = pd.cut(orders["age"], bins=[0, 18, 30, 45, 65, 120], right=False,
                            labels=["<18", "18-29", "30-44", "45-64", "65+"])
print(orders[["age", "age_band"]].T.to_string())
print()

# 5. pd.qcut: edges from quantiles, so each bin gets (about) the same number of rows
orders["spend_tier"], edges = pd.qcut(orders["amount"], q=4, labels=["low", "mid", "high", "top"],
                                      retbins=True)
print(orders["spend_tier"].value_counts(sort=False).to_dict())
print([round(float(e), 2) for e in edges])
print()

# 6. groupby on a categorical: observed=False keeps empty categories as rows with 0
print(orders.groupby("age_band", observed=False)["amount"].agg(["size", "sum"]))
print(orders.groupby("age_band", observed=True)["amount"].size().to_dict())
print()

# 7. Memory: many repeats of a few labels are much smaller as a category
labels = pd.Series(["Breda", "Utrecht", "Tilburg"] * 100_000)
print(labels.memory_usage(deep=True) // 1024, "KiB as text vs.",
      labels.astype("category").memory_usage(deep=True) // 1024, "KiB as category")
