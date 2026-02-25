from typing import List
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.models.hospitality import RoomType, Room, Reservation, POSOutlet, POSSale, POSSaleLine
from app.schemas.hospitality import RoomTypeCreate, RoomTypeRead, RoomCreate, RoomRead, ReservationCreate, ReservationRead, POSOutletCreate, POSOutletRead, POSSaleCreate, POSSaleRead
from app.services.audit_service import audit_service

router = APIRouter()


@router.get("/room-types", response_model=List[RoomTypeRead], dependencies=[Depends(require_permission("HOSPITALITY_MANAGE"))])
def list_room_types(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(RoomType).filter(RoomType.company_id == company_id).all()


@router.post("/room-types", response_model=RoomTypeRead, dependencies=[Depends(require_permission("HOSPITALITY_MANAGE"))])
def create_room_type(body: RoomTypeCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = RoomType(**body.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/rooms", response_model=List[RoomRead], dependencies=[Depends(require_permission("HOSPITALITY_MANAGE"))])
def list_rooms(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(Room).filter(Room.company_id == company_id).all()


@router.post("/rooms", response_model=RoomRead, dependencies=[Depends(require_permission("HOSPITALITY_MANAGE"))])
def create_room(body: RoomCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = Room(**body.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/reservations", response_model=List[ReservationRead], dependencies=[Depends(require_permission("HOSPITALITY_MANAGE"))])
def list_reservations(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(Reservation).filter(Reservation.company_id == company_id).order_by(Reservation.check_in_date.desc()).all()


@router.post("/reservations", response_model=ReservationRead, dependencies=[Depends(require_permission("HOSPITALITY_MANAGE"))])
def create_reservation(body: ReservationCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    data = body.model_dump()
    data["created_by"] = current_user.id
    obj = Reservation(**data)
    db.add(obj)
    room = db.get(Room, body.room_id)
    if room:
        room.status = "OCCUPIED"
    db.commit()
    db.refresh(obj)
    audit_service.log(db, action="CREATE", entity_type="Reservation", module="HOSPITALITY", user_id=current_user.id, user_email=current_user.email, entity_id=str(obj.id))
    return obj


@router.post("/reservations/{res_id}/check-in", dependencies=[Depends(require_permission("HOSPITALITY_MANAGE"))])
def check_in(res_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = db.get(Reservation, res_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Reservation not found")
    obj.status = "CHECKED_IN"
    obj.actual_check_in = datetime.utcnow()
    db.commit()
    audit_service.log(db, action="CHECK_IN", entity_type="Reservation", module="HOSPITALITY", user_id=current_user.id, user_email=current_user.email, entity_id=str(res_id))
    return {"message": "Checked in"}


@router.post("/reservations/{res_id}/check-out", dependencies=[Depends(require_permission("HOSPITALITY_MANAGE"))])
def check_out(res_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = db.get(Reservation, res_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Reservation not found")
    obj.status = "CHECKED_OUT"
    obj.actual_check_out = datetime.utcnow()
    room = db.get(Room, obj.room_id)
    if room:
        room.status = "CLEANING"
    db.commit()
    audit_service.log(db, action="CHECK_OUT", entity_type="Reservation", module="HOSPITALITY", user_id=current_user.id, user_email=current_user.email, entity_id=str(res_id))
    return {"message": "Checked out"}


@router.get("/pos-outlets", response_model=List[POSOutletRead], dependencies=[Depends(require_permission("HOSPITALITY_MANAGE"))])
def list_outlets(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(POSOutlet).filter(POSOutlet.company_id == company_id).all()


@router.post("/pos-outlets", response_model=POSOutletRead, dependencies=[Depends(require_permission("HOSPITALITY_MANAGE"))])
def create_outlet(body: POSOutletCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = POSOutlet(**body.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/pos-sales", response_model=List[POSSaleRead], dependencies=[Depends(require_permission("HOSPITALITY_MANAGE"))])
def list_pos_sales(company_id: UUID, outlet_id: UUID = None, db: Session = Depends(get_db)):
    q = db.query(POSSale).filter(POSSale.company_id == company_id)
    if outlet_id:
        q = q.filter(POSSale.outlet_id == outlet_id)
    return q.order_by(POSSale.sale_date.desc()).all()


@router.post("/pos-sales", response_model=POSSaleRead, dependencies=[Depends(require_permission("HOSPITALITY_MANAGE"))])
def create_pos_sale(body: POSSaleCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    from decimal import Decimal
    data = body.model_dump(exclude={"lines"})
    data["created_by"] = current_user.id
    subtotal = sum(l.line_total for l in body.lines)
    data["subtotal"] = subtotal
    data["tax_amount"] = Decimal("0")
    data["total_amount"] = subtotal
    obj = POSSale(**data)
    db.add(obj)
    db.flush()
    for ld in body.lines:
        line = POSSaleLine(pos_sale_id=obj.id, **ld.model_dump())
        db.add(line)
    db.commit()
    db.refresh(obj)
    audit_service.log(db, action="CREATE", entity_type="POSSale", module="HOSPITALITY", user_id=current_user.id, user_email=current_user.email, entity_id=str(obj.id))
    return obj
