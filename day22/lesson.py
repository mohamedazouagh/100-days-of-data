import pandas as pd

# A small fictional shop table: one row per order line
df = pd.DataFrame({
    "order_id": [101, 102, 103, 104, 105, 106],
    "city": ["Breda", "Utrecht", "Breda", "Gouda", "Utrecht", "Breda"],
    "product": ["tea", "coffee", "coffee", "tea", "cocoa", "tea"],
    "qty": [2, 1, 5, 3, 4, 1],
    "price": [3.5, 4.0, 4.0, 3.5, 2.75, 3.5],
}).set_index("order_id")
print(df)
print()

# 1. loc selects by LABEL (index values and column names); slices include the end label
print(df.loc[103, "product"])
print(df.loc[102:104, ["city", "qty"]])
print()

# 2. iloc selects by POSITION; slices exclude the end, like Python lists
print(df.iloc[0, 1], "|", df.iloc[-1, 0])
print(df.iloc[1:3, :2])
print()

# 3. Boolean masks: a Series of True/False, one per row. Combine with & | ~ and parentheses.
big_breda = (df["city"] == "Breda") & (df["qty"] >= 2)
print(big_breda.tolist())
print(df[big_breda])
print()

# 4. isin() for "one of these values", between() for an inclusive range
print(df[df["product"].isin(["coffee", "cocoa"])].index.tolist())
print(df[df["qty"].between(2, 4)].index.tolist())
print()

# 5. query() says the same thing as a string; @name refers to a Python variable
min_qty = 3
print(df.query("city != 'Gouda' and qty >= @min_qty").index.tolist())
print()

# 6. Filter rows AND pick columns in one loc call; assign through loc to change only those rows
df["revenue"] = df["qty"] * df["price"]
print(df.loc[df["product"] == "tea", ["city", "revenue"]])
df.loc[df["city"] == "Gouda", "price"] = 3.25
# revenue was computed from the old price: columns are values, not live formulas
print(df.loc[104, ["price", "revenue"]].tolist())
print()

# 7. Sorting: by several columns, mixed directions; nlargest() for a quick top-N
print(df.sort_values(["city", "revenue"], ascending=[True, False])[["city", "revenue"]])
print(df.nlargest(2, "revenue").index.tolist())
