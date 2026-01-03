# block.py
import pygame
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
        
        # MANTIKSAL (Hitbox)
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.original_pos = (0, 0)
        
        # GÖRSEL (Animasyonlu)
        self.visual_x = 0
        self.visual_y = 0
        
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0
        self.scale = 1.0
        self.target_scale = 1.0
        self.current_rotation = 0
        self.target_rotation = 0

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

    # --- EKSİK OLAN FONKSİYON BUYDU ---
    def flip(self):
        """Bloğu yatayda aynalar"""
        self.matrix = [row[::-1] for row in self.matrix]
        self.update_dimensions()
        # Flip yapınca da rect boyutlarını güncellemek iyi olur (simetrik olmayanlarda)
        self.rect.width = self.width
        self.rect.height = self.height

    def update(self):
        if self.dragging:
            self.target_scale = 1.1 
            delta_x = self.rect.x - self.visual_x
            self.target_rotation = -delta_x * 0.5 
            self.target_rotation = max(-15, min(15, self.target_rotation))
        else:
            self.target_scale = 1.0 
            self.target_rotation = 0

        self.visual_x = lerp(self.visual_x, self.rect.x, 0.3)
        self.visual_y = lerp(self.visual_y, self.rect.y, 0.3)
        self.scale = lerp(self.scale, self.target_scale, 0.2)
        self.current_rotation = lerp(self.current_rotation, self.target_rotation, 0.2)

    def draw(self, surface, x, y, scale=1.0, alpha=255, theme_type='glass'):
        # Ghost Blok Mantığı (Önceki fix)
        use_override_pos = (x != 0 or y != 0)
        
        draw_x = x if use_override_pos else self.visual_x
        draw_y = y if use_override_pos else self.visual_y
        
        if self.dragging and alpha == 255:
            draw_x = self.visual_x
            draw_y = self.visual_y

        final_scale = scale * self.scale
        current_tile_size = int(TILE_SIZE * final_scale)
        
        gap = 0
        if theme_type == 'glass': gap = int(current_tile_size * 0.1)
        elif theme_type == 'flat': gap = int(current_tile_size * 0.15)

        block_size = current_tile_size - gap

        if alpha < 255:
            surf_w = int(self.width * final_scale + 50)
            surf_h = int(self.height * final_scale + 50)
            temp_surface = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
            dx, dy = 10, 10 
        else:
            temp_surface = surface
            dx, dy = draw_x, draw_y

        for r_idx, row in enumerate(self.matrix):
            for c_idx, val in enumerate(row):
                if val == 1:
                    bx = dx + (c_idx * current_tile_size) + (gap // 2)
                    by = dy + (r_idx * current_tile_size) + (gap // 2)
                    rect = pygame.Rect(bx, by, block_size, block_size)

                    if theme_type == 'glass':
                        c = self.color
                        if alpha < 255: 
                            pygame.draw.rect(temp_surface, (*c, alpha), rect, border_radius=6)
                        else:
                            dark_color = (max(0, c[0]-50), max(0, c[1]-50), max(0, c[2]-50))
                            pygame.draw.rect(temp_surface, dark_color, rect, border_radius=6)
                            center = rect.inflate(-10, -10)
                            pygame.draw.rect(temp_surface, (min(255, c[0]+80), min(255, c[1]+80), min(255, c[2]+80)), center, border_radius=4)
                            pygame.draw.rect(temp_surface, c, rect, 2, border_radius=6)
                    
                    elif theme_type == 'pixel':
                         c = (*self.color, alpha) if alpha < 255 else self.color
                         pygame.draw.rect(temp_surface, c, rect)
                         pygame.draw.rect(temp_surface, (0,0,0, alpha) if alpha < 255 else (0,0,0), rect, 2)

                    elif theme_type == 'flat':
                        c = self.color
                        pastel = ((c[0]+255)//2, (c[1]+255)//2, (c[2]+255)//2)
                        if alpha < 255: pastel = (*pastel, alpha)
                        pygame.draw.rect(temp_surface, pastel, rect, border_radius=10)

        if alpha < 255:
            surface.blit(temp_surface, (draw_x - 10, draw_y - 10))