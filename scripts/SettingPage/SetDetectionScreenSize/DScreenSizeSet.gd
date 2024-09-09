extends Node

var http_request
var sc_request
var windows_request

var CropTopValue
var CropBotValue
var CropRightValue
var CropLeftValue
var CropCenterValue

var windows = []
var title

@onready var window_selector = $ColorRect/MarginContainer/ScrollContainer/VBoxContainer/WindowSelector
@onready var message_label = $ColorRect/MarginContainer/ScrollContainer/VBoxContainer/MessageLabel

# Called when the node enters the scene tree for the first time.
func _ready():
	http_request = HTTPRequest.new()
	add_child(http_request)
	http_request.request_completed.connect(self._on_request_completed)
	
	sc_request = HTTPRequest.new()
	add_child(sc_request)
	sc_request.request_completed.connect(self._on_sc_request_completed)
	
	windows_request = HTTPRequest.new()
	add_child(windows_request)
	windows_request.request_completed.connect(self._on_wr_request_completed)
	$ColorRect/MarginContainer/ScrollContainer/VBoxContainer/HBoxContainer/VBoxContainer/HBoxContainer/CropTopValue.value = float(SettingManager.CropTopValue)
	$ColorRect/MarginContainer/ScrollContainer/VBoxContainer/HBoxContainer/VBoxContainer/HBoxContainer2/CropBotValue.value = float(SettingManager.CropBotValue)
	$ColorRect/MarginContainer/ScrollContainer/VBoxContainer/HBoxContainer/VBoxContainer2/HBoxContainer/CropRightValue.value = float(SettingManager.CropRightValue)
	$ColorRect/MarginContainer/ScrollContainer/VBoxContainer/HBoxContainer/VBoxContainer2/HBoxContainer2/CropLeftValue.value = float(SettingManager.CropLeftValue)
	$ColorRect/MarginContainer/ScrollContainer/VBoxContainer/HBoxContainer/VBoxContainer3/HBoxContainer/CropCenterValue.value = float(SettingManager.CropCenterValue)
	title = SettingManager.WindowTitle
	
	# request window titles
	if windows_request.get_http_client_status() == 0:
		windows_request.request("http://127.0.0.1:"+str(GlobalVars.port)+"/get_window_titles")
	else:
		windows_request.cancel_request()
		windows_request.request("http://127.0.0.1:"+str(GlobalVars.port)+"/get_window_titles")
		
# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass


func _on_close_requested():
	queue_free()


func _on_set_button_pressed():
	CropTopValue = str($ColorRect/MarginContainer/ScrollContainer/VBoxContainer/HBoxContainer/VBoxContainer/HBoxContainer/CropTopValue.value)
	CropBotValue = str($ColorRect/MarginContainer/ScrollContainer/VBoxContainer/HBoxContainer/VBoxContainer/HBoxContainer2/CropBotValue.value)
	CropRightValue = str($ColorRect/MarginContainer/ScrollContainer/VBoxContainer/HBoxContainer/VBoxContainer2/HBoxContainer/CropRightValue.value)
	CropLeftValue = str($ColorRect/MarginContainer/ScrollContainer/VBoxContainer/HBoxContainer/VBoxContainer2/HBoxContainer2/CropLeftValue.value)
	CropCenterValue = str($ColorRect/MarginContainer/ScrollContainer/VBoxContainer/HBoxContainer/VBoxContainer3/HBoxContainer/CropCenterValue.value)
	
	if http_request.get_http_client_status() == 0:
		http_request.request("http://127.0.0.1:"+str(GlobalVars.port)+"/crop_image?crops="+
		CropTopValue+","+CropBotValue+","+CropRightValue+","+CropLeftValue+","+CropCenterValue)
	else:
		http_request.cancel_request()
		http_request.request("http://127.0.0.1:"+str(GlobalVars.port)+"/crop_image?crops="+
		CropTopValue+","+CropBotValue+","+CropRightValue+","+CropLeftValue+","+CropCenterValue)
	
