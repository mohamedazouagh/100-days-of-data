import timeit

if __name__ == "__main__":
    # 1. A set keeps one copy of each value
    cities = ["Breda", "Gent", "Breda", "Utrecht", "Gent"]
    print("unique:", sorted(set(cities)))

    # 2. Dedupe but keep the first-seen order
    print("ordered unique:", list(dict.fromkeys(cities)))

    # 3. The four core operations
    this_week = {"A1", "B2", "C3", "D4"}
    last_week = {"B2", "C3", "E5"}
    print("union       :", sorted(this_week | last_week))
    print("intersection:", sorted(this_week & last_week))
    print("new         :", sorted(this_week - last_week))
    print("dropped     :", sorted(last_week - this_week))
    print("changed     :", sorted(this_week ^ last_week))

    # 4. Subset / disjoint checks
    print("subset?", {"B2", "C3"} <= this_week, "| disjoint?", this_week.isdisjoint({"Z9"}))

    # 5. Normalise before comparing
    raw = ["Ann@Example.nl ", "ann@example.nl", " BOB@example.nl", ""]
    clean = {e.strip().lower() for e in raw if e.strip()}
    print("normalised:", sorted(clean))

    # 6. Tuples as composite keys
    sold = {("2026-10-01", "A1"), ("2026-10-01", "B2"), ("2026-10-02", "A1")}
    print("A1 on 2026-10-02?", ("2026-10-02", "A1") in sold)

    # 7. Membership speed: list vs set
    ids_list = list(range(100_000))
    ids_set = set(ids_list)
    t_list = timeit.timeit(lambda: 99_999 in ids_list, number=200)
    t_set = timeit.timeit(lambda: 99_999 in ids_set, number=200)
    print(f"set lookup faster than list: {t_set < t_list}")

    # 8. One number for overlap: Jaccard similarity
    jaccard = len(this_week & last_week) / len(this_week | last_week)
    print(f"jaccard: {jaccard:.2f}")
