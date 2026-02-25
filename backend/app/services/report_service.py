from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case
from app.models.accounting import Journal, JournalLine, Account, AccountType
from app.models.ar_ap import Invoice, Customer, Supplier
from app.models.inventory import StockBalance, Item, StockMovement
from app.models.hrm import Employee, PayrollRun, PayrollLine, LeaveRequest, AttendanceRecord
from app.models.crm import Lead, Opportunity, SalesOrder
from app.models.projects import ProjectTask, Timesheet, ProjectBilling
from app.models.master import Project
from app.models.farm import LivestockBatch, FeedRecord, ProductionRecord, MortalityRecord
from app.models.manufacturing import ProductionOrder, ProductionConsumption
from app.models.hospitality import Reservation, Room, POSSale, POSSaleLine
from app.models.travel import TravelBooking
from app.models.budget import Budget, BudgetLine


class ReportService:

    def trial_balance(self, db: Session, company_id: UUID, as_of_date: date) -> Dict:
        rows = (
            db.query(
                Account.id,
                Account.code,
                Account.name,
                AccountType.name.label("account_type"),
                func.sum(JournalLine.functional_debit).label("total_debit"),
                func.sum(JournalLine.functional_credit).label("total_credit"),
            )
            .join(JournalLine, JournalLine.account_id == Account.id)
            .join(Journal, Journal.id == JournalLine.journal_id)
            .join(AccountType, AccountType.id == Account.account_type_id)
            .filter(
                Account.company_id == company_id,
                Journal.status == "POSTED",
                Journal.journal_date <= as_of_date,
            )
            .group_by(Account.id, Account.code, Account.name, AccountType.name)
            .order_by(Account.code)
            .all()
        )
        lines = []
        total_debit = Decimal("0")
        total_credit = Decimal("0")
        for r in rows:
            dr = r.total_debit or Decimal("0")
            cr = r.total_credit or Decimal("0")
            balance = dr - cr
            lines.append({
                "account_id": str(r.id),
                "code": r.code,
                "name": r.name,
                "account_type": r.account_type,
                "debit": float(dr),
                "credit": float(cr),
                "balance": float(balance),
            })
            total_debit += dr
            total_credit += cr
        return {
            "company_id": str(company_id),
            "as_of_date": str(as_of_date),
            "lines": lines,
            "total_debit": float(total_debit),
            "total_credit": float(total_credit),
        }

    def income_statement(self, db: Session, company_id: UUID, from_date: date, to_date: date) -> Dict:
        rows = (
            db.query(
                Account.code,
                Account.name,
                AccountType.name.label("account_type"),
                func.sum(JournalLine.functional_credit - JournalLine.functional_debit).label("net_amount"),
            )
            .join(JournalLine, JournalLine.account_id == Account.id)
            .join(Journal, Journal.id == JournalLine.journal_id)
            .join(AccountType, AccountType.id == Account.account_type_id)
            .filter(
                Account.company_id == company_id,
                Journal.status == "POSTED",
                Journal.journal_date >= from_date,
                Journal.journal_date <= to_date,
                AccountType.name.in_(["REVENUE", "EXPENSE"]),
            )
            .group_by(Account.code, Account.name, AccountType.name)
            .order_by(AccountType.name, Account.code)
            .all()
        )
        revenue = []
        expenses = []
        total_revenue = Decimal("0")
        total_expense = Decimal("0")
        for r in rows:
            amt = r.net_amount or Decimal("0")
            if r.account_type == "REVENUE":
                revenue.append({"code": r.code, "name": r.name, "amount": float(amt)})
                total_revenue += amt
            else:
                expense_amt = -amt
                expenses.append({"code": r.code, "name": r.name, "amount": float(expense_amt)})
                total_expense += expense_amt
        net_profit = total_revenue - total_expense
        return {
            "company_id": str(company_id),
            "from_date": str(from_date),
            "to_date": str(to_date),
            "revenue": revenue,
            "expenses": expenses,
            "total_revenue": float(total_revenue),
            "total_expense": float(total_expense),
            "net_profit": float(net_profit),
        }

    def balance_sheet(self, db: Session, company_id: UUID, as_of_date: date) -> Dict:
        rows = (
            db.query(
                Account.code,
                Account.name,
                AccountType.name.label("account_type"),
                func.sum(JournalLine.functional_debit - JournalLine.functional_credit).label("net_amount"),
            )
            .join(JournalLine, JournalLine.account_id == Account.id)
            .join(Journal, Journal.id == JournalLine.journal_id)
            .join(AccountType, AccountType.id == Account.account_type_id)
            .filter(
                Account.company_id == company_id,
                Journal.status == "POSTED",
                Journal.journal_date <= as_of_date,
                AccountType.name.in_(["ASSET", "LIABILITY", "EQUITY"]),
            )
            .group_by(Account.code, Account.name, AccountType.name)
            .order_by(AccountType.name, Account.code)
            .all()
        )
        assets = []
        liabilities = []
        equity = []
        total_assets = Decimal("0")
        total_liabilities = Decimal("0")
        total_equity = Decimal("0")
        for r in rows:
            amt = r.net_amount or Decimal("0")
            entry = {"code": r.code, "name": r.name, "amount": float(abs(amt))}
            if r.account_type == "ASSET":
                assets.append(entry)
                total_assets += abs(amt)
            elif r.account_type == "LIABILITY":
                liabilities.append(entry)
                total_liabilities += abs(amt)
            elif r.account_type == "EQUITY":
                equity.append(entry)
                total_equity += abs(amt)
        return {
            "company_id": str(company_id),
            "as_of_date": str(as_of_date),
            "assets": assets,
            "liabilities": liabilities,
            "equity": equity,
            "total_assets": float(total_assets),
            "total_liabilities": float(total_liabilities),
            "total_equity": float(total_equity),
        }

    def cash_flow_statement(self, db: Session, company_id: UUID, from_date: date, to_date: date) -> Dict:
        cash_rows = (
            db.query(
                func.sum(JournalLine.functional_debit - JournalLine.functional_credit).label("net"),
            )
            .join(Journal, Journal.id == JournalLine.journal_id)
            .join(Account, Account.id == JournalLine.account_id)
            .join(AccountType, AccountType.id == Account.account_type_id)
            .filter(
                Account.company_id == company_id,
                Journal.status == "POSTED",
                Journal.journal_date >= from_date,
                Journal.journal_date <= to_date,
                AccountType.name == "ASSET",
                Account.name.ilike("%cash%"),
            )
            .first()
        )
        net_income_data = self.income_statement(db, company_id, from_date, to_date)
        net_income = Decimal(str(net_income_data["net_profit"]))
        cash_change = cash_rows.net if cash_rows and cash_rows.net else Decimal("0")
        return {
            "company_id": str(company_id),
            "from_date": str(from_date),
            "to_date": str(to_date),
            "net_income": float(net_income),
            "operating_activities": float(net_income),
            "investing_activities": 0.0,
            "financing_activities": 0.0,
            "net_cash_change": float(cash_change),
        }

    def aged_receivables(self, db: Session, company_id: UUID, as_of_date: date) -> Dict:
        invoices = db.query(Invoice).filter(
            Invoice.company_id == company_id,
            Invoice.invoice_type == "CUSTOMER",
            Invoice.status.in_(["POSTED", "PARTIALLY_PAID"]),
        ).all()
        buckets = {"current": Decimal("0"), "1_30": Decimal("0"), "31_60": Decimal("0"), "61_90": Decimal("0"), "over_90": Decimal("0")}
        lines = []
        for inv in invoices:
            outstanding = inv.total_amount - inv.paid_amount
            if outstanding <= 0:
                continue
            days_overdue = (as_of_date - (inv.due_date or inv.invoice_date)).days if inv.due_date else 0
            if days_overdue <= 0:
                buckets["current"] += outstanding
            elif days_overdue <= 30:
                buckets["1_30"] += outstanding
            elif days_overdue <= 60:
                buckets["31_60"] += outstanding
            elif days_overdue <= 90:
                buckets["61_90"] += outstanding
            else:
                buckets["over_90"] += outstanding
            lines.append({
                "invoice_id": str(inv.id),
                "invoice_number": inv.invoice_number,
                "invoice_date": str(inv.invoice_date),
                "due_date": str(inv.due_date) if inv.due_date else None,
                "outstanding": float(outstanding),
                "days_overdue": days_overdue,
            })
        return {
            "company_id": str(company_id),
            "as_of_date": str(as_of_date),
            "lines": lines,
            "buckets": {k: float(v) for k, v in buckets.items()},
            "total_outstanding": float(sum(buckets.values())),
        }

    def aged_payables(self, db: Session, company_id: UUID, as_of_date: date) -> Dict:
        invoices = db.query(Invoice).filter(
            Invoice.company_id == company_id,
            Invoice.invoice_type == "SUPPLIER",
            Invoice.status.in_(["POSTED", "PARTIALLY_PAID"]),
        ).all()
        buckets = {"current": Decimal("0"), "1_30": Decimal("0"), "31_60": Decimal("0"), "61_90": Decimal("0"), "over_90": Decimal("0")}
        lines = []
        for inv in invoices:
            outstanding = inv.total_amount - inv.paid_amount
            if outstanding <= 0:
                continue
            days_overdue = (as_of_date - (inv.due_date or inv.invoice_date)).days if inv.due_date else 0
            if days_overdue <= 0:
                buckets["current"] += outstanding
            elif days_overdue <= 30:
                buckets["1_30"] += outstanding
            elif days_overdue <= 60:
                buckets["31_60"] += outstanding
            elif days_overdue <= 90:
                buckets["61_90"] += outstanding
            else:
                buckets["over_90"] += outstanding
            lines.append({
                "invoice_id": str(inv.id),
                "invoice_number": inv.invoice_number,
                "outstanding": float(outstanding),
                "days_overdue": days_overdue,
            })
        return {
            "company_id": str(company_id),
            "as_of_date": str(as_of_date),
            "lines": lines,
            "buckets": {k: float(v) for k, v in buckets.items()},
            "total_outstanding": float(sum(buckets.values())),
        }

    def kpi_dashboard(self, db: Session, company_id: UUID, from_date: date, to_date: date) -> Dict:
        pl = self.income_statement(db, company_id, from_date, to_date)
        ar = self.aged_receivables(db, company_id, to_date)
        ap = self.aged_payables(db, company_id, to_date)
        return {
            "company_id": str(company_id),
            "period": {"from": str(from_date), "to": str(to_date)},
            "total_revenue": pl["total_revenue"],
            "total_expense": pl["total_expense"],
            "net_profit": pl["net_profit"],
            "total_receivables": ar["total_outstanding"],
            "total_payables": ap["total_outstanding"],
        }

    def budget_vs_actual(self, db: Session, company_id: UUID, budget_id: UUID, from_date: date, to_date: date) -> Dict:
        budget = db.get(Budget, budget_id)
        if not budget:
            return {"error": "Budget not found"}
        budget_lines = db.query(BudgetLine).filter(
            BudgetLine.budget_id == budget_id,
            BudgetLine.period_date >= from_date,
            BudgetLine.period_date <= to_date,
        ).all()
        actual = self.trial_balance(db, company_id, to_date)
        actual_map = {r["account_id"]: r["balance"] for r in actual["lines"]}
        lines = []
        for bl in budget_lines:
            act = actual_map.get(str(bl.account_id), 0.0)
            variance = float(bl.amount) - act
            lines.append({
                "account_id": str(bl.account_id),
                "period_date": str(bl.period_date),
                "budget": float(bl.amount),
                "actual": act,
                "variance": variance,
                "variance_pct": (variance / float(bl.amount) * 100) if bl.amount else 0,
            })
        return {
            "company_id": str(company_id),
            "budget_id": str(budget_id),
            "from_date": str(from_date),
            "to_date": str(to_date),
            "lines": lines,
        }

    def forecast_pl(self, db: Session, company_id: UUID, months_ahead: int = 3) -> Dict:
        today = date.today()
        forecasts = []
        for m in range(1, months_ahead + 1):
            target_month = today.replace(day=1) + timedelta(days=32 * m)
            target_month = target_month.replace(day=1)
            historical_months = []
            for h in range(1, 4):
                hist_month = target_month.replace(day=1) - timedelta(days=30 * h)
                from_d = hist_month.replace(day=1)
                if hist_month.month == 12:
                    to_d = hist_month.replace(month=12, day=31)
                else:
                    to_d = hist_month.replace(month=hist_month.month + 1, day=1) - timedelta(days=1)
                pl = self.income_statement(db, company_id, from_d, to_d)
                historical_months.append({"revenue": pl["total_revenue"], "expense": pl["total_expense"]})
            avg_revenue = sum(h["revenue"] for h in historical_months) / len(historical_months) if historical_months else 0
            avg_expense = sum(h["expense"] for h in historical_months) / len(historical_months) if historical_months else 0
            forecasts.append({
                "period": str(target_month),
                "forecasted_revenue": round(avg_revenue, 2),
                "forecasted_expense": round(avg_expense, 2),
                "forecasted_net_profit": round(avg_revenue - avg_expense, 2),
            })
        return {"company_id": str(company_id), "months_ahead": months_ahead, "forecasts": forecasts}

    def farm_batch_performance(self, db: Session, company_id: UUID, farm_id: Optional[UUID] = None, from_date: Optional[date] = None, to_date: Optional[date] = None) -> Dict:
        q = db.query(LivestockBatch).filter(LivestockBatch.company_id == company_id)
        if farm_id:
            q = q.filter(LivestockBatch.farm_id == farm_id)
        batches = q.all()
        result = []
        for batch in batches:
            feed_q = db.query(func.sum(FeedRecord.quantity_kg), func.sum(FeedRecord.total_cost)).filter(FeedRecord.batch_id == batch.id)
            if from_date:
                feed_q = feed_q.filter(FeedRecord.feed_date >= from_date)
            if to_date:
                feed_q = feed_q.filter(FeedRecord.feed_date <= to_date)
            feed_row = feed_q.first()
            total_feed_kg = float(feed_row[0] or 0)
            total_feed_cost = float(feed_row[1] or 0)
            prod_q = db.query(func.sum(ProductionRecord.quantity)).filter(ProductionRecord.batch_id == batch.id)
            if from_date:
                prod_q = prod_q.filter(ProductionRecord.production_date >= from_date)
            if to_date:
                prod_q = prod_q.filter(ProductionRecord.production_date <= to_date)
            prod_row = prod_q.first()
            total_produced_kg = float(prod_row[0] or 0)
            mort_q = db.query(func.sum(MortalityRecord.count)).filter(MortalityRecord.batch_id == batch.id)
            if from_date:
                mort_q = mort_q.filter(MortalityRecord.record_date >= from_date)
            if to_date:
                mort_q = mort_q.filter(MortalityRecord.record_date <= to_date)
            mort_row = mort_q.first()
            total_mortality = int(mort_row[0] or 0)
            mortality_rate = (total_mortality / batch.initial_count * 100) if batch.initial_count > 0 else 0
            fcr = (total_feed_kg / total_produced_kg) if total_produced_kg > 0 else 0
            cost_per_kg = (total_feed_cost / total_produced_kg) if total_produced_kg > 0 else 0
            result.append({
                "batch_id": str(batch.id),
                "batch_number": batch.batch_number,
                "species": batch.species,
                "initial_count": batch.initial_count,
                "current_count": batch.current_count,
                "mortality_count": total_mortality,
                "mortality_rate_pct": round(mortality_rate, 2),
                "total_feed_kg": total_feed_kg,
                "total_feed_cost": total_feed_cost,
                "total_produced_kg": total_produced_kg,
                "fcr": round(fcr, 3),
                "cost_per_kg": round(cost_per_kg, 4),
            })
        return {"company_id": str(company_id), "batches": result}

    def farm_production_output(self, db: Session, company_id: UUID, from_date: date, to_date: date) -> Dict:
        rows = db.query(
            ProductionRecord.product_type,
            ProductionRecord.unit,
            func.sum(ProductionRecord.quantity).label("total_qty"),
            func.sum(ProductionRecord.total_value).label("total_value"),
        ).filter(
            ProductionRecord.company_id == company_id,
            ProductionRecord.production_date >= from_date,
            ProductionRecord.production_date <= to_date,
        ).group_by(ProductionRecord.product_type, ProductionRecord.unit).all()
        return {
            "company_id": str(company_id),
            "from_date": str(from_date),
            "to_date": str(to_date),
            "lines": [{"product_type": r.product_type, "unit": r.unit, "total_qty": float(r.total_qty or 0), "total_value": float(r.total_value or 0)} for r in rows],
        }

    def manufacturing_production_report(self, db: Session, company_id: UUID, from_date: date, to_date: date) -> Dict:
        orders = db.query(ProductionOrder).filter(
            ProductionOrder.company_id == company_id,
        ).all()
        if from_date:
            orders = [o for o in orders if not o.planned_start or o.planned_start >= from_date]
        if to_date:
            orders = [o for o in orders if not o.planned_end or o.planned_end <= to_date]
        lines = []
        for o in orders:
            consumptions = db.query(ProductionConsumption).filter(ProductionConsumption.production_order_id == o.id).all()
            total_planned_cost = sum(c.planned_quantity * c.unit_cost for c in consumptions)
            total_actual_cost = sum(c.actual_quantity * c.unit_cost for c in consumptions)
            lines.append({
                "order_number": o.order_number,
                "status": o.status,
                "planned_quantity": float(o.planned_quantity),
                "produced_quantity": float(o.produced_quantity),
                "scrap_quantity": float(o.scrap_quantity),
                "planned_cost": float(total_planned_cost),
                "actual_cost": float(total_actual_cost),
                "variance": float(total_actual_cost - total_planned_cost),
            })
        return {"company_id": str(company_id), "from_date": str(from_date), "to_date": str(to_date), "orders": lines}

    def hospitality_occupancy_report(self, db: Session, company_id: UUID, from_date: date, to_date: date) -> Dict:
        total_rooms = db.query(func.count(Room.id)).filter(Room.company_id == company_id).scalar() or 0
        reservations = db.query(Reservation).filter(
            Reservation.company_id == company_id,
            Reservation.check_in_date >= from_date,
            Reservation.check_out_date <= to_date,
            Reservation.status.in_(["CHECKED_IN", "CHECKED_OUT"]),
        ).all()
        days = (to_date - from_date).days or 1
        occupied_room_nights = sum((min(r.check_out_date, to_date) - max(r.check_in_date, from_date)).days for r in reservations)
        available_room_nights = total_rooms * days
        occupancy_pct = (occupied_room_nights / available_room_nights * 100) if available_room_nights > 0 else 0
        total_revenue = sum(r.total_amount for r in reservations)
        adr = (total_revenue / occupied_room_nights) if occupied_room_nights > 0 else Decimal("0")
        revpar = (total_revenue / available_room_nights) if available_room_nights > 0 else Decimal("0")
        return {
            "company_id": str(company_id),
            "from_date": str(from_date),
            "to_date": str(to_date),
            "total_rooms": total_rooms,
            "occupied_room_nights": occupied_room_nights,
            "available_room_nights": available_room_nights,
            "occupancy_pct": round(occupancy_pct, 2),
            "total_revenue": float(total_revenue),
            "adr": float(adr),
            "revpar": float(revpar),
        }

    def travel_booking_pipeline(self, db: Session, company_id: UUID, from_date: date, to_date: date) -> Dict:
        bookings = db.query(TravelBooking).filter(
            TravelBooking.company_id == company_id,
            TravelBooking.travel_date >= from_date,
            TravelBooking.travel_date <= to_date,
        ).all()
        by_status: Dict[str, Any] = {}
        for b in bookings:
            if b.status not in by_status:
                by_status[b.status] = {"count": 0, "total_amount": 0.0}
            by_status[b.status]["count"] += 1
            by_status[b.status]["total_amount"] += float(b.total_amount)
        return {
            "company_id": str(company_id),
            "from_date": str(from_date),
            "to_date": str(to_date),
            "by_status": by_status,
            "total_bookings": len(bookings),
            "total_revenue": float(sum(b.total_amount for b in bookings)),
            "total_commission": float(sum(b.commission_amount for b in bookings)),
        }

    def trading_sales_report(self, db: Session, company_id: UUID, from_date: date, to_date: date) -> Dict:
        orders = db.query(SalesOrder).filter(
            SalesOrder.company_id == company_id,
            SalesOrder.order_date >= from_date,
            SalesOrder.order_date <= to_date,
            SalesOrder.status.in_(["CONFIRMED", "INVOICED"]),
        ).all()
        total = sum(o.total_amount for o in orders)
        return {
            "company_id": str(company_id),
            "from_date": str(from_date),
            "to_date": str(to_date),
            "total_orders": len(orders),
            "total_revenue": float(total),
            "orders": [{"id": str(o.id), "order_number": o.order_number, "order_date": str(o.order_date), "total_amount": float(o.total_amount), "status": o.status} for o in orders],
        }

    def hrm_headcount_report(self, db: Session, company_id: UUID) -> Dict:
        rows = db.query(
            Employee.employment_type,
            func.count(Employee.id).label("count"),
        ).filter(
            Employee.company_id == company_id,
            Employee.is_active == True,
        ).group_by(Employee.employment_type).all()
        total = db.query(func.count(Employee.id)).filter(Employee.company_id == company_id, Employee.is_active == True).scalar() or 0
        return {
            "company_id": str(company_id),
            "total_headcount": total,
            "by_employment_type": [{"type": r.employment_type, "count": r.count} for r in rows],
        }

    def hrm_payroll_summary(self, db: Session, company_id: UUID, from_date: date, to_date: date) -> Dict:
        runs = db.query(PayrollRun).filter(
            PayrollRun.company_id == company_id,
            PayrollRun.period_start >= from_date,
            PayrollRun.period_end <= to_date,
        ).all()
        return {
            "company_id": str(company_id),
            "from_date": str(from_date),
            "to_date": str(to_date),
            "runs": [{"id": str(r.id), "period_start": str(r.period_start), "period_end": str(r.period_end), "status": r.status, "total_gross": float(r.total_gross), "total_deductions": float(r.total_deductions), "total_net": float(r.total_net)} for r in runs],
            "total_gross": float(sum(r.total_gross for r in runs)),
            "total_net": float(sum(r.total_net for r in runs)),
        }

    def hrm_leave_report(self, db: Session, company_id: UUID, from_date: date, to_date: date) -> Dict:
        requests = db.query(LeaveRequest).filter(
            LeaveRequest.company_id == company_id,
            LeaveRequest.start_date >= from_date,
            LeaveRequest.end_date <= to_date,
        ).all()
        by_status = {}
        for r in requests:
            by_status.setdefault(r.status, 0)
            by_status[r.status] += 1
        return {
            "company_id": str(company_id),
            "from_date": str(from_date),
            "to_date": str(to_date),
            "total_requests": len(requests),
            "by_status": by_status,
            "total_days": float(sum(r.days_requested for r in requests)),
        }

    def hrm_attendance_report(self, db: Session, company_id: UUID, from_date: date, to_date: date) -> Dict:
        rows = db.query(
            AttendanceRecord.status,
            func.count(AttendanceRecord.id).label("count"),
            func.sum(AttendanceRecord.overtime_hours).label("total_overtime"),
        ).filter(
            AttendanceRecord.company_id == company_id,
            AttendanceRecord.attendance_date >= from_date,
            AttendanceRecord.attendance_date <= to_date,
        ).group_by(AttendanceRecord.status).all()
        return {
            "company_id": str(company_id),
            "from_date": str(from_date),
            "to_date": str(to_date),
            "by_status": [{"status": r.status, "count": r.count, "total_overtime_hours": float(r.total_overtime or 0)} for r in rows],
        }

    def crm_pipeline_report(self, db: Session, company_id: UUID) -> Dict:
        rows = db.query(
            Opportunity.stage,
            func.count(Opportunity.id).label("count"),
            func.sum(Opportunity.value).label("total_value"),
            func.avg(Opportunity.probability).label("avg_probability"),
        ).filter(Opportunity.company_id == company_id).group_by(Opportunity.stage).all()
        return {
            "company_id": str(company_id),
            "pipeline": [{"stage": r.stage, "count": r.count, "total_value": float(r.total_value or 0), "avg_probability": float(r.avg_probability or 0)} for r in rows],
        }

    def crm_conversion_report(self, db: Session, company_id: UUID) -> Dict:
        total_leads = db.query(func.count(Lead.id)).filter(Lead.company_id == company_id).scalar() or 0
        qualified_leads = db.query(func.count(Lead.id)).filter(Lead.company_id == company_id, Lead.status == "QUALIFIED").scalar() or 0
        total_opps = db.query(func.count(Opportunity.id)).filter(Opportunity.company_id == company_id).scalar() or 0
        won_opps = db.query(func.count(Opportunity.id)).filter(Opportunity.company_id == company_id, Opportunity.stage == "CLOSED_WON").scalar() or 0
        lead_to_opp = (total_opps / total_leads * 100) if total_leads > 0 else 0
        opp_to_win = (won_opps / total_opps * 100) if total_opps > 0 else 0
        return {
            "company_id": str(company_id),
            "total_leads": total_leads,
            "qualified_leads": qualified_leads,
            "total_opportunities": total_opps,
            "won_opportunities": won_opps,
            "lead_to_opportunity_rate": round(lead_to_opp, 2),
            "opportunity_win_rate": round(opp_to_win, 2),
        }

    def project_status_report(self, db: Session, company_id: UUID) -> Dict:
        projects = db.query(Project).filter(Project.company_id == company_id).all()
        result = []
        for p in projects:
            tasks = db.query(ProjectTask).filter(ProjectTask.project_id == p.id).all()
            total_tasks = len(tasks)
            done_tasks = sum(1 for t in tasks if t.status == "DONE")
            progress = (done_tasks / total_tasks * 100) if total_tasks > 0 else 0
            billed = db.query(func.sum(ProjectBilling.amount)).filter(ProjectBilling.project_id == p.id).scalar() or Decimal("0")
            timesheets = db.query(func.sum(Timesheet.hours), func.sum(Timesheet.hourly_rate * Timesheet.hours)).filter(
                Timesheet.project_id == p.id, Timesheet.is_billable == True
            ).first()
            cost = float(timesheets[1] or 0)
            result.append({
                "project_id": str(p.id),
                "name": p.name,
                "status": p.status,
                "budget": float(p.budget or 0),
                "billed": float(billed),
                "cost": cost,
                "progress_pct": round(progress, 2),
                "total_tasks": total_tasks,
                "done_tasks": done_tasks,
            })
        return {"company_id": str(company_id), "projects": result}

    def project_timesheet_report(self, db: Session, company_id: UUID, from_date: date, to_date: date) -> Dict:
        rows = db.query(
            Timesheet.project_id,
            Timesheet.employee_id,
            func.sum(Timesheet.hours).label("total_hours"),
            func.sum(case((Timesheet.is_billable == True, Timesheet.hours), else_=Decimal("0"))).label("billable_hours"),
        ).filter(
            Timesheet.company_id == company_id,
            Timesheet.date >= from_date,
            Timesheet.date <= to_date,
        ).group_by(Timesheet.project_id, Timesheet.employee_id).all()
        return {
            "company_id": str(company_id),
            "from_date": str(from_date),
            "to_date": str(to_date),
            "lines": [{"project_id": str(r.project_id), "employee_id": str(r.employee_id), "total_hours": float(r.total_hours or 0), "billable_hours": float(r.billable_hours or 0)} for r in rows],
        }

    def inventory_stock_report(self, db: Session, company_id: UUID) -> Dict:
        rows = db.query(
            StockBalance.item_id,
            StockBalance.warehouse_id,
            StockBalance.quantity_on_hand,
            StockBalance.average_cost,
            (StockBalance.quantity_on_hand * StockBalance.average_cost).label("total_value"),
        ).join(Item, Item.id == StockBalance.item_id).filter(Item.company_id == company_id).all()
        return {
            "company_id": str(company_id),
            "lines": [{"item_id": str(r.item_id), "warehouse_id": str(r.warehouse_id), "quantity_on_hand": float(r.quantity_on_hand), "average_cost": float(r.average_cost), "total_value": float(r.total_value or 0)} for r in rows],
            "total_inventory_value": float(sum(r.total_value or 0 for r in rows)),
        }

    def security_user_roles_report(self, db: Session) -> Dict:
        from app.models.auth import User, UserRole, Role
        rows = db.query(User.email, User.full_name, Role.name.label("role_name")).join(
            UserRole, UserRole.user_id == User.id
        ).join(Role, Role.id == UserRole.role_id).all()
        return {
            "assignments": [{"email": r.email, "full_name": r.full_name, "role": r.role_name} for r in rows],
            "total": len(rows),
        }

    def segment_report(self, db: Session, company_id: UUID, from_date: date, to_date: date, dimension: str = "department", dimension_id: Optional[UUID] = None) -> Dict:
        filter_field = getattr(Journal, f"{dimension}_id", None)
        query = db.query(
            Account.code,
            Account.name,
            AccountType.name.label("account_type"),
            func.sum(JournalLine.functional_credit - JournalLine.functional_debit).label("net"),
        ).join(JournalLine, JournalLine.account_id == Account.id).join(Journal, Journal.id == JournalLine.journal_id).join(AccountType, AccountType.id == Account.account_type_id).filter(
            Account.company_id == company_id,
            Journal.status == "POSTED",
            Journal.journal_date >= from_date,
            Journal.journal_date <= to_date,
            AccountType.name.in_(["REVENUE", "EXPENSE"]),
        )
        if filter_field is not None and dimension_id:
            query = query.filter(filter_field == dimension_id)
        rows = query.group_by(Account.code, Account.name, AccountType.name).all()
        revenue = [{"code": r.code, "name": r.name, "amount": float(r.net or 0)} for r in rows if r.account_type == "REVENUE"]
        expenses = [{"code": r.code, "name": r.name, "amount": float(-(r.net or 0))} for r in rows if r.account_type == "EXPENSE"]
        return {
            "company_id": str(company_id),
            "dimension": dimension,
            "dimension_id": str(dimension_id) if dimension_id else None,
            "from_date": str(from_date),
            "to_date": str(to_date),
            "revenue": revenue,
            "expenses": expenses,
            "total_revenue": sum(r["amount"] for r in revenue),
            "total_expense": sum(e["amount"] for e in expenses),
        }


report_service = ReportService()
