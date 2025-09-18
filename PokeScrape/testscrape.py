import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import csv

df = pd.read_excel("/Users/philip/Desktop/Lettuce/Browser-auto/Cotiza-inador/PokeScrape/lista_cartas.xlsx")

# Tomar solo la primera fila
first_row = df.iloc[0]

# Extraer valores
card_name = first_row["Nombre"]
set_name = first_row["Set"]
number_in_set = first_row["Número"]
image_url = first_row["Imagen"]

# Imprimir para test
print("Card Name:", card_name)
print("Set Name:", set_name)
print("Number in Set:", number_in_set)
print("Image URL:", image_url)