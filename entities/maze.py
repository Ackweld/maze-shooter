import pygame
from constants.maze_variants import MAZE
from constants.colors import COLORS
from constants.game_rules import *


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
                    tile_x = col * GAME_RULES["TILE_SIZE"] - camera_x
                    tile_y = row * GAME_RULES["TILE_SIZE"] - camera_y
                    if 0 <= tile_x < SCREEN_WIDTH and 0 <= tile_y < SCREEN_HEIGHT:  # Only draw visible tiles
                        color = COLORS["WALL_COLOR"] if self.grid[row][col] == 1 else COLORS["FLOOR_COLOR"]
                        pygame.draw.rect(
                            surface, color, (tile_x, tile_y, GAME_RULES["TILE_SIZE"], GAME_RULES["TILE_SIZE"]))
