from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, DECIMAL, ForeignKey, func, select
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# Configuración de la conexión a PostgreSQL
DATABASE_URL = "postgresql+psycopg2://myuser:mypassword@localhost:5433/mydb"
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# Definición de los modelos ORM necesarios
class User(Base):
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    email = Column(String, unique=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    collections = relationship("Collection", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.user_id}, name='{self.name}')>"


class Collection(Base):
    __tablename__ = 'collection'
    collection_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    user_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)
    exchange_rate = Column(DECIMAL)
    collection_price_usd = Column(DECIMAL)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    user = relationship("User", back_populates="collections")
    cards = relationship("CardInCollection", back_populates="collection")

    def __repr__(self):
        return f"<Collection(id={self.collection_id}, title='{self.title}')>"


class Card(Base):
    __tablename__ = 'card'
    card_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    language_id = Column(Integer, nullable=False)
    set_name_id = Column(Integer, nullable=False)
    set_number = Column(String)
    image_id = Column(Integer, nullable=False)
    edition_id = Column(Integer)

    def __repr__(self):
        return f"<Card(id={self.card_id}, name='{self.name}')>"


class CardCondition(Base):
    __tablename__ = 'card_condition'
    condition_id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String, unique=True)

    def __repr__(self):
        return f"<CardCondition(id={self.condition_id}, description='{self.description}')>"


class Price(Base):
    __tablename__ = 'price'
    card_id = Column(Integer, ForeignKey('card.card_id'), primary_key=True)
    condition_id = Column(Integer, ForeignKey('card_condition.condition_id'), primary_key=True)
    price_usd = Column(DECIMAL, nullable=False)
    date = Column(TIMESTAMP)
    
    card = relationship("Card")
    condition = relationship("CardCondition")

    def __repr__(self):
        return f"<Price(card_id={self.card_id}, condition_id={self.condition_id}, price_usd={self.price_usd})>"


# Definición del modelo ORM para la tabla "card_in_collection"
class CardInCollection(Base):
    __tablename__ = 'card_in_collection'
    card_collection_id = Column(Integer, primary_key=True, autoincrement=True)
    collection_id = Column(Integer, ForeignKey('collection.collection_id'), nullable=False)
    card_id = Column(Integer, nullable=False)
    condition_id = Column(Integer, nullable=False)
    quantity = Column(Integer)
    
    # Relaciones
    collection = relationship("Collection", back_populates="cards")
    # Usamos primaryjoin para las relaciones que no tienen FK directa
    card = relationship("Card", primaryjoin="CardInCollection.card_id==Card.card_id", foreign_keys=[card_id])
    condition = relationship("CardCondition", primaryjoin="CardInCollection.condition_id==CardCondition.condition_id", foreign_keys=[condition_id])
    
    # La FK compuesta a price se define a nivel de esquema SQL, no en el ORM

    def __repr__(self):
        return (f"<CardInCollection(id={self.card_collection_id}, "
                f"collection_id={self.collection_id}, card_id={self.card_id}, "
                f"condition_id={self.condition_id}, quantity={self.quantity})>")


# Función auxiliar para verificar si existe el precio
def check_price_exists(card_id: int, condition_id: int):
    """Verifica si existe un precio para la combinación de carta y condición"""
    price = session.query(Price).filter_by(
        card_id=card_id,
        condition_id=condition_id
    ).first()
    return price is not None


def get_available_conditions_for_card(card_id: int):
    """Obtiene las condiciones disponibles (con precio) para una carta"""
    prices = session.query(Price).filter_by(card_id=card_id).all()
    
    if not prices:
        print(f"No hay precios registrados para la carta ID {card_id}")
        return []
    
    print(f"\nCondiciones disponibles para la carta ID {card_id}:")
    for price in prices:
        print(f"  - Condition ID: {price.condition_id} ({price.condition.description}), Precio: ${price.price_usd}")
    
    return prices


