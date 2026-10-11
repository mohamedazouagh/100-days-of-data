# Day 13 - Files and folders with pathlib

Real data rarely arrives as one file. It is a folder of daily exports, a mix of `.csv` and
`.json`, and a few files that should be skipped. `pathlib.Path` treats paths as objects
instead of strings, so joining, finding, reading and writing files is short and works the same
on Windows, macOS and Linux.

Key points:
- Build paths with `/`: `Path("data") / "2026" / "sales.csv"`, never with string `+` and `"\\"`.
- `.name`, `.stem`, `.suffix` and `.parent` take a path apart; `.with_suffix(".json")` swaps the extension.
- `.glob("*.csv")` finds files in one folder, `.rglob("*.csv")` searches all subfolders too.
- Glob order is not guaranteed: wrap it in `sorted()` when the order matters.
- `.read_text(encoding="utf-8")` / `.write_text(...)` handle small files in one call; pass the encoding explicitly.
- `.mkdir(parents=True, exist_ok=True)` creates a folder tree and is safe to re-run.
- `.exists()`, `.is_file()` and `.stat().st_size` check a path before you use it.
- `tempfile.TemporaryDirectory()` gives a scratch folder that is deleted afterwards, ideal for experiments and tests.

Run it: `python day13/lesson.py`

## Exercise
`build_inbox(folder)` in `solution.py` creates a fictional export folder with daily sales CSVs
spread over subfolders, plus files that do not belong (a README, an empty CSV, a `.bak` copy).
1. find every `sales_YYYY-MM-DD.csv` file under the folder, in any subfolder, sorted by date;
2. skip empty files and report which ones were skipped;
3. merge the rows into one list, adding a `source` column with the file name;
4. write the merged CSV to `out/merged.csv` inside the folder (create `out/` if needed) and
   print the total amount per day.
Solution: `day13/solution.py`.
