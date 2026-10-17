from itertools import chain

# Row-oriented: one dict per record (what csv.DictReader and most JSON APIs give you)
ROWS = [
    {"id": 1, "city": "Breda", "temp": 14.2, "tags": ["rain"]},
    {"id": 2, "city": "Utrecht", "temp": 15.1, "tags": []},
    {"id": 3, "city": "Breda", "temp": 13.8, "tags": ["wind", "rain"]},
]

NESTED = {
    "station": "Breda",
    "meta": {"lat": 51.59, "lon": 4.78},
    "readings": [{"t": "08:00", "temp": 11.0}, {"t": "12:00", "temp": 15.5}],
}


def rows_to_columns(rows: list[dict]) -> dict[str, list]:
    """{'id': [1, 2, 3], 'city': [...], ...} - the shape of a DataFrame's columns."""
    keys = list(dict.fromkeys(k for r in rows for k in r))  # union of keys, first-seen order
    return {k: [r.get(k) for r in rows] for k in keys}


def columns_to_rows(cols: dict[str, list]) -> list[dict]:
    lengths = {len(v) for v in cols.values()}
    if len(lengths) > 1:
        raise ValueError(f"columns have different lengths: {sorted(lengths)}")
    return [dict(zip(cols, values)) for values in zip(*cols.values())]


def flatten(d: dict, parent: str = "", sep: str = ".") -> dict:
    """{'meta': {'lat': 1}} -> {'meta.lat': 1}; lists are left as values."""
    out = {}
    for k, v in d.items():
        key = f"{parent}{sep}{k}" if parent else k
        if isinstance(v, dict):
            out.update(flatten(v, key, sep))
        else:
            out[key] = v
    return out


if __name__ == "__main__":
    # 1. rows -> columns and back: two views of the same table
    cols = rows_to_columns(ROWS)
    print("columns:", cols["city"], cols["temp"])
    print("round trip ok:", columns_to_rows(cols) == ROWS)

    # 2. zip(*matrix) transposes a list of lists (rows <-> columns)
    matrix = [[1, 2, 3], [4, 5, 6]]
    print("transposed:", [list(c) for c in zip(*matrix)])

    # 3. zip stops at the shortest input; strict=True turns that into an error
    try:
        list(zip([1, 2, 3], ["a", "b"], strict=True))
    except ValueError as e:
        print("ValueError:", e)

    # 4. flatten nested dicts into dotted column names
    print("flat meta:", flatten({k: v for k, v in NESTED.items() if k != "readings"}))

    # 5. one row per item in a nested list ("explode"), copying the parent fields
    parent = flatten({k: v for k, v in NESTED.items() if k != "readings"})
    long_rows = [{**parent, **reading} for reading in NESTED["readings"]]
    for r in long_rows:
        print("  ", r)

    # 6. one row per tag; records without tags keep a single row with tag=None
    per_tag = [{"id": r["id"], "tag": t} for r in ROWS for t in (r["tags"] or [None])]
    print("per tag:", per_tag)
    print("all tags:", sorted(set(chain.from_iterable(r["tags"] for r in ROWS))))

    # 7. a shape mismatch is caught instead of silently truncated
    try:
        columns_to_rows({"a": [1, 2], "b": [3]})
    except ValueError as e:
        print("ValueError:", e)
