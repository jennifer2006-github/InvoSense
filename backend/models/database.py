from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./invosense.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    status = Column(String, nullable=False)          # valid / ambiguous / not_invoice
    confidence = Column(Float, nullable=True)
    vendor_name = Column(String, nullable=True)
    invoice_number = Column(String, nullable=True)
    invoice_date = Column(String, nullable=True)
    subtotal = Column(Float, nullable=True)
    tax_amount = Column(Float, nullable=True)
    grand_total = Column(Float, nullable=True)
    total_match = Column(Boolean, nullable=True)
    issues = Column(Text, nullable=True)             # JSON string of issues list
    extracted_text = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    reviewed = Column(Boolean, default=False)


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, nullable=False)
    action = Column(String, nullable=False)
    note = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)