# Funciones CRUD para CardInCollection
def add_card_to_collection(collection_id: int, card_id: int, 
                          condition_id: int, quantity: int = 1):
    """Añade una carta a una colección (con validación de precio)"""
    
    # Validar que existe el precio para esta combinación
    if not check_price_exists(card_id, condition_id):
        print(f"ERROR: No existe un precio registrado para card_id={card_id} y condition_id={condition_id}")
        print("Primero debes crear un registro en la tabla 'price' para esta combinación.")
        print("\nConsulta las condiciones disponibles para esta carta:")
        get_available_conditions_for_card(card_id)
        return None
    
    try:
        new_card_in_collection = CardInCollection(
            collection_id=collection_id,
            card_id=card_id,
            condition_id=condition_id,
            quantity=quantity
        )
        session.add(new_card_in_collection)
        session.commit()
        print(f"Carta añadida a la colección: {new_card_in_collection}")
        return new_card_in_collection
    except Exception as e:
        session.rollback()
        print(f"Error al añadir carta: {e}")
        return None


def get_all_cards_in_collections():
    """Obtiene todas las cartas en todas las colecciones"""
    cards = session.query(CardInCollection).all()
    print("Cartas en colecciones encontradas:", cards)
    return cards


def get_card_in_collection_by_id(card_collection_id: int):
    """Obtiene un registro específico por su ID"""
    card_in_collection = session.query(CardInCollection).get(card_collection_id)
    if card_in_collection:
        print(f"Registro encontrado: {card_in_collection}")
    else:
        print(f"Registro con ID {card_collection_id} no encontrado")
    return card_in_collection


def get_cards_by_collection(collection_id: int):
    """Obtiene todas las cartas de una colección específica"""
    cards = session.query(CardInCollection).filter_by(collection_id=collection_id).all()
    print(f"Cartas en la colección {collection_id}:", cards)
    return cards


def get_cards_by_collection_with_details(collection_id: int):
    """
    Obtiene todas las cartas de una colección con detalles completos,
    mostrando solo el precio más reciente por condición.
    """

    # Subconsulta para obtener la fecha más reciente por carta y condición
    subquery_latest = (
        session.query(
            Price.card_id.label("card_id"),
            Price.condition_id.label("condition_id"),
            func.max(Price.date).label("max_date")
        )
        .group_by(Price.card_id, Price.condition_id)
        .subquery()
    )

    # Query principal con joins
    query = (
        session.query(
            CardInCollection.card_collection_id,
            Card.name.label("card_name"),
            Card.set_number,
            CardCondition.description.label("condition_desc"),
            Price.price_usd,
            CardInCollection.quantity
        )
        .join(Card, CardInCollection.card_id == Card.card_id)
        .join(CardCondition, CardInCollection.condition_id == CardCondition.condition_id)
        .join(
            subquery_latest,
            (subquery_latest.c.card_id == Card.card_id) &
            (subquery_latest.c.condition_id == CardCondition.condition_id)
        )
        .join(
            Price,
            (Price.card_id == subquery_latest.c.card_id) &
            (Price.condition_id == subquery_latest.c.condition_id) &
            (Price.date == subquery_latest.c.max_date)
        )
        .filter(CardInCollection.collection_id == collection_id)
        .order_by(Card.name)
    )

    results = query.all()

    if not results:
        print(f"\nNo hay cartas registradas en la colección {collection_id}.")
        return []

    print(f"\n=== Detalle de cartas en la colección {collection_id} ===\n")
    print(f"{'ID':<4} {'Nombre':<25} {'#Set':<8} {'Condición':<15} {'Precio (USD)':<12} {'Cantidad':<8}")
    print("-" * 80)

    for r in results:
        print(f"{r.card_collection_id:<4} {r.card_name:<25} {r.set_number:<8} {r.condition_desc:<15} "
              f"${r.price_usd:<11} {r.quantity:<8}")

    return results

def get_card_quantity_in_collection(collection_id: int, card_id: int, condition_id: int):
    """Obtiene la cantidad de una carta específica en una colección"""
    card_entry = session.query(CardInCollection).filter_by(
        collection_id=collection_id,
        card_id=card_id,
        condition_id=condition_id
    ).first()
    
    if card_entry:
        print(f"Cantidad encontrada: {card_entry.quantity}")
        return card_entry.quantity
    else:
        print("Carta no encontrada en la colección")
        return 0


