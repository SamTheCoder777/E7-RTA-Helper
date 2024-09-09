import os
import socket
import cv2
import logging
from flask import Flask, jsonify, request

import numpy as np
import win32gui
import pandas as pd
from CaptureScreen import capture_screen

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
import time

# recommender imports
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
import tensorflow as tf
from attention import Attention
import ast

# For updating
import fsspec
from pathlib import Path
from packaging.version import Version
import json

# Function to send keys with a delay
def send_keys_slowly(element, text, delay=0.1):
    for char in text:
        element.send_keys(char)
        time.sleep(delay)

app = Flask(__name__)

# Configure logging
logging.basicConfig(filename='server.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_json_from_github():
    url = f"https://raw.githubusercontent.com/SamTheCoder777/E7-RTA-Helperr/main/versions.json"
    response = requests.get(url)
    
    if response.status_code == 200:
        json_data = response.json()  # Parse the response as JSON
        return json_data
    else:
        raise Exception(f"Failed to fetch file from GitHub. Status code: {response.status_code}")
    
def recursive_copy(src_dir, dst_dir):
    # Initialize the GitHub filesystem
    fs = fsspec.filesystem("github", org="SamTheCoder777", repo="E7-RTA-Helper")
    # List the contents of the source directory
    for item in fs.ls(src_dir, detail=True):
        item_path = item["name"]
        if item["type"] == "file":
            # It's a file, copy it to the destination
            destination_file = Path(dst_dir) / Path(item_path).name
            fs.get(item_path, destination_file.as_posix())
            print(f"Copied file: {item_path} -> {destination_file}")
        elif item["type"] == "directory":
            # It's a directory, create it in the destination and copy its contents recursively
            destination_subdir = Path(dst_dir) / Path(item_path).name
            destination_subdir.mkdir(exist_ok=True, parents=True)
            print(f"Entering directory: {item_path}")
            recursive_copy(item_path, destination_subdir)


@app.route('/check_update', methods=['GET'])
def check_update():
    try:
        server_json = fetch_json_from_github()

        server_data_version = server_json['data_version']
        server_program_version = server_json['program_version']

        #open versions.json
        with open('versions.json') as f:
            data = json.load(f)
            current_data_version = data['data_version']
            current_program_version = data['program_version']
            

        # Convert strings to Version objects
        current_data_version_obj = Version(current_data_version)
        server_data_version_obj = Version(server_data_version)

        current_program_version_obj = Version(current_program_version)
        server_program_version_obj = Version(server_program_version)

        is_data_updated = False
        is_program_updated = False

        # Compare the versions
        if current_data_version_obj < server_data_version_obj:
            print(f"New version: {server_data_version}is found. Updating...")
            
            recursive_copy("data", "./data")

            recursive_copy("dataset", "./dataset")

            recursive_copy("CharacterUI", "./CharacterUI")

            data['data_version'] = server_data_version
            with open('versions.json', 'w') as f:
                json.dump(data, f)
            
            is_data_updated = True
        else:
            print(f"{current_data_version} is up to date")

        if current_program_version_obj < server_program_version_obj:
            is_data_updated = True
        
        return jsonify({"data_updated": is_data_updated, "program_updated": is_program_updated}), 200
    
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return 'Error could not check for update', 500

@app.route('/search', methods=['GET'])
def search():
    try:
        # Initialize the Chrome driver
        chrome_options = Options()
        #chrome_options.add_argument("--headless")  # Enable headless mode
        #chrome_options.add_argument("--disable-gpu")
        #chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=chrome_options)

        # Navigate to the URL
        driver.get("https://epic7.gg.onstove.com/en")

        # Wait for the server option to be clickable and click it
        wait = WebDriverWait(driver, 10)
        server_option = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "server-option.selected-option")))
        server_option.click()

        # Wait for the dropdown to open
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "triangle-down.open")))

        # Get all server options
        server_elements = driver.find_elements(By.CSS_SELECTOR, "li.server-option")

        # Initialize an empty dictionary to store the data
        character_stats = {}
        hero_data = []

        server_index = 0

        # Does player have data
        player_has_data = True

        # Name of the player
        player_name = request.args.get('name')

        # Server to search
        server = request.args.get('server')

        server_clicked = False

        # Loop through each server element
        for server_element in server_elements:
            if not server_clicked and server_element.text.lower() != server.lower():
                server_index += 1
                continue

            server_clicked = True
            servers = driver.find_elements(By.CSS_SELECTOR, "li.server-option")
            
            # Click the current server element
            servers[server_index].click()
            server_index += 1

            # Find and clear the search input
            search_input = driver.find_element(By.CLASS_NAME, "search-input")
            search_input.send_keys(Keys.CONTROL + "a")
            search_input.send_keys(Keys.DELETE)
            send_keys_slowly(search_input, player_name, delay=0.05)
            search_input.send_keys(Keys.ENTER)

            # Check if there is no data
            try:
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "nodata-img")))
            except TimeoutException:
                pass
            except Exception:
                return jsonify({"message": f"Error: No data found"}), 500 

            # Check if the battle list is present
            try:
                battle_list = wait.until(EC.presence_of_element_located((By.ID, "battleList")))
            except TimeoutException:
                return jsonify({"message": f"Error: No data found"}), 500 

            #here instead of using the driver, selenium, can we use the beautifulsoup? there is nothing to interact with the page
            
            # Get the win/loss stats
            win_loss = driver.find_element(By.CSS_SELECTOR, "div.wl-score").text
            total_wins = int(win_loss.split('W')[0].strip())
            total_losses = int(win_loss.split('W')[1].split('L')[0].strip())
            win_rate = float(win_loss.split('(')[1].split('%')[0].strip())


            # Locate all hero elements
            heroes = driver.find_elements(By.CSS_SELECTOR, ".hero-list ul li")

            # Loop through each hero element and extract the necessary data
            for hero in heroes:
                img = hero.find_element(By.CSS_SELECTOR, ".hero-img img")
                code = img.get_attribute("alt")

                name = hero.find_element(By.CSS_SELECTOR, ".name").text

                score = hero.find_element(By.CSS_SELECTOR, ".score")
                wins = score.find_element(By.CSS_SELECTOR, "span:nth-child(1)").text
                losses = score.find_element(By.CSS_SELECTOR, "span:nth-child(2)").text
                win_rate = score.find_element(By.CSS_SELECTOR, "span:nth-child(3)").text

                hero_data.append({
                    "code": code,
                    "name": name,
                    "wins": wins,
                    "losses": losses,
                    "win_rate": win_rate
                })

            # Get all battle information
            battles = driver.find_elements(By.CSS_SELECTOR, "li.win.battle-info, li.lose.battle-info")
            for battle in battles:
                battle_type = "win" if "win" in battle.get_attribute("class") else "loss"
                characters = battle.find_elements(By.CSS_SELECTOR, "ul.flex-vert.align-end li.pick-hero")

                for character in characters:
                    alt_text = character.find_element(By.TAG_NAME, "img").get_attribute("alt")
                    if alt_text not in character_stats:
                        character_stats[alt_text] = {"wins": 0, "losses": 0}

                    if battle_type == "win":
                        character_stats[alt_text]["wins"] += 1
                    else:
                        character_stats[alt_text]["losses"] += 1
                        
            break
        return jsonify({"hero_data": hero_data, "character_stats": character_stats, "player_has_data": player_has_data})
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500 


