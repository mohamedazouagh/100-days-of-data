import math
import random

import numpy as np
import pandas as pd

ZONES = {"NL": "home", "BE": "near", "LU": "near", "DE": "near", "FR": "eu", "ES": "eu", "IT": "eu"}
PROMISE = {"home": 1, "near": 2, "eu": 4, "other": 7}  # promised delivery days per zone
FREE_FROM, HEAVY_KG = 75.0, 20.0
STANDARD_FEE, HEAVY_FEE = 4.95, 12.50


def make_parcels(seed: int, n: int = 400) -> list[dict]:
    """Fictional parcels with refunds, unknown country codes, odd weights and bad day counts."""
    rng = random.Random(seed)
    codes = list(ZONES) + ["XX", "US", "nl"]  # unknown codes, including a lower-case typo
    rows = []
    for i in range(n):
        amount = round(rng.uniform(5, 160), 2) if rng.random() > 0.07 else -round(rng.uniform(5, 60), 2)
        weight = round(rng.choice([rng.uniform(0.0, 3), rng.uniform(3, 25), rng.uniform(25, 60)]), 2)
        days = rng.randint(0, 9) if rng.random() > 0.04 else -1  # -1 = scanner error
        rows.append({"parcel": 1000 + i, "country": rng.choice(codes), "amount": amount,
                     "weight": weight, "days": days})
    return rows


def py_fee(r: dict) -> float:
    if r["amount"] < 0:
        return 0.0
    if r["amount"] >= FREE_FROM:
        return 0.0
    if r["weight"] > HEAVY_KG:
        return HEAVY_FEE
    return STANDARD_FEE


def py_row(r: dict) -> dict:
    zone = ZONES.get(r["country"], "other")
    weight = min(max(r["weight"], 0.1), 30.0)
    days = r["days"] if r["days"] >= 0 else None
    late = days is not None and days > PROMISE[zone]
    return {"shipping": py_fee(r), "zone": zone, "weight_c": weight, "days_c": days, "late": late}


def main() -> None:
    records = make_parcels(seed=31)
    df = pd.DataFrame(records)
    print(f"{len(df)} parcels, {int((df['amount'] < 0).sum())} refunds, "
          f"{int((df['days'] < 0).sum())} bad day counts")

    # 1. shipping fee: first matching condition wins, so the refund check comes first
    conditions = [df["amount"] < 0, df["amount"] >= FREE_FROM, df["weight"] > HEAVY_KG]
    df["shipping"] = np.select(conditions, [0.0, 0.0, HEAVY_FEE], default=STANDARD_FEE)
    print("\n1. parcels per fee:", df["shipping"].value_counts().sort_index().to_dict())

    # 2. zones by lookup; unknown codes go to "other" but are listed, not hidden
    zone = df["country"].map(ZONES)
    unknown = sorted(df.loc[zone.isna(), "country"].unique())
    df["zone"] = zone.fillna("other")
    print("2. unknown codes:", unknown, "| parcels per zone:", df["zone"].value_counts().to_dict())

    # 3. clip weights, turn negative day counts into NaN
    df["weight_c"] = df["weight"].clip(lower=0.1, upper=30.0)
    df["days_c"] = df["days"].where(df["days"] >= 0)
    print(f"3. weights clipped: {int((df['weight'] != df['weight_c']).sum())}, "
          f"days set to NaN: {int(df['days_c'].isna().sum())}")

    # 4. late = more days than the zone promises (NaN days compare False, so never late)
    df["late"] = df["days_c"] > df["zone"].map(PROMISE)
    late_share = df.groupby("zone")["late"].mean().mul(100).round(1)
    print("4. late % per zone:", late_share.to_dict())

    # 5. the same columns with apply(axis=1) and with a plain loop
    cols = ["shipping", "zone", "weight_c", "days_c", "late"]
    applied = df[["country", "amount", "weight", "days"]].apply(lambda r: pd.Series(py_row(r)), axis=1)
    loop = [py_row(r) for r in records]
    for c in cols:
        for v, a, p in zip(df[c], applied[c], (x[c] for x in loop)):
            if p is None:
                assert pd.isna(v) and pd.isna(a), c
            elif isinstance(p, float):
                assert math.isclose(v, p) and math.isclose(a, p), c
            else:
                assert v == p and a == p, c
    print("\n5. vectorised, apply(axis=1) and the plain loop agree on all",
          len(cols), "columns for all", len(df), "parcels")


if __name__ == "__main__":
    main()