def update_card_quantity(card_collection_id: int, new_quantity: int):
    """Actualiza la cantidad de una carta en la colección"""
    try:
        card_in_collection = session.query(CardInCollection).get(card_collection_id)
        if card_in_collection:
            card_in_collection.quantity = new_quantity
            session.commit()
            print(f"Cantidad actualizada: {card_in_collection}")
        else:
            print("Registro no encontrado")
        return card_in_collection
    except Exception as e:
        session.rollback()
        print(f"Error al actualizar: {e}")
        return None


def update_card_condition(card_collection_id: int, new_condition_id: int):
    """Actualiza la condición de una carta en la colección (con validación)"""
    try:
        card_in_collection = session.query(CardInCollection).get(card_collection_id)
        if card_in_collection:
            # Validar que existe precio para la nueva condición
            if not check_price_exists(card_in_collection.card_id, new_condition_id):
                print(f"ERROR: No existe precio para card_id={card_in_collection.card_id} y condition_id={new_condition_id}")
                get_available_conditions_for_card(card_in_collection.card_id)
                return None
            
            card_in_collection.condition_id = new_condition_id
            session.commit()
            print(f"Condición actualizada: {card_in_collection}")
        else:
            print("Registro no encontrado")
        return card_in_collection
    except Exception as e:
        session.rollback()
        print(f"Error al actualizar: {e}")
        return None


def update_card_in_collection(card_collection_id: int, quantity: int = None, 
                              condition_id: int = None):
    """Actualiza múltiples campos de una carta en la colección"""
    try:
        card_in_collection = session.query(CardInCollection).get(card_collection_id)
        if card_in_collection:
            if condition_id is not None:
                # Validar que existe precio para la nueva condición
                if not check_price_exists(card_in_collection.card_id, condition_id):
                    print(f"ERROR: No existe precio para card_id={card_in_collection.card_id} y condition_id={condition_id}")
                    get_available_conditions_for_card(card_in_collection.card_id)
                    return None
                card_in_collection.condition_id = condition_id
            
            if quantity is not None:
                card_in_collection.quantity = quantity
            
            session.commit()
            print(f"Registro actualizado: {card_in_collection}")
        else:
            print("Registro no encontrado")
        return card_in_collection
    except Exception as e:
        session.rollback()
        print(f"Error al actualizar: {e}")
        return None


def remove_card_from_collection(card_collection_id: int):
    """Elimina una carta de la colección"""
    try:
        card_in_collection = session.query(CardInCollection).get(card_collection_id)
        if card_in_collection:
            session.delete(card_in_collection)
            session.commit()
            print(f"Carta eliminada de la colección: {card_in_collection}")
        else:
            print("Registro no encontrado")
        return card_in_collection
    except Exception as e:
        session.rollback()
        print(f"Error al eliminar: {e}")
        return None


def remove_all_cards_from_collection(collection_id: int):
    """Elimina todas las cartas de una colección específica"""
    try:
        cards = session.query(CardInCollection).filter_by(collection_id=collection_id).all()
        count = len(cards)
        for card in cards:
            session.delete(card)
        session.commit()
        print(f"{count} cartas eliminadas de la colección {collection_id}")
        return count
    except Exception as e:
        session.rollback()
        print(f"Error al eliminar: {e}")
        return 0


def increment_card_quantity(card_collection_id: int, increment: int = 1):
    """Incrementa la cantidad de una carta en la colección"""
    try:
        card_in_collection = session.query(CardInCollection).get(card_collection_id)
        if card_in_collection:
            card_in_collection.quantity += increment
            session.commit()
            print(f"Cantidad incrementada: {card_in_collection}")
        else:
            print("Registro no encontrado")
        return card_in_collection
    except Exception as e:
        session.rollback()
        print(f"Error al incrementar: {e}")
        return None


