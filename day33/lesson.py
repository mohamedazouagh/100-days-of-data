import pandas as pd

# A small fictional table: monthly visitors per museum and city
visits = pd.DataFrame({
    "city": ["Breda", "Breda", "Breda", "Breda", "Delft", "Delft", "Delft", "Delft"],
    "museum": ["Stedelijk", "Stedelijk", "Kasteel", "Kasteel", "Prinsenhof", "Prinsenhof", "Vermeer", "Vermeer"],
    "month": ["2026-09", "2026-10", "2026-09", "2026-10", "2026-09", "2026-10", "2026-09", "2026-10"],
    "visitors": [1200, 1350, 800, 760, 2100, 2300, 1500, 1650],
})

# 1. set_index moves columns into the row labels. With several columns you get a
#    MultiIndex: every row is labelled by a tuple (city, museum, month).
v = visits.set_index(["city", "museum", "month"]).sort_index()
print(v)
print("levels:", v.index.names, "| first label:", v.index[0])
print()

# 2. loc with a partial key selects the outer level(s) and drops them from the result.
print(v.loc["Delft"])
print(v.loc[("Breda", "Kasteel")])
print("one cell:", v.loc[("Delft", "Vermeer", "2026-10"), "visitors"])
print()

# 3. xs ("cross-section") selects on an inner level without naming the outer ones.
print(v.xs("2026-10", level="month"))
print()

# 4. pd.IndexSlice slices several levels at once; the index must be sorted for slices.
idx = pd.IndexSlice
print(v.loc[idx[:, ["Kasteel", "Vermeer"], "2026-09"], :])
print()

# 5. unstack turns an index level into columns (wide view); stack is the reverse.
wide = v["visitors"].unstack("month")
print(wide)
print("growth Sep -> Oct (%):")
print(((wide["2026-10"] / wide["2026-09"] - 1) * 100).round(1))
print()

# 6. Group by index levels with level=, no reset_index needed.
print(v.groupby(level="city")["visitors"].sum())
print()

# 7. Arithmetic aligns on the index, not on position. A target table with a different
#    row order still lines up, and labels missing on one side become NaN.
target = pd.Series(
    {("Delft", "Vermeer"): 1600, ("Breda", "Kasteel"): 800, ("Breda", "Stedelijk"): 1300},
    name="target",
)
target.index.names = ["city", "museum"]
october = v.xs("2026-10", level="month")["visitors"]
print((october - target).rename("vs_target"))
print()

# 8. reset_index brings the levels back as ordinary columns (handy before saving to CSV).
print(v.reset_index().head(3).to_string(index=False))
