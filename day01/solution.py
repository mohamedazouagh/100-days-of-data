from lesson import sales

revenue: dict[str, float] = {}
for row in sales:
    revenue[row["city"]] = revenue.get(row["city"], 0) + row["price"] * row["qty"]

for city, amount in sorted(revenue.items(), key=lambda kv: kv[1], reverse=True):
    print(f"{city:<10} €{amount:>7.2f}")
