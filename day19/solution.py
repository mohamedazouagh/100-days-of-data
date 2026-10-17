import random
from decimal import Decimal

CITIES = ["Breda", "Tilburg", "Utrecht", "Eindhoven"]
SKUS = {"TEA-01": Decimal("4.50"), "MUG-02": Decimal("9.95"), "BAG-03": Decimal("2.25"), "PEN-04": Decimal("1.10")}


def make_orders(seed: int, n: int = 150) -> list[dict]:
    """Fictional API response: nested customer dict and a list of items per order."""
    rng = random.Random(seed)
    orders = []
    for i in range(1, n + 1):
        customer = {"id": rng.randint(100, 140), "address": {"country": "NL"}}
        if rng.random() > 0.1:  # ~10% of customers have no city on file
            customer["address"]["city"] = rng.choice(CITIES)
        k = 0 if rng.random() < 0.08 else rng.randint(1, 4)  # some orders are empty
        items = [{"sku": s, "qty": rng.randint(1, 5), "price": SKUS[s]} for s in rng.sample(list(SKUS), k)]
        orders.append({"order_id": i, "customer": customer, "items": items})
    return orders


def flatten(d: dict, parent: str = "", sep: str = ".") -> dict:
    out = {}
    for k, v in d.items():
        key = f"{parent}{sep}{k}" if parent else k
        if isinstance(v, dict):
            out.update(flatten(v, key, sep))
        else:
            out[key] = v
    return out


def rows_to_columns(rows: list[dict]) -> dict[str, list]:
    keys = list(dict.fromkeys(k for r in rows for k in r))
    return {k: [r.get(k) for r in rows] for k in keys}


def columns_to_rows(cols: dict[str, list]) -> list[dict]:
    return [dict(zip(cols, vals, strict=True)) for vals in zip(*cols.values(), strict=True)]


def explode_items(orders: list[dict]) -> list[dict]:
    out = []
    for o in orders:
        parent = flatten({k: v for k, v in o.items() if k != "items"})
        for item in o["items"] or [{"sku": None, "qty": 0, "price": Decimal("0")}]:
            out.append({**parent, **item})
    return out


if __name__ == "__main__":
    orders = make_orders(seed=19)

    # 1. flat order rows -> columns, missing city becomes None
    flat = [flatten({k: v for k, v in o.items() if k != "items"}) for o in orders]
    cols = rows_to_columns(flat)
    missing_city = sum(c is None for c in cols["customer.address.city"])
    print("columns:", list(cols))
    print("orders:", len(flat), "| without city:", missing_city)
    assert all(len(v) == len(orders) for v in cols.values())
    assert missing_city == sum("city" not in o["customer"]["address"] for o in orders)

    # 2. one row per item, empty orders kept once with sku=None
    lines = explode_items(orders)
    empty = sum(not o["items"] for o in orders)
    n_items = sum(len(o["items"]) for o in orders)
    print("item rows:", len(lines), "=", n_items, "items +", empty, "empty orders")
    print("first row:", lines[0])
    assert len(lines) == n_items + empty
    assert sum(r["sku"] is None for r in lines) == empty

    # 3. columns -> rows round trip (missing keys come back as explicit None)
    rebuilt = columns_to_rows(cols)
    assert rebuilt == [{k: r.get(k) for k in cols} for r in flat]
    print("round trip ok:", len(rebuilt), "rows")

    # 4. totals agree between the nested and the exploded shape
    nested_total = sum(i["qty"] * i["price"] for o in orders for i in o["items"])
    flat_total = sum(r["qty"] * r["price"] for r in lines)
    print("revenue nested:", nested_total, "| exploded:", flat_total)
    assert nested_total == flat_total
    print("all checks passed")
