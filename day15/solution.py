from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")
ZERO = Decimal("0")

# Fictional shop invoice: (item, unit price as text, quantity, VAT rate in %)
INVOICE = [
    ("Notebook", "2.49", 3, 21),
    ("Pen", "0.85", 7, 21),
    ("Coffee beans", "8.95", 2, 9),
    ("Lollipop cherry", "0.26", 1, 9),
    ("Lollipop lemon", "0.26", 1, 9),
    ("Lollipop mint", "0.26", 1, 9),
    ("Stickers", "0.35", 5, 21),
]


def cents(x: Decimal) -> Decimal:
    return x.quantize(CENT, rounding=ROUND_HALF_UP)


def line_amounts(price: str, qty: int, rate: int) -> tuple[Decimal, Decimal]:
    """(net, VAT) for one line, both rounded to cents."""
    net = cents(Decimal(price) * qty)
    vat = cents(net * rate / 100)
    return net, vat


def totals(invoice) -> dict:
    """Net total, VAT per rate (rounded per line) and grand total."""
    net_total, vat_by_rate = ZERO, {}
    for _, price, qty, rate in invoice:
        net, vat = line_amounts(price, qty, rate)
        net_total += net
        vat_by_rate[rate] = vat_by_rate.get(rate, ZERO) + vat
    grand = net_total + sum(vat_by_rate.values(), ZERO)
    return {"net": net_total, "vat": vat_by_rate, "grand": grand}


def vat_on_totals(invoice) -> dict:
    """VAT per rate computed on the summed net amounts and rounded once."""
    net_by_rate: dict[int, Decimal] = {}
    for _, price, qty, rate in invoice:
        net_by_rate[rate] = net_by_rate.get(rate, ZERO) + cents(Decimal(price) * qty)
    return {rate: cents(net * rate / 100) for rate, net in net_by_rate.items()}


def float_grand_total(invoice) -> float:
    """Same calculation with floats and no rounding, as a naive script would do it."""
    total = 0.0
    for _, price, qty, rate in invoice:
        net = float(price) * qty
        total += net + net * rate / 100
    return total


def split(total: Decimal, people: int) -> list[Decimal]:
    """Split ``total`` into ``people`` cent amounts that differ by at most 1 cent and add up exactly."""
    if people < 1:
        raise ValueError("people must be >= 1")
    base = (total / people).quantize(CENT, rounding=ROUND_DOWN)
    remainder = int((total - base * people) / CENT)
    return [base + CENT if i < remainder else base for i in range(people)]


if __name__ == "__main__":
    print(f"{'item':<16}{'net':>8}{'VAT':>7}")
    for item, price, qty, rate in INVOICE:
        net, vat = line_amounts(price, qty, rate)
        print(f"{item:<16}{net:>8}{vat:>7}  ({qty} x {price}, {rate}%)")

    t = totals(INVOICE)
    print("net total  :", t["net"])
    for rate, vat in sorted(t["vat"].items()):
        print(f"VAT {rate:>2}%    :", vat)
    print("grand total:", t["grand"])
    f = float_grand_total(INVOICE)
    float_net = 0.0
    for _, price, qty, _ in INVOICE:
        float_net += float(price) * qty
    print("float net  :", float_net, "(running float sum of the same nets)")
    print("float total:", f, "-> rounded", f"{f:.2f}", "vs invoice", t["grand"])

    on_totals = vat_on_totals(INVOICE)
    for rate in sorted(on_totals):
        diff = int((t["vat"][rate] - on_totals[rate]) / CENT)
        print(f"VAT {rate}%: per line {t['vat'][rate]} vs on total {on_totals[rate]} -> {diff:+d} cent(s)")

    shares = split(t["grand"], 3)
    print("split over 3:", [str(s) for s in shares], "sum", sum(shares, ZERO))

    # Checks
    assert t["net"] == Decimal("33.85")
    assert t["vat"] == {21: Decimal("3.19"), 9: Decimal("1.67")}
    assert t["grand"] == Decimal("38.71")
    assert f"{f:.2f}" == "38.72"  # the naive float script is a cent off the real invoice
    assert vat_on_totals(INVOICE) == {21: Decimal("3.19"), 9: Decimal("1.68")}
    assert split(t["grand"], 3) == [Decimal("12.91"), Decimal("12.90"), Decimal("12.90")]
    for total, n in [(Decimal("100.00"), 3), (Decimal("0.05"), 4), (Decimal("10.00"), 1), (Decimal("0.00"), 2)]:
        parts = split(total, n)
        assert sum(parts, ZERO) == total and max(parts) - min(parts) <= CENT
    assert cents(Decimal("2.675")) == Decimal("2.68") and round(2.675, 2) == 2.67

    print("all checks passed")
