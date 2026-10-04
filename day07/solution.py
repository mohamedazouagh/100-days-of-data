import statistics as st

# Fictional team, ten days of step counts; None = tracker not worn
STEPS = {
    "Ana": [8200, 9100, 7600, None, 8800, 9400, 8100, 7900, 8600, 9000],
    "Bram": [4100, 3900, 4500, 4200, 21000, 3800, None, 4400, 4000, 4300],
    "Chen": [12000, 11500, None, None, 12800, 13100, 11900, 12400, 12200, 11800],
}


def describe(values):
    """Count, mean, median and sample stdev of the non-missing values."""
    clean = [v for v in values if v is not None]
    return {
        "n": len(clean),
        "mean": st.mean(clean),
        "median": st.median(clean),
        "stdev": st.stdev(clean),
    }


def outlier_days(values):
    """(day number, value) pairs outside Q1 - 1.5*IQR .. Q3 + 1.5*IQR. Days start at 1."""
    clean = [v for v in values if v is not None]
    q1, _, q3 = st.quantiles(clean, n=4)
    iqr = q3 - q1
    low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return [(day, v) for day, v in enumerate(values, start=1) if v is not None and not low <= v <= high]


if __name__ == "__main__":
    stats = {name: describe(vals) for name, vals in STEPS.items()}
    ranked = sorted(stats, key=lambda name: stats[name]["median"], reverse=True)

    print(f"{'name':<6}{'n':>3}{'mean':>9}{'median':>9}{'stdev':>9}  outliers")
    for name in ranked:
        s = stats[name]
        print(
            f"{name:<6}{s['n']:>3}{s['mean']:>9.0f}{s['median']:>9.0f}{s['stdev']:>9.0f}  {outlier_days(STEPS[name])}"
        )

    skewed = max(stats, key=lambda name: abs(stats[name]["mean"] - stats[name]["median"]))
    gap = stats[skewed]["mean"] - stats[skewed]["median"]
    print(f"biggest mean/median gap: {skewed} ({gap:+.0f} steps)")

    assert ranked == ["Chen", "Ana", "Bram"]
    assert [stats[n]["n"] for n in ranked] == [8, 9, 9]
    assert stats["Bram"]["median"] == 4200 and round(stats["Bram"]["mean"]) == 6022
    assert outlier_days(STEPS["Bram"]) == [(5, 21000)]
    assert outlier_days(STEPS["Ana"]) == [] and outlier_days(STEPS["Chen"]) == []
    assert skewed == "Bram"
