import psycopg
from datetime import datetime

# Conexión a la base de datos
conn = psycopg.connect(
    host="localhost",   # o "127.0.0.1"
    port=5433,          # muy importante: usas 5433, no 5432
    dbname="mydb",
    user="myuser",
    password="mypassword"
)

# Usamos context manager para manejar el cursor
def insert_user(user_id, name, email):
    created_at = datetime.now()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO "user" (user_id, name, email, created_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id) DO NOTHING
        """, (user_id, name, email, created_at))

def insert_card(card_id, name, language, set_name, set_number, finish_type, image_url, edition):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO card (card_id, name, language, set_name, set_number, finish_type, image_url, edition)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (card_id) DO NOTHING
        """, (card_id, name, language, set_name, set_number, finish_type, image_url, edition))

def insert_card_condition(condition_id, description):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO card_condition (condition_id, description)
            VALUES (%s, %s)
            ON CONFLICT (condition_id) DO NOTHING
        """, (condition_id, description))

def insert_price(card_id, condition_id, price_usd):
    date = datetime.now()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO price (card_id, condition_id, price_usd, date)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (card_id, condition_id)
            DO UPDATE SET price_usd = EXCLUDED.price_usd, date = EXCLUDED.date
        """, (card_id, condition_id, price_usd, date))

def insert_collection(collection_id, title, user_id, exchange_rate, collection_price_usd):
    created_at = datetime.now()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO collection (collection_id, title, user_id, exchange_rate, collection_price_usd, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (collection_id) DO NOTHING
        """, (collection_id, title, user_id, exchange_rate, collection_price_usd, created_at))

def insert_card_in_collection(card_collection_id, collection_id, card_id, condition_id, quantity):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO card_in_collection (card_collection_id, collection_id, card_id, condition_id, quantity)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (card_collection_id) DO NOTHING
        """, (card_collection_id, collection_id, card_id, condition_id, quantity))

# Ejemplo de uso
insert_user(1, "Juan Pérez", "juan@example.com")
insert_card(1, "Blue-Eyes White Dragon", "EN", "Legend of Blue Eyes White Dragon", "LOB-001", "Holofoil", "https://link_a_imagen.com", "1st Edition")
insert_card_condition(1, "Near Mint")
insert_price(1, 1, 120.50)
insert_collection(1, "Mi Primera Colección", 1, 1.0, 120.50)
insert_card_in_collection(1, 1, 1, 1, 2)

# Guardar cambios y cerrar conexión
conn.commit()
conn.close()
