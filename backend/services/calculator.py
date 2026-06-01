from typing import Optional


def validate_and_calculate(fields: dict) -> dict:
    """
    Validate invoice math and compute expected totals.
    Returns calculation result with match status.
    """
    line_items = fields.get("line_items", [])
    stated_subtotal = fields.get("subtotal")
    stated_tax = fields.get("tax_amount")
    stated_total = fields.get("grand_total")

    result = {
        "calculated_subtotal": None,
        "calculated_tax": None,
        "calculated_total": None,
        "subtotal_match": None,
        "total_match": None,
        "math_issues": [],
        "summary": {}
    }

    # Calculate subtotal from line items
    if line_items:
        line_total = sum(
            (item.get("quantity", 0) * item.get("unit_price", 0))
            for item in line_items
            if item.get("unit_price") is not None
        )
        result["calculated_subtotal"] = round(line_total, 2)

        # Check line item totals individually
        for i, item in enumerate(line_items):
            if item.get("quantity") and item.get("unit_price") and item.get("total"):
                expected = round(item["quantity"] * item["unit_price"], 2)
                actual = item["total"]
                if abs(expected - actual) > 0.5:
                    result["math_issues"].append(
                        f"Line item {i+1} ({item.get('description', 'unknown')}): "
                        f"Expected {expected}, found {actual}"
                    )

    # Compare subtotals
    if result["calculated_subtotal"] is not None and stated_subtotal is not None:
        result["subtotal_match"] = abs(result["calculated_subtotal"] - stated_subtotal) < 1.0
        if not result["subtotal_match"]:
            result["math_issues"].append(
                f"Subtotal mismatch: calculated {result['calculated_subtotal']}, "
                f"stated {stated_subtotal}"
            )

    # Use stated subtotal if calculated not available
    base = result["calculated_subtotal"] or stated_subtotal or 0

    # Calculate expected total
    tax = stated_tax or 0
    result["calculated_total"] = round(base + tax, 2)

    # Compare grand totals
    if stated_total is not None:
        result["total_match"] = abs(result["calculated_total"] - stated_total) < 1.0
        if not result["total_match"]:
            result["math_issues"].append(
                f"Grand total mismatch: calculated {result['calculated_total']}, "
                f"stated {stated_total}"
            )
    else:
        result["total_match"] = None

    # Build summary
    result["summary"] = {
        "subtotal": stated_subtotal or result["calculated_subtotal"],
        "tax": stated_tax or 0,
        "grand_total": stated_total or result["calculated_total"],
        "currency": fields.get("currency", "INR"),
        "line_item_count": len(line_items),
    }

    return result