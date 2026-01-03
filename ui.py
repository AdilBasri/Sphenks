# ui.py
import pygame
import os
import random
import math
from settings import *

class VoidWidget(pygame.sprite.Sprite):
    def __init__(self, x, y, scale=0.5):
        super().__init__()
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(base_path, "assets", "void.png")
            sprite_sheet = pygame.image.load(path).convert_alpha()
        except FileNotFoundError:
            sprite_sheet = pygame.Surface((64, 16), pygame.SRCALPHA)
            sprite_sheet.fill((255, 0, 255))
        
        sheet_w = sprite_sheet.get_width()
        sheet_h = sprite_sheet.get_height()
        frame_w = sheet_w // 4
        frame_h = sheet_h
        
        base_frames = []
        for i in range(4):
            frame = sprite_sheet.subsurface((i * frame_w, 0, frame_w, frame_h))
            if scale != 1:
                frame = pygame.transform.scale(frame, (int(frame_w * scale), int(frame_h * scale)))
            base_frames.append(frame)
            
        self.animation_list = [base_frames[i] for i in [0, 1, 2, 3, 2, 1]]
        self.animation_list += [pygame.transform.flip(f, True, False) for f in self.animation_list]
        
        self.frame_index = 0
        self.image = self.animation_list[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.bottomright = (x, y)
        self.last_update = pygame.time.get_ticks()
        self.anim_speed = 100

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.anim_speed:
            self.last_update = now
            self.frame_index = (self.frame_index + 1) % len(self.animation_list)
            self.image = self.animation_list[self.frame_index]

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class UIManager:
    def __init__(self):
        self.font_small = pygame.font.SysFont(FONT_NAME, 14)
        self.font_reg = pygame.font.SysFont(FONT_NAME, UI_FONT_SIZE)
        self.font_bold = pygame.font.SysFont(FONT_NAME, UI_FONT_SIZE, bold=True)
        self.font_score = pygame.font.SysFont(FONT_NAME, SCORE_FONT_SIZE, bold=True)
        self.font_big = pygame.font.SysFont(FONT_NAME, BIG_FONT_SIZE, bold=True)
        self.title_font = pygame.font.SysFont(FONT_NAME, 60, bold=True)
        
        # Void Widget: Sağ Alt Köşe
        self.void_widget = VoidWidget(VIRTUAL_W - 20, VIRTUAL_H - 20, scale=0.8)
        
        self.bg_tiles = []
        self.tile_w = 0
        self.tile_h = 0
        self.load_bg_assets()

    def load_bg_assets(self):
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(base_path, "assets", "ra.png")
            if os.path.exists(path):
                sprite_sheet = pygame.image.load(path).convert_alpha()
                sheet_w, sheet_h = sprite_sheet.get_size()
                total_frames = 6
                active_frames = 5
                frame_w = sheet_w // total_frames
                frame_h = sheet_h
                scale = 1.0
                self.tile_w = int(frame_w * scale)
                self.tile_h = int(frame_h * scale)
                self.bg_frames = []
                for i in range(active_frames):
                    frame = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
                    frame.blit(sprite_sheet, (0, 0), (i * frame_w, 0, frame_w, frame_h))
                    self.bg_frames.append(frame)
                cols = VIRTUAL_W // self.tile_w + 1
                rows = VIRTUAL_H // self.tile_h + 1
                for r in range(rows):
                    row_data = []
                    for c in range(cols):
                        row_data.append({'frame': 0, 'animating': False, 'timer': 0})
                    self.bg_tiles.append(row_data)
        except Exception as e:
            print(f"BG Load Error: {e}")

    def update(self):
        self.void_widget.update()
        if self.bg_tiles:
            mx, my = pygame.mouse.get_pos()
            rows = len(self.bg_tiles)
            cols = len(self.bg_tiles[0])
            for r in range(rows):
                for c in range(cols):
                    tile = self.bg_tiles[r][c]
                    if not tile['animating']:
                        rect = pygame.Rect(c*self.tile_w, r*self.tile_h, self.tile_w, self.tile_h)
                        if rect.collidepoint(mx, my):
                            tile['animating'] = True
                            tile['frame'] = 1
                    if tile['animating']:
                        tile['timer'] += 1
                        if tile['timer'] > 5:
                            tile['timer'] = 0
                            tile['frame'] += 1
                            if tile['frame'] >= len(self.bg_frames):
                                tile['frame'] = 0
                                tile['animating'] = False

    def draw_bg(self, surface):
        surface.fill(BG_COLOR)
        if self.bg_tiles:
            rows = len(self.bg_tiles)
            cols = len(self.bg_tiles[0])
            for r in range(rows):
                for c in range(cols):
                    tile = self.bg_tiles[r][c]
                    frame_idx = tile['frame']
                    img = self.bg_frames[frame_idx]
                    img.set_alpha(100) 
                    surface.blit(img, (c*self.tile_w, r*self.tile_h))
        o = pygame.Surface((VIRTUAL_W, VIRTUAL_H), pygame.SRCALPHA)
        pygame.draw.rect(o, (10, 5, 20, 150), o.get_rect())
        surface.blit(o, (0,0))

    def draw_sidebar(self, surface, game):
        panel_rect = pygame.Rect(0, 0, SIDEBAR_WIDTH, VIRTUAL_H)
        pygame.draw.rect(surface, SIDEBAR_BG_COLOR, panel_rect)
        pygame.draw.line(surface, PANEL_BORDER, (SIDEBAR_WIDTH, 0), (SIDEBAR_WIDTH, VIRTUAL_H), 4)
        
        cx = SIDEBAR_WIDTH // 2
        y_cursor = 30
        
        ante_txt = self.font_bold.render(f"ANTE {game.ante} / 8", True, (200, 200, 200))
        surface.blit(ante_txt, ante_txt.get_rect(center=(cx, y_cursor)))
        y_cursor += 30
        
        round_name = ["Small Blind", "Big Blind", "Boss Blind"][game.round - 1]
        round_lbl = self.font_bold.render(round_name, True, TOTAL_COLOR)
        surface.blit(round_lbl, round_lbl.get_rect(center=(cx, y_cursor)))
        y_cursor += 30
        
        goal_lbl = self.font_small.render(f"Goal: {game.level_target}", True, (150, 150, 150))
        surface.blit(goal_lbl, goal_lbl.get_rect(center=(cx, y_cursor)))
        y_cursor += 40
        
        # Scoring Box
        score_box_h = 160
        score_box = pygame.Rect(15, y_cursor, SIDEBAR_WIDTH - 30, score_box_h)
        pygame.draw.rect(surface, SCORING_BOX_BG, score_box, border_radius=15)
        pygame.draw.rect(surface, PANEL_BORDER, score_box, 2, border_radius=15)
        
        box_cx = score_box.centerx
        box_y = score_box.y + 20
        
        chips_val = game.scoring_data['base'] if game.state == STATE_SCORING else 0
        chips_txt = self.font_score.render(str(chips_val), True, CHIPS_COLOR)
        surface.blit(chips_txt, chips_txt.get_rect(midleft=(score_box.x + 20, box_y)))
        
        lbl_chips = self.font_small.render("Chips", True, CHIPS_COLOR)
        surface.blit(lbl_chips, lbl_chips.get_rect(midleft=(score_box.x + 20, box_y + 20)))
        
        x_txt = self.font_bold.render("X", True, (255,255,255))
        surface.blit(x_txt, x_txt.get_rect(center=(box_cx, box_y + 10)))
        
        mult_val = game.scoring_data['mult'] if game.state == STATE_SCORING else 0.0
        mult_txt = self.font_score.render(f"{mult_val:.1f}", True, MULT_COLOR)
        surface.blit(mult_txt, mult_txt.get_rect(midright=(score_box.right - 20, box_y)))
        
        lbl_mult = self.font_small.render("Mult", True, MULT_COLOR)
        surface.blit(lbl_mult, lbl_mult.get_rect(midright=(score_box.right - 20, box_y + 20)))
        
        box_y += 60
        total_lbl = self.font_reg.render("Total", True, (200, 200, 200))
        surface.blit(total_lbl, total_lbl.get_rect(center=(box_cx, box_y)))
        
        box_y += 35
        shake = 0
        if game.state == STATE_SCORING: shake = random.randint(-1, 1)
        
        hand_total = game.scoring_data['total'] if game.state == STATE_SCORING else 0
        total_txt = self.font_big.render(str(hand_total), True, TOTAL_COLOR)
        surface.blit(total_txt, total_txt.get_rect(center=(box_cx + shake, box_y + shake)))
        
        y_cursor += score_box_h + 30
        
        lbl_round_score = self.font_reg.render("Round Score", True, (150, 150, 150))
        surface.blit(lbl_round_score, lbl_round_score.get_rect(center=(cx, y_cursor)))
        y_cursor += 30
        
        sc_col = (255, 255, 255)
        if game.score >= game.level_target: sc_col = (100, 255, 100)
        curr_score_txt = self.font_score.render(str(game.score), True, sc_col)
        surface.blit(curr_score_txt, curr_score_txt.get_rect(center=(cx, y_cursor)))
        
        # --- MENU BUTONU ---
        menu_btn = pygame.Rect(30, VIRTUAL_H - 60, SIDEBAR_WIDTH - 60, 40)
        col = (70, 60, 80)
        if menu_btn.collidepoint(pygame.mouse.get_pos()): col = (90, 80, 100)
        pygame.draw.rect(surface, col, menu_btn, border_radius=8)
        pygame.draw.rect(surface, (150, 150, 150), menu_btn, 1, border_radius=8)
        
        menu_txt = self.font_bold.render("MENU", True, (255, 255, 255))
        surface.blit(menu_txt, menu_txt.get_rect(center=menu_btn.center))
        
        # Bu rect'i game loop'ta tıklama için kullanacağız, return edebilir veya game objesine atayabiliriz
        # Pratik olması için game objesine bir attrib olarak ekleyelim (hacky ama hızlı çözüm)
        game.menu_btn_rect = menu_btn

    def draw_hud_elements(self, surface, game):
        # Void
        self.void_widget.draw(surface)
        v_txt = self.font_bold.render(str(game.void_count), True, (255,255,255))
        surface.blit(v_txt, v_txt.get_rect(center=self.void_widget.rect.center))
        
        # Para (Sağ Üst Köşe)
        m_bg = pygame.Rect(VIRTUAL_W - 100, 10, 90, 40)
        pygame.draw.rect(surface, (20, 40, 20), m_bg, border_radius=20)
        pygame.draw.rect(surface, (50, 200, 50), m_bg, 2, border_radius=20)
        
        m_txt = self.font_score.render(f"${game.credits}", True, (100, 255, 100))
        surface.blit(m_txt, m_txt.get_rect(center=m_bg.center))

    def draw_menu(self, surface, high_score):
        title = self.title_font.render("SPHENKS", True, ACCENT_COLOR)
        st = self.font_reg.render("LEGACY OF RA", True, (150, 150, 200))
        hs = self.font_small.render(f"BEST: {high_score}", True, (255, 215, 0))
        cx, cy = VIRTUAL_W//2, VIRTUAL_H//2
        
        surface.blit(title, title.get_rect(center=(cx, cy - 80)))
        surface.blit(st, st.get_rect(center=(cx, cy - 40)))
        surface.blit(hs, hs.get_rect(center=(cx, cy + 140)))
        
        # Butonlar
        btns = [("PLAY", 0), ("SETTINGS", 60), ("EXIT", 120)]
        self.menu_buttons = [] # Tıklama kontrolü için sakla
        
        base_y = cy 
        for text, offset in btns:
            rect = pygame.Rect(0, 0, 200, 50)
            rect.center = (cx, base_y + offset)
            
            col = ACCENT_COLOR if text == "PLAY" else (60, 60, 70)
            if rect.collidepoint(pygame.mouse.get_pos()):
                col = (min(255, col[0]+30), min(255, col[1]+30), min(255, col[2]+30))
            
            pygame.draw.rect(surface, col, rect, border_radius=8)
            txt = self.font_bold.render(text, True, (0,0,0) if text == "PLAY" else (200,200,200))
            surface.blit(txt, txt.get_rect(center=rect.center))
            self.menu_buttons.append((rect, text))

    def draw_pause_overlay(self, surface):
        o = pygame.Surface((VIRTUAL_W, VIRTUAL_H), pygame.SRCALPHA)
        o.fill((0,0,0,200))
        surface.blit(o, (0,0))
        
        cx, cy = VIRTUAL_W//2, VIRTUAL_H//2
        
        # Kutu
        box = pygame.Rect(0, 0, 400, 250)
        box.center = (cx, cy)
        pygame.draw.rect(surface, (30, 30, 40), box, border_radius=15)
        pygame.draw.rect(surface, (100, 100, 100), box, 2, border_radius=15)
        
        q = self.font_bold.render("Return to Main Menu?", True, (255, 255, 255))
        surface.blit(q, q.get_rect(center=(cx, cy - 40)))
        
        # Evet / Hayır
        yes_btn = pygame.Rect(0, 0, 100, 40)
        yes_btn.center = (cx - 70, cy + 40)
        no_btn = pygame.Rect(0, 0, 100, 40)
        no_btn.center = (cx + 70, cy + 40)
        
        mx, my = pygame.mouse.get_pos()
        
        # Yes
        c_yes = (200, 50, 50)
        if yes_btn.collidepoint(mx, my): c_yes = (255, 80, 80)
        pygame.draw.rect(surface, c_yes, yes_btn, border_radius=5)
        yt = self.font_bold.render("YES", True, (255,255,255))
        surface.blit(yt, yt.get_rect(center=yes_btn.center))
        
        # No
        c_no = (50, 150, 50)
        if no_btn.collidepoint(mx, my): c_no = (80, 200, 80)
        pygame.draw.rect(surface, c_no, no_btn, border_radius=5)
        nt = self.font_bold.render("NO", True, (255,255,255))
        surface.blit(nt, nt.get_rect(center=no_btn.center))
        
        # Tıklama için sakla
        self.pause_buttons = {'YES': yes_btn, 'NO': no_btn}

    def draw_shop(self, surface, game):
        overlay = pygame.Surface((VIRTUAL_W, VIRTUAL_H), pygame.SRCALPHA)
        overlay.fill(SHOP_BG_COLOR)
        surface.blit(overlay, (0,0))
        lbl = self.font_big.render("BAZAAR", True, ACCENT_COLOR)
        surface.blit(lbl, lbl.get_rect(center=(VIRTUAL_W//2, 30)))
        start_x = (VIRTUAL_W - (3*90)) // 2
        for i, totem in enumerate(game.shop_totems):
            rect = pygame.Rect(start_x + (i*90), 80, 70, 100)
            col = (50, 40, 60)
            if rect.collidepoint(pygame.mouse.get_pos()): col = (70, 60, 80)
            pygame.draw.rect(surface, col, rect, border_radius=4)
            pygame.draw.rect(surface, ACCENT_COLOR, rect, 1, border_radius=4)
            n = self.font_small.render(totem.name[:8], True, (255,255,255))
            p = self.font_bold.render(f"${totem.price}", True, (100, 255, 100))
            surface.blit(n, (rect.x + 2, rect.y + 5))
            surface.blit(p, (rect.x + 2, rect.bottom - 20))
            totem.rect = rect
        nxt = self.font_bold.render("NEXT ROUND >", True, (255,255,255))
        nxt_rect = nxt.get_rect(bottomright=(VIRTUAL_W - 30, VIRTUAL_H - 30))
        surface.blit(nxt, nxt_rect)

    def draw_game_over(self, surface, score):
        o = pygame.Surface((VIRTUAL_W, VIRTUAL_H), pygame.SRCALPHA)
        o.fill((0,0,0,220))
        surface.blit(o, (0,0))
        t = self.title_font.render("GAME OVER", True, (255, 50, 50))
        s = self.font_big.render(f"Score: {score}", True, (255, 255, 255))
        r = self.font_reg.render("Click to Return Menu", True, (150, 150, 150))
        cx, cy = VIRTUAL_W//2, VIRTUAL_H//2
        surface.blit(t, t.get_rect(center=(cx, cy - 50)))
        surface.blit(s, s.get_rect(center=(cx, cy + 10)))
        surface.blit(r, r.get_rect(center=(cx, cy + 60)))