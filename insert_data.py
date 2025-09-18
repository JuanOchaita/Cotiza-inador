import csv
import psycopg
from datetime import datetime

# Conexión a la base de datos
conn = psycopg.connect(
    host="localhost",
    port=5433,
    dbname="mydb",
    user="myuser",
    password="mypassword"
)

# Insertar condiciones únicas
def get_condition_id(cur, condition):
    cur.execute("SELECT condition_id FROM card_condition WHERE description = %s", (condition,))
    result = cur.fetchone()
    if result:
        return result[0]
    cur.execute("INSERT INTO card_condition (description) VALUES (%s) RETURNING condition_id", (condition,))
    return cur.fetchone()[0]

# Insertar cartas únicas
def get_card_id(cur, name, set_name, number_in_set, printing_option, image_url):
    cur.execute("""
        SELECT card_id FROM card 
        WHERE name = %s AND language = %s AND set_name = %s AND set_number = %s AND edition = %s
    """, (name, "EN", set_name, number_in_set, printing_option))
    result = cur.fetchone()
    if result:
        return result[0]

    cur.execute("""
        INSERT INTO card (name, language, set_name, set_number, image_url, edition)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING card_id
    """, (name, "EN", set_name, number_in_set, image_url, printing_option))
    return cur.fetchone()[0]

# Insertar precios
def insert_price(cur, card_id, condition_id, price):
    if not price:
        return
    cur.execute("""
        INSERT INTO price (card_id, condition_id, price_usd, date)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (card_id, condition_id) DO UPDATE
        SET price_usd = EXCLUDED.price_usd,
            date = EXCLUDED.date
    """, (card_id, condition_id, price, datetime.now()))

# Procesar CSV e insertar en BD
with conn.cursor() as cur, open("card_information.csv", newline='', encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        name = row["card_name"]   # tu CSV usa "ard_name" en vez de "card_name"
        set_name = row["set_name"]
        number_in_set = row["number_in_set"]
        printing_option = row["printing_option"]
        condition = row["condition"]
        price = row["market_price"] if row["market_price"] else None
        image_url = row["image"]

        # Normalización
        condition_id = get_condition_id(cur, condition)
        card_id = get_card_id(cur, name, set_name, number_in_set, printing_option, image_url)

        # Precio
        insert_price(cur, card_id, condition_id, price)

# Confirmar y cerrar
conn.commit()
conn.close()
