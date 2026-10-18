from collections import defaultdict

# Two small tables that share a key: customers (one row per id) and orders (many per id)
CUSTOMERS = [
    {"cid": 1, "name": "Ada", "city": "Breda"},
    {"cid": 2, "name": "Bo", "city": "Utrecht"},
    {"cid": 3, "name": "Cy", "city": "Tilburg"},  # has no orders
]
ORDERS = [
    {"oid": 10, "cid": 1, "amount": 25.0},
    {"oid": 11, "cid": 1, "amount": 12.5},
    {"oid": 12, "cid": 2, "amount": 40.0},
    {"oid": 13, "cid": 9, "amount": 7.0},  # unknown customer
]


def index_unique(rows: list[dict], key: str) -> dict:
    """{key value: row}; refuses duplicate keys instead of silently keeping the last one."""
    out = {}
    for r in rows:
        k = r[key]
        if k in out:
            raise ValueError(f"duplicate key {key}={k!r}")
        out[k] = r
    return out


def group_by(rows: list[dict], key: str) -> dict[object, list[dict]]:
    out = defaultdict(list)
    for r in rows:
        out[r[key]].append(r)
    return out


def inner_join(left: list[dict], right_index: dict, key: str) -> list[dict]:
    """Keep left rows whose key exists on the right; right fields are added to each row."""
    return [{**r, **right_index[r[key]]} for r in left if r[key] in right_index]


def left_join(left: list[dict], right_index: dict, key: str, right_fields: list[str]) -> list[dict]:
    """Keep every left row; unmatched rows get None for the right-hand fields."""
    empty = dict.fromkeys(right_fields)
    return [{**r, **right_index.get(r[key], empty)} for r in left]


def anti_join(left: list[dict], right_keys: set, key: str) -> list[dict]:
    """Left rows with no match on the right (the 'what is missing?' question)."""
    return [r for r in left if r[key] not in right_keys]


if __name__ == "__main__":
    customers = index_unique(CUSTOMERS, "cid")  # O(1) lookups instead of a nested loop

    # 1. inner join: orders with a known customer
    for row in inner_join(ORDERS, customers, "cid"):
        print("inner:", row)

    # 2. left join: every order, unknown customer gets None
    for row in left_join(ORDERS, customers, "cid", ["name", "city"]):
        print("left: ", row["oid"], row["name"], row["city"])

    # 3. anti joins in both directions
    print("orders without customer:", [o["oid"] for o in anti_join(ORDERS, set(customers), "cid")])
    print("customers without orders:", [c["name"] for c in anti_join(CUSTOMERS, {o["cid"] for o in ORDERS}, "cid")])

    # 4. one-to-many: group the many side, then aggregate per customer
    by_customer = group_by(ORDERS, "cid")
    for cid, c in customers.items():
        rows = by_customer.get(cid, [])
        print(f"{c['name']}: {len(rows)} orders, total {sum(r['amount'] for r in rows):.2f}")

    # 5. a duplicate key on the 'one' side would multiply rows in a join - fail loudly
    try:
        index_unique(CUSTOMERS + [{"cid": 2, "name": "Bo (copy)", "city": "Utrecht"}], "cid")
    except ValueError as e:
        print("ValueError:", e)

    # 6. sanity checks every join deserves
    left = left_join(ORDERS, customers, "cid", ["name", "city"])
    assert len(left) == len(ORDERS), "a left join must not add or drop rows"
    print("row counts: orders", len(ORDERS), "| inner", len(inner_join(ORDERS, customers, "cid")), "| left", len(left))
