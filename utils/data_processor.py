from typing import Dict, List, Tuple, Any


def _amount(t: Dict[str, Any]) -> float:
    """Helper: compute revenue for a single transaction safely."""
    try:
        return float(t["Quantity"]) * float(t["UnitPrice"])
    except Exception:
        return 0.0


def calculate_total_revenue(transactions: List[Dict[str, Any]]) -> float:
    """
    Calculates total revenue from all transactions
    """
    total = 0.0
    for t in transactions:
        total += _amount(t)
    return total


def region_wise_sales(transactions: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
    """
    Analyzes sales by region
    """
    stats: Dict[str, Dict[str, float]] = {}

    for t in transactions:
        region = t.get("Region")
        if not region:
            continue

        if region not in stats:
            stats[region] = {"total_revenue": 0.0, "transaction_count": 0.0, "avg_order_value": 0.0}

        stats[region]["total_revenue"] += _amount(t)
        stats[region]["transaction_count"] += 1.0

    # finalize averages + make count int-like (but keep float-safe inside dict)
    for r in list(stats.keys()):
        cnt = int(stats[r]["transaction_count"])
        total_rev = stats[r]["total_revenue"]
        stats[r]["transaction_count"] = cnt
        stats[r]["avg_order_value"] = round(total_rev / cnt, 2) if cnt > 0 else 0.0

    return stats


def top_selling_products(transactions: List[Dict[str, Any]], n: int = 5) -> List[Tuple[str, int, float]]:
    """
    Finds top n products by total quantity sold
    """
    agg: Dict[str, Dict[str, float]] = {}

    for t in transactions:
        name = t.get("ProductName")
        if not name:
            continue

        if name not in agg:
            agg[name] = {"qty": 0.0, "rev": 0.0}

        try:
            agg[name]["qty"] += int(t["Quantity"])
        except Exception:
            continue

        agg[name]["rev"] += _amount(t)

    result: List[Tuple[str, int, float]] = []
    for name, v in agg.items():
        result.append((name, int(v["qty"]), float(v["rev"])))

    # sort by quantity desc (tie-breaker: revenue desc)
    result.sort(key=lambda x: (x[1], x[2]), reverse=True)

    return result[: max(0, int(n))]


def customer_analysis(transactions: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Analyzes customer purchase patterns
    """
    cust: Dict[str, Dict[str, Any]] = {}

    for t in transactions:
        cid = t.get("CustomerID")
        pname = t.get("ProductName")
        if not cid:
            continue

        if cid not in cust:
            cust[cid] = {
                "total_spent": 0.0,
                "purchase_count": 0,
                "avg_order_value": 0.0,
                "products_bought": [],
            }

        cust[cid]["total_spent"] += _amount(t)
        cust[cid]["purchase_count"] += 1

        if pname and pname not in cust[cid]["products_bought"]:
            cust[cid]["products_bought"].append(pname)

    # finalize avg + rounding
    for cid in list(cust.keys()):
        pc = cust[cid]["purchase_count"]
        total = cust[cid]["total_spent"]
        cust[cid]["total_spent"] = float(total)
        cust[cid]["avg_order_value"] = round(total / pc, 2) if pc > 0 else 0.0

    # sort by total_spent desc (keep insertion order)
    sorted_items = sorted(cust.items(), key=lambda kv: kv[1]["total_spent"], reverse=True)
    return {k: v for k, v in sorted_items}


def find_peak_sales_day(transactions: List[Dict[str, Any]]) -> Tuple[str, float, int]:
    """
    Identifies the date with highest revenue
    """
    per_day: Dict[str, Dict[str, float]] = {}

    for t in transactions:
        d = t.get("Date")
        if not d:
            continue

        if d not in per_day:
            per_day[d] = {"rev": 0.0, "cnt": 0.0}

        per_day[d]["rev"] += _amount(t)
        per_day[d]["cnt"] += 1.0

    if not per_day:
        return ("", 0.0, 0)

    # max by revenue, tie-breaker: higher count, then lexicographically earliest date
    best_date = None
    best_rev = -1.0
    best_cnt = -1

    for d, v in per_day.items():
        rev = float(v["rev"])
        cnt = int(v["cnt"])
        if (rev > best_rev) or (rev == best_rev and cnt > best_cnt) or (rev == best_rev and cnt == best_cnt and (best_date is None or d < best_date)):
            best_date = d
            best_rev = rev
            best_cnt = cnt

    return (best_date or "", float(best_rev), int(best_cnt))


def low_performing_products(transactions: List[Dict[str, Any]], threshold: int = 10) -> List[Tuple[str, int, float]]:
    """
    Identifies products with low sales
    """
    agg: Dict[str, Dict[str, float]] = {}

    for t in transactions:
        name = t.get("ProductName")
        if not name:
            continue

        if name not in agg:
            agg[name] = {"qty": 0.0, "rev": 0.0}

        try:
            agg[name]["qty"] += int(t["Quantity"])
        except Exception:
            continue

        agg[name]["rev"] += _amount(t)

    out: List[Tuple[str, int, float]] = []
    for name, v in agg.items():
        qty = int(v["qty"])
        if qty < int(threshold):
            out.append((name, qty, float(v["rev"])))

    out.sort(key=lambda x: x[1])  # quantity ascending
    return out
