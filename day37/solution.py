import bisect
import random
from datetime import datetime, timedelta

import pandas as pd

VANS = ["van1", "van2", "van3"]
START = datetime(2026, 11, 2, 8, 0)
TOLERANCE = timedelta(minutes=10)


def make_log(seed: int) -> tuple[list[dict], list[dict]]:
    """Fictional parcel scans and GPS fixes per van, at irregular minutes."""
    rng = random.Random(seed)
    scans, fixes = [], []
    for van in VANS:
        t = START
        while t < START + timedelta(hours=4):
            t += timedelta(minutes=rng.choice([1, 2, 3, 4, 6, 15, 25]))
            fixes.append({"time": t, "van": van, "zone": f"z{rng.randint(1, 9)}"})
        for i in range(12):
            minute = rng.randint(-5, 245)  # a few scans happen before the first fix
            scans.append({"time": START + timedelta(minutes=minute), "van": van,
                          "parcel": f"{van}-p{i:02d}"})
    return scans, fixes


scans_rec, fixes_rec = make_log(37)
scans = pd.DataFrame(scans_rec).sort_values("time", kind="stable").reset_index(drop=True)
fixes = (pd.DataFrame(fixes_rec).rename(columns={"time": "fix_time"})
         .sort_values("fix_time", kind="stable").reset_index(drop=True))
fixes["time"] = fixes["fix_time"]  # keep the fix time visible after the join

# 1. latest fix of the same van at or before each scan
matched = pd.merge_asof(scans, fixes, on="time", by="van")
print(matched.head(6).to_string(index=False), "\n")

# 2. with a 10-minute tolerance: which scans have no fresh fix?
fresh = pd.merge_asof(scans, fixes, on="time", by="van", tolerance=pd.Timedelta(TOLERANCE))
stale = fresh[fresh["zone"].isna()]
print("scans without a fix in the last 10 min:")
for van, parcels in stale.groupby("van")["parcel"]:
    print(f"  {van}: {', '.join(parcels)}")
print()

# 3. age of the fix used for each scan, and the median per van
matched["age_min"] = (matched["time"] - matched["fix_time"]).dt.total_seconds() / 60
print("median fix age (min):", matched.groupby("van")["age_min"].median().to_dict(), "\n")

# 4. nearest would sometimes use a fix from after the scan
nearest = pd.merge_asof(scans, fixes, on="time", by="van", direction="nearest")
future = nearest["fix_time"] > nearest["time"]
print(f"nearest picks a later fix for {future.sum()} of {len(scans)} scans\n")

# 5. check against plain Python: bisect on each van's sorted fix times
by_van: dict[str, list[dict]] = {}
for f in sorted(fixes_rec, key=lambda f: f["time"]):
    by_van.setdefault(f["van"], []).append(f)
times = {van: [f["time"] for f in rows] for van, rows in by_van.items()}

checked = 0
for row in matched.itertuples(index=False):
    i = bisect.bisect_right(times[row.van], row.time.to_pydatetime()) - 1
    if i < 0:
        assert pd.isna(row.zone)
        expected_age = None
    else:
        fix = by_van[row.van][i]
        assert row.zone == fix["zone"] and row.fix_time == fix["time"]
        expected_age = (row.time.to_pydatetime() - fix["time"]).total_seconds() / 60
        assert row.age_min == expected_age
    stale_py = expected_age is None or expected_age > TOLERANCE.total_seconds() / 60
    assert stale_py == (row.parcel in set(stale["parcel"]))
    checked += 1

future_py = 0
for s in scans_rec:
    ts = times[s["van"]]
    i = bisect.bisect_right(ts, s["time"])
    before = s["time"] - ts[i - 1] if i > 0 else None
    after = ts[i] - s["time"] if i < len(ts) else None
    if after is not None and (before is None or after < before):
        future_py += 1
assert future_py == future.sum()
print(f"all {checked} matches, {len(stale)} stale scans and {future_py} future picks agree "
      "with the bisect version")
