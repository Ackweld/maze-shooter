import pygame
from file_paths import *

# Load shooting sounds for round-robin
shoot_sounds = [
    pygame.mixer.Sound(f"{SOUND_FX_FOLDER}/shoot_sound_1.wav"),
    pygame.mixer.Sound(f"{SOUND_FX_FOLDER}/shoot_sound_2.wav"),
    pygame.mixer.Sound(f"{SOUND_FX_FOLDER}/shoot_sound_3.wav"),
    pygame.mixer.Sound(f"{SOUND_FX_FOLDER}/shoot_sound_4.wav")
]
mini_gun_sounds = [
    pygame.mixer.Sound(f"{SOUND_FX_FOLDER}/mini_gun_sound_1.wav"),
    pygame.mixer.Sound(f"{SOUND_FX_FOLDER}/mini_gun_sound_1.wav"),
    pygame.mixer.Sound(f"{SOUND_FX_FOLDER}/mini_gun_sound_1.wav"),
    pygame.mixer.Sound(f"{SOUND_FX_FOLDER}/mini_gun_sound_1.wav"),
]

enemy_hit_sound = pygame.mixer.Sound(f"{SOUND_FX_FOLDER}/enemy_hit.wav")
punch_sound = pygame.mixer.Sound(f"{SOUND_FX_FOLDER}/punch.wav")
