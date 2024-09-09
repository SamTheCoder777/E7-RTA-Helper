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
    return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

# Initialize the Chrome driver
driver = init_driver()

# Open the initial URL to establish session/cookies
initial_url = 'https://ceciliabot.github.io/#/hero/'
driver.get(initial_url)

last_character = "//*[@id='app_content']/div/div[3]/a[332]/div/div/img" # TODO last character, change the number to the last character
last_char_name = 'Requiemroar'
#last_char_name = 'Ravi'
output_dir = 'CharacterUI/skill_images'
os.makedirs(output_dir, exist_ok=True)

#last_element = driver.find_element(By.XPATH, last_character)

#driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth' });", last_element)

'''
a = ActionChains(driver, duration=10000000)
a.move_to_element(last_element).perform()
'''

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, last_character)))

data = []

# Function to save data to CSV
def save_to_csv():
    csv_file = 'data/hero_details.csv'

    # Process the data to remove unnecessary escape characters
    for row in data:
        # Ensure the 'Hero Skill Names' field is formatted correctly
        if isinstance(row['Hero Skill Names'], list):
            row['Hero Skill Names'] = str(row['Hero Skill Names']).replace('\\"', '"')

    with open(csv_file, mode='w', newline="", encoding='utf-8') as file:
        writer = csv.DictWriter(file,fieldnames=["Hero", "Hero Name", "Role", "Element", "Hero Skill Names", "Hero Skill Descriptions", "Hero Skill Turns", "Soul Burn Count", "Soul Burn Descriptions"])
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print(f'Data has been successfully written to {csv_file}')
'''
def save_to_csv():
    file_name = 'hero_details_crawled.csv'

    fieldnames = ["Hero", "Hero Name", "Role", "Element", "Hero Skill Names", 
                  "Hero Skill Descriptions", "Hero Skill Turns", "Soul Burn Count", 
                  "Soul Burn Descriptions"]
    
    # Open the file in write mode
    with open(file_name, 'w', encoding='utf-8') as file:
        # Write the header row
        file.write(','.join(fieldnames) + '\n')
        
        # Write each row of data
        for row in data:
            fields = []
            for field in fieldnames:
                value = row.get(field, '')

                if isinstance(value, list):
                    # Escape commas in the list and join with an unescaped comma
                    formatted_value = '[' + ', '.join([item.replace(',', r'\,') for item in value]) + ']'
                else:
                    formatted_value = str(value)
                
                fields.append(formatted_value)
            
            # Write the formatted row to the file
            file.write(','.join(fields) + '\n')
    
    print(f'Data has been successfully written to {file_name}')
'''
def adjust_array(B, A):
    # Initialize an index for B
    b_index = 0
    # Initialize the result list
    result = []
    
    # Iterate through each element in A
    for a in A:
        if a == "":
            # If the element in A is an empty string, insert an empty string in the result
            result.append("")
        else:
            # Otherwise, take the element from B
            if b_index < len(B):
                result.append(B[b_index])
                b_index += 1
            else:
                # If B is exhausted, continue appending empty strings
                result.append("")
    
    return result

