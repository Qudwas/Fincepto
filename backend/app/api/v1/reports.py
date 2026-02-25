from typing import Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import require_permission
from app.services.report_service import report_service

router = APIRouter()


@router.get("/trial-balance", dependencies=[Depends(require_permission("ACCOUNTING_REPORTS_VIEW"))])
def trial_balance(company_id: UUID, as_of_date: date, db: Session = Depends(get_db)):
    return report_service.trial_balance(db, company_id, as_of_date)


@router.get("/income-statement", dependencies=[Depends(require_permission("ACCOUNTING_REPORTS_VIEW"))])
def income_statement(company_id: UUID, from_date: date, to_date: date, db: Session = Depends(get_db)):
    return report_service.income_statement(db, company_id, from_date, to_date)


@router.get("/balance-sheet", dependencies=[Depends(require_permission("ACCOUNTING_REPORTS_VIEW"))])
def balance_sheet(company_id: UUID, as_of_date: date, db: Session = Depends(get_db)):
    return report_service.balance_sheet(db, company_id, as_of_date)


@router.get("/cash-flow", dependencies=[Depends(require_permission("ACCOUNTING_REPORTS_VIEW"))])
def cash_flow(company_id: UUID, from_date: date, to_date: date, db: Session = Depends(get_db)):
    return report_service.cash_flow_statement(db, company_id, from_date, to_date)


@router.get("/aged-receivables", dependencies=[Depends(require_permission("ACCOUNTING_REPORTS_VIEW"))])
def aged_receivables(company_id: UUID, as_of_date: date, db: Session = Depends(get_db)):
    return report_service.aged_receivables(db, company_id, as_of_date)


@router.get("/aged-payables", dependencies=[Depends(require_permission("ACCOUNTING_REPORTS_VIEW"))])
def aged_payables(company_id: UUID, as_of_date: date, db: Session = Depends(get_db)):
    return report_service.aged_payables(db, company_id, as_of_date)


@router.get("/segment", dependencies=[Depends(require_permission("ACCOUNTING_REPORTS_VIEW"))])
def segment_report(company_id: UUID, from_date: date, to_date: date, dimension: str = "department", dimension_id: Optional[UUID] = None, db: Session = Depends(get_db)):
    return report_service.segment_report(db, company_id, from_date, to_date, dimension, dimension_id)


@router.get("/dashboard/kpis", dependencies=[Depends(require_permission("ACCOUNTING_REPORTS_VIEW"))])
def kpi_dashboard(company_id: UUID, from_date: date, to_date: date, db: Session = Depends(get_db)):
    return report_service.kpi_dashboard(db, company_id, from_date, to_date)


@router.get("/budget-vs-actual", dependencies=[Depends(require_permission("ACCOUNTING_FORECASTS_MANAGE"))])
def budget_vs_actual(company_id: UUID, budget_id: UUID, from_date: date, to_date: date, db: Session = Depends(get_db)):
    return report_service.budget_vs_actual(db, company_id, budget_id, from_date, to_date)


@router.get("/forecast/pl", dependencies=[Depends(require_permission("ACCOUNTING_FORECASTS_MANAGE"))])
def forecast_pl(company_id: UUID, months_ahead: int = 3, db: Session = Depends(get_db)):
    return report_service.forecast_pl(db, company_id, months_ahead)


@router.get("/farm/batch-performance", dependencies=[Depends(require_permission("FARM_REPORTS_VIEW"))])
def farm_batch_performance(company_id: UUID, farm_id: Optional[UUID] = None, from_date: Optional[date] = None, to_date: Optional[date] = None, db: Session = Depends(get_db)):
    return report_service.farm_batch_performance(db, company_id, farm_id, from_date, to_date)


