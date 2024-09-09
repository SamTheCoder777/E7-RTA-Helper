extends HBoxContainer

# Called when the node enters the scene tree for the first time.
var portrait1: TextureRect
var portrait2: TextureRect
var portrait3: TextureRect
var portrait4: TextureRect
var portrait5: TextureRect

var portraits: Array

func _ready():
	portrait1 = self.get_child(0)
	portrait2 = self.get_child(1)
	portrait3 = self.get_child(2)
	portrait4 = self.get_child(3)
	portrait5 = self.get_child(4)
	
	portraits = [portrait1, portrait2, portrait3, portrait4, portrait5]

func set_portraits(character_array):
	# Reset all portraits
	for portrait in portraits:
		print('resetting')
		portrait.texture = load('res://UI/MatchSelect/unknown_hero.png')
	
	var i = 0 # Index for setting portraits
	for character in character_array:
		if i >= portraits.size(): #break when there are more char than portraits
			break
		print('setting ' + character)
		var image = Image.load_from_file('dataset/'+str(character)+'/c.png')
		var texture = ImageTexture.create_from_image(image)
		texture.resource_name = 'dataset/'+str(character)+'/c.png'		
		portraits[i].texture = texture #load the texture
		i+=1
# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta):
#	pass
