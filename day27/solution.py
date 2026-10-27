import math
import random
from collections import defaultdict
from datetime import date, timedelta

import pandas as pd

START, END = date(2026, 9, 1), date(2026, 10, 31)


def make_log(seed: int) -> list[dict]:
    """Fictional daily step counts as text-dated records; about 1 in 12 days is missing."""
    rng = random.Random(seed)
    rows = []
    d = START
    while d <= END:
        if rng.random() >= 1 / 12:
            base = 11000 if d.weekday() >= 5 else 7500
            rows.append({"date": d.isoformat(), "steps": max(0, int(rng.gauss(base, 2500)))})
        d += timedelta(days=1)
    return rows


def close(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)


def main() -> None:
    log = make_log(seed=29)  # a seed where the row jump and the real-day jump disagree
    by_day = {date.fromisoformat(r["date"]): r["steps"] for r in log}

    # 1. Parse, index, list the gaps
    df = pd.DataFrame(log)
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
    ts = df.set_index("date")["steps"]
    full = ts.asfreq("D")
    missing = [d.date() for d in full[full.isna()].index]
    print(f"1. {len(ts)} days logged, {len(missing)} missing:", ", ".join(d.isoformat() for d in missing))
    all_days = [START + timedelta(days=i) for i in range((END - START).days + 1)]
    # asfreq only spans first..last logged day, so compare inside that span
    first, last = min(by_day), max(by_day)
    assert missing == [d for d in all_days if first <= d <= last and d not in by_day]

    # 2. Weekly totals / means / day counts (weeks ending Sunday)
    weekly = ts.resample("W-SUN").agg(["sum", "mean", "count"])
    print("\n2. steps per week (label = Sunday):")
    print(weekly.round(0).astype(int))
    py_week = defaultdict(list)
    for d, steps in by_day.items():
        py_week[d + timedelta(days=6 - d.weekday())].append(steps)
    assert [d.date() for d in weekly.index] == sorted(py_week)
    for label, row in weekly.iterrows():
        values = py_week[label.date()]
        assert row["sum"] == sum(values) and row["count"] == len(values)
        assert close(row["mean"], sum(values) / len(values))

    # 3. Monthly totals and busiest weekday on average
    monthly = ts.resample("MS").sum()
    print("\n3. monthly totals:", {d.strftime("%Y-%m"): int(v) for d, v in monthly.items()})
    for d, v in monthly.items():
        assert v == sum(s for day, s in by_day.items() if (day.year, day.month) == (d.year, d.month))
    by_weekday = ts.groupby(ts.index.day_name()).mean()
    busiest = by_weekday.idxmax()
    print(f"   busiest weekday on average: {busiest} ({by_weekday[busiest]:.0f} steps)")
    py_wd = defaultdict(list)
    for d, steps in by_day.items():
        py_wd[d.strftime("%A")].append(steps)
    py_means = {k: sum(v) / len(v) for k, v in py_wd.items()}
    assert busiest == max(py_means, key=py_means.get)
    assert close(by_weekday[busiest], py_means[busiest])

    # 4. Biggest jump: over rows vs. over real consecutive days
    row_jump = ts.diff()
    day_jump = full.diff()
    r_day, r_val = row_jump.idxmax(), row_jump.max()
    d_day, d_val = day_jump.idxmax(), day_jump.max()
    print(f"\n4. biggest jump over rows: +{r_val:.0f} on {r_day.date()}")
    print(f"   biggest jump over real days: +{d_val:.0f} on {d_day.date()}")
    ordered = sorted(by_day)
    py_rows = max((by_day[b] - by_day[a], b) for a, b in zip(ordered, ordered[1:]))
    py_days = max(
        (by_day[d] - by_day[d - timedelta(days=1)], d)
        for d in ordered if d - timedelta(days=1) in by_day
    )
    assert (r_val, r_day.date()) == py_rows and (d_val, d_day.date()) == py_days
    if py_rows != py_days:
        prev = max(d for d in ordered if d < r_day.date())
        print(f"   they differ: the row jump compares {r_day.date()} with {prev}, "
              f"{(r_day.date() - prev).days} days earlier")
    else:
        print("   same answer: the biggest row jump is between real neighbours")
    print("\nAll checks passed.")


if __name__ == "__main__":
    main()