@router.get("/farm/feed-consumption", dependencies=[Depends(require_permission("FARM_REPORTS_VIEW"))])
def farm_feed_consumption(company_id: UUID, from_date: date, to_date: date, db: Session = Depends(get_db)):
    from app.models.farm import FeedRecord
    from sqlalchemy import func
    rows = db.query(
        FeedRecord.farm_id,
        FeedRecord.batch_id,
        FeedRecord.feed_type,
        func.sum(FeedRecord.quantity_kg).label("total_qty_kg"),
        func.sum(FeedRecord.total_cost).label("total_cost"),
    ).filter(
        FeedRecord.company_id == company_id,
        FeedRecord.feed_date >= from_date,
        FeedRecord.feed_date <= to_date,
    ).group_by(FeedRecord.farm_id, FeedRecord.batch_id, FeedRecord.feed_type).all()
    return {"company_id": str(company_id), "from_date": str(from_date), "to_date": str(to_date), "lines": [{"farm_id": str(r.farm_id), "batch_id": str(r.batch_id) if r.batch_id else None, "feed_type": r.feed_type, "total_qty_kg": float(r.total_qty_kg or 0), "total_cost": float(r.total_cost or 0)} for r in rows]}


@router.get("/farm/production-output", dependencies=[Depends(require_permission("FARM_REPORTS_VIEW"))])
def farm_production_output(company_id: UUID, from_date: date, to_date: date, db: Session = Depends(get_db)):
    return report_service.farm_production_output(db, company_id, from_date, to_date)


@router.get("/manufacturing/production-orders", dependencies=[Depends(require_permission("MANUFACTURING_REPORTS_VIEW"))])
def manufacturing_production_orders(company_id: UUID, from_date: date, to_date: date, db: Session = Depends(get_db)):
    return report_service.manufacturing_production_report(db, company_id, from_date, to_date)


@router.get("/manufacturing/material-variance", dependencies=[Depends(require_permission("MANUFACTURING_REPORTS_VIEW"))])
def material_variance(company_id: UUID, from_date: date, to_date: date, db: Session = Depends(get_db)):
    from app.models.manufacturing import ProductionOrder, ProductionConsumption
    from sqlalchemy import func
    orders = db.query(ProductionOrder).filter(ProductionOrder.company_id == company_id).all()
    lines = []
    for o in orders:
        consumptions = db.query(ProductionConsumption).filter(ProductionConsumption.production_order_id == o.id).all()
        for c in consumptions:
            variance = float(c.actual_quantity - c.planned_quantity)
            lines.append({"order_number": o.order_number, "item_id": str(c.item_id), "planned_qty": float(c.planned_quantity), "actual_qty": float(c.actual_quantity), "variance": variance, "cost_variance": variance * float(c.unit_cost)})
    return {"company_id": str(company_id), "lines": lines}


@router.get("/hospitality/occupancy", dependencies=[Depends(require_permission("HOSPITALITY_REPORTS_VIEW"))])
def hospitality_occupancy(company_id: UUID, from_date: date, to_date: date, db: Session = Depends(get_db)):
    return report_service.hospitality_occupancy_report(db, company_id, from_date, to_date)


@router.get("/hospitality/revenue-by-segment", dependencies=[Depends(require_permission("HOSPITALITY_REPORTS_VIEW"))])
def hospitality_revenue_by_segment(company_id: UUID, from_date: date, to_date: date, db: Session = Depends(get_db)):
    from app.models.hospitality import Reservation, POSSale
    from sqlalchemy import func
    room_rev = db.query(func.sum(Reservation.total_amount)).filter(Reservation.company_id == company_id, Reservation.check_in_date >= from_date, Reservation.check_out_date <= to_date, Reservation.status.in_(["CHECKED_IN", "CHECKED_OUT"])).scalar() or 0
    pos_rev = db.query(func.sum(POSSale.total_amount)).filter(POSSale.company_id == company_id, POSSale.sale_date >= from_date, POSSale.sale_date <= to_date).scalar() or 0
    return {"company_id": str(company_id), "from_date": str(from_date), "to_date": str(to_date), "room_revenue": float(room_rev), "pos_revenue": float(pos_rev), "total": float(room_rev) + float(pos_rev)}


