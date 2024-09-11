extends Node

# Python server related
var python_exe_path = "python/install/python.exe"
var python_search_script_path = "search_server.py"	
var python_script_path = "server.py"

var misc_http_request: HTTPRequest
var misc_thread: Thread
var http_request: HTTPRequest
var thread: Thread


var misc_port
var port

var server_running = false
var misc_server_running = false

var main_status
var misc_status
#------------------------------
# Has detection cache been created?
var isDetectionCache = false
var isInitRecommender = false

var user_data

var hero_data # Official hero stats from Epic7
var hero_match_data # Calculated from match history
var hero_names # Hero names with codes
var hero_details # Hero info like skills
var buffs_debuffs_details # Buffs/Debuffs details

# Can you request for detection?
var request_done = false

var pid
var search_pid

# For Loading Screen Status
var loading_status = ""
var status_connected_num = 0

func read_csv(path: String):
	var rows = []
	var file = FileAccess.open(path, FileAccess.READ)
	if file:
		while !file.eof_reached():
			var csv_rows = file.get_csv_line(",")
			rows.append(csv_rows)
		file.close()
		rows.pop_back() #remove last empty array get_csv_line() has created 
		var headers = Array(rows[0])
		
		rows.pop_front() # remove header
		var csv_array = []
		for row in rows:
			var csv = {}
			
			for header_id in headers.size():
				#print(row)
				csv[headers[header_id]] = row[header_id]
			csv_array.append(csv)
		return csv_array
	else:
		return []

# Called when the node enters the scene tree for the first time.
func _ready():
	# Check OS
	match OS.get_name():
		"Windows":
			python_exe_path = "python/install/.venv/Scripts/python.exe"
			python_search_script_path = "search_server.py"	
			python_script_path = "server.py"
			
		"macOS":
			python_exe_path = "python_mac/install/bin/.venv/bin/python3.11"
			python_search_script_path = "search_server_mac.py"	
			python_script_path = "server_mac.py"
	
	# Load all csvs
	hero_match_data = read_csv("data/epic7_hero_stats.csv")
	hero_data = read_csv("data/hero_official_stats.csv")
	hero_names = read_csv("data/hero_code_to_name.csv")
	for hero in hero_data:
		if hero['Hero'] == 'c6062':
			print(hero)
	
	hero_details = read_csv('data/hero_details.csv')
	buffs_debuffs_details = read_csv('data/buffs_debuffs_details.csv')
	# Now initialize the HTTPRequest node to communicate with the server
	http_request = HTTPRequest.new()
	add_child(http_request)
	http_request.request_completed.connect(self._on_request_completed)
	
	# init misc server http
	misc_http_request = HTTPRequest.new()
	add_child(misc_http_request)
	misc_http_request.request_completed.connect(self._on_search_request_completed)
	
	main_status = HTTPRequest.new()
	add_child(main_status)
	main_status.timeout = 3	
	main_status.request_completed.connect(self._status_check)
	
	misc_status = HTTPRequest.new()
	add_child(misc_status)
	misc_status.timeout = 3
	misc_status.request_completed.connect(self._misc_status_check)
	
	# Start the server in a separate thread
	misc_thread = Thread.new()
	misc_thread.start(_run_search_server.bind(python_exe_path, python_search_script_path))

	# Start the detection server in a separate thread
	thread = Thread.new()
	thread.start(_run_server.bind(python_exe_path, python_script_path))
	
	#http_request.request(url)

func get_user_data(name, server):
	misc_http_request.request("http://127.0.0.1:"+str(misc_port)+"/search?name="+str(name).uri_encode()+"&server="+str(server))
	await misc_http_request.request_completed
	return user_data
	
# Function to recommend the top characters based on win rate and number of matches
func recommend_top_characters(character_stats: Dictionary, top_n: int = 5) -> Array:
	var character_scores = {}
	
	# Calculate scores for each character
	for character in character_stats.keys():
		var stats = character_stats[character]
		var total_matches = stats['wins'] + stats['losses']
		
		if total_matches > 0:
			var win_rate = float(stats['wins']) / total_matches
			# Use a weighted score to combine win rate and total matches
			var score = win_rate * total_matches * log(total_matches + 1)
			print(character + " "+ str(score))
			character_scores[character] = score
	
	# Sort characters by score in descending order, then by number of wins
	var sorted_characters = character_scores.keys()
	sorted_characters.sort_custom(func(a, b):
		if character_scores[b] != character_scores[a]:
			return character_scores[b] < character_scores[a]
		else:
			return character_stats[b]['wins'] > character_stats[a]['wins']  # In case of a tie, sort by number of wins
	
	)
	
	# Return the top N characters
	return sorted_characters.slice(0, top_n)

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	if pid != -1 and not server_running:
		if port and port != "":
			#print('port: '+port)
			if main_status.get_http_client_status() == 0:
				main_status.request("http://127.0.0.1:"+str(port)+"/status")
				await main_status.request_completed
		
	if search_pid != -1 and not misc_server_running:
		if misc_port and misc_port != "":
			#print('misc port: ' + misc_port)
			if misc_status.get_http_client_status() == 0:
				misc_status.request("http://127.0.0.1:"+str(misc_port)+"/status")	
				await misc_status.request_completed
		
	# If server is running, initialize methods
	if server_running and not isDetectionCache:
		var cache_url = "http://127.0.0.1:"+str(port)+"/init_cache"
		if http_request.get_http_client_status() == 0:
			http_request.request(cache_url)
			await http_request.request_completed
			# When cache done, set number of cv
			var url = "http://127.0.0.1:"+str(GlobalVars.port)+"/set_num_threads?num_threads="+str(SettingManager.CVWorker)
			http_request.request(url)
			await http_request.request_completed
		
	if misc_server_running and not isInitRecommender:
		if misc_http_request.get_http_client_status() == 0:
			misc_http_request.request("http://127.0.0.1:"+str(misc_port)+"/init_recommender")
			await misc_http_request.request_completed
		

