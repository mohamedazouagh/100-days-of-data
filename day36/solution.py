import random
from decimal import Decimal, InvalidOperation

import pandas as pd

COUNTRIES = ["NL", "BE", "DE", "FR"]


def make_export(seed: int, n: int = 40) -> list[dict]:
    """Fictional order export where every field is text and some cells are broken."""
    rng = random.Random(seed)
    rows = []
    for i in range(n):
        qty = str(rng.randint(1, 5))
        price = f"{rng.randint(2, 60)}.{rng.choice(['00', '50', '95'])}"
        paid = rng.choice(["Y", "N", "Y", "Y"])
        r = rng.random()
        if r < 0.08:
            qty = rng.choice(["", "x", "two"])
        elif r < 0.16:
            price = price.replace(".", ",")  # decimal comma: fixable
        elif r < 0.22:
            price = rng.choice(["free", "-", ""])  # not a price: lost
        elif r < 0.28:
            paid = rng.choice(["", "?"])
        rows.append({"order": f"o{i:03d}", "country": rng.choice(COUNTRIES),
                     "qty": qty, "price": price, "paid": paid})
    return rows


records = make_export(36)
raw = pd.DataFrame(records)

# 1. Convert the numbers, fixing decimal commas first, and list every cell that was lost
qty = pd.to_numeric(raw["qty"], errors="coerce").astype("Int64")
price = pd.to_numeric(raw["price"].str.replace(",", ".", regex=False), errors="coerce")
lost = {
    "qty": raw.loc[qty.isna(), "qty"].tolist(),
    "price": raw.loc[price.isna(), "price"].tolist(),
}
print("lost cells:", lost)

# 2. Flags to nullable boolean, labels to category
paid = raw["paid"].map({"Y": True, "N": False}).astype("boolean")
clean = pd.DataFrame({
    "order": raw["order"],
    "country": raw["country"].astype("category"),
    "qty": qty,
    "price": price,
    "paid": paid,
})
print(clean.dtypes.to_string())

# 3. Paid revenue per country, only rows where qty, price and paid are all known
known = clean.dropna(subset=["qty", "price", "paid"])
paid_rows = known[known["paid"]]
revenue = (paid_rows["qty"] * paid_rows["price"]).groupby(paid_rows["country"], observed=True).sum().round(2)
print("paid revenue:", revenue.to_dict())
print("unknown paid status:", int(clean["paid"].isna().sum()), "orders")

# 4. Memory before and after on a bigger copy
big_raw = pd.concat([raw] * 5_000, ignore_index=True)
big_clean = pd.concat([clean] * 5_000, ignore_index=True)
before = big_raw.memory_usage(deep=True).sum()
after = big_clean.memory_usage(deep=True).sum()
print(f"{len(big_raw):,} rows: {before / 1e6:.1f} MB -> {after / 1e6:.1f} MB ({after / before:.0%})")

# 5. Check against a plain-Python version with Decimal money maths
def parse_int(s):
    return int(s) if s.isdigit() else None


def parse_price(s):
    s = s.replace(",", ".")
    try:
        return Decimal(s)
    except InvalidOperation:
        return None


expected_lost = {"qty": [], "price": []}
expected_rev: dict[str, Decimal] = {}
for r in records:
    q, p = parse_int(r["qty"]), parse_price(r["price"])
    if q is None:
        expected_lost["qty"].append(r["qty"])
    if p is None:
        expected_lost["price"].append(r["price"])
    if q is not None and p is not None and r["paid"] == "Y":
        expected_rev[r["country"]] = expected_rev.get(r["country"], Decimal(0)) + q * p

assert lost == expected_lost
assert {k: float(v) for k, v in expected_rev.items()} == revenue.to_dict()
assert int(clean["paid"].isna().sum()) == sum(r["paid"] not in ("Y", "N") for r in records)
assert str(clean["qty"].dtype) == "Int64" and str(clean["paid"].dtype) == "boolean"
assert after < before
print("all checks passed")
