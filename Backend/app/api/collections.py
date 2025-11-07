from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..db import get_session
from ..dependencies import get_current_user
from ..models import User

router = APIRouter(prefix="/collections", tags=["collections"])


@router.get("/", response_model=list[schemas.CollectionSummary])
def list_collections(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return crud.list_collections(db, current_user.user_id)


@router.post("/", response_model=schemas.CollectionOut, status_code=status.HTTP_201_CREATED)
def create_collection(
    payload: schemas.CollectionCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El nombre es obligatorio.")
    collection = crud.create_collection(
        db,
        owner_id=current_user.user_id,
        name=name,
        description=payload.description,
    )
    return schemas.CollectionOut.model_validate(collection, from_attributes=True)


@router.get("/{collection_id}", response_model=schemas.CollectionDetail)
def collection_detail(
    collection_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    detail = crud.get_collection_detail(db, current_user.user_id, collection_id)
    if not detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Colección no encontrada.")
    return detail


@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_collection(
    collection_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    deleted = crud.delete_collection(db, current_user.user_id, collection_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Colección no encontrada.")


@router.post("/{collection_id}/cards", response_model=schemas.CardOut, status_code=status.HTTP_201_CREATED)
def add_card(
    collection_id: int,
    payload: schemas.CardCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    collection = crud.get_collection(db, current_user.user_id, collection_id)
    if not collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Colección no encontrada.")
    try:
        return crud.add_card_to_collection(db, collection=collection, payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.delete("/{collection_id}/cards/{card_collection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_card(
    collection_id: int,
    card_collection_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    deleted = crud.delete_card_from_collection(
        db,
        user_id=current_user.user_id,
        collection_id=collection_id,
        card_collection_id=card_collection_id,
    )
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carta no encontrada.")
