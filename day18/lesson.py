from functools import lru_cache, partial, reduce
from operator import add, attrgetter, itemgetter
import time

ROWS = [
    {"city": " breda ", "amount": "12.50", "region": "south"},
    {"city": "Utrecht", "amount": "7.00", "region": "centre"},
    {"city": "BREDA", "amount": "3.25", "region": "south"},
    {"city": "tilburg", "amount": "20.00", "region": "south"},
    {"city": "utrecht ", "amount": "4.75", "region": "centre"},
]


def compose(*funcs):
    """compose(f, g, h)(x) == h(g(f(x))): apply left to right, like a pipeline."""
    return lambda x: reduce(lambda acc, f: f(acc), funcs, x)


if __name__ == "__main__":
    # 1. partial: pre-fill arguments to make a specialised function
    round_whole = partial(round, ndigits=0)
    parse_hex = partial(int, base=16)
    print("partial round:", round_whole(1249.6), "| int('ff', base=16):", parse_hex("ff"))

    # 2. Small functions + compose = a readable cleaning pipeline
    clean_city = compose(str.strip, str.lower, str.title)
    print("cleaned cities:", [clean_city(r["city"]) for r in ROWS])

    # 3. reduce folds a sequence into one value (sum is a special case)
    amounts = [float(r["amount"]) for r in ROWS]
    print("reduce(add):", reduce(add, amounts), "| sum():", sum(amounts))

    def merge_totals(acc, row):
        city = clean_city(row["city"])
        return {**acc, city: round(acc.get(city, 0) + float(row["amount"]), 2)}

    print("totals per city:", reduce(merge_totals, ROWS, {}))

    # 4. operator.itemgetter / attrgetter instead of small lambdas
    by_amount = sorted(ROWS, key=lambda r: float(r["amount"]), reverse=True)
    get_pair = itemgetter("region", "amount")
    print("top row region+amount:", get_pair(by_amount[0]))
    print("real parts via attrgetter:", list(map(attrgetter("real"), [3 + 4j, 1.5])))

    # 5. lru_cache: remember results of a slow, pure function
    @lru_cache(maxsize=None)
    def lookup_region(city: str) -> str:
        time.sleep(0.05)  # pretend this is a slow API or file lookup
        return {"Breda": "NL-NB", "Tilburg": "NL-NB", "Utrecht": "NL-UT"}.get(city, "?")

    start = time.perf_counter()
    codes = [lookup_region(clean_city(r["city"])) for r in ROWS * 20]  # 100 calls
    elapsed = time.perf_counter() - start
    print("codes:", sorted(set(codes)), "| 100 lookups in", f"{elapsed:.2f}s")
    print(lookup_region.cache_info())

    # 6. Caching only makes sense for pure functions with hashable arguments
    try:
        lookup_region(["Breda"])
    except TypeError as e:
        print("TypeError:", e)
    lookup_region.cache_clear()
    print("after cache_clear:", lookup_region.cache_info().currsize, "entries")
