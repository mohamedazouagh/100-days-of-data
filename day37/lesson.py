import pandas as pd

# Two fictional streams that never share exact timestamps: shop orders, and the
# EUR->USD rate published at irregular moments. Each order should be converted with
# the latest rate known *at the moment of the order*.
orders = pd.DataFrame({
    "time": pd.to_datetime(["2026-11-02 09:05", "2026-11-02 09:40", "2026-11-02 11:15",
                            "2026-11-02 14:02", "2026-11-02 08:30"]),
    "order": ["o1", "o2", "o3", "o4", "o0"],
    "eur": [120.0, 35.5, 80.0, 15.0, 60.0],
})
rates = pd.DataFrame({
    "time": pd.to_datetime(["2026-11-02 09:00", "2026-11-02 09:30", "2026-11-02 11:00",
                            "2026-11-02 11:20"]),
    "usd_per_eur": [1.120, 1.125, 1.118, 1.121],
})

# 1. An exact merge finds nothing: no timestamp appears in both tables.
exact = orders.merge(rates, on="time", how="left")
print("exact matches:", exact["usd_per_eur"].notna().sum(), "of", len(exact), "\n")

# 2. merge_asof needs both sides sorted by the key. The default direction="backward"
#    takes the last rate at or before each order: no peeking into the future.
orders = orders.sort_values("time")
asof = pd.merge_asof(orders, rates, on="time")
asof["usd"] = (asof["eur"] * asof["usd_per_eur"]).round(2)
print(asof.to_string(index=False), "\n")
# o0 at 08:30 comes before the first rate, so it gets NaN instead of a made-up value.

# 3. tolerance: refuse matches that are too old. o4 at 14:02 would otherwise use the
#    11:20 rate, almost three hours stale.
fresh = pd.merge_asof(orders, rates, on="time", tolerance=pd.Timedelta("1h"))
print("with 1h tolerance:", fresh.set_index("order")["usd_per_eur"].to_dict(), "\n")

# 4. direction="forward" takes the next row instead, "nearest" the closest either way.
#    Handy for matching events to the next check-in, but not for prices: it leaks the future.
for direction in ["forward", "nearest"]:
    m = pd.merge_asof(orders, rates, on="time", direction=direction)
    print(f"{direction:8}", m.set_index("order")["usd_per_eur"].to_dict())
print()

# 5. by= matches within groups: each reading takes the last calibration of *its own* sensor.
readings = pd.DataFrame({
    "time": pd.to_datetime(["2026-11-02 10:00", "2026-11-02 10:00", "2026-11-02 12:00",
                            "2026-11-02 12:00"]),
    "sensor": ["a", "b", "a", "b"],
    "raw": [20.0, 19.0, 21.0, 18.5],
})
calibrations = pd.DataFrame({
    "time": pd.to_datetime(["2026-11-02 09:00", "2026-11-02 09:30", "2026-11-02 11:00"]),
    "sensor": ["a", "b", "a"],
    "offset": [0.5, -0.2, 0.3],
})
cal = pd.merge_asof(readings, calibrations, on="time", by="sensor")
cal["corrected"] = cal["raw"] + cal["offset"]
print(cal.to_string(index=False), "\n")

# 6. An unsorted key raises instead of silently matching wrong rows.
try:
    pd.merge_asof(orders.sort_values("eur"), rates, on="time")
except ValueError as exc:
    print("unsorted:", exc)