# Initialize request completed
func _on_request_completed(result, response_code, headers, body):
	if response_code == 200:
		message_label.text = ""
		var image = Image.new()
		image.load("temp_cropped.png")
		var t = ImageTexture.new()
		t.set_image(image)
		$ColorRect/MarginContainer/ScrollContainer/VBoxContainer/Preview.texture = t
		
		# save data
		SettingManager.config.set_value("Save", 'CropTopValue', CropTopValue)
		SettingManager.config.set_value("Save", 'CropBotValue', CropBotValue)
		SettingManager.config.set_value("Save", 'CropRightValue', CropRightValue)
		SettingManager.config.set_value("Save", 'CropLeftValue', CropLeftValue)
		SettingManager.config.set_value("Save", 'CropCenterValue', CropCenterValue)
		SettingManager.config.set_value("Save", 'WindowTitle', title)		
		
		SettingManager.save_config()

	else:
		var json = JSON.new()
		json.parse(body.get_string_from_utf8())
		var response = json.get_data()
		
		message_label.add_theme_color_override("font_color", Color.hex(0xff0000ff))
		message_label.text = "Request failed...\nPlease double check your window title and crop parameters"
		
		print(response)
		print("Request failed with response code %d" % response_code)

func _on_sc_request_completed(result, response_code, headers, body):
	if response_code == 200:
		message_label.text = ""
		var image = Image.new()
		image.load("temp.png")
		var t = ImageTexture.new()
		t.set_image(image)
		$ColorRect/MarginContainer/ScrollContainer/VBoxContainer/Preview.texture = t

	else:
		message_label.add_theme_color_override("font_color", Color.hex(0xff0000ff))
		message_label.text = "Request failed...\nPlease double check your window title"
		var json = JSON.new()
		json.parse(body.get_string_from_utf8())
		var response = json.get_data()
		print(response)
		print("Request failed with response code %d" % response_code)

func _on_wr_request_completed(result, response_code, headers, body):
	if response_code == 200:
		windows = JSON.parse_string(body.get_string_from_utf8().replace("'",'"'))
		#windows = body.get_string_from_utf8().split(",")
		
		for window in windows:
			window_selector.add_item(window)

	else:
		print(body.get_string_from_utf8())
		print("Request failed with response code %d" % response_code)
		
func _on_screen_shot_button_pressed():
	if window_selector.get_selected_id() == 0:
		message_label.add_theme_color_override("font_color", Color.hex(0xff0000ff))
		message_label.text = "Must select your window"
		return
	
	message_label.text = "" # Reset label
	
	title = window_selector.get_item_text(window_selector.get_selected_id())
	
	if sc_request.get_http_client_status() == 0:
		sc_request.request("http://127.0.0.1:"+str(GlobalVars.port)+"/capture_save?title="+title.uri_encode())
	else:
		sc_request.cancel_request()
		sc_request.request("http://127.0.0.1:"+str(GlobalVars.port)+"/capture_save?title="+title.uri_encode())


func _on_reset_button_pressed():
	# Reset value
	SettingManager.config.set_value("Save", 'CropTopValue', 1)
	SettingManager.config.set_value("Save", 'CropBotValue', 1)
	SettingManager.config.set_value("Save", 'CropRightValue', 1)
	SettingManager.config.set_value("Save", 'CropLeftValue', 1)
	SettingManager.config.set_value("Save", 'CropCenterValue', 0)
	SettingManager.config.set_value("Save", 'WindowTitle', "")
		
	SettingManager.save_config()
	SettingManager.update_data()
	
	#display values
	$ColorRect/MarginContainer/ScrollContainer/VBoxContainer/HBoxContainer/VBoxContainer/HBoxContainer/CropTopValue.value = float(SettingManager.CropTopValue)
	$ColorRect/MarginContainer/ScrollContainer/VBoxContainer/HBoxContainer/VBoxContainer/HBoxContainer2/CropBotValue.value = float(SettingManager.CropBotValue)
	$ColorRect/MarginContainer/ScrollContainer/VBoxContainer/HBoxContainer/VBoxContainer2/HBoxContainer/CropRightValue.value = float(SettingManager.CropRightValue)
	$ColorRect/MarginContainer/ScrollContainer/VBoxContainer/HBoxContainer/VBoxContainer2/HBoxContainer2/CropLeftValue.value = float(SettingManager.CropLeftValue)
	$ColorRect/MarginContainer/ScrollContainer/VBoxContainer/HBoxContainer/VBoxContainer3/HBoxContainer/CropCenterValue.value = float(SettingManager.CropCenterValue)

	window_selector.select(0)
