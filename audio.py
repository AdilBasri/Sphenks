# audio.py
import pygame
from settings import *

class AudioManager:
    def __init__(self):
        # Mixer başlat
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.mixer.set_num_channels(32)
        
        # Sesleri Yükle
        self.sounds = {}
        try:
            self.sounds['place'] = pygame.mixer.Sound(SND_PLACE)
            self.sounds['clear'] = pygame.mixer.Sound(SND_CLEAR)
            self.sounds['explode'] = pygame.mixer.Sound(SND_EXPLODE)
            self.sounds['gameover'] = pygame.mixer.Sound(SND_GAMEOVER)
            self.sounds['select'] = pygame.mixer.Sound(SND_SELECT)
            self.sounds['hit'] = pygame.mixer.Sound(SND_HIT)
            
            # Ses seviyeleri
            for s in self.sounds.values():
                s.set_volume(SFX_VOLUME)
        except Exception as e:
            print(f"Warning: Sound files not found. Run generate_sounds.py first. ({e})")

    def play(self, name):
        if name in self.sounds:
            self.sounds[name].play()
    
    def set_volume(self, volume):
        """Set volume for all sounds (0.0 to 1.0)"""
        for sound in self.sounds.values():
            sound.set_volume(volume)