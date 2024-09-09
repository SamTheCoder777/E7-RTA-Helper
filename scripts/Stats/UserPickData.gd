extends Node

@onready var portrait1 = $VBoxContainer/HBoxContainer/VBoxContainer/HBoxContainer/PortraitDisplay
@onready var portrait2 = $VBoxContainer/HBoxContainer/VBoxContainer/HBoxContainer2/PortraitDisplay
@onready var portrait3 = $VBoxContainer/HBoxContainer/VBoxContainer/HBoxContainer3/PortraitDisplay
@onready var portrait4 = $VBoxContainer/HBoxContainer/VBoxContainer/HBoxContainer4/PortraitDisplay
@onready var portrait5 = $VBoxContainer/HBoxContainer/VBoxContainer/HBoxContainer5/PortraitDisplay
@onready var portrait6 = $VBoxContainer/HBoxContainer/VBoxContainer2/HBoxContainer/PortraitDisplay
@onready var portrait7 = $VBoxContainer/HBoxContainer/VBoxContainer2/HBoxContainer2/PortraitDisplay
@onready var portrait8 = $VBoxContainer/HBoxContainer/VBoxContainer2/HBoxContainer3/PortraitDisplay
@onready var portrait9 = $VBoxContainer/HBoxContainer/VBoxContainer2/HBoxContainer4/PortraitDisplay
@onready var portrait10 = $VBoxContainer/HBoxContainer/VBoxContainer2/HBoxContainer5/PortraitDisplay
@onready var portraits = [portrait1, portrait2, portrait3, portrait4, portrait5, portrait6, portrait7, portrait8, portrait9, portrait10]

@onready var label1 = $VBoxContainer/HBoxContainer/VBoxContainer/HBoxContainer/Label
@onready var label2 = $VBoxContainer/HBoxContainer/VBoxContainer/HBoxContainer2/Label
@onready var label3 = $VBoxContainer/HBoxContainer/VBoxContainer/HBoxContainer3/Label
@onready var label4 = $VBoxContainer/HBoxContainer/VBoxContainer/HBoxContainer4/Label
@onready var label5 = $VBoxContainer/HBoxContainer/VBoxContainer/HBoxContainer5/Label
@onready var label6 = $VBoxContainer/HBoxContainer/VBoxContainer2/HBoxContainer/Label
@onready var label7 = $VBoxContainer/HBoxContainer/VBoxContainer2/HBoxContainer2/Label
@onready var label8 = $VBoxContainer/HBoxContainer/VBoxContainer2/HBoxContainer3/Label
@onready var label9 = $VBoxContainer/HBoxContainer/VBoxContainer2/HBoxContainer4/Label
@onready var label10 = $VBoxContainer/HBoxContainer/VBoxContainer2/HBoxContainer5/Label
@onready var labels = [label1, label2, label3, label4, label5, label6, label7, label8, label9, label10]

@onready var counter_portrait1 = $VBoxContainer/VBoxContainer2/Counters/PortraitDisplay
@onready var counter_portrait2 = $VBoxContainer/VBoxContainer2/Counters/PortraitDisplay2
@onready var counter_portrait3 = $VBoxContainer/VBoxContainer2/Counters/PortraitDisplay3
@onready var counter_portraits = [counter_portrait1, counter_portrait2, counter_portrait3]

@onready var synergy_portrait1 = $VBoxContainer/VBoxContainer2/Synergies/PortraitDisplay
@onready var synergy_portrait2 = $VBoxContainer/VBoxContainer2/Synergies/PortraitDisplay2
@onready var synergy_portrait3 = $VBoxContainer/VBoxContainer2/Synergies/PortraitDisplay3
@onready var synergy_portraits = [synergy_portrait1, synergy_portrait2, synergy_portrait3]

@onready var char_match_stats = GlobalVars.hero_match_data
@onready var hero_data = GlobalVars.hero_data

signal show_recommendation(recommendation: Array)
signal show_counters(character: String)
signal show_synergies(character: String)

func on_show_recommendation(recommendation: Array):
	# First reset all portraits and labels
	for portrait in portraits:
		portrait.texture = load('res://UI/MatchSelect/unknown_hero.png')
	for label in labels:
		label.text = "WR NaN%"
	print('rec len: ' + str(len(recommendation)))
	# Now show recommendations
	var i = 0
	for rec in recommendation:
		# If rec is more than what we can handle, break
		if i >= len(portraits):
					break
		for chars in hero_data:
			if chars['Hero'] == rec:
				var image = Image.load_from_file('dataset/'+str(rec)+'/c.png')
				var texture = ImageTexture.create_from_image(image)
				texture.resource_name = 'dataset/'+str(rec)+'/c.png'
				portraits[i].texture = texture
				#portraits[i].texture = load('dataset/'+str(rec)+'/c.png')
				if chars['Win Rate']:
					labels[i].text = "WR " + str(chars['Win Rate'])+"%"
				i += 1
	
func on_show_counters(character: String):
	#First set all portraits as unknown hero
	for portrait in counter_portraits:
		portrait.texture = load("res://UI/MatchSelect/unknown_hero.png")
	
	for chars in hero_data:
		if chars['Hero'] == character:
			#var counters = chars['Counters'].replace('\'','').replace('[', '').replace(']','').replace(' ','').split(',')
			var regex = RegEx.new()
			regex.compile('c\\d{4}')
			var counters = []
			for result in regex.search_all(chars['Counters']):
				counters.append(result.get_string())
			var i = 0
			for counter in counters:
				var image = Image.load_from_file('dataset/'+str(counter)+'/c.png')
				var texture = ImageTexture.create_from_image(image)
				texture.resource_name = 'dataset/'+str(counter)+'/c.png'				
				counter_portraits[i].texture = texture
				#counter_portraits[i].texture = load('dataset/'+str(counter)+'/c.png')
				i+=1
	
func on_show_synergies(character: String):
	#First set all portraits as unknown hero
	for portrait in synergy_portraits:
		portrait.texture = load("res://UI/MatchSelect/unknown_hero.png")
	
	for chars in hero_data:
		if chars['Hero'] == character:
			var regex = RegEx.new()
			regex.compile('c\\d{4}')
			var synergies = []
			for result in regex.search_all(chars['Synergies']):
				synergies.append(result.get_string())
			var i = 0
			for synergy in synergies:
				#synergy_portraits[i].texture = load('dataset/'+str(synergy)+'/c.png')
				var image = Image.load_from_file('dataset/'+str(synergy)+'/c.png')
				var texture = ImageTexture.create_from_image(image)
				texture.resource_name = 'dataset/'+str(synergy)+'/c.png'								
				synergy_portraits[i].texture = texture
				i+=1
	
# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass
