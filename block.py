# block.py
import pygame
from settings import *

class Block:
    def __init__(self, shape_key):
        self.shape_key = shape_key
        self.matrix = SHAPES[shape_key]
        self.base_color = SHAPE_COLORS[shape_key]
        self.color = self.base_color
        self.update_dimensions()
        
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.original_pos = (0, 0)
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0

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

    def flip(self):
        self.matrix = [row[::-1] for row in self.matrix]
        self.update_dimensions()

    def draw(self, surface, x, y, scale=1.0, alpha=255, theme_type='glass'):
        current_tile_size = int(TILE_SIZE * scale)
        
        # Tema Ayarları
        gap = 0
        if theme_type == 'glass': gap = int(current_tile_size * 0.1)
        elif theme_type == 'pixel': gap = 0 # Retroda boşluk olmaz, bitişik durur
        elif theme_type == 'flat': gap = int(current_tile_size * 0.15) # Candy'de tombul boşluk

        block_size = current_tile_size - gap

        # Şeffaflık Yüzeyi
        if alpha < 255:
            temp_surface = pygame.Surface((self.width * scale + 10, self.height * scale + 10), pygame.SRCALPHA)
            dx, dy = 0, 0
        else:
            temp_surface = surface
            dx, dy = x, y

        for r_idx, row in enumerate(self.matrix):
            for c_idx, val in enumerate(row):
                if val == 1:
                    bx = dx + (c_idx * current_tile_size) + (gap // 2)
                    by = dy + (r_idx * current_tile_size) + (gap // 2)
                    rect = pygame.Rect(bx, by, block_size, block_size)

                    # --- STİL 1: NEON / GLASS (Mevcut Stil) ---
                    if theme_type == 'glass':
                        if alpha < 255:
                            pygame.draw.rect(temp_surface, (*self.color, alpha), rect, border_radius=8)
                        else:
                            dark_color = (max(0, self.color[0]-50), max(0, self.color[1]-50), max(0, self.color[2]-50))
                            pygame.draw.rect(temp_surface, dark_color, rect, border_radius=8)
                            center_rect = rect.inflate(-15, -15)
                            pygame.draw.rect(temp_surface, (min(255, self.color[0]+50), min(255, self.color[1]+50), min(255, self.color[2]+50)), center_rect, border_radius=6)
                            pygame.draw.rect(temp_surface, self.color, rect, 2, border_radius=8)

                    # --- STİL 2: RETRO / PIXEL ---
                    elif theme_type == 'pixel':
                        # Düz renk, radius yok, kalın siyah kenar
                        c = self.color
                        if alpha < 255: c = (*c, alpha)
                        pygame.draw.rect(temp_surface, c, rect) # Köşeli
                        # İçine piksel deseni (X çiz)
                        pygame.draw.line(temp_surface, (0,0,0), rect.topleft, rect.bottomright, 2)
                        pygame.draw.line(temp_surface, (0,0,0), rect.bottomleft, rect.topright, 2)
                        pygame.draw.rect(temp_surface, (0,0,0), rect, 3) # Kalın siyah çerçeve

                    # --- STİL 3: CANDY / FLAT ---
                    elif theme_type == 'flat':
                        # Çok yuvarlak, pastel, kenar çizgisi yok
                        c = self.color
                        # Rengi pastelleştir (Beyazla karıştır)
                        pastel_c = ((c[0]+255)//2, (c[1]+255)//2, (c[2]+255)//2)
                        if alpha < 255: pastel_c = (*pastel_c, alpha)
                        
                        pygame.draw.rect(temp_surface, pastel_c, rect, border_radius=15)
                        # Minik beyaz parıltı (Jelibon gibi)
                        shine_rect = pygame.Rect(bx + block_size//4, by + block_size//4, block_size//4, block_size//4)
                        pygame.draw.circle(temp_surface, (255, 255, 255, 150) if alpha < 255 else (255,255,255), shine_rect.center, 4)

        if alpha < 255:
            surface.blit(temp_surface, (x, y))