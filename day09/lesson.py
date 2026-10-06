import re

# Free-text order notes, the kind that end up in a "comments" column
NOTES = [
    "Order #A-1042 shipped 2026-10-01, total EUR 34.90",
    "order #a-1043: refund of EUR 5.00 on 2026-10-02",
    "Call back re #A-1044 (no total yet)",
    "Duplicate of #A-1042, ignore",
]

ORDER = re.compile(r"#([A-Z]-\d{4})", re.IGNORECASE)
AMOUNT = re.compile(r"EUR\s+(?P<euros>\d+)\.(?P<cents>\d{2})")
DATE = re.compile(r"(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2})")


if __name__ == "__main__":
    # 1. search finds the first match anywhere; group(1) is the first (...) capture
    m = ORDER.search(NOTES[0])
    print(m.group(0), "->", m.group(1))

    # 2. search returns None when nothing matches - always check before .group()
    print(AMOUNT.search(NOTES[2]))

    # 3. findall returns every capture; IGNORECASE matched the lowercase 'a-1043'
    print([ORDER.findall(n) for n in NOTES])

    # 4. Named groups read like a dict and make the pattern self-documenting
    m = AMOUNT.search(NOTES[0])
    print(m.groupdict(), int(m["euros"]) * 100 + int(m["cents"]), "cents")

    # 5. finditer gives match objects with positions, lazily
    for m in DATE.finditer(" ".join(NOTES)):
        print(m.span(), m["d"] + "/" + m["m"] + "/" + m["y"])

    # 6. sub rewrites matches; a backreference \g<name> reuses a capture
    print(DATE.sub(r"\g<d>.\g<m>.\g<y>", NOTES[1]))

    # 7. fullmatch validates the *whole* string (search would accept junk around it)
    for code in ["A-1042", "A-1042x", "B-7"]:
        print(code, bool(re.fullmatch(r"[A-Z]-\d{4}", code)), bool(re.search(r"[A-Z]-\d{4}", code)))

    # 8. re.VERBOSE lets a long pattern carry comments
    price = re.compile(
        r"""
        (?P<cur>EUR|USD)  # currency code
        \s+
        (?P<value>\d+(?:\.\d{2})?)  # 12 or 12.50
        """,
        re.VERBOSE,
    )
    print(price.search("paid USD 12.50 cash").groupdict())
