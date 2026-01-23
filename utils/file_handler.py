from typing import List, Dict, Tuple, Optional

def read_sales_data(filename: str) -> List[str]:
    """
    Reads sales data from file handling encoding issues
    """
    encodings = ["utf-8", "latin-1", "cp1252"]
    last_error = None

    for enc in encodings:
        try:
            with open(filename, "r", encoding=enc) as f:
                lines = f.read().splitlines()

            # remove empty lines
            lines = [ln.strip() for ln in lines if ln.strip()]

            # skip header if present
            if lines and lines[0].lower().startswith("transactionid|date|productid"):
                lines = lines[1:]

            return lines

        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {filename}")
        except UnicodeDecodeError as e:
            last_error = e
            continue

    # if all encodings fail
    raise UnicodeDecodeError(
        "read_sales_data",b"",0,1,f"Unable to decode file using encodings {encodings}. Last error: {last_error}",
    )


def _to_int(value: str) -> Optional[int]:
    value = (value or "").strip()
    if value == "":
        return None
    value = value.replace(",", "")  # handle "1,500"
    try:
        return int(value)
    except ValueError:
        return None


def _to_float(value: str) -> Optional[float]:
    value = (value or "").strip()
    if value == "":
        return None
    value = value.replace(",", "")  # handle "1,916"
    try:
        return float(value)
    except ValueError:
        return None


def parse_transactions(raw_lines: List[str]) -> List[Dict]:
    """
    Parses raw lines into clean list of dictionaries
    """
    parsed: List[Dict] = []

    for line in raw_lines:
        if not line or not line.strip():
            continue

        parts = [p.strip() for p in line.split("|")]

        # must have exactly 8 fields
        if len(parts) != 8:
            continue

        transaction_id, date, product_id, product_name, quantity, unit_price, customer_id, region = parts

        # handle commas within ProductName (remove or replace)
        product_name = product_name.replace(",", " ").strip()

        # convert types (and remove commas from numeric fields)
        qty_int = _to_int(quantity)
        price_float = _to_float(unit_price)

        # if conversion fails, skip
        if qty_int is None or price_float is None:
            continue

        parsed.append(
            {
                "TransactionID": transaction_id,
                "Date": date,
                "ProductID": product_id,
                "ProductName": product_name,
                "Quantity": qty_int,         # int type
                "UnitPrice": float(price_float),  # float type
                "CustomerID": customer_id,
                "Region": region,
            }
        )

    return parsed


def validate_and_filter(
    transactions: List[Dict],
    region: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
) -> Tuple[List[Dict], int, Dict]:
    """
    Validates transactions and applies optional filters.
    """

    total_input = len(transactions)
    invalid_count = 0
    valid: List[Dict] = []

    required_keys = ["TransactionID", "Date", "ProductID", "ProductName", "Quantity", "UnitPrice", "CustomerID", "Region"]

    # ---- validation pass ----
    for t in transactions:
        # all required fields present and non-empty
        if any(k not in t or t[k] in (None, "") for k in required_keys):
            invalid_count += 1
            continue

        # type & positive checks
        if not isinstance(t["Quantity"], int) or t["Quantity"] <= 0:
            invalid_count += 1
            continue
        if not isinstance(t["UnitPrice"], (int, float)) or float(t["UnitPrice"]) <= 0:
            invalid_count += 1
            continue

        # ID rules
        if not str(t["TransactionID"]).startswith("T"):
            invalid_count += 1
            continue
        if not str(t["ProductID"]).startswith("P"):
            invalid_count += 1
            continue
        if not str(t["CustomerID"]).startswith("C"):
            invalid_count += 1
            continue

        valid.append(t)

    # ---- display available options before filtering (as screenshot asks) ----
    regions_available = sorted({v["Region"] for v in valid if v.get("Region")})
    amounts = [v["Quantity"] * float(v["UnitPrice"]) for v in valid]
    if amounts:
        amt_min, amt_max = min(amounts), max(amounts)
    else:
        amt_min, amt_max = 0.0, 0.0

    print(f"Available regions: {regions_available}")
    print(f"Transaction amount range: min={amt_min}, max={amt_max}")

    # ---- filtering pass ----
    filtered = valid
    filtered_by_region = 0
    filtered_by_amount = 0

    if region is not None:
        before = len(filtered)
        filtered = [t for t in filtered if t.get("Region") == region]
        filtered_by_region = before - len(filtered)
        print(f"After region filter ({region}): {len(filtered)} records")

    if min_amount is not None or max_amount is not None:
        before = len(filtered)

        def in_amount_range(t: Dict) -> bool:
            amt = t["Quantity"] * float(t["UnitPrice"])
            if min_amount is not None and amt < float(min_amount):
                return False
            if max_amount is not None and amt > float(max_amount):
                return False
            return True

        filtered = [t for t in filtered if in_amount_range(t)]
        filtered_by_amount = before - len(filtered)
        print(f"After amount filter (min={min_amount}, max={max_amount}): {len(filtered)} records")

    filter_summary = {
        "total_input": total_input,
        "invalid": invalid_count,
        "filtered_by_region": filtered_by_region,
        "filtered_by_amount": filtered_by_amount,
        "final_count": len(filtered),
    }

    return filtered, invalid_count, filter_summary
