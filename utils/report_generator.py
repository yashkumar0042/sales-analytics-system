from __future__ import annotations

from typing import Any, Dict, List, Tuple
from datetime import datetime
import os


def generate_sales_report(
    transactions: List[Dict[str, Any]],
    enriched_transactions: List[Dict[str, Any]],
    output_file: str = "output/sales_report.txt",
) -> None:
    """
    Generates a comprehensive formatted text report.

    Report Must Include (in this order):
      1. HEADER
      2. OVERALL SUMMARY
      3. REGION-WISE PERFORMANCE
      4. TOP 5 PRODUCTS
      5. TOP 5 CUSTOMERS
      6. DAILY SALES TREND
      7. PRODUCT PERFORMANCE ANALYSIS
      8. API ENRICHMENT SUMMARY

    Writes to: output/sales_report.txt (default)
    """

    # ---------------- Helpers ----------------
    def money(x: float) -> str:
        # Rupee symbol shown in sample; keep it.
        return f"₹{x:,.2f}"

    def pct(x: float) -> str:
        return f"{x:.2f}%"

    def amount(t: Dict[str, Any]) -> float:
        try:
            return float(t.get("Quantity", 0)) * float(t.get("UnitPrice", 0))
        except Exception:
            return 0.0

    def safe_str(v: Any) -> str:
        return "" if v is None else str(v)

    def line(char: str = "=", n: int = 60) -> str:
        return char * n

    def write_table(headers: List[str], rows: List[List[str]], widths: List[int]) -> str:
        """
        Simple fixed-width table generator (left for text cols, right for numeric cols).
        We'll right-align columns that look numeric by header name.
        """
        numeric_headers = {"Sales", "Revenue", "Total Spent", "Qty", "Quantity Sold", "% of Total", "Transactions", "Order Count", "Unique Customers"}
        out = []

        # header
        header_line = "  ".join(
            (h.ljust(w) if h not in numeric_headers else h.rjust(w))
            for h, w in zip(headers, widths)
        )
        out.append(header_line)
        out.append("-" * len(header_line))

        for r in rows:
            row_line = "  ".join(
                (c.ljust(w) if headers[i] not in numeric_headers else c.rjust(w))
                for i, (c, w) in enumerate(zip(r, widths))
            )
            out.append(row_line)

        return "\n".join(out)

    # ---------------- Core computations ----------------
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_records = len(transactions)

    total_revenue = sum(amount(t) for t in transactions)
    total_tx = len(transactions)
    avg_order_value = (total_revenue / total_tx) if total_tx else 0.0

    dates = sorted({t.get("Date") for t in transactions if t.get("Date")})
    date_range = (dates[0], dates[-1]) if dates else ("", "")

    # Region-wise
    region_stats: Dict[str, Dict[str, Any]] = {}
    for t in transactions:
        r = t.get("Region")
        if not r:
            continue
        region_stats.setdefault(r, {"sales": 0.0, "count": 0})
        region_stats[r]["sales"] += amount(t)
        region_stats[r]["count"] += 1

    region_rows_sorted = sorted(region_stats.items(), key=lambda kv: kv[1]["sales"], reverse=True)

    # Top products (by total quantity sold)
    prod_agg: Dict[str, Dict[str, float]] = {}
    for t in transactions:
        p = t.get("ProductName")
        if not p:
            continue
        prod_agg.setdefault(p, {"qty": 0.0, "rev": 0.0})
        try:
            prod_agg[p]["qty"] += int(t.get("Quantity", 0))
        except Exception:
            continue
        prod_agg[p]["rev"] += amount(t)

    top_products = sorted(
        [(p, int(v["qty"]), float(v["rev"])) for p, v in prod_agg.items()],
        key=lambda x: (x[1], x[2]),
        reverse=True,
    )[:5]

    # Customer analysis (sorted by total_spent desc)
    cust_agg: Dict[str, Dict[str, Any]] = {}
    for t in transactions:
        cid = t.get("CustomerID")
        if not cid:
            continue
        cust_agg.setdefault(cid, {"spent": 0.0, "count": 0})
        cust_agg[cid]["spent"] += amount(t)
        cust_agg[cid]["count"] += 1

    top_customers = sorted(
        [(cid, float(v["spent"]), int(v["count"])) for cid, v in cust_agg.items()],
        key=lambda x: x[1],
        reverse=True,
    )[:5]

    # Daily sales trend: Date, Revenue, Transactions, Unique Customers
    daily: Dict[str, Dict[str, Any]] = {}
    for t in transactions:
        d = t.get("Date")
        if not d:
            continue
        daily.setdefault(d, {"rev": 0.0, "tx": 0, "customers": set()})
        daily[d]["rev"] += amount(t)
        daily[d]["tx"] += 1
        cid = t.get("CustomerID")
        if cid:
            daily[d]["customers"].add(cid)

    daily_rows_sorted = sorted(daily.items(), key=lambda kv: kv[0])

    # Best selling day (peak revenue)
    best_day = ("", 0.0, 0)
    for d, v in daily.items():
        rev = float(v["rev"])
        txc = int(v["tx"])
        if rev > best_day[1]:
            best_day = (d, rev, txc)

    # Low performing products (total qty < 10)
    low_threshold = 10
    low_products = sorted(
        [(p, int(v["qty"]), float(v["rev"])) for p, v in prod_agg.items() if int(v["qty"]) < low_threshold],
        key=lambda x: x[1],
    )

    # Avg transaction value per region
    avg_tx_value_region = []
    for r, v in region_rows_sorted:
        cnt = v["count"]
        avgv = (v["sales"] / cnt) if cnt else 0.0
        avg_tx_value_region.append((r, avgv))

    # API enrichment summary (from enriched_transactions)
    # Count matches by transaction
    match_count = 0
    total_enriched_records = len(enriched_transactions)
    not_enriched_products = set()

    for t in enriched_transactions:
        if t.get("API_Match") is True:
            match_count += 1
        else:
            # list products that couldn't be enriched (unique names preferred)
            pname = t.get("ProductName") or t.get("ProductID")
            if pname:
                not_enriched_products.add(str(pname))

    success_rate = (match_count / total_enriched_records * 100.0) if total_enriched_records else 0.0
    not_enriched_list = sorted(not_enriched_products)

    # ---------------- Build report text ----------------
    parts: List[str] = []

    # 1) HEADER
    parts.append(line("="))
    parts.append("SALES ANALYTICS REPORT".center(60))
    parts.append(f"Generated: {generated_at}".center(60))
    parts.append(f"Records Processed: {total_records}".center(60))
    parts.append(line("="))
    parts.append("")

    # 2) OVERALL SUMMARY
    parts.append("OVERALL SUMMARY")
    parts.append(line("-", 40))
    parts.append(f"Total Revenue:        {money(total_revenue)}")
    parts.append(f"Total Transactions:   {total_tx}")
    parts.append(f"Average Order Value:  {money(avg_order_value)}")
    if date_range[0] and date_range[1]:
        parts.append(f"Date Range:           {date_range[0]} to {date_range[1]}")
    else:
        parts.append("Date Range:           ")
    parts.append("")

    # 3) REGION-WISE PERFORMANCE
    parts.append("REGION-WISE PERFORMANCE")
    parts.append(line("-", 40))

    region_table_rows: List[List[str]] = []
    for r, v in region_rows_sorted:
        sales = float(v["sales"])
        cnt = int(v["count"])
        percent_total = (sales / total_revenue * 100.0) if total_revenue else 0.0
        region_table_rows.append([r, money(sales), pct(percent_total), str(cnt)])

    region_headers = ["Region", "Sales", "% of Total", "Transactions"]
    region_widths = [10, 14, 10, 12]
    parts.append(write_table(region_headers, region_table_rows, region_widths))
    parts.append("")

    # 4) TOP 5 PRODUCTS
    parts.append("TOP 5 PRODUCTS")
    parts.append(line("-", 40))
    prod_rows = []
    for i, (name, qty, rev) in enumerate(top_products, start=1):
        prod_rows.append([str(i), name, str(qty), money(rev)])

    prod_headers = ["Rank", "Product Name", "Quantity Sold", "Revenue"]
    prod_widths = [6, 20, 14, 14]
    parts.append(write_table(prod_headers, prod_rows, prod_widths))
    parts.append("")

    # 5) TOP 5 CUSTOMERS
    parts.append("TOP 5 CUSTOMERS")
    parts.append(line("-", 40))
    cust_rows = []
    for i, (cid, spent, cnt) in enumerate(top_customers, start=1):
        cust_rows.append([str(i), cid, money(spent), str(cnt)])

    cust_headers = ["Rank", "Customer ID", "Total Spent", "Order Count"]
    cust_widths = [6, 14, 14, 12]
    parts.append(write_table(cust_headers, cust_rows, cust_widths))
    parts.append("")

    # 6) DAILY SALES TREND
    parts.append("DAILY SALES TREND")
    parts.append(line("-", 40))
    daily_rows = []
    for d, v in daily_rows_sorted:
        daily_rows.append([d, money(float(v["rev"])), str(int(v["tx"])), str(len(v["customers"]))])

    daily_headers = ["Date", "Revenue", "Transactions", "Unique Customers"]
    daily_widths = [12, 14, 12, 16]
    parts.append(write_table(daily_headers, daily_rows, daily_widths))
    parts.append("")

    # 7) PRODUCT PERFORMANCE ANALYSIS
    parts.append("PRODUCT PERFORMANCE ANALYSIS")
    parts.append(line("-", 40))
    parts.append(f"Best Selling Day: {best_day[0]}  | Revenue: {money(best_day[1])}  | Transactions: {best_day[2]}")
    parts.append("")
    parts.append(f"Low Performing Products (Quantity < {low_threshold}):")
    if low_products:
        for p, q, r in low_products:
            parts.append(f"- {p}: Qty={q}, Revenue={money(r)}")
    else:
        parts.append("- None")
    parts.append("")
    parts.append("Average Transaction Value per Region:")
    for r, avgv in avg_tx_value_region:
        parts.append(f"- {r}: {money(avgv)}")
    parts.append("")

    # 8) API ENRICHMENT SUMMARY
    parts.append("API ENRICHMENT SUMMARY")
    parts.append(line("-", 40))
    parts.append(f"Total transactions enriched: {match_count} / {total_enriched_records}")
    parts.append(f"Success rate: {pct(success_rate)}")
    parts.append("Products that couldn't be enriched:")
    if not_enriched_list:
        # keep it readable in text report
        for p in not_enriched_list[:50]:
            parts.append(f"- {p}")
        if len(not_enriched_list) > 50:
            parts.append(f"... and {len(not_enriched_list) - 50} more")
    else:
        parts.append("- None")
    parts.append("")

    report_text = "\n".join(parts)

    # ---------------- Write to file ----------------
    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report_text)
