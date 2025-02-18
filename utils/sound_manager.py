import pygame
from constants.file_paths import SOUND_FX_FOLDER

# Initialize Pygame mixer for sounds
pygame.mixer.init()


class SoundManager:
    def __init__(self):
        self.sounds = {
            "plasma_gun": pygame.mixer.Sound(f"{SOUND_FX_FOLDER}shoot.wav"),
            "projectile_impact": pygame.mixer.Sound(f"{SOUND_FX_FOLDER}enemy_death.wav"),
        }

    def play(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()


# Create a singleton instance of SoundManager
sound_manager = SoundManager()
