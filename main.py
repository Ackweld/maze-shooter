import pygame
import random
import time
import math
import heapq
from maze import MAZE

# Initialize pygame
pygame.init()

# Constants
TILE_SIZE = 50
MAZE_WIDTH, MAZE_HEIGHT = len(MAZE[0]), len(MAZE)
FPS = 60

PLAYER_WIDTH = TILE_SIZE - 10  # Adjust as needed
PLAYER_HEIGHT = TILE_SIZE - 10  # Adjust as needed

ENEMY_WIDTH = TILE_SIZE - 10
ENEMY_HEIGHT = TILE_SIZE - 10

PROJECTILE_WIDTH = TILE_SIZE - 30
PROJECTILE_HEIGHT = TILE_SIZE - 30

ENEMY_COUNT = 5

# Colors
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
WALL_COLOR = (100, 100, 100)
FLOOR_COLOR = (200, 200, 200)
HEALTH_COLOR = (255, 0, 0)

# Set the display size
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h

# Create the window with borderless fullscreen (Windowed Fullscreen mode)
# screen = pygame.display.set_mode(
#     (WIDTH, HEIGHT), pygame.NOFRAME | pygame.FULLSCREEN)
screen = pygame.display.set_mode(
    (WIDTH, HEIGHT))

pygame.display.set_caption("Pygame Maze with Camera Movement")

PLAYER_SPEED = 3
ENEMY_SPEED = 1

crosshair_image = pygame.image.load("crosshair.png")
crosshair_image = pygame.transform.scale(
    crosshair_image, (TILE_SIZE, TILE_SIZE))

# Set a default system cursor first (for fallback)
pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

# Then, set the custom crosshair cursor:
pygame.mouse.set_visible(False)  # Hide the default cursor
crosshair_width, crosshair_height = crosshair_image.get_size()

# Initialize the mixer for sound
pygame.mixer.init()

# Background music
pygame.mixer.music.load("soundtrack.mp3")  # Load your soundtrack
pygame.mixer.music.set_volume(0.3)  # Optional: set the volume (0.0 to 1.0)
# Start playing and loop indefinitely
pygame.mixer.music.play(loops=-1, start=0.0)

# Load shooting sounds for round-robin
shoot_sounds = [
    pygame.mixer.Sound("shoot_sound_1.wav"),
    pygame.mixer.Sound("shoot_sound_2.wav"),
    pygame.mixer.Sound("shoot_sound_3.wav"),
    pygame.mixer.Sound("shoot_sound_4.wav")
]
mini_gun_sounds = [
    pygame.mixer.Sound("mini_gun_sound_1.wav"),
    pygame.mixer.Sound("mini_gun_sound_1.wav"),
    pygame.mixer.Sound("mini_gun_sound_1.wav"),
    pygame.mixer.Sound("mini_gun_sound_1.wav"),
]

enemy_hit_sound = pygame.mixer.Sound("enemy_hit.wav")
punch_sound = pygame.mixer.Sound("punch.wav")


class Maze:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = MAZE  # Ensure this matches the grid's dimensions (24x18)

    def draw(self, surface, camera_x, camera_y):
        """Draws the maze, adjusting for the camera offset."""
        for row in range(self.height):
            for col in range(self.width):
                # Make sure we stay within the grid bounds
                if 0 <= col < len(self.grid[0]) and 0 <= row < len(self.grid):
                    tile_x = col * TILE_SIZE - camera_x
                    tile_y = row * TILE_SIZE - camera_y
                    if 0 <= tile_x < WIDTH and 0 <= tile_y < HEIGHT:  # Only draw visible tiles
                        color = WALL_COLOR if self.grid[row][col] == 1 else FLOOR_COLOR
                        pygame.draw.rect(
                            surface, color, (tile_x, tile_y, TILE_SIZE, TILE_SIZE))


