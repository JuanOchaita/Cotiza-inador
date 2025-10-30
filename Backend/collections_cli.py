from __future__ import annotations
from typing import Optional, List
from contextlib import contextmanager

from sqlalchemy import Column, Integer, String, func, select, UniqueConstraint
from sqlalchemy.exc import IntegrityError

# Reutiliza la MISMA conexión/Session/Base de user_orm
from user_orm import engine, Base, Session

# -----------------
# MODELO ORM (usa la columna real owner_id en la BD)
# -----------------
class Collection(Base):
    __tablename__ = "collections"
    __table_args__ = (
        UniqueConstraint("owner_id", "name", name="uq_user_collection_name"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column("owner_id", Integer, nullable=False, index=True)
    name = Column(String(120), nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(String, server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<Collection id={self.id} user_id={self.user_id} name='{self.name}'>"


# Crea la tabla si no existe (sin tocar la estructura existente)
Base.metadata.create_all(bind=engine, checkfirst=True)

# -----------------
# SESIÓN SEGURA
# -----------------
@contextmanager
def get_session():
    s = Session()
    try:
        yield s
        s.commit()
    except Exception as e:
        s.rollback()
        print(f"⚠️ Error en la base de datos: {e}")
        raise
    finally:
        s.close()

# -----------------
# CRUD
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

        try:
            s.add(Collection(user_id=user_id, name=name, description=description))
            print("✅ Colección creada.")
        except IntegrityError:
            print("⚠️ Error: el usuario no existe en la tabla 'user'.")


def list_collections(user_id: int) -> List[dict]:
    """Devuelve una lista de colecciones en formato dict (no objetos ORM)."""
    with get_session() as s:
        rows = s.execute(
            select(Collection)
            .where(Collection.user_id == user_id)
            .order_by(Collection.id.asc())
        ).scalars().all()

        # Convertimos los resultados en diccionarios (para evitar DetachedInstanceError)
        return [
            {
                "id": r.id,
                "name": r.name,
                "description": r.description,
                "created_at": r.created_at,
            }
            for r in rows
        ]


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
