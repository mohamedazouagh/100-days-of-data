import pandas as pd

# Two small fictional tables that share a key, like an orders export and a product list
orders = pd.DataFrame({
    "order_id": [101, 102, 103, 104, 105],
    "sku": ["A1", "B2", "A1", "Z9", "C3"],   # Z9 is not in the product list
    "qty": [2, 1, 5, 1, 3],
})
products = pd.DataFrame({
    "sku": ["A1", "B2", "C3", "D4"],          # D4 has never been ordered
    "name": ["mug", "pen", "cap", "bag"],
    "price": [8.5, 1.2, 12.0, 30.0],
})

# 1. merge(): inner keeps only keys found in both tables (Z9 and D4 disappear)
inner = orders.merge(products, on="sku", how="inner")
print(inner)
print()

# 2. how="left" keeps every order; products that are missing become NaN
left = orders.merge(products, on="sku", how="left")
print(left[["order_id", "sku", "name", "price"]])
print("orders without a product:", left["name"].isna().sum())
print()

# 3. how="outer" keeps both sides; indicator=True says where each row came from
outer = orders.merge(products, on="sku", how="outer", indicator=True)
print(outer[["sku", "order_id", "name", "_merge"]])
print(outer["_merge"].value_counts().to_dict())
print()

# 4. validate= catches a broken key before it silently multiplies rows
dup_products = pd.concat([products, products.iloc[[0]]])   # A1 listed twice
print(len(orders.merge(dup_products, on="sku")), "rows instead of", len(inner))
try:
    orders.merge(dup_products, on="sku", validate="many_to_one")
except pd.errors.MergeError as e:
    print("MergeError:", str(e).splitlines()[0])
print()

# 5. Different key names: left_on / right_on (then drop the duplicate key column)
stock = pd.DataFrame({"product_code": ["A1", "C3"], "in_stock": [40, 0]})
print(products.merge(stock, left_on="sku", right_on="product_code", how="left").drop(columns="product_code"))
print()

# 6. concat(): stack tables with the same columns (e.g. monthly exports) on top of each other
sept = pd.DataFrame({"order_id": [90, 91], "sku": ["B2", "A1"], "qty": [1, 1]})
all_orders = pd.concat([sept, orders], ignore_index=True)    # fresh 0..n-1 index
print(len(sept), "+", len(orders), "=", len(all_orders), "rows")
print(pd.concat([sept, orders], keys=["sep", "oct"]).loc["sep"])  # keys remember the source
