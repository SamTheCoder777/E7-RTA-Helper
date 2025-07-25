import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
#from webdriver_manager.firefox import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from selenium.webdriver.firefox.options import Options
from datetime import datetime, timedelta

# Initialize Chrome options
chrome_options = Options()
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--headless')
chrome_options.binary_location = r'/usr/bin/firefox-esr'
def init_driver():
    #print(ChromeService().install())
    #ChromeService(ChromeDriverManager().install())
    return webdriver.Firefox(service=Service('/usr/local/bin/geckodriver'), options=chrome_options)

# Initialize the Chrome driver
driver = init_driver()

# Open the initial URL to establish session/cookies
initial_url = 'https://epic7.onstove.com/en/gg/rank/server'
driver.get(initial_url)

# Optionally, wait for the page to fully load
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

# Store data
data = []
total_matches = 0

# Set to keep track of visited hero names
visited_heroes = set()
# Function to extract match data
def extract_match_data(soup):
    global total_matches
    class_combinations = ['battle-info win', 'battle-info lose']
    battle_info_elements = soup.find_all('li', class_=class_combinations)
    #battle_info_elements = [battle_info_elements[i] for i in range(len(battle_info_elements)) if i not in clicked_button_indices]

    #do only the first index but check it exists
    if len(battle_info_elements) < 1:
        return
    
    battle = battle_info_elements[current_index]
    if 'win' in battle['class']:
        battle_result = "Win"
        enemy_result = "Loss"
    else:
        battle_result = "Loss"
        enemy_result = "Win"

    my_team = battle.find('div', class_='my-team w-100')
    my_team_heroes = my_team.find_all('li', class_=['ban', 'pick-hero']) if my_team else []

    #check if em.show.firstpick exists in my_team
    first_pick = None
    is_my_team_first = my_team.find('em', class_='show firstpick') is not None

    enemy_team = battle.find('div', class_='enemy-team w-100')
    enemy_team_heroes = enemy_team.find_all('li', class_=['ban', 'pick-hero']) if enemy_team else []

    if is_my_team_first:
        first_pick = 'My Team'
    else:
        first_pick = 'Enemy Team'

    match_data = []

    first_pick_index = [1,4,5,8,9]
    second_pick_index = [2,3,6,7,10]
    # My team hero is reversed
    for hero in reversed(my_team_heroes):
        hero_img = hero.find('img')
        hero_code = hero_img['alt'] if hero_img else 'Unknown'
        if hero_code == 'Unknown':
            break
        match_data.append({
            'Match Number': total_matches,
            'Match Result': battle_result,
            'Team': 'My Team',
            'Hero': hero_code,
            'Pick Order': first_pick_index.pop(0) if first_pick == 'My Team' else second_pick_index.pop(0),
            'First Pick': 1 if first_pick == 'My Team' else 0
        })

    for hero in enemy_team_heroes:
        hero_img = hero.find('img')
        hero_code = hero_img['alt'] if hero_img else 'Unknown'
        if hero_code == 'Unknown':
            break
        match_data.append({
            'Match Number': total_matches,
            'Match Result': enemy_result,
            'Team': 'Enemy Team',
            'Hero': hero_code,
            'Pick Order': first_pick_index.pop(0) if first_pick == 'Enemy Team' else second_pick_index.pop(0),
            'First Pick': 1 if first_pick == 'Enemy Team' else 0
        })
    #check if match_data length is 10
    if match_data and len(match_data) == 10:
        total_matches += 1  # Increment only if there's match data
        data.extend(match_data)

# Function to save data to CSV
def save_to_csv():
    csv_file = 'data/epic7_match_history.csv'
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['Match Number', 'Pick Order', 'Match Result', 'Team', 'Hero', 'First Pick'])
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print(f'Data has been successfully written to {csv_file}')

# Restart threshold
restart_threshold = 10

# Timing control
start_time = datetime.now()
end_time = start_time + timedelta(hours=5)
save_interval = timedelta(minutes=5)
last_save_time = start_time

# Track Server
server_names = ['Global', 'Korea', 'Asia', 'Europe', 'Japan']
#server_names = ['All Servers']
current_server_name = server_names.pop(0)

