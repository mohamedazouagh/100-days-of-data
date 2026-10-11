import csv
import io
import re
import tempfile
from collections import defaultdict
from pathlib import Path

SALES_NAME = re.compile(r"sales_(\d{4}-\d{2}-\d{2})\.csv")


def build_inbox(folder: Path) -> None:
    """Create a fictional export folder: daily sales files plus files that do not belong."""
    files = {
        "2026/10/sales_2026-10-02.csv": "order_id,amount\nA-7,12.50\nA-8,30.00\n",
        "2026/10/sales_2026-10-01.csv": "order_id,amount\nA-1,20.00\nA-2,5.25\nA-3,14.75\n",
        "2026/09/sales_2026-09-30.csv": "order_id,amount\nZ-9,99.90\n",
        "late/sales_2026-10-03.csv": "order_id,amount\nB-1,8.00\n",
        "2026/10/sales_2026-10-04.csv": "",  # export failed: empty file
        "2026/10/sales_2026-10-02.csv.bak": "order_id,amount\nOLD,1.00\n",
        "README.txt": "Daily exports land here.\n",
    }
    for rel, text in files.items():
        path = folder / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def find_sales_files(folder: Path) -> list[tuple[str, Path]]:
    """All sales_YYYY-MM-DD.csv files in any subfolder, as (date, path), sorted by date."""
    found = []
    for path in folder.rglob("sales_*.csv"):
        m = SALES_NAME.fullmatch(path.name)  # fullmatch rejects names like *.csv.bak
        if m:
            found.append((m.group(1), path))
    return sorted(found)


def merge(files: list[tuple[str, Path]]) -> tuple[list[dict], list[str]]:
    """Read every non-empty file; return (merged rows with a source column, skipped names)."""
    rows, skipped = [], []
    for _, path in files:
        if path.stat().st_size == 0:
            skipped.append(path.name)
            continue
        with path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                rows.append({**row, "source": path.name})
    return rows, skipped


def write_merged(rows: list[dict], folder: Path) -> Path:
    out = folder / "out" / "merged.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["order_id", "amount", "source"])
        writer.writeheader()
        writer.writerows(rows)
    return out


def totals_per_day(rows: list[dict]) -> dict[str, float]:
    totals: dict[str, float] = defaultdict(float)
    for r in rows:
        totals[SALES_NAME.fullmatch(r["source"]).group(1)] += float(r["amount"])
    return {day: round(total, 2) for day, total in totals.items()}


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        inbox = Path(tmp)
        build_inbox(inbox)

        files = find_sales_files(inbox)
        print("found:", [p.relative_to(inbox).as_posix() for _, p in files])

        rows, skipped = merge(files)
        print("skipped empty:", skipped)
        print("merged rows:", len(rows))

        out = write_merged(rows, inbox)
        print("written:", out.relative_to(inbox).as_posix())
        print(out.read_text(encoding="utf-8").splitlines()[:3])

        for day, total in totals_per_day(rows).items():
            print(f"{day}  {total:>7.2f}")

        # Checks
        assert [d for d, _ in files] == ["2026-09-30", "2026-10-01", "2026-10-02", "2026-10-03", "2026-10-04"]
        assert skipped == ["sales_2026-10-04.csv"]
        assert len(rows) == 7 and all(r["order_id"] != "OLD" for r in rows)
        assert totals_per_day(rows) == {"2026-09-30": 99.9, "2026-10-01": 40.0, "2026-10-02": 42.5, "2026-10-03": 8.0}
        assert len(out.read_text(encoding="utf-8").splitlines()) == 8  # header + 7 rows
        print("all checks passed")
