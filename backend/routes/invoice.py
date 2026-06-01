from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import get_db, Invoice, AuditLog
from pydantic import BaseModel
import json

router = APIRouter(prefix="/api")


class ReviewUpdate(BaseModel):
    action: str   # "approve" or "reject"
    note: str = ""


@router.get("/invoices")
def get_all_invoices(db: Session = Depends(get_db)):
    invoices = db.query(Invoice).order_by(Invoice.uploaded_at.desc()).all()
    return [_serialize(inv) for inv in invoices]


@router.get("/invoices/{invoice_id}")
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return _serialize(invoice)


@router.patch("/invoices/{invoice_id}/review")
def review_invoice(invoice_id: int, body: ReviewUpdate, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if body.action == "approve":
        invoice.status = "valid"
        invoice.reviewed = True
    elif body.action == "reject":
        invoice.status = "rejected"
        invoice.reviewed = True
    else:
        raise HTTPException(status_code=400, detail="Action must be approve or reject")

    db.add(AuditLog(invoice_id=invoice_id, action=body.action, note=body.note))
    db.commit()
    db.refresh(invoice)
    return _serialize(invoice)


@router.delete("/invoices/{invoice_id}")
def delete_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    db.delete(invoice)
    db.commit()
    return {"message": "Invoice deleted"}


def _serialize(inv: Invoice) -> dict:
    return {
        "id": inv.id,
        "filename": inv.filename,
        "status": inv.status,
        "confidence": inv.confidence,
        "vendor_name": inv.vendor_name,
        "invoice_number": inv.invoice_number,
        "invoice_date": inv.invoice_date,
        "subtotal": inv.subtotal,
        "tax_amount": inv.tax_amount,
        "grand_total": inv.grand_total,
        "total_match": inv.total_match,
        "issues": json.loads(inv.issues) if inv.issues else [],
        "reviewed": inv.reviewed,
        "uploaded_at": inv.uploaded_at.isoformat() if inv.uploaded_at else None,
    }