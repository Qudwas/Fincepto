import uuid
from datetime import date, datetime
from typing import Optional
from decimal import Decimal
from sqlalchemy import String, Boolean, ForeignKey, Numeric, Date, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, new_uuid


class TravelPackage(Base, TimestampMixin):
    __tablename__ = "travel_packages"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    destination: Mapped[str] = mapped_column(String(255), nullable=False)
    duration_days: Mapped[int] = mapped_column(nullable=False, default=1)
    base_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    currency_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("currencies.id"), nullable=True)


class TravelSupplier(Base, TimestampMixin):
    __tablename__ = "travel_suppliers"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    supplier_type: Mapped[str] = mapped_column(String(30), nullable=False)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class TravelBooking(Base, TimestampMixin):
    __tablename__ = "travel_bookings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    booking_number: Mapped[str] = mapped_column(String(100), nullable=False)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    package_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("travel_packages.id"), nullable=True)
    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("customers.id"), nullable=True)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    travel_date: Mapped[date] = mapped_column(Date, nullable=False)
    return_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    pax_count: Mapped[int] = mapped_column(nullable=False, default=1)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    commission_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="ENQUIRY", nullable=False)
    invoice_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("invoices.id"), nullable=True)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(nullable=True)

    package: Mapped[Optional["TravelPackage"]] = relationship("TravelPackage")
    supplier_costs: Mapped[list["BookingSupplierCost"]] = relationship("BookingSupplierCost", back_populates="booking", cascade="all, delete-orphan")


class BookingSupplierCost(Base):
    __tablename__ = "booking_supplier_costs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    booking_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("travel_bookings.id", ondelete="CASCADE"), nullable=False)
    supplier_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("travel_suppliers.id"), nullable=False)
    service_description: Mapped[str] = mapped_column(String(500), nullable=False)
    cost_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    currency_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("currencies.id"), nullable=True)

    booking: Mapped["TravelBooking"] = relationship("TravelBooking", back_populates="supplier_costs")
    supplier: Mapped["TravelSupplier"] = relationship("TravelSupplier")
