import pandas as pd

# The same small table as in Phase 1, but as a DataFrame instead of a list of dicts
ROWS = [
    {"city": "Breda", "date": "2026-10-01", "temp_c": 14.2, "rain_mm": 0.0},
    {"city": "Breda", "date": "2026-10-02", "temp_c": 15.8, "rain_mm": 2.4},
    {"city": "Utrecht", "date": "2026-10-01", "temp_c": 13.9, "rain_mm": 1.1},
    {"city": "Utrecht", "date": "2026-10-02", "temp_c": None, "rain_mm": 0.0},
]

# 1. A Series is one labelled column: values + an index
temps = pd.Series([14.2, 15.8, 13.9], index=["mon", "tue", "wed"], name="temp_c")
print(temps)
print("mean:", round(temps.mean(), 2), "| by label:", temps["tue"], "| by position:", temps.iloc[0])
print()

# 2. A DataFrame is a dict of Series sharing one index. Build it from records or from columns.
df = pd.DataFrame(ROWS)
same = pd.DataFrame({k: [r[k] for r in ROWS] for k in ROWS[0]})
print("from records == from columns:", df.equals(same))
print()

# 3. Inspect before doing anything else: size, column types, missing values, a peek
print("shape:", df.shape)
print(df.dtypes.to_string())
print("missing per column:", df.isna().sum().to_dict())
print(df.head(2))
print()

# 4. Fix types explicitly: text dates are just strings until converted
df["date"] = pd.to_datetime(df["date"])
print("date dtype after to_datetime:", df["date"].dtype)
print()

# 5. Selecting: one column -> Series, a list of columns -> DataFrame
print(type(df["temp_c"]).__name__, type(df[["city", "temp_c"]]).__name__)

# 6. Vectorised maths: no loop, and missing values are skipped by aggregations
print("temps in F:", (df["temp_c"] * 9 / 5 + 32).round(1).tolist())
print("mean temp (NaN skipped):", round(df["temp_c"].mean(), 2), "| count:", df["temp_c"].count())

# 7. New columns are computed for every row at once
df["wet"] = df["rain_mm"] > 0
print(df[["city", "date", "rain_mm", "wet"]].to_string(index=False))

# 8. describe() gives count/mean/std/min/quartiles/max for numeric columns in one call
print(df.describe().round(2))