# Function to recommend a hero
# Load the CSV file
data = pd.read_csv('data/epic7_match_history.csv')
win_rates = {}

@app.route('/init_recommender', methods=['GET'])
def init_recommender():
    global type_encoder, hero_encoder, max_sequence_length, model, hero_types, hero_type_dict, available_heroes, most_picked
    try:
        with open('data/rec_variables.pkl', 'rb') as f:
            type_encoder, hero_encoder, max_sequence_length = pickle.load(f)
        model = tf.keras.models.load_model('data/rec_model.h5', custom_objects={'Attention': Attention})
        hero_types = pd.read_csv('data/hero_types.csv')
        hero_types['type_list'] = hero_types['type'].apply(ast.literal_eval)

        # In case user and enemy are both empty, recommend random hero from top 50
        # most picked heroes
        most_picked = pd.read_csv('data/epic7_hero_stats.csv')
        most_picked = most_picked.sort_values(by='Pick Rate', ascending=False)
        most_picked = most_picked['Hero'].values[:50]

        # Transform type_list and handle multiple columns
        encoded_types = type_encoder.transform(hero_types['type_list'].tolist())
        encoded_columns = [f'encoded_type_{i}' for i in range(encoded_types.shape[1])]
        hero_types[encoded_columns] = pd.DataFrame(encoded_types, index=hero_types.index)

        # Precompute a dictionary for fast lookup
        hero_type_dict = dict(zip(hero_types['code'], encoded_types))
        hero_type_dict['unknown'] = type_encoder.transform([['Unknown']])[0]
        
        # check available heroes and store in dictionary as key
        available_heroes = {key: None for key in hero_encoder.classes_}

        # Use model.predict to initialize the model
        predict_next_hero(['unknown'], ['unknown'], 'My Team')

        return jsonify({"message": "Recommender model initialized successfully"}), 200

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500
    
