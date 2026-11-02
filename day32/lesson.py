import pandas as pd

# A small fictional sales table
sales = pd.DataFrame({
    "shop": ["Breda", "Tilburg", "Breda", "Gouda", "Tilburg", "Breda", "Gouda"],
    "product": ["tea", "tea", "cake", "cake", "coffee", "coffee", "tea"],
    "qty": [3, 5, 2, 0, 4, 6, 1],
    "unit_price": [2.5, 2.5, 3.0, 3.0, 2.0, 2.0, 2.5],
    "discount": [0.0, 0.1, 0.0, 0.0, 0.25, 0.0, 0.1],
})

# 1. The step-by-step style: every line reassigns or mutates df, and the intermediate
#    variables pile up (and it is easy to run one cell twice in a notebook).
df = sales.copy()
df = df[df["qty"] > 0]
df["revenue"] = df["qty"] * df["unit_price"] * (1 - df["discount"])
per_shop = df.groupby("shop")["revenue"].sum().sort_values(ascending=False)
print(per_shop.round(2).to_dict())
print()

# 2. The same as one chain. assign() returns a NEW frame with the extra column, so the
#    original table is never touched. A lambda receives the frame as it is at that point.
chained = (
    sales
    .query("qty > 0")
    .assign(revenue=lambda d: d["qty"] * d["unit_price"] * (1 - d["discount"]))
    .groupby("shop")["revenue"].sum()
    .sort_values(ascending=False)
)
print(chained.round(2).to_dict())
print("same result:", chained.equals(per_shop), "| sales unchanged:", "revenue" not in sales)
print()

# 3. query() takes a boolean expression as a string. Column names are plain names,
#    @name refers to a Python variable, backticks quote names with spaces.
min_qty = 3
print(sales.query("qty >= @min_qty and shop != 'Gouda'")[["shop", "product", "qty"]].to_string(index=False))
odd = sales.rename(columns={"unit_price": "unit price"})
print(odd.query("`unit price` > 2.4")["product"].unique().tolist())
print()

# 4. Later assign() arguments can use columns created by earlier ones in the same call.
print(
    sales.assign(
        gross=lambda d: d["qty"] * d["unit_price"],
        net=lambda d: d["gross"] * (1 - d["discount"]),
    )[["gross", "net"]].sum().round(2).to_dict()
)
print()


# 5. pipe() puts your own function into the chain: df.pipe(f, x) is f(df, x).
#    A small "tap" function that prints the shape is handy for debugging long chains.
def drop_zero_qty(d: pd.DataFrame) -> pd.DataFrame:
    return d[d["qty"] > 0]


def tap(d: pd.DataFrame, label: str) -> pd.DataFrame:
    print(f"  [{label}] {d.shape[0]} rows x {d.shape[1]} cols")
    return d


top = (
    sales
    .pipe(tap, "start")
    .pipe(drop_zero_qty)
    .pipe(tap, "after drop_zero_qty")
    .assign(revenue=lambda d: d["qty"] * d["unit_price"] * (1 - d["discount"]))
    .nlargest(2, "revenue")
    .pipe(tap, "top 2")
)
print(top[["shop", "product", "revenue"]].to_string(index=False))
print()

# 6. eval() computes an expression from column names. Fine for arithmetic between
#    columns; assign() with a lambda is easier to read once the logic grows.
print(sales.eval("qty * unit_price * (1 - discount)").round(2).tolist())
print()

# 7. The trap: a lambda that uses the ORIGINAL table instead of its argument d.
#    After reset_index the row labels no longer match, so values land on the wrong rows.
base = sales.query("qty > 0").reset_index(drop=True)
wrong = base.assign(revenue=lambda d: sales["qty"] * sales["unit_price"])
right = base.assign(revenue=lambda d: d["qty"] * d["unit_price"])
print("wrong:", wrong["revenue"].tolist())
print("right:", right["revenue"].tolist())
