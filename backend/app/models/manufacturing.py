import uuid
from datetime import date, datetime
from typing import Optional
from decimal import Decimal
from sqlalchemy import String, Boolean, ForeignKey, Numeric, Date, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, new_uuid


class BillOfMaterials(Base, TimestampMixin):
    __tablename__ = "bill_of_materials"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    finished_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("items.id"), nullable=False)
    version: Mapped[str] = mapped_column(String(20), default="1.0", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    lines: Mapped[list["BOMLine"]] = relationship("BOMLine", back_populates="bom", cascade="all, delete-orphan")
    finished_item: Mapped["Item"] = relationship("Item", foreign_keys=[finished_item_id])


class BOMLine(Base):
    __tablename__ = "bom_lines"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    bom_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("bill_of_materials.id", ondelete="CASCADE"), nullable=False)
    component_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("items.id"), nullable=False)
    quantity_per_unit: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    unit_of_measure: Mapped[str] = mapped_column(String(20), nullable=False, default="UNIT")

    bom: Mapped["BillOfMaterials"] = relationship("BillOfMaterials", back_populates="lines")
    component_item: Mapped["Item"] = relationship("Item", foreign_keys=[component_item_id])


class ProductionOrder(Base, TimestampMixin):
    __tablename__ = "production_orders"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    order_number: Mapped[str] = mapped_column(String(100), nullable=False)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    finished_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("items.id"), nullable=False)
    bom_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("bill_of_materials.id"), nullable=True)
    planned_quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    produced_quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0"), nullable=False)
    scrap_quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="DRAFT", nullable=False)
    planned_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    planned_end: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    actual_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    actual_end: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    cost_center_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("cost_centers.id"), nullable=True)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(nullable=True)

    finished_item: Mapped["Item"] = relationship("Item", foreign_keys=[finished_item_id])
    consumptions: Mapped[list["ProductionConsumption"]] = relationship("ProductionConsumption", back_populates="production_order", cascade="all, delete-orphan")


class ProductionConsumption(Base):
    __tablename__ = "production_consumptions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=new_uuid)
    production_order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("production_orders.id", ondelete="CASCADE"), nullable=False)
    item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("items.id"), nullable=False)
    planned_quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    actual_quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0"), nullable=False)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0"), nullable=False)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)

    production_order: Mapped["ProductionOrder"] = relationship("ProductionOrder", back_populates="consumptions")
    item: Mapped["Item"] = relationship("Item", foreign_keys=[item_id])
