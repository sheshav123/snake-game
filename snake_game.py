import pygame
import pygame_gui
import random
import time
import sys
import json
import os
from enum import Enum, auto
from typing import List, Tuple, Optional, Dict, Any

# Initialize pygame and mixer
pygame.init()
pygame.mixer.init()

# Constants
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
GRID_SIZE = 24
GRID_WIDTH = 30  # Will be adjusted based on window size
GRID_HEIGHT = 20  # Will be adjusted based on window size
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (255, 50, 50)
BLUE = (0, 100, 255)
DARK_GREEN = (0, 150, 0)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
DARK_BLUE = (0, 0, 100)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
BRONZE = (205, 127, 50)

# Game states
class GameState(Enum):
    MAIN_MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    HIGH_SCORES = auto()
    DIFFICULTY_SELECT = auto()

# Difficulty levels
class Difficulty(Enum):
    EASY = {"name": "Easy", "speed": 8, "grid_size": 24, "score_multiplier": 1}
    MEDIUM = {"name": "Medium", "speed": 12, "grid_size": 20, "score_multiplier": 2}
    HARD = {"name": "Hard", "speed": 18, "grid_size": 16, "score_multiplier": 3}

# High score file
HIGH_SCORE_FILE = "high_scores.json"

# Directions
class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    NONE = (0, 0)  # For when the game is not moving

