# totems.py
import pygame
from settings import *

class Totem:
    def __init__(self, key, data):
        self.key = key
        self.name = data['name']
        self.desc = data['desc']
        self.price = data['price']
        self.rarity = data.get('rarity', 'Common') # Common, Rare, Legendary
        self.trigger_type = data['trigger'] # 'on_score', 'on_clear', 'passive', 'on_shop'
        
        # Görsel
        self.rect = pygame.Rect(0, 0, 70, 90) # Küçük kartlar (Slotlara sığsın)
        self.hovered = False

    def trigger(self, game_state, context=None):
        """
        Oyunun durumuna göre tetiklenir ve sonucu değiştirir.
        context: O anki olayla ilgili veri (örn: silinen satır sayısı)
        """
        pass # Alt sınıflarda doldurulacak

    def draw(self, surface, x, y):
        self.rect.topleft = (x, y)
        
        # Rarity Renkleri
        border_color = (100, 100, 100) # Common
        if self.rarity == 'Rare': border_color = (0, 200, 255)
        elif self.rarity == 'Legendary': border_color = (255, 215, 0)
        
        bg_color = (40, 30, 50) if not self.hovered else (60, 50, 70)
        
        # Kart Çizimi
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=8)
        
        # İsim (İlk harf veya sembol)
        font = pygame.font.SysFont(FONT_NAME, 24, bold=True)
        txt = font.render(self.name[:2].upper(), True, border_color)
        surface.blit(txt, txt.get_rect(center=self.rect.center))

# --- TOTEM VERİTABANI VE MANTIKLARI ---

TOTEM_DATA = {
    'sniper': {'name': 'Sniper', 'price': 6, 'desc': 'Edge placements give x2 Mult', 'trigger': 'on_score', 'rarity': 'Common'},
    'miner': {'name': 'Miner', 'price': 8, 'desc': '+$1 for every Stone destroyed', 'trigger': 'on_clear', 'rarity': 'Common'},
    'architect': {'name': 'Architect', 'price': 10, 'desc': '+50 Chips if NO lines cleared', 'trigger': 'on_place', 'rarity': 'Rare'},
    'void_walker': {'name': 'Void Walker', 'price': 15, 'desc': 'x3 Mult if Void Stock < 5', 'trigger': 'on_score', 'rarity': 'Rare'},
    'midas': {'name': 'King Midas', 'price': 25, 'desc': 'All cleared blocks give $0.2', 'trigger': 'on_clear', 'rarity': 'Legendary'},
    'recycler': {'name': 'Recycler', 'price': 12, 'desc': 'Discard is FREE', 'trigger': 'passive', 'rarity': 'Rare'},
    'blood_pact': {'name': 'Blood Pact', 'price': 0, 'desc': 'x4 Mult but -1 Void Ammo per turn', 'trigger': 'on_score', 'rarity': 'Legendary'},
}

class TotemLogic:
    @staticmethod
    def apply_on_score(totem_key, current_mult, current_chips, game):
        """Puan hesaplama anında devreye girer"""
        mult_mod = 1
        chips_mod = 0
        
        if totem_key == 'sniper':
            # Bloğun herhangi bir parçası kenardaysa
            is_edge = False
            b = game.held_block
            grid_r, grid_c = game.last_grid_pos # Bunu game'e ekleyeceğiz
            
            for r in range(b.rows):
                for c in range(b.cols):
                    if b.matrix[r][c] == 1:
                        abs_r, abs_c = grid_r + r, grid_c + c
                        if abs_r == 0 or abs_r == GRID_SIZE-1 or abs_c == 0 or abs_c == GRID_SIZE-1:
                            is_edge = True
            if is_edge: mult_mod *= 2

        elif totem_key == 'void_walker':
            if game.void_count < 5: mult_mod *= 3
            
        elif totem_key == 'blood_pact':
            mult_mod *= 4
            game.void_count = max(0, game.void_count - 1)

        return current_mult * mult_mod, current_chips + chips_mod

    @staticmethod
    def apply_on_place(totem_key, game, lines_cleared):
        """Blok konduğunda (patlama olmadan)"""
        chips_add = 0
        if totem_key == 'architect':
            if lines_cleared == 0: chips_add = 50
        return chips_add

    @staticmethod
    def apply_on_clear(totem_key, game, cleared_cells_count, destroyed_stones):
        """Satır silindiğinde"""
        money_add = 0
        if totem_key == 'miner':
            money_add += destroyed_stones * 1
        elif totem_key == 'midas':
            money_add += cleared_cells_count * 0.2
        
        return money_add