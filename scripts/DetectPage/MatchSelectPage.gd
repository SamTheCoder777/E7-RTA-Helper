extends Node

var http_request: HTTPRequest
var misc_http_request: HTTPRequest
var thread: Thread

@onready
var EnemyPortraits = $CanvasLayer/MatchSelect/Container/ColorRect/MarginContainer2/RealTimeEnemyDetection/EnemyPortraits

@onready 
var UserPortraits = $CanvasLayer/MatchSelect/Container/ColorRect/MarginContainer2/RealTimeEnemyDetection/UserPortraits

@onready
var EnemyPickStats = $CanvasLayer/EnemyPickStats

var DetectOutput = {}
var port
var misc_port

# Check if you can make a request
var request_done = GlobalVars.request_done

# Check if you can ask for a recommendation
var can_ask_rec = true

# Check who is first pick
var is_user_first_pick = true

# Check if paused
var paused = false

# Crop values
var CropTopValue = 1
var CropBotValue = 1
var CropRightValue = 1
var CropLeftValue = 1
var CropCenterValue = 0
var title = ""

# User Data
var user_data = {}

# Check if team changed
var old_user_team = []
var old_enemy_team = []

func _ready():
	"""
	GlobalVars.user_data = { "character_stats": { "c1117": { "losses": 1, "wins": 0 }, "c1134": { "losses": 0, "wins": 1 }, "c1144": { "losses": 0, "wins": 1 }, "c1151": { "losses": 1, "wins": 2 }, "c1156": { "losses": 0, "wins": 4 }, "c1159": { "losses": 1, "wins": 2 }, "c2008": { "losses": 1, "wins": 1 }, "c2016": { "losses": 1, "wins": 5 }, "c2039": { "losses": 1, "wins": 2 }, "c2042": { "losses": 2, "wins": 6 }, "c2066": { "losses": 0, "wins": 2 }, "c2090": { "losses": 3, "wins": 5 }, "c2109": { "losses": 1, "wins": 2 }, "c2111": { "losses": 0, "wins": 1 }, "c5082": { "losses": 1, "wins": 1 }, "c6037": { "losses": 1, "wins": 0 }, "c6062": { "losses": 1, "wins": 0 } }, "hero_data": [{ "code": "c1159", "losses": "184L", "name": "Laia", "win_rate": "(71.29%)", "wins": "457W" }, { "code": "c2090", "losses": "169L", "name": "Death Dealer Ray", "win_rate": "(71.88%)", "wins": "432W" }, { "code": "c2008", "losses": "157L", "name": "Crimson Armin", "win_rate": "(71.25%)", "wins": "389W" }, { "code": "c2042", "losses": "154L", "name": "Ambitious Tywin", "win_rate": "(71.32%)", "wins": "383W" }, { "code": "c2016", "losses": "118L", "name": "Abyssal Yufine", "win_rate": "(74.68%)", "wins": "348W" }], "player_has_data": true }	
	var test = { "character_stats": { "c1117": { "losses": 1, "wins": 0 }, "c1134": { "losses": 0, "wins": 1 }, "c1144": { "losses": 0, "wins": 1 }, "c1151": { "losses": 1, "wins": 2 }, "c1156": { "losses": 0, "wins": 4 }, "c1159": { "losses": 1, "wins": 2 }, "c2008": { "losses": 1, "wins": 1 }, "c2016": { "losses": 1, "wins": 5 }, "c2039": { "losses": 1, "wins": 2 }, "c2042": { "losses": 2, "wins": 6 }, "c2066": { "losses": 0, "wins": 2 }, "c2090": { "losses": 3, "wins": 5 }, "c2109": { "losses": 1, "wins": 2 }, "c2111": { "losses": 0, "wins": 1 }, "c5082": { "losses": 1, "wins": 1 }, "c6037": { "losses": 1, "wins": 0 }, "c6062": { "losses": 1, "wins": 0 } }, "hero_data": [{ "code": "c1159", "losses": "184L", "name": "Laia", "win_rate": "(71.29%)", "wins": "457W" }, { "code": "c2090", "losses": "169L", "name": "Death Dealer Ray", "win_rate": "(71.88%)", "wins": "432W" }, { "code": "c2008", "losses": "157L", "name": "Crimson Armin", "win_rate": "(71.25%)", "wins": "389W" }, { "code": "c2042", "losses": "154L", "name": "Ambitious Tywin", "win_rate": "(71.32%)", "wins": "383W" }, { "code": "c2016", "losses": "118L", "name": "Abyssal Yufine", "win_rate": "(74.68%)", "wins": "348W" }], "player_has_data": true }
	var test_arr = test['character_stats']
	$CanvasLayer/UserPickData.emit_signal('show_counters', 'c6062')
	$CanvasLayer/UserPickData.emit_signal('show_synergies', 'c0002')
	$CanvasLayer/UserPickData.emit_signal('show_recommendation', ['c1117', 'c1134', 'c2066', 'c0002', 'c1001', 'c1004'])
	
	$CanvasLayer/EnemyPickStats.emit_signal('char_picked','c1117')
	$CanvasLayer/UserStats.emit_signal('_update_most_picks', GlobalVars.recommend_top_characters(test_arr))
	$CanvasLayer/UserStats.emit_signal('_update_recent_picks')
	"""
	
	# make http request for character detection
	http_request = HTTPRequest.new()
	add_child(http_request)
	http_request.request_completed.connect(self._on_detection_completed)

	# make http request for misc server
	misc_http_request = HTTPRequest.new()
	add_child(misc_http_request)
	misc_http_request.request_completed.connect(self._on_misc_server_completed)

	#print(await GlobalVars.get_user_data('khhm'))
	
	SettingManager.update_data()
	CropTopValue = str(SettingManager.CropTopValue)
	CropBotValue = str(SettingManager.CropBotValue)
	CropRightValue = str(SettingManager.CropRightValue)
	CropLeftValue = str(SettingManager.CropLeftValue)
	CropCenterValue = str(SettingManager.CropCenterValue)
	title = SettingManager.WindowTitle
	user_data = SettingManager.UserData

	# Display user stats
	if user_data.size() != 0:
		GlobalVars.user_data = user_data
		$CanvasLayer/UserStats.emit_signal('_update_most_picks')	
		$CanvasLayer/UserStats.emit_signal('_update_recent_picks',GlobalVars.recommend_top_characters(user_data['character_stats']))
		