class SnakeGame:
    def __init__(self):
        # Initialize display
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption('Snake Game - Enhanced')
        
        # Initialize UI manager
        self.ui_manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT), 'theme.json')
        
        # Game state
        self.state = GameState.MAIN_MENU
        self.difficulty = Difficulty.MEDIUM
        self.high_scores = self.load_high_scores()
        
        # UI elements
        self.buttons = {}
        self.create_ui_elements()
        
        # Game variables (will be initialized in reset_game)
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.SysFont('Arial', 64, bold=True)
        self.font_medium = pygame.font.SysFont('Arial', 36, bold=True)
        self.font_small = pygame.font.SysFont('Arial', 24)
        
        # Sound effects
        self.sounds = {
            'eat': self.load_sound('eat.wav'),
            'game_over': self.load_sound('game_over.wav'),
            'menu_select': self.load_sound('menu_select.wav')
        }
        
        # Initialize game
        self.reset_game()
    
    def load_sound(self, filename):
        """Load a sound file, return None if not found"""
        try:
            sound = pygame.mixer.Sound(f'sounds/{filename}')
            sound.set_volume(0.5)
            return sound
        except:
            # Return a silent sound if file not found
            sound = pygame.mixer.Sound(buffer=bytes([128] * 1000))
            sound.set_volume(0)
            return sound
    
    def create_ui_elements(self):
        """Create all UI elements for the game"""
        button_width = 300
        button_height = 60
        center_x = WINDOW_WIDTH // 2 - button_width // 2
        
        # Main menu buttons
        self.buttons['new_game'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((center_x, 250), (button_width, button_height)),
            text='New Game',
            manager=self.ui_manager,
            object_id='#new_game_btn',
            visible=False
        )
        
        self.buttons['continue_game'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((center_x, 330), (button_width, button_height)),
            text='Continue',
            manager=self.ui_manager,
            object_id='#continue_btn',
            visible=False
        )
        
        self.buttons['high_scores'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((center_x, 410), (button_width, button_height)),
            text='High Scores',
            manager=self.ui_manager,
            object_id='#high_scores_btn',
            visible=False
        )
        
        self.buttons['quit'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((center_x, 490), (button_width, button_height)),
            text='Quit',
            manager=self.ui_manager,
            object_id='#quit_btn',
            visible=False
        )
        
        # Difficulty selection buttons
        self.buttons['easy'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((center_x, 300), (button_width, button_height)),
            text='Easy',
            manager=self.ui_manager,
            object_id='#easy_btn',
            visible=False
        )
        
        self.buttons['medium'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((center_x, 380), (button_width, button_height)),
            text='Medium',
            manager=self.ui_manager,
            object_id='#medium_btn',
            visible=False
        )
        
        self.buttons['hard'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((center_x, 460), (button_width, button_height)),
            text='Hard',
            manager=self.ui_manager,
            object_id='#hard_btn',
            visible=False
        )
        
        self.buttons['back'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((center_x, 540), (button_width, button_height)),
            text='Back',
            manager=self.ui_manager,
            object_id='#back_btn',
            visible=False
        )
        
        # In-game buttons
        self.buttons['pause'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((WINDOW_WIDTH - 120, 20), (100, 40)),
            text='Pause',
            manager=self.ui_manager,
            object_id='#pause_btn',
            visible=False
        )
        
        # Pause menu buttons
        self.buttons['resume'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((center_x, 300), (button_width, button_height)),
            text='Resume',
            manager=self.ui_manager,
            object_id='#resume_btn',
            visible=False
        )
        
        # Game over buttons
        self.buttons['play_again'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((center_x - 160, 450), (button_width, button_height)),
            text='Play Again',
            manager=self.ui_manager,
            object_id='#play_again_btn',
            visible=False
        )
        
        self.buttons['main_menu'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((center_x + 160, 450), (button_width, button_height)),
            text='Main Menu',
            manager=self.ui_manager,
            object_id='#main_menu_btn',
            visible=False
        )
        
        # High scores back button
        self.buttons['scores_back'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((center_x, 650), (button_width, button_height)),
            text='Back to Menu',
            manager=self.ui_manager,
            object_id='#scores_back_btn',
            visible=False
        )

    def load_high_scores(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load high scores from file or return default if not found"""
        try:
            if os.path.exists(HIGH_SCORE_FILE):
                with open(HIGH_SCORE_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading high scores: {e}")
        
        # Return default high scores if file doesn't exist or there's an error
        return {
            'Easy': [{"name": "Player", "score": 100, "date": "2023-01-01"}],
            'Medium': [{"name": "Player", "score": 200, "date": "2023-01-01"}],
            'Hard': [{"name": "Player", "score": 300, "date": "2023-01-01"}]
        }
    
    def save_high_scores(self):
        """Save high scores to file"""
        try:
            with open(HIGH_SCORE_FILE, 'w') as f:
                json.dump(self.high_scores, f, indent=2)
        except Exception as e:
            print(f"Error saving high scores: {e}")
    
    def add_high_score(self, name: str, score: int):
        """Add a new high score"""
        difficulty = self.difficulty.value['name']
        if difficulty not in self.high_scores:
            self.high_scores[difficulty] = []
        
        # Add new score
        self.high_scores[difficulty].append({
            "name": name,
            "score": score,
            "date": time.strftime("%Y-%m-%d")
        })
        
        # Sort by score (descending) and keep top 10
        self.high_scores[difficulty].sort(key=lambda x: x['score'], reverse=True)
        self.high_scores[difficulty] = self.high_scores[difficulty][:10]
        
        # Save to file
        self.save_high_scores()
    
    def reset_game(self):
        """Reset the game state"""
        # Set up game area based on difficulty
        self.speed = self.difficulty.value['speed']
        self.score_multiplier = self.difficulty.value['score_multiplier']
        
        # Calculate grid dimensions based on window size and difficulty
        self.grid_size = self.difficulty.value['grid_size']
        self.grid_width = (WINDOW_WIDTH - 400) // self.grid_size  # Leave space for UI
        self.grid_height = (WINDOW_HEIGHT - 100) // self.grid_size
        
        # Game state
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.snake = [(self.grid_width // 2, self.grid_height // 2)]
        self.snake.append((self.snake[0][0] - 1, self.snake[0][1]))  # Add initial body segment
        
        # Initialize special food first to avoid reference before assignment
        self.special_food = None
        self.special_food_timer = 0
        
        # Now generate food
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False
        self.paused = False
        self.last_score = 0
        self.food_timer = 0
        
        # Calculate game area position (centered)
        self.game_area_x = (WINDOW_WIDTH - (self.grid_width * self.grid_size)) // 2
        self.game_area_y = 80  # Leave space for score and UI

    def generate_food(self) -> Tuple[int, int]:
        """Generate food at a random position not occupied by the snake"""
        while True:
            food = (random.randint(0, self.grid_width - 1), random.randint(0, self.grid_height - 1))
            if food not in self.snake and (not self.special_food or food != self.special_food[0]):
                return food
    
    def generate_special_food(self):
        """Generate special food that gives bonus points"""
        if not self.special_food and random.random() < 0.2:  # 20% chance to spawn special food
            food_pos = self.generate_food()
            self.special_food = (food_pos, time.time(), 10)  # (position, spawn_time, points)
            self.special_food_timer = time.time()
            return True
        return False

    def handle_events(self):
        time_delta = self.clock.tick(FPS) / 1000.0
        
        for event in pygame.event.get():
            # Handle UI events
            self.ui_manager.process_events(event)
            
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.VIDEORESIZE:
                # Handle window resize
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self.ui_manager.set_window_resolution((event.w, event.h))
                self.update_ui_positions()
            
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    self.handle_button_click(event.ui_element)
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                        self.update_ui_visibility()
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING
                        self.update_ui_visibility()
                    return True
                
                if self.state == GameState.PLAYING and not self.paused and not self.game_over:
                    if event.key == pygame.K_UP and self.direction != Direction.DOWN:
                        self.next_direction = Direction.UP
                    elif event.key == pygame.K_DOWN and self.direction != Direction.UP:
                        self.next_direction = Direction.DOWN
                    elif event.key == pygame.K_LEFT and self.direction != Direction.RIGHT:
                        self.next_direction = Direction.LEFT
                    elif event.key == pygame.K_RIGHT and self.direction != Direction.LEFT:
                        self.next_direction = Direction.RIGHT
                    elif event.key == pygame.K_p:
                        self.state = GameState.PAUSED
                        self.update_ui_visibility()
        
        # Update UI
        self.ui_manager.update(time_delta)
        return True
    
    def handle_button_click(self, button):
        """Handle button clicks from the UI"""
        if button == self.buttons['new_game']:
            self.state = GameState.DIFFICULTY_SELECT
            self.update_ui_visibility()
            
        elif button == self.buttons['continue_game']:
            if self.state == GameState.MAIN_MENU and hasattr(self, 'last_score') and self.last_score > 0:
                self.state = GameState.PLAYING
                self.update_ui_visibility()
            
        elif button == self.buttons['high_scores']:
            self.state = GameState.HIGH_SCORES
            self.update_ui_visibility()
            
        elif button == self.buttons['quit']:
            return False
            
        elif button == self.buttons['easy']:
            self.difficulty = Difficulty.EASY
            self.start_new_game()
            
        elif button == self.buttons['medium']:
            self.difficulty = Difficulty.MEDIUM
            self.start_new_game()
            
        elif button == self.buttons['hard']:
            self.difficulty = Difficulty.HARD
            self.start_new_game()
            
        elif button == self.buttons['back']:
            if self.state == GameState.DIFFICULTY_SELECT:
                self.state = GameState.MAIN_MENU
                self.update_ui_visibility()
                
        elif button == self.buttons['pause']:
            self.state = GameState.PAUSED
            self.update_ui_visibility()
            
        elif button == self.buttons['resume']:
            self.state = GameState.PLAYING
            self.update_ui_visibility()
            
        elif button == self.buttons['play_again']:
            self.start_new_game()
            
        elif button == self.buttons['main_menu'] or button == self.buttons['scores_back']:
            self.state = GameState.MAIN_MENU
            self.update_ui_visibility()
            
        # Play sound effect
        if hasattr(self, 'sounds') and 'menu_select' in self.sounds:
            self.sounds['menu_select'].play()
            
        return True

    def update(self):
        if self.state != GameState.PLAYING or self.game_over:
            return
            
        # Update direction
        self.direction = self.next_direction
        
        # Only move the snake at the appropriate speed
        current_time = time.time()
        if current_time - self.last_update_time < 1.0 / self.speed:
            return
            
        self.last_update_time = current_time
        
        dx, dy = self.direction.value
        
        # Move snake
        head_x, head_y = self.snake[0]
        new_head = ((head_x + dx) % self.grid_width, (head_y + dy) % self.grid_height)
        
        # Check for collision with self
        if new_head in self.snake[1:]:
            self.game_over = True
            self.state = GameState.GAME_OVER
            self.update_ui_visibility()
            
            # Add to high scores if score is high enough
            if self.score > 0:
                difficulty_name = self.difficulty.value['name']
                if (difficulty_name in self.high_scores and 
                    (len(self.high_scores[difficulty_name]) < 10 or 
                     self.score > self.high_scores[difficulty_name][-1]['score'])):
                    # Show high score input dialog
                    self.show_high_score_input()
            
            if hasattr(self, 'sounds') and 'game_over' in self.sounds:
                self.sounds['game_over'].play()
                
            return
        
        self.snake.insert(0, new_head)
        
        # Check if food is eaten
        food_eaten = False
        if new_head == self.food:
            self.score += 1 * self.score_multiplier
            self.food = self.generate_food()
            food_eaten = True
            
            # Play sound effect
            if hasattr(self, 'sounds') and 'eat' in self.sounds:
                self.sounds['eat'].play()
                
            # Chance to spawn special food
            if random.random() < 0.2:  # 20% chance
                self.generate_special_food()
        
        # Check if special food is eaten
        if (self.special_food and 
            new_head[0] == self.special_food[0][0] and 
            new_head[1] == self.special_food[0][1]):
            self.score += self.special_food[2] * self.score_multiplier  # Bonus points
            self.special_food = None
            food_eaten = True
            
            # Play sound effect
            if hasattr(self, 'sounds') and 'eat' in self.sounds:
                self.sounds['eat'].play()
        
        # Remove tail only if no food was eaten
        if not food_eaten:
            self.snake.pop()
        
        # Update special food timer
        if self.special_food:
            if current_time - self.special_food[1] > 10:  # Special food disappears after 10 seconds
                self.special_food = None
        
        # Update food timer
        self.food_timer += 1
        if self.food_timer > 100:  # Move food every 100 frames if not eaten
            self.food = self.generate_food()
            self.food_timer = 0

    def draw(self):
        # Clear screen
        self.screen.fill(BLACK)
        
        # Draw different screens based on game state
        if self.state == GameState.MAIN_MENU:
            self.draw_main_menu()
        elif self.state == GameState.DIFFICULTY_SELECT:
            self.draw_difficulty_select()
        elif self.state == GameState.HIGH_SCORES:
            self.draw_high_scores()
        elif self.state in [GameState.PLAYING, GameState.PAUSED, GameState.GAME_OVER]:
            self.draw_game()
        
        # Draw UI elements
        self.ui_manager.draw_ui(self.screen)
        
        # Update display
        pygame.display.flip()
    
    def draw_main_menu(self):
        """Draw the main menu screen"""
        # Draw title
        title = self.font_large.render('SNAKE GAME', True, GREEN)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        # Draw version/subtitle
        subtitle = self.font_small.render('Enhanced Edition', True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, 220))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Show last score if available
        if hasattr(self, 'last_score') and self.last_score > 0:
            last_score_text = self.font_small.render(
                f'Last Score: {self.last_score} ({self.difficulty.value["name"]})', 
                True, 
                WHITE
            )
            last_score_rect = last_score_text.get_rect(center=(WINDOW_WIDTH // 2, 600))
            self.screen.blit(last_score_text, last_score_rect)
    
    def draw_difficulty_select(self):
        """Draw the difficulty selection screen"""
        # Draw title
        title = self.font_medium.render('Select Difficulty', True, WHITE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 200))
        self.screen.blit(title, title_rect)
    
    def draw_high_scores(self):
        """Draw the high scores screen"""
        # Draw title
        title = self.font_medium.render('HIGH SCORES', True, GOLD)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Draw difficulty tabs
        difficulties = ['Easy', 'Medium', 'Hard']
        tab_width = 200
        tab_height = 50
        tab_y = 160
        
        for i, diff in enumerate(difficulties):
            tab_x = (WINDOW_WIDTH - (len(difficulties) * (tab_width + 10))) // 2 + i * (tab_width + 10)
            
            # Highlight current difficulty
            color = BLUE if diff == self.difficulty.value['name'] else DARK_BLUE
            pygame.draw.rect(self.screen, color, (tab_x, tab_y, tab_width, tab_height))
            pygame.draw.rect(self.screen, WHITE, (tab_x, tab_y, tab_width, tab_height), 2)
            
            # Draw difficulty name
            diff_text = self.font_small.render(diff, True, WHITE)
            diff_rect = diff_text.get_rect(center=(tab_x + tab_width // 2, tab_y + tab_height // 2))
            self.screen.blit(diff_text, diff_rect)
            
            # Handle click on tab
            mouse_pos = pygame.mouse.get_pos()
            mouse_clicked = pygame.mouse.get_pressed()[0]
            
            if (tab_x <= mouse_pos[0] <= tab_x + tab_width and 
                tab_y <= mouse_pos[1] <= tab_y + tab_height):
                if mouse_clicked:
                    self.difficulty = Difficulty[diff.upper()]
                    # Small delay to prevent multiple clicks
                    pygame.time.delay(200)
        
        # Draw high scores for current difficulty
        difficulty_name = self.difficulty.value['name']
        if difficulty_name in self.high_scores:
            y_offset = 240
            
            # Column headers
            header_bg = pygame.Surface((WINDOW_WIDTH - 200, 40))
            header_bg.fill(DARK_BLUE)
            self.screen.blit(header_bg, (100, y_offset - 5))
            
            headers = ['Rank', 'Name', 'Score', 'Date']
            col_widths = [100, 300, 200, 200]
            x_pos = 120
            
            for i, header in enumerate(headers):
                header_text = self.font_small.render(header, True, WHITE)
                self.screen.blit(header_text, (x_pos, y_offset))
                x_pos += col_widths[i]
            
            y_offset += 50
            
            # High score entries
            for i, entry in enumerate(self.high_scores[difficulty_name][:10]):
                # Alternate row colors
                row_color = (40, 40, 40) if i % 2 == 0 else (30, 30, 30)
                pygame.draw.rect(self.screen, row_color, (100, y_offset - 5, WINDOW_WIDTH - 200, 40))
                
                # Rank
                rank = f'{i+1}.'
                rank_text = self.font_small.render(rank, True, WHITE)
                self.screen.blit(rank_text, (120, y_offset))
                
                # Name (truncate if too long)
                name = entry['name'][:15] + '...' if len(entry['name']) > 15 else entry['name']
                name_text = self.font_small.render(name, True, WHITE)
                self.screen.blit(name_text, (220, y_offset))
                
                # Score with color based on rank
                score_color = GOLD if i == 0 else SILVER if i == 1 else BRONZE if i == 2 else WHITE
                score_text = self.font_small.render(str(entry['score']), True, score_color)
                self.screen.blit(score_text, (520, y_offset))
                
                # Date
                date_text = self.font_small.render(entry['date'], True, WHITE)
                self.screen.blit(date_text, (720, y_offset))
                
                y_offset += 45
    
    def draw_game(self):
        """Draw the main game screen"""
        # Draw game area background
        game_area_rect = pygame.Rect(
            self.game_area_x - 10, 
            self.game_area_y - 10, 
            self.grid_width * self.grid_size + 20, 
            self.grid_height * self.grid_size + 20
        )
        pygame.draw.rect(self.screen, (30, 30, 30), game_area_rect)
        pygame.draw.rect(self.screen, BLUE, game_area_rect, 2)
        
        # Draw grid
        for x in range(0, self.grid_width * self.grid_size, self.grid_size):
            pygame.draw.line(
                self.screen, 
                (40, 40, 40), 
                (self.game_area_x + x, self.game_area_y), 
                (self.game_area_x + x, self.game_area_y + self.grid_height * self.grid_size)
            )
        for y in range(0, self.grid_height * self.grid_size, self.grid_size):
            pygame.draw.line(
                self.screen, 
                (40, 40, 40), 
                (self.game_area_x, self.game_area_y + y), 
                (self.game_area_x + self.grid_width * self.grid_size, self.game_area_y + y)
            )
        
        # Draw snake
        for i, (x, y) in enumerate(self.snake):
            # Head is a different color
            if i == 0:
                # Draw head with eyes
                head_rect = pygame.Rect(
                    self.game_area_x + x * self.grid_size + 2, 
                    self.game_area_y + y * self.grid_size + 2, 
                    self.grid_size - 4, 
                    self.grid_size - 4
                )
                pygame.draw.rect(self.screen, DARK_GREEN, head_rect, border_radius=3)
                
                # Draw eyes
                eye_size = max(2, self.grid_size // 6)
                eye_offset = self.grid_size // 4
                
                # Left eye
                if self.direction == Direction.RIGHT:
                    eye1 = (x * self.grid_size + self.game_area_x + self.grid_size - eye_offset, 
                           y * self.grid_size + self.game_area_y + eye_offset)
                    eye2 = (x * self.grid_size + self.game_area_x + self.grid_size - eye_offset, 
                           y * self.grid_size + self.game_area_y + self.grid_size - eye_offset * 2)
                elif self.direction == Direction.LEFT:
                    eye1 = (x * self.grid_size + self.game_area_x + eye_offset, 
                           y * self.grid_size + self.game_area_y + eye_offset)
                    eye2 = (x * self.grid_size + self.game_area_x + eye_offset, 
                           y * self.grid_size + self.game_area_y + self.grid_size - eye_offset * 2)
                elif self.direction == Direction.UP:
                    eye1 = (x * self.grid_size + self.game_area_x + eye_offset, 
                           y * self.grid_size + self.game_area_y + eye_offset)
                    eye2 = (x * self.grid_size + self.game_area_x + self.grid_size - eye_offset * 2, 
                           y * self.grid_size + self.game_area_y + eye_offset)
                else:  # DOWN
                    eye1 = (x * self.grid_size + self.game_area_x + eye_offset, 
                           y * self.grid_size + self.game_area_y + self.grid_size - eye_offset)
                    eye2 = (x * self.grid_size + self.game_area_x + self.grid_size - eye_offset * 2, 
                           y * self.grid_size + self.game_area_y + self.grid_size - eye_offset)
                
                pygame.draw.circle(self.screen, WHITE, eye1, eye_size)
                pygame.draw.circle(self.screen, WHITE, eye2, eye_size)
                
                # Pupils
                pygame.draw.circle(self.screen, BLACK, eye1, eye_size // 2)
                pygame.draw.circle(self.screen, BLACK, eye2, eye_size // 2)
                
            else:
                # Body segment with gradient
                segment_rect = pygame.Rect(
                    self.game_area_x + x * self.grid_size + 1, 
                    self.game_area_y + y * self.grid_size + 1, 
                    self.grid_size - 2, 
                    self.grid_size - 2
                )
                
                # Create a gradient effect for the body
                color_offset = min(50, i * 2)  # Darken based on position
                body_color = (
                    max(0, GREEN[0] - color_offset),
                    max(0, GREEN[1] - color_offset),
                    max(0, GREEN[2] - color_offset)
                )
                
                pygame.draw.rect(self.screen, body_color, segment_rect, border_radius=2)
                pygame.draw.rect(
                    self.screen, 
                    (0, 100, 0), 
                    segment_rect, 
                    width=1, 
                    border_radius=2
                )
        
        # Draw food
        food_rect = pygame.Rect(
            self.game_area_x + self.food[0] * self.grid_size + 2, 
            self.game_area_y + self.food[1] * self.grid_size + 2, 
            self.grid_size - 4, 
            self.grid_size - 4
        )
        pygame.draw.rect(self.screen, RED, food_rect, border_radius=self.grid_size // 2)
        
        # Draw special food if it exists
        if self.special_food:
            special_food_pos, spawn_time, points = self.special_food
            food_rect = pygame.Rect(
                self.game_area_x + special_food_pos[0] * self.grid_size + 2, 
                self.game_area_y + special_food_pos[1] * self.grid_size + 2, 
                self.grid_size - 4, 
                self.grid_size - 4
            )
            
            # Pulsing effect
            pulse = (pygame.time.get_ticks() % 1000) / 1000.0
            pulse_size = int(2 * (0.5 + 0.5 * math.sin(pulse * 2 * math.pi)))
            
            pygame.draw.rect(
                self.screen, 
                GOLD, 
                food_rect.inflate(pulse_size * 2, pulse_size * 2), 
                border_radius=(self.grid_size - 4 + pulse_size * 2) // 2
            )
            
            # Draw star in the middle
            star_points = 5
            star_radius = self.grid_size // 3
            star_center = (
                self.game_area_x + special_food_pos[0] * self.grid_size + self.grid_size // 2,
                self.game_area_y + special_food_pos[1] * self.grid_size + self.grid_size // 2
            )
            self.draw_star(self.screen, star_center, star_points, star_radius, star_radius // 2, BLACK)
        
        # Draw score and game info
        self.draw_game_ui()
        
        # Draw game over or paused overlay
        if self.state == GameState.GAME_OVER:
            self.draw_game_over()
        elif self.state == GameState.PAUSED:
            self.draw_paused()
    
    def draw_star(self, surface, center, points, outer_radius, inner_radius, color):
        """Draw a star shape"""
        point_angle = 2 * math.pi / points
        rotation = -math.pi / 2  # Start from top
        
        points_list = []
        for i in range(points * 2):
            radius = outer_radius if i % 2 == 0 else inner_radius
            angle = rotation + i * point_angle / 2
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            points_list.append((x, y))
        
        pygame.draw.polygon(surface, color, points_list)
    
    def draw_game_ui(self):
        """Draw the game UI elements (score, level, etc.)"""
        # Draw score
        score_text = self.font_medium.render(f'Score: {self.score}', True, WHITE)
        self.screen.blit(score_text, (20, 20))
        
        # Draw difficulty
        diff_text = self.font_small.render(
            f'Difficulty: {self.difficulty.value["name"]}', 
            True, 
            WHITE
        )
        self.screen.blit(diff_text, (20, 60))
        
        # Draw high score for current difficulty
        diff_name = self.difficulty.value['name']
        high_score = max([s['score'] for s in self.high_scores.get(diff_name, [{'score':0}])])
        high_score_text = self.font_small.render(
            f'High Score: {high_score}', 
            True, 
            GOLD if self.score >= high_score and self.score > 0 else WHITE
        )
        self.screen.blit(high_score_text, (20, 90))
    
    def draw_game_over(self):
        """Draw the game over overlay"""
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_text = self.font_large.render('GAME OVER', True, RED)
        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, 250))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Score text
        score_text = self.font_medium.render(f'Final Score: {self.score}', True, WHITE)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, 350))
        self.screen.blit(score_text, score_rect)
        
        # Check if this is a new high score
        diff_name = self.difficulty.value['name']
        high_scores = self.high_scores.get(diff_name, [])
        is_high_score = len(high_scores) < 10 or any(self.score > score['score'] for score in high_scores)
        
        if is_high_score and self.score > 0:
            high_score_text = self.font_medium.render('NEW HIGH SCORE!', True, GOLD)
            high_score_rect = high_score_text.get_rect(center=(WINDOW_WIDTH // 2, 400))
            self.screen.blit(high_score_text, high_score_rect)
    
    def draw_paused(self):
        """Draw the paused overlay"""
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        # Paused text
        paused_text = self.font_large.render('PAUSED', True, WHITE)
        paused_rect = paused_text.get_rect(center=(WINDOW_WIDTH // 2, 300))
        self.screen.blit(paused_text, paused_rect)
        
        # Instructions
        inst_text = self.font_small.render('Press ESC or click Resume to continue', True, LIGHT_GRAY)
        inst_rect = inst_text.get_rect(center=(WINDOW_WIDTH // 2, 370))
        self.screen.blit(inst_text, inst_rect)
    
    def update_ui_visibility(self):
        """Update visibility of UI elements based on game state"""
        # Hide all buttons first
        for button in self.buttons.values():
            button.hide()
        
        if self.state == GameState.MAIN_MENU:
            self.buttons['new_game'].show()
            
            # Only show continue if there's a previous game
            if hasattr(self, 'last_score') and self.last_score > 0:
                self.buttons['continue_game'].show()
                
            self.buttons['high_scores'].show()
            self.buttons['quit'].show()
            
        elif self.state == GameState.DIFFICULTY_SELECT:
            self.buttons['easy'].show()
            self.buttons['medium'].show()
            self.buttons['hard'].show()
            self.buttons['back'].show()
            
        elif self.state == GameState.PLAYING:
            self.buttons['pause'].show()
            
        elif self.state == GameState.PAUSED:
            self.buttons['resume'].show()
            self.buttons['main_menu'].show()
            
        elif self.state == GameState.GAME_OVER:
            self.buttons['play_again'].show()
            self.buttons['main_menu'].show()
            
        elif self.state == GameState.HIGH_SCORES:
            self.buttons['scores_back'].show()
    
    def update_ui_positions(self):
        """Update positions of UI elements when window is resized"""
        center_x = self.screen.get_width() // 2 - 150  # 150 is half button width
        
        # Main menu buttons
        self.buttons['new_game'].set_position((center_x, 250))
        self.buttons['continue_game'].set_position((center_x, 330))
        self.buttons['high_scores'].set_position((center_x, 410))
        self.buttons['quit'].set_position((center_x, 490))
        
        # Difficulty selection
        self.buttons['easy'].set_position((center_x, 300))
        self.buttons['medium'].set_position((center_x, 380))
        self.buttons['hard'].set_position((center_x, 460))
        self.buttons['back'].set_position((center_x, 540))
        
        # In-game UI
        self.buttons['pause'].set_position((self.screen.get_width() - 120, 20))
        
        # Pause menu
        self.buttons['resume'].set_position((center_x, 300))
        
        # Game over
        self.buttons['play_again'].set_position((center_x - 160, 450))
        self.buttons['main_menu'].set_position((center_x + 160, 450))
        
        # High scores
        self.buttons['scores_back'].set_position((center_x, 650))
    
    def start_new_game(self):
        """Start a new game with the selected difficulty"""
        self.reset_game()
        self.state = GameState.PLAYING
        self.update_ui_visibility()
        self.last_update_time = time.time()
    
    def show_high_score_input(self):
        """Show dialog to enter name for high score"""
        # Create a simple input dialog
        input_rect = pygame.Rect(WINDOW_WIDTH // 2 - 150, 450, 300, 40)
        input_text = ''
        input_active = True
        
        # Default name
        input_text = 'Player'
        
        # Simple input loop
        while input_active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        input_active = False
                    elif event.key == pygame.K_ESCAPE:
                        return
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    elif len(input_text) < 10:  # Limit name length
                        input_text += event.unicode
            
            # Draw
            self.draw()
            
            # Draw input box
            pygame.draw.rect(self.screen, WHITE, input_rect, 2)
            pygame.draw.rect(self.screen, (50, 50, 50), input_rect.inflate(-4, -4))
            
            # Draw text
            font = pygame.font.SysFont('Arial', 24)
            text_surface = font.render('Enter your name:', True, WHITE)
            self.screen.blit(text_surface, (input_rect.x, input_rect.y - 30))
            
            # Draw input text
            text_surface = font.render(input_text, True, WHITE)
            self.screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
            
            # Draw cursor
            if int(time.time() * 2) % 2 == 0:  # Blinking cursor
                cursor_x = input_rect.x + 5 + font.size(input_text)[0]
                pygame.draw.line(
                    self.screen, 
                    WHITE, 
                    (cursor_x, input_rect.y + 5), 
                    (cursor_x, input_rect.y + 35), 
                    2
                )
            
            pygame.display.flip()
            self.clock.tick(30)
        
        # Add high score
        if input_text.strip():
            self.add_high_score(input_text.strip(), self.score)
    
    def draw_centered_text(self, text, color, y_offset=0, font_size=36):
        """Draw centered text on the screen"""
        font = pygame.font.SysFont('Arial', font_size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + y_offset))
        self.screen.blit(text_surface, text_rect)

    def run(self):
        """Main game loop"""
        self.state = GameState.MAIN_MENU
        self.update_ui_visibility()
        self.last_update_time = time.time()
        
        running = True
        while running:
            running = self.handle_events()
            
            # Only update game logic if we're playing
            if self.state == GameState.PLAYING:
                self.update()
            
            self.draw()
            self.clock.tick(FPS)
        
        # Clean up
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = SnakeGame()
    game.run()
