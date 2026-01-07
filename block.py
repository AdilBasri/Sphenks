# block.py
import pygame
import math
import random 
from settings import *

def lerp(start, end, amount):
    """İki değer arasında yumuşak geçiş sağlar (Linear Interpolation)"""
    return start + (end - start) * amount

class Block:
    def __init__(self, shape_key):
        self.shape_key = shape_key
        self.matrix = SHAPES[shape_key]
        self.base_color = SHAPE_COLORS[shape_key]
        
        # TAG SİSTEMİ - Rastgele tag ataması
        self.tag = self._assign_random_tag()
        
        # Tag'e göre renk belirleme
        if self.tag != 'NONE' and BLOCK_TAG_COLORS.get(self.tag):
            self.color = BLOCK_TAG_COLORS[self.tag]
        else:
            self.color = self.base_color
        
        # YENİ: RÜN SİSTEMİ (Hücre Bazlı - Çoklu Rün Desteği)
        self.runes = {}  # {(row, col): RuneObj} formatında - Her hücreye ayrı rün
        
        # GOLD bloklarda pulse efekti için
        self.glow_pulse = 0.0
        
        self.update_dimensions()
        
        # MANTIKSAL (Hitbox)
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.original_pos = (0, 0)
        
        # GÖRSEL (Animasyon)
        self.visual_x = 0
        self.visual_y = 0
        
        # FİZİK
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0
        
        # Efektler
        self.scale = 1.0
        self.target_scale = 1.0
        self.angle = 0
        self.target_angle = 0
        
        # Idle Animasyon (Rastgele başlangıç)
        self.idle_offset = random.uniform(0, 6.28) 
    
    def _assign_random_tag(self):
        """Bloğa rastgele tag atar (ağırlıklı olasılık)"""
        tags = list(BLOCK_TAG_WEIGHTS.keys())
        weights = list(BLOCK_TAG_WEIGHTS.values())
        return random.choices(tags, weights=weights, k=1)[0]

    def update_dimensions(self):
        self.rows = len(self.matrix)
        self.cols = len(self.matrix[0])
        self.width = self.cols * TILE_SIZE
        self.height = self.rows * TILE_SIZE

    def rotate(self):
        old_rows = self.rows
        old_cols = self.cols
        self.matrix = [list(row) for row in zip(*self.matrix[::-1])]
        self.update_dimensions()
        self.rect.width = self.width
        self.rect.height = self.height
        
        # Tüm rün hücrelerini güncelle (90 derece saat yönünde döndür)
        if self.runes:
            new_runes = {}
            for (old_r, old_c), rune_obj in self.runes.items():
                # Saat yönünde 90 derece: (r, c) -> (c, old_rows - 1 - r)
                new_r = old_c
                new_c = old_rows - 1 - old_r
                new_runes[(new_r, new_c)] = rune_obj
            self.runes = new_runes
        
        # Pop efekti
        self.target_scale = 1.2
        self.angle += 90 

    def flip(self):
        self.matrix = [row[::-1] for row in self.matrix]
        self.update_dimensions()
        self.rect.width = self.width
        self.rect.height = self.height
        
        # Tüm rün hücrelerini güncelle (yatay flip)
        if self.runes:
            new_runes = {}
            for (old_r, old_c), rune_obj in self.runes.items():
                # Yatay flip: (r, c) -> (r, cols - 1 - c)
                new_c = self.cols - 1 - old_c
                new_runes[(old_r, new_c)] = rune_obj
            self.runes = new_runes
        
        self.target_scale = 1.2 

    def update(self):
        # 1. HEDEF BELİRLEME
        target_x = 0
        target_y = 0
        
        if self.dragging:
            mx, my = pygame.mouse.get_pos()
            target_x = mx - self.offset_x
            target_y = my - self.offset_y
            
            self.target_scale = 1.15
            
            # Tilt (Yatma) Hesabı
            delta_x = target_x - self.visual_x
            tilt = -delta_x * 0.5 
            self.target_angle = max(-20, min(20, tilt))
            
        else:
            target_x = self.rect.x
            target_y = self.rect.y
            
            self.target_scale = 1.0
            self.target_angle = 0
            
            # Idle Float (Nefes Alma) - DEVRE DIŞI: Sabit duruş
            # time = pygame.time.get_ticks() / 500
            # float_y = math.sin(time + self.idle_offset) * 3
            # target_y += float_y

        # 2. FİZİK (LERP)
        self.visual_x = lerp(self.visual_x, target_x, 0.25)
        self.visual_y = lerp(self.visual_y, target_y, 0.25)
        self.angle = lerp(self.angle, self.target_angle, 0.15)
        self.scale = lerp(self.scale, self.target_scale, 0.2)

        # Hitbox güncelle (Sadece boşta ise)
        if not self.dragging:
            self.rect.x = int(self.visual_x)
            # Y'yi güncellemiyoruz çünkü idle animasyon hitboxı bozmasın

    def draw(self, surface, x, y, scale=1.0, alpha=255, theme_type='glass'):
        # Ghost blok mu? (Koordinat override edilmişse evet)
        is_ghost = (x != 0 or y != 0)
        
        draw_x = x if is_ghost else self.visual_x
        draw_y = y if is_ghost else self.visual_y
        
        current_angle = 0 if is_ghost else self.angle
        current_scale = scale if is_ghost else (scale * self.scale)
        
        base_tile = TILE_SIZE
        final_tile_size = int(base_tile * current_scale)
        gap = int(final_tile_size * 0.1)
        block_size = final_tile_size - gap
        
        # GOLD bloklarda SABİT çerçeve (pulsating glow KALDIRILDI)
        is_gold_block = (self.tag == 'GOLD' and not is_ghost)

        # Yüzey Oluştur
        surf_w = int(self.width * current_scale * 1.5) + 50
        surf_h = int(self.height * current_scale * 1.5) + 50
        temp_surface = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
        
        center_x = surf_w // 2
        center_y = surf_h // 2
        
        start_draw_x = center_x - (self.cols * final_tile_size) // 2
        start_draw_y = center_y - (self.rows * final_tile_size) // 2

        for r_idx, row in enumerate(self.matrix):
            for c_idx, val in enumerate(row):
                if val == 1:
                    bx = start_draw_x + (c_idx * final_tile_size) + (gap // 2)
                    by = start_draw_y + (r_idx * final_tile_size) + (gap // 2)
                    rect = pygame.Rect(bx, by, block_size, block_size)
                    
                    # GOLD blok için SABİT altın çerçeve
                    if is_gold_block:
                        gold_border_rect = rect.inflate(4, 4)
                        pygame.draw.rect(temp_surface, (255, 215, 0), gold_border_rect, 3, border_radius=8)

                    if theme_type == 'glass':
                        c = self.color
                        if alpha < 255: 
                            pygame.draw.rect(temp_surface, (*c, alpha), rect, border_radius=6)
                        else:
                            dark = (max(0, c[0]-50), max(0, c[1]-50), max(0, c[2]-50))
                            light = (min(255, c[0]+80), min(255, c[1]+80), min(255, c[2]+80))
                            pygame.draw.rect(temp_surface, dark, rect, border_radius=6)
                            pygame.draw.rect(temp_surface, light, rect.inflate(-10, -10), border_radius=4)
                            pygame.draw.rect(temp_surface, c, rect, 2, border_radius=6)
                    
                    elif theme_type == 'pixel':
                         c = (*self.color, alpha) if alpha < 255 else self.color
                         pygame.draw.rect(temp_surface, c, rect)
                         pygame.draw.rect(temp_surface, (0,0,0, alpha) if alpha < 255 else (0,0,0), rect, 2)
                         
        # --- RÜN ÇİZİMİ (Çoklu Rün - Her Hücre İçin) ---
        if self.runes and not is_ghost:
            for (rune_r, rune_c), rune_obj in self.runes.items():
                # Hücre koordinatını piksel koordinatına çevir
                rune_cx = start_draw_x + (rune_c * final_tile_size) + (final_tile_size // 2)
                rune_cy = start_draw_y + (rune_r * final_tile_size) + (final_tile_size // 2)
                
                rune_radius = int(12 * current_scale)
                # Rün arka planı
                pygame.draw.circle(temp_surface, (20, 20, 30), (rune_cx, rune_cy), rune_radius)
                pygame.draw.circle(temp_surface, rune_obj.color, (rune_cx, rune_cy), rune_radius, 2)
                # Rün harfi
                font = pygame.font.SysFont("Arial", int(14 * current_scale), bold=True)
                txt = font.render(rune_obj.icon, True, rune_obj.color)
                txt_rect = txt.get_rect(center=(rune_cx, rune_cy))
                temp_surface.blit(txt, txt_rect)

        # Döndür ve Çiz
        if current_angle != 0:
            rotated_surface = pygame.transform.rotate(temp_surface, current_angle)
            new_rect = rotated_surface.get_rect()
            
            # Bloğun merkezini bul
            block_center_x = draw_x + (self.width * current_scale) / 2
            block_center_y = draw_y + (self.height * current_scale) / 2
            
            new_rect.center = (block_center_x, block_center_y)
            surface.blit(rotated_surface, new_rect)
        else:
            blit_x = draw_x - start_draw_x
            blit_y = draw_y - start_draw_y
            surface.blit(temp_surface, (blit_x, blit_y))