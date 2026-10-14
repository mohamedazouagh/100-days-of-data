import codecs
import csv
import io
import unicodedata

if __name__ == "__main__":
    # 1. str is text, bytes is an encoding of that text
    name = "Café Zoë"
    utf8, cp1252 = name.encode("utf-8"), name.encode("cp1252")
    print("utf-8  :", utf8, len(utf8), "bytes")
    print("cp1252 :", cp1252, len(cp1252), "bytes")

    # 2. Decoding with the wrong codec: mojibake or an error
    print("utf-8 bytes read as cp1252:", utf8.decode("cp1252"))
    try:
        cp1252.decode("utf-8")
    except UnicodeDecodeError as e:
        print("UnicodeDecodeError:", e.reason, "at byte", e.start)

    # 3. A simple fallback: try utf-8 first, then a legacy codec
    def decode_any(raw: bytes) -> tuple[str, str]:
        for enc in ("utf-8-sig", "cp1252"):
            try:
                return raw.decode(enc), enc
            except UnicodeDecodeError:
                continue
        return raw.decode("utf-8", errors="replace"), "utf-8 (replaced)"

    print("decode_any:", decode_any(utf8), decode_any(cp1252))

    # 4. The BOM: Excel's "CSV UTF-8" starts with EF BB BF
    raw = codecs.BOM_UTF8 + "id,city\n1,Breda\n".encode("utf-8")
    plain = next(csv.DictReader(io.StringIO(raw.decode("utf-8"))))
    sig = next(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    print("utf-8 keys    :", list(plain))
    print("utf-8-sig keys:", list(sig))

    # 5. Same look, different code points: normalise before comparing
    composed, decomposed = "é", "é"
    print("equal?", composed == decomposed, "| lengths:", len(composed), len(decomposed))
    nfc = unicodedata.normalize("NFC", decomposed)
    print("after NFC equal?", composed == nfc)

    # 6. NFKC also folds "compatibility" forms like full-width digits and ligatures
    print("NFKC:", unicodedata.normalize("NFKC", "１２３ ﬁle"))

    # 7. casefold() is a stronger lower() for case-insensitive matching
    print("lower   :", "Straße".lower(), "| casefold:", "Straße".casefold())
    print("match?  ", "STRASSE".lower() == "Straße".lower(), "vs", "STRASSE".casefold() == "Straße".casefold())

    # 8. Stripping accents for a search key (keeps the original for display)
    def ascii_key(s: str) -> str:
        nfkd = unicodedata.normalize("NFKD", s)
        return "".join(c for c in nfkd if not unicodedata.combining(c)).casefold()

    print("search keys:", [ascii_key(s) for s in ("Zoë", "José", "Ærø")])