def get_detail(soup, driver, hero_code):
    # Get hero name
    hero_name = soup.find('div', class_='page-title-box flex flex-col').find('h2').text
    print(f"Hero Name: {hero_name}")

    # Get hero element and role
    images = soup.find_all('img', class_='inline-icon-image')
    role_pattern = re.compile(r'cm_icon_role_(\w+)\.png')
    element_pattern = re.compile(r'cm_icon_prom(\w+)\.png')

    role = ""
    elem = ""

    for img in images:
        if 'src' in img.attrs:
            src = img['src']
            role_match = role_pattern.search(src)
            element_match = element_pattern.search(src)
            if role_match:
                role = role_match.group(1)
            if element_match:
                elem = element_match.group(1)
    if elem == 'wind':
        elem = 'earth'

    # Get hero skill names
    hero_skill_names = []
    skill_names = soup.find_all('span', class_='flex-fill')
    for skill_name in skill_names:
        hero_skill_names.append(skill_name.text.strip())
    hero_skill_names = "[" + ", ".join(['"{}"'.format(name) for name in hero_skill_names]) + "]"

    # Get soul burn soul count (not ordered)
    h3_tags = soup.find_all('h3')
    soulburn_count = []
    for tag in h3_tags:
        style = tag.get('style', '')
        if 'color: var(--font-color-primary); margin-bottom: -10px;' in style:
            soulburn_count.append(tag.get_text(strip=True))

    # Get hero skills and Soul burn descriptions
    hero_skills = []
    skills = soup.find_all('div', class_='skill-description margin-vertical')
    soul_burns = ["","",""]
    soul_burns_index = 0
    for skill_index, skill in enumerate(skills):
        
        # Initialize the result string
        formatted_text = []

         # is it soulburn?
        is_soulburn = 'style' in skill.attrs
        if is_soulburn:
            if len(soulburn_count) == 1:
                match skill_index:
                    case 1:
                        soul_burns_index = 0
                    case 2:
                        soul_burns_index = 1
                    case 3:
                        soul_burns_index = 2
            if len(soulburn_count) == 2: # For ml ludwig
                match skill_index:
                    case 1:
                        soul_burns_index = 0
                    case 3:
                        soul_burns_index = 1
                    case 5:
                        soul_burns_index = 2

        last_text = ""

        # Process each element in the HTML
        for element in skill.descendants:
            if isinstance(element, str):
                # Handle plain text
                text = element.strip()
                if text and text != last_text:
                    formatted_text.append(text)
                    last_text = text
            elif element.name == 'span':
                # Process span text with formatting
                text = element.get_text(strip=True)
                class_name = element.get('class', [])
                if 'skill-common' in class_name:
                    formatted_text.append(f"[b]{text}[/b]")
                elif 'skill-variable' in class_name:
                    formatted_text.append(f"[color=orange]{text}[/color]")
                elif 'skill-debuff' in class_name:
                    formatted_text.append(f"[color=red]{text}[/color]")
                elif 'skill-buff' in class_name:
                    formatted_text.append(f"[color=#1080e5]{text}[/color]")
                last_text = text

        # Join all parts into a single string with space as a separator
        result_text = ' '.join(formatted_text).replace('  ', ' ').replace('‘',"'").replace("\n","").replace(" "," ").replace("’","'").replace("“","\"").replace("”","\"")
        result_text = re.sub(r'\s+([,\.!?])', r'\1', result_text)

        # Write soulburn
        if is_soulburn:
            soul_burns[soul_burns_index] = result_text
        else:
            hero_skills.append(result_text)

    # Check if character has specialty change
    specialty_change_skills_desc = []
    specialty_change_skills = soup.find_all('div', attrs={'class': 'pad-5', 'style': 'background: var(--background-modifier-darken-alpha);'})
    if specialty_change_skills:
        
        for skill_index, skill in enumerate(specialty_change_skills):
            skill = specialty_change_skills[skill_index].find('div', class_="", style="")
            
            # Initialize the result string
            formatted_text = []

            last_text = ""

            # Process each element in the HTML
            for element in skill.descendants:
                if isinstance(element, str):
                    # Handle plain text
                    text = element.strip()
                    if text and text != last_text:
                        formatted_text.append(text)
                        last_text = text
                elif element.name == 'span':
                    # Process span text with formatting
                    text = element.get_text(strip=True)
                    class_name = element.get('class', [])
                    if 'skill-common' in class_name:
                        formatted_text.append(f"[b]{text}[/b]")
                    elif 'skill-variable' in class_name:
                        formatted_text.append(f"[color=orange]{text}[/color]")
                    elif 'skill-debuff' in class_name:
                        formatted_text.append(f"[color=red]{text}[/color]")
                    elif 'skill-buff' in class_name:
                        formatted_text.append(f"[color=#1080e5]{text}[/color]")
                    last_text = text

            # Join all parts into a single string with space as a separator
            result_text = ' '.join(formatted_text).replace('  ', ' ').replace('‘',"'").replace("\n","").replace(" "," ").replace("’","'").replace("“","\"").replace("”","\"")
            result_text = re.sub(r'\s+([,\.!?])', r'\1', result_text)

            specialty_change_skills_desc.append(result_text)

        # Add specialty change skills to hero skills
        hero_skills = [a + b for a, b in zip(hero_skills, specialty_change_skills_desc)]

    # Fix bug where some skills have double quotation marks
    hero_skills = "[" + ", ".join(['"{}"'.format(name) for name in hero_skills]) + "]"
    
    # Adjust the soul burn array to match the number of skills (order)
    soulburn_count = adjust_array(soulburn_count, soul_burns)

    # Fix bug where some soul burns have double quotation marks
    soul_burns = "[" + ", ".join(['"{}"'.format(name) for name in soul_burns]) + "]"

    # Get skill turns
    skill_turns = []
    spans = soup.find_all('span', style="float: right;")
    turns = [span.get_text(strip=True) for span in spans if 'turns' in span.get_text(strip=True)]
    if len(turns) == 1:
        skill_turns = ['','',turns[0]]
    elif len(turns) == 2:
        skill_turns = ['',turns[0],turns[1]]
    
    else: # When consumes fighting spirit or other resources
        spans = soup.find_all('div', class_="consume-resource col-2")
        turns = [span.get_text(strip=True) for span in spans if 'consume' in span.get_text(strip=True).lower()]
        if len(turns) == 1:
            skill_turns = ['','',turns[0]]
        elif len(turns) == 2:
            skill_turns = ['',turns[0],turns[1]]

    # Save skill images
    divs = soup.find_all('div', class_='icon-box relative')
    # Initialize counter for naming
    counter = 1

    # Iterate through each <div> and find <img> tags
    for div in divs:
        imgs = div.find_all('img')
        
        for img in imgs:
            src = img.get('src')
            if 'skill' in src:  # Filter images with 'skill' in URL
                # Download image
                response = requests.get(src)
                if response.status_code == 200:
                    # Save image with desired naming convention
                    hero_dir = os.path.join(output_dir, hero_code)
                    os.makedirs(hero_dir, exist_ok=True)

                    filename = f'sk_{counter}.png'
                    filepath = os.path.join(hero_dir, filename)
                    with open(filepath, 'wb') as file:
                        file.write(response.content)
                    print(f'Saved: {filepath}')
                    counter += 1

    data.append({
            'Hero': hero_code,
            'Hero Name': hero_name.strip(),
            'Role': role,
            'Element': elem,
            'Hero Skill Names': hero_skill_names,
            'Hero Skill Descriptions': hero_skills,
            'Hero Skill Turns': skill_turns,
            'Soul Burn Count': soulburn_count,
            'Soul Burn Descriptions': soul_burns
        })
    # Go back to initial page when done
    driver.execute_script("window.history.go(-1)")
    driver.refresh() # Refresh the page to prevent stale element
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, last_character)))

    return hero_name
    


