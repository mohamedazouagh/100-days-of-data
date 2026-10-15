import random
from collections import Counter, defaultdict
from statistics import mean, quantiles

REGIONS = {"north": 0.5, "south": 0.3, "east": 0.2}  # share of orders per region


def make_orders(seed: int, n: int = 1_000) -> list[dict]:
    """Fictional orders: id, region (weighted) and an amount that differs a bit per region."""
    rng = random.Random(seed)
    base = {"north": 40.0, "south": 55.0, "east": 70.0}
    regions = rng.choices(list(REGIONS), weights=list(REGIONS.values()), k=n)
    return [
        {"id": i, "region": r, "amount": round(max(1.0, rng.gauss(base[r], 15)), 2)}
        for i, r in enumerate(regions, start=1)
    ]


def simple_sample(rows: list[dict], k: int, rng: random.Random) -> list[dict]:
    return rng.sample(rows, k)


def stratified_sample(rows: list[dict], frac: float, rng: random.Random) -> list[dict]:
    """Same fraction from every region (rounded), so region shares are kept."""
    groups: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        groups[r["region"]].append(r)
    out = []
    for region in sorted(groups):
        group = groups[region]
        out += rng.sample(group, round(len(group) * frac))
    return out


def bootstrap_ci(values: list[float], rng: random.Random, reps: int = 2_000) -> tuple[float, float]:
    """95 % percentile interval of the mean from ``reps`` resamples with replacement."""
    means = [mean(rng.choices(values, k=len(values))) for _ in range(reps)]
    cuts = quantiles(means, n=40, method="inclusive")  # cut points every 2.5 %
    return cuts[0], cuts[-1]


def run(seed: int) -> dict:
    orders = make_orders(seed)
    rng = random.Random(seed + 1)
    sample = simple_sample(orders, 50, rng)
    strat = stratified_sample(orders, 0.10, rng)
    amounts = [o["amount"] for o in sample]
    lo, hi = bootstrap_ci(amounts, rng)
    return {
        "full_mean": mean(o["amount"] for o in orders),
        "full_regions": Counter(o["region"] for o in orders),
        "sample_mean": mean(amounts),
        "sample_regions": Counter(o["region"] for o in sample),
        "strat_regions": Counter(o["region"] for o in strat),
        "ci": (lo, hi),
    }


if __name__ == "__main__":
    res = run(seed=2026)

    print(f"1. full table mean : {res['full_mean']:.2f} over 1000 orders")
    print(f"   sample (n=50)   : {res['sample_mean']:.2f}  (diff {res['sample_mean'] - res['full_mean']:+.2f})")

    print("2. region counts    full | simple 50 | stratified 10 %")
    for region in sorted(REGIONS):
        print(f"   {region:<6} {res['full_regions'][region]:>11} | {res['sample_regions'][region]:>9} | {res['strat_regions'][region]:>6}")
    for region in sorted(REGIONS):
        assert res["strat_regions"][region] == round(res["full_regions"][region] * 0.10)

    lo, hi = res["ci"]
    print(f"3. 95 % bootstrap CI for the sample mean: {lo:.2f} to {hi:.2f}")
    print(f"   contains the full-table mean? {lo <= res['full_mean'] <= hi}")

    again = run(seed=2026)
    print("4. same seed, identical results?", again == res)
    assert again == res
    print("   different seed, same results?", run(seed=7) == res)
