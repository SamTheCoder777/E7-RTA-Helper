import os
import socket
import cv2
import logging
from flask import Flask, jsonify, request

import win32gui
import numpy as np
import pandas as pd
from CaptureScreen import capture_screen

app = Flask(__name__)

# Configure logging
logging.basicConfig(filename='server.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

template_images = None
descriptor_cache = None

characters_in_match = []
positions = {}
y_coords = {}

@app.route('/set_num_threads', methods=['GET'])
def set_num_threads():
    try:
        num_threads = int(request.args.get('num_threads'))
        cv2.setNumThreads(num_threads)
        return jsonify({"message": f"Number of threads set to {num_threads}"})
    except Exception as e:
        return jsonify({"message": f"Error setting number of threads: {str(e)}"}), 500
    
def load_multiple_templates(character_folder, max_templates=3):
    templates = []
    for i in range(max_templates):
        suffix = f"_{i}" if i > 0 else ""
        normal_image_path = os.path.join(character_folder, f'c{suffix}.png')
        flipped_image_path = os.path.join(character_folder, f'c{suffix}_flipped.png')

        if os.path.exists(normal_image_path) and os.path.exists(flipped_image_path):
            normal_image = cv2.imread(normal_image_path)
            flipped_image = cv2.imread(flipped_image_path)

            if normal_image is not None and flipped_image is not None:
                normal_gray = cv2.cvtColor(normal_image, cv2.COLOR_BGR2GRAY)
                flipped_gray = cv2.cvtColor(flipped_image, cv2.COLOR_BGR2GRAY)
                templates.append((normal_gray, flipped_gray))

    return templates

def init_cache():
    global template_images, descriptor_cache
    try:
        template_images = {}
        descriptor_cache = {}

        for character in os.listdir('dataset'):
            character_folder = os.path.join('dataset', character)
            if os.path.isdir(character_folder):
                templates = load_multiple_templates(character_folder)

                if templates:
                    template_images[character] = templates
                    descriptor_cache[character] = []

                    for normal_gray, flipped_gray in templates:
                        keypoints_normal, descriptors_normal = compute_descriptors(normal_gray)
                        keypoints_flipped, descriptors_flipped = compute_descriptors(flipped_gray)
                        descriptor_cache[character].append(
                            (keypoints_normal, descriptors_normal, 
                             keypoints_flipped, descriptors_flipped)
                        )

        logging.info('Cache initialized successfully')
    except Exception as e:
        logging.error(f'Error initializing cache: {str(e)}')

def SIFT_feature_matching(target_gray, descriptors_target, keypoints_target, character, template_index):  
		keypoints_template_normal, descriptors_template_normal, keypoints_template_flipped, descriptors_template_flipped = descriptor_cache[character][template_index]
          
		bf = cv2.BFMatcher()
		matches = bf.knnMatch(descriptors_template_normal, descriptors_target, k=2)
		matches_flipped = bf.knnMatch(descriptors_template_flipped, descriptors_target, k=2)

		flipped = False
		good_matches = []
		for m, n in matches:
			if m.distance < 0.5 * n.distance:
				good_matches.append(m)

		min_good_matches = 5
		if len(good_matches) < min_good_matches:
			good_matches.clear()
			flipped = True
			for m, n in matches_flipped:
				if m.distance < 0.5 * n.distance:
					good_matches.append(m)

		if len(good_matches) >= min_good_matches:
			characters_in_match.append(character)

			matched_coords = [keypoints_target[m.trainIdx].pt for m in good_matches]
			avg_x = np.mean([pt[0] for pt in matched_coords])
			avg_y = np.mean([pt[1] for pt in matched_coords])

			position = 'left' if avg_x < target_gray.shape[1] / 2 else 'right'

			positions[character] = position
			y_coords[character] = avg_y
                     

def compute_descriptors(image):
		if not isinstance(image, np.ndarray):
			raise ValueError("Image must be a numpy array")
		sift = cv2.SIFT_create()
		keypoints, descriptors = sift.detectAndCompute(image, None)
		return keypoints, descriptors

@app.route('/detect_enemy', methods=['GET'])
def _test_SIFT_feature_matching():

    window_title = request.args.get('title')

    crop_top_percent = 1
    crop_bottom_percent = 1
    crop_right_percent = 1
    crop_left_percent = 1
    crop_middle = 0

    crops = request.args.get('crops')
    if crops:
        crops = crops.split(',')
        crop_top_percent, crop_bottom_percent, crop_right_percent, crop_left_percent, crop_middle = map(float, crops)


    'rta_2.jpg'
	# Capture window
    target_image = capture_screen(window_title)  # Reduce resolution

    if target_image is None:
        raise ValueError("Failed to load target image")

    height, width = target_image.shape[:2]
    crop_left = int(width * (crop_left_percent / 100))
    crop_right = int(width * (crop_right_percent / 100))
    crop_bottom = int(height * (crop_bottom_percent / 100))
    crop_top = int(height * (crop_top_percent / 100))

    target_image = target_image[crop_top:-crop_bottom, crop_left:-crop_right]

    # Crop middle

    height, width = target_image.shape[:2]
    middle = width // 2
    offset = int(width * (float(crop_middle)/100)) // 2  # 20% of the image width

    # Now crop middle
    left = target_image[:, :middle-offset]
    right = target_image[:, middle+offset:]

    # Concatenate the two parts back together
    target_image = np.concatenate((left, right), axis=1)
    target_gray = cv2.cvtColor(target_image, cv2.COLOR_BGR2GRAY)

    sift = cv2.SIFT_create()
    keypoints_target, descriptors_target = sift.detectAndCompute(target_gray, None)

    # Clear previous results
    characters_in_match.clear()  
    positions.clear()
    y_coords.clear()

    for character, templates in template_images.items():
        for template_index, (normal_gray, flipped_gray) in enumerate(templates):
            SIFT_feature_matching(target_gray, descriptors_target, keypoints_target, character, template_index)

    user_team = [code for code, position in positions.items() if position == 'left']
    user_team.sort(key=lambda x: y_coords[x])
    enemy_team = [code for code, position in positions.items() if position == 'right']
    enemy_team.sort(key=lambda x: y_coords[x])
    return jsonify({"user_team": user_team, "enemy_team": enemy_team})


@app.route('/capture_save', methods=['GET'])
def capture_save():
    try:
        window_title = request.args.get('title')

        crop_top_percent = 1
        crop_bottom_percent = 1
        crop_right_percent = 1
        crop_left_percent = 1
        crop_middle = 0
            
        image = capture_screen(window_title)

        height, width = image.shape[:2]
        crop_left = int(width * (crop_left_percent / 100))
        crop_right = int(width * (crop_right_percent / 100))
        crop_bottom = int(height * (crop_bottom_percent / 100))
        crop_top = int(height * (crop_top_percent / 100))

        target_image = image[crop_top:-crop_bottom, crop_left:-crop_right]

        # Crop middle

        height, width = target_image.shape[:2]
        middle = width // 2
        offset = int(width * (float(crop_middle)/100)) // 2  # 20% of the image width

        # Now crop middle
        left = target_image[:, :middle-offset]
        right = target_image[:, middle+offset:]

        # Concatenate the two parts back together
        target_image = np.concatenate((left, right), axis=1)
        if target_image.any():
            temp_image = target_image
            cv2.imwrite('temp.png', target_image)
            return jsonify({"message": "Image saved as temp.png successfully"})
        else:
            return jsonify({"message": "Failed to save image, Image Null"}), 500
    except Exception as e:
        return jsonify({"message": f"Error saving image: {str(e)}"}), 500

@app.route('/crop_image', methods=['GET'])
def crop_image():
    try:
        crop_top_percent = 1
        crop_bottom_percent = 1
        crop_right_percent = 1
        crop_left_percent = 1
        crop_middle = 0

        crops = request.args.get('crops')
        if crops:
            crops = crops.split(',')
            crop_top_percent, crop_bottom_percent, crop_right_percent, crop_left_percent, crop_middle = map(float, crops)

        temp_image = cv2.imread('temp.png')
        height, width = temp_image.shape[:2]
        crop_left = int(width * (crop_left_percent / 100))
        crop_right = int(width * (crop_right_percent / 100))
        crop_bottom = int(height * (crop_bottom_percent / 100))
        crop_top = int(height * (crop_top_percent / 100))

        target_image = temp_image[crop_top:-crop_bottom, crop_left:-crop_right]

        # Crop middle

        height, width = target_image.shape[:2]
        middle = width // 2
        offset = int(width * (float(crop_middle)/100)) // 2  # 20% of the image width

        # Now crop middle
        left = target_image[:, :middle-offset]
        right = target_image[:, middle+offset:]

        # Concatenate the two parts back together
        target_image = np.concatenate((left, right), axis=1)
        if target_image.any():
            cv2.imwrite('temp_cropped.png', target_image)
            return jsonify({"message": "Image cropped successfully"})
        else:
            return jsonify({"message": "Failed to crop image, Image Null"}), 500
    except Exception as e:
        return jsonify({"message": f"Error cropping image: {str(e)}"}), 500

@app.route('/get_window_titles', methods=['GET'])

def get_window_titles():
    def enum_windows_proc(hwnd, window_titles):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                window_titles.append(title)
        return True

    try:
        window_titles = []
        win32gui.EnumWindows(enum_windows_proc, window_titles)
        windows_joined = ",".join(window_titles)
        return window_titles
    except Exception as e:
        return str(e), 500


def configure_port():
    # Check if server_port.txt exists
    # Generate a new port if server_port.txt doesn't exist
    port = find_available_port()
    with open('server_port.txt', 'w') as f:
        f.write(str(port))
    print(f"Port {port} written to server_port.txt")

    return port

def find_available_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port

@app.route('/init_cache', methods=['GET'])
def init_cache_route():
    try:
        init_cache()
        return jsonify({"message":len(template_images.items()) })
    except Exception as e:
          return jsonify({"message": f"Error initializing cache: {str(e)}"}),500
    
@app.route('/status', methods=['GET'])
def status():
    return jsonify({"message": "Server is running"}), 200

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    
@app.get('/shutdown')
def shutdown():
    #shutdown_server()
    os.kill(os.getpid(), 9)
    return jsonify({"message": "Server shutting down"}), 200


if __name__ == '__main__':
    port = configure_port()
    print(f"Starting server on port {port}")
    logging.info(f"Starting server on port {port}")
    app.run(host='127.0.0.1', port=port)
