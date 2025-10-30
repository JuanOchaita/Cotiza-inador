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

# Modelo User
class User(Base):
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    email = Column(String, unique=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    collections = relationship("Collection", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.user_id}, name='{self.name}', email='{self.email}')>"

# Modelo Collection
class Collection(Base):
    __tablename__ = 'collection'
    collection_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    user_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)
    exchange_rate = Column(DECIMAL)
    collection_price_usd = Column(DECIMAL)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    user = relationship("User", back_populates="collections")

    def __repr__(self):
        return (f"<Collection(id={self.collection_id}, title='{self.title}', "
                f"user_id={self.user_id}, price_usd={self.collection_price_usd})>")

# Funciones CRUD
def create_collection(title: str, user_id: int, exchange_rate: float = 7.66, collection_price_usd: float = 0):
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

def delete_collection(collection_id: int):
    collection = session.query(Collection).get(collection_id)
    if collection:
        session.delete(collection)
        session.commit()
        print(f"Colección eliminada: {collection}")
    else:
        print("Colección no encontrada")
    return collection

def get_collections_by_user(user_id: int):
    """Obtiene todas las colecciones de un usuario"""
    collections = session.query(Collection).filter_by(user_id=user_id).all()
    if collections:
        print(f"\nColecciones del usuario {user_id}:")
        for c in collections:
            print(f"- {c.title} (ID: {c.collection_id}, USD: {c.collection_price_usd})")
    else:
        print("\nNo hay colecciones para este usuario.")
    return collections

# Menú interactivo
def collection_menu(user_id):
    while True:
        print("\nMenú de Opciones:")
        print("1. Ver colección")
        print("2. Crear colección")
        print("3. Eliminar colección")
        print("4. Salir")

        option = input("Seleccione una opción (1-4): ").strip()

        if option == "1":
            get_collections_by_user(user_id)  # Mostrar todas las colecciones
            title = input("\nIngrese el nombre de la colección: ").strip()
            collection = session.query(Collection).filter_by(user_id=user_id, title=title).first()
            if collection:
                print(f"\nColección encontrada: {collection}")
                print(f"Usuario: {collection.user.name} ({collection.user.email})")
                print(f"Precio USD: {collection.collection_price_usd}")
                print(f"Tipo de cambio: {collection.exchange_rate}")
                return collection.collection_id  # Retorna el ID de la colección
            
            elif not session.query(Collection).filter_by(user_id=user_id).all():
                print("\nNo tienes colecciones")
                
            else:
                print("\nColección no encontrada.")

        elif option == "2":
            title = input("\nIngrese el título de la nueva colección: ").strip()
            create_collection(title, user_id)

        elif option == "3":
            get_collections_by_user(user_id)  # Mostrar todas las colecciones
            title = input("\nIngrese el nombre de la colección a eliminar: ").strip()
            collection = session.query(Collection).filter_by(user_id=user_id, title=title).first()
            if collection:
                confirm = input(f"¿Confirma eliminar la colección '{title}'? (s/n): ").strip().lower()
                if confirm == "s":
                    delete_collection(collection.collection_id)
                else:
                    print("\nEliminación cancelada.")
            else:
                print("\nColección no encontrada.")

        elif option == "4":
            print("Saliendo del menú...")
            return None  # Retorna None si el usuario sale

        else:
            print("Opción no válida, intente nuevamente.")

if __name__ == "__main__":
    Base.metadata.create_all(engine)  # Crea las tablas si no existen
    user_id = int(input("Ingrese su User ID: "))
    selected_collection_id = collection_menu(user_id)
    if selected_collection_id:
        print(f"\nID de la colección seleccionada: {selected_collection_id}")
    else:
        print("\nNo se seleccionó ninguna colección.")
