import pygame
import random

# Initialize pygame
pygame.init()

# Game settings
WIDTH = 600
HEIGHT = 400
BLOCK_SIZE = 20
SPEED = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Setup screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Snake Game')
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Game variables
snake = [[WIDTH // 2, HEIGHT // 2]]  # Snake starts in center
direction = 'RIGHT'
food = [random.randrange(0, WIDTH, BLOCK_SIZE), random.randrange(0, HEIGHT, BLOCK_SIZE)]
score = 0
game_over = False

# Main game loop - keeps running until player closes window
running = True
while running:
    
    # STEP 1: Check what player is doing
    for event in pygame.event.get():
        # Did player close window?
        if event.type == pygame.QUIT:
            running = False
        
        # Did player press a key?
        if event.type == pygame.KEYDOWN:
            # Change direction (only if game is not over)
            if not game_over:
                if event.key == pygame.K_UP and direction != 'DOWN':
                    direction = 'UP'
                if event.key == pygame.K_DOWN and direction != 'UP':
                    direction = 'DOWN'
                if event.key == pygame.K_LEFT and direction != 'RIGHT':
                    direction = 'LEFT'
                if event.key == pygame.K_RIGHT and direction != 'LEFT':
                    direction = 'RIGHT'
            
            # Restart game if R is pressed after game over
            if event.key == pygame.K_r and game_over:
                snake = [[WIDTH // 2, HEIGHT // 2]]
                direction = 'RIGHT'
                food = [random.randrange(0, WIDTH, BLOCK_SIZE), random.randrange(0, HEIGHT, BLOCK_SIZE)]
                score = 0
                game_over = False
    
    # STEP 2: Update game (only if not game over)
    if not game_over:
        # Get current head position
        head_x = snake[0][0]
        head_y = snake[0][1]
        
        # Calculate new head position based on direction
        if direction == 'UP':
            new_head = [head_x, head_y - BLOCK_SIZE]
        elif direction == 'DOWN':
            new_head = [head_x, head_y + BLOCK_SIZE]
        elif direction == 'LEFT':
            new_head = [head_x - BLOCK_SIZE, head_y]
        else:  # RIGHT
            new_head = [head_x + BLOCK_SIZE, head_y]
        
        # Add new head to front of snake
        snake.insert(0, new_head)
        
        # Did snake eat food?
        if new_head == food:
            score += 1
            # Create new food at random position
            food = [random.randrange(0, WIDTH, BLOCK_SIZE), random.randrange(0, HEIGHT, BLOCK_SIZE)]
        else:
            # Remove tail (snake doesn't grow)
            snake.pop()
        
        # Check if snake hit wall
        if new_head[0] < 0 or new_head[0] >= WIDTH:
            game_over = True
        if new_head[1] < 0 or new_head[1] >= HEIGHT:
            game_over = True
        
        # Check if snake hit itself
        if new_head in snake[1:]:
            game_over = True
    
    # STEP 3: Draw everything on screen
    screen.fill(BLACK)  # Clear screen with black
    
    # Draw snake (each segment)
    for segment in snake:
        pygame.draw.rect(screen, GREEN, [segment[0], segment[1], BLOCK_SIZE, BLOCK_SIZE])
    
    # Draw food
    pygame.draw.rect(screen, RED, [food[0], food[1], BLOCK_SIZE, BLOCK_SIZE])
    
    # Draw score at top left
    score_text = font.render(f'Score: {score}', True, WHITE)
    screen.blit(score_text, [10, 10])
    
    # Show game over message if game ended
    if game_over:
        game_over_text = font.render('GAME OVER! Press R to restart', True, RED)
        text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(game_over_text, text_rect)
    
    # Update display and control speed
    pygame.display.flip()
    clock.tick(SPEED)

pygame.quit()
