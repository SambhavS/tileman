'''
Table of Contents
-Imports
-Pygame Setup [initializations & population sourcing]
-Tools [block/blockmatrix tools]
-Game Logic [initializations, function defs, obj classes]
-Main Calls [function defs & calls]
'''
#####Imports#####
from draw import draw_mat
from matrix_tools import *
import sys
from pygame import *
import pygame.transform as pytr
import pygame.image as pyim
import random

#####Pygame Setup######
#Initializations
SHOW_BLOCKS = 4
BLOCK_WIDTH = 4
init()
width, height = 480, 480
size = (width, height)
back_col = (30, 180, 160)
square_width = 30
tiles_wide = width // square_width
tiles_high = height // square_width
dimensions = [tiles_wide, tiles_high]
square_size = (square_width, square_width)
screen = display.set_mode(size)
#Populate sources
sources = {}
filenames_codes = [	("heroU.png", 0),
					("heroL.png", 1),
					("heroD.png", 2),
					("heroR.png", 3),
					("green.png", 111),
					("stepped.png", 888),
					("tree.png" ,222)	]
for filename, code in filenames_codes:
	sources[code] = pytr.scale(pyim.load(filename), square_size)


######Tools######
## Block & block matrix tools
def random_seed_fill(a, b):
	master_random = random.Random(7256412)
	def create_allowable_int(size, allowable, rand_obj):
		number = 0
		for i in range(size):
			number *= 1000
			number += rand_obj.choice(allowable)
		return number
	return fill2Dmat(a, b, lambda x, y: create_allowable_int(BLOCK_WIDTH**2, [111,111,111,222], master_random))

def extract_num(i,j,block_id):
	pos = i * BLOCK_WIDTH + j
	return (block_id // (1000 ** pos) ) % 1000

def make_block(block_id):
	return fill2Dmat(BLOCK_WIDTH,BLOCK_WIDTH, lambda x,y: extract_num(x,y,block_id))

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

def change_num(i,j,delta,num):
	block = make_block(num)
	block[i][j] += delta
	return compress_block(block)

def tile_hero_interaction(tile, hero):
	i, j = hero.in_block_coords() #i & j denote where in a block the hero is
	seed_x, seed_y = hero.seed_coords()
	BImat_i, BImat_j = hero.BImat_coords()

	#gets the new tile id
	block_id = seed_mat[seed_y][seed_x]
	pos = j * BLOCK_WIDTH + i
	tile_id = extract_num(j,i,block_id)
	print(tile.name)
	new_tile_id = tile.interact(hero)
	print(new_tile_id)
	#update tile on BImat
	BImat[BImat_j][BImat_i] = new_tile_id 	

	#update seed matrix with new tile
	delta = new_tile_id - tile_id
	current_long = seed_mat[seed_y][seed_x]
	seed_mat[seed_y][seed_x] = change_num(j, i, delta, current_long)

#Classes
class BaseTile:
	def __init__(self, name, interact, source, stop):
		self.name = name
		self.interact = interact
		self.source = source
		self.stop = stop

class Tile:
	def __init__(self, tile_id):
		self.base = bases[tile_id]
		self.name = self.base.name
		self.interact = self.base.interact
		self.source = self.base.source
		self.stop = self.base.stop

class Explorer:
	def __init__(self):
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
		return ((BI_x - BI_x%BLOCK_WIDTH)//BLOCK_WIDTH) - 1, ((BI_y - BI_y%BLOCK_WIDTH)//BLOCK_WIDTH) - 1

	def seed_coords(self):
		block_x, block_y = self.block_coords()
		return x_range[0] + block_x + 1, y_range[0] + block_y + 1

	def print_coords(self):
		print("Visible Coords",self.vis_coords())
		print("Big IMat Coords",self.BImat_coords())
		print("Block Coords",self.block_coords())

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
		next_tile_x = player_x + delX
		next_tile_y = player_y + delY
		next_tile = Tile(BImat[next_tile_x][next_tile_y])
		tile_hero_interaction(next_tile, self)
		if not next_tile.stop:
			self.move(direction, delX, delY)

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
def key_manager(keys, move_ticker, hero):
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

def game_loop(hero):
	k = 0
	move_ticker = 0
	while True:
		for e in event.get():
			if e.type == QUIT:
				sys.exit()
		if k:	
			move_ticker = key_manager(key.get_pressed(), move_ticker, hero)
		draw_mat(show_mat, sources, screen, back_col, square_width)
		display.flip()
		k+=1

#Playground
def become_tree(hero):
	print("A")
	return 222
def become_stomped_grass(hero):
	print("B")
	return 888

baseFreshGrass = BaseTile("fresh grass", become_stomped_grass, 111, False)
baseTree = BaseTile("tree", become_stomped_grass, 222, False)
baseStompedGrass = BaseTile("stomped grass", become_stomped_grass, 888, False)
bases = {111: baseFreshGrass, 222: baseTree, 888: baseStompedGrass}

#Calls
hero = Explorer()
game_loop(hero)


'''
Feature Ideas
-tile objects: tentative tile philosophy => tile objects are immutable, but user interaction can change which class of tiles, a square belongs to; a tree tile can become a stump tile, and the tile id # will change as well. all tile attributes will be unchanging because the tile as a whole should be unchanging. a tile interaction should take in a tile, the player, and return a new tile identity; eg fresh grass => stomped grass | how will changed tiles be saved?
-coordinate system
-block patterns
-refactoring
-wrap around map
-game objective
-external rooms













Project Ideas
-image cropper
-snake
'''

