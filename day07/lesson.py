import statistics as st

# Daily max temperatures (°C) for two weeks; one day was not reported
TEMPS = [21.4, 22.1, 26.2, 24.8, 21.0, 19.5, 19.7, None, 18.2, 17.9, 18.6, 20.3, 31.5, 19.1]


if __name__ == "__main__":
    # 1. Drop missing values first - the statistics functions do not skip None
    values = [t for t in TEMPS if t is not None]
    print(len(TEMPS), "days,", len(values), "with a value")

    # 2. Centre: mean is pulled by the 31.5 outlier, median is not
    print(f"mean   {st.mean(values):.2f}")
    print(f"median {st.median(values):.2f}")

    # 3. Spread: sample standard deviation (n - 1) vs population (n)
    print(f"stdev  {st.stdev(values):.2f}  (sample)")
    print(f"pstdev {st.pstdev(values):.2f}  (population)")

    # 4. Quartiles and the interquartile range (IQR)
    q1, q2, q3 = st.quantiles(values, n=4)
    iqr = q3 - q1
    print(f"Q1 {q1:.2f} | Q2 {q2:.2f} | Q3 {q3:.2f} | IQR {iqr:.2f}")

    # 5. A simple outlier rule: more than 1.5 * IQR outside the quartiles
    low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    outliers = [v for v in values if v < low or v > high]
    print(f"fences {low:.2f} .. {high:.2f} -> outliers {outliers}")

    # 6. Without the outlier the mean moves a lot, the median barely
    clean = [v for v in values if v not in outliers]
    print(f"clean mean {st.mean(clean):.2f}, clean median {st.median(clean):.2f}")

    # 7. Statistics on an empty list raise StatisticsError - guard for it
    try:
        st.mean([])
    except st.StatisticsError as exc:
        print("empty:", exc)
