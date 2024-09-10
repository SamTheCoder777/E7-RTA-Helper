extends Node

var misc_http_request
var update_checked = false

# Called when the node enters the scene tree for the first time.
func _ready():
	# make http request for misc server
	misc_http_request = HTTPRequest.new()
	add_child(misc_http_request)
	misc_http_request.request_completed.connect(self._on_misc_server_completed)


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass


func _on_set_d_screen_size_pressed():
	SettingManager.update_data() # update settings
	get_tree().root.add_child(load('res://scenes/SettingPage/SetDetectionScreenSize/DScreenSizeSet.tscn').instantiate())

func _on_set_user_data_pressed():
	SettingManager.update_data() # update settings
	get_tree().root.add_child(load('res://scenes/SettingPage/SetUser/SetUser.tscn').instantiate())

func _on_performance_setting_pressed():
	SettingManager.update_data() # update settings
	get_tree().root.add_child(load('res://scenes/SettingPage/PerformanceSetting/PerformanceSetting.tscn').instantiate())
	
	
func _on_close_requested():
	queue_free()


func _on_credits_pressed():
	get_tree().root.add_child(load('res://scenes/SettingPage/CreditPage/CreditPage.tscn').instantiate())	


func _on_check_updates_pressed():
	if misc_http_request.get_http_client_status() == 0 and !update_checked:
		update_checked = true
		$ColorRect/ScrollContainer/VBoxContainer/UpdatesStatus.visible = true
		$ColorRect/ScrollContainer/VBoxContainer/UpdatesStatus.text = "Checking for updates..."
		
		misc_http_request.request("http://127.0.0.1:"+str(GlobalVars.misc_port)+"/check_update")
	
func _on_misc_server_completed(result, response_code, headers, body):
	if response_code == 200:
		update_checked = true
		var json = JSON.new()
		json.parse(body.get_string_from_utf8())
		var response = json.get_data()
		
		var text = ''
		if response['data_updated'] == true:
			$ColorRect/ScrollContainer/VBoxContainer/UpdatesStatus.visible = true
			if text != '':
				text+="\n"
			text += 'Data/Recommender sucessfully updated'
		if response['program_updated'] == true:
			$ColorRect/ScrollContainer/VBoxContainer/UpdatesStatus.visible = true
			if text != '':
				text+="\n"
			text += 'Program update detected. Please download it on github'
		if !response['data_updated'] and !response['program_updated']:
			$ColorRect/ScrollContainer/VBoxContainer/UpdatesStatus.visible = true
			text += 'You are up to date!'
			
		$ColorRect/ScrollContainer/VBoxContainer/UpdatesStatus.text = text
		
	else:
		$ColorRect/ScrollContainer/VBoxContainer/UpdatesStatus.visible = true
		$ColorRect/ScrollContainer/VBoxContainer/UpdatesStatus.text = "Failed to check for updates... Please check github..."
		
		
		
