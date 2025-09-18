import asyncio
import pandas as pd
# from playwright.async_api import async_playwright

async def scrape_card_data(card_name, set_name, number_in_set):
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, slow_mo=50)
        page = await browser.new_page()

        # 1. Ir a tcgplayer
        await page.goto("https://www.tcgplayer.com")

        # 2. Buscar carta
        search_query = f"{card_name} {set_name}"
        await page.fill("input[placeholder='Search']", search_query)
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(3000)

        # 3. Seleccionar primer resultado
        await page.click("a.search-result__title")  # <-- puede necesitar refinamiento
        await page.wait_for_timeout(3000)

        # 4. Iterar sobre printings
        printing_options = await page.query_selector_all("div.product__printing button")
        for i in range(len(printing_options)):
            await printing_options[i].click()
            await page.wait_for_timeout(2000)

            printing_name = await printing_options[i].inner_text()

            # 5. Iterar sobre condiciones
            condition_rows = await page.query_selector_all("div.product-details__condition-row")
            for row in condition_rows:
                condition = await row.query_selector("span.condition-label")
                price = await row.query_selector("span.market-price")

                if condition and price:
                    results.append({
                        "CardName": card_name,
                        "SetName": set_name,
                        "NumberInSet": number_in_set,
                        "PrintingOption": printing_name.strip(),
                        "Condition": (await condition.inner_text()).strip(),
                        "MarketPrice": (await price.inner_text()).strip()
                    })

        await browser.close()

    return results


async def main():
    # Leer Excel
    df = pd.read_excel("pokemon_cards.xlsx")

    all_data = []
    for _, row in df.iterrows():
        card_name = row["CardName"]
        set_name = row["SetName"]
        number_in_set = row["NumberInSet"]

        data = await scrape_card_data(card_name, set_name, number_in_set)
        all_data.extend(data)

    # Guardar en CSV
    out_df = pd.DataFrame(all_data)
    out_df.to_csv("pokemon_prices.csv", index=False)


if __name__ == "__main__":
    asyncio.run(main())
