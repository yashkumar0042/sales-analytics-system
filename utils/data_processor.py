import pandas as pd

def _is_missing(val) -> bool:
    """True if val is NaN, None, empty, or only spaces."""
    if pd.isna(val):
        return True
    if str(val).strip() == "":
        return True
    return False

def clean_and_validate(df):
    total_records = len(df)
    invalid_count = 0
    cleaned_rows = []

    for _, row in df.iterrows():

        # --- Parse UnitPrice safely (remove commas) ---
        try:
            unit_price = float(str(row["UnitPrice"]).replace(",", "").strip())
        except:
            invalid_count += 1
            continue

        # --- Parse Quantity safely ---
        try:
            quantity = int(str(row["Quantity"]).strip())
        except:
            invalid_count += 1
            continue

        # --- Validation (as per Masai screenshots) ---
        if not str(row["TransactionID"]).startswith("T"):
            invalid_count += 1
            continue

        if _is_missing(row["CustomerID"]) or _is_missing(row["Region"]):
            invalid_count += 1
            continue

        if quantity <= 0 or unit_price <= 0:
            invalid_count += 1
            continue

        # --- Cleaning rules (KEEP valid rows) ---
        row["ProductName"] = str(row["ProductName"]).replace(",", "")
        row["UnitPrice"] = unit_price
        row["Quantity"] = quantity

        cleaned_rows.append(row)

    valid_count = len(cleaned_rows)

    # --- REQUIRED OUTPUT ---
    print(f"Total records parsed: {total_records}")
    print(f"Invalid records removed: {invalid_count}")
    print(f"Valid records after cleaning: {valid_count}")

    return cleaned_rows
