import math
import random
from collections import defaultdict

import pandas as pd

CATEGORIES = {"tea": 4.50, "coffee": 7.25, "mug": 9.95, "biscuits": 3.20, "teapot": 24.00}
VOUCHERS = {"": 0.0, "WELCOME10": 0.10, "LOYAL15": 0.15}
SIZE_BINS = [0, 20, 60, math.inf]
SIZE_LABELS = ["small", "medium", "large"]


def make_log(seed: int, n_orders: int = 250) -> list[dict]:
    """Fictional order lines: several lines per order, some cancelled orders, zero quantities."""
    rng = random.Random(seed)
    rows = []
    for order in range(5000, 5000 + n_orders):
        status = "cancelled" if rng.random() < 0.08 else "paid"
        voucher = rng.choice(["", "", "", "WELCOME10", "LOYAL15"])
        for product in rng.sample(list(CATEGORIES), k=rng.randint(1, 3)):
            qty = rng.randint(0, 4) if rng.random() < 0.1 else rng.randint(1, 4)
            rows.append({"order id": order, "status": status, "category": product,
                         "qty": qty, "unit_price": CATEGORIES[product], "voucher": voucher})
    return rows


def add_order_size(d: pd.DataFrame) -> pd.DataFrame:
    """Label every line with the size of its whole order (by order net total)."""
    total = d.groupby("order id")["net"].transform("sum")
    return d.assign(order_size=pd.cut(total, SIZE_BINS, labels=SIZE_LABELS, right=False))


def tap(d: pd.DataFrame, label: str) -> pd.DataFrame:
    print(f"  [{label}] {d.shape[0]} rows x {d.shape[1]} cols")
    return d


def summarise(d: pd.DataFrame) -> pd.DataFrame:
    return (
        d.groupby("category")
        .agg(orders=("order id", "nunique"), units=("qty", "sum"), revenue=("net", "sum"))
        .assign(avg_per_order=lambda s: s["revenue"] / s["orders"])
        .sort_values("revenue", ascending=False)
    )


def chain(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    lines = (
        raw
        .pipe(tap, "raw")
        .query("status == 'paid' and qty > 0")
        .pipe(tap, "paid, qty > 0")
        .assign(
            gross=lambda d: d["qty"] * d["unit_price"],
            voucher_off=lambda d: d["gross"] * d["voucher"].map(VOUCHERS),
            net=lambda d: d["gross"] - d["voucher_off"],
        )
        .pipe(add_order_size)
        .pipe(tap, "with money columns and order size")
    )
    return lines, lines.pipe(summarise)


def step_by_step(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    df = df[df["status"] == "paid"]
    df = df[df["qty"] > 0]
    df["gross"] = df["qty"] * df["unit_price"]
    df["voucher_off"] = df["gross"] * df["voucher"].map(VOUCHERS)
    df["net"] = df["gross"] - df["voucher_off"]
    return summarise(df)


def plain_loop(records: list[dict]) -> dict[str, tuple[int, int, float]]:
    orders, units, revenue = defaultdict(set), defaultdict(int), defaultdict(float)
    for r in records:
        if r["status"] != "paid" or r["qty"] <= 0:
            continue
        gross = r["qty"] * r["unit_price"]
        net = gross - gross * VOUCHERS[r["voucher"]]
        orders[r["category"]].add(r["order id"])
        units[r["category"]] += r["qty"]
        revenue[r["category"]] += net
    return {c: (len(orders[c]), units[c], revenue[c]) for c in orders}


def main() -> None:
    records = make_log(seed=32)
    raw = pd.DataFrame(records)
    before = raw.copy()
    print(f"{len(raw)} order lines in {raw['order id'].nunique()} orders, "
          f"{int((raw['status'] == 'cancelled').sum())} cancelled lines, {int((raw['qty'] == 0).sum())} zero quantities")

    # 1-2. one chain: filter, money columns, order size; tap prints the shape at each stage
    print("\n1-2. chain:")
    lines, summary = chain(raw)
    sizes = lines.drop_duplicates("order id")["order_size"].value_counts().reindex(SIZE_LABELS)
    print("     orders per size:", sizes.to_dict())

    # 3. per-category summary at the end of the chain
    print("\n3. per category:")
    print(summary.round(2).to_string())

    # 4. raw log untouched, and the same numbers three ways
    assert raw.equals(before), "the chain must not modify the raw log"
    stepwise = step_by_step(raw)
    pd.testing.assert_frame_equal(summary, stepwise)
    loop = plain_loop(records)
    assert set(loop) == set(summary.index)
    for cat, (n_orders, n_units, rev) in loop.items():
        row = summary.loc[cat]
        assert row["orders"] == n_orders and row["units"] == n_units, cat
        assert math.isclose(row["revenue"], rev, rel_tol=1e-12), cat
    print("\n4. raw log unchanged; chain, step-by-step and the plain loop agree for all",
          len(loop), "categories")


if __name__ == "__main__":
    main()
