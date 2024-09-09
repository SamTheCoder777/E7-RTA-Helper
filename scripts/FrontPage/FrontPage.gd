extends Node

@onready var MatchDetect = preload('res://scenes/DetectPage/MatchSelectPage.tscn').instantiate()

signal setup_complete
# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	if GlobalVars.isDetectionCache and GlobalVars.isInitRecommender:
		emit_signal('setup_complete')


func _on_start_button_pressed():
	if GlobalVars.isDetectionCache and GlobalVars.isInitRecommender:
		get_tree().root.add_child(MatchDetect)
	else:
		$CanvasLayer/LoadingScreen.visible = true
		await setup_complete
		$CanvasLayer/LoadingScreen.visible = false
		get_tree().root.add_child(MatchDetect)


func _on_settings_button_pressed():
	if GlobalVars.isDetectionCache and GlobalVars.isInitRecommender:	
		get_tree().root.add_child(load('res://scenes/SettingPage/SettingPage.tscn').instantiate())
	else:
		$CanvasLayer/LoadingScreen.visible = true
		await setup_complete
		$CanvasLayer/LoadingScreen.visible = false
		get_tree().root.add_child(load('res://scenes/SettingPage/SettingPage.tscn').instantiate())		
