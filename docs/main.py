import pygame
import asyncio
import random

#初始化遊戲、FPS設定
pygame.init()
snake_speed = 15
fps = pygame.time.Clock()

#遊戲狀態
game_state = 'instruction'  # 'instruction' or 'playing'
dragging_slider = False

#視窗尺寸與設定
screen_width = 720
screen_height = 480
pygame.display.set_caption('Pygame Snakes')
screen = pygame.display.set_mode((screen_width, screen_height))

#定義顏色變數
black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)

#角色預設位置
snake_position = [100, 50]

#角色身體預設位置
snake_body = [[100, 50],
			[90, 50],
			[80, 50],
			[70, 50]
			]
#食物預設位置
fruit_position = [random.randrange(1, (screen_width//10)) * 10, 
				random.randrange(1, (screen_height//10)) * 10]

fruit_spawn = True

#設定預設方向
direction = 'RIGHT'
change_to = direction

#初始分數
score = 0

#顯示即時分數
def show_score(color, font, size):
	#設置分數字體
	score_font = pygame.font.SysFont(font, size)
	
	# 設置分數顯示內容
	score_box = score_font.render('Score : ' + str(score), True, color)	

	#顯示文字
	screen.blit(score_box, (10, 10))

#顯示指令面板
async def show_instruction_panel():
	global game_state, snake_speed, dragging_slider
	
	# 繪製背景
	screen.fill(black)
	
	# 繪製中央面板
	panel_width = 500
	panel_height = 400
	panel_x = (screen_width - panel_width) // 2
	panel_y = (screen_height - panel_height) // 2
	panel_color = pygame.Color(40, 40, 40)
	pygame.draw.rect(screen, panel_color, pygame.Rect(panel_x, panel_y, panel_width, panel_height))
	pygame.draw.rect(screen, white, pygame.Rect(panel_x, panel_y, panel_width, panel_height), 3)
	
	# 標題
	title_font = pygame.font.SysFont('times new roman', 60)
	title_text = title_font.render('Snake Game', True, green)
	title_rect = title_text.get_rect(center=(screen_width//2, panel_y + 50))
	screen.blit(title_text, title_rect)
	
	# 指令文字
	instruction_font = pygame.font.SysFont('times new roman', 28)
	instructions = [
		'Use Arrow Keys to Move',
		'Eat the white fruit',
		'Avoid walls and your body'
	]
	
	y_offset = panel_y + 120
	for instruction in instructions:
		text = instruction_font.render(instruction, True, white)
		text_rect = text.get_rect(center=(screen_width//2, y_offset))
		screen.blit(text, text_rect)
		y_offset += 40
	
	# 速度滑桿
	slider_y = panel_y + 260
	slider_label_font = pygame.font.SysFont('times new roman', 24)
	slider_label = slider_label_font.render(f'Speed: {snake_speed}', True, white)
	slider_label_rect = slider_label.get_rect(center=(screen_width//2, slider_y))
	screen.blit(slider_label, slider_label_rect)
	
	# 滑桿設定
	slider_x = panel_x + 100
	slider_y_bar = slider_y + 30
	slider_width = 300
	slider_height = 10
	min_speed = 15
	max_speed = 30
	
	# 繪製滑桿背景
	pygame.draw.rect(screen, pygame.Color(100, 100, 100), 
					pygame.Rect(slider_x, slider_y_bar, slider_width, slider_height))
	
	# 繪製已填充部分
	filled_width = ((snake_speed - min_speed) / (max_speed - min_speed)) * slider_width
	pygame.draw.rect(screen, green, 
					pygame.Rect(slider_x, slider_y_bar, filled_width, slider_height))
	
	# 繪製滑桿手柄
	handle_x = slider_x + filled_width
	handle_y = slider_y_bar + slider_height // 2
	pygame.draw.circle(screen, white, (int(handle_x), int(handle_y)), 12)
	
	# 處理滑桿拖曳
	mouse_pos = pygame.mouse.get_pos()
	mouse_pressed = pygame.mouse.get_pressed()[0]
	
	if mouse_pressed:
		if (slider_x <= mouse_pos[0] <= slider_x + slider_width and 
			slider_y_bar - 15 <= mouse_pos[1] <= slider_y_bar + slider_height + 15):
			dragging_slider = True
	else:
		dragging_slider = False
	
	if dragging_slider:
		relative_pos = max(0, min(slider_width, mouse_pos[0] - slider_x))
		snake_speed = int(min_speed + (relative_pos / slider_width) * (max_speed - min_speed))
	
	# START 按鈕
	button_width = 200
	button_height = 50
	button_x = (screen_width - button_width) // 2
	button_y = panel_y + 330
	button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
	
	# 檢查滑鼠懸停
	button_color = green if button_rect.collidepoint(mouse_pos) else pygame.Color(0, 180, 0)
	
	# 繪製按鈕
	pygame.draw.rect(screen, button_color, button_rect)
	pygame.draw.rect(screen, white, button_rect, 3)
	
	# 按鈕文字
	button_font = pygame.font.SysFont('times new roman', 36)
	button_text = button_font.render('START', True, white)
	button_text_rect = button_text.get_rect(center=button_rect.center)
	screen.blit(button_text, button_text_rect)
	
	# 檢查按鈕點擊
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			return False
		if event.type == pygame.MOUSEBUTTONDOWN:
			if button_rect.collidepoint(event.pos):
				game_state = 'playing'
	
	pygame.display.update()
	return True

#遊戲結束
async def game_over():
	my_font = pygame.font.SysFont('times new roman', 50)
	
	# creating a text surface on which text 
	game_over_surface = my_font.render('Your Score is : ' + str(score), True, red)
	
	# create a rectangular object for the text 
	# surface object
	game_over_rect = game_over_surface.get_rect()
	
	# setting position of the text
	game_over_rect.midtop = (screen_width/2, screen_height/4)
	
	# blit will draw the text on screen
	screen.blit(game_over_surface, game_over_rect)
	pygame.display.flip()
	
	# after 2 seconds we will quit the program
	await asyncio.sleep(2)
	
	# deactivating pygame library
	pygame.quit()
	
	# quit the program
	return False


# Main Function
async def main():
	global game_state, direction, change_to, snake_position, snake_body, fruit_position, fruit_spawn, score
	
	running = True
	while running:
		# Show instruction panel if game not started
		if game_state == 'instruction':
			running = await show_instruction_panel()
			fps.tick(30)
			await asyncio.sleep(0)  # Yield control to browser
			continue
		
		# Game playing mode
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_UP:
					change_to = 'UP'
				if event.key == pygame.K_DOWN:
					change_to = 'DOWN'
				if event.key == pygame.K_LEFT:
					change_to = 'LEFT'
				if event.key == pygame.K_RIGHT:
					change_to = 'RIGHT'
					
			if event.type == pygame.QUIT:
				running = False

		# If two keys pressed simultaneously we don't want snake to move into two directions
		if change_to == 'UP' and direction != 'DOWN':
			direction = 'UP'
		if change_to == 'DOWN' and direction != 'UP':
			direction = 'DOWN'
		if change_to == 'LEFT' and direction != 'RIGHT':
			direction = 'LEFT'
		if change_to == 'RIGHT' and direction != 'LEFT':
			direction = 'RIGHT'

		#移動
		if direction == 'UP':
			snake_position[1] -= 10
		if direction == 'DOWN':
			snake_position[1] += 10
		if direction == 'LEFT':
			snake_position[0] -= 10
		if direction == 'RIGHT':
			snake_position[0] += 10

		# Snake body growing mechanism: if fruits and snakes collide then scores will be incremented by 10
		snake_body.insert(0, list(snake_position))
		if snake_position[0] == fruit_position[0] and snake_position[1] == fruit_position[1]:
			score += 10
			fruit_spawn = False
		else:
			snake_body.pop()
			
		if not fruit_spawn:
			fruit_position = [random.randrange(1, (screen_width//10)) * 10, 
							random.randrange(1, (screen_height//10)) * 10]
			
		fruit_spawn = True
		screen.fill(black)
		
		for pos in snake_body:
			pygame.draw.rect(screen, green,
							pygame.Rect(pos[0], pos[1], 10, 10))
		pygame.draw.rect(screen, white, pygame.Rect(
			fruit_position[0], fruit_position[1], 10, 10))

		# Game Over conditions
		if snake_position[0] < 0 or snake_position[0] > screen_width-10:
			running = await game_over()
		if snake_position[1] < 0 or snake_position[1] > screen_height-10:
			running = await game_over()

		# Touching the snake body
		for block in snake_body[1:]:
			if snake_position[0] == block[0] and snake_position[1] == block[1]:
				running = await game_over()

		# displaying score continuously
		show_score(white, 'times new roman', 20)

		# Refresh game screen
		pygame.display.update()

		# Frame Per Second /Refresh Rate
		fps.tick(snake_speed)
		
		# Yield control to browser (critical for Pygbag)
		await asyncio.sleep(0)

# Run the game
asyncio.run(main())
