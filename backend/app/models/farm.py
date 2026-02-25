import uuid
from datetime import date, datetime
from typing import Optional
from decimal import Decimal
from sqlalchemy import String, Boolean, ForeignKey, Numeric, Date, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, new_uuid


class Farm(Base, TimestampMixin):
    __tablename__ = "farms"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    location_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("locations.id"), nullable=True)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    farm_type: Mapped[str] = mapped_column(String(20), default="LIVESTOCK", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)


class LivestockBatch(Base, TimestampMixin):
    __tablename__ = "livestock_batches"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    farm_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("farms.id"), nullable=False)
    species: Mapped[str] = mapped_column(String(100), nullable=False)
    breed: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    batch_number: Mapped[str] = mapped_column(String(100), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    initial_count: Mapped[int] = mapped_column(nullable=False, default=0)
    current_count: Mapped[int] = mapped_column(nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)

    farm: Mapped["Farm"] = relationship("Farm")


class FeedRecord(Base, TimestampMixin):
    __tablename__ = "feed_records"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    batch_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("livestock_batches.id"), nullable=False)
    farm_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("farms.id"), nullable=False)
    feed_date: Mapped[date] = mapped_column(Date, nullable=False)
    feed_type: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity_kg: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0"), nullable=False)
    total_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0"), nullable=False)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(nullable=True)

    batch: Mapped["LivestockBatch"] = relationship("LivestockBatch")


class ProductionRecord(Base, TimestampMixin):
    __tablename__ = "production_records"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    farm_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("farms.id"), nullable=False)
    batch_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("livestock_batches.id"), nullable=True)
    production_date: Mapped[date] = mapped_column(Date, nullable=False)
    product_type: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False, default="KG")
    unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0"), nullable=False)
    total_value: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0"), nullable=False)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(nullable=True)


class MortalityRecord(Base, TimestampMixin):
    __tablename__ = "mortality_records"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    batch_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("livestock_batches.id"), nullable=False)
    record_date: Mapped[date] = mapped_column(Date, nullable=False)
    count: Mapped[int] = mapped_column(nullable=False, default=0)
    cause: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)

    batch: Mapped["LivestockBatch"] = relationship("LivestockBatch")
