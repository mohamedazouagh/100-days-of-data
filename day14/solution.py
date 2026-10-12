from collections import Counter

# Fictional exports from two systems (example.nl / example.com are reserved demo domains)
CRM = [
    "ann@example.nl",
    " Bob@Example.nl",
    "carla@example.com",
    "",
    "ANN@example.nl ",
    "dirk@example.nl",
    "eva@example.com",
    "bob@example.nl",
]
BILLING = [
    "bob@example.nl",
    "Eva@example.com",
    "frank@example.nl",
    "   ",
    "gina@example.com",
    "carla@example.com",
]


def normalise(emails: list[str]) -> list[str]:
    """Strip and lowercase every address, drop blanks, dedupe keeping first-seen order."""
    cleaned = (e.strip().lower() for e in emails)
    return list(dict.fromkeys(e for e in cleaned if e))


def compare(a: list[str], b: list[str]) -> dict[str, list[str]]:
    sa, sb = set(a), set(b)
    return {"only_a": sorted(sa - sb), "only_b": sorted(sb - sa), "both": sorted(sa & sb)}


def duplicates(emails: list[str]) -> list[str]:
    """Addresses that occur more than once after normalising (blanks ignored)."""
    counts = Counter(e.strip().lower() for e in emails if e.strip())
    return sorted(e for e, n in counts.items() if n > 1)


def jaccard(a: list[str], b: list[str]) -> float:
    sa, sb = set(a), set(b)
    return len(sa & sb) / len(sa | sb) if sa | sb else 1.0


def coverage(known: list[str], wanted: list[str]) -> float:
    """Share of ``wanted`` that also appears in ``known``."""
    sw = set(wanted)
    return len(sw & set(known)) / len(sw) if sw else 1.0


if __name__ == "__main__":
    crm, billing = normalise(CRM), normalise(BILLING)
    print("crm    :", crm)
    print("billing:", billing)

    result = compare(crm, billing)
    print("only in CRM    :", result["only_a"])
    print("only in billing:", result["only_b"])
    print("in both        :", result["both"])
    print("CRM duplicates :", duplicates(CRM))
    print(f"jaccard overlap: {jaccard(crm, billing):.2f}")
    print(f"billing customers known to CRM: {coverage(crm, billing):.0%}")

    # Checks
    assert crm == ["ann@example.nl", "bob@example.nl", "carla@example.com", "dirk@example.nl", "eva@example.com"]
    assert billing == ["bob@example.nl", "eva@example.com", "frank@example.nl", "gina@example.com", "carla@example.com"]
    assert result == {
        "only_a": ["ann@example.nl", "dirk@example.nl"],
        "only_b": ["frank@example.nl", "gina@example.com"],
        "both": ["bob@example.nl", "carla@example.com", "eva@example.com"],
    }
    assert duplicates(CRM) == ["ann@example.nl", "bob@example.nl"]
    assert round(jaccard(crm, billing), 4) == round(3 / 7, 4)
    assert coverage(crm, billing) == 0.6
    assert normalise(["", "  "]) == [] and jaccard([], []) == 1.0
    print("all checks passed")
