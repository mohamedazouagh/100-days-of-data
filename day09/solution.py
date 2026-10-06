import re

# Fictional support-ticket subject lines
TICKETS = [
    "TCK-0001 refund EUR 12.50 requested on 2026-10-03",
    "tck-0002: double charge €7,99 (see also TCK-0001)",
    "Re: Tck-0003 invoice 03/10/2026 shows 120.00 EUR",
    "TCK-0002 follow-up, paid €15 on 04/10/2026",
    "no ticket id here, just EUR 3.05",
]

TICKET = re.compile(r"\bTCK-(\d{4})\b", re.IGNORECASE)
AMOUNT = re.compile(
    r"""
    (?:EUR\s*|€)(?P<pre>\d+(?:[.,]\d{2})?)  # EUR 12.50 / €12,50 / €15
    |
    (?P<post>\d+(?:[.,]\d{2})?)\s*EUR      # 12.50 EUR
    """,
    re.VERBOSE,
)
DATE = re.compile(r"(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2})|(?P<d2>\d{2})/(?P<m2>\d{2})/(?P<y2>\d{4})")
PRODUCT = re.compile(r"[A-Z]{3}-\d{3}")


def ticket_ids(lines):
    """Upper-cased ticket IDs, de-duplicated, in first-seen order."""
    seen = {}
    for line in lines:
        for digits in TICKET.findall(line):
            seen.setdefault(f"TCK-{digits}", None)
    return list(seen)


def to_cents(text):
    """'12.50', '7,99' or '15' -> integer cents."""
    euros, _, cents = re.sub(",", ".", text).partition(".")
    return int(euros) * 100 + int(cents or 0)


def amounts(line):
    return [to_cents(m["pre"] or m["post"]) for m in AMOUNT.finditer(line)]


def iso_dates(line):
    out = []
    for m in DATE.finditer(line):
        if m["y"]:
            out.append(f"{m['y']}-{m['m']}-{m['d']}")
        else:
            out.append(f"{m['y2']}-{m['m2']}-{m['d2']}")
    return out


def valid_codes(codes):
    return {code: PRODUCT.fullmatch(code) is not None for code in codes}


if __name__ == "__main__":
    ids = ticket_ids(TICKETS)
    print("tickets:", ids)

    found = [amounts(t) for t in TICKETS]
    print("amounts (cents):", found)

    dates = [iso_dates(t) for t in TICKETS]
    print("dates:", dates)

    codes = valid_codes(["ABC-123", "abc-123", "ABCD-123", "AB-123", "XYZ-999 "])
    print("codes:", codes)

    assert ids == ["TCK-0001", "TCK-0002", "TCK-0003"]
    assert found == [[1250], [799], [12000], [1500], [305]]
    assert dates == [["2026-10-03"], [], ["2026-10-03"], ["2026-10-04"], []]
    assert codes == {"ABC-123": True, "abc-123": False, "ABCD-123": False, "AB-123": False, "XYZ-999 ": False}
    print("all checks passed")
