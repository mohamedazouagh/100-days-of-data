import pandas as pd

# A small fictional log of daily webshop orders, as it might come out of a CSV:
# dates are text, one day (2026-10-04) is missing entirely
raw = pd.DataFrame({
    "day": ["2026-09-28", "2026-09-29", "2026-09-30", "2026-10-01", "2026-10-02",
            "2026-10-03", "2026-10-05", "2026-10-06", "2026-10-07"],
    "orders": [12, 15, 9, 20, 18, 25, 11, 14, 16],
})
print(raw.dtypes.to_dict())
print()

# 1. to_datetime: text -> datetime64. Give the format so nothing is guessed
raw["day"] = pd.to_datetime(raw["day"], format="%Y-%m-%d")
print(raw.dtypes.to_dict())
print()

# 2. The .dt accessor pulls calendar parts out of a datetime column
parts = raw.assign(
    weekday=raw["day"].dt.day_name(),
    month=raw["day"].dt.month,
    iso_week=raw["day"].dt.isocalendar().week,
)
print(parts.head(4))
print()

# 3. A DatetimeIndex makes date slicing work with plain strings
ts = raw.set_index("day")["orders"]
print(ts.loc["2026-10"])          # all of October
print(ts.loc["2026-09-30":"2026-10-02"].sum())  # both ends included
print()

# 4. asfreq("D") puts every calendar day in the index, so gaps become visible NaN
daily = ts.asfreq("D")
print(daily[daily.isna()])
print()

# 5. resample: group by time buckets. "W-SUN" = weeks ending on Sunday, "MS" = month start
print(ts.resample("W-SUN").sum())
print(ts.resample("MS").agg(["sum", "count"]))
print()

# 6. shift / diff / pct_change compare each row with the previous row (not the previous DAY)
change = pd.DataFrame({
    "orders": ts,
    "prev": ts.shift(1),
    "diff": ts.diff(),
    "pct": ts.pct_change().round(3),
})
print(change.head(8))
print()

# 7. On the gap-filled daily series the "previous row" is yesterday, so 2026-10-05 gets NaN
print(daily.diff().loc["2026-10-03":"2026-10-06"])
