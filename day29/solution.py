import bisect
import random
from collections import Counter

import pandas as pd

SIZES = ["XS", "S", "M", "L", "XL"]
AGE_EDGES = [0, 18, 30, 45, 65, 120]
AGE_LABELS = ["<18", "18-29", "30-44", "45-64", "65+"]
DELIVERY_EDGES = [0, 24, 48, float("inf")]
DELIVERY_LABELS = ["same day", "next day", "later"]


def make_orders(seed: int, n: int = 60) -> list[dict]:
    """Fictional order log; XS is never bought and a few sizes are typed wrong."""
    rng = random.Random(seed)
    rows = []
    for i in range(n):
        size = rng.choices(["S", "M", "L", "XL", "XXL", "m"], weights=[20, 35, 25, 15, 3, 2])[0]
        rows.append({
            "order_id": 1000 + i,
            "size": size,
            "age": rng.randint(18, 79),
            "amount": round(rng.lognormvariate(3.2, 0.6), 2),
            "delivery_h": round(rng.uniform(4, 90), 1),
        })
    return rows


def band(value: float, edges: list[float], labels: list[str]) -> str:
    """Left-closed band [edges[i], edges[i+1]) for ``value``, the plain-Python twin of pd.cut."""
    i = bisect.bisect_right(edges, value) - 1
    return labels[i]


def main() -> None:
    records = make_orders(seed=29)
    df = pd.DataFrame(records)
    print(f"{len(df)} orders, for example:")
    print(df.head(4).to_string(index=False))

    # 1. Ordered sizes; unknown labels listed first, then counts in size order incl. zeros
    size_type = pd.CategoricalDtype(SIZES, ordered=True)
    unknown = df.loc[~df["size"].isin(SIZES), ["order_id", "size"]]
    print(f"\n1. unknown sizes ({len(unknown)}):", unknown.to_dict("records"))
    known = df[df["size"].isin(SIZES)].copy()
    known["size"] = known["size"].astype(size_type)
    per_size = known.groupby("size", observed=False).size()
    print("orders per size:", per_size.to_dict())
    py_counts = Counter(r["size"] for r in records)
    assert per_size.to_dict() == {s: py_counts.get(s, 0) for s in SIZES}
    assert sorted(unknown["order_id"]) == [r["order_id"] for r in records if r["size"] not in SIZES]
    assert (known["size"] >= "L").sum() == sum(r["size"] in ("L", "XL") for r in records)

    # 2. Age bands, left-closed
    df["age_band"] = pd.cut(df["age"], bins=AGE_EDGES, right=False, labels=AGE_LABELS)
    print("\n2. orders per age band:", df.groupby("age_band", observed=False).size().to_dict())
    for r, b in zip(records, df["age_band"]):
        assert b == band(r["age"], AGE_EDGES, AGE_LABELS)

    # 3. Four equal-sized spend tiers
    df["tier"], edges = pd.qcut(df["amount"], q=4, labels=["low", "mid", "high", "top"], retbins=True)
    print("\n3. tier sizes:", df["tier"].value_counts(sort=False).to_dict())
    print("   edges (EUR):", [round(float(e), 2) for e in edges])
    assert df["tier"].value_counts().max() - df["tier"].value_counts().min() <= 1
    amounts = sorted(r["amount"] for r in records)
    assert float(edges[0]) == amounts[0] and float(edges[-1]) == amounts[-1]
    for r, t in zip(records, df["tier"]):
        # qcut bins are right-closed, with the lowest value included in the first bin
        i = max(bisect.bisect_left(list(edges), r["amount"]) - 1, 0)
        assert t == ["low", "mid", "high", "top"][i]

    # 4. Delivery bands and an age x delivery table that keeps empty cells
    df["delivery"] = pd.cut(df["delivery_h"], bins=DELIVERY_EDGES, right=False, labels=DELIVERY_LABELS)
    table = df.groupby(["age_band", "delivery"], observed=False).size().unstack("delivery")
    print("\n4. orders by age band and delivery band:")
    print(table.to_string())
    py_table = Counter(
        (band(r["age"], AGE_EDGES, AGE_LABELS), band(r["delivery_h"], DELIVERY_EDGES, DELIVERY_LABELS))
        for r in records
    )
    assert table.shape == (len(AGE_LABELS), len(DELIVERY_LABELS))
    for a in AGE_LABELS:
        for d in DELIVERY_LABELS:
            assert table.loc[a, d] == py_table.get((a, d), 0)
    print(f"   empty cells kept: {int((table == 0).sum().sum())}")
    print("\n5. all checks against plain Python passed")


if __name__ == "__main__":
    main()
