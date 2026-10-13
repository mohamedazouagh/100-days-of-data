from decimal import ROUND_DOWN, ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")

if __name__ == "__main__":
    # 1. Floats cannot store most cent amounts exactly
    print("float  :", 0.1 + 0.2, "| == 0.3?", 0.1 + 0.2 == 0.3)
    print("Decimal:", Decimal("0.1") + Decimal("0.2"), "| == 0.3?", Decimal("0.1") + Decimal("0.2") == Decimal("0.3"))

    # 2. Build from strings, not floats
    print("from float :", Decimal(19.99))
    print("from string:", Decimal("19.99"))

    # 3. Rounding to cents: pick the rule explicitly
    for x in ("2.675", "2.665", "0.125"):
        d = Decimal(x)
        print(f"{x}: half_up={d.quantize(CENT, rounding=ROUND_HALF_UP)}"
              f" half_even={d.quantize(CENT, rounding=ROUND_HALF_EVEN)}"
              f" float round()={round(float(x), 2)}")
    print("round(2.5), round(3.5):", round(2.5), round(3.5))

    # 4. Adding up small amounts one by one (a running balance)
    #    (Python 3.12+ sum() compensates float error, a plain += loop does not)
    float_total, dec_total = 0.0, Decimal("0")
    for _ in range(10):
        float_total += 0.10
        dec_total += Decimal("0.10")
    print("ten x 0.10 ->", float_total, "vs", dec_total)

    # 5. Round each line vs. round the total
    lines = [Decimal("0.333"), Decimal("0.333"), Decimal("0.333")]
    per_line = sum((x.quantize(CENT, rounding=ROUND_HALF_UP) for x in lines), Decimal("0"))
    on_total = sum(lines, Decimal("0")).quantize(CENT, rounding=ROUND_HALF_UP)
    print("per line:", per_line, "| on total:", on_total)

    # 6. Splitting money without losing a cent
    total, people = Decimal("100.00"), 3
    base = (total / people).quantize(CENT, rounding=ROUND_DOWN)
    remainder = int((total - base * people) / CENT)
    shares = [base + CENT if i < remainder else base for i in range(people)]
    print("shares:", shares, "| sum:", sum(shares, Decimal("0")))

    # 7. Mixing with float is an error, on purpose
    try:
        Decimal("1.00") + 0.5
    except TypeError as e:
        print("TypeError:", e)
