from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import get_db, Invoice, AuditLog, create_tables
from services.ocr import extract_text_from_file
from services.classifier import classify_invoice
from services.extractor import extract_fields
from services.calculator import validate_and_calculate
import shutil, os, json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/api")

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
ALLOWED_TYPES = ["application/pdf", "image/jpeg", "image/png", "image/jpg", "image/webp"]
MAX_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))


@router.on_event("startup")
def startup():
    create_tables()
    os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_invoice(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Validate file type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file.content_type} not supported. Upload PDF or image."
        )

    # Save file
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_name = f"{timestamp}_{file.filename.replace(' ', '_')}"
    file_path = os.path.join(UPLOAD_DIR, safe_name)

    with open(file_path, "wb") as buffer:
        content = await file.read()
        if len(content) > MAX_SIZE_MB * 1024 * 1024:
            raise HTTPException(status_code=400, detail=f"File too large. Max {MAX_SIZE_MB}MB.")
        buffer.write(content)

    # Step 1: OCR — extract text
    ocr_result = extract_text_from_file(file_path)
    extracted_text = ocr_result.get("text", "")

    if ocr_result.get("error"):
        raise HTTPException(status_code=500, detail=f"OCR failed: {ocr_result['error']}")

    # Step 2: Classify
    classification = classify_invoice(extracted_text)

    # Step 3: Extract fields (always, for any classification)
    fields = extract_fields(extracted_text)

    # Step 4: Calculate & validate (only for valid or ambiguous)
    calc_result = {}
    if classification["status"] in ["valid", "ambiguous"]:
        calc_result = validate_and_calculate(fields)
        # Add math issues to classification issues
        if calc_result.get("math_issues"):
            classification["issues"] = classification.get("issues", []) + calc_result["math_issues"]
            if classification["status"] == "valid" and calc_result["math_issues"]:
                classification["status"] = "ambiguous"

    # Step 5: Save to database
    invoice_record = Invoice(
        filename=file.filename,
        status=classification["status"],
        confidence=classification["confidence"],
        vendor_name=fields.get("vendor_name"),
        invoice_number=fields.get("invoice_number"),
        invoice_date=fields.get("invoice_date"),
        subtotal=calc_result.get("summary", {}).get("subtotal"),
        tax_amount=calc_result.get("summary", {}).get("tax"),
        grand_total=calc_result.get("summary", {}).get("grand_total"),
        total_match=calc_result.get("total_match"),
        issues=json.dumps(classification.get("issues", [])),
        extracted_text=extracted_text[:2000],
    )
    db.add(invoice_record)
    db.commit()
    db.refresh(invoice_record)

    # Audit log
    db.add(AuditLog(invoice_id=invoice_record.id, action="uploaded"))
    db.commit()

    return {
        "id": invoice_record.id,
        "filename": file.filename,
        "status": classification["status"],
        "confidence": classification["confidence"],
        "issues": classification.get("issues", []),
        "fields": fields,
        "calculation": calc_result.get("summary", {}),
        "math_issues": calc_result.get("math_issues", []),
        "total_match": calc_result.get("total_match"),
        "pages": ocr_result.get("pages", 1),
    }