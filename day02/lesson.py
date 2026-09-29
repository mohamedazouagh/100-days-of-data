raw_cities = ["  Breda", "breda ", "EINDHOVEN", "Tilburg", " tilburg  "]

raw_prices = ["€ 12,50", " 7.99 ", "1.020,00", "n/a", "€3", "", "24,95"]


def clean_city(name: str) -> str:
    return name.strip().title()


if __name__ == "__main__":
    cleaned = [clean_city(c) for c in raw_cities]
    print(cleaned)
    print(sorted(set(cleaned)))

    line = "2026-09-28;Breda;21,4"
    day, city, temp = line.split(";")
    print(day, city, float(temp.replace(",", ".")))
    print(" | ".join([day, city, temp]))
