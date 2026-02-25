from typing import List, Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.models.accounting import Account, AccountType, FiscalYear, AccountingPeriod, Journal, JournalLine, TaxCode
from app.schemas.accounting import (
    AccountCreate, AccountRead, FiscalYearCreate, FiscalYearRead,
    AccountingPeriodCreate, AccountingPeriodRead, JournalCreate, JournalRead, TaxCodeCreate, TaxCodeRead
)
from app.services.audit_service import audit_service
from app.services.journal_service import journal_service

router = APIRouter()


@router.get("/account-types")
def list_account_types(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(AccountType).all()


@router.get("/accounts", response_model=List[AccountRead], dependencies=[Depends(require_permission("ACCOUNTING_VIEW"))])
def list_accounts(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(Account).filter(Account.company_id == company_id).order_by(Account.code).all()


@router.post("/accounts", response_model=AccountRead, dependencies=[Depends(require_permission("ACCOUNTING_POST"))])
def create_account(body: AccountCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = Account(**body.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    audit_service.log(db, action="CREATE", entity_type="Account", module="ACCOUNTING", user_id=current_user.id, user_email=current_user.email, entity_id=str(obj.id))
    return obj


@router.put("/accounts/{account_id}", response_model=AccountRead, dependencies=[Depends(require_permission("ACCOUNTING_POST"))])
def update_account(account_id: UUID, body: AccountCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = db.get(Account, account_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Account not found")
    for k, v in body.model_dump().items():
        if hasattr(obj, k):
            setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    audit_service.log(db, action="UPDATE", entity_type="Account", module="ACCOUNTING", user_id=current_user.id, user_email=current_user.email, entity_id=str(obj.id))
    return obj


@router.get("/fiscal-years", response_model=List[FiscalYearRead], dependencies=[Depends(require_permission("ACCOUNTING_VIEW"))])
def list_fiscal_years(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(FiscalYear).filter(FiscalYear.company_id == company_id).all()


@router.post("/fiscal-years", response_model=FiscalYearRead, dependencies=[Depends(require_permission("ACCOUNTING_POST"))])
def create_fiscal_year(body: FiscalYearCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = FiscalYear(**body.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    audit_service.log(db, action="CREATE", entity_type="FiscalYear", module="ACCOUNTING", user_id=current_user.id, user_email=current_user.email, entity_id=str(obj.id))
    return obj


@router.get("/periods", response_model=List[AccountingPeriodRead], dependencies=[Depends(require_permission("ACCOUNTING_VIEW"))])
def list_periods(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(AccountingPeriod).filter(AccountingPeriod.company_id == company_id).order_by(AccountingPeriod.start_date).all()


@router.post("/periods", response_model=AccountingPeriodRead, dependencies=[Depends(require_permission("ACCOUNTING_POST"))])
def create_period(body: AccountingPeriodCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = AccountingPeriod(**body.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.post("/periods/{period_id}/lock", dependencies=[Depends(require_permission("ACCOUNTING_POST"))])
def lock_period(period_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    period = db.get(AccountingPeriod, period_id)
    if not period:
        raise HTTPException(status_code=404, detail="Period not found")
    period.is_locked = True
    db.commit()
    audit_service.log(db, action="LOCK_PERIOD", entity_type="AccountingPeriod", module="ACCOUNTING", user_id=current_user.id, user_email=current_user.email, entity_id=str(period_id))
    return {"message": "Period locked"}


@router.post("/periods/{period_id}/unlock", dependencies=[Depends(require_permission("SYSTEM_ADMIN"))])
def unlock_period(period_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    period = db.get(AccountingPeriod, period_id)
    if not period:
        raise HTTPException(status_code=404, detail="Period not found")
    period.is_locked = False
    db.commit()
    audit_service.log(db, action="UNLOCK_PERIOD", entity_type="AccountingPeriod", module="ACCOUNTING", user_id=current_user.id, user_email=current_user.email, entity_id=str(period_id))
    return {"message": "Period unlocked"}


@router.get("/journals", response_model=List[JournalRead], dependencies=[Depends(require_permission("ACCOUNTING_VIEW"))])
def list_journals(company_id: UUID, status: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Journal).filter(Journal.company_id == company_id)
    if status:
        q = q.filter(Journal.status == status)
    return q.order_by(Journal.journal_date.desc()).all()


@router.post("/journals", response_model=JournalRead, dependencies=[Depends(require_permission("ACCOUNTING_POST"))])
def create_journal(body: JournalCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    data = body.model_dump(exclude={"lines"})
    data["created_by"] = current_user.id
    journal = Journal(**data)
    db.add(journal)
    db.flush()
    for line_data in body.lines:
        line = JournalLine(journal_id=journal.id, **line_data.model_dump())
        line.functional_debit = line.debit
        line.functional_credit = line.credit
        db.add(line)
    db.commit()
    db.refresh(journal)
    audit_service.log(db, action="CREATE", entity_type="Journal", module="ACCOUNTING", user_id=current_user.id, user_email=current_user.email, entity_id=str(journal.id))
    return journal


@router.get("/journals/{journal_id}", response_model=JournalRead, dependencies=[Depends(require_permission("ACCOUNTING_VIEW"))])
def get_journal(journal_id: UUID, db: Session = Depends(get_db)):
    j = db.get(Journal, journal_id)
    if not j:
        raise HTTPException(status_code=404, detail="Journal not found")
    return j


@router.post("/journals/{journal_id}/post", response_model=JournalRead, dependencies=[Depends(require_permission("ACCOUNTING_POST"))])
def post_journal_endpoint(journal_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    j = journal_service.post(db, journal_id, current_user.id)
    audit_service.log(db, action="POST_JOURNAL", entity_type="Journal", module="ACCOUNTING", user_id=current_user.id, user_email=current_user.email, entity_id=str(journal_id))
    return j


@router.post("/journals/{journal_id}/reverse", response_model=JournalRead, dependencies=[Depends(require_permission("ACCOUNTING_POST"))])
def reverse_journal_endpoint(journal_id: UUID, reversal_date: date, description: Optional[str] = None, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    rev = journal_service.reverse(db, journal_id, current_user.id, reversal_date, description)
    audit_service.log(db, action="REVERSE_JOURNAL", entity_type="Journal", module="ACCOUNTING", user_id=current_user.id, user_email=current_user.email, entity_id=str(journal_id))
    return rev


@router.get("/tax-codes", response_model=List[TaxCodeRead], dependencies=[Depends(require_permission("ACCOUNTING_VIEW"))])
def list_tax_codes(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(TaxCode).filter(TaxCode.company_id == company_id).all()


@router.post("/tax-codes", response_model=TaxCodeRead, dependencies=[Depends(require_permission("ACCOUNTING_POST"))])
def create_tax_code(body: TaxCodeCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = TaxCode(**body.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    audit_service.log(db, action="CREATE", entity_type="TaxCode", module="ACCOUNTING", user_id=current_user.id, user_email=current_user.email, entity_id=str(obj.id))
    return obj
