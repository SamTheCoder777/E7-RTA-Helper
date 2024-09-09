extends Node

var option_request

var CVWorker = -1
@onready var CVWorkerInput = $ColorRect/VBoxContainer/HBoxContainer/SpinBox
@onready var CVSetLabel = $ColorRect/VBoxContainer/OpenCVSetLabel

# Called when the node enters the scene tree for the first time.
func _ready():
	CVWorker = SettingManager.CVWorker
	CVWorkerInput.value = CVWorker
	
	# Http request for option setting
	option_request = HTTPRequest.new()
	add_child(option_request)
	option_request.request_completed.connect(self._on_option_request)

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass


func _on_close_requested():
	queue_free()

func _on_button_pressed():
	CVWorker = CVWorkerInput.value
	SettingManager.config.set_value("Save", 'CVWorker', CVWorker)
	SettingManager.save_config()
	
	var url = "http://127.0.0.1:"+str(GlobalVars.port)+"/set_num_threads?num_threads="+str(CVWorker)
	option_request.request(url)
	
	await option_request.request_completed
	CVSetLabel.visible = true

func _on_option_request(result, response_code, headers, body):
	print(body.get_string_from_utf8())
