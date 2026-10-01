import csv
import io

RAW = """date,city,temp,rain_mm
2026-09-27,Breda,22.1,0.0
2026-09-28,Breda,21.4,1.9
2026-09-28,"Den Bosch, NL",21.8,
2026-09-29,Breda,26.2,0.1
"""


def to_float(value: str) -> float | None:
    """Empty string -> None, anything else -> float."""
    return float(value) if value.strip() else None


if __name__ == "__main__":
    # 1. Naive splitting breaks on the quoted comma
    third_line = RAW.splitlines()[3]
    print(third_line.split(","))

    # 2. DictReader handles quotes and gives dicts keyed by the header
    rows = list(csv.DictReader(io.StringIO(RAW)))
    print(rows[2])

    # 3. Everything is a string - convert explicitly
    typed = [
        {"date": r["date"], "city": r["city"], "temp": to_float(r["temp"]), "rain_mm": to_float(r["rain_mm"])}
        for r in rows
    ]
    print(typed[2])

    # 4. Write back out; DictWriter quotes fields that need it
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=["date", "city", "temp"], extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(typed)
    print(out.getvalue())

    # With a real file, always use newline="" and an encoding:
    # with open("clean.csv", "w", newline="", encoding="utf-8") as f: ...