# Check for key press
func _input(event):
	# Escape	
	if event.is_action_pressed("ui_cancel"):
		paused = !paused
		
		if paused: # Pause
			# Display pause screen
			$CanvasLayer/PauseScreen.visible = true
			
			# Cancel all requests and stop them
			if http_request.get_http_client_status() != 0:
				http_request.cancel_request()
			GlobalVars.request_done = false
			
			if misc_http_request.get_http_client_status() != 0:
				misc_http_request.cancel_request()
			can_ask_rec = false
			print('status: paused')
			
		else: # Resume
			# Stop displaying pause screen
			$CanvasLayer/PauseScreen.visible = false
			
			# Resume all requests
			GlobalVars.request_done = true
			can_ask_rec = true
			print('status: resumed')
			
func _process(_delta):
	# Update request_done
	request_done = GlobalVars.request_done

	# Request char detection
	if request_done:
		# Reset DetectOutput
		DetectOutput = {}
		var url = "http://127.0.0.1:"+str(GlobalVars.port)+"/detect_enemy?title="+title.uri_encode()+"&crops="+CropTopValue+","+CropBotValue+","+CropRightValue+","+CropLeftValue+","+CropCenterValue
		if http_request.get_http_client_status() == 0:
			http_request.request(url)
			request_done = false # Stop request call until the detection finishes

func _on_misc_server_completed(result, response_code, headers, body):
	print("Request recommendations")
	if response_code == 200:
		can_ask_rec = true
		var json = JSON.new()
		json.parse(body.get_string_from_utf8())
		var Recommendation = json.get_data()
		print("Rec: " + str(Recommendation))
		print("Rec: " + str(Recommendation['top_10_heroes']))
		print("Rec: " + str(Recommendation['win_prediction']))		
		
		$CanvasLayer/UserPickData.emit_signal('show_recommendation', Recommendation['top_10_heroes'])
		
		# Set Win Prediction
		$CanvasLayer/MatchSelect/Container/ColorRect/WinPredictionBar.value = float(Recommendation['win_prediction'])*100
	else:
		can_ask_rec = true	
		print('rec error: '+ body.get_string_from_utf8())	
		# If failed, then show no rec
		$CanvasLayer/UserPickData.emit_signal('show_recommendation', [])
		# Set Win Prediction to 50%
		$CanvasLayer/MatchSelect/Container/ColorRect/WinPredictionBar.value = 50.0	
