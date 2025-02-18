import pygame
import time
import heapq
import math
import random

from constants.file_paths import *
from constants.game_rules import GAME_RULES
from constants.maze_variants import MAZE, MAZE_WIDTH, MAZE_HEIGHT
from entities.projectile import Projectile


class Enemy:
    def __init__(self, maze):

        self.enemy_image = pygame.image.load(f"{IMAGES_FOLDER}/enemy.png")
        self.enemy_image = pygame.transform.smoothscale(
            self.enemy_image, (GAME_RULES["ENEMY_SIZE"], GAME_RULES["ENEMY_SIZE"]))
        self.enemy_death_sound = pygame.mixer.Sound(
            f"{SOUND_FX_FOLDER}/death.wav")
        while True:
            x = random.randint(1, MAZE_WIDTH - 2)
            y = random.randint(1, MAZE_HEIGHT - 2)

            # Ensure the enemy doesn't spawn inside a wall
            if MAZE[y][x] == 0:  # 0 means walkable space
                self.x = x * GAME_RULES["TILE_SIZE"]
                self.y = y * GAME_RULES["TILE_SIZE"]
                self.health = 3  # Reset health
                break  # Found a valid position, exit loop
        self.speed = GAME_RULES["ENEMY_SPEED"]
        self.health = 3
        self.path = []
        self.target = None
        self.last_damage_time = time.time()
        self.last_shot_time = time.time()  # Time the enemy last shot
        self.maze_grid = maze.grid if hasattr(maze, 'grid') else maze
        self.sound_index = 0

    def set_target(self, player):
        """Set the player's position as the enemy's target."""
        self.target = (
            player.x // GAME_RULES["TILE_SIZE"], player.y // GAME_RULES["TILE_SIZE"])

    def fire_projectile(self, player, projectiles):
        """Fire a projectile towards the player every 3 seconds if the player is in line of sight."""
        current_time = time.time()
        if current_time - self.last_shot_time >= 3 and self.is_in_line_of_sight(player):
            # Fire the projectile
            projectile = Projectile(
                self.x, self.y, player.x + GAME_RULES["TILE_SIZE"] // 2, player.y + GAME_RULES["TILE_SIZE"] // 2, False, "plasma_gun_projectile.png")
            projectiles.append(projectile)  # Add projectile to the list
            self.last_shot_time = current_time  # Update last shot time
            # shoot_sounds[self.sound_index].play()
            # self.sound_index = (self.sound_index + 1) % len(shoot_sounds)

    def heuristic(self, a, b):
        """Manhattan distance heuristic for A*."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def find_path(self):
        """Uses A* algorithm to find a path to the player while avoiding walls, allowing diagonal movement."""
        if not self.target:
            return

        start = (self.x // GAME_RULES["TILE_SIZE"],
                 self.y // GAME_RULES["TILE_SIZE"])
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
            (new_x + GAME_RULES["ENEMY_SIZE"] - 1, new_y),  # Top-right
            (new_x, new_y + GAME_RULES["ENEMY_SIZE"] - 1),  # Bottom-left
            (new_x + GAME_RULES["ENEMY_SIZE"] - 1, new_y +
             GAME_RULES["ENEMY_SIZE"] - 1)  # Bottom-right
        ]

        for cx, cy in corners:
            col, row = cx // GAME_RULES["TILE_SIZE"], cy // GAME_RULES["TILE_SIZE"]
            if row < 0 or row >= MAZE_HEIGHT or col < 0 or col >= MAZE_WIDTH or self.maze_grid[row][col] == 1:
                return False  # Collision detected

        return True  # No collisions

    def move_along_path(self):
        """Moves the enemy along the calculated path, allowing diagonal movement while checking for collisions."""
        if self.path:
            next_tile = self.path[0]  # Get the next tile in the path
            target_x, target_y = next_tile[0] * \
                GAME_RULES["TILE_SIZE"], next_tile[1] * GAME_RULES["TILE_SIZE"]

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
                GAME_RULES["TILE_SIZE"], next_tile[1] * GAME_RULES["TILE_SIZE"]

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
                enemy_x + GAME_RULES["ENEMY_SIZE"] // 2, enemy_y + GAME_RULES["ENEMY_SIZE"] // 2)

            # Draw the rotated enemy image
            surface.blit(rotated_image, rotated_rect)
        else:
            # If no path, just draw the enemy image normally
            surface.blit(self.enemy_image, (enemy_x, enemy_y))

    def check_attack(self, player):
        """Check if enemy is close enough to attack the player."""
        if abs(self.x - player.x) < GAME_RULES["TILE_SIZE"] and abs(self.y - player.y) < GAME_RULES["TILE_SIZE"]:
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
            col, row = int(
                check_x // GAME_RULES["TILE_SIZE"]), int(check_y // GAME_RULES["TILE_SIZE"])
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
                self.x = x * GAME_RULES["TILE_SIZE"]
                self.y = y * GAME_RULES["TILE_SIZE"]
                self.health = 3  # Reset health
                break  # Found a valid position, exit loop
