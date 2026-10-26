import pandas as pd

# A small fictional "wide" table, like a spreadsheet export: one column per month
wide = pd.DataFrame({
    "store": ["Breda", "Delft", "Gouda"],
    "2026-08": [120, 95, 60],
    "2026-09": [135, None, 72],     # Delft did not report in September
    "2026-10": [128, 101, 80],
})
print(wide)
print()

# 1. melt(): wide -> long. id_vars stay, every other column becomes (variable, value) rows
long = wide.melt(id_vars="store", var_name="month", value_name="sales")
print(long)
print(len(wide), "rows x", wide.shape[1] - 1, "months ->", len(long), "rows")
print()

# 2. Long data is easy to filter and group: missing months are just NaN rows
long = long.dropna(subset=["sales"])
print(long.groupby("month")["sales"].sum())
print()

# 3. pivot(): long -> wide again. Fails if a (index, column) pair appears twice
back = long.pivot(index="store", columns="month", values="sales")
print(back)
print()

# 4. pivot_table(): like pivot, but aggregates duplicates (two rows for Breda in October)
extra = pd.concat([long, pd.DataFrame({"store": ["Breda"], "month": ["2026-10"], "sales": [10]})])
try:
    extra.pivot(index="store", columns="month", values="sales")
except ValueError as e:
    print("pivot ValueError:", e)
table = extra.pivot_table(index="store", columns="month", values="sales", aggfunc="sum",
                          fill_value=0, margins=True, margins_name="total")
print(table)
print()

# 5. stack()/unstack(): move a column level into the index and back
stacked = back.stack()          # Series with a (store, month) MultiIndex, NaN dropped
print(stacked.head(4))
print(stacked.unstack("store"))  # months as rows, stores as columns
print()

# 6. Tidy month columns: after melt the month is text, so parse it before sorting by date
long["month"] = pd.to_datetime(long["month"], format="%Y-%m")
print(long.sort_values(["store", "month"]).head(3))
print(long.dtypes.to_dict())
