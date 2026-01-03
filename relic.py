# relic.py
import pygame
from settings import *

class Relic:
    def __init__(self, key):
        data = RELICS[key]
        self.key = key
        self.name = data['name']
        self.price = data['price']
        self.desc = data['desc']
        self.type = data['type']
        self.value = data['value']
        
        # Görsel İçin (Kart Yapısı)
        self.rect = pygame.Rect(0, 0, 160, 220) # Kart Boyutu
        self.hovered = False

    def draw(self, surface, x, y, font_title, font_desc):
        self.rect.topleft = (x, y)
        
        # Hover Efekti (Mouse üzerindeyse parlasın)
        color = (70, 60, 80) if not self.hovered else (90, 80, 110)
        border = (150, 150, 150) if not self.hovered else ACCENT_COLOR
        
        # Kart Gövdesi
        pygame.draw.rect(surface, color, self.rect, border_radius=12)
        pygame.draw.rect(surface, border, self.rect, 3, border_radius=12)
        
        # İsim
        title_surf = font_title.render(self.name, True, (255, 200, 100))
        # Açıklama (Basit kelime kaydırma gerekebilir ama şimdilik tek satır)
        desc_surf = font_desc.render(self.desc, True, (200, 200, 200))
        # Fiyat
        price_surf = font_title.render(f"${self.price}", True, (100, 255, 100))
        
        # Ortalama
        surface.blit(title_surf, title_surf.get_rect(center=(x + 80, y + 40)))
        surface.blit(desc_surf, desc_surf.get_rect(center=(x + 80, y + 110)))
        surface.blit(price_surf, price_surf.get_rect(center=(x + 80, y + 180)))