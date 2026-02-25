import uuid
from datetime import date, datetime
from typing import Optional
from decimal import Decimal
from sqlalchemy import String, Boolean, ForeignKey, Numeric, Date, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, new_uuid


class AccountType(Base):
    __tablename__ = "account_types"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    normal_balance: Mapped[str] = mapped_column(String(10), nullable=False, default="DEBIT")


class Account(Base, TimestampMixin):
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("account_types.id"), nullable=False)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    currency_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("currencies.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_control_account: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    account_type: Mapped["AccountType"] = relationship("AccountType")
    children: Mapped[list["Account"]] = relationship("Account", back_populates="parent")
    parent: Mapped[Optional["Account"]] = relationship("Account", back_populates="children", remote_side="Account.id")


class FiscalYear(Base, TimestampMixin):
    __tablename__ = "fiscal_years"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_closed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    periods: Mapped[list["AccountingPeriod"]] = relationship("AccountingPeriod", back_populates="fiscal_year", cascade="all, delete-orphan")


class AccountingPeriod(Base, TimestampMixin):
    __tablename__ = "accounting_periods"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    fiscal_year_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("fiscal_years.id"), nullable=False)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    fiscal_year: Mapped["FiscalYear"] = relationship("FiscalYear", back_populates="periods")


class Journal(Base, TimestampMixin):
    __tablename__ = "journals"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    reference: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    journal_date: Mapped[date] = mapped_column(Date, nullable=False)
    currency_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("currencies.id"), nullable=True)
    exchange_rate: Mapped[Decimal] = mapped_column(Numeric(18, 6), default=Decimal("1.0"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="DRAFT", nullable=False)
    is_reversal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reversed_journal_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("journals.id"), nullable=True)
    posted_by: Mapped[Optional[uuid.UUID]] = mapped_column(nullable=True)
    posted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    business_line_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("business_lines.id"), nullable=True)
    location_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("locations.id"), nullable=True)
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("departments.id"), nullable=True)
    cost_center_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("cost_centers.id"), nullable=True)
    project_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("projects.id"), nullable=True)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(nullable=True)

    lines: Mapped[list["JournalLine"]] = relationship("JournalLine", back_populates="journal", cascade="all, delete-orphan")


class JournalLine(Base):
    __tablename__ = "journal_lines"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    journal_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("journals.id", ondelete="CASCADE"), nullable=False)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    debit: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0"), nullable=False)
    credit: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0"), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    currency_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("currencies.id"), nullable=True)
    functional_debit: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0"), nullable=False)
    functional_credit: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0"), nullable=False)

    journal: Mapped["Journal"] = relationship("Journal", back_populates="lines")
    account: Mapped["Account"] = relationship("Account")


class TaxCode(Base, TimestampMixin):
    __tablename__ = "tax_codes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    rate: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False)
    tax_type: Mapped[str] = mapped_column(String(20), nullable=False)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
