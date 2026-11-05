import io

import pandas as pd

# A small fictional export from a Dutch till system: semicolons between fields,
# a comma as decimal mark, a dot as thousands separator, a title line on top,
# "n/a" and "-" meaning "no value", and a trailing total line.
RAW = """Export kassa;week 44
date;store;sku;qty;price;revenue;note
03-11-2026;Breda;0042;3;2,50;7,50;
03-11-2026;Delft;0042;-;2,50;-;till offline
04-11-2026;Breda;0107;1.200;0,99;1.188,00;bulk order
04-11-2026;Gouda;0107;n/a;0,99;n/a;
05-11-2026;Delft;0009;2;12,95;25,90;
TOTAL;;;;;1.221,40;
"""

# 1. The naive read assumes commas between fields and a header on line 1. Here the
#    title line has no comma (1 field), then decimal commas split "2,50" into extra
#    fields, so the parser gives up.
try:
    pd.read_csv(io.StringIO(RAW))
except pd.errors.ParserError as e:
    print("ParserError:", str(e).strip())
print()

# 2. Tell read_csv what the file looks like instead of fixing it afterwards.
df = pd.read_csv(
    io.StringIO(RAW),
    sep=";",                     # field separator
    skiprows=1,                  # skip the title line above the header
    skipfooter=1,                # drop the TOTAL line (needs the python engine)
    engine="python",
    decimal=",",                 # 2,50 -> 2.5
    thousands=".",               # 1.200 -> 1200
    na_values=["n/a", "-"],      # extra markers that mean "missing"
    dtype={"sku": "string",      # keep leading zeros: "0042", not 42
           "qty": "Int64"},      # whole numbers that may be missing (else float64)
)
print(df)
print(df.dtypes)
print()

# 3. Dates: an explicit format (day first) instead of letting pandas guess.
df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
print(df["date"].dt.day_name().tolist())
print()

# 4. usecols reads only the columns you need (less memory on wide files).
small = pd.read_csv(io.StringIO(RAW), sep=";", skiprows=1, usecols=["store", "sku"],
                    dtype={"sku": "string"})
print(small.head(2))
print()

# 5. Big files: chunksize returns an iterator of DataFrames, so you can aggregate
#    piece by piece without loading everything at once. skipfooter does not work
#    with chunks, so the TOTAL line is filtered out inside the loop instead.
qty_per_store: dict[str, int] = {}
reader = pd.read_csv(io.StringIO(RAW), sep=";", skiprows=1, decimal=",", thousands=".",
                     na_values=["n/a", "-"], dtype={"qty": "Int64"}, chunksize=2,
                     engine="python")
for chunk in reader:
    chunk = chunk[chunk["date"] != "TOTAL"]
    for store, q in chunk.groupby("store")["qty"].sum().items():
        qty_per_store[store] = qty_per_store.get(store, 0) + int(q)
print(qty_per_store)
print()

# 6. Writing back: choose the separator/decimal the reader expects, and drop the index.
out = io.StringIO()
df.to_csv(out, sep=";", decimal=",", index=False, date_format="%Y-%m-%d")
print(out.getvalue().splitlines()[:3])
