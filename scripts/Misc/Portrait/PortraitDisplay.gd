extends TextureRect
class_name PortraitDisplay
var regex

var char_desc = preload('res://scenes/CharacterDesc/CharacterDesc.tscn').instantiate()
var current_char = "Unknown"
var current_name = "Unknown"
# Called when the node enters the scene tree for the first time.
func _ready():
	regex = RegEx.new()
	regex.compile('c\\d{4}')

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	var character_path = self.texture.resource_name
	var character = regex.search(character_path)
	if character_path and character and character.get_string() != "":
		if current_char != character.get_string():
			for entry in GlobalVars.hero_names:
				if entry['code'] == character.get_string():
					self.tooltip_text = entry['name']
					current_char = character.get_string()
					current_name = entry['name']
	else:
		self.tooltip_text = "Unknown"
		current_char = "Unknown"
		current_name = "Unknown"


func _on_button_pressed():
	if current_name != "Unknown":
		char_desc.set_content(current_char)		
		get_tree().root.add_child(char_desc)
		char_desc = preload('res://scenes/CharacterDesc/CharacterDesc.tscn').instantiate()
	
