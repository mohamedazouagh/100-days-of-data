import math
import random
from collections import defaultdict
from datetime import date, timedelta

import pandas as pd

COUNTRIES = ["NL", "BE", "DE", "FR"]
CATEGORIES = ["books", "games", "garden", "kitchen"]
STATUSES = ["shipped"] * 7 + ["pending"] * 2 + ["cancelled"]


def make_orders(seed: int, n: int = 300) -> list[dict]:
    """Fictional webshop order lines (same generator as Day 22), plus a few without a country."""
    rng = random.Random(seed)
    start = date(2026, 9, 1)
    rows = [
        {
            "order_id": 5000 + i,
            "date": (start + timedelta(days=rng.randint(0, 60))).isoformat(),
            "country": rng.choice(COUNTRIES),
            "category": rng.choice(CATEGORIES),
            "qty": rng.randint(1, 6),
            "unit_price": round(rng.uniform(4, 40), 2),
            "status": rng.choice(STATUSES),
        }
        for i in range(n)
    ]
    for row in rng.sample(rows, 8):
        row["country"] = None  # e.g. guest checkouts without an address yet
    return rows


def close(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)


def main() -> None:
    rows = make_orders(seed=23)
    df = pd.DataFrame(rows)
    df["value"] = df["qty"] * df["unit_price"]
    grand_total = df["value"].sum()
    print("order lines:", len(df), "| grand total:", round(grand_total, 2))

    # Plain-Python reference values used for every check below
    py_value = defaultdict(float)
    for r in rows:
        py_value[r["country"]] += r["qty"] * r["unit_price"]

    # 1. Value per country; without dropna=False the rows lacking a country disappear
    per_country = df.groupby("country")["value"].sum()
    per_country_all = df.groupby("country", dropna=False)["value"].sum()
    print("\n1. value per country:")
    print(per_country.round(2))
    print("sum without dropna=False:", round(per_country.sum(), 2),
          "| with:", round(per_country_all.sum(), 2))
    assert not close(per_country.sum(), grand_total)
    assert close(per_country_all.sum(), grand_total)
    for country, total in per_country.items():
        assert close(total, py_value[country])
    assert close(per_country_all[per_country_all.index.isna()].iloc[0], py_value[None])

    # 2. One summary row per category with named aggregation
    df["is_cancelled"] = df["status"] == "cancelled"
    summary = df.groupby("category").agg(
        lines=("order_id", "count"),
        units=("qty", "sum"),
        value=("value", "sum"),
        avg_unit_price=("unit_price", "mean"),
        cancelled_share=("is_cancelled", "mean"),  # mean of True/False = share of True
    )
    print("\n2. per category:")
    print(summary.round(3))
    for cat in CATEGORIES:
        cat_rows = [r for r in rows if r["category"] == cat]
        assert summary.loc[cat, "lines"] == len(cat_rows)
        assert summary.loc[cat, "units"] == sum(r["qty"] for r in cat_rows)
        assert close(summary.loc[cat, "value"], sum(r["qty"] * r["unit_price"] for r in cat_rows))
        assert close(summary.loc[cat, "avg_unit_price"], sum(r["unit_price"] for r in cat_rows) / len(cat_rows))
        cancelled = sum(r["status"] == "cancelled" for r in cat_rows)
        assert close(summary.loc[cat, "cancelled_share"], cancelled / len(cat_rows))

    # 3. size() counts rows, count() counts non-missing values
    sizes = df.groupby("category").size()
    counts = df.groupby("category")["country"].count()
    print("\n3. size vs. count of country:")
    print(pd.DataFrame({"size": sizes, "count_country": counts, "missing": sizes - counts}))
    for cat in CATEGORIES:
        assert sizes[cat] == sum(r["category"] == cat for r in rows)
        assert counts[cat] == sum(r["category"] == cat and r["country"] is not None for r in rows)
    assert (sizes - counts).sum() == 8

    # 4. Two keys as ordinary columns, and the best-selling category per country
    by_status = df.groupby(["country", "status"], as_index=False)["value"].sum()
    print("\n4. value per country and status (first rows):")
    print(by_status.head(6).round(2))
    py_two = defaultdict(float)
    for r in rows:
        if r["country"] is not None:
            py_two[(r["country"], r["status"])] += r["qty"] * r["unit_price"]
    assert len(by_status) == len(py_two)
    for rec in by_status.itertuples():
        assert close(rec.value, py_two[(rec.country, rec.status)])

    by_cat = df.groupby(["country", "category"], as_index=False)["value"].sum()
    best = by_cat.sort_values("value", ascending=False).drop_duplicates("country").set_index("country")
    print("best-selling category per country:")
    print(best.sort_index().round(2))
    py_cat = defaultdict(float)
    for r in rows:
        if r["country"] is not None:
            py_cat[(r["country"], r["category"])] += r["qty"] * r["unit_price"]
    for country in COUNTRIES:
        top = max(CATEGORIES, key=lambda c: py_cat[(country, c)])
        assert best.loc[country, "category"] == top

    # 5. Categories whose average order-line value beats the overall average
    avg_by_cat = df.groupby("category")["value"].mean()
    overall = df["value"].mean()
    above = avg_by_cat[avg_by_cat > overall].sort_values(ascending=False)
    print(f"\n5. overall average line value {overall:.2f}; categories above it:")
    print(above.round(2))
    py_overall = sum(r["qty"] * r["unit_price"] for r in rows) / len(rows)
    py_above = set()
    for cat in CATEGORIES:
        vals = [r["qty"] * r["unit_price"] for r in rows if r["category"] == cat]
        if sum(vals) / len(vals) > py_overall:
            py_above.add(cat)
    assert set(above.index) == py_above

    print("\nall checks passed")


if __name__ == "__main__":
    main()
