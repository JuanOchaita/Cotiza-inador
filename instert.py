import psycopg
from datetime import datetime

# Database connection
conn = psycopg.connect(
    host="localhost",
    port=5433,
    dbname="mydb",
    user="myuser",
    password="mypassword"
)

# Insert a new user and return the generated user_id
def insert_user(name, email):
    created_at = datetime.now()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO "user" (name, email, created_at)
            VALUES (%s, %s, %s)
            ON CONFLICT (email) DO NOTHING
            RETURNING user_id
        """, (name, email, created_at))
        result = cur.fetchone()
        return result[0] if result else None

def insert_card(name, language, set_name, set_number, finish_type, image_url, edition):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO card (name, language, set_name, set_number, finish_type, image_url, edition)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (name, set_number) DO NOTHING
            RETURNING card_id
        """, (name, language, set_name, set_number, finish_type, image_url, edition))
        result = cur.fetchone()
        return result[0] if result else None

def insert_card_condition(description):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO card_condition (description)
            VALUES (%s)
            ON CONFLICT (description) DO NOTHING
            RETURNING condition_id
        """, (description,))
        result = cur.fetchone()
        return result[0] if result else None

def insert_price(card_id, condition_id, price_usd):
    date = datetime.now()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO price (card_id, condition_id, price_usd, date)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (card_id, condition_id)
            DO UPDATE SET price_usd = EXCLUDED.price_usd, date = EXCLUDED.date
        """, (card_id, condition_id, price_usd, date))

def insert_collection(title, user_id, exchange_rate, collection_price_usd):
    created_at = datetime.now()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO collection (title, user_id, exchange_rate, collection_price_usd, created_at)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING collection_id
        """, (title, user_id, exchange_rate, collection_price_usd, created_at))
        result = cur.fetchone()
        return result[0]

def insert_card_in_collection(collection_id, card_id, condition_id, quantity):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO card_in_collection (collection_id, card_id, condition_id, quantity)
            VALUES (%s, %s, %s, %s)
            RETURNING card_collection_id
        """, (collection_id, card_id, condition_id, quantity))
        result = cur.fetchone()
        return result[0]

# Example usage

'''
user_id = insert_user("Patroclus", "juan@example.com")
card_id = insert_card("Puchamon", "EN", "Legend of Blue Eyes White Dragon", "LOB-001", "Holofoil", "https://link_to_image.com", "1st Edition")
condition_id = insert_card_condition("Near Mint")
insert_price(card_id, condition_id, 120.50)
collection_id = insert_collection("My First Collection", user_id, 1.0, 120.50)
insert_card_in_collection(collection_id, card_id, condition_id, 2)
'''

# Commit changes and close connection
conn.commit()
conn.close()
