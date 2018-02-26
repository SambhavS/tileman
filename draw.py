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