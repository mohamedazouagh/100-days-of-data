import pandas as pd

# A small fictional export of webshop product names, typed in by hand over the years
products = pd.DataFrame({
    "name": ["  Oat Milk 1L", "oat milk 1l ", "ALMOND milk 1 L", "Soy Yoghurt 500g",
             "soy  yoghurt 500 g", None, "Rice Drink 1.5L"],
    "code": ["DRK-0012", "drk-0012", "DRK-0031", "YOG-0007", "yog-7", "DRK-0040", "DRK-0055"],
})
print(products.dtypes.to_dict())   # text columns get the string dtype
print()

# 1. Every Python str method has a vectorised twin under .str; missing values stay missing
clean = (
    products["name"]
    .str.strip()
    .str.lower()
    .str.replace(r"\s+", " ", regex=True)     # collapse runs of spaces
)
print(clean.tolist())
print()

# 2. Normalise the unit spelling with a regex: "1 l" / "1l" -> "1l", "500 g" -> "500g"
clean = clean.str.replace(r"(\d)\s*(l|g)\b", r"\1\2", regex=True)
print(clean.value_counts(dropna=False))
print()

# 3. .str.contains gives a boolean mask; decide what missing names count as with na=
print(clean.str.contains("milk", na=False).tolist())
print()

# 4. .str.split(expand=True) turns parts into columns; .str.extract does it with a regex
print(products["code"].str.upper().str.split("-", expand=True))
parts = products["code"].str.extract(r"(?i)^(?P<group>[a-z]+)-(?P<num>\d+)$")
parts["group"] = parts["group"].str.upper()
parts["num"] = parts["num"].astype(int)     # "0012" and "12" become the same number
print(parts)
print()

# 5. The same product written two ways now gets one key
products["key"] = parts["group"] + "-" + parts["num"].astype(str).str.zfill(4)
print(products[["code", "key"]].drop_duplicates("key"))
print()

# 6. Lengths, slices and padding are vectorised too
print(clean.str.len().tolist())
print(clean.str[:3].tolist())
