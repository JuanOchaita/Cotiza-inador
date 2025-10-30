# collections_cli.py — CRUD de colecciones Pokémon en terminal
from __future__ import annotations
import os
from typing import Optional, List
from contextlib import contextmanager

from sqlalchemy import create_engine, Column, Integer, String, func, select
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import IntegrityError

# -----------------
# Config DB
# -----------------
# Usa SQLite por defecto para que funcione sin configurar nada
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///collections.db")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# -----------------
# Modelo ORM
# -----------------
class Collection(Base):
    __tablename__ = "collections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(120), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(String, server_default=func.now())

    def __repr__(self):
        return f"<Collection id={self.id}, name='{self.name}'>"

# Crear la tabla si no existe
Base.metadata.create_all(bind=engine)

# -----------------
# Sesión segura
# -----------------
@contextmanager
def get_session():
    s = SessionLocal()
    try:
        yield s
        s.commit()
    except Exception as e:
        s.rollback()
        print(f"⚠️ Error: {e}")
    finally:
        s.close()

# -----------------
# CRUD
# -----------------
def add_collection(name: str, description: Optional[str] = None) -> None:
    name = name.strip()
    if not name:
        print("⚠️ El nombre no puede estar vacío.")
        return
    with get_session() as s:
        if s.query(Collection).filter(Collection.name == name).first():
            print("⚠️ Ya existe una colección con ese nombre.")
            return
        new = Collection(name=name, description=description)
        s.add(new)
        print(f"✅ Colección creada: {name}")

def list_collections() -> List[Collection]:
    with get_session() as s:
        return s.query(Collection).order_by(Collection.id.asc()).all()

def delete_collection_by_id(cid: int) -> None:
    with get_session() as s:
        obj = s.get(Collection, cid)
        if not obj:
            print("⚠️ Colección no encontrada.")
            return
        s.delete(obj)
        print(f"✅ Colección eliminada: {obj.name}")

def delete_collection_by_name(name: str) -> None:
    with get_session() as s:
        obj = s.query(Collection).filter(Collection.name == name).first()
        if not obj:
            print("⚠️ Colección no encontrada.")
            return
        s.delete(obj)
        print(f"✅ Colección eliminada: {obj.name}")