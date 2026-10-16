import random
import re
import time
from functools import lru_cache, partial, reduce
from operator import itemgetter

AREAS = ["4811", "4812", "3511", "3512", "5038", "1012"]
REGION_OF_AREA = {"48": "Breda area", "35": "Utrecht area", "50": "Tilburg area", "10": "Amsterdam area"}
POSTCODE = re.compile(r"[1-9]\d{3}[A-Z]{2}")


def compose(*funcs):
    return lambda x: reduce(lambda acc, f: f(acc), funcs, x)


def drop_separators(s: str) -> str:
    return s.replace(" ", "").replace("-", "")


def validate(code: str) -> str | None:
    return code if POSTCODE.fullmatch(code) else None


normalise_postcode = compose(str.strip, str.upper, drop_separators, validate)


def parse_number(text: str, decimal: str = ".") -> float:
    return float(text.strip().replace(decimal, "."))


parse_amount = partial(parse_number, decimal=",")


def make_records(seed: int, n: int = 2_000) -> list[dict]:
    """Fictional deliveries with messy postcode formats and decimal-comma amounts."""
    rng = random.Random(seed)
    styles = [lambda a, l: f" {a}{l.lower()}", lambda a, l: f"{a} {l}", lambda a, l: f"{a}-{l.lower()}"]
    out = []
    for _ in range(n):
        area, letters = rng.choice(AREAS), "".join(rng.choices("ABCDEFGHJKLMNPRTVWXZ", k=2))
        code = rng.choice(styles)(area, letters)
        if rng.random() < 0.02:
            code = rng.choice(["48A1 BC", "0123AB", "4811", ""])  # broken input
        cents = rng.randint(250, 9_999)
        out.append({"postcode": code, "amount": f"{cents // 100},{cents % 100:02d}"})
    return out


def slow_area_to_region(area: str) -> str:
    time.sleep(0.01)  # stands in for a slow lookup
    return REGION_OF_AREA.get(area[:2], "unknown")


cached_area_to_region = lru_cache(maxsize=None)(slow_area_to_region)


def add_row(acc: dict, row: dict) -> dict:
    code = normalise_postcode(row["postcode"])
    if code is None:
        acc["invalid"] += 1
        return acc
    area = code[:4]
    acc["totals"][area] = round(acc["totals"].get(area, 0.0) + parse_amount(row["amount"]), 2)
    return acc


if __name__ == "__main__":
    records = make_records(seed=18)

    # 1. composed normaliser + partial parser
    for raw in [" 4811ab", "4811 AB", "4811-ab", "0123AB", "48A1 BC"]:
        print(f"{raw!r:>11} -> {normalise_postcode(raw)}")
    print("parse_amount('12,50') =", parse_amount("12,50"))
    assert normalise_postcode(" 4811ab") == normalise_postcode("4811-ab") == "4811AB"
    assert parse_amount("12,50") == 12.5

    # 2. totals per area with reduce, top 3 with itemgetter
    result = reduce(add_row, records, {"totals": {}, "invalid": 0})
    totals, invalid = result["totals"], result["invalid"]
    top3 = sorted(totals.items(), key=itemgetter(1), reverse=True)[:3]
    print("top 3 areas:", top3, "| invalid postcodes:", invalid)
    grand = round(sum(totals.values()), 2)
    valid_sum = round(sum(parse_amount(r["amount"]) for r in records if normalise_postcode(r["postcode"])), 2)
    assert grand == valid_sum, (grand, valid_sum)

    # 3. cached lookup: one miss per distinct area
    areas = [normalise_postcode(r["postcode"])[:4] for r in records if normalise_postcode(r["postcode"])]
    start = time.perf_counter()
    cached = [cached_area_to_region(a) for a in areas]
    elapsed = time.perf_counter() - start
    info = cached_area_to_region.cache_info()
    print(f"{len(areas)} cached lookups in {elapsed:.2f}s:", info)
    assert info.misses == len(set(areas)) and info.hits == len(areas) - info.misses

    # 4. cached == uncached, and nothing silently dropped
    distinct = sorted(set(areas))
    assert [cached_area_to_region(a) for a in distinct] == [slow_area_to_region(a) for a in distinct]
    assert len(areas) + invalid == len(records)
    print("regions:", {a: cached_area_to_region(a) for a in distinct})
    print("all checks passed")
