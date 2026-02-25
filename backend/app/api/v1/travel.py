from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.models.travel import TravelPackage, TravelSupplier, TravelBooking, BookingSupplierCost
from app.schemas.travel import TravelPackageCreate, TravelPackageRead, TravelSupplierCreate, TravelSupplierRead, TravelBookingCreate, TravelBookingRead
from app.services.audit_service import audit_service

router = APIRouter()


@router.get("/packages", response_model=List[TravelPackageRead], dependencies=[Depends(require_permission("TRAVEL_MANAGE"))])
def list_packages(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(TravelPackage).filter(TravelPackage.company_id == company_id).all()


@router.post("/packages", response_model=TravelPackageRead, dependencies=[Depends(require_permission("TRAVEL_MANAGE"))])
def create_package(body: TravelPackageCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = TravelPackage(**body.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    audit_service.log(db, action="CREATE", entity_type="TravelPackage", module="TRAVEL", user_id=current_user.id, user_email=current_user.email, entity_id=str(obj.id))
    return obj


@router.get("/suppliers", response_model=List[TravelSupplierRead], dependencies=[Depends(require_permission("TRAVEL_MANAGE"))])
def list_travel_suppliers(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(TravelSupplier).filter(TravelSupplier.company_id == company_id).all()


@router.post("/suppliers", response_model=TravelSupplierRead, dependencies=[Depends(require_permission("TRAVEL_MANAGE"))])
def create_travel_supplier(body: TravelSupplierCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = TravelSupplier(**body.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/bookings", response_model=List[TravelBookingRead], dependencies=[Depends(require_permission("TRAVEL_MANAGE"))])
def list_bookings(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(TravelBooking).filter(TravelBooking.company_id == company_id).order_by(TravelBooking.travel_date.desc()).all()


@router.post("/bookings", response_model=TravelBookingRead, dependencies=[Depends(require_permission("TRAVEL_MANAGE"))])
def create_booking(body: TravelBookingCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    data = body.model_dump(exclude={"supplier_costs"})
    data["created_by"] = current_user.id
    obj = TravelBooking(**data)
    db.add(obj)
    db.flush()
    for sc in body.supplier_costs:
        cost = BookingSupplierCost(booking_id=obj.id, **sc.model_dump())
        db.add(cost)
    db.commit()
    db.refresh(obj)
    audit_service.log(db, action="CREATE", entity_type="TravelBooking", module="TRAVEL", user_id=current_user.id, user_email=current_user.email, entity_id=str(obj.id))
    return obj


@router.post("/bookings/{booking_id}/confirm", dependencies=[Depends(require_permission("TRAVEL_MANAGE"))])
def confirm_booking(booking_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = db.get(TravelBooking, booking_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Booking not found")
    obj.status = "CONFIRMED"
    db.commit()
    audit_service.log(db, action="CONFIRM_BOOKING", entity_type="TravelBooking", module="TRAVEL", user_id=current_user.id, user_email=current_user.email, entity_id=str(booking_id))
    return {"message": "Booking confirmed"}
