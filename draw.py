import pygame.transform as pytr
import pygame.image as pyim
import pygame.font as pyfont

#Renders integer matrix
def draw_mat(int_mat, sources, screen, back_col, square_width):

	#Returns Rect, given source & position
	def get_rect(source, posx, posy):
		return source.get_rect().move(posx, posy)

	#Converts integer matrix to tile matrix
	def tilify_mat(intM, sources):
		square_matrix = []
		for i in range(len(intM)):
			square_row = []
			for j in range(len(intM[0])):
				int_key = intM[i][j]
				item_source = sources[int_key]
				item = get_rect(item_source, j * square_width, i * square_width)
				square_row.append((item_source, item))
			square_matrix.append(square_row)
		return square_matrix

	#Actual Rendering
	screen.fill(back_col)
	tile_mat = tilify_mat(int_mat, sources)
	for row in tile_mat:
		for source, obj in row:
			screen.blit(source, obj)

def draw_output(screen, messages, font_obj):
	#White Background
	source = pytr.scale(pyim.load("white.png"), (480, 120))
	screen.blit(source, source.get_rect().move(0, 480))
	#Text rendering
	for i in range(min(5, len(messages))):
		message = str(messages[::-1][i])
		if i == 0:
			col = (0,0,0)
		else:
			col = (140, 140, 140)
		textsurface = font_obj.render(message, True, col)
		screen.blit(textsurface,(10, 490 + i * 17))

def draw_input(screen, text, clear, font_obj):
	source = pytr.scale(pyim.load("offwhite.png"), (480, 30))
	screen.blit(source, source.get_rect().move(0, 600))
	if clear:
		text = ""
	#Text rendering
	textsurface = font_obj.render(str(text), True, (20, 20, 20))
	screen.blit(textsurface,(10, 605))