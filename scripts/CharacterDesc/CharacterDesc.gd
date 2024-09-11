extends Node

# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	pass
	
func levenshtein_distance(str1: String, str2: String) -> int:
	var len1 = str1.length()
	var len2 = str2.length()
	
	if len1 == 0:
		return len2
	if len2 == 0:
		return len1
	
	var matrix = []
	for i in range(len1 + 1):
		matrix.append([])
		for j in range(len2 + 1):
			if i == 0:
				matrix[i].append(j)
			elif j == 0:
				matrix[i].append(i)
			else:
				matrix[i].append(0)
	
	for i in range(1, len1 + 1):
		for j in range(1, len2 + 1):
			var cost = 0 if str1[i - 1] == str2[j - 1] else 1
			matrix[i][j] = min(matrix[i - 1][j] + 1, min(matrix[i][j - 1] + 1, matrix[i - 1][j - 1] + cost))
	
	return matrix[len1][len2]

func find_file(directory_path: String, search_term: String) -> Dictionary:
	# Get the list of files in the directory
	var dir := DirAccess.open(directory_path)
	
	if dir == null:
		print("Cannot open directory: ", directory_path)
		return {"file_path": "", "file_without_ext": ""}
	
	# Convert the search term to lowercase and split it into words
	search_term = search_term.to_lower()
	var search_terms = search_term.split(" ")
	
	# Store best match information
	var best_match = {"file_path": "", "file_without_ext": ""}
	var best_distance = -1
	var exact_word_match_found = false
	var exact_phrase_match_found = false
	var prefix_match_found = false
	
	# Iterate through all files in the directory
	dir.list_dir_begin()
	var file = dir.get_next()
	
	while file != "":
		# Skip "." and ".." which represent the current and parent directories
		if file != "." and file != "..":
			# Check if it's a file and not a directory
			if not dir.current_is_dir():
				# Check if the file has a .png extension
				if file.ends_with(".png"):
					# Extract the name without the extension
					var file_without_ext = file.substr(0, file.length() - 4).to_lower()  # remove .png and convert to lowercase
					var file_words = file_without_ext.split(" ")
					
					# Check for exact phrase match
					if search_term == file_without_ext:
						exact_phrase_match_found = true
						best_match = {"file_path": directory_path.path_join(file), "file_without_ext": file_without_ext}
						break  # Since an exact phrase match is found, exit the loop
					
					# Check if the search term is an exact match for any word in the file name
					var all_words_match = true
					for term in search_terms:
						if term not in file_words:
							all_words_match = false
							break
					
					if all_words_match:
						# Prefer exact word match
						exact_word_match_found = true
						best_match = {"file_path": directory_path.path_join(file), "file_without_ext": file_without_ext}
					
					# Check if the search term is a prefix of any word in the file name
					if not exact_phrase_match_found and not exact_word_match_found:
						for word in file_words:
							if word.begins_with(search_terms[0]):  # Check if first word is a prefix match
								prefix_match_found = true
								best_match = {"file_path": directory_path.path_join(file), "file_without_ext": file_without_ext}
								break
					
					# Calculate the Levenshtein distance as a fallback
					if not exact_phrase_match_found and not exact_word_match_found and not prefix_match_found:
						var distance = levenshtein_distance(file_without_ext, search_term)
						
						# Update best match if a closer match is found
						if best_distance == -1 or distance < best_distance:
							best_distance = distance
							best_match = {"file_path": directory_path.path_join(file), "file_without_ext": file_without_ext}
		file = dir.get_next()
	
	dir.list_dir_end()
	return best_match


