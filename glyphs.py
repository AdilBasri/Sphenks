# glyphs.py
import pygame
from settings import *

class Glyph:
    def __init__(self, key):
        data = GLYPHS[key]
        self.key = key
        self.name = data['name']
        self.desc = data['desc']
        self.price = data['price']
        self.color = data['color']
        
        self.rect = pygame.Rect(0, 0, 50, 50) # UI'da küçük kareler
        self.hovered = False

    def activate(self, game):
        """Rün kullanıldığında ne olacağını tanımlar"""
        if self.key == 'REFILL':
            game.void_count += 5
            game.particle_system.create_text(game.w//2, game.h//2, "+5 AMMO", self.color, font_path=game.font_name)
            return True # Başarılı kullanım

        elif self.key == 'RESET':
            # Eli yenile (Maliyet ödemeden)
            game.blocks.clear()
            game.refill_hand()
            game.particle_system.create_text(game.w//2, game.h//2, "HAND RESET", self.color, font_path=game.font_name)
            return True

        elif self.key == 'STONE_BREAKER':
            # Tüm taşları yok et
            cleared = 0
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    if game.grid.grid[r][c] == STONE_COLOR:
                        game.grid.grid[r][c] = None
                        # Görsel efekt
                        x = game.grid_offset_x + (c * TILE_SIZE) + TILE_SIZE//2
                        y = game.grid_offset_y + (r * TILE_SIZE) + TILE_SIZE//2
                        game.particle_system.create_explosion(x, y, (100, 100, 100))
                        cleared += 1
            
            if cleared > 0:
                game.particle_system.create_text(game.w//2, game.h//2, "STONES CRUSHED!", self.color, font_path=game.font_name)
                game.audio.play('explode')
                return True
            else:
                return False # Hiç taş yoksa boşa gitmesin

        # BOMB mantığı özeldir (Mouse ile tıklama gerektirir), 
        # onu game.py içinde "Active Glyph" state'i ile yöneteceğiz.
        return False 

    def draw(self, surface, x, y):
        self.rect.topleft = (x, y)
        
        # Hover Effect
        scale = 1.1 if self.hovered else 1.0
        draw_rect = self.rect.inflate(int(self.rect.width*(scale-1)), int(self.rect.height*(scale-1)))
        
        # Rün Taşı Şekli (Elmas/Kare)
        pygame.draw.rect(surface, (20, 20, 30), draw_rect, border_radius=5)
        pygame.draw.rect(surface, self.color, draw_rect, 2, border_radius=5)
        
        # İçine harf
        font = pygame.font.SysFont('Arial', 20, bold=True)
        txt = font.render(self.name[0], True, self.color)
        surface.blit(txt, txt.get_rect(center=draw_rect.center))