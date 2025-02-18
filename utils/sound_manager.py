import pygame
import random
from constants.file_paths import SOUND_FX_FOLDER


class SoundManager:
    def __init__(self):
        self.sounds = {
            # Store the 4 plasma gun firing sounds in a list for round-robin or random selection
            "plasma_gun": [
                pygame.mixer.Sound(f"{SOUND_FX_FOLDER}/plasma_gun_fire_1.wav"),
                pygame.mixer.Sound(f"{SOUND_FX_FOLDER}/plasma_gun_fire_2.wav"),
                pygame.mixer.Sound(f"{SOUND_FX_FOLDER}/plasma_gun_fire_3.wav"),
                pygame.mixer.Sound(f"{SOUND_FX_FOLDER}/plasma_gun_fire_4.wav")
            ],
            "mini_gun": [
                pygame.mixer.Sound(f"{SOUND_FX_FOLDER}/mini_gun_fire_1.wav"),
                pygame.mixer.Sound(f"{SOUND_FX_FOLDER}/mini_gun_fire_2.wav"),
                pygame.mixer.Sound(f"{SOUND_FX_FOLDER}/mini_gun_fire_3.wav"),
                pygame.mixer.Sound(f"{SOUND_FX_FOLDER}/mini_gun_fire_4.wav")
            ],
            "projectile_impact": pygame.mixer.Sound(f"{SOUND_FX_FOLDER}/projectile_impact.wav"),
            "punch": pygame.mixer.Sound(f"{SOUND_FX_FOLDER}/punch.wav"),
            "explode": pygame.mixer.Sound(f"{SOUND_FX_FOLDER}/explode.wav")
        }

    def play(self, sound_name):
        print(pygame.mixer.get_num_channels())
        if sound_name in self.sounds:
            sound = self.sounds[sound_name]

            # For "plasma_gun" or "mini_gun", pick a random sound from the list
            if isinstance(sound, list):  # Check if it's a list of sounds
                sound = random.choice(sound)  # Randomly choose one sound

            # Find an available channel and play the sound
            channel = pygame.mixer.find_channel()
            if channel:
                channel.play(sound)
            else:
                # Optional: Handle case where no channels are available, e.g., retry or log a message
                print(f"Warning: No available channel for {sound_name}!")


# Create a singleton instance of SoundManager
sound_manager = SoundManager()
