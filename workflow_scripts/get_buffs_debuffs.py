import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timedelta
from selenium.webdriver.common.keys import Keys
import re
import os
import requests

# Initialize Chrome options
chrome_options = Options()
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--headless')

def init_driver():
    print(ChromeDriverManager().install())
    #ChromeService(ChromeDriverManager().install())
    return webdriver.Chrome(options=chrome_options)

# Initialize the Chrome driver
driver = init_driver()

# Open the initial URL to establish session/cookies
buff_url = 'https://ceciliabot.github.io/#/database/buffs/'
debuff_url = 'https://ceciliabot.github.io/#/database/debuffs/'
driver.get(buff_url)

last_buff = "//*[@id='app_content']/div[3]/div[69]/a/div" # TODO last character, change the number to the last character
last_buff_name = 'Requiemroar'

buff_img_dir = 'CharacterUI/buff_images'
os.makedirs(buff_img_dir, exist_ok=True)

debuff_img_dir = 'CharacterUI/debuff_images'
os.makedirs(debuff_img_dir, exist_ok=True)

#last_element = driver.find_element(By.XPATH, last_character)

#driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth' });", last_element)

'''
a = ActionChains(driver, duration=10000000)
a.move_to_element(last_element).perform()
'''

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, last_buff)))

data = []

# Function to save data to CSV
def save_to_csv():
    csv_file = 'data/buffs_debuffs_details.csv'
    with open(csv_file, mode='w', newline="", encoding='utf-8') as file:
        writer = csv.DictWriter(file,fieldnames=["Type", "Name", "Description", "Heroes"])
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print(f'Data has been successfully written to {csv_file}')

# Download images for buffs
cards = driver.find_elements(By.CSS_SELECTOR, 'div.card-with-image.relative.overflow-hidden.mat-hover')
for card in cards:
    actions = ActionChains(driver)
    actions.move_to_element(card).perform()

    # Use WebDriverWait to wait for the image within the current card
    WebDriverWait(driver, 10).until(lambda d: card.find_element(By.CSS_SELECTOR, 'div.image-wrapper img'))

    image = card.find_element(By.CSS_SELECTOR, 'div.image-wrapper img')
    src = image.get_attribute('src')
    if src is None:
        src = image.get_attribute('data-src')
    response = requests.get(src)
    if response.status_code == 200:
        filename = card.find_element(By.CSS_SELECTOR, 'div.name-wrapper span').text + '.png'
        # For Increase Attack (Greater)
        if filename.find('(Greater)') == -1:
            filename = re.sub(r'\s*\(.*?\)', '', filename)
        filepath = os.path.join(buff_img_dir, filename)
        with open(filepath, 'wb') as file:
            file.write(response.content)
        print(f'Saved: {filepath}')
   
data = []

# Track the index of the last processed element
last_processed_index = 0

while True:
    save_to_csv()
    # Wait until the elements are reloaded after going back
    time.sleep(2)
    
    # Find all elements with the specific class
    all_elements = driver.find_elements(By.CSS_SELECTOR, 'div.card-with-image.relative.overflow-hidden.mat-hover')
    
    # Loop through elements starting from the last processed index
    for i in range(last_processed_index, len(all_elements)):
        element = all_elements[i]
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(element))
        try:
            name = element.find_element(By.CSS_SELECTOR, 'div.name-wrapper').text
            element.click()

            # Wait for the specific div to load on the new page
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div[style='font-size: 14px; margin: 0px auto; width: 90%; max-width: 600px; background: rgba(33, 150, 243, 0.64); color: white; padding: 10px; border-radius: 8px;']")
                )
            )

            char_portraits = driver.find_elements(By.CSS_SELECTOR, 'div.panel.full-h.full-w')
            # go to all char_portraits
            for portrait in char_portraits:
                actions = ActionChains(driver)
                actions.move_to_element(portrait).perform()

            time.sleep(3)
            div = driver.find_element(
                By.CSS_SELECTOR, 
                "div[style='font-size: 14px; margin: 0px auto; width: 90%; max-width: 600px; background: rgba(33, 150, 243, 0.64); color: white; padding: 10px; border-radius: 8px;']")
            description = div.find_element(By.TAG_NAME, "span").text

            print(f"Name: {name}")

            hero_elements = driver.find_elements(By.CSS_SELECTOR, 'img.hero-img')
            heroes = []
            for hero_element in hero_elements:
                    hero_name = hero_element.get_attribute('src')
                    
                    hero_name = re.search(r'c\d{4}', hero_name).group()
                    heroes.append(hero_name)
                    print(f'Processing hero: {hero_name}')

            data.append({
                'Type': 'Buff',
                'Name': re.sub(r'\s*\(.*?\)', '', name) if name.find('(Greater)') == -1 else name, #For Increase Attack (Greater)
                'Description': description,
                'Heroes': heroes
            })

            # Update the last processed index
            last_processed_index = i + 1
            
        except Exception as e:
            print(f"Encountered an error: {e}")
            continue  # Skip the problematic element and move on to the next one

        finally:
            # After interacting with the element, go back to the previous page
            driver.execute_script("window.history.go(-1)")
            
            # Break out of the loop to avoid processing the next elements in this iteration
            break  # This forces the loop to refresh the elements after going back

    # Exit the loop if all elements have been processed
    if last_processed_index >= len(all_elements):
        break

