import math
import random
import statistics

import numpy as np
import pandas as pd

CITIES = ["Breda", "Utrecht", "Gouda", "Delft", "Leiden"]
PLACEHOLDER_CITIES = {"n/a", "-"}


def make_customers(seed: int, n: int = 120) -> list[dict]:
    """Fictional customer export: placeholders, gaps and re-exported customers."""
    rng = random.Random(seed)
    rows = []
    for cid in range(1, n + 1):
        r = rng.random()
        if r < 0.08:
            email = None
        elif r < 0.14:
            email = rng.choice(["", "   "])
        else:
            email = f"customer{cid}@example.com"
        city = rng.choice(CITIES + ["n/a", "-"]) if rng.random() < 0.2 else rng.choice(CITIES)
        if rng.random() < 0.05:
            city = None
        rows.append({
            "customer_id": cid,
            "email": email,
            "city": city,
            "age": None if rng.random() < 0.15 else rng.randint(18, 75),
            "orders": None if rng.random() < 0.1 else rng.randint(0, 12),
        })
    # Re-export ~15 customers later in the file with a newer order count
    for row in rng.sample(rows, 15):
        newer = dict(row)
        newer["orders"] = (row["orders"] or 0) + rng.randint(1, 3)
        rows.append(newer)
    return rows


def is_missing(value) -> bool:
    return value is None or (isinstance(value, float) and math.isnan(value))


def close(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)


def main() -> None:
    rows = make_customers(seed=24)
    df = pd.DataFrame(rows)
    print("rows:", len(df), "| distinct customers:", df["customer_id"].nunique())

    # 1. Missing values before and after converting placeholders
    before = df.isna().sum()
    df["email"] = df["email"].str.strip().replace("", np.nan)
    df["city"] = df["city"].replace(sorted(PLACEHOLDER_CITIES), np.nan)
    after = df.isna().sum()
    print("\n1. missing per column (before -> after placeholders):")
    print(pd.DataFrame({"before": before, "after": after}))

    py_clean = []
    for r in rows:
        email = None if r["email"] is None or not r["email"].strip() else r["email"].strip()
        city = None if r["city"] is None or r["city"] in PLACEHOLDER_CITIES else r["city"]
        py_clean.append({**r, "email": email, "city": city})
    for col in ["customer_id", "email", "city", "age", "orders"]:
        assert before[col] == sum(r[col] is None for r in rows)
        assert after[col] == sum(r[col] is None for r in py_clean)
    assert after["email"] > before["email"] and after["city"] > before["city"]

    # 2. Drop repeated ids, keeping the last (newest) row
    print("\n2. whole-row duplicates:", int(df.duplicated().sum()),
          "| repeated ids:", int(df.duplicated(subset=["customer_id"]).sum()))
    deduped = df.drop_duplicates(subset=["customer_id"], keep="last")
    print("rows after dedupe:", len(deduped))
    assert deduped["customer_id"].is_unique
    last_by_id = {}
    for r in py_clean:
        last_by_id[r["customer_id"]] = r  # later rows overwrite earlier ones
    assert len(deduped) == len(last_by_id)
    for rec in deduped.itertuples():
        expected = last_by_id[rec.customer_id]["orders"]
        assert (is_missing(rec.orders) and expected is None) or rec.orders == expected

    # 3. Customers we can email
    emailable = deduped.dropna(subset=["email"])
    print("\n3. emailable customers:", len(emailable), "of", len(deduped))
    assert len(emailable) == sum(r["email"] is not None for r in last_by_id.values())

    # 4. Fill cities and ages; leave orders missing on purpose
    median_age = deduped["age"].median()
    filled = deduped.fillna({"city": "unknown", "age": median_age})
    print(f"\n4. median age used for gaps: {median_age}")
    print(filled["city"].value_counts().to_dict())
    py_ages = [r["age"] for r in last_by_id.values() if r["age"] is not None]
    assert close(median_age, statistics.median(py_ages))
    assert filled["city"].isna().sum() == 0 and filled["age"].isna().sum() == 0
    assert filled["orders"].isna().sum() == sum(r["orders"] is None for r in last_by_id.values())
    assert (filled["city"] == "unknown").sum() == sum(r["city"] is None for r in last_by_id.values())

    # 5. NaN skipped vs. NaN treated as zero
    skip = deduped["orders"].mean()
    zero = deduped["orders"].fillna(0).mean()
    print(f"\n5. average orders: {skip:.3f} with NaN skipped vs. {zero:.3f} with NaN as 0")
    py_orders = [r["orders"] for r in last_by_id.values()]
    known = [o for o in py_orders if o is not None]
    assert close(skip, sum(known) / len(known))
    assert close(zero, sum(known) / len(py_orders))
    assert zero < skip

    print("\nall checks passed")


if __name__ == "__main__":
    main()
