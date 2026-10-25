import math
import random
from collections import defaultdict

import pandas as pd

CITIES = ["Breda", "Utrecht", "Gouda", "Delft"]


def make_shop(seed: int):
    """Fictional webshop: customers, products and two monthly order exports with some orphans."""
    rng = random.Random(seed)
    customers = [{"customer_id": cid, "city": rng.choice(CITIES)} for cid in range(1, 31)]
    products = [
        {"sku": f"P{i:02d}", "price": round(rng.uniform(2, 40), 2)} for i in range(1, 11)
    ]
    sold_skus = [p["sku"] for p in products[:-1]]        # the last product is never ordered
    months = {}
    oid = 1000
    for month in ["2026-09", "2026-10"]:
        rows = []
        for _ in range(rng.randint(35, 45)):
            oid += 1
            r = rng.random()
            rows.append({
                "order_id": oid,
                "customer_id": 99 if r < 0.06 else rng.randint(1, 30),   # 99 does not exist
                "sku": "X00" if 0.06 <= r < 0.11 else rng.choice(sold_skus),  # X00 does not exist
                "qty": rng.randint(1, 4),
            })
        months[month] = rows
    return customers, products, months


def close(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)


def main() -> None:
    customers, products, months = make_shop(seed=25)
    cust_df = pd.DataFrame(customers)
    prod_df = pd.DataFrame(products)

    # 1. Stack the monthly exports, remembering the month
    orders = pd.concat(
        [pd.DataFrame(rows) for rows in months.values()], keys=list(months), names=["month", None]
    ).reset_index(level="month").reset_index(drop=True)
    print("1. orders per month:", orders["month"].value_counts().sort_index().to_dict(), "| total:", len(orders))
    py_orders = [{**r, "month": m} for m, rows in months.items() for r in rows]
    assert len(orders) == len(py_orders) == sum(len(rows) for rows in months.values())
    assert orders["order_id"].is_unique
    assert orders["month"].tolist() == [r["month"] for r in py_orders]

    # 2. Left join to products, with the key relationship checked
    priced = orders.merge(prod_df, on="sku", how="left", validate="many_to_one")
    priced["revenue"] = priced["qty"] * priced["price"]
    unknown_sku = int(priced["price"].isna().sum())
    print(f"\n2. orders with an unknown SKU: {unknown_sku} | known revenue: {priced['revenue'].sum():.2f}")
    price_of = {p["sku"]: p["price"] for p in products}
    assert len(priced) == len(orders)          # a left join never drops rows
    assert unknown_sku == sum(r["sku"] not in price_of for r in py_orders) > 0
    py_revenue = sum(r["qty"] * price_of[r["sku"]] for r in py_orders if r["sku"] in price_of)
    assert close(priced["revenue"].sum(), py_revenue)   # sum() skips the NaN revenue

    # 3. Products never ordered, via an outer join and the indicator column
    audit = prod_df.merge(orders[["sku"]].drop_duplicates(), on="sku", how="outer", indicator=True)
    never = sorted(audit.loc[audit["_merge"] == "left_only", "sku"])
    ghost = sorted(audit.loc[audit["_merge"] == "right_only", "sku"])
    print("\n3. never ordered:", never, "| ordered but not in the catalogue:", ghost)
    ordered = {r["sku"] for r in py_orders}
    assert never == sorted(set(price_of) - ordered) == ["P10"]
    assert ghost == sorted(ordered - set(price_of)) == ["X00"]

    # 4. Revenue per city: inner join drops orders from unknown customers
    with_city = priced.merge(cust_df, on="customer_id", how="inner", validate="many_to_one")
    orphans = int((~priced["customer_id"].isin(cust_df["customer_id"])).sum())
    per_city = with_city.groupby("city")["revenue"].sum().round(2).sort_values(ascending=False)
    print(f"\n4. rows {len(priced)} -> {len(with_city)} after the inner join ({orphans} orphan orders)")
    print(per_city)
    city_of = {c["customer_id"]: c["city"] for c in customers}
    assert len(with_city) == len(priced) - orphans and orphans > 0
    py_city = defaultdict(float)
    for r in py_orders:
        if r["customer_id"] in city_of and r["sku"] in price_of:
            py_city[city_of[r["customer_id"]]] += r["qty"] * price_of[r["sku"]]
    assert set(per_city.index) == set(py_city)
    for city, total in py_city.items():
        assert close(per_city[city], round(total, 2))

    # 5. A duplicated product row multiplies matches; validate= refuses it
    dup = pd.concat([prod_df, prod_df[prod_df["sku"] == "P01"]], ignore_index=True)
    blown_up = orders.merge(dup, on="sku", how="left")
    p01_orders = int((orders["sku"] == "P01").sum())
    print(f"\n5. with P01 listed twice: {len(orders)} -> {len(blown_up)} rows (+{p01_orders} P01 orders)")
    assert len(blown_up) == len(orders) + p01_orders
    try:
        orders.merge(dup, on="sku", how="left", validate="many_to_one")
    except pd.errors.MergeError as e:
        print("   validate:", str(e).splitlines()[0])
    else:
        raise AssertionError("validate should have raised MergeError")

    print("\nall checks passed")


if __name__ == "__main__":
    main()
