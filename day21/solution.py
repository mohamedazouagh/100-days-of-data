import math
import random
from datetime import datetime, timedelta

import pandas as pd

STATIONS = ["north", "harbour", "park", "station"]


def make_readings(seed: int, n: int = 200) -> list[dict]:
    """Fictional sensor readings every 30 minutes; ~4% of the values are missing."""
    rng = random.Random(seed)
    start = datetime(2026, 10, 1, 0, 0)
    rows = []
    for i in range(n):
        temp = round(rng.gauss(12, 3), 1) if rng.random() > 0.04 else None
        hum = round(rng.uniform(55, 98), 1) if rng.random() > 0.04 else None
        rows.append({
            "station": STATIONS[i % len(STATIONS)],
            "ts": (start + timedelta(minutes=30 * i)).strftime("%Y-%m-%d %H:%M"),
            "temp_c": temp,
            "humidity": hum,
        })
    return rows


def pandas_summary(df: pd.DataFrame, col: str) -> dict:
    s = df[col]
    return {"count": int(s.count()), "mean": float(s.mean()), "min": float(s.min()), "max": float(s.max())}


def python_summary(rows: list[dict], col: str) -> dict:
    vals = [r[col] for r in rows if r[col] is not None]
    return {"count": len(vals), "mean": sum(vals) / len(vals), "min": min(vals), "max": max(vals)}


def main() -> None:
    rows = make_readings(seed=21)

    # 1. Build and inspect
    df = pd.DataFrame(rows)
    print("shape:", df.shape)
    print(df.dtypes.to_string())
    missing = df.isna().sum()
    print("missing per column:", missing.to_dict())
    assert df.shape == (len(rows), 4)
    assert missing["temp_c"] == sum(r["temp_c"] is None for r in rows)
    assert missing["humidity"] == sum(r["humidity"] is None for r in rows)

    # 2. Timestamps: text -> datetime
    df["ts"] = pd.to_datetime(df["ts"], format="%Y-%m-%d %H:%M")
    print("first reading:", df["ts"].min(), "| last reading:", df["ts"].max())
    assert df["ts"].is_monotonic_increasing
    assert df["ts"].max() - df["ts"].min() == pd.Timedelta(minutes=30 * (len(rows) - 1))

    # 3. Derived columns
    df["temp_f"] = df["temp_c"] * 9 / 5 + 32
    df["humid"] = df["humidity"] > 80
    print(df.head(4).to_string(index=False))
    print("humid readings:", int(df["humid"].sum()))
    # NaN > 80 is False, so missing humidity never counts as humid
    assert int(df["humid"].sum()) == sum(1 for r in rows if r["humidity"] is not None and r["humidity"] > 80)
    assert df["temp_f"].isna().sum() == missing["temp_c"]

    # 4 + 5. Summaries, checked against plain Python on the original records
    for col in ("temp_c", "humidity"):
        pd_sum, py_sum = pandas_summary(df, col), python_summary(rows, col)
        print(f"{col:9}", {k: round(v, 2) for k, v in pd_sum.items()})
        assert pd_sum["count"] == py_sum["count"]
        for key in ("mean", "min", "max"):
            assert math.isclose(pd_sum[key], py_sum[key], rel_tol=1e-12), (col, key)
    print("all checks passed: pandas matches the plain-Python results")


if __name__ == "__main__":
    main()
