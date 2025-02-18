import pygame

pygame.init()
info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h

GAME_RULES = {
    "FPS": 60,
    "TILE_SIZE": 50,
    "PLAYER_SIZE": 40,
    "ENEMY_SIZE": 40,
    "PROJECTILE_SIZE": 20,
    "ENEMY_COUNT": 5,
    "PLAYER_SPEED": 3,
    "ENEMY_SPEED": 1
}
