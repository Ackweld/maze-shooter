import pygame
from constants.file_paths import *
from constants.colors import COLORS
from constants.game_rules import *
from constants.maze_variants import *

# Uncertain imports that might be removed later
from entities.maze import Maze
from init import initialize_game
from entities.player import Player
from entities.enemy import Enemy
from utils.sound_manager import sound_manager

screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT))

crosshair_image = pygame.image.load("assets/images/crosshair.png")
crosshair_image = pygame.transform.smoothscale(
    crosshair_image, (GAME_RULES["TILE_SIZE"], GAME_RULES["TILE_SIZE"]))

# Set the custom crosshair cursor:
crosshair_width, crosshair_height = crosshair_image.get_size()


def game_over_screen():
    """Displays the 'You Died' screen with options to restart or exit."""
    font = pygame.font.Font(None, 100)
    button_font = pygame.font.Font(None, 50)

    text = font.render("You Died", True, (255, 0, 0))
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))

    # Button positions
    play_again_rect = pygame.Rect(
        SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2, 200, 50)
    exit_rect = pygame.Rect(SCREEN_WIDTH // 3 * 2 - 100,
                            SCREEN_HEIGHT // 2, 200, 50)

    while True:
        screen.fill(COLORS["GRAY"])  # Clear screen
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
    initialize_game()

    while True:  # Game loop to allow restarting
        clock = pygame.time.Clock()

        player = Player()
        maze = Maze(MAZE_WIDTH, MAZE_HEIGHT)
        enemies = [Enemy(maze) for _ in range(GAME_RULES["ENEMY_COUNT"])]
        projectiles = []  # List to store active projectiles

        kill_count = 0
        camera_x, camera_y = 0, 0  # Camera position
        running = True
        while running:
            clock.tick(GAME_RULES["FPS"])

            # Update weapon if kill count is greater than 0
            if kill_count > 0:
                player.weapon = "mini_gun"

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return  # Ensure the program exits cleanly after quitting

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        if player.weapon == "plasma_gun":
                            player.fire_projectile(
                                camera_x, camera_y, projectiles)
                        elif player.weapon == "mini_gun":
                            player.is_firing = True  # Start firing for mini gun

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # Left mouse button
                        if player.weapon == "mini_gun":
                            player.is_firing = False  # Stop firing for mini gun

            # Handle continuous firing for mini gun
            if player.weapon == "mini_gun" and player.is_firing:
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
                    sound_manager.play("punch")
                    player.health -= 2

            # Update projectiles
            for projectile in projectiles[:]:
                projectile.move(maze)
                if projectile.hit:
                    sound_manager.play("projectile_impact")
                    projectiles.remove(projectile)

                # Check for collisions with enemies
                for enemy in enemies:
                    if projectile.check_collision(enemy) and projectile.player_projectile:
                        enemy.health -= 1
                        if projectile in projectiles:
                            projectiles.remove(projectile)
                            sound_manager.play("projectile_impact")
                        if enemy.health <= 0:
                            sound_manager.play("explode")
                            enemy.respawn()
                            kill_count += 1
                if projectile.check_collision(player) and not projectile.player_projectile:
                    player.health -= 1
                    if projectile in projectiles:
                        sound_manager.play("projectile_impact")
                        projectiles.remove(projectile)

            # Check for game over
            if player.health <= 0:
                running = False

            # Update the camera
            camera_x = player.x - SCREEN_WIDTH // 2 + \
                GAME_RULES["TILE_SIZE"] // 2
            camera_y = player.y - SCREEN_HEIGHT // 2 + \
                GAME_RULES["TILE_SIZE"] // 2

            # Draw everything
            screen.fill(COLORS["GRAY"])
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
            screen.blit(kill_text, (SCREEN_WIDTH - 150, 20))

            # Draw custom crosshair cursor
            mouse_x, mouse_y = pygame.mouse.get_pos()
            screen.blit(crosshair_image, (mouse_x - crosshair_width //
                        2, mouse_y - crosshair_height // 2))

            pygame.display.flip()

        # Show game over screen and restart if needed
        game_over_screen()


if __name__ == "__main__":
    main()
