import math
import random
import re

import pandas as pd

# (group, number, product name, pack size in ml): a fictional drinks range
BASE = [
    ("DRK", 12, "Oat Milk", 1000),
    ("DRK", 31, "Almond Milk", 1000),
    ("DRK", 55, "Rice Drink", 1500),
    ("JCE", 3, "Orange Juice", 750),
    ("JCE", 18, "Apple Juice", 330),
    ("WTR", 1, "Sparkling Water", 500),
]
BASE_PRICE = {12: 1.89, 31: 2.49, 55: 2.19, 3: 2.29, 18: 0.99, 1: 0.65}
CODE_RE = r"(?i)^(?P<group>[a-z]{3})[-_ ]?(?P<num>\d{1,4})$"
SIZE_RE = r"(?i)(?P<qty>\d+(?:[.,]\d+)?)\s*(?P<unit>ml|cl|l)\b"
UNIT_ML = {"ml": 1, "cl": 10, "l": 1000}


def messy_name(rng: random.Random, name: str) -> str:
    style = rng.choice([str.title, str.lower, str.upper, str])
    words = style(name).split(" ")
    return " " * rng.randint(0, 2) + (" " * rng.randint(1, 3)).join(words) + " " * rng.randint(0, 2)


def messy_code(rng: random.Random, group: str, num: int) -> str:
    return rng.choice([
        f"{group}-{num:04d}", f"{group.lower()}-{num}", f"{group}_{num:04d}", f"{group} {num}",
        f"{group}/{num:04d}",  # a supplier style the pattern deliberately rejects
    ])


def messy_price(rng: random.Random, price: float) -> str:
    text = f"{price:.2f}"
    return rng.choice([f"€ {text.replace('.', ',')}", f"{text} EUR", f"EUR{text.replace('.', ',')}", f"€{text}"])


def messy_size(rng: random.Random, ml: int) -> str:
    options = [f"{ml} ml", f"{ml}ml", f"{ml / 10:g} cl", f"{ml / 1000:g} L", f"{ml / 1000:g}l".replace(".", ",")]
    return rng.choice(options)


def make_price_list(seed: int) -> list[dict]:
    """Fictional supplier rows: every product appears 2-4 times with its own spelling and price."""
    rng = random.Random(seed)
    rows = []
    for group, num, name, ml in BASE:
        for _ in range(rng.randint(2, 4)):
            price = round(BASE_PRICE[num] * rng.uniform(0.9, 1.1), 2)
            rows.append({
                "name": messy_name(rng, name),
                "code": messy_code(rng, group, num),
                "price": messy_price(rng, price),
                "size": messy_size(rng, ml),
            })
    rng.shuffle(rows)
    return rows


def close(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)


def main() -> None:
    records = make_price_list(seed=28)
    df = pd.DataFrame(records)
    print(f"{len(df)} supplier rows, for example:")
    print(df.head(4).to_string())

    # 1. Normalise names
    df["name_clean"] = df["name"].str.strip().str.lower().str.replace(r"\s+", " ", regex=True)
    names = sorted(df["name_clean"].unique())
    print(f"\n1. {df['name'].nunique()} raw spellings -> {len(names)} products:", names)
    py_names = sorted({" ".join(r["name"].split()).lower() for r in records})
    assert names == py_names

    # 2. One key per code; list the codes that do not fit the pattern
    parts = df["code"].str.extract(CODE_RE)
    ok = parts["num"].notna()
    df["key"] = (parts["group"].str.upper() + "-" + parts["num"].str.zfill(4).where(ok)).where(ok)
    bad = df.loc[~ok, "code"].tolist()
    print(f"\n2. {ok.sum()} codes -> {df['key'].nunique()} keys; rejected: {bad}")
    for r, key in zip(records, df["key"]):
        m = re.match(CODE_RE, r["code"])
        assert (key if isinstance(key, str) else None) == (
            f"{m['group'].upper()}-{int(m['num']):04d}" if m else None
        )

    # 3. Price text -> float: keep digits and separators, then use "." as the decimal point
    df["price_eur"] = (
        df["price"].str.replace(r"[^\d,.]", "", regex=True).str.replace(",", ".", regex=False).astype(float)
    )
    print("\n3. prices:", sorted(df["price_eur"].tolist()))
    for r, p in zip(records, df["price_eur"]):
        digits = "".join(ch for ch in r["price"] if ch.isdigit() or ch in ",.")
        assert close(p, float(digits.replace(",", ".")))

    # 4. Pack size -> ml, then price per litre
    size = df["size"].str.extract(SIZE_RE)
    qty = size["qty"].str.replace(",", ".", regex=False).astype(float)
    df["ml"] = (qty * size["unit"].str.lower().map(UNIT_ML)).round().astype(int)
    df["eur_per_l"] = (df["price_eur"] / df["ml"] * 1000).round(2)
    table = (
        df.groupby("name_clean")
        .agg(rows=("key", "size"), ml=("ml", "first"), min_eur_l=("eur_per_l", "min"), max_eur_l=("eur_per_l", "max"))
        .sort_values("min_eur_l")
    )
    print("\n4. price per litre by product:")
    print(table.to_string())
    assert (df.groupby("name_clean")["ml"].nunique() == 1).all()  # every spelling agrees on the size
    for r, ml, per_l in zip(records, df["ml"], df["eur_per_l"]):
        m = re.search(SIZE_RE, r["size"])
        py_ml = round(float(m["qty"].replace(",", ".")) * UNIT_ML[m["unit"].lower()])
        assert ml == py_ml
        price = float("".join(ch for ch in r["price"] if ch.isdigit() or ch in ",.").replace(",", "."))
        assert close(per_l, round(price / py_ml * 1000, 2))
    cheapest = table.index[0]
    print(f"\nCheapest per litre: {cheapest} at {table.loc[cheapest, 'min_eur_l']:.2f} EUR/l")
    print("\n5. all checks against plain Python passed")


if __name__ == "__main__":
    main()
