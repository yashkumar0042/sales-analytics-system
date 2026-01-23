from typing import Any, Dict, List, Optional
import os

import requests


BASE_URL = "https://dummyjson.com/products"


def fetch_all_products() -> List[Dict[str, Any]]:
    """
    Fetches all products from DummyJSON API
    Returns: list of product dictionaries
    """
    try:
        url = f"{BASE_URL}?limit=100"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        # DummyJSON returns {"products": [...], "total": ..., ...}
        products = data.get("products", [])
        if not isinstance(products, list):
            print("API fetch failed: invalid response format")
            return []

        print(f"Successfully fetched {len(products)} products from API")
        return products

    except Exception as e:
        print(f"API fetch failed: {e}")
        return []


def create_product_mapping(api_products: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    """
    Creates a mapping of product IDs to product info
    Parameters: api_products from fetch_all_products()
    Returns: dictionary mapping product IDs to info
    """
    mapping: Dict[int, Dict[str, Any]] = {}

    for p in api_products:
        try:
            pid = int(p.get("id"))
        except Exception:
            continue

        mapping[pid] = {
            "title": p.get("title"),
            "category": p.get("category"),
            "brand": p.get("brand"),
            "rating": p.get("rating"),
        }

    return mapping


def _extract_numeric_product_id(product_id_str: Optional[str]) -> Optional[int]:
    """
    Extract numeric ID from ProductID string
    """
    if not product_id_str:
        return None

    s = str(product_id_str).strip()
    if not s:
        return None

    # keep only digits
    digits = "".join(ch for ch in s if ch.isdigit())
    if not digits:
        return None

    try:
        return int(digits)
    except Exception:
        return None


def enrich_sales_data(
    transactions: List[Dict[str, Any]],
    product_mapping: Dict[int, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Enriches transaction data with API product information
    Parameters:
    Returns: list of enriched transaction dictionaries
    """
    enriched: List[Dict[str, Any]] = []

    for t in transactions:
        # copy original transaction
        row = dict(t)

        try:
            numeric_id = _extract_numeric_product_id(row.get("ProductID"))
            api_info = product_mapping.get(numeric_id) if numeric_id is not None else None

            if api_info:
                row["API_Category"] = api_info.get("category")
                row["API_Brand"] = api_info.get("brand")
                row["API_Rating"] = api_info.get("rating")
                row["API_Match"] = True
            else:
                row["API_Category"] = None
                row["API_Brand"] = None
                row["API_Rating"] = None
                row["API_Match"] = False

        except Exception:
            # any unexpected issue => mark no match
            row["API_Category"] = None
            row["API_Brand"] = None
            row["API_Rating"] = None
            row["API_Match"] = False

        enriched.append(row)

    # Save to file as required
    save_enriched_data(enriched, filename="data/enriched_sales_data.txt")

    return enriched


def save_enriched_data(
    enriched_transactions: List[Dict[str, Any]],
    filename: str = "data/enriched_sales_data.txt",
) -> None:
    """
    Saves enriched transactions back to file
    """
    # ensure folder exists
    folder = os.path.dirname(filename)
    if folder:
        os.makedirs(folder, exist_ok=True)

    header_fields = [
        "TransactionID",
        "Date",
        "ProductID",
        "ProductName",
        "Quantity",
        "UnitPrice",
        "CustomerID",
        "Region",
        "API_Category",
        "API_Brand",
        "API_Rating",
        "API_Match",
    ]

    def fmt(v: Any) -> str:
        if v is None:
            return ""
        if isinstance(v, bool):
            return "True" if v else "False"
        return str(v)

    with open(filename, "w", encoding="utf-8") as f:
        f.write("|".join(header_fields) + "\n")
        for t in enriched_transactions:
            row = [fmt(t.get(col)) for col in header_fields]
            f.write("|".join(row) + "\n")
