from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.models.ar_ap import Customer, Supplier, Invoice, InvoiceLine, Payment, PaymentAllocation
from app.schemas.ar_ap import CustomerCreate, CustomerRead, SupplierCreate, SupplierRead, InvoiceCreate, InvoiceRead, PaymentCreate, PaymentRead, PaymentAllocationCreate
from app.services.audit_service import audit_service

router = APIRouter()


@router.get("/customers", response_model=List[CustomerRead], dependencies=[Depends(require_permission("ACCOUNTING_VIEW"))])
def list_customers(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(Customer).filter(Customer.company_id == company_id).all()


@router.post("/customers", response_model=CustomerRead, dependencies=[Depends(require_permission("ACCOUNTING_POST"))])
def create_customer(body: CustomerCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = Customer(**body.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    audit_service.log(db, action="CREATE", entity_type="Customer", module="AR", user_id=current_user.id, user_email=current_user.email, entity_id=str(obj.id))
    return obj


@router.get("/customers/{cust_id}", response_model=CustomerRead, dependencies=[Depends(require_permission("ACCOUNTING_VIEW"))])
def get_customer(cust_id: UUID, db: Session = Depends(get_db)):
    obj = db.get(Customer, cust_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Customer not found")
    return obj


@router.get("/suppliers", response_model=List[SupplierRead], dependencies=[Depends(require_permission("ACCOUNTING_VIEW"))])
def list_suppliers(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(Supplier).filter(Supplier.company_id == company_id).all()


@router.post("/suppliers", response_model=SupplierRead, dependencies=[Depends(require_permission("ACCOUNTING_POST"))])
def create_supplier(body: SupplierCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = Supplier(**body.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    audit_service.log(db, action="CREATE", entity_type="Supplier", module="AP", user_id=current_user.id, user_email=current_user.email, entity_id=str(obj.id))
    return obj


@router.get("/invoices", response_model=List[InvoiceRead], dependencies=[Depends(require_permission("ACCOUNTING_VIEW"))])
def list_invoices(company_id: UUID, invoice_type: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Invoice).filter(Invoice.company_id == company_id)
    if invoice_type:
        q = q.filter(Invoice.invoice_type == invoice_type)
    return q.order_by(Invoice.invoice_date.desc()).all()


@router.post("/invoices", response_model=InvoiceRead, dependencies=[Depends(require_permission("ACCOUNTING_POST"))])
def create_invoice(body: InvoiceCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    from decimal import Decimal
    lines_data = body.model_dump(exclude={"lines"})
    lines_data["created_by"] = current_user.id
    subtotal = sum(l.line_total for l in body.lines)
    tax_amount = Decimal("0")
    lines_data["subtotal"] = subtotal
    lines_data["tax_amount"] = tax_amount
    lines_data["total_amount"] = subtotal + tax_amount
    inv = Invoice(**lines_data)
    db.add(inv)
    db.flush()
    for ld in body.lines:
        line = InvoiceLine(invoice_id=inv.id, **ld.model_dump())
        db.add(line)
    db.commit()
    db.refresh(inv)
    audit_service.log(db, action="CREATE", entity_type="Invoice", module="AR", user_id=current_user.id, user_email=current_user.email, entity_id=str(inv.id))
    return inv


@router.post("/invoices/{invoice_id}/post", dependencies=[Depends(require_permission("ACCOUNTING_POST"))])
def post_invoice(invoice_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    inv = db.get(Invoice, invoice_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if inv.status != "DRAFT":
        raise HTTPException(status_code=400, detail="Only DRAFT invoices can be posted")
    inv.status = "POSTED"
    db.commit()
    audit_service.log(db, action="POST_INVOICE", entity_type="Invoice", module="AR", user_id=current_user.id, user_email=current_user.email, entity_id=str(invoice_id))
    return {"message": "Invoice posted"}


@router.get("/payments", response_model=List[PaymentRead], dependencies=[Depends(require_permission("ACCOUNTING_VIEW"))])
def list_payments(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(Payment).filter(Payment.company_id == company_id).all()


@router.post("/payments", response_model=PaymentRead, dependencies=[Depends(require_permission("ACCOUNTING_POST"))])
def create_payment(body: PaymentCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = Payment(**body.model_dump(), created_by=current_user.id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    audit_service.log(db, action="CREATE", entity_type="Payment", module="AR", user_id=current_user.id, user_email=current_user.email, entity_id=str(obj.id))
    return obj


@router.post("/payments/allocate", dependencies=[Depends(require_permission("ACCOUNTING_POST"))])
def allocate_payment(body: PaymentAllocationCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    payment = db.get(Payment, body.payment_id)
    invoice = db.get(Invoice, body.invoice_id)
    if not payment or not invoice:
        raise HTTPException(status_code=404, detail="Payment or invoice not found")
    alloc = PaymentAllocation(**body.model_dump())
    db.add(alloc)
    invoice.paid_amount = (invoice.paid_amount or 0) + body.allocated_amount
    if invoice.paid_amount >= invoice.total_amount:
        invoice.status = "PAID"
    elif invoice.paid_amount > 0:
        invoice.status = "PARTIALLY_PAID"
    db.commit()
    audit_service.log(db, action="PAYMENT_ALLOCATION", entity_type="Payment", module="AR", user_id=current_user.id, user_email=current_user.email, entity_id=str(body.payment_id))
    return {"message": "Payment allocated"}
