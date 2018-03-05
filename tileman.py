'''
Code Org:
-Imports
-Pygame Setup [initializations & population sourcing]
-Tools [block/blockmatrix tools]
-Game Logic [initializations, function defs, obj classes]
-Main Calls [function defs & calls]
'''

#####Imports#####
from draw import draw_mat, draw_input, draw_output
from matrix_tools import *
import sys
from pygame import *
import pygame.transform as pytr
import pygame.image as pyim
import random
import pygame.font as pyfont

#####Pygame Setup######
#Initializations
SHOW_BLOCKS = 4
BLOCK_WIDTH = 4
MASTER_SEED = 7256412
width, height = 480, 630
size = (width, height)
back_col = (0, 212, 157)
square_width = 30
tiles_wide = width // square_width
tiles_high = height // square_width
dimensions = [tiles_wide, tiles_high]
square_size = (square_width, square_width)
messages = []
alpha_num_keys = [K_a, K_b, K_c, K_d, K_e, K_f, K_g, K_h, K_i, K_j, K_k, K_l, K_m, K_n, K_o,K_p, K_q, K_r, K_s, K_t, K_u, K_v, K_w, K_x, K_y, K_z, K_0, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9, K_BACKSPACE, K_RETURN, K_SPACE]
alpha_num_chars = "abcdefghijklmnopqrstuvwxyz0123456789B! "
user_input = ""
execute_and_clear = False
init()
pyfont.init()
opensans_font = pyfont.Font("Open_Sans/OpenSans-SemiBold.ttf", 13)
screen = display.set_mode(size)
#Populate sources
sources = {}
filenames_codes = [	("heroU.png", 0),
					("heroL.png", 1),
					("heroD.png", 2),
					("heroR.png", 3),
					("green.png", 888),
					("tree.png", 222),
					("coin.png", 777),
					("mush.png", 555)	]
for filename, code in filenames_codes:
	sources[code] = pytr.scale(pyim.load(filename), square_size)


######Tools######
## Block & block matrix tools
def random_seed_fill(a, b):
	choices = [888, 222, 777, 555]
	weights = [200000, 50000, 10000, 10]
	master_random = random.Random(MASTER_SEED)
	allowable = []
	for i, w in enumerate(weights):
		allowable += [choices[i]] * w
	def create_allowable_int(size, rand_obj):
		number = 0
		for i in range(size):
			number *= 1000
			number += rand_obj.choice(allowable)
		return number
	return fill2Dmat(a, b, lambda x, y: create_allowable_int(BLOCK_WIDTH**2, master_random))

