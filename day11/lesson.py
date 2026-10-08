from datetime import date

# Fictional sensor readings as they might come out of a CSV export
READINGS = [
    {"sensor": "s1", "day": "2026-10-01", "value": "21.5"},
    {"sensor": "s2", "day": "2026-10-01", "value": ""},
    {"sensor": "s1", "day": "2026-10-32", "value": "20.1"},
    {"sensor": "s3", "day": "2026-10-02", "value": "abc"},
    {"sensor": "s2", "day": "2026-10-02", "value": "-80"},
    {"day": "2026-10-03", "value": "19.0"},
]


def parse(row):
    """Return a clean reading or raise ValueError explaining what is wrong."""
    try:
        sensor, day, value = row["sensor"], row["day"], row["value"]
    except KeyError as exc:
        raise ValueError(f"missing field {exc}") from None
    value = float(value)                   # ValueError for "" and "abc"
    day = date.fromisoformat(day)          # ValueError for 2026-10-32
    if not -50 <= value <= 60:
        raise ValueError(f"value out of range: {value}")
    return {"sensor": sensor, "day": day, "value": value}


if __name__ == "__main__":
    # 1. Built-in conversions raise ValueError on bad input
    for text in ["42", "", "4.2.1"]:
        try:
            print(repr(text), "->", int(text))
        except ValueError as exc:
            print(repr(text), "->", type(exc).__name__, exc)

    # 2. Keep good rows, collect bad ones with the reason and line number
    good, rejected = [], []
    for line, row in enumerate(READINGS, start=1):
        try:
            clean = parse(row)
        except ValueError as exc:
            rejected.append((line, str(exc)))
        else:                               # only runs when parse() succeeded
            good.append(clean)
    print(len(good), "good:", [(r["sensor"], r["value"]) for r in good])
    for line, reason in rejected:
        print(f"  line {line}: {reason}")

    # 3. finally always runs - handy for closing files or logging a summary
    try:
        ratio = len(rejected) / len(READINGS)
    finally:
        print("checked", len(READINGS), "rows")
    print(f"reject rate {ratio:.0%}")