@router.get("/hospitality/pos-sales", dependencies=[Depends(require_permission("HOSPITALITY_REPORTS_VIEW"))])
def hospitality_pos_sales(company_id: UUID, from_date: date, to_date: date, outlet_id: Optional[UUID] = None, db: Session = Depends(get_db)):
    from app.models.hospitality import POSSale
    from sqlalchemy import func
    q = db.query(POSSale.outlet_id, func.count(POSSale.id).label("count"), func.sum(POSSale.total_amount).label("total")).filter(POSSale.company_id == company_id, POSSale.sale_date >= from_date, POSSale.sale_date <= to_date)
    if outlet_id:
        q = q.filter(POSSale.outlet_id == outlet_id)
    rows = q.group_by(POSSale.outlet_id).all()
    return {"company_id": str(company_id), "from_date": str(from_date), "to_date": str(to_date), "by_outlet": [{"outlet_id": str(r.outlet_id), "count": r.count, "total_amount": float(r.total or 0)} for r in rows]}


@router.get("/travel/booking-pipeline", dependencies=[Depends(require_permission("TRAVEL_REPORTS_VIEW"))])
def travel_booking_pipeline(company_id: UUID, from_date: date, to_date: date, db: Session = Depends(get_db)):
    return report_service.travel_booking_pipeline(db, company_id, from_date, to_date)


@router.get("/travel/revenue-by-package", dependencies=[Depends(require_permission("TRAVEL_REPORTS_VIEW"))])
def travel_revenue_by_package(company_id: UUID, from_date: date, to_date: date, db: Session = Depends(get_db)):
    from app.models.travel import TravelBooking
    from sqlalchemy import func
    rows = db.query(TravelBooking.package_id, func.count(TravelBooking.id).label("count"), func.sum(TravelBooking.total_amount).label("total")).filter(TravelBooking.company_id == company_id, TravelBooking.travel_date >= from_date, TravelBooking.travel_date <= to_date, TravelBooking.status.in_(["BOOKED", "CONFIRMED"])).group_by(TravelBooking.package_id).all()
    return {"company_id": str(company_id), "from_date": str(from_date), "to_date": str(to_date), "by_package": [{"package_id": str(r.package_id) if r.package_id else None, "count": r.count, "total_revenue": float(r.total or 0)} for r in rows]}


@router.get("/trading/sales", dependencies=[Depends(require_permission("TRADING_REPORTS_VIEW"))])
def trading_sales(company_id: UUID, from_date: date, to_date: date, db: Session = Depends(get_db)):
    return report_service.trading_sales_report(db, company_id, from_date, to_date)


@router.get("/trading/gross-margin", dependencies=[Depends(require_permission("TRADING_REPORTS_VIEW"))])
def trading_gross_margin(company_id: UUID, from_date: date, to_date: date, db: Session = Depends(get_db)):
    from app.models.crm import SalesOrder, SalesOrderLine
    from app.models.inventory import Item
    from sqlalchemy import func
    rows = db.query(SalesOrderLine.item_id, func.sum(SalesOrderLine.line_total).label("revenue"), func.sum(SalesOrderLine.quantity * Item.standard_cost).label("cost")).join(SalesOrder).join(Item, Item.id == SalesOrderLine.item_id).filter(SalesOrder.company_id == company_id, SalesOrder.order_date >= from_date, SalesOrder.order_date <= to_date).group_by(SalesOrderLine.item_id).all()
    result = [{"item_id": str(r.item_id), "revenue": float(r.revenue or 0), "cost": float(r.cost or 0), "gross_margin": float((r.revenue or 0) - (r.cost or 0)), "margin_pct": round(((float(r.revenue or 0) - float(r.cost or 0)) / float(r.revenue) * 100) if r.revenue else 0, 2)} for r in rows]
    return {"company_id": str(company_id), "from_date": str(from_date), "to_date": str(to_date), "lines": result}


