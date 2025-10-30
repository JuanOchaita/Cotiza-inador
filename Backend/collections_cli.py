from __future__ import annotations
from typing import Optional, List
from contextlib import contextmanager

from sqlalchemy import Column, Integer, String, func, select, UniqueConstraint, Index
from sqlalchemy.exc import IntegrityError

# 👇 Importa la MISMA conexión y Base que usa usuarios
# user_orm debe definir: DATABASE_URL, engine, Base, Session (sessionmaker)
from user_orm import engine, Base, Session  # <-- REUTILIZAMOS, no creamos otro engine/Base


# -----------------
# Modelo ORM (mismo Base = misma BD)
# -----------------
class Collection(Base):
    __tablename__ = "collections"
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_collection_name"),
        Index("ix_collections_user_id", "user_id"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    name = Column(String(120), nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(String, server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<Collection id={self.id} user_id={self.user_id} name='{self.name}'>"


# Crea la tabla si no existe, en la MISMA BD
Base.metadata.create_all(bind=engine)


# -----------------
# Sesión segura (usa el Session de user_orm)
# -----------------
@contextmanager
def get_session():
    s = Session()  # mismo factory que usa usuarios
    try:
        yield s
        s.commit()
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()


# -----------------
# CRUD (filtrado por user_id)
# -----------------
def add_collection(user_id: int, name: str, description: Optional[str] = None) -> None:
    name = (name or "").strip()
    if not name:
        print("⚠️ El nombre no puede estar vacío.")
        return
    with get_session() as s:
        exists = s.execute(
            select(Collection).where(
                Collection.user_id == user_id,
                Collection.name == name
            )
        ).scalars().first()
        if exists:
            print("⚠️ Ya tenés una colección con ese nombre.")
            return
        s.add(Collection(user_id=user_id, name=name, description=description))
        print("✅ Colección creada.")


def list_collections(user_id: int) -> List[Collection]:
    with get_session() as s:
        rows = s.execute(
            select(Collection)
            .where(Collection.user_id == user_id)
            .order_by(Collection.id.asc())
        ).scalars().all()
        return rows or []  # nunca None


def delete_collection_by_id(user_id: int, cid: int) -> None:
    with get_session() as s:
        obj = s.execute(
            select(Collection).where(
                Collection.user_id == user_id,
                Collection.id == cid
            )
        ).scalars().first()
        if not obj:
            print("⚠️ No encontrada.")
            return
        s.delete(obj)
        print(f"✅ Eliminada: {obj.name}")


def delete_collection_by_name(user_id: int, name: str) -> None:
    with get_session() as s:
        obj = s.execute(
            select(Collection).where(
                Collection.user_id == user_id,
                Collection.name == (name or "").strip()
            )
        ).scalars().first()
        if not obj:
            print("⚠️ No encontrada.")
            return
        s.delete(obj)
        print(f"✅ Eliminada: {obj.name}")