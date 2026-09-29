from lesson import raw_prices


def parse_price(text: str) -> float | None:
    """Turn a hand-typed price into a float; None for empty / 'n/a'."""
    t = text.strip().replace("€", "").replace(" ", "")
    if t.lower() in ("", "n/a"):
        return None
    if "," in t:
        # European format: dots are thousands separators, comma is the decimal point
        t = t.replace(".", "").replace(",", ".")
    return float(t)


if __name__ == "__main__":
    prices = [p for p in (parse_price(r) for r in raw_prices) if p is not None]
    print(prices)
    print(f"average: {round(sum(prices) / len(prices), 2)}")
