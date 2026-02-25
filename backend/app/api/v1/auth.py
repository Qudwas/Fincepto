from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from app.core.deps import get_current_user
from app.crud.auth import get_user_by_email
from app.schemas.auth import UserLogin, Token, TokenRefresh, UserRead
from app.services.audit_service import audit_service

router = APIRouter()


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_email(db, credentials.email)
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is inactive")
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    audit_service.log(db, action="LOGIN", entity_type="User", module="AUTH", user_id=user.id, user_email=user.email, entity_id=str(user.id))
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
def refresh_token(body: TokenRefresh, db: Session = Depends(get_db)):
    payload = decode_token(body.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    user_id = payload.get("sub")
    from app.models.auth import User
    from uuid import UUID
    user = db.get(User, UUID(user_id))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    access_token = create_access_token({"sub": str(user.id)})
    new_refresh = create_refresh_token({"sub": str(user.id)})
    return Token(access_token=access_token, refresh_token=new_refresh)


@router.post("/logout")
def logout(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    audit_service.log(db, action="LOGOUT", entity_type="User", module="AUTH", user_id=current_user.id, user_email=current_user.email, entity_id=str(current_user.id))
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserRead)
def get_me(current_user=Depends(get_current_user)):
    return current_user
