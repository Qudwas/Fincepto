from typing import Optional, List
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models.accounting import Journal, JournalLine, Account, AccountingPeriod
from fastapi import HTTPException


def post_journal(db: Session, journal_id: UUID, user_id: UUID) -> Journal:
    journal = db.get(Journal, journal_id)
    if not journal:
        raise HTTPException(status_code=404, detail="Journal not found")
    if journal.status != "DRAFT":
        raise HTTPException(status_code=400, detail="Only DRAFT journals can be posted")

    total_debit = sum(line.debit for line in journal.lines)
    total_credit = sum(line.credit for line in journal.lines)
    if abs(total_debit - total_credit) > Decimal("0.01"):
        raise HTTPException(status_code=400, detail=f"Debits ({total_debit}) must equal Credits ({total_credit})")

    period = db.query(AccountingPeriod).filter(
        AccountingPeriod.company_id == journal.company_id,
        AccountingPeriod.start_date <= journal.journal_date,
        AccountingPeriod.end_date >= journal.journal_date,
    ).first()
    if period and period.is_locked:
        raise HTTPException(status_code=400, detail="Accounting period is locked")

    journal.status = "POSTED"
    journal.posted_by = user_id
    journal.posted_at = datetime.utcnow()
    for line in journal.lines:
        line.functional_debit = line.debit * journal.exchange_rate
        line.functional_credit = line.credit * journal.exchange_rate
    db.commit()
    db.refresh(journal)
    return journal


def reverse_journal(db: Session, journal_id: UUID, user_id: UUID, reversal_date: date, description: str = None) -> Journal:
    original = db.get(Journal, journal_id)
    if not original:
        raise HTTPException(status_code=404, detail="Journal not found")
    if original.status != "POSTED":
        raise HTTPException(status_code=400, detail="Only POSTED journals can be reversed")

    reversal = Journal(
        company_id=original.company_id,
        reference=f"REV-{original.reference}",
        description=description or f"Reversal of {original.reference}",
        journal_date=reversal_date,
        currency_id=original.currency_id,
        exchange_rate=original.exchange_rate,
        status="DRAFT",
        is_reversal=True,
        reversed_journal_id=original.id,
        business_line_id=original.business_line_id,
        location_id=original.location_id,
        department_id=original.department_id,
        cost_center_id=original.cost_center_id,
        project_id=original.project_id,
        created_by=user_id,
    )
    db.add(reversal)
    db.flush()

    for line in original.lines:
        rev_line = JournalLine(
            journal_id=reversal.id,
            account_id=line.account_id,
            debit=line.credit,
            credit=line.debit,
            description=line.description,
            currency_id=line.currency_id,
            functional_debit=line.functional_credit,
            functional_credit=line.functional_debit,
        )
        db.add(rev_line)

    reversal.status = "POSTED"
    reversal.posted_by = user_id
    reversal.posted_at = datetime.utcnow()
    original.status = "REVERSED"
    db.commit()
    db.refresh(reversal)
    return reversal


def get_account_balances(db: Session, company_id: UUID, from_date: date, to_date: date) -> dict:
    rows = (
        db.query(
            JournalLine.account_id,
            func.sum(JournalLine.functional_debit).label("total_debit"),
            func.sum(JournalLine.functional_credit).label("total_credit"),
        )
        .join(Journal, Journal.id == JournalLine.journal_id)
        .filter(
            Journal.company_id == company_id,
            Journal.status == "POSTED",
            Journal.journal_date >= from_date,
            Journal.journal_date <= to_date,
        )
        .group_by(JournalLine.account_id)
        .all()
    )
    return {str(r.account_id): {"debit": r.total_debit or Decimal("0"), "credit": r.total_credit or Decimal("0")} for r in rows}
