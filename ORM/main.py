from fastapi import FastAPI, HTTPException
from typing import List

import user_orm as user_mod
import collection_orm as collection_mod
import card_in_collection_orm as card_mod

app = FastAPI(title="Colecciones de Cartas API")

# ------------------ USUARIOS ------------------

@app.post("/users/")
def create_user(name: str, email: str):
    try:
        return user_mod.create_user(name, email)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

#@app.get("/users/", response_model=List[dict])
#def get_users():
#    return user_mod.get_all_users()

@app.get("/users/{email}")
def get_user(email: str):
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

@app.post("/collections/")
def create_collection(title: str, user_id: int, exchange_rate: float = None, collection_price_usd: float = None):
    try:
        return collection_mod.create_collection(title, user_id, exchange_rate, collection_price_usd)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/collections/", response_model=List[dict])
def get_collections():
    return collection_mod.get_all_collections()

@app.get("/collections/{collection_id}")
def get_collection(collection_id: int):
    collection = collection_mod.get_collection_by_id(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Colección no encontrada")
    return collection

@app.put("/collections/{collection_id}")
def update_collection(collection_id: int, title: str = None, exchange_rate: float = None, collection_price_usd: float = None):
    collection = collection_mod.update_collection(collection_id, title, exchange_rate, collection_price_usd)
    if not collection:
        raise HTTPException(status_code=404, detail="Colección no encontrada")
    return collection

@app.delete("/collections/{collection_id}")
def delete_collection(collection_id: int):
    collection = collection_mod.delete_collection(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Colección no encontrada")
    return {"message": "Colección eliminada"}

# ------------------ CARTAS EN COLECCIONES ------------------

@app.post("/cards_in_collection/")
def add_card(collection_id: int, card_id: int, condition_id: int, quantity: int = 1):
    card = card_mod.add_card_to_collection(collection_id, card_id, condition_id, quantity)
    if not card:
        raise HTTPException(status_code=400, detail="No se pudo añadir la carta")
    return card

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

