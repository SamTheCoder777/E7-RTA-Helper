extends Node

signal char_picked(character)

@onready var char_portrait = $PickedChar
@onready var char_stat = $PickedStat
@onready var epic7_char_stat = $E7Stat

@onready var char_match_stats = GlobalVars.hero_match_data
@onready var hero_data = GlobalVars.hero_data

@onready var rank_1_equip_portrait1 = $EquipmentSetsData/HBox/VBoxContainer2/HBoxContainer/EquipPortrait1
@onready var rank_1_equip_portrait2 = $EquipmentSetsData/HBox/VBoxContainer2/HBoxContainer/EquipPortrait2
@onready var rank_1_equip_portrait3 = $EquipmentSetsData/HBox/VBoxContainer2/HBoxContainer/EquipPortrait3
@onready var rank_1_equip_portraits = [rank_1_equip_portrait1,rank_1_equip_portrait2, rank_1_equip_portrait3]

@onready var rank_2_equip_portrait1 = $EquipmentSetsData/HBox/VBoxContainer2/HBoxContainer2/EquipPortrait1
@onready var rank_2_equip_portrait2 = $EquipmentSetsData/HBox/VBoxContainer2/HBoxContainer2/EquipPortrait2
@onready var rank_2_equip_portrait3 = $EquipmentSetsData/HBox/VBoxContainer2/HBoxContainer2/EquipPortrait3
@onready var rank_2_equip_portraits = [rank_2_equip_portrait1, rank_2_equip_portrait2, rank_2_equip_portrait3]

@onready var rank_3_equip_portrait1 = $EquipmentSetsData/HBox/VBoxContainer2/HBoxContainer3/EquipPortrait1
@onready var rank_3_equip_portrait2 = $EquipmentSetsData/HBox/VBoxContainer2/HBoxContainer3/EquipPortrait2
@onready var rank_3_equip_portrait3 = $EquipmentSetsData/HBox/VBoxContainer2/HBoxContainer3/EquipPortrait3
@onready var rank_3_equip_portraits = [rank_3_equip_portrait1, rank_3_equip_portrait2, rank_3_equip_portrait3]

@onready var rank_4_equip_portrait1 = $EquipmentSetsData/HBox/VBoxContainer2/HBoxContainer4/EquipPortrait1
@onready var rank_4_equip_portrait2 = $EquipmentSetsData/HBox/VBoxContainer2/HBoxContainer4/EquipPortrait2
@onready var rank_4_equip_portrait3 = $EquipmentSetsData/HBox/VBoxContainer2/HBoxContainer4/EquipPortrait3
@onready var rank_4_equip_portaits = [rank_4_equip_portrait1, rank_4_equip_portrait2, rank_4_equip_portrait3]

@onready var rank_5_equip_portrait1 = $EquipmentSetsData/HBox/VBoxContainer2/HBoxContainer5/EquipPortrait1
@onready var rank_5_equip_portrait2 = $EquipmentSetsData/HBox/VBoxContainer2/HBoxContainer5/EquipPortrait2
@onready var rank_5_equip_portrait3 = $EquipmentSetsData/HBox/VBoxContainer2/HBoxContainer5/EquipPortrait3
@onready var rank_5_equip_portraits = [rank_5_equip_portrait1, rank_5_equip_portrait2, rank_5_equip_portrait3]

@onready var all_equip_portraits = [rank_1_equip_portraits,rank_2_equip_portraits,rank_3_equip_portraits,rank_4_equip_portaits,rank_5_equip_portraits]

@onready var equip_winrate1 = $EquipmentSetsData/HBox/VBoxContainer2/HBoxContainer/Winrate1
@onready var equip_winrate2 = $EquipmentSetsData/HBox/VBoxContainer2/HBoxContainer2/Winrate2
@onready var equip_winrate3 = $EquipmentSetsData/HBox/VBoxContainer2/HBoxContainer3/Winrate3
@onready var equip_winrate4 = $EquipmentSetsData/HBox/VBoxContainer2/HBoxContainer4/Winrate4
@onready var equip_winrate5 = $EquipmentSetsData/HBox/VBoxContainer2/HBoxContainer5/Winrate5
@onready var equip_winrates = [equip_winrate1, equip_winrate2, equip_winrate3, equip_winrate4, equip_winrate5]

# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass

func _on_char_picked(character):
	# Set character portrait
	if character:
		#char_portrait.texture = load('dataset/'+str(character)+'/c.png')
		var image = Image.load_from_file('dataset/'+str(character)+'/c.png')
		var texture = ImageTexture.create_from_image(image)
		texture.resource_name = 'dataset/'+str(character)+'/c.png'
		char_portrait.texture = texture
	else:
		char_portrait.texture = load('res://UI/MatchSelect/unknown_hero.png')
	# Reset all equip winrates
	var E7Stat = "Picked NaN%\nWin Rate NaN%"
	for equip_winrate in equip_winrates:
		equip_winrate.text = "No Data"
	
	# Reset all equip portraits
	for equip_portraits in all_equip_portraits:
		for equip_portrait in equip_portraits:
			equip_portrait.visible = false
			
	for chars in char_match_stats:
		if chars['Hero'] == character:
			if str(chars['Pick Rate']).is_valid_float():
				var rate = "%.2f"%(float(chars['Pick Rate'])*100) 
				E7Stat = "Picked "+str(rate)+"%"
			else:
				E7Stat = "Picked NaN%"
			
			if str(chars['Winrate']).is_valid_float() and float(chars['Winrate']) != -1.0:
				var rate = "%.2f"%(float(chars['Winrate'])*100)
				E7Stat += "\nWin Rate "+str(rate)+"%"
			else:
				E7Stat += "\nWin Rate NaN%"
				
	# Set Character Stat label
	char_stat.text = E7Stat
	
	var e7_char_stat = "Win Rate NaN%\n# NaN"
	
	
	for chars in hero_data:
		if chars['Hero'] == character:
			if str(chars['Win Rate']).is_valid_float():
				print('win rate: ' + str(chars['Win Rate']))
				var rate = "%.2f"%float(chars['Win Rate'])
				e7_char_stat = "Win Rate "+str(rate)+"%"
			else:
				e7_char_stat = "Win Rate NaN%"
				
			if not (str(chars['Rank']) == "" or "Ranking:" not in str(chars['Rank'])):
				e7_char_stat += "\n# " + str(chars['Rank']).split("Ranking: ")[1].strip_edges()
			else:
				e7_char_stat += "\n# NaN"
			
			var equipments = JSON.parse_string(chars['Equipment'].replace('\'', "\""))
			var equipment_win_rate = JSON.parse_string(chars['Equipment Win Rate'].replace('\'', "\""))
			print(equipments)
			
			# First hide all equipment portraits
			for equipment_portrait_array in all_equip_portraits:
				for equipment_portrait in equipment_portrait_array:
					equipment_portrait.visible = false
			
			var i = 0
			if equipments:
				for key in equipments.keys():
					# TODO make a system that loads all equipment png
					var equipment_array = equipments[key]
					var portrait_index = 0
					for equip in equipment_array:
						# Make the portrait visible first
						all_equip_portraits[i][portrait_index].visible = true
						#all_equip_portraits[i][portrait_index].texture = load('CharacterUI/Sets/'+str(equip)+'.png')
						var image = Image.load_from_file('CharacterUI/Sets/'+str(equip)+'.png')
						var texture = ImageTexture.create_from_image(image)
						texture.resource_name = 'CharacterUI/Sets/'+str(equip)+'.png'
						all_equip_portraits[i][portrait_index].texture = texture
						portrait_index += 1
						print(equip)
					#equip_portraits[i].texture = load('UI/Sets/'+str(equipments[key])+'.png')
					if str(equipment_win_rate[key]) == "-1":
						equip_winrates[i].text = "Win Rate " + "NaN" +"%"
					else:						
						equip_winrates[i].text = "Win Rate " + equipment_win_rate[key] +"%"
					i+=1
					
				
	epic7_char_stat.text = e7_char_stat
