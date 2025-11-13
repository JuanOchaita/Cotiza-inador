from sqlalchemy import create_engine, Column, Integer, Numeric, ForeignKey, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# ==================================================
# Configuración de la conexión
# ==================================================
DATABASE_URL = "postgresql+psycopg2://myuser:mypassword@localhost:5433/mydb"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ==================================================
# Definición del modelo de la tabla price
# ==================================================
class Price(Base):
    __tablename__ = "price"

    card_id = Column(Integer, ForeignKey("card.card_id"), primary_key=True)
    condition_id = Column(Integer, ForeignKey("card_condition.condition_id"), primary_key=True)
    price_usd = Column(Numeric, nullable=False)
    date = Column(DateTime, server_default=func.now())

    # Relaciones opcionales
    card = relationship("Card", back_populates="prices")
    condition = relationship("CardCondition", back_populates="prices")


# Relaciones básicas para evitar errores de ForeignKey
class Card(Base):
    __tablename__ = "card"
    card_id = Column(Integer, primary_key=True)
    prices = relationship("Price", back_populates="card")


class CardCondition(Base):
    __tablename__ = "card_condition"
    condition_id = Column(Integer, primary_key=True)
    prices = relationship("Price", back_populates="condition")


# ==================================================
# Funciones CRUD
# ==================================================

def create_price(session, card_id, condition_id, price_usd):
    """Crea un nuevo registro en la tabla price."""
    new_price = Price(card_id=card_id, condition_id=condition_id, price_usd=price_usd)
    session.add(new_price)
    session.commit()
    print(f"Precio creado: card_id={card_id}, condition_id={condition_id}, price_usd={price_usd}")


def read_price(session, card_id, condition_id):
    """Obtiene un registro de la tabla price."""
    price = session.query(Price).filter_by(card_id=card_id, condition_id=condition_id).first()
    if price:
        print(f"Registro encontrado -> card_id={price.card_id}, condition_id={price.condition_id}, price_usd={price.price_usd}")
        return price
    else:
        print("No se encontró el registro.")
        return None


def update_price(session, card_id, condition_id, new_price_usd):
    """Actualiza el precio de un registro existente."""
    price = session.query(Price).filter_by(card_id=card_id, condition_id=condition_id).first()
    if price:
        price.price_usd = new_price_usd
        session.commit()
        print(f"Precio actualizado a {new_price_usd} USD.")
    else:
        print("No se encontró el registro para actualizar.")


def delete_price(session, card_id, condition_id):
    """Elimina un registro de la tabla price."""
    price = session.query(Price).filter_by(card_id=card_id, condition_id=condition_id).first()
    if price:
        session.delete(price)
        session.commit()
        print("Registro eliminado correctamente.")
    else:
        print("No se encontró el registro para eliminar.")


# ==================================================
# Ejemplo de uso
# ==================================================
if __name__ == "__main__":
    session = SessionLocal()

    # Crear un nuevo precio
    # create_price(session, card_id=1, condition_id=1, price_usd=50.00)

    # Leer el precio
    #read_price(session, card_id=1, condition_id=1)

    # Actualizar el precio
    update_price(session, card_id=1, condition_id=1, new_price_usd=55.00)

    # Eliminar el precio
    # delete_price(session, card_id=1, condition_id=1)

    # session.close()
