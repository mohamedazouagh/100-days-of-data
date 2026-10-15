import random
from collections import Counter
from statistics import mean

if __name__ == "__main__":
    # 1. A seed makes "random" results reproducible
    random.seed(17)
    first = [random.randint(1, 6) for _ in range(5)]
    random.seed(17)
    again = [random.randint(1, 6) for _ in range(5)]
    print("same seed, same rolls:", first, again, first == again)

    # 2. Own Random instance: reproducible without touching the global state
    rng = random.Random(42)
    print("rng.random():", round(rng.random(), 4), "| uniform(10, 20):", round(rng.uniform(10, 20), 2))

    # 3. sample = without replacement, choices = with replacement
    ids = list(range(1, 11))
    print("sample 4  :", rng.sample(ids, 4))
    print("choices 4 :", rng.choices(ids, k=4))
    try:
        rng.sample(ids, 11)
    except ValueError as e:
        print("ValueError:", e)

    # 4. Weighted choices: simulate a biased source and check the shares
    picks = rng.choices(["web", "app", "store"], weights=[6, 3, 1], k=10_000)
    shares = {k: round(v / len(picks), 3) for k, v in sorted(Counter(picks).items())}
    print("weighted shares:", shares)

    # 5. shuffle works in place and returns None; copy first to keep the original
    deck = ["a", "b", "c", "d", "e"]
    shuffled = deck[:]
    print("shuffle returns:", rng.shuffle(shuffled), "| original:", deck, "| shuffled:", shuffled)

    # 6. Reproducible train/test split
    rows = list(range(100))
    order = rows[:]
    random.Random(7).shuffle(order)
    train, test = sorted(order[:80]), sorted(order[80:])
    print("train/test sizes:", len(train), len(test), "| overlap:", len(set(train) & set(test)))
    print("first test ids:", test[:5])

    # 7. Sampling error: means of small samples scatter around the true mean
    population = [rng.gauss(50, 10) for _ in range(10_000)]
    sample_means = [mean(rng.sample(population, 25)) for _ in range(1_000)]
    print("population mean:", round(mean(population), 2),
          "| sample means range:", round(min(sample_means), 1), "to", round(max(sample_means), 1))
