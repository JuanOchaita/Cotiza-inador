from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import auth, crud, schemas
from ..db import get_session
from ..config import settings
from ..dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.AuthResponse)
def register(payload: schemas.UserCreate, db: Session = Depends(get_session)):
    try:
        user = crud.create_user(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    token = auth.create_access_token(
        subject=user.email,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return schemas.AuthResponse(
        access_token=token,
        user=schemas.UserOut.model_validate(user, from_attributes=True),
    )


@router.post("/login", response_model=schemas.AuthResponse)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_session)):
    user = crud.authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas.")
    token = auth.create_access_token(
        subject=user.email,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return schemas.AuthResponse(
        access_token=token,
        user=schemas.UserOut.model_validate(user, from_attributes=True),
    )


@router.get("/me", response_model=schemas.UserOut)
def me(current_user=Depends(get_current_user)):
    return schemas.UserOut.model_validate(current_user, from_attributes=True)
