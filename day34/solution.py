import csv
import io
import random
from collections import defaultdict
from datetime import date, timedelta

import pandas as pd

SWAP = str.maketrans(",.", ".,")


def nl_amount(x: float) -> str:
    """1234.5 -> '1.234,50' (Dutch thousands dot and decimal comma)."""
    return f"{x:,.2f}".translate(SWAP)


def make_export(seed: int, n: int = 60) -> str:
    """A fictional bank-style export: preamble, semicolons, Dutch numbers, a balance line."""
    rng = random.Random(seed)
    accounts = [f"{rng.randrange(10**9):010d}" for _ in range(4)]  # leading zeros on purpose
    lines = ["Rekeningoverzicht (fictional);", "Periode;2026-08-01 t/m 2026-10-31",
             "date;account;description;debit;credit"]
    balance = 0.0
    for _ in range(n):
        d = date(2026, 8, 1) + timedelta(days=rng.randrange(92))
        amount = round(rng.uniform(1, 2500), 2)
        is_debit = rng.random() < 0.6
        missing = rng.random() < 0.08  # amount not filled in by the bank
        debit = "--" if not is_debit or missing else nl_amount(amount)
        credit = "--" if is_debit or missing else nl_amount(amount)
        if not missing:
            balance += -amount if is_debit else amount
        desc = rng.choice(["groceries", "rent", "salary", "refund", "transfer", "energy"])
        lines.append(f"{d:%d-%m-%Y};{rng.choice(accounts)};{desc};{debit};{credit}")
    lines.append(f"Eindsaldo;;;;{nl_amount(balance)}")
    return "\n".join(lines) + "\n"


RAW = make_export(34)
OPTS = dict(sep=";", skiprows=2, decimal=",", thousands=".", na_values=["--"],
            dtype={"account": "string"}, engine="python")

# 1. One read_csv call with the right options
df = pd.read_csv(io.StringIO(RAW), skipfooter=1, **OPTS)
print(df.dtypes.to_string())
assert df["debit"].dtype == "float64" and df["credit"].dtype == "float64"
assert df["account"].str.len().eq(10).all()  # leading zeros kept
print("rows:", len(df), "| missing amounts:", int((df["debit"].isna() & df["credit"].isna()).sum()))

# 2. Dates and per-month totals
df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
monthly = df.groupby(df["date"].dt.to_period("M"))[["debit", "credit"]].sum().round(2)
print()
print(monthly)

# 3. Same totals from a chunked read (no skipfooter with chunks: drop the balance line)
parts = []
for chunk in pd.read_csv(io.StringIO(RAW), chunksize=15, **OPTS):
    chunk = chunk[chunk["date"] != "Eindsaldo"]
    month = pd.to_datetime(chunk["date"], format="%d-%m-%Y").dt.to_period("M")
    parts.append(chunk.groupby(month)[["debit", "credit"]].sum())
chunked = pd.concat(parts).groupby(level=0).sum().round(2)
pd.testing.assert_frame_equal(chunked, monthly, check_names=False)
print("\nchunked read matches")

# 4. Check against a plain csv-module parse
def parse_nl(s: str) -> float | None:
    return None if s == "--" else float(s.replace(".", "").replace(",", "."))


plain = defaultdict(lambda: [0.0, 0.0])
reader = csv.reader(io.StringIO(RAW), delimiter=";")
rows = list(reader)[3:-1]
for d, _account, _desc, debit, credit in rows:
    key = d[6:10] + "-" + d[3:5]
    plain[key][0] += parse_nl(debit) or 0.0
    plain[key][1] += parse_nl(credit) or 0.0
assert len(rows) == len(df)
for period, (deb, cred) in monthly.iterrows():
    assert abs(plain[str(period)][0] - deb) < 0.005
    assert abs(plain[str(period)][1] - cred) < 0.005
closing = parse_nl(RAW.strip().splitlines()[-1].split(";")[-1])
assert abs((df["credit"].sum() - df["debit"].sum()) - closing) < 0.005
print("closing balance", closing, "matches credits - debits")
print("\nall checks passed")
