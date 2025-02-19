import pygame
from constants.game_rules import GAME_RULES, SCREEN_WIDTH, SCREEN_HEIGHT
from constants.file_paths import MUSIC_FOLDER
from entities.player import Player


def initialize_game():

    # Initialize pygame
    pygame.init()

    pygame.display.set_caption("MAZE SHOOTER")

    crosshair_image = pygame.image.load("assets/images/crosshair.png")
    crosshair_image = pygame.transform.smoothscale(
        crosshair_image, (GAME_RULES["TILE_SIZE"], GAME_RULES["TILE_SIZE"]))

    # Set a default system cursor first (for fallback)
    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    pygame.mouse.set_visible(False)  # Hide the default cursor

    # Initialize the mixer for sound

    pygame.mixer.init()
    pygame.mixer.set_num_channels(48)

    print("Nr of channels: ", pygame.mixer.get_num_channels())

    # Background music
    # Load your soundtrack
    # pygame.mixer.music.load(f"{MUSIC_FOLDER}/soundtrack.mp3")
    # pygame.mixer.music.set_volume(0.3)  # Optional: set the volume (0.0 to 1.0)
    # pygame.mixer.music.play(loops=-1, start=0.0)
