import random
from collections import defaultdict
from datetime import date, timedelta

import pandas as pd

MEMBERS = ["m01", "m02", "m03", "m04", "m05"]
START = date(2026, 10, 1)


def make_visits(seed: int) -> list[dict]:
    """Fictional gym visits: member, date, minutes. Rows come out shuffled, at most one visit per day."""
    rng = random.Random(seed)
    rows = []
    for m in MEMBERS:
        days = sorted(rng.sample(range(31), rng.randint(2, 8)))
        for d in days:
            rows.append({"member": m, "date": START + timedelta(days=d), "minutes": rng.randint(20, 120)})
    rng.shuffle(rows)
    return rows


records = make_visits(35)
visits = pd.DataFrame(records)
visits["date"] = pd.to_datetime(visits["date"])

# 1. Per-row group statistics with transform
g = visits.groupby("member")["minutes"]
visits["share"] = visits["minutes"] / g.transform("sum")
visits["vs_avg"] = visits["minutes"] - g.transform("mean")

# 2. Number visits in date order, running minutes, gap since the previous visit
visits = visits.sort_values(["member", "date"])
gm = visits.groupby("member")
visits["visit_no"] = gm.cumcount() + 1
visits["running_min"] = gm["minutes"].cumsum()
visits["gap_days"] = gm["date"].diff().dt.days
print(visits.head(8).round({"share": 3, "vs_avg": 3}).to_string(index=False), "\n")

# 3. Regulars (4+ visits) and the longest gap any of them had
regulars = visits.groupby("member").filter(lambda d: len(d) >= 4)
reg_members = sorted(regulars["member"].unique())
longest_gap = regulars["gap_days"].max()
worst = regulars.loc[regulars["gap_days"].idxmax(), ["member", "date"]]
print("regulars:", reg_members, f"- longest gap {longest_gap:.0f} days ({worst['member']}, back on {worst['date']:%Y-%m-%d})")

# 4. Longest visit and first visit per member
longest = visits.loc[gm["minutes"].idxmax(), ["member", "date", "minutes"]]
first = gm.head(1)[["member", "date"]]
print("\nlongest visit per member:")
print(longest.to_string(index=False))
print("\nfirst visits:", [f"{m} {d:%m-%d}" for m, d in first.itertuples(index=False)])

# --- 5. check against plain Python ---
by_member: dict[str, list[tuple[date, int]]] = defaultdict(list)
for r in records:
    by_member[r["member"]].append((r["date"], r["minutes"]))
plain_gaps = []
for m, rows in by_member.items():
    rows.sort()
    total = sum(mins for _, mins in rows)
    avg = total / len(rows)
    mine = visits[visits["member"] == m]
    assert mine["visit_no"].tolist() == list(range(1, len(rows) + 1))
    running = 0
    for (d, mins), (_, row) in zip(rows, mine.iterrows()):
        running += mins
        assert row["date"].date() == d and row["minutes"] == mins
        assert abs(row["share"] - mins / total) < 1e-12
        assert abs(row["vs_avg"] - (mins - avg)) < 1e-9
        assert row["running_min"] == running
    gaps = [(b[0] - a[0]).days for a, b in zip(rows, rows[1:])]
    assert mine["gap_days"].iloc[1:].tolist() == gaps and pd.isna(mine["gap_days"].iloc[0])
    if len(rows) >= 4:
        plain_gaps += gaps
    best = max(rows, key=lambda t: t[1])  # first on ties, same as idxmax after sorting by date
    lrow = longest[longest["member"] == m].iloc[0]
    assert (lrow["date"].date(), lrow["minutes"]) == best
    assert first[first["member"] == m]["date"].iloc[0].date() == rows[0][0]
assert reg_members == sorted(m for m, rows in by_member.items() if len(rows) >= 4)
assert longest_gap == max(plain_gaps)
print("\nall checks passed")
