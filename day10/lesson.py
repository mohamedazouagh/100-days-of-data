import heapq
from operator import itemgetter

# Fictional product sales, one dict per row (like csv.DictReader output from day 04)
SALES = [
    {"product": "kettle", "category": "kitchen", "units": 14, "price": 29.99},
    {"product": "toaster", "category": "kitchen", "units": 9, "price": 34.50},
    {"product": "lamp", "category": "living", "units": 21, "price": 19.00},
    {"product": "rug", "category": "living", "units": 3, "price": 89.00},
    {"product": "mug", "category": "kitchen", "units": 21, "price": 6.50},
    {"product": "cushion", "category": "living", "units": 9, "price": 12.00},
]


def revenue(row):
    return round(row["units"] * row["price"], 2)


if __name__ == "__main__":
    # 1. sorted() returns a new list; key= says what to compare
    print([r["product"] for r in sorted(SALES, key=revenue, reverse=True)])

    # 2. itemgetter is a faster, named alternative to lambda r: r["units"]
    print([r["product"] for r in sorted(SALES, key=itemgetter("units"))])

    # 3. Sort is stable: equal keys keep their input order (lamp before mug, toaster before cushion)
    print([(r["product"], r["units"]) for r in sorted(SALES, key=itemgetter("units"), reverse=True)])

    # 4. Several keys with a tuple; negate a number to mix directions (units desc, name asc)
    print([r["product"] for r in sorted(SALES, key=lambda r: (-r["units"], r["product"]))])

    # 5. itemgetter with several fields builds that tuple for you (all ascending)
    print([r["product"] for r in sorted(SALES, key=itemgetter("category", "units"))])

    # 6. Top-N without sorting everything: heapq.nlargest / nsmallest accept key= too
    print([r["product"] for r in heapq.nlargest(2, SALES, key=revenue)])
    print([r["product"] for r in heapq.nsmallest(2, SALES, key=itemgetter("price"))])

    # 7. max/min with key return the whole row, not just the value
    best = max(SALES, key=revenue)
    print(best["product"], revenue(best))

    # 8. Dense rank: equal values share a rank, the next distinct value gets rank + 1
    distinct = sorted({r["units"] for r in SALES}, reverse=True)
    rank = {units: i + 1 for i, units in enumerate(distinct)}
    print([(r["product"], rank[r["units"]]) for r in SALES])

    # 9. list.sort() sorts in place and returns None - a classic bug when assigned
    rows = list(SALES)
    result = rows.sort(key=itemgetter("price"))
    print(result, rows[0]["product"])
