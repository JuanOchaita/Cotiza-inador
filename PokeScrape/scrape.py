import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import urllib.parse

async def search_card(page, card_name, set_name):
    # Encode the search query to be URL-safe
    query = urllib.parse.quote_plus(f"{card_name} {set_name}")
    
    # Construct the URL directly
    url = f"https://www.tcgplayer.com/search/all/product?q={query}&view=grid&ProductTypeName=Cards&page=1"
    
    # Go to the URL
    await page.goto(url, wait_until="domcontentloaded")
    
    # Wait for product cards to appear
    await page.wait_for_selector("section.product-card__product")

    # Get all cards, click the first one
    cards = await page.query_selector_all("section.product-card__product")
    if cards:
        await cards[0].click()
        await page.wait_for_timeout(3000)  # give it time to load product page
    else:
        print(f"No results found for {query}")

async def scrape_card_data(page, card_name, set_name, number_in_set, image_url):
    condition_list = ['Damaged', 'Heavily Played', 'Moderately Played', 'Lightly Played', 'Near Mint']
    results = []

    # --- Buscar carta ---
    await search_card(page, card_name, set_name)
    await page.reload()

    await page.wait_for_timeout(3000)

    # --- Abrir Printing popover ---
    await page.wait_for_selector("button[data-testid='filterBar-Printing']")
    await page.click("button[data-testid='filterBar-Printing']")
    await page.wait_for_selector("div[data-testid='searchFilterPrinting']")

    # --- Extraer opciones de Printing ---
    printing_checkboxes = await page.query_selector_all(
        "div[data-testid='searchFilterPrinting'] input.tcg-input-checkbox__input"
    )
    printing_options = {}
    for checkbox in printing_checkboxes:
        id_attr = await checkbox.get_attribute("id")
        label_text_el = await checkbox.evaluate_handle(
            "el => el.closest('label').querySelector('.tcg-input-checkbox__label-text')"
        )
        label_text = await label_text_el.inner_text() if label_text_el else id_attr
        printing_options[label_text] = id_attr

    # --- Abrir Condition popover ---
    await page.wait_for_selector("button[data-testid='filterBar-Condition']")
    await page.click("button[data-testid='filterBar-Condition']")
    await page.wait_for_selector("div[data-testid='searchFilterCondition']")

    # --- Extraer opciones de Condition ---
    condition_checkboxes = await page.query_selector_all(
        "div[data-testid='searchFilterCondition'] input.tcg-input-checkbox__input"
    )
    condition_options = {}
    for checkbox in condition_checkboxes:
        id_attr = await checkbox.get_attribute("id")
        label_text_el = await checkbox.evaluate_handle(
            "el => el.closest('label').querySelector('.tcg-input-checkbox__label-text')"
        )
        label_text = await label_text_el.inner_text() if label_text_el else id_attr
        condition_options[label_text] = id_attr

    # --- Iterar Printing × Condition ---
    for print_label, print_id in printing_options.items():
        for cond_label in condition_list:
            
            await page.click("button#clearFilters")
            await page.wait_for_timeout(200)

            # Idioma fijo en inglés
            await page.click("button[data-testid='filterBar-Language']")
            await page.click("label[for='hfb-Language-English-filter']")

            # Seleccionar impresión
            await page.click("button[data-testid='filterBar-Printing']")
            await page.click(f"label[for='hfb-{print_id}']")

            price_value = None

            # Seleccionar condición solo si existe
            if cond_label in condition_options:
                cond_id = condition_options[cond_label]
                await page.click("button[data-testid='filterBar-Condition']")
                await page.click(f"label[for='hfb-{cond_id}']")

                try:
                    await page.wait_for_selector("td .price-points__upper__price", timeout=5000)
                    price_text = await page.inner_text("td .price-points__upper__price")
                    price_value = float(price_text.replace("$", "").replace(",", ""))
                except:
                    price_value = None  # si no hay precio

            # --- Guardar resultado como una fila ---
            results.append({
                "card_name": card_name,
                "set_name": set_name,
                "number_in_set": number_in_set,
                "printing_option": print_label,
                "condition": cond_label,
                "market_price": price_value,
                "image": image_url
            })

    return results

async def scrape_from_excel(file_path, page, headless=True):
    df = pd.read_excel(file_path)
    all_data = []

    for _, row in df.iterrows():
        card_name = row["Nombre"]
        set_name = row["Set"]
        number_in_set = row["Número"]
        image_url = row.get("Imagen", None)

        try:
            data = await scrape_card_data(
                page=page,
                card_name=card_name,
                set_name=set_name,
                number_in_set=number_in_set,
                image_url=image_url
            )
            all_data.extend(data)

        except Exception as e:
            print(f"Error scraping {card_name} ({set_name}): {e}")
            # Generar fila con valores nulos para esta carta
            condition_list = ['Damaged', 'Heavily Played', 'Moderately Played', 'Lightly Played', 'Near Mint']
            for cond in condition_list:
                all_data.append({
                    "card_name": card_name,
                    "set_name": set_name,
                    "number_in_set": number_in_set,
                    "printing_option": None,
                    "condition": cond,
                    "market_price": None,
                    "image": image_url
                })

    result_df = pd.DataFrame(all_data)
    result_df.to_csv("card_information_en.csv", index=False)

    return result_df

async def main():
    # Iniciar Playwright y navegador
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False, slow_mo=0)
        page = await browser.new_page()

        # Path a tu Excel
        excel_path = "/Users/philip/Desktop/Lettuce/Browser-auto/Cotiza-inador/PokeScrape/lista_cartas.xlsx"

        # Llamada a la función que hace el scraping
        df_results = await scrape_from_excel(excel_path, page)

        # Mostrar resultados
        print(df_results)

        # Cerrar navegador
        await browser.close()

# Ejecutar el main
if __name__ == "__main__":
    asyncio.run(main())