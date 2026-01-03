import pygame
import math
import random
import os
from settings import *

class UIManager:
    def __init__(self, screen):
        self.screen = screen
        self.w, self.h = screen.get_size()
        
        # Fontlar
        self.ui_font = pygame.font.SysFont(FONT_NAME, UI_FONT_SIZE, bold=True)
        self.score_font = pygame.font.SysFont(FONT_NAME, SCORE_FONT_SIZE, bold=True)
        self.large_font = pygame.font.SysFont(FONT_NAME, 80, bold=True)
        self.card_title_font = pygame.font.SysFont(FONT_NAME, 20, bold=True)
        self.card_desc_font = pygame.font.SysFont(FONT_NAME, 16)

        # --- GÖZ ANİMASYONU YÜKLEME (Yeni İnteraktif Sistem) ---
        self.tile_frames = [] # Küçük, işlenmiş kareleri tutacak
        self.bg_grid_state = [] # Her bir karenin durumunu (hangi framede olduğunu) tutacak 2D liste
        self.tile_size = (0, 0) # Karelerin son boyutu

        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(base_path, "assets", "ra.png")
            if not os.path.exists(os.path.join(base_path, "assets")): os.makedirs(os.path.join(base_path, "assets"))
            
            if os.path.exists(path):
                sprite_sheet = pygame.image.load(path).convert_alpha()
                sheet_w, sheet_h = sprite_sheet.get_size()
                
                total_slots = 6      
                active_frames = 5    
                frame_w = sheet_w // total_slots
                frame_h = sheet_h
                
                # --- DEĞİŞİKLİK 1: SKALA KÜÇÜLDÜ (Daha yoğun görünüm) ---
                scale = 2 
                final_w = frame_w * scale
                final_h = frame_h * scale
                self.tile_size = (final_w, final_h)

                # Kareleri tek tek işle ve listeye at
                for i in range(active_frames):
                    # 1. Kes
                    frame_surf = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
                    frame_surf.blit(sprite_sheet, (0, 0), (i * frame_w, 0, frame_w, frame_h))
                    
                    # 2. Büyüt
                    scaled_surf = pygame.transform.scale(frame_surf, (final_w, final_h))
                    
                    # --- DEĞİŞİKLİK 2: ÇERÇEVE EKLE (Blok hissi için) ---
                    # Kare etrafına dijital bir çerçeve çiz
                    border_rect = scaled_surf.get_rect()
                    pygame.draw.rect(scaled_surf, (60, 50, 80), border_rect, 2) # Dış çerçeve
                    pygame.draw.rect(scaled_surf, (30, 20, 50), border_rect.inflate(-2, -2), 1) # İç ince çerçeve
                    
                    self.tile_frames.append(scaled_surf)
                
                print(f"OK: Interactive background assets loaded. Tile size: {self.tile_size}")
            else:
                print(f"WARNING: Image not found at {path}")
                
        except Exception as e:
            print(f"ERROR loading background: {e}")
            self.tile_frames = []

    def draw_sphenks_background(self):
        """Etkileşimli, Duraksamalı Arka Plan Çizimi"""
        if not self.tile_frames:
            self.screen.fill((20, 10, 30))
            for x in range(0, self.w, 40): pygame.draw.line(self.screen, (40, 30, 60), (x, 0), (x, self.h))
            return

        tile_w, tile_h = self.tile_size
        # Ekranı dolduracak kadar satır/sütun hesabı (+1 taşma payı)
        cols = self.w // tile_w + 1
        rows = self.h // tile_h + 1

        # --- DEĞİŞİKLİK 3: GRID DURUMUNU BAŞLAT (İlk çalışma) ---
        if not self.bg_grid_state:
            for r in range(rows):
                row_data = []
                for c in range(cols):
                    # Her kare için: {'frame_idx': Şu anki kare no, 'counter': Hız kontrol sayacı}
                    row_data.append({'frame_idx': 0, 'counter': 0})
                self.bg_grid_state.append(row_data)

        mx, my = pygame.mouse.get_pos()
        
        # Arka plan zemin rengi
        self.screen.fill((15, 5, 25)) 

        # --- IZGARA ÇİZİMİ VE ETKİLEŞİM ---
        animation_speed_ticks = 4 # Animasyon hızı (Düşük = Daha hızlı)

        for r in range(rows):
            for c in range(cols):
                x = c * tile_w
                y = r * tile_h
                tile_rect = pygame.Rect(x, y, tile_w, tile_h)
                
                # Bu karenin verisini al
                tile_data = self.bg_grid_state[r][c]
                
                # Mouse bu karenin üzerinde mi?
                if tile_rect.collidepoint(mx, my):
                    # Üzerindeyse, sayacı artır
                    tile_data['counter'] += 1
                    # Sayaç dolunca bir sonraki kareye geç (Loop)
                    if tile_data['counter'] >= animation_speed_ticks:
                        tile_data['frame_idx'] = (tile_data['frame_idx'] + 1) % len(self.tile_frames)
                        tile_data['counter'] = 0
                    
                    # Hover efekti: Hafifçe parlatalım
                    hover_overlay = pygame.Surface((tile_w, tile_h), pygame.SRCALPHA)
                    hover_overlay.fill((100, 50, 150, 50))
                    self.screen.blit(hover_overlay, (x,y))
                
                # (Else durumunda hiçbir şey yapmıyoruz, yani frame_idx olduğu yerde kalıyor -> PAUSE)

                # İlgili kareyi çiz
                frame_to_draw = self.tile_frames[tile_data['frame_idx']]
                self.screen.blit(frame_to_draw, (x, y))

        # Vignette (Kenar Karartma) - Atmosfer için
        overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 80))
        self.screen.blit(overlay, (0,0))

    # --- DİĞER UI FONKSİYONLARI (Aynen Kalmalı - Değişiklik Yok) ---
    def draw_menu(self, high_score):
        self.draw_sphenks_background() # Menüde de çalışsın
        menu_overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        menu_overlay.fill((0, 0, 0, 100))
        self.screen.blit(menu_overlay, (0,0))
        title = self.large_font.render("SPHENKS", True, ACCENT_COLOR)
        subtitle = self.ui_font.render("VOID GRID PUZZLE", True, (150, 150, 200))
        hs_text = self.ui_font.render(f"HIGH SCORE: {high_score}", True, (255, 215, 0))
        self.screen.blit(title, title.get_rect(center=(self.w//2, self.h//2 - 100)))
        self.screen.blit(subtitle, subtitle.get_rect(center=(self.w//2, self.h//2 - 40)))
        self.screen.blit(hs_text, hs_text.get_rect(center=(self.w//2, self.h//2 + 180)))
        mx, my = pygame.mouse.get_pos()
        play_rect = pygame.Rect(self.w//2 - 100, self.h//2, 200, 60)
        color = ACCENT_COLOR if play_rect.collidepoint(mx, my) else (100, 100, 100)
        pygame.draw.rect(self.screen, color, play_rect, border_radius=10)
        play_txt = self.ui_font.render("PLAY", True, (255,255,255))
        self.screen.blit(play_txt, play_txt.get_rect(center=play_rect.center))
        quit_rect = pygame.Rect(self.w//2 - 100, self.h//2 + 80, 200, 60)
        color = ACCENT_COLOR if quit_rect.collidepoint(mx, my) else (100, 100, 100)
        pygame.draw.rect(self.screen, color, quit_rect, border_radius=10)
        quit_txt = self.ui_font.render("QUIT", True, (255,255,255))
        self.screen.blit(quit_txt, quit_txt.get_rect(center=quit_rect.center))

    def draw_pause(self):
        overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0,0))
        title = self.large_font.render("PAUSED", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(center=(self.w//2, self.h//2 - 100)))
        mx, my = pygame.mouse.get_pos()
        res_rect = pygame.Rect(self.w//2 - 100, self.h//2, 200, 60)
        color = ACCENT_COLOR if res_rect.collidepoint(mx, my) else (100, 100, 100)
        pygame.draw.rect(self.screen, color, res_rect, border_radius=10)
        res_txt = self.ui_font.render("RESUME", True, (255,255,255))
        self.screen.blit(res_txt, res_txt.get_rect(center=res_rect.center))
        menu_rect = pygame.Rect(self.w//2 - 100, self.h//2 + 80, 200, 60)
        color = ACCENT_COLOR if menu_rect.collidepoint(mx, my) else (100, 100, 100)
        pygame.draw.rect(self.screen, color, menu_rect, border_radius=10)
        menu_txt = self.ui_font.render("MAIN MENU", True, (255,255,255))
        self.screen.blit(menu_txt, menu_txt.get_rect(center=menu_rect.center))

    def draw_shop(self, game):
        self.screen.fill(SHOP_BG_COLOR)
        title = self.large_font.render("THE VOID MARKET", True, ACCENT_COLOR)
        money = self.score_font.render(f"Credits: ${game.credits}", True, (100, 255, 100))
        self.screen.blit(title, title.get_rect(center=(self.w//2, 100)))
        self.screen.blit(money, money.get_rect(center=(self.w//2, 160)))
        start_x = (self.w - (3 * 200)) // 2 
        for i, totem in enumerate(game.shop_totems):
            x = start_x + (i * 200); y = self.h // 2 - 110
            card_rect = pygame.Rect(x, y, 160, 220)
            mx, my = pygame.mouse.get_pos()
            bg_col = (60, 50, 70) if card_rect.collidepoint(mx, my) else (40, 30, 50)
            border_col = (255, 215, 0) if totem.rarity == 'Legendary' else (0, 200, 255) if totem.rarity == 'Rare' else (100, 100, 100)
            pygame.draw.rect(self.screen, bg_col, card_rect, border_radius=12)
            pygame.draw.rect(self.screen, border_col, card_rect, 3, border_radius=12)
            name_surf = self.card_title_font.render(totem.name, True, border_col)
            self.screen.blit(name_surf, name_surf.get_rect(center=(x + 80, y + 30)))
            words = totem.desc.split(' '); lines = []; current_line = []
            for word in words:
                current_line.append(word)
                if len(' '.join(current_line)) > 15: lines.append(' '.join(current_line[:-1])); current_line = [word]
            lines.append(' '.join(current_line))
            for j, line in enumerate(lines):
                desc_surf = self.card_desc_font.render(line, True, (200, 200, 200))
                self.screen.blit(desc_surf, desc_surf.get_rect(center=(x + 80, y + 80 + (j*20))))
            price_surf = self.score_font.render(f"${totem.price}", True, (100, 255, 100))
            self.screen.blit(price_surf, price_surf.get_rect(center=(x + 80, y + 180)))
            totem.rect = card_rect 
        inv_label = self.ui_font.render(f"Totems ({len(game.totems)}/{MAX_TOTEM_SLOTS}):", True, TEXT_COLOR)
        self.screen.blit(inv_label, (50, self.h - 140))
        for i in range(MAX_TOTEM_SLOTS):
            slot_rect = pygame.Rect(50 + (i*90), self.h - 110, 70, 90)
            pygame.draw.rect(self.screen, (30, 30, 40), slot_rect, border_radius=8)
            pygame.draw.rect(self.screen, (60, 60, 80), slot_rect, 2, border_radius=8)
            if i < len(game.totems): game.totems[i].draw(self.screen, slot_rect.x, slot_rect.y)
        btn_rect = pygame.Rect(self.w - 220, self.h - 100, 200, 60)
        hover = btn_rect.collidepoint(pygame.mouse.get_pos())
        color = ACCENT_COLOR if hover else (100, 100, 100)
        pygame.draw.rect(self.screen, color, btn_rect, border_radius=10)
        btn_text = self.ui_font.render("NEXT LEVEL >", True, (255, 255, 255))
        self.screen.blit(btn_text, btn_text.get_rect(center=btn_rect.center))

    def draw_level_complete(self, game):
        overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0,0))
        panel_w, panel_h = 600, 400
        panel_rect = pygame.Rect((self.w - panel_w)//2, (self.h - panel_h)//2, panel_w, panel_h)
        pygame.draw.rect(self.screen, (40, 40, 50), panel_rect, border_radius=20)
        pygame.draw.rect(self.screen, ACCENT_COLOR, panel_rect, 4, border_radius=20)
        title = self.large_font.render("LEVEL COMPLETE", True, (0, 255, 100))
        score_info = self.score_font.render(f"Score: {game.score}", True, TEXT_COLOR)
        click_info = self.ui_font.render("- Click to Enter Shop -", True, (0, 200, 255))
        self.screen.blit(title, title.get_rect(center=(self.w//2, self.h//2 - 50)))
        self.screen.blit(score_info, score_info.get_rect(center=(self.w//2, self.h//2 + 20)))
        if (pygame.time.get_ticks() // 500) % 2 == 0: self.screen.blit(click_info, click_info.get_rect(center=(self.w//2, self.h//2 + 100)))

    def draw_game_over(self, game):
        overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        overlay.fill((20, 0, 0, 220)) 
        self.screen.blit(overlay, (0,0))
        go_text = self.large_font.render("GAME OVER", True, (255, 50, 50))
        score_text = self.score_font.render(f"Final Score: {game.score}", True, TEXT_COLOR)
        hs_text = self.ui_font.render(f"High Score: {game.high_score}", True, (255, 215, 0))
        restart_text = self.ui_font.render("Press 'R' to Retry", True, (200, 200, 200))
        self.screen.blit(go_text, go_text.get_rect(center=(self.w//2, self.h//2 - 50)))
        self.screen.blit(score_text, score_text.get_rect(center=(self.w//2, self.h//2 + 20)))
        self.screen.blit(hs_text, hs_text.get_rect(center=(self.w//2, self.h//2 + 60)))
        self.screen.blit(restart_text, restart_text.get_rect(center=(self.w//2, self.h//2 + 120)))

    def draw_trash_bin(self, hovered=False):
        w, h = 80, 80
        x = self.w - w - 20
        y = (self.h // 2) - (h // 2)
        rect = pygame.Rect(x, y, w, h)
        color = (220, 50, 50) if hovered else (60, 30, 30)
        border_col = (255, 150, 150) if hovered else (120, 50, 50)
        pygame.draw.rect(self.screen, color, rect, border_radius=15)
        pygame.draw.rect(self.screen, border_col, rect, 5 if hovered else 2, border_radius=15)
        pygame.draw.rect(self.screen, border_col, (x+10, y+20, w-20, 5)) 
        pygame.draw.rect(self.screen, border_col, (x+25, y+15, 30, 5))   
        pygame.draw.rect(self.screen, border_col, (x+20, y+25, 40, 40), 2)
        pygame.draw.line(self.screen, border_col, (x+30, y+30), (x+30, y+60), 2)
        pygame.draw.line(self.screen, border_col, (x+40, y+30), (x+40, y+60), 2)
        pygame.draw.line(self.screen, border_col, (x+50, y+30), (x+50, y+60), 2)
        cost_color = (255, 255, 255) if hovered else (150, 100, 100)
        cost_surf = self.ui_font.render(f"-${DISCARD_COST}", True, cost_color)
        self.screen.blit(cost_surf, cost_surf.get_rect(center=(x + w//2, y - 15)))
        return rect

    def draw_combo_bar(self, combo_val, max_combo, is_hyper):
        bar_w = 400; bar_h = 20; x = (self.w - bar_w) // 2; y = 120 
        pygame.draw.rect(self.screen, (30, 30, 40), (x, y, bar_w, bar_h), border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 150), (x, y, bar_w, bar_h), 2, border_radius=10)
        fill_pct = min(1.0, combo_val / max_combo)
        fill_w = int(bar_w * fill_pct)
        if fill_w > 0:
            if is_hyper:
                t = pygame.time.get_ticks() * 0.01
                r = int((math.sin(t) + 1) * 127)
                g = int((math.sin(t + 2) + 1) * 127)
                b = int((math.sin(t + 4) + 1) * 127)
                bar_color = (r, g, b)
            else: bar_color = (255, int(255 * (1 - fill_pct)), 0)
            pygame.draw.rect(self.screen, bar_color, (x+2, y+2, fill_w-4, bar_h-4), border_radius=8)
        lbl = "HYPER MODE!" if is_hyper else "COMBO"
        lbl_surf = self.ui_font.render(lbl, True, (255, 255, 255))
        self.screen.blit(lbl_surf, (x + bar_w + 10, y))

    def draw_void_portal(self, game):
        center_x = self.w - 100; center_y = self.h - 100; radius = 50
        for i in range(3):
            angle = game.portal_angle * (i + 1) * 0.8; color = (100 + i*40, 20, 200) 
            rect = pygame.Rect(center_x - radius + (i*5), center_y - radius + (i*5), (radius - i*5)*2, (radius - i*5)*2)
            pygame.draw.arc(self.screen, color, rect, angle, angle + 2, 4)
            pygame.draw.arc(self.screen, color, rect, angle + 3.14, angle + 3.14 + 2, 4)
        pulse = math.sin(pygame.time.get_ticks() * 0.005) * 4
        pygame.draw.circle(self.screen, (30, 0, 60), (center_x, center_y), radius - 15 + pulse)
        stok_text = self.score_font.render(str(game.void_count), True, (0, 255, 255))
        text_rect = stok_text.get_rect(center=(center_x, center_y))
        label_text = self.ui_font.render("VOID", True, (180, 150, 220))
        label_rect = label_text.get_rect(center=(center_x, center_y - radius - 20))
        self.screen.blit(stok_text, text_rect); self.screen.blit(label_text, label_rect)

    def draw_hud(self, game):
        for i in range(MAX_TOTEM_SLOTS):
            slot_rect = pygame.Rect(50 + (i*50), 50, 40, 50)
            pygame.draw.rect(self.screen, (40, 40, 50), slot_rect, border_radius=5)
            pygame.draw.rect(self.screen, (80, 80, 100), slot_rect, 1, border_radius=5)
        score_text = self.score_font.render(f"{game.score}", True, ACCENT_COLOR)
        score_rect = score_text.get_rect(center=(self.w // 2, self.h * 0.05)) 
        target_text = self.ui_font.render(f"LVL {game.level} | TARGET: {game.level_target}", True, (150, 150, 150))
        target_rect = target_text.get_rect(center=(self.w // 2, self.h * 0.09))
        money_text = self.ui_font.render(f"${game.credits}", True, (100, 255, 100))
        self.screen.blit(money_text, (self.w - 150, 50))
        self.screen.blit(score_text, score_rect); self.screen.blit(target_text, target_rect)
        if game.current_boss:
            boss_text = self.score_font.render(f"BOSS: {game.current_boss}", True, (255, 50, 50))
            boss_rect = boss_text.get_rect(center=(self.w // 2, self.h * 0.13))
            if (pygame.time.get_ticks() // 300) % 2 == 0: self.screen.blit(boss_text, boss_rect)
        self.draw_void_portal(game)

    def draw_glyphs(self, game):
        start_x = 50; start_y = self.h - 220
        lbl = self.ui_font.render("GLYPHS:", True, (200, 200, 200))
        self.screen.blit(lbl, (start_x, start_y - 30))
        for i in range(MAX_GLYPH_SLOTS):
            slot_rect = pygame.Rect(start_x, start_y + (i * 60), 50, 50)
            pygame.draw.rect(self.screen, (30, 30, 40), slot_rect, border_radius=5)
            pygame.draw.rect(self.screen, (60, 60, 80), slot_rect, 1, border_radius=5)
            if i < len(game.glyphs):
                game.glyphs[i].draw(self.screen, slot_rect.x, slot_rect.y)
                if game.glyphs[i].hovered:
                    tip_surf = self.ui_font.render(f"{game.glyphs[i].name}: {game.glyphs[i].desc}", True, ACCENT_COLOR)
                    self.screen.blit(tip_surf, (slot_rect.right + 10, slot_rect.centery - 10))