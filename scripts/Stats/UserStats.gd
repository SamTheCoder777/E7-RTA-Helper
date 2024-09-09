extends Node

var most_char1
var most_char2
var most_char3
var most_char4
var most_char5
var most_chars

var most_stat1
var most_stat2
var most_stat3
var most_stat4
var most_stat5
var most_stats

var recent_char1
var recent_char2
var recent_char3
var recent_char4
var recent_char5
var recent_chars

var recent_stat1
var recent_stat2
var recent_stat3
var recent_stat4
var recent_stat5
var recent_stats

signal _update_most_picks(characters)
signal _update_recent_picks()

# Called when the node enters the scene tree for the first time.
func _ready():
	most_char1 = $HBoxContainer/VBoxContainer/HBoxContainer/MostChar1
	most_char2 = $HBoxContainer/VBoxContainer/HBoxContainer2/MostChar2
	most_char3 = $HBoxContainer/VBoxContainer/HBoxContainer3/MostChar3
	most_char4 = $HBoxContainer/VBoxContainer/HBoxContainer4/MostChar4
	most_char5 = $HBoxContainer/VBoxContainer/HBoxContainer5/MostChar5
	most_chars = [most_char1, most_char2, most_char3, most_char4, most_char5]
	
	most_stat1 = $HBoxContainer/VBoxContainer/HBoxContainer/MostStat1
	most_stat2 = $HBoxContainer/VBoxContainer/HBoxContainer2/MostStat2
	most_stat3 = $HBoxContainer/VBoxContainer/HBoxContainer3/MostStat3
	most_stat4 = $HBoxContainer/VBoxContainer/HBoxContainer4/MostStat4
	most_stat5 = $HBoxContainer/VBoxContainer/HBoxContainer5/MostStat5
	most_stats = [most_stat1, most_stat2, most_stat3, most_stat4, most_stat5]
	
	recent_char1 = $HBoxContainer/VBoxContainer2/HBoxContainer/RecentChar1
	recent_char2 = $HBoxContainer/VBoxContainer2/HBoxContainer2/RecentChar2
	recent_char3 = $HBoxContainer/VBoxContainer2/HBoxContainer3/RecentChar3
	recent_char4 = $HBoxContainer/VBoxContainer2/HBoxContainer4/RecentChar4
	recent_char5 = $HBoxContainer/VBoxContainer2/HBoxContainer5/RecentChar5
	recent_chars = [recent_char1, recent_char2, recent_char3, recent_char4, recent_char5]
	
	recent_stat1 = $HBoxContainer/VBoxContainer2/HBoxContainer/RecentStat1
	recent_stat2 = $HBoxContainer/VBoxContainer2/HBoxContainer2/RecentStat2
	recent_stat3 = $HBoxContainer/VBoxContainer2/HBoxContainer3/RecentStat3
	recent_stat4 = $HBoxContainer/VBoxContainer2/HBoxContainer4/RecentStat4
	recent_stat5 = $HBoxContainer/VBoxContainer2/HBoxContainer5/RecentStat5
	recent_stats = [recent_stat1, recent_stat2, recent_stat3, recent_stat4, recent_stat5]

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass

# Give characters as an array
func _on_update_recent_picks(characters: Array):
	# Reset all most pick portraits
	for portrait in recent_chars:
		portrait.texture = load('res://UI/MatchSelect/unknown_hero.png')
	
	# Reset all win rate label
	for win_rate_label in recent_stats:
		win_rate_label.text = "Wins: NaN Losses: NaN\nWin Rate NaN%"
	
	var user_data = GlobalVars.user_data
	
	var user_stats = user_data['character_stats']
	
	var i = 0
	if user_stats:
		# Display portrait image
		for character in characters:
			var image = Image.load_from_file('dataset/'+str(character)+'/c.png')
			var texture = ImageTexture.create_from_image(image)
			texture.resource_name = 'dataset/'+str(character)+'/c.png'				
			recent_chars[i].texture = texture
			
			for stat in user_stats.keys():
				if stat == character:
					var wins = user_stats[stat]['wins']
					var losses = user_stats[stat]['losses']
					if str(losses) and str(wins):
						recent_stats[i].text = "Wins: " + str(wins) +" Losses: " + str(losses) + "\nWin Rate: " +"%.2f"%((float(wins)/(int(wins)+int(losses))*100))+"%"

			i+=1

# From characters from E7 Match History
func _on_update_most_picks():
	# Reset all most pick portraits
	for portrait in most_chars:
		portrait.texture = load('res://UI/MatchSelect/unknown_hero.png')
	
	# Reset all win rate label
	for win_rate_label in most_stats:
		win_rate_label.text = "Wins: NaN Losses: NaN\nWin Rate NaN%"
	
	var user_data = GlobalVars.user_data
	var user_stats = user_data['hero_data']
	
	var i = 0 
	for characters in user_stats:
		#most_chars[i].texture = load('dataset/'+str(characters['code'])+"/c.png")
		var image = Image.load_from_file('dataset/'+str(characters['code'])+'/c.png')
		var texture = ImageTexture.create_from_image(image)
		texture.resource_name = 'dataset/'+str(characters['code'])+'/c.png'				
		most_chars[i].texture = texture
		
		var wins = "NaN"
		var losses = "NaN"
		var winrate = "NaN"
		if str(characters['wins']) and characters['wins'] != "" and "W" in characters['wins']:
			wins = characters['wins'].split("W")[0]
		if str(characters['losses']) and characters['losses'] != "" and "L" in characters['losses']:
			losses = characters['losses'].split("L")[0]
		if str(characters['win_rate']) and characters['win_rate'] != "" and "%" in characters['win_rate']:
			var winrate_raw = characters['win_rate']
			var regex = RegEx.new()
			regex.compile("\\d+.\\d+")
			winrate = regex.search(winrate_raw).get_string()
	
		most_stats[i].text = "Wins: " + str(wins) + " Losses: " + str(losses) + "\nWin Rate: " + "%.2f"%float(winrate)+"%"
		
		i+=1
		
