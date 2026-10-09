from dataclasses import asdict, dataclass, field, replace
from datetime import date


@dataclass(frozen=True, order=True)
class Reading:
    """One fictional sensor reading; fields compare in this order."""
    sensor: str
    day: date
    value: float
    unit: str = "C"

    def __post_init__(self):
        if not -50 <= self.value <= 60:
            raise ValueError(f"value out of range: {self.value}")

    @property
    def fahrenheit(self):
        return round(self.value * 9 / 5 + 32, 1)


@dataclass
class Batch:
    name: str
    readings: list = field(default_factory=list)  # never use a bare [] default

    def add(self, reading):
        self.readings.append(reading)


if __name__ == "__main__":
    # 1. Generated __init__, __repr__ and __eq__
    a = Reading("s2", date(2026, 10, 2), 19.5)
    b = Reading("s1", date(2026, 10, 3), 21.0)
    print(a)
    print("equal copies:", a == Reading("s2", date(2026, 10, 2), 19.5))

    # 2. order=True: sorted() compares sensor, then day, then value
    print([r.sensor for r in sorted([a, b])])

    # 3. frozen=True: read-only and hashable; replace() makes a changed copy
    try:
        a.value = 30
    except AttributeError as exc:
        print("frozen:", type(exc).__name__)
    print("in a set:", len({a, a, b}))
    print(replace(a, value=20.0))

    # 4. __post_init__ validation and a computed property
    try:
        Reading("s3", date(2026, 10, 2), 99)
    except ValueError as exc:
        print("rejected:", exc)
    print("21.0 C =", b.fahrenheit, "F")

    # 5. Mutable default via default_factory: each batch gets its own list
    x, y = Batch("x"), Batch("y")
    x.add(a)
    print(len(x.readings), len(y.readings))

    # 6. Back to a plain dict for csv/json
    print(asdict(b))