def process_picks(first_team_picks, non_first_team_picks):
    # Define the maximum picks allowed at each stage based on the first team's picks
    max_non_first_team_picks = [0, 2, 2, 4, 4, 5]
    max_first_team_picks = [1, 1, 3, 3, 5, 5, 5]

    len_first_team_picks = len(first_team_picks)
    len_non_first_team_picks = len(non_first_team_picks)

    # Limit the non-first team's picks according to the first team's picks
    if len_first_team_picks < 6:
        non_first_team_picks = non_first_team_picks[:max_non_first_team_picks[len_first_team_picks]]

    # Limit the first team's picks according to the non-first team's picks
    if len_non_first_team_picks < 6:
        first_team_picks = first_team_picks[:max_first_team_picks[len_non_first_team_picks]]

    # Ensure both lists have a maximum of 6 elements
    first_team_picks = first_team_picks[:5]
    non_first_team_picks = non_first_team_picks[:5]

    return first_team_picks, non_first_team_picks

def predict_next_hero(enemy_team_picks, user_team_picks, first_pick_team):
    combined_sequence = []
    combined_types = []
    first_pick_index = [0, 3, 4, 7, 8]
    enemy_index = 0
    user_index = 0

    # Filter out unavailable heroes
    for i, hero in enumerate(user_team_picks):
        if hero not in available_heroes.keys():
            print(f"Hero {hero} not found in available heroes. Removing from user picks.")
            user_team_picks[i] = 'unknown'
            
    for i, hero in enumerate(enemy_team_picks):
        if hero not in available_heroes.keys():
            print(f"Hero {hero} not found in available heroes. Removing from enemy picks.")
            enemy_team_picks[i] = 'unknown'

    # When both are empty, then return a high pickrate hero
    if first_pick_team == 'My Team' and len(user_team_picks) == 0:
        np.random.shuffle(most_picked)
        most_picks = most_picked[:10].tolist()
        return jsonify({
        'top_10_heroes': most_picks,
        'win_prediction': str(50.0)
        }), 200
    
    elif first_pick_team == 'Enemy Team' and len(enemy_team_picks) == 0:
        np.random.shuffle(most_picked)
        most_picks = most_picked[:10].tolist()
        return jsonify({
        'top_10_heroes': most_picks,
        'win_prediction': str(50.0)
        }), 200

    # Get only the first 5 in enemy and user picks
    enemy_team_picks = enemy_team_picks[:5]
    user_team_picks = user_team_picks[:5]

    # Determine the pick limits based on who picks first
    if first_pick_team == 'My Team':
        user_team_picks, enemy_team_picks = process_picks(user_team_picks, enemy_team_picks)
    else:
        enemy_team_picks, user_team_picks = process_picks(enemy_team_picks, user_team_picks)
    
    
    # First pick win/loss sequence
    first_pick_win_sequences = []

    if first_pick_team == 'My Team':
        first_pick_win_sequences = [1,1,1,1,1,1,1,1,1,1]

    else:
        first_pick_win_sequences = [0,0,0,0,0,0,0,0,0,0]


    # Vectorized and Precomputed Lookup
    if first_pick_team == 'My Team':
        for i in range(len(user_team_picks) + len(enemy_team_picks)):
            if i in first_pick_index:
                combined_sequence.append(user_team_picks[user_index])
                combined_types.append(hero_type_dict[user_team_picks[user_index]])
                #print(f"User :" + hero_type_dict[user_team_picks[user_index]].as_string())
                user_index += 1
            else:
                combined_sequence.append(enemy_team_picks[enemy_index])
                combined_types.append(hero_type_dict[enemy_team_picks[enemy_index]])
                #print(f"Enemy :" + hero_type_dict[enemy_team_picks[enemy_index]].as_string())
                enemy_index += 1
    else:
        for i in range(len(user_team_picks) + len(enemy_team_picks)):
            if i in first_pick_index:
                combined_sequence.append(enemy_team_picks[enemy_index])
                combined_types.append(hero_type_dict[enemy_team_picks[enemy_index]])
                #print(f"Enemy :" + hero_type_dict[enemy_team_picks[enemy_index]].as_string())
                enemy_index += 1
            else:
                combined_sequence.append(user_team_picks[user_index])
                combined_types.append(hero_type_dict[user_team_picks[user_index]])
                #print(f"User :" + hero_type_dict[user_team_picks[user_index]].as_string())
                user_index += 1

    picks_sequence_encoded = hero_encoder.transform(combined_sequence)
    padded_sequence = pad_sequences([picks_sequence_encoded], maxlen=max_sequence_length, padding='pre')

    # Drafting order and sequences
    first_pick_team_encoded = 0 if first_pick_team == 'My Team' else 1
    full_pick_order_sequence = np.arange(1, len(combined_sequence) + 1)
    full_team_sequence = np.array([0, 1, 1, 0, 0, 1, 1, 0, 0, 1] if first_pick_team_encoded == 0 else [1, 0, 0, 1, 1, 0, 0, 1, 1, 0])
    first_pick_sequence = np.array([1, 0, 0, 1, 1, 0, 0, 1, 1, 0])

    # Ensure that the sequences do not contain any out-of-range indices before padding
    padded_sequence = np.clip(padded_sequence, 0, len(hero_encoder.classes_) - 1)
    full_pick_order_sequence = np.clip(full_pick_order_sequence, 0, max_sequence_length - 1)
    full_team_sequence = np.clip(full_team_sequence, 0, max_sequence_length - 1)
    first_pick_sequence = np.clip(first_pick_sequence, 0, max_sequence_length - 1)
    combined_types = [np.clip(seq, 0, 1) for seq in combined_types]  # Assuming combined_types are multi-hot vectors

    padded_order_sequence = pad_sequences([full_pick_order_sequence], maxlen=max_sequence_length, padding='pre')
    padded_team_sequence = pad_sequences([full_team_sequence], maxlen=max_sequence_length, padding='pre')
    padded_first_pick_sequence = pad_sequences([first_pick_sequence], maxlen=max_sequence_length, padding='pre')
    padded_types_sequence = pad_sequences([combined_types], maxlen=max_sequence_length, padding='pre', dtype=object, value=[0]*len(type_encoder.classes_))
    padded_types_sequence = np.array([np.stack(x) for x in padded_types_sequence], dtype=np.float32)
    X_first_pick_wins = pad_sequences([first_pick_win_sequences], maxlen=max_sequence_length, padding='pre')
    
    print(f"Max sequence length: {max_sequence_length}")

    print("Shapes before filtering:")
    print("padded_sequence:", padded_sequence.shape)
    print("padded_order_sequence:", padded_order_sequence.shape)
    print("padded_team_sequence:", padded_team_sequence.shape)
    print("padded_first_pick_sequence:", padded_first_pick_sequence.shape)
    print("padded_types_sequence:", padded_types_sequence.shape)

    valid_indices = np.all(padded_order_sequence < max_sequence_length, axis=1)
    padded_sequence = padded_sequence[valid_indices]
    padded_order_sequence = padded_order_sequence[valid_indices]
    padded_team_sequence = padded_team_sequence[valid_indices]
    padded_first_pick_sequence = padded_first_pick_sequence[valid_indices]
    padded_types_sequence = padded_types_sequence[valid_indices]

    print("Shapes after filtering:")
    print("padded_sequence:", padded_sequence.shape)
    print("padded_order_sequence:", padded_order_sequence.shape)
    print("padded_team_sequence:", padded_team_sequence.shape)
    print("padded_first_pick_sequence:", padded_first_pick_sequence.shape)
    print("padded_types_sequence:", padded_types_sequence.shape)
    
    prediction, win_prediction = model.predict([padded_sequence, padded_order_sequence, padded_team_sequence, padded_first_pick_sequence, padded_types_sequence, X_first_pick_wins])

    combined_hero_indices = set(picks_sequence_encoded)
    top_10_indices = np.argsort(prediction[0])[::-1]
    filtered_top_10_indices = [idx for idx in top_10_indices if idx not in combined_hero_indices][:10]

    top_10_heroes = hero_encoder.inverse_transform(filtered_top_10_indices)

    # if both are full, return only win prediction
    if len(user_team_picks) >= 5 and len(enemy_team_picks) >= 5:
        return jsonify({
        'top_10_heroes': [],
        'win_prediction': str(win_prediction[0][0]) if first_pick_team == 'My Team' else str(1.0-win_prediction[0][0])
        }), 200

    return jsonify({
        'top_10_heroes': top_10_heroes.tolist(),
        'win_prediction': str(win_prediction[0][0]) if first_pick_team == 'My Team' else str(1.0-win_prediction[0][0])
    }), 200

