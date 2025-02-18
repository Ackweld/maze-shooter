import pygame
import random
import math
import time
from constants.file_paths import IMAGES_FOLDER
from constants.game_rules import GAME_RULES
from constants.maze_variants import MAZE, MAZE_WIDTH, MAZE_HEIGHT
from constants.colors import COLORS
from entities.projectile import Projectile
from utils.sound_manager import sound_manager


class Player:
    def __init__(self):

        self.player_image = pygame.image.load(f"{IMAGES_FOLDER}/player.png")
        self.player_image = pygame.transform.smoothscale(
            self.player_image, (GAME_RULES["PLAYER_SIZE"], GAME_RULES["PLAYER_SIZE"]))
        self.weapon = "plasma_gun"
        self.last_shot_time = 0
        self.fire_rate = 100
        self.is_firing = False

        while True:
            x = random.randint(1, MAZE_WIDTH - 2)
            y = random.randint(1, MAZE_HEIGHT - 2)

            # Ensure the player doesn't spawn inside a wall
            if MAZE[y][x] == 0:  # 0 means walkable space
                self.x = x * GAME_RULES["TILE_SIZE"]
                self.y = y * GAME_RULES["TILE_SIZE"]
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
                self.x, self.y, mouse_x + camera_x, mouse_y + camera_y, True, "plasma_gun_projectile.png")
            projectiles.append(projectile)
            sound_manager.play("plasma_gun")

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
                sound_manager.play("mini_gun")
                self.last_shot_time = current_time

    def can_move(self, x, y, maze):
        """Check collisions for all corners of the player's bounding box."""
        corners = [
            (x, y),  # Top-left
            (x + GAME_RULES["PLAYER_SIZE"] - 1, y),  # Top-right
            (x, y + GAME_RULES["PLAYER_SIZE"] - 1),  # Bottom-left
            (x + GAME_RULES["PLAYER_SIZE"] - 1, y +
             GAME_RULES["PLAYER_SIZE"] - 1)  # Bottom-right
        ]

        for cx, cy in corners:
            col, row = cx // GAME_RULES["TILE_SIZE"], cy // GAME_RULES["TILE_SIZE"]
            if row < 0 or row >= MAZE_HEIGHT or col < 0 or col >= MAZE_WIDTH or maze.grid[row][col] == 1:
                return False  # Collision detected

        return True  # No collisions

    def move(self, keys, maze):
        """Handles player movement while checking for wall collisions."""
        new_x, new_y = self.x, self.y

        if keys[pygame.K_w] and self.can_move(self.x, self.y - GAME_RULES["PLAYER_SPEED"], maze):
            new_y -= GAME_RULES["PLAYER_SPEED"]
        if keys[pygame.K_s] and self.can_move(self.x, self.y + GAME_RULES["PLAYER_SPEED"], maze):
            new_y += GAME_RULES["PLAYER_SPEED"]
        if keys[pygame.K_a] and self.can_move(self.x - GAME_RULES["PLAYER_SPEED"], self.y, maze):
            new_x -= GAME_RULES["PLAYER_SPEED"]
        if keys[pygame.K_d] and self.can_move(self.x + GAME_RULES["PLAYER_SPEED"], self.y, maze):
            new_x += GAME_RULES["PLAYER_SPEED"]

        self.x, self.y = new_x, new_y  # Update position only if movement is allowed

    def draw(self, surface, camera_x, camera_y):
        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Calculate the angle between the player and the mouse
        dx = mouse_x - (self.x - camera_x + GAME_RULES["PLAYER_SIZE"] // 2)
        dy = mouse_y - (self.y - camera_y + GAME_RULES["PLAYER_SIZE"] // 2)
        angle = math.degrees(math.atan2(dy, dx))  # Convert radians to degrees

        # Rotate the player image to face the mouse cursor
        rotated_image = pygame.transform.rotate(self.player_image, -angle - 90)
        rotated_rect = rotated_image.get_rect()

        # Position the rotated image correctly (centering it)
        rotated_rect.center = (
            self.x - camera_x + GAME_RULES["PLAYER_SIZE"] // 2, self.y - camera_y + GAME_RULES["PLAYER_SIZE"] // 2)

        # Draw the rotated player image
        surface.blit(rotated_image, rotated_rect)

    def draw_health(self, surface):
        for i in range(self.health):
            pygame.draw.rect(
                surface, COLORS["HEALTH_COLOR"], (i * 20, 20, 18, 10))
