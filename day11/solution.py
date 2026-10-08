from collections import Counter
from datetime import date

# Fictional order lines, all values still strings as read from a CSV
RAW = [
    {"id": "A1", "date": "2026-10-01", "qty": "3", "price": "4.50"},
    {"id": "A2", "date": "2026-10-01", "qty": "two", "price": "3.00"},
    {"id": "A3", "date": "2026-02-30", "qty": "1", "price": "12.00"},
    {"id": "A4", "date": "2026-10-02", "qty": "0", "price": "7.25"},
    {"id": "A5", "date": "2026-10-02", "qty": "5", "price": "2.20"},
    {"id": "A6", "date": "2026-10-03", "qty": "2"},
    {"id": "A7", "date": "2026-10-03", "qty": "1", "price": "-1.00"},
    {"id": "A8", "date": "2026-10-04", "qty": "10", "price": "0.99"},
    {"id": "A9", "date": "2026-10-04", "qty": " 4 ", "price": "1.25"},
    {"id": "B1", "date": "2026-10-05", "qty": "1", "price": "30"},
    {"id": "B2", "date": "2026-10-05", "qty": "2", "price": "1.50"},
    {"id": "B3", "date": "2026-10-06", "qty": "1", "price": "8"},
    {"id": "B4", "date": "2026-10-06", "qty": "3", "price": "0.50"},
]

MAX_REJECT_SHARE = 0.4


def parse_order(row):
    """Clean order dict, or ValueError whose message starts with a category."""
    missing = [f for f in ("id", "date", "qty", "price") if not row.get(f, "").strip()]
    if missing:
        raise ValueError(f"missing field: {', '.join(missing)}")
    try:
        qty, price = int(row["qty"]), float(row["price"])
    except ValueError:
        raise ValueError(f"bad number: qty={row['qty']!r} price={row['price']!r}") from None
    try:
        day = date.fromisoformat(row["date"])
    except ValueError:
        raise ValueError(f"bad date: {row['date']}") from None
    if qty <= 0:
        raise ValueError(f"bad quantity: must be positive, got {qty}")
    if price < 0:
        raise ValueError(f"bad price: must not be negative, got {price}")
    return {"id": row["id"].strip(), "date": day, "qty": qty, "price": price}


def split_rows(rows):
    good, rejected = [], []
    for line, row in enumerate(rows, start=1):
        try:
            order = parse_order(row)
        except ValueError as exc:
            rejected.append((line, str(exc)))
        else:
            good.append(order)
    return good, rejected


def revenue(orders):
    return round(sum(o["qty"] * o["price"] for o in orders), 2)


def reject_summary(rejected, total, max_share=MAX_REJECT_SHARE):
    """Counts per category; raises if too large a share of the rows was bad."""
    share = len(rejected) / total if total else 0.0
    if share > max_share:
        raise RuntimeError(f"{share:.0%} of rows rejected (limit {max_share:.0%})")
    return Counter(reason.split(":")[0] for _, reason in rejected)


if __name__ == "__main__":
    good, rejected = split_rows(RAW)
    print("good:", [o["id"] for o in good])
    for line, reason in rejected:
        print(f"  line {line}: {reason}")
    total = revenue(good)
    summary = reject_summary(rejected, len(RAW))
    print("revenue:", total)
    print("rejects:", dict(summary))

    assert [o["id"] for o in good] == ["A1", "A5", "A8", "A9", "B1", "B2", "B3", "B4"]
    assert rejected == [
        (2, "bad number: qty='two' price='3.00'"),
        (3, "bad date: 2026-02-30"),
        (4, "bad quantity: must be positive, got 0"),
        (6, "missing field: price"),
        (7, "bad price: must not be negative, got -1.0"),
    ]
    assert total == 81.9  # 13.50 + 11.00 + 9.90 + 5.00 + 30.00 + 3.00 + 8.00 + 1.50
    assert summary == {"bad number": 1, "bad date": 1, "bad quantity": 1,
                       "missing field": 1, "bad price": 1}
    try:
        reject_summary(rejected, len(RAW), max_share=0.3)
    except RuntimeError as exc:
        print("threshold check:", exc)
    else:
        raise AssertionError("expected the 30% limit to trip")
    print("all checks passed")
