import codecs
import unicodedata

# Fictional customer exports, as the raw bytes each system wrote.
SOURCES = {
    # Excel "CSV UTF-8": BOM + UTF-8; one name was already mojibake'd upstream.
    "webshop": codecs.BOM_UTF8 + "Zoë Jansen\n  José Martín \nCafÃ© Owner\nRené Faber\n".encode("utf-8"),
    # Old desktop tool: Windows-1252.
    "till": "ZOË JANSEN\nRené Faber\nBjörk Lund\n".encode("cp1252"),
    # macOS export: UTF-8 with combining accents (NFD).
    "app": unicodedata.normalize("NFD", "jose martin\nBjörk Lund\nAnaïs Petit\n").encode("utf-8"),
}

MOJIBAKE_MARKERS = ("Ã", "â€", "Â")


def decode_any(raw: bytes) -> tuple[str, str]:
    """Decode with utf-8-sig (handles a BOM), fall back to cp1252."""
    for enc in ("utf-8-sig", "cp1252"):
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace"), "utf-8 (replaced)"


def fix_mojibake(s: str) -> str:
    """Undo UTF-8-read-as-cp1252 once; leave the text alone if that is not what happened."""
    if not any(m in s for m in MOJIBAKE_MARKERS):
        return s
    try:
        return s.encode("cp1252").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


def clean(name: str) -> str:
    return unicodedata.normalize("NFC", fix_mojibake(name)).strip()


def match_key(name: str) -> str:
    """Case- and accent-insensitive key, whitespace collapsed."""
    nfkd = unicodedata.normalize("NFKD", name)
    base = "".join(c for c in nfkd if not unicodedata.combining(c))
    return " ".join(base.casefold().split())


if __name__ == "__main__":
    # 1. Decode every source with the detected codec
    names: dict[str, list[str]] = {}
    for source, raw in SOURCES.items():
        text, enc = decode_any(raw)
        names[source] = text.splitlines()
        print(f"{source:8} decoded as {enc}")
    assert decode_any(SOURCES["till"])[1] == "cp1252"
    assert not names["webshop"][0].startswith("﻿"), "BOM must be gone"

    # 2 + 4. Normalise to NFC, strip, repair mojibake
    repaired = [n for ns in names.values() for n in ns if fix_mojibake(n) != n]
    cleaned = {s: [clean(n) for n in ns] for s, ns in names.items()}
    print("repaired mojibake:", [(n, clean(n)) for n in repaired])
    assert cleaned["webshop"][2] == "Café Owner"
    # NFD "Björk" from the app now equals the NFC one from the till, byte for byte
    assert cleaned["app"][1] == cleaned["till"][2] == "Björk Lund"
    assert names["app"][1] != "Björk Lund"  # before normalising it did not

    # 3. Group the same person across sources by match key
    groups: dict[str, list[tuple[str, str]]] = {}
    for source, ns in cleaned.items():
        for n in ns:
            groups.setdefault(match_key(n), []).append((source, n))
    print("\nsame person in more than one source:")
    for key, hits in sorted(groups.items()):
        if len({s for s, _ in hits}) > 1:
            print(f"  {key:12} <- " + ", ".join(f"{s}: {n!r}" for s, n in hits))
    print("only in one source:", sorted(k for k, h in groups.items() if len({s for s, _ in h}) == 1))

    multi = {k for k, h in groups.items() if len({s for s, _ in h}) > 1}
    assert multi == {"zoe jansen", "jose martin", "rene faber", "bjork lund"}
    print("\nall checks passed")
