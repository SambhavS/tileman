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
back_col = (70, 200, 160)
square_width = 30
tiles_wide = width // square_width
tiles_high = height // square_width
dimensions = [tiles_wide, tiles_high]
square_size = (square_width, square_width)
screen = display.set_mode(size)
#Populate sources
sources = {}
ordered_filenames = ["heroU.png","heroL.png","heroD.png","heroR.png","green.png","tree.png"]
for i, filename in enumerate(ordered_filenames):
	sources[i] = pytr.scale(pyim.load(filename), square_size)

######Tools######
## Block & Block matrix tools
def random_seed_fill(a, b):
	return fill2Dmat(a, b, lambda x, y: random.randrange(500000))
def empty_block():
	return empty_mat(BLOCK_WIDTH, BLOCK_WIDTH)
def empty_block_mat():
	return fill2Dmat(SHOW_BLOCKS + 2, SHOW_BLOCKS + 2, lambda x, y: empty_block())
def rand_block(rand_obj):
	#VOLATILE RANDOMNESS (check rand_mat)
	return rand_mat(BLOCK_WIDTH, BLOCK_WIDTH, rand_obj)
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
	block_mat = gen_mat(y_range[0], y_range[1], x_range[0], x_range[1], seed_mat, lambda a, b, i0, i1, j0, j1, seed_mat: rand_block(seed_mat[a][b]))
	return to_BImat(block_mat)

#####Game Logic#####
#Initializations
seed_mat = random_seed_fill(500, 500)
y_range = [0, 6]
x_range = [0, 6]
show_posy = [4, 20]
show_posx = [4, 20]
BImat = new_BImat()
show_mat = get_showable(BImat, 10, 10, 2)

#Functions
def tile_hero_interaction(block_x, block_y, tile, i, j, hero, BImat_i, BImat_j):
	#tile identities must be between 100 and 999
	block_id = seed_mat[block_x][block_y]
	pos = i * BLOCK_WIDTH + j
	tile_id = (block_id//(100**pos))%1000
	new_tile_id = tile.interact(hero)
	BImat[BImat_i][BImat_j] = new_tile_id
	delta_id = new_tile_id - tile_id
	seed_mat[block_x][block_y] += delta_id*(100**pos)

#Classes
class tileman:
	def __init__(self):
		###Movement Variables###
		self.x = 10
		self.y = 10
		#Up, Left, Down, Right
		self.counts = [0,0,0,0]
		#minY, minX, maxY, maxX
		self.edges = [2,2,13,13]

	def move(self, direction):
		global BImat
		global show_mat

		direction = direction.lower()
		if direction == "u":
			delX, delY, count_ind, show_range, block_range = 0,  1, 0, show_posy, y_range
		elif direction == "l":
			delX, delY, count_ind, show_range, block_range = 1, 0, 1, show_posx, x_range
		elif direction == "d":
			delX, delY, count_ind, show_range, block_range = 0, -1, 2, show_posy, y_range
		elif direction == "r":
			delX, delY, count_ind, show_range, block_range = -1,  0, 3, show_posx, x_range
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
				y_range[i] -= delY
				x_range[i] -= delX
			for i in range(len(show_range)):
				direction = max(delX, delY, key = lambda a: abs(a))
				show_range[i] += BLOCK_WIDTH * direction
			BImat = new_BImat()
		show_mat = get_showable(BImat, self.x, self.y, count_ind)
			

#####Main#####
#Function Definitions
def key_manager(keys, move_ticker, hero):
	if move_ticker:
		move_ticker -= 1
	else:
		move_ticker = 7
		if keys[K_LEFT]:
			hero.move('l')
		elif keys[K_RIGHT]:
			hero.move('r')
		elif keys[K_UP]:
			hero.move('u')
		elif keys[K_DOWN]:
			hero.move('d')
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

#Calls
hero = tileman()
game_loop(hero)

'''
Feature Ideas
-tile objects: tentative tile philosophy => tile objects are immutable, but user interaction can change which class of tiles, a square belongs to; a tree tile can become a stump tile, and the tile id # will change as well. all tile attributes will be unchanging because the tile as a whole should be unchanging. a tile interaction should take in a tile, the player, and return a new tile identity; eg fresh grass => stomped grass | how will changed tiles be saved?
-block patterns
-refactoring
-game objective
-external rooms













Project Ideas
-image cropper
-snake
'''