class Player:
    def __init__(self):

        self.player_image = pygame.image.load("player.png")
        self.player_image = pygame.transform.smoothscale(
            self.player_image, (PLAYER_WIDTH, PLAYER_HEIGHT))
        self.weapon = "plasma_gun"
        self.last_shot_time = 0
        self.fire_rate = 100
        self.is_firing = False

        while True:
            x = random.randint(1, MAZE_WIDTH - 2)
            y = random.randint(1, MAZE_HEIGHT - 2)

            # Ensure the player doesn't spawn inside a wall
            if MAZE[y][x] == 0:  # 0 means walkable space
                self.x = x * TILE_SIZE
                self.y = y * TILE_SIZE
                self.health = 3  # Reset health
                break  # Found a valid position, exit loop

        self.health = 10
        self.last_damage_time = time.time()
        self.sound_index = 0

    def fire_projectile(self, camera_x, camera_y, projectiles):
        """Get the mouse position and create a new projectile, firing continuously if the mouse is held down."""

        if self.weapon == "plasma_gun":
            mouse_x, mouse_y = pygame.mouse.get_pos()
            projectile = Projectile(
                self.x, self.y, mouse_x + camera_x, mouse_y + camera_y, True, "projectile.png")
            projectiles.append(projectile)
            shoot_sounds[self.sound_index].play()
            self.sound_index = (self.sound_index + 1) % len(shoot_sounds)

        if self.weapon == "mini_gun":
            current_time = pygame.time.get_ticks()

            # Fire only if enough time has passed to respect the fire rate
            if current_time - self.last_shot_time >= self.fire_rate:
                # Get mouse position
                mouse_x, mouse_y = pygame.mouse.get_pos()

                # Create the projectile and add it to the list
                projectile = Projectile(
                    self.x, self.y, mouse_x + camera_x, mouse_y + camera_y, True, "mini_gun_projectile.png")
                projectiles.append(projectile)

                # Play shoot sound
                mini_gun_sounds[self.sound_index].play()
                self.sound_index = (self.sound_index +
                                    1) % len(mini_gun_sounds)

                # Update the last shot time
                self.last_shot_time = current_time

    def can_move(self, x, y, maze):
        """Check collisions for all corners of the player's bounding box."""
        corners = [
            (x, y),  # Top-left
            (x + PLAYER_WIDTH - 1, y),  # Top-right
            (x, y + PLAYER_HEIGHT - 1),  # Bottom-left
            (x + PLAYER_WIDTH - 1, y + PLAYER_HEIGHT - 1)  # Bottom-right
        ]

        for cx, cy in corners:
            col, row = cx // TILE_SIZE, cy // TILE_SIZE
            if row < 0 or row >= MAZE_HEIGHT or col < 0 or col >= MAZE_WIDTH or maze.grid[row][col] == 1:
                return False  # Collision detected

        return True  # No collisions

    def move(self, keys, maze):
        """Handles player movement while checking for wall collisions."""
        new_x, new_y = self.x, self.y

        if keys[pygame.K_w] and self.can_move(self.x, self.y - PLAYER_SPEED, maze):
            new_y -= PLAYER_SPEED
        if keys[pygame.K_s] and self.can_move(self.x, self.y + PLAYER_SPEED, maze):
            new_y += PLAYER_SPEED
        if keys[pygame.K_a] and self.can_move(self.x - PLAYER_SPEED, self.y, maze):
            new_x -= PLAYER_SPEED
        if keys[pygame.K_d] and self.can_move(self.x + PLAYER_SPEED, self.y, maze):
            new_x += PLAYER_SPEED

        self.x, self.y = new_x, new_y  # Update position only if movement is allowed

    def draw(self, surface, camera_x, camera_y):
        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Calculate the angle between the player and the mouse
        dx = mouse_x - (self.x - camera_x + PLAYER_WIDTH // 2)
        dy = mouse_y - (self.y - camera_y + PLAYER_HEIGHT // 2)
        angle = math.degrees(math.atan2(dy, dx))  # Convert radians to degrees

        # Rotate the player image to face the mouse cursor
        rotated_image = pygame.transform.rotate(self.player_image, -angle - 90)
        rotated_rect = rotated_image.get_rect()

        # Position the rotated image correctly (centering it)
        rotated_rect.center = (
            self.x - camera_x + PLAYER_WIDTH // 2, self.y - camera_y + PLAYER_HEIGHT // 2)

        # Draw the rotated player image
        surface.blit(rotated_image, rotated_rect)

    def draw_health(self, surface):
        for i in range(self.health):
            pygame.draw.rect(surface, HEALTH_COLOR, (i * 20, 20, 18, 10))


class Projectile:
    def __init__(self, start_x, start_y, target_x, target_y, player_projectile, projectile_type):
        # Spawn projectile from the center of the player

        # Load projectile image
        self.projectile_image = pygame.image.load(projectile_type)
        self.projectile_image = pygame.transform.scale(
            self.projectile_image, (PROJECTILE_WIDTH, PROJECTILE_HEIGHT))

        self.x = start_x + PLAYER_WIDTH // 2
        self.y = start_y + PLAYER_HEIGHT // 2
        self.speed = 10  # Speed of the projectile

        self.player_projectile = player_projectile
        self.explode = False

        # Calculate the direction from player to crosshair (target)
        dx = target_x - self.x
        dy = target_y - self.y

        # Calculate the distance between start and target
        distance = math.sqrt(dx**2 + dy**2)

        # Normalize direction and set the speed of the projectile
        self.dx = (dx / distance) * self.speed
        self.dy = (dy / distance) * self.speed

        # Calculate angle for rotating the projectile image
        self.angle = math.degrees(math.atan2(dy, dx))  # Angle in degrees
        self.angle -= 90  # Offset to align the image

    def can_move(self, x, y, maze):
        """Check if the projectile can move without hitting a wall."""
        col, row = int(x // TILE_SIZE), int(y // TILE_SIZE)

        # If outside the bounds of the maze or inside a wall, return False
        if row < 0 or row >= MAZE_HEIGHT or col < 0 or col >= MAZE_WIDTH or maze.grid[row][col] == 1:
            self.explode = True
            return False  # Collision detected

        return True  # No collision

    def move(self, maze):
        """Move the projectile along the calculated path, stopping if it hits a wall."""
        new_x = self.x + self.dx
        new_y = self.y + self.dy

        # Check if the projectile can move to the new position
        if self.can_move(new_x, new_y, maze):
            self.x = new_x
            self.y = new_y
        else:
            # Stop moving by setting speed to zero
            self.dx = 0
            self.dy = 0

    def draw(self, surface, camera_x, camera_y):
        """Draw the projectile with proper rotation based on movement."""
        rotated_image = pygame.transform.rotate(
            self.projectile_image, -self.angle)  # Rotate counter-clockwise
        new_rect = rotated_image.get_rect(
            center=(self.x - camera_x, self.y - camera_y))

        # Draw the rotated image
        surface.blit(rotated_image, new_rect.topleft)

    def check_collision(self, enemy):
        """Check if the projectile collides with an enemy, considering enemy size."""
        # Calculate the enemy's center point and a reasonable collision radius
        enemy_center_x = enemy.x + ENEMY_WIDTH // 2
        enemy_center_y = enemy.y + ENEMY_HEIGHT // 2
        # You can tweak this value for more or less sensitivity
        collision_radius = TILE_SIZE // 2

        # Calculate the distance between the projectile and the enemy center
        dist_x = abs(self.x - enemy_center_x)
        dist_y = abs(self.y - enemy_center_y)

        # Check if within collision radius
        if dist_x < collision_radius and dist_y < collision_radius:
            return True

        return False


class Enemy:
    def __init__(self, maze):

        self.enemy_image = pygame.image.load("enemy.png")
        self.enemy_image = pygame.transform.smoothscale(
            self.enemy_image, (ENEMY_WIDTH, ENEMY_HEIGHT))
        self.enemy_death_sound = pygame.mixer.Sound("death.wav")
        while True:
            x = random.randint(1, MAZE_WIDTH - 2)
            y = random.randint(1, MAZE_HEIGHT - 2)

            # Ensure the enemy doesn't spawn inside a wall
            if MAZE[y][x] == 0:  # 0 means walkable space
                self.x = x * TILE_SIZE
                self.y = y * TILE_SIZE
                self.health = 3  # Reset health
                break  # Found a valid position, exit loop
        self.speed = ENEMY_SPEED
        self.health = 3
        self.path = []
        self.target = None
        self.last_damage_time = time.time()
        self.last_shot_time = time.time()  # Time the enemy last shot
        self.maze_grid = maze.grid if hasattr(maze, 'grid') else maze
        self.sound_index = 0

    def set_target(self, player):
        """Set the player's position as the enemy's target."""
        self.target = (player.x // TILE_SIZE, player.y // TILE_SIZE)

    def fire_projectile(self, player, projectiles):
        """Fire a projectile towards the player every 3 seconds if the player is in line of sight."""
        current_time = time.time()
        if current_time - self.last_shot_time >= 3 and self.is_in_line_of_sight(player):
            # Fire the projectile
            projectile = Projectile(
                self.x, self.y, player.x + TILE_SIZE // 2, player.y + TILE_SIZE // 2, False, "projectile.png")
            projectiles.append(projectile)  # Add projectile to the list
            self.last_shot_time = current_time  # Update last shot time
            shoot_sounds[self.sound_index].play()
            self.sound_index = (self.sound_index + 1) % len(shoot_sounds)

    def heuristic(self, a, b):
        """Manhattan distance heuristic for A*."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def find_path(self):
        """Uses A* algorithm to find a path to the player while avoiding walls, allowing diagonal movement."""
        if not self.target:
            return

        start = (self.x // TILE_SIZE, self.y // TILE_SIZE)
        goal = self.target

        # Include diagonal directions: Up, Down, Left, Right, and all diagonals
        directions = [
            (0, -1), (0, 1), (-1, 0), (1, 0),  # Cardinal directions
            (-1, -1), (1, -1), (-1, 1), (1, 1)  # Diagonal directions
        ]

        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal:
                # Reconstruct path
                self.path = []
                while current in came_from:
                    self.path.insert(0, current)
                    current = came_from[current]
                return

            for dx, dy in directions:
                neighbor = (current[0] + dx, current[1] + dy)

                # Ensure diagonal movement is valid (no walls blocking movement)
                if 0 <= neighbor[0] < MAZE_WIDTH and 0 <= neighbor[1] < MAZE_HEIGHT:
                    # Check if it's walkable
                    if self.maze_grid[neighbor[1]][neighbor[0]] == 0:

                        # Check for diagonal wall collisions
                        if abs(dx) + abs(dy) == 2:  # Diagonal move
                            # Ensure diagonals aren't blocked by corner walls
                            if self.maze_grid[current[1]][neighbor[0]] == 1 and self.maze_grid[neighbor[1]][current[0]] == 1:
                                continue  # If both adjacent tiles are walls, don't move diagonally

                        # Diagonal is slightly longer
                        temp_g_score = g_score[current] + \
                            (1.4 if abs(dx) + abs(dy) == 2 else 1)

                        if neighbor not in g_score or temp_g_score < g_score[neighbor]:
                            came_from[neighbor] = current
                            g_score[neighbor] = temp_g_score
                            f_score[neighbor] = temp_g_score + \
                                self.heuristic(neighbor, goal)
                            heapq.heappush(
                                open_set, (f_score[neighbor], neighbor))

        self.path = []  # No path found

    def can_move_to(self, new_x, new_y):
        """Check if the enemy can move to the given position (collision check for all corners)."""
        corners = [
            (new_x, new_y),  # Top-left
            (new_x + ENEMY_WIDTH - 1, new_y),  # Top-right
            (new_x, new_y + ENEMY_HEIGHT - 1),  # Bottom-left
            (new_x + ENEMY_WIDTH - 1, new_y + ENEMY_HEIGHT - 1)  # Bottom-right
        ]

        for cx, cy in corners:
            col, row = cx // TILE_SIZE, cy // TILE_SIZE
            if row < 0 or row >= MAZE_HEIGHT or col < 0 or col >= MAZE_WIDTH or self.maze_grid[row][col] == 1:
                return False  # Collision detected

        return True  # No collisions

    def move_along_path(self):
        """Moves the enemy along the calculated path, allowing diagonal movement while checking for collisions."""
        if self.path:
            next_tile = self.path[0]  # Get the next tile in the path
            target_x, target_y = next_tile[0] * \
                TILE_SIZE, next_tile[1] * TILE_SIZE

            # Calculate movement direction
            move_x = self.speed if self.x < target_x else - \
                self.speed if self.x > target_x else 0
            move_y = self.speed if self.y < target_y else - \
                self.speed if self.y > target_y else 0

            # Try moving diagonally first (if both x and y movement are needed)
            if move_x != 0 and move_y != 0:
                new_x, new_y = self.x + move_x, self.y + move_y
                if self.can_move_to(new_x, new_y):
                    self.x, self.y = new_x, new_y  # Move diagonally
                else:
                    # If diagonal move is blocked, try X and Y separately
                    if self.can_move_to(new_x, self.y):
                        self.x = new_x
                    if self.can_move_to(self.x, new_y):
                        self.y = new_y
            else:
                # Move normally (horizontal or vertical if no diagonal move needed)
                if self.can_move_to(self.x + move_x, self.y):
                    self.x += move_x
                if self.can_move_to(self.x, self.y + move_y):
                    self.y += move_y

            # Remove tile from path when reached
            if (self.x, self.y) == (target_x, target_y):
                self.path.pop(0)

    def move_towards_target(self):
        """Finds a path and moves toward the target while avoiding walls."""
        if not self.path or (self.target and self.path[-1] != self.target):
            self.find_path()  # Recalculate path if needed

        self.move_along_path()  # Follow path step by step

    def draw(self, surface, camera_x, camera_y):
        """Draw the enemy, facing the movement direction."""
        enemy_x = self.x - camera_x
        enemy_y = self.y - camera_y

        # Get next position to face
        if self.path:
            next_tile = self.path[0]
            target_x, target_y = next_tile[0] * \
                TILE_SIZE, next_tile[1] * TILE_SIZE

            # Calculate the angle to the next tile
            dx = target_x - self.x
            dy = target_y - self.y
            # Convert radians to degrees
            angle = math.degrees(math.atan2(dy, dx))

            # Rotate the enemy image to face the next tile
            rotated_image = pygame.transform.rotate(
                self.enemy_image, -angle - 90)
            rotated_rect = rotated_image.get_rect()

            # Position the rotated image correctly (center it on the enemy)
            rotated_rect.center = (
                enemy_x + ENEMY_WIDTH // 2, enemy_y + ENEMY_HEIGHT // 2)

            # Draw the rotated enemy image
            surface.blit(rotated_image, rotated_rect)
        else:
            # If no path, just draw the enemy image normally
            surface.blit(self.enemy_image, (enemy_x, enemy_y))

    def check_attack(self, player):
        """Check if enemy is close enough to attack the player."""
        if abs(self.x - player.x) < TILE_SIZE and abs(self.y - player.y) < TILE_SIZE:
            current_time = time.time()
            if current_time - self.last_damage_time >= 1:
                self.last_damage_time = current_time
                return True
        return False

    def is_in_line_of_sight(self, player):
        """Check if the player is in the enemy's line of sight."""
        # Calculate direction towards the player
        dx = player.x - self.x
        dy = player.y - self.y
        angle = math.degrees(math.atan2(dy, dx))

        # Check for obstacles between the enemy and the player (basic version)
        # Cast a line from enemy to player and check if it's clear of walls
        step_size = 10  # Step size for checking along the line
        steps = max(abs(dx), abs(dy)) // step_size

        for i in range(1, steps + 1):
            # Check along the line from enemy to player
            check_x = self.x + i * dx / steps
            check_y = self.y + i * dy / steps
            col, row = int(check_x // TILE_SIZE), int(check_y // TILE_SIZE)
            if self.maze_grid[row][col] == 1:  # Wall detected
                return False

        return True

    def respawn(self):
        """Respawn the enemy at a random valid location in the maze."""
        self.enemy_death_sound.play()
        while True:
            x = random.randint(1, MAZE_WIDTH - 2)
            y = random.randint(1, MAZE_HEIGHT - 2)

            # Ensure the enemy doesn't spawn inside a wall
            if MAZE[y][x] == 0:  # 0 means walkable space
                self.x = x * TILE_SIZE
                self.y = y * TILE_SIZE
                self.health = 3  # Reset health
                break  # Found a valid position, exit loop


def game_over_screen():
    """Displays the 'You Died' screen with options to restart or exit."""
    font = pygame.font.Font(None, 100)
    button_font = pygame.font.Font(None, 50)

    text = font.render("You Died", True, (255, 0, 0))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 3))

    # Button positions
    play_again_rect = pygame.Rect(WIDTH // 3, HEIGHT // 2, 200, 50)
    exit_rect = pygame.Rect(WIDTH // 3 * 2 - 100, HEIGHT // 2, 200, 50)

    while True:
        screen.fill(GRAY)  # Clear screen
        screen.blit(text, text_rect)

        # Draw buttons
        # Green Play Again
        pygame.draw.rect(screen, (0, 255, 0), play_again_rect)
        pygame.draw.rect(screen, (255, 0, 0), exit_rect)  # Red Exit

        # Draw button text
        play_again_text = button_font.render("Play Again", True, (0, 0, 0))
        exit_text = button_font.render("Exit Game", True, (0, 0, 0))
        screen.blit(play_again_text, play_again_text.get_rect(
            center=play_again_rect.center))
        screen.blit(exit_text, exit_text.get_rect(center=exit_rect.center))

        # Draw custom crosshair cursor
        mouse_x, mouse_y = pygame.mouse.get_pos()
        screen.blit(crosshair_image, (mouse_x - crosshair_width //
                    2, mouse_y - crosshair_height // 2))

        pygame.display.flip()

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if play_again_rect.collidepoint(mouse_x, mouse_y):
                    return  # Restart the game
                elif exit_rect.collidepoint(mouse_x, mouse_y):
                    pygame.quit()


def main():
    while True:  # Game loop to allow restarting
        clock = pygame.time.Clock()

        player = Player()
        maze = Maze(MAZE_WIDTH, MAZE_HEIGHT)
        enemies = [Enemy(maze) for _ in range(ENEMY_COUNT)]
        projectiles = []  # List to store active projectiles

        kill_count = 0
        camera_x, camera_y = 0, 0  # Camera position
        running = True
        while running:
            clock.tick(FPS)

            if kill_count > 3:
                player.weapon = "mini_gun"
            # # Handle events
            if player.weapon == "plasma_gun":
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:  # Left mouse button
                            player.fire_projectile(
                                camera_x, camera_y, projectiles)

            if player.weapon == "mini_gun":
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:  # Left mouse button
                            player.is_firing = True  # Indicate that the player is holding down the fire button
                    elif event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 1:  # Left mouse button
                            player.is_firing = False  # Stop firing when the button is released

                if player.is_firing:
                    player.fire_projectile(camera_x, camera_y, projectiles)

            keys = pygame.key.get_pressed()

            # Move the player
            player.move(keys, maze)

            # Update enemies, check for damage, and fire projectiles
            for enemy in enemies:
                enemy.set_target(player)
                enemy.move_towards_target()
                enemy.fire_projectile(player, projectiles)

                # Check for collision with player
                if enemy.check_attack(player):
                    punch_sound.play()
                    player.health -= 2

            # Update projectiles
            for projectile in projectiles[:]:
                projectile.move(maze)
                if projectile.explode:
                    projectiles.remove(projectile)
                    enemy_hit_sound.play()

                # Check for collisions with enemies
                for enemy in enemies:
                    if projectile.check_collision(enemy) and projectile.player_projectile:
                        enemy.health -= 1
                        enemy_hit_sound.play()
                        if projectile in projectiles:
                            projectiles.remove(projectile)
                        if enemy.health <= 0:
                            kill_count += 1
                            enemy.respawn()
                if projectile.check_collision(player) and not projectile.player_projectile:
                    player.health -= 1
                    enemy_hit_sound.play()
                    if projectile in projectiles:
                        projectiles.remove(projectile)

            # Check for game over
            if player.health <= 0:
                running = False

            # Update the camera
            camera_x = player.x - WIDTH // 2 + TILE_SIZE // 2
            camera_y = player.y - HEIGHT // 2 + TILE_SIZE // 2

            # Draw everything
            screen.fill(GRAY)
            maze.draw(screen, camera_x, camera_y)
            player.draw(screen, camera_x, camera_y)
            player.draw_health(screen)

            for projectile in projectiles:
                projectile.draw(screen, camera_x, camera_y)

            for enemy in enemies:
                enemy.draw(screen, camera_x, camera_y)

            # Draw kill counter in top right
            font = pygame.font.Font(None, 40)
            kill_text = font.render(
                f"Kills: {kill_count}", True, (255, 255, 255))
            screen.blit(kill_text, (WIDTH - 150, 20))

            # Draw custom crosshair cursor
            mouse_x, mouse_y = pygame.mouse.get_pos()
            screen.blit(crosshair_image, (mouse_x - crosshair_width //
                        2, mouse_y - crosshair_height // 2))

            pygame.display.flip()

        # Show game over screen and restart if needed
        game_over_screen()


if __name__ == "__main__":
    main()
