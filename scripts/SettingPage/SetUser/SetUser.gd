extends Node

var server = ""
var username = ""
var server_error_string = "[center][color=red]Please Select Your Server[/color][center]"
var username_error_string = "[center][color=red]Username cannot be empty![/color][center]"
var successful_string = "[center][color=green]Searching for your data...[/color][center]"
var task_done_string = "[center][color=green]Done![/color][center]"
var reset_done_string = "[center][color=green]User Data Reset![/color][center]"
var error_string = "[center][color=red]Something unexpected happened![/color][center]"

var user_data = {}

# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass

func _on_close_requested():
	queue_free()


func _on_button_pressed():
	if username == "":
		$VBoxContainer/ErrorMessageLabel.visible = true
		$VBoxContainer/ErrorMessageLabel.text = username_error_string
	elif server == "":
		$VBoxContainer/ErrorMessageLabel.visible = true
		$VBoxContainer/ErrorMessageLabel.text = server_error_string
	else:
		$VBoxContainer/ErrorMessageLabel.visible = true
		$VBoxContainer/ErrorMessageLabel.text = successful_string
		
		user_data = await GlobalVars.get_user_data(username, server)
		if str(user_data) == "":
			$VBoxContainer/ErrorMessageLabel.text = error_string
		else:
			SettingManager.config.set_value("Save", 'UserData', user_data)
			SettingManager.save_config()
			$VBoxContainer/ErrorMessageLabel.text = task_done_string			


func _on_option_button_item_selected(index):
	server = $VBoxContainer/MarginContainer/HBoxContainer/OptionButton.get_item_text(index)


func _on_line_edit_text_changed(new_text):
	username = new_text

func _on_reset_button_pressed():
	SettingManager.config.set_value("Save", 'UserData', {})
	SettingManager.save_config()
	$VBoxContainer/ErrorMessageLabel.visible = true
	$VBoxContainer/ErrorMessageLabel.text = reset_done_string