# Now do the same for debuffs
driver.get(debuff_url)
driver.refresh()
time.sleep(2)

# Track the index of the last processed element
last_processed_index = 0

# Download images for debuffs
cards = driver.find_elements(By.CSS_SELECTOR, 'div.card-with-image.relative.overflow-hidden.mat-hover')
for card in cards:
    actions = ActionChains(driver)
    actions.move_to_element(card).perform()

    # Use WebDriverWait to wait for the image within the current card
    WebDriverWait(driver, 10).until(lambda d: card.find_element(By.CSS_SELECTOR, 'div.image-wrapper img'))

    image = card.find_element(By.CSS_SELECTOR, 'div.image-wrapper img')
    src = image.get_attribute('src')
    if src is None:
        src = image.get_attribute('data-src')

    response = requests.get(src)
    if response.status_code == 200:
        filename = card.find_element(By.CSS_SELECTOR, 'div.name-wrapper span').text + '.png'
        filename = re.sub(r'\s*\(.*?\)', '', filename)
        filepath = os.path.join(debuff_img_dir, filename)
        with open(filepath, 'wb') as file:
            file.write(response.content)
        print(f'Saved: {filepath}')

while True:
    save_to_csv()
    # Wait until the elements are reloaded after going back
    time.sleep(2)
    
    # Find all elements with the specific class
    all_elements = driver.find_elements(By.CSS_SELECTOR, 'div.card-with-image.relative.overflow-hidden.mat-hover')
    
    # Loop through elements starting from the last processed index
    for i in range(last_processed_index, len(all_elements)):
        element = all_elements[i]
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(element))
        try:
            name = element.find_element(By.CSS_SELECTOR, 'div.name-wrapper').text
            element.click()

            # Wait for the specific div to load on the new page
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div[style='font-size: 14px; margin: 0px auto; width: 90%; max-width: 600px; background: rgba(244, 67, 54, 0.64); color: white; padding: 10px; border-radius: 8px;")
                )
            )

            char_portraits = driver.find_elements(By.CSS_SELECTOR, 'div.panel.full-h.full-w')
            # go to all char_portraits
            for portrait in char_portraits:
                actions = ActionChains(driver)
                actions.move_to_element(portrait).perform()

            time.sleep(3)
            div = driver.find_element(
                By.CSS_SELECTOR, 
                "div[style='font-size: 14px; margin: 0px auto; width: 90%; max-width: 600px; background: rgba(244, 67, 54, 0.64); color: white; padding: 10px; border-radius: 8px;")
            description = div.find_element(By.TAG_NAME, "span").text

            print(f"Name: {name}")

            hero_elements = driver.find_elements(By.CSS_SELECTOR, 'img.hero-img')
            heroes = []
            for hero_element in hero_elements:
                    hero_name = hero_element.get_attribute('src')
                    
                    hero_name = re.search(r'c\d{4}', hero_name).group()
                    heroes.append(hero_name)
                    print(f'Processing hero: {hero_name}')

            data.append({
                'Type': 'Debuff',
                'Name': re.sub(r'\s*\(.*?\)', '', name),
                'Description': description,
                'Heroes': heroes
            })

            # Update the last processed index
            last_processed_index = i + 1
            
        except Exception as e:
            print(f"Encountered an error: {e}")
            continue  # Skip the problematic element and move on to the next one

        finally:
            # After interacting with the element, go back to the previous page
            driver.execute_script("window.history.go(-1)")
            
            # Break out of the loop to avoid processing the next elements in this iteration
            break  # This forces the loop to refresh the elements after going back

    # Exit the loop if all elements have been processed
    if last_processed_index >= len(all_elements):
        break

save_to_csv()
# Close the WebDriver
driver.quit()