hero_elements = driver.find_elements(By.CSS_SELECTOR, 'img.hero-img')
visited_heroes = []
is_done = False
while True:
    try:
        if is_done:
            break

        # Get the hero elements again to prevent stale element
        hero_elements = driver.find_elements(By.CSS_SELECTOR, 'img.hero-img')

        for hero_element in hero_elements:
                hero_name = hero_element.get_attribute('data-src')
                if hero_name is None:
                    is_done = True
                    break

                hero_name = re.search(r'c\d{4}', hero_name).group()

                if hero_name in visited_heroes:
                    continue  # Skip if hero name is already visited

                print(f'Processing hero: {hero_name}')
                
                visited_heroes.append(hero_name)  # Mark hero name as visited
                ActionChains(driver).move_to_element(hero_element).perform()
                button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(hero_element))

                button.click()

                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'e7-chat-bubble')))

                # Scroll to the bottom of the page to load all elements
                driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth' });", driver.find_element(By.CSS_SELECTOR, 'div.text-center.flex-fill'))
                
                sliders = driver.find_elements(By.CSS_SELECTOR, 'div.e7-range-input input[type="range"]')
                for slider in sliders:
                    # Use JavaScript to set the slider's value to the maximum
                    max_value = slider.get_attribute('max')
                    driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input'));", slider, max_value)


                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                current_hero_name = get_detail(soup, driver, hero_name)

                if current_hero_name.strip().lower() == last_char_name.strip().lower():
                    is_done = True  # Set is_done to True if the last character is found
                    break  # Exit the loop

    except Exception as e:
        driver.refresh() # Refresh the page to prevent stale element
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, last_character)))
    
    finally:
        save_to_csv()
driver.quit()

print(len(hero_elements))