# crt.py
import pygame
from settings import *

class CRTManager:
    def __init__(self):
        # Scanlines (Yatay Çizgiler)
        self.overlay = pygame.Surface((VIRTUAL_W, VIRTUAL_H), pygame.SRCALPHA)
        self.create_effects()

    def create_effects(self):
        # 1. Hafif Yatay Çizgiler (Scanlines)
        for y in range(0, VIRTUAL_H, 2):
            pygame.draw.line(self.overlay, (0, 0, 0, 40), (0, y), (VIRTUAL_W, y))
        
        # 2. Vignette (Kenar Karartma) - Curved hissi için
        # Kenarlara kalın, şeffaf siyah çerçeve çiz
        pygame.draw.rect(self.overlay, (0,0,0, 60), (0,0,VIRTUAL_W, VIRTUAL_H), 8)
        pygame.draw.rect(self.overlay, (0,0,0, 30), (0,0,VIRTUAL_W, VIRTUAL_H), 20)
        
        # 3. Ekran Köşeleri (Oval CRT Maskesi)
        # Köşelere siyah üçgenler koyarak ekranı yuvarlatıyoruz
        corner_size = 15
        color = (0, 0, 0) # Tam Siyah
        # Sol Üst
        pygame.draw.polygon(self.overlay, color, [(0,0), (corner_size,0), (0,corner_size)])
        # Sağ Üst
        pygame.draw.polygon(self.overlay, color, [(VIRTUAL_W,0), (VIRTUAL_W-corner_size,0), (VIRTUAL_W,corner_size)])
        # Sol Alt
        pygame.draw.polygon(self.overlay, color, [(0,VIRTUAL_H), (0,VIRTUAL_H-corner_size), (corner_size,VIRTUAL_H)])
        # Sağ Alt
        pygame.draw.polygon(self.overlay, color, [(VIRTUAL_W,VIRTUAL_H), (VIRTUAL_W,VIRTUAL_H-corner_size), (VIRTUAL_W-corner_size,VIRTUAL_H)])

    def draw(self, screen):
        # Filtreyi ekrana bas
        screen.blit(self.overlay, (0, 0))