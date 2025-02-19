import pygame
import math
from constants.game_rules import GAME_RULES
from constants.file_paths import IMAGES_FOLDER
from constants.maze_variants import MAZE_WIDTH, MAZE_HEIGHT
from utils.sound_manager import sound_manager


class Projectile:
    def __init__(self, start_x, start_y, target_x, target_y, player_projectile, projectile_type):
        # Spawn projectile from the center of the player

        # Load projectile image
        self.projectile_image = pygame.image.load(
            f"{IMAGES_FOLDER}/{projectile_type}")
        self.projectile_image = pygame.transform.smoothscale(
            self.projectile_image, (GAME_RULES["PROJECTILE_SIZE"], GAME_RULES["PROJECTILE_SIZE"]))

        self.x = start_x + GAME_RULES["PLAYER_SIZE"] // 2
        self.y = start_y + GAME_RULES["PLAYER_SIZE"] // 2
        self.speed = 10  # Speed of the projectile

        self.player_projectile = player_projectile
        self.hit = False

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

    def can_move(self, x, y, maze):
        """Check if the projectile can move without hitting a wall."""
        col, row = int(x // GAME_RULES["TILE_SIZE"]
                       ), int(y // GAME_RULES["TILE_SIZE"])

        # If outside the bounds of the maze or inside a wall, return False
        if row < 0 or row >= MAZE_HEIGHT or col < 0 or col >= MAZE_WIDTH or maze.grid[row][col] == 1:
            self.hit = True
            return False  # Collision detected

        return True  # No collision

    def check_collision(self, enemy):
        """Check if the projectile collides with an enemy, considering enemy size."""
        # Calculate the enemy's center point and a reasonable collision radius
        enemy_center_x = enemy.x + GAME_RULES["ENEMY_SIZE"] // 2
        enemy_center_y = enemy.y + GAME_RULES["ENEMY_SIZE"] // 2
        # You can tweak this value for more or less sensitivity
        collision_radius = GAME_RULES["TILE_SIZE"] // 2

        # Calculate the distance between the projectile and the enemy center
        dist_x = abs(self.x - enemy_center_x)
        dist_y = abs(self.y - enemy_center_y)

        # Check if within collision radius
        if dist_x < collision_radius and dist_y < collision_radius:
            return True

        return False

    def draw(self, surface, camera_x, camera_y):
        """Draw the projectile with proper rotation based on movement."""
        rotated_image = pygame.transform.rotate(
            self.projectile_image, -self.angle)  # Rotate counter-clockwise
        new_rect = rotated_image.get_rect(
            center=(self.x - camera_x, self.y - camera_y))

        # Draw the rotated image
        surface.blit(rotated_image, new_rect.topleft)
