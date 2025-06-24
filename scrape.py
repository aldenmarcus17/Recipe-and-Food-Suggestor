import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# set up driver and shtuff
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# csv loading
ingredients_df = pd.read_csv('ingredients copy.csv')
ingredient_prices = {}

# scrape from nofrills
base_url = "https://www.nofrills.ca/en/search?search-bar="

for ingredient in ingredients_df['Aliased Ingredient Name']:
    try:
        ingredient_url = base_url + ingredient.replace(' ', '+')

        driver.get(ingredient_url)
        time.sleep(5)

        prices = []
        # selects all elements with this css tag
        items = driver.find_elements(By.CSS_SELECTOR, ".chakra-linkbox.css-yxqevf")

        for item in items[:5]:
            try:
                price_text = item.find_element(By.CSS_SELECTOR, "[data-testid='regular-price']").text.strip()

                # found this online, uses regex to find float like numbers, and does not include words
                match = re.search(r"(\d+(\.\d+)?)", price_text)

                if match:
                    price = float(match.group(1))
                    prices.append(price)

            # exception thrown for items that are weird (outta my control LOL)
            except Exception as e:
                print(f"Skipping item due to error: {e}")

        # takes average price
        if prices:
            avg_price = round(sum(prices) / len(prices), 2)
            ingredient_prices[ingredient] = avg_price
        else:
            ingredient_prices[ingredient] = None

    # exception thrown if ingredient is weird and can't be searched
    except Exception as e:
        print(f"Error processing {ingredient}: {e}")

# dataframe (it's like an excel spreadsheet hehe)
results = pd.DataFrame(list(ingredient_prices.items()), columns=["Ingredient", "Average Price"])

# dataframe can save directly to csv woohoo!
results.to_csv('ingredient_prices.csv', index=False)

# close
driver.quit()

print("Scraping complete. Average prices saved to ingredient_prices.csv.")
