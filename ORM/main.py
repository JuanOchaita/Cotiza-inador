from fastapi import FastAPI, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError

import user_orm as user_mod
import collection_orm as collection_mod
import card_in_collection_orm as card_mod

app = FastAPI(title="Colecciones de Cartas API")

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models expected by the frontend
class CreateUserRequest(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    user_id: int
    email: str

    class Config:
        orm_mode = True

class CreateCollectionRequest(BaseModel):
    title: str
    user_id: int

class UpdateExchangeRateRequest(BaseModel):
    new_exchange_rate: float

class AddCardRequest(BaseModel):
    collection_id: int
    condition_id: int
    quantity: int
    card_name: str
    number_in_set: str
    set_name: str
    language_id: int
    edition: str

class RemoveCardRequest(BaseModel):
    card_id: int
    collection_id: int

# ------------------ USUARIOS ------------------

@app.post("/users/", response_model=UserOut, status_code=201)
def create_user(payload: CreateUserRequest):
    try:
        return user_mod.create_user(payload.email, payload.password)
    except IntegrityError:
        # Likely duplicate email constraint
        raise HTTPException(status_code=409, detail="Email already exists")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

#@app.get("/users/", response_model=List[dict])
#def get_users():
#    return user_mod.get_all_users()

@app.get("/users/{email}", response_model=UserOut)
def get_user(email: str, password: Optional[str] = None):
    if password is not None:
        user = user_mod.get_user_by_email_and_password(email, password)
    else:
        user = user_mod.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@app.put("/users/{user_id}/email")
def update_email(user_id: int, new_email: str):
    user = user_mod.update_user_email(user_id, new_email)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    user = user_mod.delete_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"message": "Usuario eliminado"}

# ------------------ COLECCIONES ------------------


# Crear una colección
@app.post("/collections/")
def create_collection(payload: CreateCollectionRequest):
    try:
        return collection_mod.create_collection(payload.title, payload.user_id, None, None)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Obtener todas las colecciones
@app.get("/collections/", response_model=List[dict])
def get_collections():
    try:
        return collection_mod.get_all_collections()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Obtener colección por ID
@app.get("/collections/{collection_id}")
def get_collection(collection_id: int):
    collection = collection_mod.get_collection_by_id(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Colección no encontrada")
    return collection

# Obtener todas las colecciones de un usuario
@app.get("/collections/user/{user_id}")
def get_collections_by_user(user_id: int):
    try:
        return collection_mod.get_collections_by_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Actualizar título de colección
@app.put("/collections/{collection_id}/title")
def update_collection_title(collection_id: int, new_title: str):
    collection = collection_mod.update_collection_title(collection_id, new_title)
    if not collection:
        raise HTTPException(status_code=404, detail="Colección no encontrada")
    return collection

# Actualizar precio de colección
@app.put("/collections/{collection_id}/price")
def update_collection_price(collection_id: int, new_price_usd: float):
    collection = collection_mod.update_collection_price(collection_id, new_price_usd)
    if not collection:
        raise HTTPException(status_code=404, detail="Colección no encontrada")
    return collection

# Actualizar tipo de cambio de colección
@app.put("/collections/{collection_id}/exchange_rate")
def update_collection_exchange_rate(collection_id: int, payload: UpdateExchangeRateRequest):
    collection = collection_mod.update_collection_exchange_rate(collection_id, payload.new_exchange_rate)
    if not collection:
        raise HTTPException(status_code=404, detail="Colección no encontrada")
    return collection

# Actualizar múltiples campos de colección
@app.put("/collections/{collection_id}/update")
def update_collection(collection_id: int, title: str = None, exchange_rate: float = None, collection_price_usd: float = None):
    collection = collection_mod.update_collection(collection_id, title, exchange_rate, collection_price_usd)
    if not collection:
        raise HTTPException(status_code=404, detail="Colección no encontrada")
    return collection

# Obtener colección con información del usuario
@app.get("/collections/{collection_id}/with_user")
def get_collection_with_user(collection_id: int):
    collection = collection_mod.get_collection_with_user(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Colección no encontrada")
    return collection

# Eliminar colección
@app.delete("/collections/{collection_id}")
def delete_collection(collection_id: int):
    collection = collection_mod.delete_collection(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Colección no encontrada")
    return {"message": "Colección eliminada"}


# ------------------ CARTAS EN COLECCIONES ------------------

@app.post("/cards_in_collection/")
def add_card(payload: AddCardRequest):
    # The current ORM adds by card_id and validates price; it does not resolve card by names/set.
    # Until ORM supports this, return a clear error to the client.
    raise HTTPException(status_code=400, detail="Adding card by name/set is not supported yet on the backend")

# Obtener cartas de una colección (con detalles), para coincidir con el frontend
@app.get("/cards_in_collection/details/{collection_id}")
def get_cards_details_by_collection(collection_id: int):
    return card_mod.get_cards_by_collection_with_details(collection_id)

@app.get("/cards_in_collection/", response_model=List[dict])
def get_all_cards():
    return card_mod.get_all_cards_in_collections()

@app.get("/cards_in_collection/{card_collection_id}")
def get_card(card_collection_id: int):
    card = card_mod.get_card_in_collection_by_id(card_collection_id)
    if not card:
        raise HTTPException(status_code=404, detail="Carta no encontrada")
    return card

@app.put("/cards_in_collection/{card_collection_id}")
def update_card(card_collection_id: int, quantity: int = None, condition_id: int = None):
    card = card_mod.update_card_in_collection(card_collection_id, quantity, condition_id)
    if not card:
        raise HTTPException(status_code=400, detail="No se pudo actualizar la carta")
    return card

@app.delete("/cards_in_collection/{card_collection_id}")
def remove_card(card_collection_id: int):
    card = card_mod.remove_card_from_collection(card_collection_id)
    if not card:
        raise HTTPException(status_code=404, detail="Carta no encontrada")
    return {"message": "Carta eliminada"}

# Eliminar carta por payload (card_id + collection_id) para coincidir con el frontend
@app.delete("/cards_in_collection/")
def remove_card_by_payload(payload: RemoveCardRequest):
    # Remove all entries that match the given card_id within the collection
    session = card_mod.session
    CardInCollection = card_mod.CardInCollection
    matches = session.query(CardInCollection).filter_by(
        card_id=payload.card_id,
        collection_id=payload.collection_id
    ).all()
    if not matches:
        raise HTTPException(status_code=404, detail="Carta no encontrada en la colección")
    for entry in matches:
        session.delete(entry)
    session.commit()
    return {"message": f"{len(matches)} carta(s) eliminada(s)"}