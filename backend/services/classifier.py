import re
from typing import Optional

# -----------------------------------------------------------
# Rule-based classifier (works without GPU / model download)
# Swap classify_invoice() body with LayoutLM version when ready
# -----------------------------------------------------------

INVOICE_KEYWORDS = [
    "invoice", "bill", "receipt", "tax invoice", "proforma",
    "invoice no", "invoice number", "inv no", "inv#", "order id", "order no",
    "bill to", "ship to", "sold to", "billing address", "shipping address",
    "subtotal", "sub total", "total amount", "grand total", "net amount",
    "amount due", "balance due", "payment due",
    "gst", "vat", "tax", "cgst", "sgst", "igst", "utgst",
    "hsn", "sac", "quantity", "qty", "unit price", "rate", "price",
    "purchase order", "po number", "vendor", "supplier", "pay by", "thank you"
]

NOT_INVOICE_KEYWORDS = [
    "curriculum vitae", "resume", "cover letter",
    "meeting minutes", "agenda", "contract agreement",
    "terms and conditions", "privacy policy",
    "job description", "offer letter", "salary slip",
    "powerpoint presentation", "slide deck"
]


def classify_invoice(text: str) -> dict:
    """
    Classify extracted text as valid / ambiguous / not_invoice.
    Returns classification result with confidence and issues list.
    """
    if not text or len(text.strip()) < 15:
        return {
            "status": "not_invoice",
            "confidence": 0.95,
            "issues": ["Document appears to be empty or unreadable"]
        }

    text_lower = text.lower()

    # Check for non-invoice documents (more strict now)
    not_invoice_hits = sum(1 for kw in NOT_INVOICE_KEYWORDS if kw in text_lower)
    if not_invoice_hits >= 3:
        return {
            "status": "not_invoice",
            "confidence": 0.90,
            "issues": ["Document identified as a non-invoice document type"]
        }

    # Count invoice keyword matches
    keyword_hits = sum(1 for kw in INVOICE_KEYWORDS if kw in text_lower)
    keyword_score = min(keyword_hits / 6, 1.0)  # slightly lowered denominator

    # Check required fields
    issues = _detect_issues(text, text_lower)

    # Determine status
    if keyword_score >= 0.5 and len(issues) <= 1:
        return {
            "status": "valid",
            "confidence": round(0.70 + keyword_score * 0.25, 2),
            "issues": issues
        }
    elif keyword_score >= 0.15: # Much more lenient
        return {
            "status": "ambiguous",
            "confidence": round(0.40 + keyword_score * 0.30, 2),
            "issues": issues if issues else ["Invoice detected but some details match poorly"]
        }
    else:
        # Only reject if almost NO keywords are found
        return {
            "status": "not_invoice",
            "confidence": round(0.60 + (1 - keyword_score) * 0.35, 2),
            "issues": ["Document does not resemble an invoice"]
        }


def _detect_issues(text: str, text_lower: str) -> list:
    issues = []

    # Check invoice number / order id
    inv_pattern = r"(inv(?:oice)?|order|bill)[\s#\-no:\.]+[\w\-]+"
    if not re.search(inv_pattern, text_lower):
        issues.append("Invoice/Order number not found")

    # Check date
    date_pattern = r"\b(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}|\d{4}[\/\-]\d{2}[\/\-]\d{2}|[A-Z][a-z]{2,8}\s+\d{1,2},?\s+\d{4})\b"
    if not re.search(date_pattern, text):
        issues.append("Invoice date not found")

    # Check vendor / company name
    if len(text.strip()) > 0:
        first_500 = text[:500]
        has_company = bool(re.search(r"[A-Z][a-zA-Z0-9\s\.]{3,50}(pvt|ltd|llc|inc|corp|co\.|limited|private)", first_500, re.IGNORECASE))
        if not has_company:
            issues.append("Vendor name unclear")

    # Check total amount
    amount_pattern = r"(total|grand total|amount|payable|balance)[\s:₹$€£]*[\d,]+\.?\d*"
    if not re.search(amount_pattern, text_lower):
        issues.append("Total amount not detected")

    # Check for line items (optional for ambiguous)
    line_item_pattern = r"\d+[\s]+[A-Za-z].*[\s]+[\d,\.]+[\s]+[\d,\.]+"
    if not re.search(line_item_pattern, text):
        # We don't mark line items as a "hard" issue for classification anymore
        pass

    return issues


# -----------------------------------------------------------
# LayoutLM v3 version (uncomment when model is ready)
# -----------------------------------------------------------
# from transformers import AutoProcessor, LayoutLMv3ForSequenceClassification
# import torch
#
# MODEL_NAME = "microsoft/layoutlmv3-base"
# processor = AutoProcessor.from_pretrained(MODEL_NAME)
# model = LayoutLMv3ForSequenceClassification.from_pretrained(MODEL_NAME)
#
# def classify_with_layoutlm(text: str, image_path: str) -> dict:
#     image = Image.open(image_path).convert("RGB")
#     encoding = processor(image, text[:512], return_tensors="pt", truncation=True)
#     with torch.no_grad():
#         outputs = model(**encoding)
#     logits = outputs.logits
#     predicted_class = logits.argmax(-1).item()
#     confidence = torch.softmax(logits, dim=-1).max().item()
#     label_map = {0: "not_invoice", 1: "ambiguous", 2: "valid"}
#     return {"status": label_map[predicted_class], "confidence": round(confidence, 2), "issues": []}