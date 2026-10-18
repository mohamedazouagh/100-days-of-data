import random
from collections import defaultdict
from decimal import Decimal

CATEGORIES = ["tea", "mugs", "bags", "stationery"]
TARGETS = {"tea": Decimal("1500"), "mugs": Decimal("1800"), "bags": Decimal("2200"), "stationery": Decimal("3200")}


def make_tables(seed: int) -> tuple[list[dict], list[dict]]:
    """Fictional products (with one duplicated id) and sales lines (a few unknown ids)."""
    rng = random.Random(seed)
    products = [
        {"pid": f"P{i:03d}", "category": CATEGORIES[i % 4], "price": Decimal(rng.randint(100, 1500)) / 100}
        for i in range(1, 41)
    ]
    dup = dict(products[6])  # same id as P007, different price: a typical copy-paste error
    dup["price"] += 1
    products.append(dup)
    known = [p["pid"] for p in products[:35]]  # P036..P040 never sell
    sales = []
    for line in range(1, 301):
        pid = rng.choice(known) if rng.random() > 0.03 else f"X{rng.randint(1, 9)}"
        sales.append({"line": line, "pid": pid, "qty": rng.randint(1, 6)})
    return products, sales


def index_first(rows: list[dict], key: str) -> tuple[dict, list]:
    """Unique index keeping the first row per key; returns (index, duplicate keys seen)."""
    index, dups = {}, []
    for r in rows:
        if r[key] in index:
            dups.append(r[key])
            continue
        index[r[key]] = r
    return index, dups


def left_join(left: list[dict], index: dict, key: str, fields: list[str]) -> list[dict]:
    empty = dict.fromkeys(fields)
    return [{**r, **{f: index.get(r[key], empty)[f] for f in fields}} for r in left]


if __name__ == "__main__":
    products, sales = make_tables(seed=20)

    # 1. unique product index (duplicate reported, first row kept)
    index, dups = index_first(products, "pid")
    print("products:", len(products), "rows ->", len(index), "unique | duplicates:", dups)
    assert dups == ["P007"] and len(index) == 40

    # 2. left join sales -> products
    lines = left_join(sales, index, "pid", ["category", "price"])
    unknown = [r for r in lines if r["category"] is None]
    print("sales lines:", len(lines), "| unknown product:", len(unknown))
    assert len(lines) == len(sales), "left join must keep every sales line"

    # 3. anti joins both ways
    sold = {s["pid"] for s in sales}
    never_sold = sorted(pid for pid in index if pid not in sold)
    orphan_ids = sorted({r["pid"] for r in unknown})
    print("never sold:", never_sold)
    print("unknown ids in sales:", orphan_ids)
    assert set(never_sold) >= {"P036", "P037", "P038", "P039", "P040"}

    # 4. revenue per category (one-to-many) vs. targets
    revenue = defaultdict(Decimal)
    for r in lines:
        if r["category"] is not None:
            revenue[r["category"]] += r["qty"] * r["price"]
    for cat in CATEGORIES:
        flag = "below target" if revenue[cat] < TARGETS[cat] else "ok"
        print(f"{cat:<10} {revenue[cat]:>9} / {TARGETS[cat]:>6}  {flag}")

    # 5. totals reconcile: known categories + unknown lines = all lines
    unknown_qty = sum(r["qty"] for r in unknown)
    total_known = sum(revenue.values())
    check = sum(r["qty"] * index[r["pid"]]["price"] for r in sales if r["pid"] in index)
    print("revenue known:", total_known, "| unknown lines qty:", unknown_qty)
    assert total_known == check
    assert sum(r["qty"] for r in lines) == sum(s["qty"] for s in sales)
    print("all checks passed")
