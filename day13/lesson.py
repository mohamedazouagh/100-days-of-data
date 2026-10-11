import json
import tempfile
from pathlib import Path

if __name__ == "__main__":
    # 1. Paths are objects: join with /, take apart with attributes
    p = Path("exports") / "2026" / "sales_2026-10-01.csv"
    print(p.as_posix())
    print("name:", p.name, "| stem:", p.stem, "| suffix:", p.suffix, "| parent:", p.parent.as_posix())
    print("as json:", p.with_suffix(".json").name)

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)

        # 2. mkdir(parents=True, exist_ok=True) is safe to run twice
        (root / "exports" / "2026" / "10").mkdir(parents=True, exist_ok=True)
        (root / "exports" / "2026" / "10").mkdir(parents=True, exist_ok=True)

        # 3. write_text / read_text with an explicit encoding
        (root / "exports" / "a.csv").write_text("city,temp\nBreda,14.1\n", encoding="utf-8")
        (root / "exports" / "2026" / "10" / "b.csv").write_text("city,temp\nGent,15.0\n", encoding="utf-8")
        (root / "exports" / "notes.txt").write_text("not data", encoding="utf-8")
        (root / "exports" / "meta.json").write_text(json.dumps({"rows": 2}), encoding="utf-8")

        exports = root / "exports"
        # 4. glob looks in one folder, rglob in all subfolders; sort for a stable order
        print("glob :", [f.name for f in sorted(exports.glob("*.csv"))])
        print("rglob:", [f.relative_to(exports).as_posix() for f in sorted(exports.rglob("*.csv"))])

        # 5. Check before using, and read file sizes
        for f in sorted(exports.iterdir()):
            kind = "dir " if f.is_dir() else "file"
            size = f.stat().st_size if f.is_file() else "-"
            print(f"{kind} {f.name:<10} {size}")
        print("missing exists?", (exports / "missing.csv").exists())

        # 6. Reading every CSV into one list of lines (header kept once)
        lines = []
        for f in sorted(exports.rglob("*.csv")):
            header, *rows = f.read_text(encoding="utf-8").splitlines()
            lines = lines or [header]
            lines += rows
        print(lines)
        print("meta:", json.loads((exports / "meta.json").read_text(encoding="utf-8")))