def extract_num(i,j,block_id):
	pos = i * BLOCK_WIDTH + j
	return (block_id // (1000 ** pos) ) % 1000

def make_block(block_id):
	return fill2Dmat(BLOCK_WIDTH,BLOCK_WIDTH, lambda x,y: extract_num(x,y,block_id))

def print_block(block, isNum=False):
	if isNum:
		block = make_block(block)
	print("BLOCK")
	for row in block:
		print(row)
	print()

def compress_block(block):
	x=[]
	for row in block:
		for i in row:
			x.append(str(i))
	x.reverse()
	return int(''.join(x))

def to_BImat(block_mat):
	imat = [[] for i in range(len(block_mat[0]) * len(block_mat[0][0]))]
	for i, blockrow in enumerate(block_mat):
		for j, block in enumerate(blockrow):
			for k, row in enumerate(block):
				imat[i * len(block) + k] += row
	return imat

def get_showable(BImat, x, y, appearance):
	submatrix = submat(show_posy[0],show_posy[1],show_posx[0],show_posx[1],BImat)
	submatrix[y][x] = appearance
	return submatrix

def new_BImat():
	block_mat = gen_mat(y_range[0], y_range[1], x_range[0], x_range[1], seed_mat, lambda a, b, i0, i1, j0, j1, seed_mat: make_block(seed_mat[a][b]))
	return to_BImat(block_mat)

#####Game Logic#####
#Initializations
seed_mat = random_seed_fill(80, 80)
y_range = [0, 6]
x_range = [0, 6]
show_posy = [4, 20]
show_posx = [4, 20]
BImat = new_BImat()
show_mat = get_showable(BImat, 8, 8, 2)

#General Functions
def change_num(i,j,delta,num):
	block = make_block(num)
	block[i][j] += delta
	return compress_block(block)

def tile_hero_interaction(tile, hero):
	i, j = hero.in_block_coords() #i & j denote where in a block the hero is
	seed_x, seed_y = hero.seed_coords()
	
	#gets the new tile id
	block_id = seed_mat[seed_y][seed_x]
	pos = j * BLOCK_WIDTH + i
	tile_id = extract_num(j,i,block_id)
	new_tile_id = tile.interact(hero)
	block_id = seed_mat[seed_y][seed_x]
	

	#update seed matrix with new tile
	delta = new_tile_id - tile_id
	current_long = seed_mat[seed_y][seed_x]
	seed_mat[seed_y][seed_x] = change_num(j, i, delta, current_long)
	return new_tile_id
	
#Classes
class BaseTile:
	def __init__(self, name, source, interact, stop):
		self.name = name
		self.source = source
		self.interact = interact
		self.stop = stop

class StopBase(BaseTile):
	def __init__(self, name, source, interact):
		super().__init__(name, source, interact, True)

class StepBase(BaseTile):
	def __init__(self, name, source, interact):
		super().__init__(name, source, interact, False)
		

class Tile:
	def __init__(self, tile_id):
		self.base = bases[tile_id]
		self.name = self.base.name
		self.interact = self.base.interact
		self.source = self.base.source
		self.stop = self.base.stop

#Base Tile Stuff
def do_nothing(hero):
	return
def grass_action(hero):
	return 888
def coin_action(hero):
	global messages
	hero.coins += 1
	messages.append("Coins: "+str(hero.coins))
	return grass_action(hero)
def mushroom_action(hero):
	global messages
	hero.mushrooms += 1
	messages.append("You collected a rare mushroom! Rare mushrooms: "+str(hero.mushrooms))
	return grass_action(hero)

baseCoin = StepBase("coin", 777, coin_action)
baseShroom = StepBase("mushroom", 555, mushroom_action)
baseTree = StopBase("tree", 222, do_nothing)
baseGrass = StepBase("grass", 888, grass_action)
bases = {222: baseTree, 888: baseGrass, 777: baseCoin, 555: baseShroom}


class Explorer:
	def __init__(self):
		self.coins = 0
		self.mushrooms = 0
		###Movement Variables###
		self.x = 8
		self.y = 8
		#Up, Left, Down, Right
		self.counts = [0,0,0,0]
		#minY, minX, maxY, maxX
		self.edges = [3,3,12,12]

	def vis_coords(self):
		return (self.x, self.y)

	def in_block_coords(self):
		BI_x, BI_y = self.BImat_coords()
		return (BI_x%BLOCK_WIDTH, BI_y%BLOCK_WIDTH)

	def BImat_coords(self):
		return (show_posx[0] + self.x, show_posy[0] + self.y)

	def block_coords(self):
		# 0 <= block_coord x < BLOCK_WIDTH,
		# 0 <= block_coord y < BLOCK_WIDTH,
		BI_x, BI_y = self.BImat_coords()
		return ((BI_x - BI_x % BLOCK_WIDTH) // BLOCK_WIDTH) - 1, ((BI_y - BI_y % BLOCK_WIDTH) // BLOCK_WIDTH) - 1

	def seed_coords(self):
		block_x, block_y = self.block_coords()
		return x_range[0] + block_x + 1, y_range[0] + block_y + 1

	def print_coords(self):
		print("Visible Coords",self.vis_coords())
		print("Big IMat Coords",self.BImat_coords())
		print("Block Coords",self.block_coords())

	def around_actions(self):
		x, y = self.BImat_coords()
		around = (	(x+1,y+1),(x,y+1),(x-1,y+1),
					(x+1,y),          (x-1,y),
					(x+1,y-1),(x,y-1),(x-1,y-1),)
		for x0, y0 in around:
			outer_tile = bases[BImat[y0][x0]]
			if outer_tile.stop:
				outer_tile.interact(hero)

	def attempt_move(self, direction):
		global show_mat
		if direction == "u":
			delX, delY = 0, 1
		elif direction == "l":
			delX, delY = 1, 0,
		elif direction == "d":
			delX, delY = 0, -1
		elif direction == "r":
			delX, delY = -1, 0
		player_x, player_y = self.BImat_coords()
		next_tile_x = player_x - delX
		next_tile_y = player_y - delY
		next_tile = Tile(BImat[next_tile_y][next_tile_x])
		 
		if not next_tile.stop:
			self.move(direction, delX, delY)
			new_tile_code = tile_hero_interaction(next_tile, self)
			tile_x, tile_y = self.BImat_coords()
			BImat[tile_y][tile_x] = new_tile_code
		self.around_actions()
		

	def move(self, direction, delX, delY):
		global BImat
		global show_mat
		direction = direction.lower()
		if direction == "u":
			count_ind, show_range, block_range = 0, show_posy, y_range
		elif direction == "l":
			count_ind, show_range, block_range = 1, show_posx, x_range
		elif direction == "d":
			count_ind, show_range, block_range = 2, show_posy, y_range
		elif direction == "r":
			count_ind, show_range, block_range = 3, show_posx, x_range
		edge_coord = self.edges[count_ind]

		self.y -= delY
		self.x -= delX

		if(self.y == edge_coord):
			self.y += delY
			self.counts[count_ind] += 1
			for i in range(len(show_range)):
				show_range[i] -= delY
		elif(self.x == edge_coord):
			self.x += delX
			self.counts[count_ind] += 1
			for i in range(len(show_range)):
				show_range[i] -= delX

		if(self.counts[count_ind] == BLOCK_WIDTH):
			self.counts[count_ind] = 0
			for i in range(len(block_range)):
				y_range[i] = (y_range[i] - delY) 
				x_range[i] = (x_range[i] - delX)
			for i in range(len(show_range)):
				direction = max(delX, delY, key = lambda a: abs(a))
				show_range[i] += BLOCK_WIDTH * direction
			BImat = new_BImat()
		#self.print_coords()
		show_mat = get_showable(BImat, self.x, self.y, count_ind)
			

#####Main#####
#Function Definitions
def move_key_manager(keys, move_ticker, hero):
	#Hero Movement
	if move_ticker:
		move_ticker -= 1
	else:
		move_ticker = 7
		if keys[K_LEFT]:
			hero.attempt_move('l')
		elif keys[K_RIGHT]:
			hero.attempt_move('r')
		elif keys[K_UP]:
			hero.attempt_move('u')
		elif keys[K_DOWN]:
			hero.attempt_move('d')
		else:
			move_ticker = 0
	return move_ticker

def user_key_manager(keys, last_key, hero):
	global user_input
	global execute_and_clear
	untouched = True
	#User Input
	for i, key in enumerate(alpha_num_keys):
		if keys[key]:
			untouched = False
			char_key = alpha_num_chars[i]
			if char_key != last_key:
				last_key = char_key
				if char_key == "!":
					execute_and_clear = True
				elif char_key == "B":
					if keys[K_LSHIFT] or keys[K_RSHIFT]:
						user_input = ""
					user_input = user_input[:len(user_input) - 1]
				else:
					user_input += char_key
			break
	if untouched:
		last_key = ""
	return last_key

def input_manager():
	global execute_and_clear
	global user_input
	draw_input(screen, user_input, execute_and_clear, opensans_font)
	if execute_and_clear:
		user_input = ""
		execute_and_clear = False
	
def game_loop(hero):
	k = 0
	move_ticker = 0
	last_key = ""
	matches = 0
	while True:
		draw_mat(show_mat, sources, screen, back_col, square_width)
		draw_output(screen, messages, opensans_font)
		for e in event.get():
			if e.type == QUIT:
				sys.exit()
		if k:	
			move_ticker = move_key_manager(key.get_pressed(), move_ticker, hero)
			last_key = user_key_manager(key.get_pressed(), last_key, hero)
		input_manager()
		display.flip()
		k+=1

#Calls
hero = Explorer()
game_loop(hero)

'''
Feature Ideas
-block patterns
-refactoring
-wrap around map
-game objective
-external rooms
-external communication/control (keyboard based)
-add interactive stops










'''