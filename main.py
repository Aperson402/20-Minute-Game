import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Set up the screen
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Chasing Squares")

# Load background image
background = pygame.image.load("Assets/background.png").convert()
background = pygame.transform.scale(background, (screen_width, screen_height))

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ACID_GREEN = (0, 128, 0)  # Custom color for acid blotches

# Player attributes
player_size = 50
player_x = screen_width // 2
player_y = screen_height // 2
player_speed = 5

# Enemy attributes
enemy_size = 30
enemy_speed = 2
enemies = []
max_enemies = 10
enemy_spawn_rate = .1

# Acid blotch attributes
acid_size = 20
acid_blotches = []
max_acid_blotches = 5  # Adjust the number of acid blotches as needed

# Game variables
running = True
game_over = False
score = 0
grace_active = False

# Special enemy attributes
special_enemy_size = 60  # Increased size for the yellow enemy
special_enemy_speed = 6  # Increased speed for the yellow enemy
dash_distance = 200
dash_cooldown = 120  # Frames between each dash
dash_timer = dash_cooldown  # Initialize timer

# Power-up attributes
power_ups = []
power_up_spawn_rate = 0.005
power_up_duration = 500  # Frames

# Create enemies in a circular formation with holes from the edges
def create_enemy_circle():
    # Calculate the radius of the circle
    radius = min(screen_width, screen_height) // 2 - enemy_size

    # Calculate the number of enemies to spawn
    num_enemies = max_enemies - len(enemies)

    # Define the number of holes and their positions
    num_holes = 3
    hole_angles = [random.uniform(0, 2 * math.pi) for _ in range(num_holes)]

    # Calculate the angle increment for evenly spacing the enemies
    angle_increment = 2 * math.pi / num_enemies

    # Spawn enemies around the circle, leaving holes
    for i in range(num_enemies):
        angle = i * angle_increment
        if all(abs(angle - hole_angle) > angle_increment for hole_angle in hole_angles):
            enemy_x = int(screen_width / 2 + radius * math.cos(angle)) - enemy_size // 2
            enemy_y = int(screen_height / 2 + radius * math.sin(angle)) - enemy_size // 2
            enemies.append([enemy_x, enemy_y])

# Create special enemy
class SpecialEnemy:
    def __init__(self):
        self.x = random.randint(0, screen_width - special_enemy_size)
        self.y = random.randint(0, screen_height - special_enemy_size)
        self.dashing = False
        self.dash_target_x = 0
        self.dash_target_y = 0
        self.dash_timer = dash_cooldown

    def move(self):
        if self.dashing:
            # Move towards dash target
            angle = math.atan2(self.dash_target_y - self.y, self.dash_target_x - self.x)
            self.x += special_enemy_speed * math.cos(angle)
            self.y += special_enemy_speed * math.sin(angle)
            # Check if arrived at dash target
            if distance(self.x, self.y, self.dash_target_x, self.dash_target_y) < special_enemy_speed:
                self.dashing = False
                self.dash_timer = dash_cooldown
        else:
            # Move randomly
            self.x += random.randint(-1, 1)
            self.y += random.randint(-1, 1)
        # Ensure enemy stays within screen bounds
        self.x = max(0, min(self.x, screen_width - special_enemy_size))
        self.y = max(0, min(self.y, screen_height - special_enemy_size))

    def dash(self, target_x, target_y):
        self.dashing = True
        self.dash_target_x = target_x
        self.dash_target_y = target_y

class ShootingEnemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 3
        self.shoot_cooldown = 60  # Cooldown between shots
        self.shoot_timer = 0

    def move(self, player_x, player_y):
        # Move towards the player
        angle = math.atan2(player_y - self.y, player_x - self.x)
        self.x += self.speed * math.cos(angle)
        self.y += self.speed * math.sin(angle)

    def shoot(self, player_x, player_y):
        if self.shoot_timer <= 0:
            # Shoot projectile towards the player
            angle = math.atan2(player_y - self.y, player_x - self.x)
            # Implement projectile spawning code here
            self.shoot_timer = self.shoot_cooldown

    def update(self, player_x, player_y):
        self.move(player_x, player_y)
        self.shoot(player_x, player_y)
        if self.shoot_timer > 0:
            self.shoot_timer -= 1

# Calculate distance between two points
def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# Function to display text on screen
def draw_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    screen.blit(text_surface, text_rect)

def update_special_enemies(dash_timer):
    if dash_timer > 0:
        dash_timer -= 1
    elif dash_timer == 0:
        if special_enemy:
            special_enemy.dash(player_x, player_y)
        dash_timer = dash_cooldown

    return dash_timer

