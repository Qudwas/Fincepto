from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.models.farm import Farm, LivestockBatch, FeedRecord, ProductionRecord, MortalityRecord
from app.schemas.farm import FarmCreate, FarmRead, LivestockBatchCreate, LivestockBatchRead, FeedRecordCreate, FeedRecordRead, ProductionRecordCreate, ProductionRecordRead, MortalityRecordCreate, MortalityRecordRead
from app.services.audit_service import audit_service

router = APIRouter()


@router.get("/farms", response_model=List[FarmRead], dependencies=[Depends(require_permission("FARM_MANAGE"))])
def list_farms(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(Farm).filter(Farm.company_id == company_id).all()


@router.post("/farms", response_model=FarmRead, dependencies=[Depends(require_permission("FARM_MANAGE"))])
def create_farm(body: FarmCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = Farm(**body.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    audit_service.log(db, action="CREATE", entity_type="Farm", module="FARM", user_id=current_user.id, user_email=current_user.email, entity_id=str(obj.id))
    return obj


@router.get("/batches", response_model=List[LivestockBatchRead], dependencies=[Depends(require_permission("FARM_MANAGE"))])
def list_batches(company_id: UUID, farm_id: UUID = None, db: Session = Depends(get_db)):
    q = db.query(LivestockBatch).filter(LivestockBatch.company_id == company_id)
    if farm_id:
        q = q.filter(LivestockBatch.farm_id == farm_id)
    return q.all()


@router.post("/batches", response_model=LivestockBatchRead, dependencies=[Depends(require_permission("FARM_MANAGE"))])
def create_batch(body: LivestockBatchCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    data = body.model_dump()
    data["current_count"] = data["initial_count"]
    obj = LivestockBatch(**data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    audit_service.log(db, action="CREATE", entity_type="LivestockBatch", module="FARM", user_id=current_user.id, user_email=current_user.email, entity_id=str(obj.id))
    return obj


@router.get("/feed-records", response_model=List[FeedRecordRead], dependencies=[Depends(require_permission("FARM_MANAGE"))])
def list_feed_records(company_id: UUID, batch_id: UUID = None, db: Session = Depends(get_db)):
    q = db.query(FeedRecord).filter(FeedRecord.company_id == company_id)
    if batch_id:
        q = q.filter(FeedRecord.batch_id == batch_id)
    return q.order_by(FeedRecord.feed_date.desc()).all()


@router.post("/feed-records", response_model=FeedRecordRead, dependencies=[Depends(require_permission("FARM_MANAGE"))])
def create_feed_record(body: FeedRecordCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    data = body.model_dump()
    data["total_cost"] = data["quantity_kg"] * data["unit_cost"]
    data["created_by"] = current_user.id
    obj = FeedRecord(**data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    audit_service.log(db, action="CREATE", entity_type="FeedRecord", module="FARM", user_id=current_user.id, user_email=current_user.email, entity_id=str(obj.id))
    return obj


@router.get("/production-records", response_model=List[ProductionRecordRead], dependencies=[Depends(require_permission("FARM_MANAGE"))])
def list_production_records(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(ProductionRecord).filter(ProductionRecord.company_id == company_id).order_by(ProductionRecord.production_date.desc()).all()


@router.post("/production-records", response_model=ProductionRecordRead, dependencies=[Depends(require_permission("FARM_MANAGE"))])
def create_production_record(body: ProductionRecordCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    data = body.model_dump()
    data["total_value"] = data["quantity"] * data["unit_price"]
    data["created_by"] = current_user.id
    obj = ProductionRecord(**data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    audit_service.log(db, action="CREATE", entity_type="ProductionRecord", module="FARM", user_id=current_user.id, user_email=current_user.email, entity_id=str(obj.id))
    return obj


@router.get("/mortality-records", response_model=List[MortalityRecordRead], dependencies=[Depends(require_permission("FARM_MANAGE"))])
def list_mortality_records(company_id: UUID, batch_id: UUID = None, db: Session = Depends(get_db)):
    q = db.query(MortalityRecord).filter(MortalityRecord.company_id == company_id)
    if batch_id:
        q = q.filter(MortalityRecord.batch_id == batch_id)
    return q.order_by(MortalityRecord.record_date.desc()).all()


@router.post("/mortality-records", response_model=MortalityRecordRead, dependencies=[Depends(require_permission("FARM_MANAGE"))])
def create_mortality_record(body: MortalityRecordCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = MortalityRecord(**body.model_dump())
    db.add(obj)
    db.flush()
    batch = db.get(LivestockBatch, body.batch_id)
    if batch:
        batch.current_count = max(0, batch.current_count - body.count)
    db.commit()
    db.refresh(obj)
    audit_service.log(db, action="CREATE", entity_type="MortalityRecord", module="FARM", user_id=current_user.id, user_email=current_user.email, entity_id=str(obj.id))
    return obj
