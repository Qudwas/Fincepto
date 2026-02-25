import uuid
from datetime import date, datetime
from typing import Optional
from decimal import Decimal
from sqlalchemy import String, Boolean, ForeignKey, Numeric, Date, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, new_uuid


class RoomType(Base, TimestampMixin):
    __tablename__ = "room_types"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    base_rate: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    capacity: Mapped[int] = mapped_column(nullable=False, default=2)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)


class Room(Base, TimestampMixin):
    __tablename__ = "rooms"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    room_number: Mapped[str] = mapped_column(String(20), nullable=False)
    room_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("room_types.id"), nullable=False)
    floor: Mapped[Optional[int]] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="AVAILABLE", nullable=False)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)

    room_type: Mapped["RoomType"] = relationship("RoomType")


class Reservation(Base, TimestampMixin):
    __tablename__ = "reservations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    reservation_number: Mapped[str] = mapped_column(String(100), nullable=False)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    room_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("rooms.id"), nullable=False)
    guest_name: Mapped[str] = mapped_column(String(255), nullable=False)
    guest_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    guest_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    check_in_date: Mapped[date] = mapped_column(Date, nullable=False)
    check_out_date: Mapped[date] = mapped_column(Date, nullable=False)
    actual_check_in: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_check_out: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    rate_per_night: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="CONFIRMED", nullable=False)
    invoice_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("invoices.id"), nullable=True)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(nullable=True)

    room: Mapped["Room"] = relationship("Room")


class POSOutlet(Base, TimestampMixin):
    __tablename__ = "pos_outlets"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    outlet_type: Mapped[str] = mapped_column(String(30), nullable=False, default="RESTAURANT")
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    location_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("locations.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class POSSale(Base, TimestampMixin):
    __tablename__ = "pos_sales"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    sale_number: Mapped[str] = mapped_column(String(100), nullable=False)
    outlet_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pos_outlets.id"), nullable=False)
    sale_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    customer_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0"), nullable=False)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0"), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0"), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(20), default="CASH", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="OPEN", nullable=False)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(nullable=True)

    outlet: Mapped["POSOutlet"] = relationship("POSOutlet")
    lines: Mapped[list["POSSaleLine"]] = relationship("POSSaleLine", back_populates="pos_sale", cascade="all, delete-orphan")


class POSSaleLine(Base):
    __tablename__ = "pos_sale_lines"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    pos_sale_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pos_sales.id", ondelete="CASCADE"), nullable=False)
    item_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("items.id"), nullable=True)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    line_total: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)

    pos_sale: Mapped["POSSale"] = relationship("POSSale", back_populates="lines")
