# Day 16 - Text encodings and Unicode normalisation

Files hold bytes; Python strings hold text. An *encoding* (UTF-8, cp1252, latin-1) is the rule
that turns one into the other. Most "weird characters" in data work come from reading bytes
with the wrong rule, or from two strings that look identical but are built from different
code points.

Key points:
- `str.encode("utf-8")` gives bytes, `bytes.decode("utf-8")` gives text. Always pass `encoding=` to `open()`;
  the default depends on the operating system.
- UTF-8 bytes decoded as cp1252 produce *mojibake* (`CafÃ©`); cp1252 bytes decoded as UTF-8 usually raise
  `UnicodeDecodeError`. Trying UTF-8 first and a legacy codec second is a reasonable fallback, because
  valid UTF-8 is rarely produced by accident.
- Excel's "CSV UTF-8" starts with a BOM (`EF BB BF`). Read it with `utf-8-sig`, or your first column is
  called `'﻿id'` and `row["id"]` fails.
- `"é"` can be one code point or `e` + a combining accent. They print the same but compare unequal;
  `unicodedata.normalize("NFC", s)` makes them equal. `NFKC` also folds full-width digits and ligatures.
- `casefold()` is the right tool for case-insensitive matching: `"Straße".casefold() == "strasse"`, `lower()` keeps the ß.
- Stripping accents (NFKD + drop combining marks) makes a good *search key*, but only for letters that decompose:
  `Æ` and `ø` are separate letters and stay as they are. Keep the original text for display.

Run it: `python day16/lesson.py`

## Exercise
`solution.py` holds a small export of customer names as raw bytes from three sources: a UTF-8 file with a BOM,
a cp1252 file and a UTF-8 file whose names use combining accents.
1. decode each source with the right codec (detect it with the UTF-8-then-cp1252 fallback, BOM handled);
2. normalise every name to NFC and strip surrounding whitespace;
3. build a case- and accent-insensitive key and report which names are the same person across sources;
4. find and repair names that were already mojibake'd before export (`Ã©` style) by re-encoding as cp1252 and decoding as UTF-8.
Solution: `day16/solution.py`.
