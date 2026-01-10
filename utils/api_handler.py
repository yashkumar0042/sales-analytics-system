def enrich_products(records):
    product_map = {
        "P101": "Laptop",
        "P102": "Mouse",
        "P103": "Keyboard",
        "P104": "Monitor",
        "P105": "Webcam",
        "P106": "Headphones",
        "P107": "USB Cable",
        "P108": "Hard Drive",
        "P109": "Wireless Mouse",
        "P110": "Charger"
    }

    for r in records:
        r["ProductCategory"] = product_map.get(r["ProductID"], "Other")

    return records
