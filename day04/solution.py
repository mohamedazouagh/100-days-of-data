import csv
import io

RAW = """date,city,temp_c
2026-09-27,Breda,22.1
2026-09-28,"Den Bosch, NL",21.8
2026-09-28,Tilburg,
2026-09-29,Breda,26.2
"""


def clean(raw: str) -> str:
    """Drop rows without a temperature, add temp_f, return CSV text."""
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=["date", "city", "temp_c", "temp_f"], lineterminator="\n")
    writer.writeheader()
    for row in csv.DictReader(io.StringIO(raw)):
        if not row["temp_c"].strip():
            continue
        temp_c = float(row["temp_c"])
        writer.writerow({**row, "temp_c": temp_c, "temp_f": round(temp_c * 9 / 5 + 32, 1)})
    return out.getvalue()


if __name__ == "__main__":
    result = clean(RAW)
    print(result)

    rows = list(csv.DictReader(io.StringIO(result)))
    assert len(rows) == 3
    assert "Tilburg" not in {r["city"] for r in rows}
    assert rows[1] == {"date": "2026-09-28", "city": "Den Bosch, NL", "temp_c": "21.8", "temp_f": "71.2"}
    assert '"Den Bosch, NL"' in result
