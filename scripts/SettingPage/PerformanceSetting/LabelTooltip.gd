extends Node

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
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass
