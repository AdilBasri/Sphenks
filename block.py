# block.py
import pygame
import math
from settings import *

def lerp(start, end, amount):
    return start + (end - start) * amount

class Block:
    def __init__(self, shape_key):
        self.shape_key = shape_key
        self.matrix = SHAPES[shape_key]
        self.base_color = SHAPE_COLORS[shape_key]
        self.color = self.base_color
        self.update_dimensions()
        
        # MANTIKSAL KONUM (Oyunun gördüğü gerçek kutu)
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.original_pos = (0, 0)
        
        # GÖRSEL KONUM (Gözün gördüğü)
        # Başlangıçta 0,0 olmamalı, game.py bunu hemen güncelleyecek
        self.visual_x = 0
        self.visual_y = 0
        
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0
        
        self.target_rotation = 0
        self.current_rotation = 0
        self.scale = 1.0
        self.target_scale = 1.0

    def update_dimensions(self):
        self.rows = len(self.matrix)
        self.cols = len(self.matrix[0])
        self.width = self.cols * TILE_SIZE
        self.height = self.rows * TILE_SIZE

    def rotate(self):
        self.matrix = [list(row) for row in zip(*self.matrix[::-1])]
        self.update_dimensions()
        self.rect.width = self.width
        self.rect.height = self.height
        self.current_rotation += 90 

    def update(self):
        # 1. Animasyon Hedefleri
        if self.dragging:
            self.target_scale = 1.1 
            # Tilt: Görsel gerideyse eğil
            delta_x = self.rect.x - self.visual_x
            self.target_rotation = -delta_x * 0.5 
            self.target_rotation = max(-15, min(15, self.target_rotation))
        else:
            self.target_scale = 1.0 
            self.target_rotation = 0

        # 2. GÖRSELİ, RECT'E DOĞRU ÇEK (Lerp)
        # Rect nereye giderse görsel oraya "sünerek" gelir.
        self.visual_x = lerp(self.visual_x, self.rect.x, 0.3) # 0.3 = Hız (Daha sıkı takip)
        self.visual_y = lerp(self.visual_y, self.rect.y, 0.3)
        
        self.scale = lerp(self.scale, self.target_scale, 0.2)
        self.current_rotation = lerp(self.current_rotation, self.target_rotation, 0.2)

    def draw(self, surface, x, y, scale=1.0, alpha=255, theme_type='glass'):
        # Çizim görsel koordinatlarda yapılır
        draw_x = self.visual_x
        draw_y = self.visual_y
        
        # Eğer dışarıdan override koordinat geliyorsa (Ghost Piece gibi)
        # O zaman görseli değil, o koordinatı kullan
        if x != 0 and y != 0: 
            # (Ghost piece 0,0'a çizilmez, bu basit bir kontrol)
            draw_x = x
            draw_y = y

        final_scale = scale * self.scale
        
        surf_w = int(self.width * final_scale * 1.5)
        surf_h = int(self.height * final_scale * 1.5)
        temp_surface = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
        
        current_tile_size = int(TILE_SIZE * final_scale)
        gap = 0
        if theme_type == 'glass': gap = int(current_tile_size * 0.1)
        elif theme_type == 'flat': gap = int(current_tile_size * 0.15)

        block_size = current_tile_size - gap
        
        start_x = (surf_w - (self.cols * current_tile_size)) // 2
        start_y = (surf_h - (self.rows * current_tile_size)) // 2

        for r_idx, row in enumerate(self.matrix):
            for c_idx, val in enumerate(row):
                if val == 1:
                    bx = start_x + (c_idx * current_tile_size) + (gap // 2)
                    by = start_y + (r_idx * current_tile_size) + (gap // 2)
                    rect = pygame.Rect(bx, by, block_size, block_size)

                    if theme_type == 'glass':
                        dark_color = (max(0, self.color[0]-50), max(0, self.color[1]-50), max(0, self.color[2]-50))
                        pygame.draw.rect(temp_surface, dark_color, rect, border_radius=6)
                        center = rect.inflate(-10, -10)
                        pygame.draw.rect(temp_surface, (min(255, self.color[0]+80), min(255, self.color[1]+80), min(255, self.color[2]+80)), center, border_radius=4)
                        pygame.draw.rect(temp_surface, self.color, rect, 2, border_radius=6)
                    elif theme_type == 'pixel':
                         pygame.draw.rect(temp_surface, self.color, rect)
                         pygame.draw.rect(temp_surface, (0,0,0), rect, 2)
                    elif theme_type == 'flat':
                        pygame.draw.rect(temp_surface, self.color, rect, border_radius=10)

        if alpha < 255:
            temp_surface.set_alpha(alpha)

        if self.current_rotation != 0:
            rotated_surf = pygame.transform.rotate(temp_surface, self.current_rotation)
            new_rect = rotated_surf.get_rect(center=(draw_x + self.width//2, draw_y + self.height//2))
            surface.blit(rotated_surf, new_rect)
        else:
            offset_x = (surf_w - self.width) // 2
            offset_y = (surf_h - self.height) // 2
            surface.blit(temp_surface, (draw_x - offset_x, draw_y - offset_y))