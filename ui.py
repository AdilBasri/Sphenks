# ui.py
import pygame
import os
import random
from settings import *

class VoidWidget(pygame.sprite.Sprite):
    def __init__(self, cx, cy):
        super().__init__()
        # 1. Görseli Yükle
        try:
            # assets klasöründe void.png olmalı
            base_path = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(base_path, "assets", "void.png")
            sprite_sheet = pygame.image.load(path).convert_alpha()
        except FileNotFoundError:
            # Yedek kare (Dosya yoksa mor kutu)
            sprite_sheet = pygame.Surface((64, 16), pygame.SRCALPHA)
            sprite_sheet.fill((255, 0, 255))
        
        # 2. Kareleri Ayıkla
        sheet_w = sprite_sheet.get_width()
        sheet_h = sprite_sheet.get_height()
        frame_w = sheet_w // 4
        frame_h = sheet_h
        
        # --- İSTENEN KARMAŞIK DÖNGÜ MANTIĞI ---
        base_frames = []
        for i in range(4):
            frame = sprite_sheet.subsurface((i * frame_w, 0, frame_w, frame_h))
            # Scale
            if VOID_UI_SCALE != 1:
                frame = pygame.transform.scale(frame, (int(frame_w * VOID_UI_SCALE), int(frame_h * VOID_UI_SCALE)))
            base_frames.append(frame)
            
        # 1-2-3-4 -> 3-2-1 mantığı (0, 1, 2, 3, 2, 1)
        ping_pong_indices = [0, 1, 2, 3, 2, 1]
        normal_sequence = [base_frames[i] for i in ping_pong_indices]
        
        # Ayna (Flip) Dizisi
        mirrored_sequence = [pygame.transform.flip(f, True, False) for f in normal_sequence]
        
        # Birleştir: Normal + Ayna
        self.animation_list = normal_sequence + mirrored_sequence
        
        self.frame_index = 0
        self.image = self.animation_list[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (cx, cy)
        
        self.last_update = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > VOID_ANIMATION_SPEED:
            self.last_update = now
            self.frame_index = (self.frame_index + 1) % len(self.animation_list)
            self.image = self.animation_list[self.frame_index]

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class UIManager:
    def __init__(self):
        self.ui_font = pygame.font.SysFont(FONT_NAME, UI_FONT_SIZE, bold=True)
        self.score_font = pygame.font.SysFont(FONT_NAME, SCORE_FONT_SIZE, bold=True)
        self.title_font = pygame.font.SysFont(FONT_NAME, 40, bold=True)
        self.small_font = pygame.font.SysFont(FONT_NAME, 10)

        # Göz Animasyon Sistemi
        self.tile_frames = [] 
        self.bg_grid_state = [] 
        self.tile_w = 0
        self.tile_h = 0
        self.load_ra_assets()

        # Void Animasyon Widget'ı (Sağ Alt Köşe)
        self.void_widget = VoidWidget(VIRTUAL_W - 25, VIRTUAL_H - 25)

    def update(self):
        """UI Animasyonlarını günceller"""
        self.void_widget.update()

    def load_ra_assets(self):
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(base_path, "assets", "ra.png")
            
            if os.path.exists(path):
                sprite_sheet = pygame.image.load(path).convert_alpha()
                sheet_w, sheet_h = sprite_sheet.get_size()
                
                total_slots = 6      
                active_frames = 5    
                frame_w = sheet_w // total_slots
                frame_h = sheet_h
                
                scale = 1.0
                self.tile_w = int(frame_w * scale)
                self.tile_h = int(frame_h * scale)
                
                for i in range(active_frames):
                    frame = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
                    frame.blit(sprite_sheet, (0, 0), (i * frame_w, 0, frame_w, frame_h))
                    scaled = pygame.transform.scale(frame, (self.tile_w, self.tile_h))
                    pygame.draw.rect(scaled, (30, 20, 40), scaled.get_rect(), 1)
                    self.tile_frames.append(scaled)
                
                cols = VIRTUAL_W // self.tile_w + 1
                rows = VIRTUAL_H // self.tile_h + 1
                for r in range(rows):
                    row_data = []
                    for c in range(cols):
                        row_data.append({'frame_index': 0, 'anim_timer': 0, 'active': False})
                    self.bg_grid_state.append(row_data)
        except Exception as e:
            print(f"BG Load Error: {e}")

    def draw_bg(self, surface, mouse_pos):
        if not self.tile_frames:
            surface.fill(BG_COLOR)
            return

        mx, my = mouse_pos
        cols = len(self.bg_grid_state[0])
        rows = len(self.bg_grid_state)
        
        for r in range(rows):
            for c in range(cols):
                data = self.bg_grid_state[r][c]
                x = c * self.tile_w
                y = r * self.tile_h
                rect = pygame.Rect(x, y, self.tile_w, self.tile_h)
                
                if rect.collidepoint(mx, my):
                    data['active'] = True
                
                if data['active']:
                    data['anim_timer'] += 1
                    if data['anim_timer'] >= 5:
                        data['frame_index'] = (data['frame_index'] + 1) % len(self.tile_frames)
                        data['anim_timer'] = 0
                        if data['frame_index'] == 0: data['active'] = False
                else:
                    data['frame_index'] = 0
                
                frame = self.tile_frames[data['frame_index']]
                surface.blit(frame, (x, y))
        
        o = pygame.Surface((VIRTUAL_W, VIRTUAL_H), pygame.SRCALPHA)
        o.fill((10, 5, 20, 180)) 
        surface.blit(o, (0,0))

    def draw_hud(self, surface, game):
        # Skor
        s = self.score_font.render(str(game.score), True, ACCENT_COLOR)
        surface.blit(s, (10, 5))
        
        t = self.small_font.render(f"GOAL: {game.level_target}", True, (200, 200, 200))
        surface.blit(t, (10, 30))
        
        # Para
        m = self.ui_font.render(f"${game.credits}", True, (100, 255, 100))
        surface.blit(m, (VIRTUAL_W - m.get_width() - 10, 5))
        
        # Void Ammo (Artık Animasyonlu Sprite Çiziyoruz)
        self.void_widget.draw(surface)
        
        # Ammo Sayısı (Sprite'ın üzerine ortala)
        v = self.small_font.render(str(game.void_count), True, (255, 255, 255))
        v_rect = v.get_rect(center=self.void_widget.rect.center)
        surface.blit(v, v_rect)

    def draw_menu(self, surface, high_score):
        title = self.title_font.render("SPHENKS", True, ACCENT_COLOR)
        st = self.small_font.render("LEGACY OF RA", True, (150, 150, 200))
        hs = self.small_font.render(f"BEST: {high_score}", True, (255, 215, 0))
        
        surface.blit(title, title.get_rect(center=(VIRTUAL_W//2, VIRTUAL_H//2 - 30)))
        surface.blit(st, st.get_rect(center=(VIRTUAL_W//2, VIRTUAL_H//2 + 5)))
        surface.blit(hs, hs.get_rect(center=(VIRTUAL_W//2, VIRTUAL_H//2 + 80)))
        
        btn = pygame.Rect(0, 0, 100, 30)
        btn.center = (VIRTUAL_W//2, VIRTUAL_H//2 + 40)
        pygame.draw.rect(surface, ACCENT_COLOR, btn, border_radius=5)
        txt = self.ui_font.render("PLAY", True, (0,0,0))
        surface.blit(txt, txt.get_rect(center=btn.center))

    def draw_shop(self, surface, game):
        surface.fill(SHOP_BG_COLOR)
        lbl = self.ui_font.render("MARKET", True, ACCENT_COLOR)
        surface.blit(lbl, lbl.get_rect(center=(VIRTUAL_W//2, 20)))
        
        start_x = 40
        for i, totem in enumerate(game.shop_totems):
            rect = pygame.Rect(start_x + (i*90), 50, 70, 100)
            col = (50, 40, 60)
            if rect.collidepoint(pygame.mouse.get_pos()): col = (70, 60, 80)
               
            pygame.draw.rect(surface, col, rect, border_radius=4)
            pygame.draw.rect(surface, ACCENT_COLOR, rect, 1, border_radius=4)
            
            n = self.small_font.render(totem.name[:8], True, (255,255,255))
            p = self.ui_font.render(f"${totem.price}", True, (100, 255, 100))
            
            surface.blit(n, (rect.x + 2, rect.y + 5))
            surface.blit(p, (rect.x + 2, rect.bottom - 20))
            totem.rect = rect

        nxt = self.ui_font.render("NEXT LEVEL >", True, (255,255,255))
        surface.blit(nxt, (VIRTUAL_W - 100, VIRTUAL_H - 25))
    
    def draw_game_over(self, surface, score):
        o = pygame.Surface((VIRTUAL_W, VIRTUAL_H), pygame.SRCALPHA)
        o.fill((0,0,0,200))
        surface.blit(o, (0,0))
        t = self.title_font.render("GAME OVER", True, (255, 50, 50))
        s = self.ui_font.render(f"Final: {score}", True, (255, 255, 255))
        surface.blit(t, t.get_rect(center=(VIRTUAL_W//2, VIRTUAL_H//2 - 20)))
        surface.blit(s, s.get_rect(center=(VIRTUAL_W//2, VIRTUAL_H//2 + 20)))