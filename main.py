import pygame
import random
import sys
import time

def make_grid():
	grid = [0 for _ in range(max(0, (MAP_WIDTH*MAP_HEIGHT) - STARTING_MINES))] + [-1 for _ in range(min(MAP_WIDTH * MAP_HEIGHT, STARTING_MINES))]
	random.shuffle(grid)
	grid = [grid[i*MAP_WIDTH:(i+1)*MAP_WIDTH] for i in range(MAP_HEIGHT)]

	grid = update_numbers_on_tiles(grid)

	return grid

def update_numbers_on_tiles(grid):
	for y in range(MAP_HEIGHT):
		for x in range(MAP_WIDTH):
			if grid[y][x] != -1:
				count = 0
				for i in range(-1, 2):
					for j in range(-1, 2):
						if x+i > -1 and x+i < MAP_WIDTH:
							if y+j > -1 and y+j < MAP_HEIGHT:
								if grid[y+j][x+i] == -1:
									count += 1
				grid[y][x] = count
	return grid

def make_visible_grid():
	return [[False for i in range(MAP_WIDTH)] for i in range(MAP_HEIGHT)]

def make_flag_grid():
	return [[False for i in range(MAP_WIDTH)] for i in range(MAP_HEIGHT)]

def get_clicked():
	x, y = pygame.mouse.get_pos()
	clicked = (x // TILE_SIZE, y // TILE_SIZE)
	return clicked

def first_uncover(grid, visible_grid, flag_grid, pos):
	x, y = pos

	bombs_missing = 0
	for i in range(-1, 2):
		for j in range(-1, 2):
			if x+i > -1 and x+i < MAP_WIDTH:
				if y+j > -1 and y+j < MAP_HEIGHT:
					if grid[y+j][x+i] == -1:
						grid[y+j][x+i] = 0
						bombs_missing += 1

	aviable = get_aviable_positions(grid, pos)

	while aviable and bombs_missing:
		x, y = aviable.pop(random.randint(0, len(aviable)-1))
		grid[y][x] = -1
		bombs_missing -= 1

	update_numbers_on_tiles(grid)

	uncover(grid, visible_grid, flag_grid, pos)

def get_aviable_positions(grid, pos=(-10,-10)):
	positions = []

	for i in range(MAP_WIDTH):
		for j in range(MAP_HEIGHT):
			if grid[j][i] != -1:
				if not (abs(i-pos[0]) <= 1 or abs(j-pos[1]) <= 1):
					positions.append((i, j))

	return positions

def valid_to_uncover(visible_grid, pos):
	if sum([sum(row) for row in visible_grid]) == 0:
		return True

	x, y = pos

	if not visible_grid[y][x]:
		if   y != 0 and visible_grid[y-1][x]:
			return True
		if   y != MAP_HEIGHT-1 and visible_grid[y+1][x]:
			return True
		if   x != 0 and visible_grid[y][x-1]:
			return True
		if   x != MAP_WIDTH-1 and visible_grid[y][x+1]:
			return True

		if   y != 0 and visible_grid[y-1][x-1]:
			return True
		if   y != MAP_HEIGHT-1 and visible_grid[y-1][x+1]:
			return True
		if   x != 0 and visible_grid[y+1][x-1]:
			return True
		if   x != MAP_WIDTH-1 and visible_grid[y+1][x+1]:
			return True

	return False

def uncover(grid, visible_grid, flag_grid, pos):
	if valid_to_uncover(visible_grid, pos):
		x, y = pos

		flag_grid[y][x] = False
		visible_grid[y][x] = True

		if grid[y][x] == -1:
			grid[y][x] = -2
			enter_final(grid, screen, NUMBERS_IMAGES)

		if MAP_WIDTH*MAP_HEIGHT - sum([sum(row) for row in visible_grid]) == STARTING_MINES:
			current_time = time.time()
			enter_win_final(screen, startint_time, current_time)

		if grid[y][x] == 0:
			uncover_surroundings(grid, visible_grid, flag_grid, pos)

def uncover_surroundings(grid, visible_grid, flag_grid, pos):
	x, y = pos

	for i in range(-1, 2):
		for j in range(-1, 2):
			if x+i > -1 and x+i < MAP_WIDTH:
				if y+j > -1 and y+j < MAP_HEIGHT:
					new_pos = (x+i, y+j)
					uncover(grid, visible_grid, flag_grid, new_pos)

def uncover_surroundings_no_flags(grid, visible_grid, flag_grid, pos):
	x, y = pos

	for i in range(-1, 2):
		for j in range(-1, 2):
			if x+i > -1 and x+i < MAP_WIDTH:
				if y+j > -1 and y+j < MAP_HEIGHT:
					if not flag_grid[y+j][x+i]:
						new_pos = (x+i, y+j)
						uncover(grid, visible_grid, flag_grid, new_pos)


def put_flag(visible_grid, flag_grid, pos, last_placed_flag_time):
	if time.time() - last_placed_flag_time < 0.2:
		return last_placed_flag_time

	x, y = pos

	if not visible_grid[y][x]:
		flag_grid[y][x] = not flag_grid[y][x]

	return time.time()

def draw(grid, visible_grid, flag_grid, screen, NUMBERS_IMAGES, COVERED_IMAGE, FLAG_IMAGE):
	for j in range(MAP_HEIGHT):
		for i in range(MAP_WIDTH):
			offset = (i*TILE_SIZE, j*TILE_SIZE)

			if visible_grid[j][i]:
				screen.blit(NUMBERS_IMAGES[grid[j][i]], offset)
			else:
				if flag_grid[j][i]:
					screen.blit(FLAG_IMAGE, offset)
				else:
					screen.blit(COVERED_IMAGE, offset)

def enter_final(grid, screen, NUMBERS_IMAGES):
	draw_final(grid, screen, NUMBERS_IMAGES)
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					restart(grid, visible_grid, flag_grid, startint_time)
					return

def draw_final(grid, screen, NUMBERS_IMAGES):
	screen.fill(DARK_GRAY)
	for j in range(MAP_HEIGHT):
		for i in range(MAP_WIDTH):
			offset = (i*TILE_SIZE, j*TILE_SIZE)
			screen.blit(NUMBERS_IMAGES[grid[j][i]], offset)
	pygame.display.update()

def enter_win_final(screen, startint_time, current_time):
	time = current_time - startint_time
	draw_win_final(screen, time)

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					restart(grid, visible_grid, flag_grid, startint_time)
					return

def draw_win_final(screen, time):
	ms = int((time - int(time))*100)
	mins, secs = divmod(int(time), 60)

	pygame.font.init()

	fuente = pygame.font.SysFont("monospace", 100)
	text1 = str(mins) + ":" + str(secs)
	label1 = fuente.render(text1, 1, BLACK)

	fuente = pygame.font.SysFont("monospace", 60)
	text2 = "." + str(ms)
	label2 = fuente.render(text2, 1, BLACK)

	screen.fill(LIGHT_GRAY)

	screen.blit(label1, (0, 0))
	screen.blit(label2, (label1.get_rect()[2], label1.get_rect()[3] - label2.get_rect()[3]))

	pygame.display.update()

def restart(grid, visible_grid, flag_grid, startint_time):
	temp_grid = make_grid()
	for i in range(len(grid)):
		grid[i] = temp_grid[i]
	del temp_grid
	
	for i in range(len(visible_grid)):
		visible_grid[i] = [False for _ in range(len(visible_grid[i]))]

	for i in range(len(flag_grid)):
		flag_grid[i] = [False for _ in range(len(flag_grid[i]))]

	startint_time = time.time()

def get_image_by_position_on_sheet(x, y):
	x_offset = - 16 * x
	y_offset = - 16 * y

	surface = pygame.Surface((16,16))
	surface.blit(SPRITES, (x_offset, y_offset))

	surface = pygame.transform.scale(surface, (TILE_SIZE, TILE_SIZE))

	return surface

def get_number_image(number):
	if number == 0:
		return get_image_by_position_on_sheet(1, 0)

	return get_image_by_position_on_sheet(number-1, 1)
def get_covered_image():
	return get_image_by_position_on_sheet(0, 0)
def get_flag_image():
	return get_image_by_position_on_sheet(2, 0)
def get_bomb_image():
	return get_image_by_position_on_sheet(5, 0)
def get_red_bomb_image():
	return get_image_by_position_on_sheet(6, 0)


# Controls
# Left click to uncover
# Press mouse wheel to uncover nearby tiles
# Right click to put down flags
# When a game is over (win or loose), press space to restart

# Constants
MAP_WIDTH, MAP_HEIGHT = 30, 20
TILE_SIZE = 40
STARTING_MINES = 100

SCREEN_WIDTH, SCREEN_HEIGHT = MAP_WIDTH*TILE_SIZE, MAP_HEIGHT*TILE_SIZE

SPRITES = pygame.image.load("tiles.png")
NUMBERS_IMAGES = [get_number_image(i) for i in range(9)] + [get_red_bomb_image(), get_bomb_image()]
FLAG_IMAGE = get_flag_image()
COVERED_IMAGE = get_covered_image()

# Colors
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
DARK_GRAY = (50,50,50)
GRAY = (128,128,128)
LIGHT_GRAY = (200,200,200)

if __name__ == "__main__":
	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
	pygame.display.set_caption("Minesweeper")
	clock = pygame.time.Clock()

	grid = make_grid()
	visible_grid = make_visible_grid()
	flag_grid = make_flag_grid()

	last_placed_flag_time = time.time()

	startint_time = time.time()

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()

		if pygame.mouse.get_pressed()[0]:  # Left (uncover)
			if sum([sum(row) for row in visible_grid]) == 0:
				first_uncover(grid, visible_grid, flag_grid, get_clicked())
			else:
				uncover(grid, visible_grid, flag_grid, get_clicked())

		if pygame.mouse.get_pressed()[1]:  # Middle (uncover surroundings)
			pos = x, y = get_clicked()
			if visible_grid[y][x]:
				uncover_surroundings_no_flags(grid, visible_grid, flag_grid, pos)

		if pygame.mouse.get_pressed()[2]:  # Right (flag)
			if not sum([sum(row) for row in visible_grid]) == 0:
				last_placed_flag_time = put_flag(visible_grid, flag_grid, get_clicked(), last_placed_flag_time)

		screen.fill(DARK_GRAY)
		draw(grid, visible_grid, flag_grid, screen, NUMBERS_IMAGES, COVERED_IMAGE, FLAG_IMAGE)

		pygame.display.update()
		clock.tick(60)
