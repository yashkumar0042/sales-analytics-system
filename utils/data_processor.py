import re

def clean_and_validate(df):
    total_records = len(df)
    invalid_count = 0
    cleaned_rows = []

    for _, row in df.iterrows():
        # Validation rules
        if (
            not str(row["TransactionID"]).startswith("T") or
            not row["CustomerID"] or
            not row["Region"] or
            row["Quantity"] <= 0 or
            row["UnitPrice"] <= 0
        ):
            invalid_count += 1
            continue

        # Clean ProductName commas
        row["ProductName"] = str(row["ProductName"]).replace(",", "")

        # Clean UnitPrice commas
        row["UnitPrice"] = float(str(row["UnitPrice"]).replace(",", ""))

        cleaned_rows.append(row)

    valid_count = len(cleaned_rows)

    print(f"Total records parsed: {total_records}")
    print(f"Invalid records removed: {invalid_count}")
    print(f"Valid records after cleaning: {valid_count}")

    return cleaned_rows
