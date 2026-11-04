import random
from collections import defaultdict

import pandas as pd

SHOPS = ["Breda", "Delft", "Gouda"]
PRODUCTS = ["bread", "cheese", "jam", "tea"]
WEEKS = ["2026-W40", "2026-W41", "2026-W42", "2026-W43"]


def make_sales(seed: int) -> list[dict]:
    """Fictional weekly units sold per shop and product, in a shuffled row order."""
    rng = random.Random(seed)
    rows = [{"shop": s, "product": p, "week": w, "units": rng.randint(5, 60)}
            for s in SHOPS for p in PRODUCTS for w in WEEKS]
    rng.shuffle(rows)
    return rows


def make_targets(seed: int) -> list[dict]:
    """Targets for total units over the 4 weeks; one (shop, product) pair has no target."""
    rng = random.Random(seed + 1)
    rows = [{"shop": s, "product": p, "target": rng.randrange(60, 200, 10)}
            for s in SHOPS for p in PRODUCTS if (s, p) != ("Gouda", "jam")]
    rng.shuffle(rows)
    return rows


records = make_sales(33)
target_rows = make_targets(33)

# 1. Index by the natural key and look things up
sales = pd.DataFrame(records).set_index(["shop", "product", "week"]).sort_index()
print("Delft rows:", len(sales.loc["Delft"]))
cell = sales.loc[("Gouda", "tea", "2026-W42"), "units"]
print("Gouda tea W42:", cell)
w43 = sales.xs("2026-W43", level="week")["units"]
print("all shops, W43:", w43.sum(), "units over", len(w43), "shop-product pairs")

# 2. Two products over the last two weeks, every shop
idx = pd.IndexSlice
recent = sales.loc[idx[:, ["cheese", "tea"], WEEKS[-2:]], "units"]
print("cheese+tea, last 2 weeks:", len(recent), "rows,", recent.sum(), "units")

# 3. Wide view and change from the first to the last week
wide = sales["units"].unstack("week")
change = (wide[WEEKS[-1]] - wide[WEEKS[0]]).rename("change")
print("\nbiggest risers:")
print(change.sort_values(ascending=False).head(3).to_string())

# 4. Totals vs. shuffled targets: aligned by label, not by row order
totals = sales.groupby(level=["shop", "product"])["units"].sum()
targets = pd.DataFrame(target_rows).set_index(["shop", "product"])["target"]
gap = (totals - targets).rename("vs_target")
no_target = gap[gap.isna()].index.tolist()
print("\npairs without a target:", no_target)
print("missed target:", (gap < 0).sum(), "of", gap.notna().sum())

# --- check against plain Python dicts ---
by_key = {(r["shop"], r["product"], r["week"]): r["units"] for r in records}
assert cell == by_key[("Gouda", "tea", "2026-W42")]
assert w43.sum() == sum(u for (s, p, w), u in by_key.items() if w == "2026-W43")
assert recent.sum() == sum(u for (s, p, w), u in by_key.items()
                           if p in ("cheese", "tea") and w in WEEKS[-2:])
plain_total = defaultdict(int)
for (s, p, w), u in by_key.items():
    plain_total[(s, p)] += u
plain_target = {(r["shop"], r["product"]): r["target"] for r in target_rows}
for (s, p), total in plain_total.items():
    assert totals[(s, p)] == total
    assert change[(s, p)] == by_key[(s, p, WEEKS[-1])] - by_key[(s, p, WEEKS[0])]
    if (s, p) in plain_target:
        assert gap[(s, p)] == total - plain_target[(s, p)]
    else:
        assert pd.isna(gap[(s, p)])
assert no_target == [("Gouda", "jam")]
print("\nall checks passed")
