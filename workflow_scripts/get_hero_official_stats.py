from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
import os
import csv
import re
import time

# Function to save data to CSV
def save_to_csv(data):
    csv_file = 'data/hero_official_stats.csv'
    with open(csv_file, mode='w', newline="", encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['Hero', 'Rank', 'Win Rate', 'Equipment', 'Equipment Win Rate', 'Counters', 'Synergies'])
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print(f'Data has been successfully written to {csv_file}')

# Custom wait function to handle element loading
def custom_find_element(driver, by, value, retries=3, delay=5):
    for _ in range(retries):
        try:
            element = WebDriverWait(driver, delay).until(EC.presence_of_element_located((by, value)))
            return element
        except TimeoutException:
            time.sleep(delay)
    raise TimeoutException(f'Element with {by}={value} not found after {retries} retries')

# Custom wait function to handle multiple elements loading
def custom_find_elements(driver, by, value, retries=3, delay=5):
    for _ in range(retries):
        try:
            elements = WebDriverWait(driver, delay).until(EC.presence_of_all_elements_located((by, value)))
            return elements
        except TimeoutException:
            time.sleep(delay)
    raise TimeoutException(f'Elements with {by}={value} not found after {retries} retries')

# Function to process a character
def process_character(driver, character, root_url, max_retries=5):
    url = root_url + character
    attempt = 0
    while attempt < max_retries:
        try:
            driver.get(url)

            # Wait for the hero page to load
            custom_find_element(driver, By.CLASS_NAME, 'hero-analysis-wrap')

            result = {
                "Hero": character,
                "Rank": "",
                "Win Rate": "",
                "Equipment": {
                    "0": [],
                    "1": [],
                    "2": [],
                    "3": [],
                    "4": [],
                },
                "Equipment Win Rate": {
                    "0": -1,
                    "1": -1,
                    "2": -1,
                    "3": -1,
                    "4": -1,
                },
                "Counters": [],
                "Synergies": []
            }
            # Wait until rank is loaded
            custom_find_element(driver, By.CSS_SELECTOR, 'div.win-rate-wrap')

            try:
                # Get winrate rank
                rank = custom_find_element(driver, By.CSS_SELECTOR, '.up.rank, .down.rank, .same.rank')
                result['Rank'] = rank.text
                win_rate = custom_find_element(driver, By.CLASS_NAME, 'win-rate').text
                result['Win Rate'] = re.search(r'(\d+(?:\.\d+)?)', win_rate).group()
            except Exception:
                result['Win Rate'] = ""

            try:
                # Get equipment box
                equipments = custom_find_elements(driver, By.CSS_SELECTOR, 'ul.equip-list-wrap > li')
                for i, equipment in enumerate(equipments):
                    equipment_rank = custom_find_element(equipment, By.CLASS_NAME, 'equip-name').text

                    try:
                        equipment_win_rate = custom_find_element(equipment, By.CLASS_NAME, 'equip-winrate').text
                        equipment_win_rate = re.search(r'(\d+(?:\.\d+)?)', equipment_win_rate).group()
                    except Exception:
                        equipment_win_rate = ""

                    result['Equipment Win Rate'][str(i)] = equipment_win_rate

                    equipment_names = custom_find_elements(equipment, By.CSS_SELECTOR, 'ul.equip-icon img')
                    for equipment_name in equipment_names:
                        result['Equipment'][str(i)].append(equipment_name.get_attribute('alt'))
            except Exception as e:
                print(f'Error processing equipment for {character}: {e}')

            try:
                # Get counters and synergies
                counters = custom_find_element(driver, By.CLASS_NAME, 'hard-hero')
                counter_heroes = custom_find_elements(counters, By.CSS_SELECTOR, 'ul > li')
                for counter_hero in counter_heroes:
                    result['Counters'].append(custom_find_element(counter_hero, By.CSS_SELECTOR, 'img').get_attribute('alt'))
            except Exception as e:
                print(f'Error processing counters for {character}: {e}')

            try:
                synergies = custom_find_element(driver, By.CLASS_NAME, 'with-hero')
                synergy_heroes = custom_find_elements(synergies, By.CSS_SELECTOR, 'ul > li')
                for synergy_hero in synergy_heroes:
                    result['Synergies'].append(custom_find_element(synergy_hero, By.CSS_SELECTOR, 'img').get_attribute('alt'))
            except Exception as e:
                print(f'Error processing synergies for {character}: {e}')

            return result  # Return the result if no exception was raised
        except Exception as e:
            attempt += 1
            print(f'Attempt {attempt} failed for {character}: {e}')
            if attempt < max_retries:
                time.sleep(2)  # Wait before retrying
            else:
                print(f'Failed to process {character} after {max_retries} attempts')
                return result

try:
    # Initialize the Chrome driver outside the process_character function
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Enable headless mode
    chrome_options.add_argument("--disable-gpu")
    #chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.page_load_strategy = 'none'

    driver = webdriver.Chrome(options=chrome_options)

    # Get Folders in the dataset (Characters)
    character_names = [f for f in os.listdir('dataset') if os.path.isdir(os.path.join('dataset', f))]
    root_url = 'https://epic7.onstove.com/en/gg/herorecord/'

    data = []

    for character in character_names:
        print(f'Processing {character}...')
        character_data = process_character(driver, character, root_url)
        if character_data:
            data.append(character_data)
        print(f'Finished processing {character}')

except Exception as e:
    print(f'General error: {e}')

finally:
    save_to_csv(data)
    # Quit the driver after processing all characters
    driver.quit()
