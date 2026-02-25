from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID
from sqlalchemy.orm import Session
from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: UUID) -> Optional[ModelType]:
        return db.get(self.model, id)

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100, **filters) -> List[ModelType]:
        query = db.query(self.model)
        for key, value in filters.items():
            if value is not None and hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: Any) -> ModelType:
        if hasattr(obj_in, "model_dump"):
            obj_data = obj_in.model_dump(exclude_unset=False)
        else:
            obj_data = dict(obj_in)
        obj_data = {k: v for k, v in obj_data.items() if hasattr(self.model, k)}
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: ModelType, obj_in: Any) -> ModelType:
        if hasattr(obj_in, "model_dump"):
            update_data = obj_in.model_dump(exclude_unset=True)
        else:
            update_data = dict(obj_in)
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: UUID) -> Optional[ModelType]:
        obj = db.get(self.model, id)
        if obj:
            if hasattr(obj, "is_active"):
                obj.is_active = False
                db.add(obj)
                db.commit()
            else:
                db.delete(obj)
                db.commit()
        return obj