func set_content(char_code) -> void:
	var skill_name_label1 = $ColorRect/ScrollContainer/AspectRatioContainer/VBoxContainer/Skill1Margin/SkillContainer/CenterContainer/VBoxContainer/SkillTitle
	var skill_name_label2 = $ColorRect/ScrollContainer/AspectRatioContainer/VBoxContainer/Skill2Margin/SkillContainer/CenterContainer/VBoxContainer/SkillTitle
	var skill_name_label3 = $ColorRect/ScrollContainer/AspectRatioContainer/VBoxContainer/Skill3Margin/SkillContainer/CenterContainer/VBoxContainer/SkillTitle
	var skill_name_labels = [skill_name_label1, skill_name_label2, skill_name_label3]
	
	var skill_desc_label1 = $ColorRect/ScrollContainer/AspectRatioContainer/VBoxContainer/Skill1Margin/SkillContainer/CenterContainer2/VBoxContainer/SkillDesc
	var skill_desc_label2 = $ColorRect/ScrollContainer/AspectRatioContainer/VBoxContainer/Skill2Margin/SkillContainer/CenterContainer2/VBoxContainer/SkillDesc
	var skill_desc_label3 = $ColorRect/ScrollContainer/AspectRatioContainer/VBoxContainer/Skill3Margin/SkillContainer/CenterContainer2/VBoxContainer/SkillDesc
	var skill_desc_labels = [skill_desc_label1, skill_desc_label2, skill_desc_label3]
	
	var skill_portrait1 = $ColorRect/ScrollContainer/AspectRatioContainer/VBoxContainer/Skill1Margin/SkillContainer/CenterContainer/VBoxContainer/CenterContainer/StaticPortrait
	var skill_portrait2 = $ColorRect/ScrollContainer/AspectRatioContainer/VBoxContainer/Skill2Margin/SkillContainer/CenterContainer/VBoxContainer/CenterContainer/StaticPortrait
	var skill_portrait3 = $ColorRect/ScrollContainer/AspectRatioContainer/VBoxContainer/Skill3Margin/SkillContainer/CenterContainer/VBoxContainer/CenterContainer/StaticPortrait
	var skill_portraits = [skill_portrait1, skill_portrait2, skill_portrait3]
	
	var skill_turn_label1 = $ColorRect/ScrollContainer/AspectRatioContainer/VBoxContainer/Skill1Margin/SkillContainer/CenterContainer/VBoxContainer/SkillCd
	var skill_turn_label2 = $ColorRect/ScrollContainer/AspectRatioContainer/VBoxContainer/Skill2Margin/SkillContainer/CenterContainer/VBoxContainer/SkillCd
	var skill_turn_label3 = $ColorRect/ScrollContainer/AspectRatioContainer/VBoxContainer/Skill3Margin/SkillContainer/CenterContainer/VBoxContainer/SkillCd
	var skill_turn_labels = [skill_turn_label1, skill_turn_label2, skill_turn_label3]
	
	var dbuff_portrait_container1 = $ColorRect/ScrollContainer/AspectRatioContainer/VBoxContainer/Skill1Margin/SkillContainer/CenterContainer2/VBoxContainer/MarginContainer/DBuffContainer
	var dbuff_portrait_container2 = $ColorRect/ScrollContainer/AspectRatioContainer/VBoxContainer/Skill2Margin/SkillContainer/CenterContainer2/VBoxContainer/MarginContainer/DBuffContainer
	var dbuff_portrait_container3 = $ColorRect/ScrollContainer/AspectRatioContainer/VBoxContainer/Skill3Margin/SkillContainer/CenterContainer2/VBoxContainer/MarginContainer/DBuffContainer
	var dbuff_portrait_containers = [dbuff_portrait_container1, dbuff_portrait_container2, dbuff_portrait_container3]
	
	var name = "Unknown"
	var element_img = 'CharacterUI/elements/%s.png'%"dark"
	var role_img = 'CharacterUI/roles/%s.png'%'assassin'
	
	var skill_imgs = []
	var skill_names = []
	var skill_descs = []
	var soul_burn_descs = []
	
	var skill_img_base = "CharacterUI/skill_images/"+char_code+"/"
	
	for hero in GlobalVars.hero_details:
		if hero['Hero'] == char_code:
			name = hero['Hero Name']
			element_img = 'CharacterUI/elements/%s.png'%hero['Element']
			role_img = 'CharacterUI/roles/%s.png'%hero['Role']
			
			# skill names to array
			skill_names = JSON.parse_string(hero['Hero Skill Names'])
			
			# skill desc to array
			skill_descs = JSON.parse_string(hero['Hero Skill Descriptions'])
			
			# skill desc to array
			soul_burn_descs = JSON.parse_string(hero['Soul Burn Descriptions'])
			
			# skill cooldowns to array
			var skill_cds = JSON.parse_string(hero['Hero Skill Turns'].replace("'","\"").strip_edges())
			for skill_cd_index in skill_cds.size():
				if skill_cds[skill_cd_index] == "":
					skill_turn_labels[skill_cd_index].visible = false
				else:
					skill_turn_labels[skill_cd_index].visible = true
					skill_turn_labels[skill_cd_index].text = skill_cds[skill_cd_index]
			
			# Display Soul Count
			var soul_burn_count = JSON.parse_string(hero['Soul Burn Count'].replace("'","\"").strip_edges())
			for skill_portrait_index in skill_portraits.size():
				if soul_burn_count[skill_portrait_index] != "":
					if soul_burn_count[skill_portrait_index].contains("10"):
						skill_portraits[skill_portrait_index].SetSouls.emit(1)
						# Add Soul Burn info to skill_descs
						skill_descs[skill_portrait_index] =skill_descs[skill_portrait_index]+'\n[color=lightblue]Soul Burn (10 souls): ' + soul_burn_descs[skill_portrait_index]+'[/color]'

					if soul_burn_count[skill_portrait_index].contains("20"):
						skill_portraits[skill_portrait_index].SetSouls.emit(2)
						# Add Soul Burn info to skill_descs
						skill_descs[skill_portrait_index] =skill_descs[skill_portrait_index]+'\n[color=lightblue]Soul Burn (20 souls): ' + soul_burn_descs[skill_portrait_index]+'[/color]'
			
			# Display Hero Skill Images
			for skill_portrait_index in skill_portraits.size():
				var image = Image.load_from_file(skill_img_base+'sk_'+str(skill_portrait_index+1)+'.png')
				var texture = ImageTexture.create_from_image(image)
				texture.resource_path = skill_img_base+'sk_'+str(skill_portrait_index+1)+'.png'				
				skill_portraits[skill_portrait_index].texture = texture
				
	# Display Hero Name
	$ColorRect/ScrollContainer/AspectRatioContainer/VBoxContainer/MarginContainer/NameContainer/VBoxContainer/MarginContainer2/Name.text = name
	
	var image = Image.load_from_file('res://dataset/%s/c.png'%char_code)
	var texture = ImageTexture.create_from_image(image)
	texture.resource_path = 'res://dataset/%s/c.png'%char_code			
	
	# Dispaly Hero Portrait
	$ColorRect/ScrollContainer/AspectRatioContainer/VBoxContainer/MarginContainer/NameContainer/HeroPortrait.texture = texture
	
	var element_image = Image.load_from_file(element_img)
	var element = ImageTexture.create_from_image(element_image)
	element.resource_path = element_img
	
	# Display Element Portrait
	$ColorRect/ScrollContainer/AspectRatioContainer/VBoxContainer/MarginContainer/NameContainer/VBoxContainer/MarginContainer/HBoxContainer/ElementPortrait.texture = element
	
	var role_image = Image.load_from_file(role_img)
	var role = ImageTexture.create_from_image(role_image)
	role.resource_path = role_img
	# Display Role Portrait
	$ColorRect/ScrollContainer/AspectRatioContainer/VBoxContainer/MarginContainer/NameContainer/VBoxContainer/MarginContainer/HBoxContainer/RolePortrait.texture = role

	# Display Skill Names
	for name_index in skill_names.size():
		skill_name_labels[name_index].text = skill_names[name_index]
	
	# Define Buff/Debuff Regex
	var debuff_regex = RegEx.new()
	debuff_regex.compile("\\[color=red\\](.*?)\\[\\/color\\]")
	
	var buff_regex = RegEx.new()
	buff_regex.compile("\\[color=#1080e5\\](.*?)\\[\\/color\\]")
	
	# Display Skill Descriptions
	for skill_index in skill_descs.size():
		skill_desc_labels[skill_index].text = skill_descs[skill_index]
		
		# Find Debuffs
		var debuffs_selected = []
		var debuffs = debuff_regex.search_all(skill_descs[skill_index])
		for debuff_index in debuffs.size():
			var portrait_scene = load('res://scenes/CharacterDesc/StaticPortrait.tscn')
			var portrait_scene_instance = portrait_scene.instantiate()
			
			var DBuff_Portrait = portrait_scene_instance as TextureRect
			
			DBuff_Portrait.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
			DBuff_Portrait.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
			DBuff_Portrait.custom_minimum_size = Vector2(40,40)
			
			# Check if the buff is "Random Debuff" or "Random Debuffs"
			if debuffs[debuff_index].get_string(1).to_lower() == "random debuff" or debuffs[debuff_index].get_string(1).to_lower() == "random debuffs":
				for record in GlobalVars.buffs_debuffs_details:
							if record['Name'].to_lower() == "random debuff":
								var heroes = JSON.parse_string(record['Heroes'].replace("'","\"").strip_edges())
								if char_code in heroes:
									var random_buffs = record['Description'].split(",")
									for random_buff in random_buffs:
										var DBuff_image_path = find_file('CharacterUI/debuff_images/', random_buff.strip_edges())
										if not DBuff_image_path['file_path'] in debuffs_selected:
											debuffs_selected.append(DBuff_image_path['file_path'])
											var multi_portrait_scene = load('res://scenes/CharacterDesc/StaticPortrait.tscn')
											var multi_portrait_scene_instance = multi_portrait_scene.instantiate()
											
											var multi_DBuff_Portrait = multi_portrait_scene_instance as TextureRect
											
											multi_DBuff_Portrait.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
											multi_DBuff_Portrait.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
											multi_DBuff_Portrait.custom_minimum_size = Vector2(40,40)
											var image_texture = Image.load_from_file(DBuff_image_path['file_path'])
											var texture_portrait = ImageTexture.create_from_image(image_texture)
											texture_portrait.resource_path = DBuff_image_path['file_path']	
											
											multi_DBuff_Portrait.texture = texture_portrait
						
											# Update Tooltip
											multi_DBuff_Portrait.tooltip_text = DBuff_image_path['file_without_ext']
											for single_buff in GlobalVars.buffs_debuffs_details:
												if single_buff['Name'].to_lower() == DBuff_image_path['file_without_ext'].to_lower():
													print('db: des' + single_buff['Name'])
													multi_DBuff_Portrait.tooltip_text += "\n"+single_buff['Description']
													break
											
											dbuff_portrait_containers[skill_index].add_child(multi_DBuff_Portrait)
											
											print('db rand debuff: '+DBuff_image_path['file_without_ext'])
											print('db rand debuff: '+DBuff_image_path['file_path'])
									break
													
			else:
				var DBuff_image_path = find_file('CharacterUI/debuff_images/', debuffs[debuff_index].get_string(1))
				if DBuff_image_path['file_path'] != "":
					if not DBuff_image_path['file_path'] in debuffs_selected:
						# Keep track of already shown debuffs
						debuffs_selected.append(DBuff_image_path['file_path'])
						var debuff_img = Image.load_from_file(DBuff_image_path['file_path'])
						var debuff_texture = ImageTexture.create_from_image(debuff_img)
						debuff_texture.resource_path = DBuff_image_path['file_path']	
						
						DBuff_Portrait.texture = debuff_texture
						
						# Update tooltip
						DBuff_Portrait.tooltip_text = DBuff_image_path['file_without_ext']
						
						for record in GlobalVars.buffs_debuffs_details:
							if record['Name'].to_lower() == DBuff_image_path['file_without_ext'].to_lower():
								DBuff_Portrait.tooltip_text += "\n"+record['Description']
									
								dbuff_portrait_containers[skill_index].add_child(DBuff_Portrait)
								break
						print('db debuff: '+DBuff_image_path['file_without_ext'])
						print('db debuff: '+DBuff_image_path['file_path'])						
						
			
		# Find Buffs
		var buffs_selected = []
		var buffs = buff_regex.search_all(skill_descs[skill_index]) 
		for buff_index in buffs.size():
			var portrait_scene = load('res://scenes/CharacterDesc/StaticPortrait.tscn')
			var portrait_scene_instance = portrait_scene.instantiate()
			
			var DBuff_Portrait = portrait_scene_instance as TextureRect
			
			DBuff_Portrait.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
			DBuff_Portrait.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
			DBuff_Portrait.custom_minimum_size = Vector2(40,40)
			
			print('db regex: '+ buffs[buff_index].get_string(1))
			# Check if the buff is "Random Buff" or "Random Buffs"
			if buffs[buff_index].get_string(1).to_lower() == "random buff" or buffs[buff_index].get_string(1).to_lower() == "random buffs":
				for record in GlobalVars.buffs_debuffs_details:
							if record['Name'].to_lower() == "random buff":
								var heroes = JSON.parse_string(record['Heroes'].replace("'","\"").strip_edges())
								if char_code in heroes:
									var random_buffs = record['Description'].split(",")
									for random_buff in random_buffs:
										var DBuff_image_path = find_file('CharacterUI/buff_images/', random_buff.strip_edges())
										if not DBuff_image_path['file_path'] in buffs_selected:
											buffs_selected.append(DBuff_image_path['file_path'])
											print('db random buffs: '+ DBuff_image_path['file_path'])
											var multi_portrait_scene = load('res://scenes/CharacterDesc/StaticPortrait.tscn')
											var multi_portrait_scene_instance = multi_portrait_scene.instantiate()
											
											var multi_DBuff_Portrait = multi_portrait_scene_instance as TextureRect
											
											multi_DBuff_Portrait.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
											multi_DBuff_Portrait.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
											multi_DBuff_Portrait.custom_minimum_size = Vector2(40,40)
											var buff_image = Image.load_from_file(DBuff_image_path['file_path'])
											var buff_texture = ImageTexture.create_from_image(buff_image)
											buff_texture.resource_path = DBuff_image_path['file_path']
											
											multi_DBuff_Portrait.texture = buff_texture
						
											# Update Tooltip
											multi_DBuff_Portrait.tooltip_text = DBuff_image_path['file_without_ext']
											for single_buff in GlobalVars.buffs_debuffs_details:
												if single_buff['Name'].to_lower() == DBuff_image_path['file_without_ext'].to_lower():
													multi_DBuff_Portrait.tooltip_text += "\n"+single_buff['Description']
													break
											
											dbuff_portrait_containers[skill_index].add_child(multi_DBuff_Portrait)
									break

			else:
				var DBuff_image_path = find_file('CharacterUI/buff_images/', buffs[buff_index].get_string(1))
				if DBuff_image_path['file_path'] != "":
					if not DBuff_image_path['file_path'] in buffs_selected:
						# Keep track of buffs that were shown
						buffs_selected.append(DBuff_image_path['file_path'])
						var buff_image = Image.load_from_file(DBuff_image_path['file_path'])
						var buff_texture = ImageTexture.create_from_image(buff_image)
						buff_texture.resource_path = DBuff_image_path['file_path']
						
						DBuff_Portrait.texture = buff_texture
						
						# Update Tooltip
						DBuff_Portrait.tooltip_text = DBuff_image_path['file_without_ext']
						
						for record in GlobalVars.buffs_debuffs_details:
							if record['Name'].to_lower() == DBuff_image_path['file_without_ext'].to_lower():
								DBuff_Portrait.tooltip_text += "\n"+record['Description']
								
								dbuff_portrait_containers[skill_index].add_child(DBuff_Portrait)
								break
						print('db: '+DBuff_image_path['file_path'])
				
	
func _on_close_requested():
	queue_free()