var index = 0
func _on_detection_completed(result, response_code, headers, body):
	print("Char Detection Completed!")
	if response_code == 200:
		request_done = true # Can do request call again
		var json = JSON.new()
		json.parse(body.get_string_from_utf8())
		DetectOutput = json.get_data()
		
		var user_team = ""
		index+=1
		if len(DetectOutput['user_team'])>0:
			for i in range(DetectOutput['user_team'].size()):
				user_team += str(DetectOutput['user_team'][i])
				if i < DetectOutput['user_team'].size() -1:
					user_team += ","
				
				
			UserPortraits.set_portraits(DetectOutput['user_team'])
			# Now Show Synergies to last user pick
			$CanvasLayer/UserPickData.emit_signal('show_synergies', DetectOutput['user_team'].back())
		else:
			print('eh?')
			UserPortraits.set_portraits([])
			$CanvasLayer/UserPickData.emit_signal('show_synergies', '')
		
		var enemy_team = ""
		# Now Set the Portraits
		if len(DetectOutput['enemy_team'])>0:
			for i in range(DetectOutput['enemy_team'].size()):
				enemy_team += str(DetectOutput['enemy_team'][i])
				if i < DetectOutput['enemy_team'].size() -1:
					enemy_team += ","
			EnemyPortraits.set_portraits(DetectOutput['enemy_team'])
			# Now Show Counters to last enemy pick
			$CanvasLayer/UserPickData.emit_signal('show_counters', DetectOutput['enemy_team'].back())
			
			# Show char picked
			EnemyPickStats.emit_signal('char_picked',DetectOutput['enemy_team'].back())
		
		else:
			EnemyPortraits.set_portraits([])			
			$CanvasLayer/UserPickData.emit_signal('show_counters', '')
			EnemyPickStats.emit_signal('char_picked','')			
		
		var response = json.get_data()		
		print("Detection Success")
		
		# Request recommendations
		if can_ask_rec and (DetectOutput['user_team'] != old_user_team or DetectOutput['enemy_team'] != old_enemy_team):
				old_user_team = DetectOutput['user_team']
				old_enemy_team = DetectOutput['enemy_team']
				can_ask_rec = false
				var first_pick_team = "My Team"if is_user_first_pick else "Enemy Team"
				var url = "http://127.0.0.1:"+str(GlobalVars.misc_port)+"/recommend"+"?user_picks="+user_team+"&enemy_picks="+enemy_team+"&first_pick_team="+first_pick_team.uri_encode()
				print('url: '+url)
				misc_http_request.request(url)
				
	else:
		request_done = true # Try again
		can_ask_rec = true
		old_user_team = []
		old_enemy_team = []
		
		# Delete all portraits
		UserPortraits.set_portraits([])
		$CanvasLayer/UserPickData.emit_signal('show_synergies', '')
		EnemyPickStats.emit_signal('char_picked','')
		EnemyPortraits.set_portraits([])
		$CanvasLayer/UserPickData.emit_signal('show_counters', '')						
		$CanvasLayer/UserPickData.emit_signal('show_recommendation', [])		
		$CanvasLayer/MatchSelect/Container/ColorRect/WinPredictionBar.value = 50.0			

		
		var json = JSON.new()
		json.parse(body.get_string_from_utf8())
		var response = json.get_data()
		print(response)
		DetectOutput = {}
		print("Request failed with response code %d" % response_code)

func _on_back_button_pressed():
	# Move back to front page and remove this scene
	get_tree().change_scene_to_file('res://scenes/FrontPage/FrontPage.tscn')
	self.queue_free()

# First pick selector
func _on_first_pick_selector_selected(index):
	is_user_first_pick = index == 1
	# Cancel rec request
	if misc_http_request.get_http_client_status() != 0:
		misc_http_request.cancel_request()
	# Force resubmit rec
	can_ask_rec = true
	old_user_team = []
	old_enemy_team = []
	
