import math

sales = [
    {"city": "Breda", "product": "hoodie", "price": 59.0, "qty": 2},
    {"city": "Eindhoven", "product": "tee", "price": 29.0, "qty": 5},
    {"city": "Breda", "product": "tee", "price": 29.0, "qty": 1},
    {"city": "Tilburg", "product": "cap", "price": 24.0, "qty": 3},
]


if __name__ == "__main__":
    print(0.1 + 0.2 == 0.3)               # False
    print(math.isclose(0.1 + 0.2, 0.3))   # True

    total_units = sum(row["qty"] for row in sales)
    biggest = max(sales, key=lambda row: row["price"] * row["qty"])
    print(f"{total_units=}")
    print(f"biggest order: {biggest['city']} {biggest['product']}")
