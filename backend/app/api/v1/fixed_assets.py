from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.models.fixed_assets import AssetCategory, FixedAsset, DepreciationSchedule
from app.services.audit_service import audit_service

router = APIRouter()


@router.get("/categories", dependencies=[Depends(require_permission("ACCOUNTING_VIEW"))])
def list_asset_categories(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(AssetCategory).filter(AssetCategory.company_id == company_id).all()


@router.post("/categories", dependencies=[Depends(require_permission("ACCOUNTING_POST"))])
def create_asset_category(body: dict, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = AssetCategory(**{k: v for k, v in body.items() if hasattr(AssetCategory, k)})
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/assets", dependencies=[Depends(require_permission("ACCOUNTING_VIEW"))])
def list_assets(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(FixedAsset).filter(FixedAsset.company_id == company_id).all()


@router.post("/assets", dependencies=[Depends(require_permission("ACCOUNTING_POST"))])
def create_asset(body: dict, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    data = {k: v for k, v in body.items() if hasattr(FixedAsset, k)}
    data["created_by"] = str(current_user.id)
    data["net_book_value"] = data.get("purchase_cost", 0)
    obj = FixedAsset(**data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    audit_service.log(db, action="CREATE", entity_type="FixedAsset", module="FIXED_ASSETS", user_id=current_user.id, user_email=current_user.email, entity_id=str(obj.id))
    return obj


@router.get("/assets/{asset_id}", dependencies=[Depends(require_permission("ACCOUNTING_VIEW"))])
def get_asset(asset_id: UUID, db: Session = Depends(get_db)):
    obj = db.get(FixedAsset, asset_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Asset not found")
    return obj


@router.get("/depreciation", dependencies=[Depends(require_permission("ACCOUNTING_VIEW"))])
def list_depreciation_schedules(asset_id: UUID, db: Session = Depends(get_db)):
    return db.query(DepreciationSchedule).filter(DepreciationSchedule.asset_id == asset_id).order_by(DepreciationSchedule.period_date).all()