def decrement_card_quantity(card_collection_id: int, decrement: int = 1):
    """Decrementa la cantidad de una carta en la colección"""
    try:
        card_in_collection = session.query(CardInCollection).get(card_collection_id)
        if card_in_collection:
            new_quantity = card_in_collection.quantity - decrement
            if new_quantity > 0:
                card_in_collection.quantity = new_quantity
                session.commit()
                print(f"Cantidad decrementada: {card_in_collection}")
            else:
                print("La cantidad resultante sería 0 o negativa. Considera eliminar el registro.")
        else:
            print("Registro no encontrado")
        return card_in_collection
    except Exception as e:
        session.rollback()
        print(f"Error al decrementar: {e}")
        return None
    
# Menú interactivo
# Menú interactivo
def collection_menu(collection_id):
    while True:
        print(f"\n=== MENÚ DE COLECCIÓN #{collection_id} ===")
        print("1. Ver detalle de cartas")
        print("2. Agregar carta")
        print("3. Eliminar carta")
        print("4. Salir")

        option = input("Seleccione una opción (1-4): ").strip()

        if option == "1":
            print("\n--- Detalle de cartas en la colección ---")
            get_cards_by_collection_with_details(collection_id)

        elif option == "2":
            print("\n--- Agregar carta a colección ---")
            try:
                card_id = int(input("Ingrese el ID de la carta: ").strip())
                condition_id = int(input("Ingrese el ID de la condición: ").strip())
                quantity = int(input("Ingrese la cantidad: ").strip())
                add_card_to_collection(collection_id, card_id, condition_id, quantity)
            except ValueError:
                print("Entrada inválida, inténtelo de nuevo.")

        elif option == "3":
            print("\n--- Eliminar carta de colección ---")
            cards = get_cards_by_collection_with_details(collection_id)
            if cards:
                try:
                    card_collection_id = int(input("\nIngrese el ID del registro a eliminar: ").strip())
                    remove_card_from_collection(card_collection_id)
                except ValueError:
                    print("ID inválido.")
            else:
                print("No hay cartas para eliminar.")

        elif option == "4":
            print("Saliendo del menú de colecciones...")
            break

        else:
            print("Opción no válida. Intente nuevamente.")

# Test de las funciones CRUD
# Bloque principal (pantalla de prueba)
if __name__ == "__main__":
    Base.metadata.create_all(engine)  # Crea las tablas si no existen
    
    try:
        collection_id = int(input("Ingrese el ID de la colección con la que desea trabajar: ").strip())
    except ValueError:
        print("ID inválido. Terminando ejecución.")
        exit()

    collection_menu(collection_id)
    print("\nPrograma finalizado.")
    
    # Primero, verificar qué condiciones están disponibles para la carta
    # print("=== Verificando condiciones disponibles ===")
    # get_available_conditions_for_card(card_id=2)
    
    # Añadir una carta a una colección
    # IMPORTANTE: Usa un condition_id que exista en la tabla price para tu card_id
    # add_card_to_collection(
    #     collection_id=1, 
    #     card_id=2, 
    #     condition_id=1,
    #     quantity=2
    # )
    
    # Obtener todas las cartas en colecciones
    # get_all_cards_in_collections()
    
    # Obtener cartas de una colección específica
    # get_cards_by_collection(1)
    
    # Obtener cartas con detalles completos
    # get_cards_by_collection_with_details(1)
    
    # Obtener cantidad específica
    # get_card_quantity_in_collection(collection_id=1, card_id=2, condition_id=1)
    
    # Actualizar cantidad
    # update_card_quantity(1, 5)
    
    # Actualizar condición (valida automáticamente)
    # update_card_condition(1, 4)
    
    # Actualizar múltiples campos
    # update_card_in_collection(1, quantity=10, condition_id=3)
    
    # Incrementar cantidad
    # increment_card_quantity(1, 2)
    
    # Decrementar cantidad
    # decrement_card_quantity(1, 1)
    
    # Eliminar carta de colección
    # remove_card_from_collection(1)
    
    # Eliminar todas las cartas de una colección
    # remove_all_cards_from_collection(1)