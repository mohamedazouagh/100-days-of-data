import numpy as np
import pandas as pd

# A small fictional sign-up export with typical problems: gaps, a blank-ish email,
# a "n/a" placeholder and a customer exported twice
df = pd.DataFrame({
    "customer_id": [1, 2, 3, 4, 2, 5, 6],
    "email": ["a@example.com", "b@example.com", None, "d@example.com", "b@example.com", "  ", "f@example.com"],
    "city": ["Breda", "Utrecht", "Breda", None, "Utrecht", "Gouda", "n/a"],
    "age": [34, np.nan, 29, 41, np.nan, 23, np.nan],
    "orders": [3, 1, 0, np.nan, 2, 2, 5],   # customer 2 again, with a newer order count
})
print(df)
print()

# 1. Find the gaps: isna() gives a True/False table, sum() counts per column
print(df.isna().sum().to_dict())
print("rows with any gap:", int(df.isna().any(axis=1).sum()))
print()

# 2. Placeholders are not NaN until you say so: turn blanks and "n/a" into real missing values
df["email"] = df["email"].str.strip().replace("", np.nan)
df["city"] = df["city"].replace("n/a", np.nan)
print(df.isna().sum().to_dict())
print()

# 3. dropna(): drop rows with a gap anywhere, only in chosen columns, or below a threshold
print(len(df.dropna()), "rows without any gap")
print(len(df.dropna(subset=["email"])), "rows with an email")
print(len(df.dropna(thresh=4)), "rows with at least 4 filled values")
print()

# 4. fillna(): one value per column with a dict; a statistic for numbers, a label for text
filled = df.fillna({"orders": 0, "city": "unknown", "age": df["age"].median()})
print(filled[["customer_id", "city", "age", "orders"]])
print()

# 5. Missing values change statistics: mean() skips NaN, filling with 0 drags it down
print("mean orders, NaN skipped:", round(df["orders"].mean(), 2))
print("mean orders, NaN as 0:   ", round(df["orders"].fillna(0).mean(), 2))
print()

# 6. Duplicates: duplicated() flags repeats, drop_duplicates() removes them
print(df.duplicated().tolist())                               # whole-row repeats: none
print(df.duplicated(subset=["customer_id"]).tolist())         # same id, other values differ
deduped = df.drop_duplicates(subset=["customer_id"], keep="last")   # keep the newer export
print(len(df), "->", len(deduped), "rows after dropping repeated customer ids")
