from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.database import get_db, Invoice
from datetime import datetime, timedelta

router = APIRouter(prefix="/api")


@router.get("/analytics/summary")
def get_summary(db: Session = Depends(get_db)):
    total = db.query(Invoice).count()
    valid = db.query(Invoice).filter(Invoice.status == "valid").count()
    ambiguous = db.query(Invoice).filter(Invoice.status == "ambiguous").count()
    not_invoice = db.query(Invoice).filter(Invoice.status == "not_invoice").count()
    rejected = db.query(Invoice).filter(Invoice.status == "rejected").count()
    pending_review = db.query(Invoice).filter(
        Invoice.status == "ambiguous", Invoice.reviewed == False
    ).count()

    total_spend = db.query(func.sum(Invoice.grand_total)).filter(
        Invoice.status == "valid"
    ).scalar() or 0

    return {
        "total": total,
        "valid": valid,
        "ambiguous": ambiguous,
        "not_invoice": not_invoice,
        "rejected": rejected,
        "pending_review": pending_review,
        "total_spend": round(total_spend, 2),
        "approval_rate": round((valid / total * 100) if total > 0 else 0, 1),
    }


@router.get("/analytics/daily")
def get_daily_trend(db: Session = Depends(get_db)):
    """Last 7 days upload counts"""
    result = []
    for i in range(6, -1, -1):
        day = datetime.utcnow() - timedelta(days=i)
        start = day.replace(hour=0, minute=0, second=0)
        end = day.replace(hour=23, minute=59, second=59)
        count = db.query(Invoice).filter(
            Invoice.uploaded_at >= start,
            Invoice.uploaded_at <= end
        ).count()
        result.append({
            "date": day.strftime("%b %d"),
            "count": count
        })
    return result


@router.get("/analytics/vendors")
def get_vendor_stats(db: Session = Depends(get_db)):
    """Top vendors by invoice count"""
    vendors = db.query(
        Invoice.vendor_name,
        func.count(Invoice.id).label("count"),
        func.sum(Invoice.grand_total).label("total_spend")
    ).filter(
        Invoice.vendor_name.isnot(None),
        Invoice.status == "valid"
    ).group_by(Invoice.vendor_name).order_by(
        func.count(Invoice.id).desc()
    ).limit(10).all()

    return [
        {
            "vendor": v.vendor_name,
            "count": v.count,
            "total_spend": round(v.total_spend or 0, 2)
        }
        for v in vendors
    ]