@router.get("/trading/inventory-aging", dependencies=[Depends(require_permission("TRADING_REPORTS_VIEW"))])
def inventory_aging(company_id: UUID, db: Session = Depends(get_db)):
    from app.models.inventory import StockBalance, Item, StockMovement
    from sqlalchemy import func
    balances = db.query(StockBalance).join(Item).filter(Item.company_id == company_id, StockBalance.quantity_on_hand > 0).all()
    result = []
    for b in balances:
        last_mv = db.query(StockMovement).filter(StockMovement.item_id == b.item_id, StockMovement.warehouse_id == b.warehouse_id).order_by(StockMovement.movement_date.desc()).first()
        from datetime import date as dt
        days_since = (dt.today() - last_mv.movement_date.date()).days if last_mv else 0
        result.append({"item_id": str(b.item_id), "warehouse_id": str(b.warehouse_id), "qty_on_hand": float(b.quantity_on_hand), "avg_cost": float(b.average_cost), "total_value": float(b.quantity_on_hand * b.average_cost), "days_since_last_movement": days_since})
    return {"company_id": str(company_id), "lines": result}


@router.get("/hrm/headcount", dependencies=[Depends(require_permission("HR_REPORTS_VIEW"))])
def hrm_headcount(company_id: UUID, db: Session = Depends(get_db)):
    return report_service.hrm_headcount_report(db, company_id)


@router.get("/hrm/payroll-summary", dependencies=[Depends(require_permission("HR_REPORTS_VIEW"))])
def hrm_payroll_summary(company_id: UUID, from_date: date, to_date: date, db: Session = Depends(get_db)):
    return report_service.hrm_payroll_summary(db, company_id, from_date, to_date)


@router.get("/hrm/leave", dependencies=[Depends(require_permission("HR_REPORTS_VIEW"))])
def hrm_leave_report(company_id: UUID, from_date: date, to_date: date, db: Session = Depends(get_db)):
    return report_service.hrm_leave_report(db, company_id, from_date, to_date)


@router.get("/hrm/attendance", dependencies=[Depends(require_permission("HR_REPORTS_VIEW"))])
def hrm_attendance_report(company_id: UUID, from_date: date, to_date: date, db: Session = Depends(get_db)):
    return report_service.hrm_attendance_report(db, company_id, from_date, to_date)


@router.get("/crm/pipeline", dependencies=[Depends(require_permission("CRM_REPORTS_VIEW"))])
def crm_pipeline(company_id: UUID, db: Session = Depends(get_db)):
    return report_service.crm_pipeline_report(db, company_id)


@router.get("/crm/conversion", dependencies=[Depends(require_permission("CRM_REPORTS_VIEW"))])
def crm_conversion(company_id: UUID, db: Session = Depends(get_db)):
    return report_service.crm_conversion_report(db, company_id)


@router.get("/projects/status", dependencies=[Depends(require_permission("PROJECTS_REPORTS_VIEW"))])
def projects_status(company_id: UUID, db: Session = Depends(get_db)):
    return report_service.project_status_report(db, company_id)


@router.get("/projects/timesheet", dependencies=[Depends(require_permission("PROJECTS_REPORTS_VIEW"))])
def projects_timesheet(company_id: UUID, from_date: date, to_date: date, db: Session = Depends(get_db)):
    return report_service.project_timesheet_report(db, company_id, from_date, to_date)


@router.get("/projects/profitability", dependencies=[Depends(require_permission("PROJECTS_REPORTS_VIEW"))])
def projects_profitability(company_id: UUID, db: Session = Depends(get_db)):
    return report_service.project_status_report(db, company_id)


@router.get("/inventory/stock-on-hand", dependencies=[Depends(require_permission("INVENTORY_REPORTS_VIEW"))])
def inventory_stock_on_hand(company_id: UUID, db: Session = Depends(get_db)):
    return report_service.inventory_stock_report(db, company_id)


@router.get("/inventory/valuation", dependencies=[Depends(require_permission("INVENTORY_REPORTS_VIEW"))])
def inventory_valuation(company_id: UUID, db: Session = Depends(get_db)):
    return report_service.inventory_stock_report(db, company_id)


@router.get("/security/user-roles", dependencies=[Depends(require_permission("AUDIT_VIEW"))])
def security_user_roles(db: Session = Depends(get_db)):
    return report_service.security_user_roles_report(db)
