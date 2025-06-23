def multiply_unit_price(entries):
    for entry in entries:
        if "unitPrice" in entry:
            entry["unitPrice"] *= 2
    return entries


# Example entries
entries = [
    {"model": "A", "variant": "V1", "qty": 1, "colors": ["Red"], "unitPrice": 100, "total": 100},
    {"model": "B", "variant": "V2", "qty": 2, "colors": ["Blue"], "unitPrice": 200, "total": 400},
]

# Process entries
multiply_unit_price(entries)

# Print updated entries
for entry in entries:
    print(entry)
