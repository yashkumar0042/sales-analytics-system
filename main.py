from __future__ import annotations

import os
from typing import Any, Dict, List, Tuple

# Part 1
from utils.file_handler import parse_transactions, validate_and_filter, read_sales_data

# Part 2
from utils.data_processor import (
    calculate_total_revenue,
    region_wise_sales,
    top_selling_products,
    customer_analysis,
    find_peak_sales_day,
    low_performing_products,
)

# Part 3
from utils.api_handler import fetch_all_products, create_product_mapping, enrich_sales_data, save_enriched_data

# Part 4
from utils.report_generator import generate_sales_report


def _amount(t: Dict[str, Any]) -> float:
    try:
        return float(t.get("Quantity", 0)) * float(t.get("UnitPrice", 0))
    except Exception:
        return 0.0


def main() -> None:
    """
    Main execution function

    Workflow:
    1. Print welcome message
    2. Read sales data file (handle encoding)
    3. Parse and clean transactions
    4. Display filter options to user
    5. If yes, ask for filter criteria and apply
    6. Validate transactions
    7. Display validation summary
    8. Perform all data analyses (Part 2)
    9. Fetch products from API
    10. Enrich sales data with API info
    11. Save enriched data to file
    12. Generate comprehensive report
    13. Print success message with file locations

    Error Handling:
    - Wrap entire process in try-except
    - Display user-friendly error messages
    - Don't let program crash on errors
    """

    try:
        print("=" * 35)
        print("SALES ANALYTICS SYSTEM")
        print("=" * 35)
        print()

        # 1) Read sales data
        print("[1/10] Reading sales data...")
        raw_lines = read_sales_data("data/sales_data.txt")
        print(f"Successfully read {len(raw_lines)} transactions")
        print()

        # 2) Parse and clean
        print("[2/10] Parsing and cleaning data...")
        transactions = parse_transactions(raw_lines)
        print(f"Parsed {len(transactions)} records")
        print()

        # 3) Filter options display
        print("[3/10] Filter Options Available:")
        regions = sorted({t.get("Region") for t in transactions if t.get("Region")})
        amounts = [_amount(t) for t in transactions]
        min_amt = min(amounts) if amounts else 0.0
        max_amt = max(amounts) if amounts else 0.0
        print(f"Regions: {', '.join(regions) if regions else 'N/A'}")
        print(f"Amount Range: ₹{min_amt:,.0f} - ₹{max_amt:,.0f}")
        print()

        apply_filter = input("Do you want to filter data? (y/n): ").strip().lower()

        region_filter = None
        min_amount = None
        max_amount = None

        if apply_filter == "y":
            # Ask filters
            r = input("Enter region to filter (or press Enter to skip): ").strip()
            region_filter = r if r else None

            mn = input("Enter minimum amount (or press Enter to skip): ").strip()
            if mn:
                try:
                    min_amount = float(mn)
                except ValueError:
                    min_amount = None

            mx = input("Enter maximum amount (or press Enter to skip): ").strip()
            if mx:
                try:
                    max_amount = float(mx)
                except ValueError:
                    max_amount = None

        # 4) Validate + filter
        print()
        print("[4/10] Validating transactions...")
        valid_transactions, invalid_count, filter_summary = validate_and_filter(
            transactions,
            region=region_filter,
            min_amount=min_amount,
            max_amount=max_amount,
        )
        print(f"Valid: {len(valid_transactions)} | Invalid: {invalid_count}")
        print()

        # 5) Analyze sales data (call all Part 2 functions)
        print("[5/10] Analyzing sales data...")
        _ = calculate_total_revenue(valid_transactions)
        _ = region_wise_sales(valid_transactions)
        _ = top_selling_products(valid_transactions, n=5)
        _ = customer_analysis(valid_transactions)
        _ = find_peak_sales_day(valid_transactions)
        _ = low_performing_products(valid_transactions, threshold=10)
        print("Analysis complete")
        print()

        # 6) Fetch product data from API
        print("[6/10] Fetching product data from API...")
        api_products = fetch_all_products()
        print(f"Fetched {len(api_products)} products")
        print()

        # 7) Create mapping + Enrich
        print("[7/10] Enriching sales data...")
        product_mapping = create_product_mapping(api_products)
        enriched_transactions = enrich_sales_data(valid_transactions, product_mapping)

        enriched_ok = sum(1 for t in enriched_transactions if t.get("API_Match") is True)
        total_valid = len(valid_transactions) if valid_transactions else 0
        rate = (enriched_ok / total_valid * 100.0) if total_valid else 0.0
        print(f"Enriched {enriched_ok}/{total_valid} transactions ({rate:.1f}%)")
        print()

        # 8) Save enriched data
        print("[8/10] Saving enriched data...")
        os.makedirs("data", exist_ok=True)
        enriched_file = "data/enriched_sales_data.txt"
        save_enriched_data(enriched_transactions, filename=enriched_file)
        print(f"Saved to: {enriched_file}")
        print()

        # 9) Generate report
        print("[9/10] Generating report...")
        os.makedirs("output", exist_ok=True)
        report_file = "output/sales_report.txt"
        generate_sales_report(valid_transactions, enriched_transactions, output_file=report_file)
        print(f"Report saved to: {report_file}")
        print()

        # 10) Done
        print("[10/10] Process Complete!")
        print("=" * 35)

    except FileNotFoundError as e:
        print(f"File not found: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
