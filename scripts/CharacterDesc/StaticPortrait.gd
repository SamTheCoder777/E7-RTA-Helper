extends Node
signal SetPortrait(img_path)
signal SetSouls(soul_count)

# Override the _make_custom_tooltip method
func _make_custom_tooltip(for_text: String) -> Control:
	# Create a Label for the tooltip text
	var tooltip_label = Label.new()
	tooltip_label.text = for_text
	tooltip_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	tooltip_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER # Align the text to the center
	tooltip_label.custom_minimum_size = Vector2(250,20)
	
	# Create a PanelContainer to hold the label
	var tooltip_panel = PanelContainer.new()
	tooltip_panel.add_child(tooltip_label)
	
	# Create and customize a StyleBoxFlat for the background
	var stylebox = StyleBoxFlat.new()
	stylebox.bg_color = Color(0, 0, 0, 1)  # Set background to opaque black
	stylebox.set_corner_radius_all(8)
	
	# Apply the stylebox to the panel
	tooltip_panel.add_theme_stylebox_override("panel", stylebox)
	
	# Return the fully customized tooltip
	return tooltip_panel

# Called when the node enters the scene tree for the first time.
func _ready():
	pass


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass


func _on_set_portrait(img_path):
	if img_path:
		self.texture = img_path


func _on_set_souls(soul_count):
	
	var soul_portrait1 = $Container/HBoxContainer/Soul1
	var soul_portrait2 = $Container/HBoxContainer/Soul2

	var soul_portraits = [soul_portrait1, soul_portrait2]

	for soul_portrait in soul_portraits:
		soul_portrait.visible = false
		
	if soul_count == 1:
		soul_portraits[0].visible = true
	elif soul_count == 2:
		soul_portraits[0].visible = true		
		soul_portraits[1].visible = true
