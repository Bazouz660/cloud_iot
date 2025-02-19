import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Set up the window dimensions
window_width = 800
window_height = 600
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Snake Game")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Snake and food settings
snake_block = 20
snake_speed = 15

# Initialize clock
clock = pygame.time.Clock()

# Font for score display
font = pygame.font.SysFont(None, 50)

def our_snake(snake_block, snake_list):
    """Draw the snake on the screen."""
    for x in snake_list:
        pygame.draw.rect(window, GREEN, [x[0], x[1], snake_block, snake_block])

def get_food(snake_list, snake_block):
    """Generate food at a random position not occupied by the snake."""
    food = [round(random.randrange(0, window_width - snake_block) / snake_block) * snake_block,
            round(random.randrange(0, window_height - snake_block) / snake_block) * snake_block]
    while food in snake_list:
        food = [round(random.randrange(0, window_width - snake_block) / snake_block) * snake_block,
                round(random.randrange(0, window_height - snake_block) / snake_block) * snake_block]
    return food

def gameLoop():
    """Main game loop."""
    game_over = False
    game_close = False

    x1 = window_width / 4
    y1 = window_height / 4

    x1_change = 0
    y1_change = 0

    snake_List = []
    Length_of_snake = 1

    food = get_food(snake_List, snake_block)

    while not game_over:
        while game_close:
            window.fill(BLACK)
            show_message = font.render("You Lost! Press Q-Quit or C-Play Again", True, RED)
            window.blit(show_message, [window_width/6, window_height/3])
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x1_change = -snake_block
                    y1_change = 0
                elif event.key == pygame.K_RIGHT:
                    x1_change = snake_block
                    y1_change = 0
                elif event.key == pygame.K_UP:
                    y1_change = -snake_block
                    x1_change = 0
                elif event.key == pygame.K_DOWN:
                    y1_change = snake_block
                    x1_change = 0

        if x1 >= window_width or x1 < 0 or y1 >= window_height or y1 < 0:
            game_close = True

        x1 += x1_change
        y1 += y1_change
        window.fill(BLACK)
        pygame.draw.rect(window, RED, [food[0], food[1], snake_block, snake_block])
        
        snake_Head = []
        snake_Head.append(x1)
        snake_Head.append(y1)
        snake_List.append(snake_Head)
        
        if len(snake_List) > Length_of_snake:
            del snake_List[0]

        for hit in snake_List[:-1]:
            if hit == snake_Head:
                game_close = True

        our_snake(snake_block, snake_List)
        pygame.display.update()

        if x1 == food[0] and y1 == food[1]:
            food = get_food(snake_List, snake_block)
            Length_of_snake += 1

        clock.tick(snake_speed)

    pygame.quit()
    quit()

# Start the game
gameLoop()