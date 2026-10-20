import random
from datetime import date, timedelta

import pandas as pd

COUNTRIES = ["NL", "BE", "DE", "FR"]
CATEGORIES = ["books", "games", "garden", "kitchen"]
STATUSES = ["shipped"] * 7 + ["pending"] * 2 + ["cancelled"]


def make_orders(seed: int, n: int = 300) -> list[dict]:
    """Fictional webshop order lines spread over September and October 2026."""
    rng = random.Random(seed)
    start = date(2026, 9, 1)
    return [
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


def main() -> None:
    rows = make_orders(seed=22)
    df = pd.DataFrame(rows).set_index("order_id")
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = df["qty"] * df["unit_price"]
    print("orders:", df.shape)

    # 1. loc includes the end label, iloc excludes the end position
    by_label = df.loc[5000:5004]
    by_position = df.iloc[0:4]
    print("loc[5000:5004] rows:", len(by_label), "| iloc[0:4] rows:", len(by_position))
    assert by_label.index.tolist() == [5000, 5001, 5002, 5003, 5004]
    assert by_position.index.tolist() == [5000, 5001, 5002, 5003]

    # 2. Shipped NL/BE orders worth at least 50: mask vs. query vs. plain Python
    mask = (df["status"] == "shipped") & df["country"].isin(["NL", "BE"]) & (df["value"] >= 50)
    big = df[mask]
    via_query = df.query("status == 'shipped' and country in ['NL', 'BE'] and value >= 50")
    plain = [
        r["order_id"] for r in rows
        if r["status"] == "shipped" and r["country"] in ("NL", "BE") and r["qty"] * r["unit_price"] >= 50
    ]
    print("big shipped NL/BE orders:", len(big), "| total value:", round(big["value"].sum(), 2))
    assert big.index.tolist() == via_query.index.tolist() == plain

    # 3. First week of October (between() is inclusive on both ends)
    week = df[df["date"].between("2026-10-01", "2026-10-07")]
    plain_week = [r["order_id"] for r in rows if "2026-10-01" <= r["date"] <= "2026-10-07"]
    print("orders 1-7 Oct:", len(week), "| per day:", week["date"].dt.day.value_counts().sort_index().to_dict())
    assert week.index.tolist() == plain_week

    # 4. Cancelled orders get qty 0 through loc; only those rows change
    before = df.copy()
    cancelled = df["status"] == "cancelled"
    df.loc[cancelled, "qty"] = 0
    df["value"] = df["qty"] * df["unit_price"]
    changed = (df["qty"] != before["qty"]) | (df["value"] != before["value"])
    print("cancelled:", int(cancelled.sum()), "| rows changed:", int(changed.sum()))
    assert changed.equals(cancelled)
    assert (df.loc[cancelled, "value"] == 0).all()
    assert df.loc[~cancelled].equals(before.loc[~cancelled])

    # 5. Sort by country A-Z then value high-to-low, keep the top 3 per country
    ranked = df.sort_values(["country", "value"], ascending=[True, False], kind="stable")
    top3 = ranked.groupby("country").head(3)
    print(top3[["country", "category", "qty", "unit_price", "value"]].round(2).to_string())

    # 6. Same top 3 in plain Python on the original records (cancelled -> value 0)
    def line_value(r: dict) -> float:
        return 0 if r["status"] == "cancelled" else r["qty"] * r["unit_price"]

    expected = []
    for country in sorted(COUNTRIES):
        mine = [r for r in rows if r["country"] == country]
        mine.sort(key=line_value, reverse=True)  # sort is stable, ties keep input order
        expected += [r["order_id"] for r in mine[:3]]
    assert top3.index.tolist() == expected
    print("all checks passed")


if __name__ == "__main__":
    main()