func _status_check(result, response_code, headers, body):
	if response_code == 200:
		print('server connected')
		status_connected_num += 1
		loading_status = 'server connected: ('+str(status_connected_num)+'/2)'
		server_running = true
		
func _misc_status_check(result, response_code, headers, body):
	if response_code == 200:
		print('misc server connected')
		status_connected_num += 1		
		loading_status = 'misc server connected: ('+str(status_connected_num)+'/2)'
		misc_server_running = true
	
func _exit_tree():
	#stop future requests
	request_done = false
	#cancel http requests
	if misc_http_request and misc_http_request.get_http_client_status() != 0:
		misc_http_request.cancel_request()
		
	if http_request and http_request.get_http_client_status() != 0:
		http_request.cancel_request()
	"""
	#send shutdown request
	if misc_http_request:
		print('Shutting down servers')
		misc_http_request.request("http://127.0.0.1:"+str(misc_port)+"/shutdown")
		await misc_http_request.request_completed
	
	if http_request:
		var url = "http://127.0.0.1:"+str(port)+"/shutdown"
		http_request.request(url)
		await http_request.request_completed
	"""
	# force close servers
	if pid and pid != -1:
		OS.kill(pid)
	if search_pid and search_pid != -1:
		OS.kill(search_pid)
	
	
func _on_search_request_completed(result, response_code, headers, body):
	print("Search Request Completed!")
	if response_code == 200:
		isInitRecommender = true
		var json = JSON.new()
		json.parse(body.get_string_from_utf8())
		var response = json.get_data()
		user_data = response
		print(response)
	else:
		var json = JSON.new()
		json.parse(body.get_string_from_utf8())
		var response = json.get_data()
		user_data = ""
		print(response)
		print("Request failed with response code %d" % response_code)
		
# Initialize request completed
func _on_request_completed(result, response_code, headers, body):
	print("Char Detection Completed!")
	if response_code == 200:
		request_done = true
		isDetectionCache = true
		var json = JSON.new()
		json.parse(body.get_string_from_utf8())
		var response = json.get_data()		
		print(response)
	else:
		var json = JSON.new()
		json.parse(body.get_string_from_utf8())
		var response = json.get_data()
		print(response)
		print("Request failed with response code %d" % response_code)
	
# Function for running search server
func _run_search_server(python_exe_path, python_script_path):
	var output = []
	print('running python script')
	loading_status = 'starting server...'
	
	#pid = OS.execute(python_exe_path, [python_script_path], [], false)
	pid = OS.create_process(python_exe_path, [python_script_path])
	# create process until no errors
	while pid == -1:
		if pid == -1:
			pid = OS.create_process(python_exe_path, [python_script_path])
			print("Failed to start Python server. Error code:", pid)
		else:
			print("Python server started successfully.")
			loading_status = 'Server started successfully...'			
	
	# When python server gets executed keep updating port
	while not misc_server_running:
		var misc_port_file = FileAccess.open("search_server_port.txt", FileAccess.READ)
		misc_port = misc_port_file.get_as_text().strip_edges(true,true)
		
# Function for running detection server
func _run_server(python_exe_path, python_script_path):
	var output = []
	print('running search python script')
	loading_status = 'starting misc server...'
	
	#search_pid = OS.execute(python_exe_path, [python_script_path], output, false)
	search_pid = OS.create_process(python_exe_path, [python_script_path])	
	while search_pid == -1:
		if search_pid == -1:
			search_pid = OS.create_process(python_exe_path, [python_script_path])
			print("Failed to start Python server. Error code:", search_pid)
		else:
			print("Python server started successfully.")
			loading_status = 'Misc server started successfully...'
	
	# When python server gets executed keep updating port
	while not server_running:
		var port_file = FileAccess.open("server_port.txt", FileAccess.READ)
		port = port_file.get_as_text().strip_edges(true,true)