# Main game loop
running = True
game_over = False
score = 0
special_enemy = None
shooting_enemy = ShootingEnemy(random.randint(0, screen_width), random.randint(0, screen_height))  # Create shooting enemy
while running:
    # Event handling
    dash_timer = update_special_enemies(dash_timer)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and game_over:
            # Restart the game if the user clicks after the game ends
            game_over = False
            score = 0
            player_x = screen_width // 2
            player_y = screen_height // 2
            enemies.clear()
            special_enemy = None
            shooting_enemy = ShootingEnemy(random.randint(0, screen_width), random.randint(0, screen_height))  # Reset shooting enemy position
            enemy_speed = 1.9
    if not game_over:
        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_x = max(0, player_x - player_speed)
        if keys[pygame.K_RIGHT]:
            player_x = min(screen_width - player_size, player_x + player_speed)
        if keys[pygame.K_UP]:
            player_y = max(0, player_y - player_speed)
        if keys[pygame.K_DOWN]:
            player_y = min(screen_height - player_size, player_y + player_speed)

        # Increase score
        score += 1

        # Spawning a special enemy every 100 score
        if score == 100:
            special_enemy = SpecialEnemy()
            if dash_cooldown > 100:
                dash_cooldown -= 50
        if score%100 == 0:
            enemy_speed += .1
        
        # Spawn regular enemies if the current count is less than the maximum
        if len(enemies) < max_enemies:
            if random.random() < enemy_spawn_rate:
                create_enemy_circle()

        # Acid blotch spawning (if needed)
        if len(acid_blotches) < max_acid_blotches:
            if random.random() < 0.01:  # Adjust spawn rate as needed
                acid_x = random.randint(0, screen_width - acid_size)
                acid_y = random.randint(0, screen_height - acid_size)
                acid_blotches.append([acid_x, acid_y])

        # Inside the loop where enemies move towards the player, add randomness to their movement
        for enemy in enemies:
            enemy_x, enemy_y = enemy
            angle = math.atan2(player_y - enemy_y, player_x - enemy_x)
            # Add a random offset to enemy movement
            offset = random.uniform(0.5, .6)  # Adjust the values as needed
            enemy_x += enemy_speed * offset * math.cos(angle)
            enemy_y += enemy_speed * offset * math.sin(angle)
            enemy[0], enemy[1] = enemy_x, enemy_y
            # Collision detection with player
            if not grace_active and math.sqrt((player_x - enemy_x)**2 + (player_y - enemy_y)**2) < player_size / 2 + enemy_size / 2:
                game_over = True
            elif grace_active and math.sqrt((player_x - enemy_x)**2 + (player_y - enemy_y)**2) < player_size / 2 + enemy_size / 2:
                enemies.remove(enemy)

        # Special enemy movement
        if special_enemy:
            special_enemy.move()

        # Special enemy dash
        if dash_timer > 0:
            dash_timer -= 1
        elif dash_timer == 0:
            if special_enemy:
                special_enemy.dash(player_x, player_y)
            dash_timer = dash_cooldown

        # Shooting enemy behavior
        if not game_over:
            shooting_enemy.update(player_x, player_y)
            # Handle collision detection with player
            if math.sqrt((player_x - shooting_enemy.x)**2 + (player_y - shooting_enemy.y)**2) < player_size / 2 + enemy_size / 2:
                game_over = True

        # Collision detection with special enemies
        if special_enemy:
            if math.sqrt((player_x - special_enemy.x)**2 + (player_y - special_enemy.y)**2) < player_size / 2 + special_enemy_size / 2:
                game_over = True

        # Collision detection with acid blotches
        for acid in acid_blotches:
            if math.sqrt((player_x - acid[0])**2 + (player_y - acid[1])**2) < player_size / 2 + acid_size / 2:
                game_over = True

    # Drawing
    screen.blit(background, (0, 0))  # Draw background
    if not game_over:
        pygame.draw.rect(screen, RED, (player_x, player_y, player_size, player_size))
        for enemy in enemies:
            pygame.draw.rect(screen, BLUE, (enemy[0], enemy[1], enemy_size, enemy_size))
        for acid in acid_blotches:
            pygame.draw.rect(screen, ACID_GREEN, (acid[0], acid[1], acid_size, acid_size))
        if special_enemy:
            pygame.draw.circle(screen, YELLOW, (int(special_enemy.x + special_enemy_size / 2), int(special_enemy.y + special_enemy_size / 2)), special_enemy_size // 2)
        pygame.draw.rect(screen, BLACK, (shooting_enemy.x, shooting_enemy.y, enemy_size, enemy_size))  # Draw shooting enemy
        draw_text("Score: " + str(score), pygame.font.Font(None, 36), BLACK, 100, 50)
    else:
        draw_text("Game Over", pygame.font.Font(None, 72), BLACK, screen_width // 2, screen_height // 2 - 50)
        draw_text("Click to Restart", pygame.font.Font(None, 36), BLACK, screen_width // 2, screen_height // 2 + 50)
    pygame.display.flip()

    # Frame rate
    pygame.time.Clock().tick(60)

# Quit Pygame
pygame.quit()
