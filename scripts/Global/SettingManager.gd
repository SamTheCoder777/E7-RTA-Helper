extends Node

var config = ConfigFile.new()

var err = config.load("res://config.cfg")

var CropTopValue = "1"
var CropBotValue = "1"
var CropRightValue = "1"
var CropLeftValue = "1"
var CropCenterValue = "0"

var WindowTitle = ""

var UserData = {}

var CVWorker = -1

# Called when the node enters the scene tree for the first time.
func _ready():
	if err != OK:
		return
	for section in config.get_sections():
		CropTopValue = config.get_value(section, 'CropTopValue', "1")
		CropBotValue = config.get_value(section, 'CropBotValue', "1")
		CropRightValue = config.get_value(section, 'CropRightValue', "1")
		CropLeftValue = config.get_value(section, 'CropLeftValue', "1")
		CropCenterValue = config.get_value(section, 'CropCenterValue', "0")
		WindowTitle = config.get_value(section, 'WindowTitle', "")
		UserData = config.get_value(section, 'UserData', {})
		CVWorker = config.get_value(section, 'CVWorker', -1)
		
func update_data():
	var err = config.load("res://config.cfg")
	if err != OK:
		return
	for section in config.get_sections():
		CropTopValue = config.get_value(section, 'CropTopValue', "1")
		CropBotValue = config.get_value(section, 'CropBotValue', "1")
		CropRightValue = config.get_value(section, 'CropRightValue', "1")
		CropLeftValue = config.get_value(section, 'CropLeftValue', "1")
		CropCenterValue = config.get_value(section, 'CropCenterValue', "0")
		WindowTitle = config.get_value(section, 'WindowTitle', "")
		UserData = config.get_value(section, 'UserData', {})
		CVWorker = config.get_value(section, 'CVWorker', -1)
		
		print(WindowTitle)
func save_config():
	config.save("res://config.cfg")
	
func _exit_tree():
	save_config()

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass
