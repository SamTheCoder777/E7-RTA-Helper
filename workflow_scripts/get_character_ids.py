import csv
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.chrome.options import Options

# Initialize Chrome options
chrome_options = Options()
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--headless')

# Initialize the Chrome driver
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

# Open the initial URL to establish session/cookies
initial_url = 'https://epic7.onstove.com/en/gg/herorecord'
driver.get(initial_url)

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.filterlist-wrap ul li')))
time.sleep(10) # For some reason some eleemnts are not loaded together causing errors

# Create the 'dataset' directory if it doesn't exist
os.makedirs('dataset', exist_ok=True)

# Find all elements with class 'filterlist-wrap' (assuming this contains hero information)
try:
    # Wait until all hero elements are present
    heros = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.filterlist-wrap ul li')))
    
    # List to store hero data
    hero_data = []

    # Iterate through each hero element and extract hero code and name
    for hero_element in heros:
        try:
            # Extract hero code (from img alt attribute)
            hero_code = hero_element.find_element(By.TAG_NAME, 'img').get_attribute('alt')

            # Extract hero name (from i tag)
            hero_name = hero_element.find_element(By.TAG_NAME, 'i').text
            
            # Append to hero_data list as dictionary
            hero_data.append({'code': hero_code, 'name': hero_name})
            print(f"Found hero: {hero_code} - {hero_name}")
            
            # Create a new folder for the hero in the 'dataset' directory
            hero_dir = os.path.join('dataset', hero_code)
            os.makedirs(hero_dir, exist_ok=True)
            
            # Define the image URL and the local path
            image_url = f'https://static.smilegatemegaport.com/event/live/epic7/guide/images/hero/{hero_code}_s.png'
            image_path = os.path.join(hero_dir, 'c.png')
            
            # Download the image and save it locally
            response = requests.get(image_url)
            if response.status_code == 200:
                with open(image_path, 'wb') as img_file:
                    img_file.write(response.content)
            else:
                print(f"Failed to download image for {hero_code}")
            
        except Exception as e:
            print(f"Error retrieving hero information: {e}")
            continue  # Continue to next hero
    
    # Save data to CSV file
    csv_file = 'data/hero_code_to_name.csv'
    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['code', 'name'])
        writer.writeheader()
        writer.writerows(hero_data)
    
    print(f"Saved hero code and name data to {csv_file}")

except Exception as e:
    print(f"Error finding or saving hero elements: {e}")

# Close the driver
driver.quit()

# Now Flip images
import os
from PIL import Image

# Define the dataset directory
dataset_dir = 'dataset'

# Iterate through each hero_code folder in the dataset directory
for hero_code in os.listdir(dataset_dir):
    hero_dir = os.path.join(dataset_dir, hero_code)
    if os.path.isdir(hero_dir):
        # Define the path to the original and flipped images
        original_image_path = os.path.join(hero_dir, 'c.png')
        flipped_image_path = os.path.join(hero_dir, 'c_flipped.png')
        try:
            # Open the original image
            with Image.open(original_image_path) as img:
                # Horizontally flip the image
                flipped_img = img.transpose(method=Image.FLIP_LEFT_RIGHT)
                
                # Save the flipped image
                flipped_img.save(flipped_image_path)
                
            print(f"Saved flipped image for {hero_code} to {flipped_image_path}")
        
        except Exception as e:
            print(f"Error processing image for {hero_code}: {e}")

# Flip Skins If Exists
# Define the dataset directory
dataset_dir = 'dataset'

# Iterate through each hero_code folder in the dataset directory
for hero_code in os.listdir(dataset_dir):
    hero_dir = os.path.join(dataset_dir, hero_code)
    if os.path.isdir(hero_dir):
        # Define the path to the original and flipped images
        original_image_path = os.path.join(hero_dir, 'c_1.png')
        flipped_image_path = os.path.join(hero_dir, 'c_1_flipped.png')
        try:
            # Open the original image
            with Image.open(original_image_path) as img:
                # Horizontally flip the image
                flipped_img = img.transpose(method=Image.FLIP_LEFT_RIGHT)
                
                # Save the flipped image
                flipped_img.save(flipped_image_path)
                
            print(f"Saved flipped image for {hero_code} to {flipped_image_path}")
        
        except Exception as e:
            print(f"Error processing image for {hero_code}: {e}")
