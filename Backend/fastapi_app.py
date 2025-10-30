from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

# Reusamos tu lógica existente (NO cambiamos nada interno)
from collections_cli import (
    list_collections,
    add_collection,
    delete_collection_by_id,
    delete_collection_by_name,
)

app = FastAPI(title="Cotiza-inador Local HTTPS", version="0.1.0")


# ---------- Modelos de request/response ----------
class CollectionOut(BaseModel):
    id: int
    user_id: int = Field(..., alias="owner_id")  # si tu dict usa 'owner_id', cámbialo acá
    name: str
    description: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        populate_by_name = True  # permite responder como user_id si el dict trae owner_id


class CollectionCreate(BaseModel):
    user_id: int
    name: str
    description: Optional[str] = None


class DeleteByName(BaseModel):
    user_id: int
    name: str


# ---------- Rutas básicas ----------
@app.get("/")
def root():
    return {"status": "ok", "https": True}


@app.get("/ping")
def ping():
    return {"pong": True}


# ---------- Colecciones ----------
@app.get("/collections/{user_id}", response_model=List[Dict[str, Any]])
def api_list_collections(user_id: int):
    """
    Devuelve las colecciones del usuario (lo que retorne tu list_collections).
    No imponemos un esquema fijo para no romper tu salida actual (dicts).
    """
    try:
        rows = list_collections(user_id)
        # rows ya es una lista de dicts en tu implementación actual
        return rows or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar: {e}")


@app.post("/collections", status_code=201)
def api_add_collection(payload: CollectionCreate):
    """
    Crea una colección para el usuario.
    """
    try:
        add_collection(payload.user_id, payload.name, payload.description)
        return {"ok": True, "message": "Colección creada."}
    except Exception as e:
        # Tu capa imprime mensajes; acá devolvemos el error como HTTP
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/collections/{user_id}/{collection_id}")
def api_delete_collection_by_id(user_id: int, collection_id: int):
    """
    Elimina por ID (scoped al usuario).
    """
    try:
        delete_collection_by_id(user_id, collection_id)
        return {"ok": True, "message": "Colección eliminada (si existía)."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/collections/by-name")
def api_delete_collection_by_name(payload: DeleteByName):
    """
    Elimina por nombre exacto (scoped al usuario).
    """
    try:
        delete_collection_by_name(payload.user_id, payload.name)
        return {"ok": True, "message": "Colección eliminada (si existía)."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
