import csv
import io
from dataclasses import asdict, dataclass
from datetime import date

# Fictional stock movements, all values still strings as read from a CSV
ROWS = [
    {"sku": "P-100", "warehouse": "AMS", "date": "2026-10-01", "change": "+20"},
    {"sku": "P-100", "warehouse": "RTM", "date": "2026-10-01", "change": "5"},
    {"sku": "P-200", "warehouse": "AMS", "date": "2026-10-02", "change": "8"},
    {"sku": "P-100", "warehouse": "AMS", "date": "2026-10-03", "change": "-12"},
    {"sku": "P-100", "warehouse": "RTM", "date": "2026-10-02", "change": "-7"},
    {"sku": "P-200", "warehouse": "AMS", "date": "2026-10-01", "change": "-3"},
    {"sku": "P-100", "warehouse": "RTM", "date": "2026-10-04", "change": "10"},
    {"sku": "P-100", "warehouse": "AMS", "date": "2026-10-05", "change": "-8"},
]


@dataclass(frozen=True, order=True)
class Movement:
    sku: str
    warehouse: str
    day: date
    change: int

    def __post_init__(self):
        if self.change == 0:
            raise ValueError(f"zero change for {self.sku}/{self.warehouse} on {self.day}")

    @classmethod
    def from_row(cls, row):
        return cls(
            sku=row["sku"].strip(),
            warehouse=row["warehouse"].strip().upper(),
            day=date.fromisoformat(row["date"]),
            change=int(row["change"]),
        )


def stock_levels(movements):
    """Closing stock per (sku, warehouse) and the pairs that dipped below zero.

    Movements are replayed in sorted order, i.e. per pair in date order.
    """
    closing, went_negative = {}, []
    for m in sorted(movements):
        key = (m.sku, m.warehouse)
        closing[key] = closing.get(key, 0) + m.change
        if closing[key] < 0 and key not in went_negative:
            went_negative.append(key)
    return closing, went_negative


def to_csv(movements):
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=["sku", "warehouse", "day", "change"], lineterminator="\n")
    writer.writeheader()
    for m in sorted(movements):
        writer.writerow(asdict(m))  # date objects are written as YYYY-MM-DD
    return buf.getvalue()


if __name__ == "__main__":
    moves = [Movement.from_row(r) for r in ROWS]
    ordered = sorted(moves)
    for m in ordered:
        print(f"{m.sku} {m.warehouse} {m.day} {m.change:+d}")
    closing, negative = stock_levels(moves)
    print("closing:", closing)
    print("went negative:", negative)
    text = to_csv(moves)
    print(text, end="")

    assert [(m.sku, m.warehouse, m.day.day) for m in ordered] == [
        ("P-100", "AMS", 1), ("P-100", "AMS", 3), ("P-100", "AMS", 5),
        ("P-100", "RTM", 1), ("P-100", "RTM", 2), ("P-100", "RTM", 4),
        ("P-200", "AMS", 1), ("P-200", "AMS", 2),
    ]
    assert closing == {("P-100", "AMS"): 0, ("P-100", "RTM"): 8, ("P-200", "AMS"): 5}
    # RTM: 5 - 7 = -2 on 10-02; P-200: -3 on 10-01 before the +8 arrives
    assert negative == [("P-100", "RTM"), ("P-200", "AMS")]
    assert text.splitlines()[:2] == ["sku,warehouse,day,change", "P-100,AMS,2026-10-01,20"]
    assert len(text.splitlines()) == len(ROWS) + 1
    try:
        Movement.from_row({"sku": "P-300", "warehouse": "ams", "date": "2026-10-06", "change": "0"})
    except ValueError as exc:
        print("rejected:", exc)
    else:
        raise AssertionError("expected a zero change to be rejected")
    try:
        moves[0].change = 99
    except AttributeError:
        pass
    else:
        raise AssertionError("Movement should be frozen")
    print("all checks passed")
