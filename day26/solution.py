import math
import random
from collections import defaultdict

import pandas as pd

STORES = ["Breda", "Delft", "Gouda"]
PRODUCTS = ["coffee", "tea", "cocoa"]
MONTHS = ["2026-07", "2026-08", "2026-09", "2026-10"]


def make_sheet(seed: int) -> list[dict]:
    """Fictional wide sales sheet: one row per (store, product), one key per month, None = not reported."""
    rng = random.Random(seed)
    rows = []
    for store in STORES:
        for product in PRODUCTS:
            row = {"store": store, "product": product}
            for month in MONTHS:
                row[month] = None if rng.random() < 0.12 else rng.randint(20, 160)
            rows.append(row)
    return rows


def close(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)


def main() -> None:
    sheet = make_sheet(seed=26)
    wide = pd.DataFrame(sheet)
    reported = [(r["store"], r["product"], m, r[m]) for r in sheet for m in MONTHS if r[m] is not None]

    # 1. Wide -> long, parse months, drop unreported cells
    long = wide.melt(id_vars=["store", "product"], var_name="month", value_name="sales")
    assert len(long) == len(sheet) * len(MONTHS)
    long = long.dropna(subset=["sales"]).copy()
    long["month"] = pd.to_datetime(long["month"], format="%Y-%m")
    long["sales"] = long["sales"].astype("Int64")
    missing = len(sheet) * len(MONTHS) - len(long)
    print(f"1. long rows: {len(long)} reported, {missing} unreported cells dropped")
    assert len(long) == len(reported)
    assert long["month"].dt.month.isin([7, 8, 9, 10]).all()

    # 2. Store x month totals with margins
    table = long.pivot_table(index="store", columns="month", values="sales", aggfunc="sum",
                             fill_value=0, margins=True, margins_name="total")
    table.columns = [c if c == "total" else c.strftime("%Y-%m") for c in table.columns]
    print("\n2. sales per store and month:")
    print(table)
    py_totals = defaultdict(int)
    for store, _, month, sales in reported:
        py_totals[(store, month)] += sales
    for store in STORES:
        for month in MONTHS:
            assert table.loc[store, month] == py_totals[(store, month)]
        assert table.loc[store, "total"] == sum(py_totals[(store, m)] for m in MONTHS)
    assert table.loc["total", "total"] == long["sales"].sum() == sum(s for *_, s in reported)

    # 3. pivot refuses duplicates; a full key round-trips
    try:
        long.pivot(index="store", columns="month", values="sales")
        raise AssertionError("expected pivot to fail on duplicate (store, month) pairs")
    except ValueError as e:
        print("\n3. pivot on store x month:", e)
    back = long.pivot(index=["store", "product"], columns="month", values="sales")
    back.columns = [c.strftime("%Y-%m") for c in back.columns]
    # pivot sorts the index (coffee, cocoa, tea), so put rows back in the sheet's order
    order = pd.MultiIndex.from_tuples([(r["store"], r["product"]) for r in sheet], names=["store", "product"])
    back = back.reindex(index=order, columns=MONTHS).reset_index()
    for orig, (_, row) in zip(sheet, back.iterrows(), strict=True):
        assert (orig["store"], orig["product"]) == (row["store"], row["product"])
        for m in MONTHS:
            assert (orig[m] is None and pd.isna(row[m])) or orig[m] == row[m]
    print("   pivot on (store, product) x month round-trips to the original", back.shape, "sheet")

    # 4. Best month per store via stack + idxmax
    per_month = table.drop(index="total", columns="total")
    best = per_month.stack().groupby(level="store").idxmax()
    print("\n4. best month per store:")
    for store, (_, month) in best.items():
        print(f"   {store}: {month} ({per_month.loc[store, month]})")
        top = max(MONTHS, key=lambda m: (py_totals[(store, m)], -MONTHS.index(m)))
        assert month == top
    print("\nall checks passed")


if __name__ == "__main__":
    main()