try:
    global clicked_button_indices, current_index
    heroes_processed = 0
    main_failures = 0
    failures = 0
    while True:  # Infinite loop to keep scraping
        try:
            current_time = datetime.now()

            '''
            # Check if the 5-hour mark has been reached
            if current_time >= end_time:
                print("Reached the 5-hour mark. Exiting...")
                break
            '''
            
            # Save CSV every 5 minutes
            if current_time - last_save_time >= save_interval:
                save_to_csv()
                last_save_time = current_time

            # Restart the driver if the threshold is reached
            if heroes_processed >= restart_threshold:
                driver.close()
                driver.quit()  # Quit the current driver
                driver = init_driver()  # Start a new driver
                driver.get(initial_url)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                heroes_processed = 0  # Reset the counter

            """
            # server selection
            current_active_server = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.select-box.grade div.option.selected"))).text
            
            if current_active_server != current_server_name:
                # Iterate through all servers
                server_option = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.select-box.grade div.option.selected")))
                server_option.click()

                # Wait for the dropdown to open
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "triangle-down.open")))

                # Get all server options
                server_elements = driver.find_elements(By.CSS_SELECTOR, "div.select-box.grade.open ul li.option, div.select-box.grade.open ul li.option.active")
                server_index = 0
                for element in server_elements:
                    if element.text == current_server_name:
                        server_index = server_elements.index(element)
                        print(f"Found server index: {server_index}")
                        print(f"Current server name: {current_server_name}")
                        break
                
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable(server_elements[server_index]))
                server_elements[server_index].click() # Click the next server

                time.sleep(5)  # Wait for the page to load after clicking
            """

            # Click through all elements with class 'hero-name'
            hero_elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'hero-name')))
            
            for i, hero_element in enumerate(hero_elements):
                try:
                    hero_name = hero_element.text.strip()
                    if hero_name in visited_heroes:
                        continue  # Skip if hero name is already visited
                    
                    print(f'player {i}/{len(hero_elements)}')
                    print('processing player: ' + hero_name)
                    
                    visited_heroes.add(hero_name)  # Mark hero name as visited

                    hero_element.click()
                    time.sleep(5)  # Wait for the page to load after clicking

                    # Click through all buttons on the hero page
                    clicked_button_indices = []
                    matches = 0
                    while matches < 100:
                        try:
                            btn_details = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'btn-detail')))
                            new_button_indices = [i for i in range(len(btn_details)) if i not in clicked_button_indices]

                            if not new_button_indices:
                                break  # No more buttons to click, exit loop

                            for index in new_button_indices:
                                try:
                                    matches += 1  # Increment match
                                    clicked_button_indices.append(index)
                                    current_index = index
                                    #time.sleep(5)  # Wait for dynamic content to load
                                    page_source = driver.page_source
                                    soup = BeautifulSoup(page_source, 'html.parser')
                                    extract_match_data(soup)

                                    if matches >= 100:
                                        break

                                    # Re-fetch the button elements after each click
                                    btn_details = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'btn-detail')))
                                except Exception as e:
                                    print(f"Error clicking button: {e}")

                            # Check if there are more match history to load
                            load_more_button = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.CLASS_NAME, 'loadMoreBtn')))
                            load_more_button.click()
                            time.sleep(2)  # Wait for additional content to load
        
                        except Exception as e:
                            print(f"Error in main loop: {e}")
                            break

                    # Go back to the initial page to click the next hero
                    driver.execute_script("window.history.go(-1)")  # Go back to the main page
                    driver.refresh()  # Refresh the page
                    time.sleep(2)  # Wait for the page to load after going back

                    heroes_processed += 1  # Increment the counter after processing a hero

                except Exception as e:
                    print(f"Error clicking hero element: {e}")

            # Check if there are more heroes to load
            try:
                load_more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'loadMoreBtn')))
                #load_more_button.click()
                driver.execute_script("arguments[0].click();", load_more_button)
                time.sleep(2)  # Wait for additional content to load
                failures = 0  # Reset the failure counter
            except Exception as e:
                failures += 1
                print(f"No more heroes to load: {e}")

                # Move to the next server if there are more servers to load
                if failures >= 3 and len(server_names)>0:
                    current_server_name = server_names.pop(0)
                    failures = 0

                # Exit if there are no more servers to load
                elif failures >= 5 and len(server_names) == 0:
                    print("No more heroes to load. Saving and Exiting...")
                    save_to_csv()
                    break
        except Exception as e:
            main_failures += 1
            print(f"Failure when trying to search players: {e}")
            driver.refresh()  # Refresh the page

            if main_failures >= 5:
                print("No more players to load. Saving and Exiting...")
                save_to_csv()

except KeyboardInterrupt:
    print("Manually interrupted")

finally:
    # Close the driver
    driver.quit()

    # Write the data to a CSV file
    save_to_csv()
