import re
from typing import Optional


def extract_fields(text: str) -> dict:
    """
    Extract key invoice fields from text.
    Returns dict of all detected fields.
    """
    return {
        "vendor_name": _extract_vendor(text),
        "invoice_number": _extract_invoice_number(text),
        "invoice_date": _extract_date(text),
        "due_date": _extract_due_date(text),
        "subtotal": _extract_amount(text, ["subtotal", "sub total", "sub-total"]),
        "tax_amount": _extract_tax(text),
        "grand_total": _extract_grand_total(text),
        "line_items": _extract_line_items(text),
        "currency": _detect_currency(text),
        "gstin": _extract_gstin(text),
        "po_number": _extract_po_number(text),
    }


def _extract_vendor(text: str) -> Optional[str]:
    lines = text.strip().split("\n")
    for line in lines[:8]:
        line = line.strip()
        if len(line) > 3 and not re.match(r"^\d", line):
            # Skip lines that look like addresses or dates
            if not re.search(r"\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}", line):
                return line
    return None


def _extract_invoice_number(text: str) -> Optional[str]:
    patterns = [
        r"inv(?:oice)?[\s#\-no:\.]+([A-Z0-9\-\/]+)",
        r"invoice\s*(?:no\.?|number|#)\s*:?\s*([A-Z0-9\-\/]+)",
        r"bill\s*(?:no\.?|number|#)\s*:?\s*([A-Z0-9\-\/]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def _extract_date(text: str) -> Optional[str]:
    patterns = [
        r"(?:invoice\s*date|date\s*of\s*issue|date)\s*:?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
        r"(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
        r"(\d{4}[\/\-]\d{2}[\/\-]\d{2})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def _extract_due_date(text: str) -> Optional[str]:
    pattern = r"(?:due\s*date|payment\s*due|pay\s*by)\s*:?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})"
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else None


def _extract_amount(text: str, keywords: list) -> Optional[float]:
    for kw in keywords:
        pattern = rf"{kw}\s*:?\s*[₹$€£]?\s*([\d,]+\.?\d*)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return _clean_amount(match.group(1))
    return None


def _extract_tax(text: str) -> Optional[float]:
    patterns = [
        r"(?:total\s*)?(?:gst|vat|tax|cgst|sgst|igst)\s*(?:@[\d\.]+%?)?\s*:?\s*[₹$€£]?\s*([\d,]+\.?\d*)",
    ]
    total_tax = 0.0
    found = False
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            try:
                total_tax += _clean_amount(match.group(1)) or 0
                found = True
            except:
                pass
    return round(total_tax, 2) if found else None


def _extract_grand_total(text: str) -> Optional[float]:
    keywords = ["grand total", "total amount", "amount due", "balance due", "net payable", "total payable", "total"]
    for kw in keywords:
        pattern = rf"{kw}\s*:?\s*[₹$€£]?\s*([\d,]+\.?\d*)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return _clean_amount(match.group(1))
    return None


def _extract_line_items(text: str) -> list:
    items = []
    # Pattern: description | qty | unit price | total
    pattern = r"([A-Za-z][A-Za-z\s\-\/]{2,40})\s+(\d+)\s+([\d,]+\.?\d*)\s+([\d,]+\.?\d*)"
    for match in re.finditer(pattern, text):
        desc, qty, unit_price, total = match.groups()
        items.append({
            "description": desc.strip(),
            "quantity": int(qty),
            "unit_price": _clean_amount(unit_price),
            "total": _clean_amount(total)
        })
    return items[:20]  # cap at 20 items


def _detect_currency(text: str) -> str:
    if "₹" in text or "inr" in text.lower() or "rupee" in text.lower():
        return "INR"
    elif "$" in text or "usd" in text.lower():
        return "USD"
    elif "€" in text or "eur" in text.lower():
        return "EUR"
    elif "£" in text or "gbp" in text.lower():
        return "GBP"
    return "INR"  # default for Indian invoices


def _extract_gstin(text: str) -> Optional[str]:
    pattern = r"\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}\b"
    match = re.search(pattern, text)
    return match.group(0) if match else None


def _extract_po_number(text: str) -> Optional[str]:
    pattern = r"(?:po|purchase\s*order)\s*(?:no\.?|number|#)?\s*:?\s*([A-Z0-9\-\/]+)"
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else None


def _clean_amount(value: str) -> Optional[float]:
    try:
        return float(value.replace(",", "").strip())
    except:
        return None