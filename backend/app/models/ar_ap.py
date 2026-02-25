import uuid
from datetime import date, datetime
from typing import Optional
from decimal import Decimal
from sqlalchemy import String, Boolean, ForeignKey, Numeric, Date, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, new_uuid


class Customer(Base, TimestampMixin):
    __tablename__ = "customers"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    credit_limit: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0"), nullable=False)
    currency_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("currencies.id"), nullable=True)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    account_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Supplier(Base, TimestampMixin):
    __tablename__ = "suppliers"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    currency_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("currencies.id"), nullable=True)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    account_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Invoice(Base, TimestampMixin):
    __tablename__ = "invoices"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    invoice_number: Mapped[str] = mapped_column(String(100), nullable=False)
    invoice_type: Mapped[str] = mapped_column(String(20), nullable=False)
    party_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    party_type: Mapped[str] = mapped_column(String(20), nullable=False)
    invoice_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    currency_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("currencies.id"), nullable=True)
    exchange_rate: Mapped[Decimal] = mapped_column(Numeric(18, 6), default=Decimal("1.0"), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0"), nullable=False)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0"), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0"), nullable=False)
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0"), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="DRAFT", nullable=False)
    journal_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("journals.id"), nullable=True)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(nullable=True)

    lines: Mapped[list["InvoiceLine"]] = relationship("InvoiceLine", back_populates="invoice", cascade="all, delete-orphan")


class InvoiceLine(Base):
    __tablename__ = "invoice_lines"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    invoice_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False)
    item_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("items.id"), nullable=True)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    discount_rate: Mapped[Decimal] = mapped_column(Numeric(8, 4), default=Decimal("0"), nullable=False)
    tax_code_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("tax_codes.id"), nullable=True)
    line_total: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)

    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="lines")


class Payment(Base, TimestampMixin):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    payment_number: Mapped[str] = mapped_column(String(100), nullable=False)
    payment_type: Mapped[str] = mapped_column(String(20), nullable=False)
    party_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    party_type: Mapped[str] = mapped_column(String(20), nullable=False)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    currency_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("currencies.id"), nullable=True)
    exchange_rate: Mapped[Decimal] = mapped_column(Numeric(18, 6), default=Decimal("1.0"), nullable=False)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="DRAFT", nullable=False)
    journal_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("journals.id"), nullable=True)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(nullable=True)

    allocations: Mapped[list["PaymentAllocation"]] = relationship("PaymentAllocation", back_populates="payment", cascade="all, delete-orphan")


class PaymentAllocation(Base):
    __tablename__ = "payment_allocations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    payment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("payments.id", ondelete="CASCADE"), nullable=False)
    invoice_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("invoices.id"), nullable=False)
    allocated_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)

    payment: Mapped["Payment"] = relationship("Payment", back_populates="allocations")
