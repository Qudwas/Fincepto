import uuid
from datetime import date, datetime
from typing import Optional
from decimal import Decimal
from sqlalchemy import String, Boolean, ForeignKey, Numeric, Date, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, new_uuid


class AssetCategory(Base, TimestampMixin):
    __tablename__ = "asset_categories"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    useful_life_years: Mapped[int] = mapped_column(nullable=False, default=5)
    depreciation_method: Mapped[str] = mapped_column(String(30), nullable=False, default="STRAIGHT_LINE")
    depreciation_rate: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False, default=Decimal("20.0"))
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    asset_account_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    depreciation_account_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    accum_depreciation_account_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("accounts.id"), nullable=True)


class FixedAsset(Base, TimestampMixin):
    __tablename__ = "fixed_assets"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("asset_categories.id"), nullable=False)
    purchase_date: Mapped[date] = mapped_column(Date, nullable=False)
    purchase_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    accumulated_depreciation: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0"), nullable=False)
    net_book_value: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)
    location_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("locations.id"), nullable=True)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    journal_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("journals.id"), nullable=True)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(nullable=True)
    disposal_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    disposal_proceeds: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 4), nullable=True)

    category: Mapped["AssetCategory"] = relationship("AssetCategory")
    schedules: Mapped[list["DepreciationSchedule"]] = relationship("DepreciationSchedule", back_populates="asset", cascade="all, delete-orphan")


class DepreciationSchedule(Base):
    __tablename__ = "depreciation_schedules"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("fixed_assets.id", ondelete="CASCADE"), nullable=False)
    period_date: Mapped[date] = mapped_column(Date, nullable=False)
    depreciation_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    accumulated_to_date: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    journal_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("journals.id"), nullable=True)
    is_posted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    asset: Mapped["FixedAsset"] = relationship("FixedAsset", back_populates="schedules")