@app.route('/recommend', methods=['GET'])
def recommend_characters():
    try:
        recommendations = []
        try:
            enemy_picks = request.args.get('enemy_picks')
            enemy_picks = enemy_picks.split(',')
            user_picks = request.args.get('user_picks')
            user_picks = user_picks.split(',')
            first_pick_team = request.args.get('first_pick_team')
        except Exception:
            return jsonify({"message": "Please provide enemy_picks and user_picks and first_pick_team"}), 400
        
        try:
            available_characters = request.args.get('available_characters')
            available_characters = available_characters.split(',')
        except Exception:
            available_characters = set(data['Hero'].unique()) - set(user_picks) - set(enemy_picks)
            
        result = predict_next_hero(enemy_picks, user_picks, first_pick_team)
        return result
    
    except Exception as e:
        print('Error on recommend: ', str(e))
        logging.error(f"Error: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500


@app.route('/status', methods=['GET'])
def status():
    return jsonify({"message": "Server is running"}), 200

def configure_port():
    # Check if server_port.txt exists
    # Generate a new port if server_port.txt doesn't exist
    port = find_available_port()
    with open('search_server_port.txt', 'w') as f:
        f.write(str(port))
    print(f"Port {port} written to search_server_port.txt")
    return port

def find_available_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    
@app.get('/shutdown')
def shutdown():
    #shutdown_server()
    driver.quit()
    os.kill(os.getpid(), 9)
    return jsonify({"message": "Server shutting down"}), 200

if __name__ == '__main__':
    port = configure_port()
    print(f"Starting server on port {port}")
    logging.info(f"Starting server on port {port}")
    app.run(host='127.0.0.1', port=port)
