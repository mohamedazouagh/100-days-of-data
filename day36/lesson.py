import pandas as pd

# A fictional sensor export where every column arrived as text, the usual result of
# read_csv on a file with a few bad cells or of building a frame from JSON strings.
raw = pd.DataFrame({
    "sensor": ["s1", "s2", "s1", "s3", "s2", "s1", "s3", "s2"],
    "reading": ["21.5", "19.0", "n/a", "22.1", "18,7", "21.9", "", "19.4"],
    "count": ["3", "4", "2", "", "5", "3", "4", "?"],
    "ok": ["yes", "no", "yes", "yes", None, "no", "yes", "yes"],
})
print(raw.dtypes.to_string(), "\n")  # all text: nothing numeric works yet

# 1. astype is strict: one bad cell makes the whole conversion fail.
try:
    raw["reading"].astype(float)
except ValueError as exc:
    print("astype(float) failed:", exc, "\n")

# 2. to_numeric(errors="coerce") turns every unparsable cell into NaN, so count them
#    before and after to see exactly what was lost. Fix known formats (decimal comma) first.
fixed = raw["reading"].str.replace(",", ".", regex=False)
reading = pd.to_numeric(fixed, errors="coerce")
lost = raw.loc[reading.isna(), "reading"].tolist()
print("reading:", reading.tolist(), "-> unparsable:", lost, "\n")

# 3. A float column can't hold "missing" ints without turning 3 into 3.0.
#    The nullable Int64 dtype (capital I) keeps integers and uses <NA> for gaps.
count_float = pd.to_numeric(raw["count"], errors="coerce")
count_int = count_float.astype("Int64")
print("float64:", count_float.tolist())
print("Int64:  ", count_int.tolist(), "sum =", count_int.sum(), "\n")

# 4. Map text flags to the nullable boolean dtype; unknown values become <NA>, not False.
ok = raw["ok"].map({"yes": True, "no": False}).astype("boolean")
print("ok:", ok.tolist(), "-> true share of known:", round(ok.mean(), 3), "\n")

# 5. Repeated labels are cheap as category, and numbers can be downcast to smaller types.
clean = pd.DataFrame({
    "sensor": raw["sensor"].astype("category"),
    "reading": pd.to_numeric(reading, downcast="float"),
    "count": count_int,
    "ok": ok,
})
print(clean.dtypes.to_string(), "\n")

# 6. memory_usage(deep=True) counts the real size of the strings; without deep=True
#    object columns only count their 8-byte pointers. Compare on a bigger frame.
big_raw = pd.concat([raw] * 10_000, ignore_index=True)
big_clean = pd.concat([clean] * 10_000, ignore_index=True)
before = big_raw.memory_usage(deep=True).sum()
after = big_clean.memory_usage(deep=True).sum()
print(f"{len(big_raw):,} rows: {before / 1e6:.1f} MB as text -> {after / 1e6:.1f} MB typed "
      f"({after / before:.0%})")
