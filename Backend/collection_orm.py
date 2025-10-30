from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, DECIMAL, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Configuración de la conexión a PostgreSQL
DATABASE_URL = "postgresql+psycopg2://myuser:mypassword@localhost:5433/mydb"
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# Definición del modelo ORM para la tabla "user"
class User(Base):
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    email = Column(String, unique=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relación con collections
    collections = relationship("Collection", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.user_id}, name='{self.name}', email='{self.email}')>"


# Definición del modelo ORM para la tabla "collection"
class Collection(Base):
    __tablename__ = 'collection'
    collection_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    user_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)
    exchange_rate = Column(DECIMAL)
    collection_price_usd = Column(DECIMAL)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relación con user
    user = relationship("User", back_populates="collections")

    def __repr__(self):
        return (f"<Collection(id={self.collection_id}, title='{self.title}', "
                f"user_id={self.user_id}, price_usd={self.collection_price_usd})>")


# Funciones CRUD para Collection
def create_collection(title: str, user_id: int, exchange_rate: float = None, collection_price_usd: float = None):
    """Crea una nueva colección"""
    new_collection = Collection(
        title=title,
        user_id=user_id,
        exchange_rate=exchange_rate,
        collection_price_usd=collection_price_usd
    )
    session.add(new_collection)
    session.commit()
    print(f"Colección creada: {new_collection}")
    return new_collection


def get_all_collections():
    """Obtiene todas las colecciones"""
    collections = session.query(Collection).all()
    print("Colecciones encontradas:", collections)
    return collections


def get_collection_by_id(collection_id: int):
    """Obtiene una colección por su ID"""
    collection = session.query(Collection).get(collection_id)
    if collection:
        print(f"Colección encontrada: {collection}")
    else:
        print(f"Colección con ID {collection_id} no encontrada")
    return collection


def get_collections_by_user(user_id: int):
    """Obtiene todas las colecciones de un usuario específico"""
    collections = session.query(Collection).filter_by(user_id=user_id).all()
    print(f"Colecciones del usuario {user_id}:", collections)
    return collections


def update_collection_title(collection_id: int, new_title: str):
    """Actualiza el título de una colección"""
    collection = session.query(Collection).get(collection_id)
    if collection:
        collection.title = new_title
        session.commit()
        print(f"Colección actualizada: {collection}")
    else:
        print("Colección no encontrada")
    return collection


def update_collection_price(collection_id: int, new_price_usd: float):
    """Actualiza el precio de una colección"""
    collection = session.query(Collection).get(collection_id)
    if collection:
        collection.collection_price_usd = new_price_usd
        session.commit()
        print(f"Precio actualizado: {collection}")
    else:
        print("Colección no encontrada")
    return collection


def update_collection_exchange_rate(collection_id: int, new_exchange_rate: float):
    """Actualiza el tipo de cambio de una colección"""
    collection = session.query(Collection).get(collection_id)
    if collection:
        collection.exchange_rate = new_exchange_rate
        session.commit()
        print(f"Tipo de cambio actualizado: {collection}")
    else:
        print("Colección no encontrada")
    return collection


def update_collection(collection_id: int, title: str = None, 
                     exchange_rate: float = None, collection_price_usd: float = None):
    """Actualiza múltiples campos de una colección"""
    collection = session.query(Collection).get(collection_id)
    if collection:
        if title is not None:
            collection.title = title
        if exchange_rate is not None:
            collection.exchange_rate = exchange_rate
        if collection_price_usd is not None:
            collection.collection_price_usd = collection_price_usd
        session.commit()
        print(f"Colección actualizada: {collection}")
    else:
        print("Colección no encontrada")
    return collection


def delete_collection(collection_id: int):
    """Elimina una colección"""
    collection = session.query(Collection).get(collection_id)
    if collection:
        session.delete(collection)
        session.commit()
        print(f"Colección eliminada: {collection}")
    else:
        print("Colección no encontrada")
    return collection


def get_collection_with_user(collection_id: int):
    """Obtiene una colección con información del usuario"""
    collection = session.query(Collection).get(collection_id)
    if collection:
        print(f"Colección: {collection.title}")
        print(f"Usuario: {collection.user.name} ({collection.user.email})")
    else:
        print("Colección no encontrada")
    return collection


# Test de las funciones CRUD
if __name__ == "__main__":
    # Crear una colección para el usuario con ID 1
    create_collection(
        title="test collection", 
        user_id=8, 
        exchange_rate=7.50, 
        collection_price_usd=0
    )
    
    # Obtener todas las colecciones
    # get_all_collections()
    
    # Obtener colección por ID
    # get_collection_by_id(1)
    
    # Obtener todas las colecciones de un usuario
    # get_collections_by_user(1)
    
    # Actualizar título de colección
    # update_collection_title(1, "Mi Colección Premium")
    
    # Actualizar precio
    # update_collection_price(1, 2000.00)
    
    # Actualizar tipo de cambio
    # update_collection_exchange_rate(1, 7.75)
    
    # Actualizar múltiples campos
    # update_collection(1, title="Colección Actualizada", collection_price_usd=2500.00)
    
    # Obtener colección con información del usuario
    # get_collection_with_user(1)
    
    # Eliminar colección
    # delete_collection(1)