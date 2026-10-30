import pandas as pd

# A small fictional shop: units sold per day for two products
sales = pd.DataFrame({
    "day": pd.date_range("2026-03-02", periods=8, freq="D").repeat(2),
    "product": ["tea", "mug"] * 8,
    "units": [5, 2, 7, 1, 6, 0, 9, 3, 4, 2, 8, 6, 12, 1, 3, 4],
})
tea = sales[sales["product"] == "tea"].set_index("day")["units"]
print(tea.tolist())
print()

# 1. rolling(n): a window of the last n rows. The first n-1 results are NaN because the
#    window is not full yet; min_periods=1 fills them from the rows that are there.
print(tea.rolling(3).mean().round(2).tolist())
print(tea.rolling(3, min_periods=1).mean().round(2).tolist())
print()

# 2. center=True puts the window around each row instead of behind it (smoothing a
#    chart, not a forecast: it looks one row into the future)
print(tea.rolling(3, center=True).mean().round(2).tolist())
print()

# 3. With a DatetimeIndex, a window can be a time span: "3D" = this day and the two
#    before it, whatever the number of rows. Missing days are then handled correctly.
gappy = tea.drop(tea.index[[2, 3]])          # two days without data
print(gappy.rolling(3).sum().tolist())        # last 3 rows, spans 5 calendar days
print(gappy.rolling("3D").sum().tolist())     # last 3 calendar days
print()

# 4. expanding(): everything from the first row up to now (running total, best so far)
print(tea.expanding().sum().tolist())
print(tea.expanding().max().tolist())
print()

# 5. Per group: groupby(...).rolling(...) keeps products apart. The result has the group
#    key as an extra index level, so drop it before putting the values back.
sales["avg3"] = (
    sales.groupby("product")["units"].rolling(3, min_periods=1).mean()
    .reset_index(level=0, drop=True).round(2)
)
print(sales[sales["product"] == "mug"]["avg3"].tolist())
print()

# 6. pct_change and diff compare a row with the previous one; rank orders rows
print(tea.diff().tolist())
print((tea.pct_change() * 100).round(1).tolist())
print(tea.rank(ascending=False, method="min").astype(int).tolist())   # 1 = best day
