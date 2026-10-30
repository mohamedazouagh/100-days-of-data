import math
import random
from datetime import date, timedelta

import pandas as pd

BRANCHES = ["Centrum", "Haven", "Station"]
START = date(2026, 3, 2)
DAYS = 35


def make_visits(seed: int) -> list[dict]:
    """Fictional visitor counts; a few days per branch are missing and some are closed (0)."""
    rng = random.Random(seed)
    rows = []
    for branch in BRANCHES:
        base = rng.randint(60, 120)
        for i in range(DAYS):
            if rng.random() < 0.1:
                continue  # counter offline: no row at all
            day = START + timedelta(days=i)
            visitors = 0 if rng.random() < 0.06 else max(0, round(rng.gauss(base, 20)))
            rows.append({"branch": branch, "day": day.isoformat(), "visitors": visitors})
    return rows


def main() -> None:
    records = make_visits(seed=30)
    df = pd.DataFrame(records)
    df["day"] = pd.to_datetime(df["day"])
    df = df.sort_values(["branch", "day"]).reset_index(drop=True)
    print(f"{len(df)} rows for {df['branch'].nunique()} branches, missing days per branch:",
          (DAYS - df.groupby("branch").size()).to_dict())

    by_branch: dict[str, list[dict]] = {}
    for r in sorted(records, key=lambda r: (r["branch"], r["day"])):
        by_branch.setdefault(r["branch"], []).append(r)
    py_rows = [r for b in sorted(by_branch) for r in by_branch[b]]  # same order as df

    # 1. 7-calendar-day average vs. a 7-row window
    g = df.set_index("day").groupby("branch")["visitors"]
    df["avg_7d"] = g.rolling("7D").mean().reset_index(level=0, drop=True).to_numpy()
    df["avg_7rows"] = g.rolling(7, min_periods=1).mean().reset_index(level=0, drop=True).to_numpy()
    differ = df[(df["avg_7d"] - df["avg_7rows"]).abs() > 1e-9]
    print(f"\n1. rows where 7 days != 7 rows (a gap inside the window): {len(differ)}")
    print(differ[["branch", "day", "avg_7d", "avg_7rows"]].head(4).round({"avg_7d": 1, "avg_7rows": 1}).to_string(index=False))
    for r, a7d, a7r in zip(py_rows, df["avg_7d"], df["avg_7rows"]):
        same = by_branch[r["branch"]]
        d = date.fromisoformat(r["day"])
        window = [x["visitors"] for x in same if d - timedelta(days=6) <= date.fromisoformat(x["day"]) <= d]
        assert math.isclose(a7d, sum(window) / len(window))
        pos = same.index(r)
        last7 = [x["visitors"] for x in same[max(0, pos - 6): pos + 1]]
        assert math.isclose(a7r, sum(last7) / len(last7))

    # 2. Running total and best day so far per branch
    gv = df.groupby("branch")["visitors"]
    df["running_total"] = gv.expanding().sum().reset_index(level=0, drop=True).astype(int)
    df["best_so_far"] = gv.expanding().max().reset_index(level=0, drop=True).astype(int)
    totals = df.groupby("branch")[["running_total", "best_so_far"]].last()
    print("\n2. final running total and best day per branch:")
    print(totals.to_string())
    for b, rows in by_branch.items():
        total, best = 0, 0
        sub = df[df["branch"] == b]
        for r, rt, bs in zip(rows, sub["running_total"], sub["best_so_far"]):
            total += r["visitors"]
            best = max(best, r["visitors"])
            assert (rt, bs) == (total, best)

    # 3. Change vs. the previous recorded day; a previous 0 gives NaN instead of inf
    prev = gv.shift()
    df["change"] = gv.diff()
    df["pct_change"] = (df["change"] / prev.where(prev != 0) * 100).round(1)
    n_after_zero = int(((prev == 0) & df["change"].notna()).sum())
    print(f"\n3. rows after a closed day (pct_change left empty): {n_after_zero}, "
          f"any inf: {bool(df['pct_change'].isin([float('inf'), float('-inf')]).any())}")
    for r, ch, pc in zip(py_rows, df["change"], df["pct_change"]):
        rows = by_branch[r["branch"]]
        pos = rows.index(r)
        if pos == 0:
            assert math.isnan(ch) and math.isnan(pc)
            continue
        p = rows[pos - 1]["visitors"]
        assert ch == r["visitors"] - p
        assert math.isnan(pc) if p == 0 else pc == round((r["visitors"] - p) / p * 100, 1)

    # 4. Rank days from busiest to quietest per branch; top 3 days each
    df["rank"] = gv.rank(ascending=False, method="min").astype(int)
    top3 = df[df["rank"] <= 3].sort_values(["branch", "rank", "day"])
    print("\n4. top 3 days per branch:")
    print(top3[["branch", "day", "visitors", "rank"]].to_string(index=False))
    for r, rk in zip(py_rows, df["rank"]):
        assert rk == 1 + sum(x["visitors"] > r["visitors"] for x in by_branch[r["branch"]])
    print("\n5. all checks against plain Python passed")


if __name__ == "__main__":
    main()
