# ui.py
import pygame
import os
import random
import math
from settings import *

# --- MENÜ İÇİN UÇUŞAN DEKORATİF BLOK ---
class MenuBlock:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(20, 40)
        self.color = random.choice(list(SHAPE_COLORS.values()))
        self.speed_y = random.uniform(-1, -3) # Yukarı doğru
        self.speed_x = random.uniform(-1, 1)
        self.angle = random.randint(0, 360)
        self.spin = random.uniform(-2, 2)
        
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.angle += self.spin
        # Ekran dışına çıkarsa aşağıdan tekrar girsin
        if self.y < -50:
            self.y = VIRTUAL_H + 50
            self.x = random.randint(0, VIRTUAL_W)
            self.color = random.choice(list(SHAPE_COLORS.values()))
            
    def draw(self, surface):
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        # Cam (Glass) efekti
        pygame.draw.rect(s, (*self.color, 150), (0,0,self.size,self.size), border_radius=4)
        pygame.draw.rect(s, (255,255,255, 100), (0,0,self.size,self.size), 2, border_radius=4)
        
        rotated = pygame.transform.rotate(s, self.angle)
        surface.blit(rotated, rotated.get_rect(center=(self.x, self.y)))

# --- LOGO HARFLERİ İÇİN GELİŞMİŞ FİZİK SINIFI ---
class TitleLetter:
    def __init__(self, img, x, y):
        self.original_image = img
        self.width = img.get_width()
        self.height = img.get_height()
        
        # Merkez noktası (Origin)
        self.origin_x = x
        self.origin_y = y
        
        # Fizik Konumu
        self.x = x
        self.y = y
        self.vel_x = 0
        self.vel_y = 0
        
        # Sürükleme Durumu
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        
        # Döndürme (Tilt) Efekti
        self.angle = 0
        self.target_angle = 0
        
        # Yay (Spring) Ayarları - "Jelly" hissi için
        self.stiffness = 0.08  # Yay sertliği (Daha düşük = daha gevşek)
        self.damping = 0.90    # Sönümleme (Enerji kaybı)

    def resolve_collision(self, other):
        """Diğer harfle çarpışmayı kontrol et ve tepki ver"""
        if self is other: return

        # Basit mesafe kontrolü (Dairesel Hitbox varsayımı daha yumuşak hissettirir)
        dx = self.x - other.x
        dy = self.y - other.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # İki harfin yarıçapları toplamı (biraz overlap payı bırakıyoruz * 0.85)
        min_dist = (self.width/2 + other.width/2) * 0.85
        
        if distance < min_dist and distance > 0:
            # Çarpışma var! İtme kuvveti hesapla
            overlap = min_dist - distance
            force = overlap * 0.1 # Yaylanma kuvveti
            
            # Normal vektör (İtme yönü)
            nx = dx / distance
            ny = dy / distance
            
            # Newton'un 3. Yasası: Etki - Tepki
            # Eğer biri sürükleniyorsa, sadece diğeri itilsin (Buldozer etkisi)
            if self.dragging and not other.dragging:
                other.vel_x -= nx * force * 2
                other.vel_y -= ny * force * 2
            elif other.dragging and not self.dragging:
                self.vel_x += nx * force * 2
                self.vel_y += ny * force * 2
            else:
                # İkisi de serbestse birbirini itsin
                self.vel_x += nx * force
                self.vel_y += ny * force
                other.vel_x -= nx * force
                other.vel_y -= ny * force

    def update(self):
        # 1. Sürükleme Mantığı
        if self.dragging:
            mx, my = pygame.mouse.get_pos()
            target_x = mx - self.drag_offset_x
            target_y = my - self.drag_offset_y
            
            # Hızı hesapla (Mouse hareketine göre)
            self.vel_x = (target_x - self.x) * 0.5
            self.vel_y = (target_y - self.y) * 0.5
            
            self.x = target_x
            self.y = target_y
            
            # Sürüklenirken daha fazla eğilsin
            self.target_angle = -self.vel_x * 1.5 
            
        else:
            # 2. Yay (Spring) Fiziği - Eve Dönüş
            force_x = (self.origin_x - self.x) * self.stiffness
            force_y = (self.origin_y - self.y) * self.stiffness
            
            self.vel_x += force_x
            self.vel_y += force_y
            
            # Sönümleme
            self.vel_x *= self.damping
            self.vel_y *= self.damping
            
            # Konumu güncelle
            self.x += self.vel_x
            self.y += self.vel_y
            
            # Serbestken hızına göre eğilsin
            self.target_angle = -self.vel_x * 2.0

        # 3. Açı İnterpolasyonu (Yumuşak Geçiş)
        # Açıyı sınırla (-30 ile 30 derece arası)
        self.target_angle = max(-30, min(30, self.target_angle))
        self.angle += (self.target_angle - self.angle) * 0.2

    def draw(self, surface):
        # Resmi döndür
        # Not: Döndürme işlemi resmin boyutunu değiştirir, merkezi korumalıyız.
        if abs(self.angle) > 0.5:
            rotated_img = pygame.transform.rotate(self.original_image, self.angle)
            new_rect = rotated_img.get_rect(center=(self.x, self.y))
            surface.blit(rotated_img, new_rect)
        else:
            rect = self.original_image.get_rect(center=(self.x, self.y))
            surface.blit(self.original_image, rect)

class VoidWidget(pygame.sprite.Sprite):
    def __init__(self, x, y, scale=0.5):
        super().__init__()
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(base_path, "assets", "void.png")
            sprite_sheet = pygame.image.load(path).convert_alpha()
        except:
            sprite_sheet = pygame.Surface((64, 16), pygame.SRCALPHA)
            sprite_sheet.fill((255, 0, 255))
        sheet_w = sprite_sheet.get_width(); sheet_h = sprite_sheet.get_height()
        frame_w = sheet_w // 4; frame_h = sheet_h
        base_frames = []
        for i in range(4):
            frame = sprite_sheet.subsurface((i * frame_w, 0, frame_w, frame_h))
            if scale != 1: frame = pygame.transform.scale(frame, (int(frame_w * scale), int(frame_h * scale)))
            base_frames.append(frame)
        self.animation_list = [base_frames[i] for i in [0, 1, 2, 3, 2, 1]]
        self.animation_list += [pygame.transform.flip(f, True, False) for f in self.animation_list]
        self.frame_index = 0
        self.image = self.animation_list[self.frame_index]
        self.rect = self.image.get_rect(); self.rect.bottomright = (x, y)
        self.last_update = pygame.time.get_ticks(); self.anim_speed = 100
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.anim_speed:
            self.last_update = now
            self.frame_index = (self.frame_index + 1) % len(self.animation_list)
            self.image = self.animation_list[self.frame_index]
    def draw(self, surface): surface.blit(self.image, self.rect)

class UIManager:
    def __init__(self):
        self.font_small = pygame.font.SysFont(FONT_NAME, 12)
        self.font_reg = pygame.font.SysFont(FONT_NAME, 14)
        self.font_bold = pygame.font.SysFont(FONT_NAME, 16, bold=True)
        self.font_score = pygame.font.SysFont(FONT_NAME, 22, bold=True)
        self.font_big = pygame.font.SysFont(FONT_NAME, 32, bold=True)
        self.title_font = pygame.font.SysFont(FONT_NAME, 60, bold=True)
        
        self.void_widget = VoidWidget(VIRTUAL_W - 20, VIRTUAL_H - 20, scale=0.8)
        self.bg_tiles = []
        self.tile_w = 0; self.tile_h = 0
        self.ra_frames = []; self.symbol_images = []
        
        self.totem_images = {}
        self.title_letters = [] 
        
        self.load_bg_assets()
        self.load_totem_assets()
        
        # YENİ: Title ve Menu Block
        self.load_title_assets()
        self.menu_blocks = [MenuBlock(random.randint(0, VIRTUAL_W), random.randint(0, VIRTUAL_H)) for _ in range(15)]

    def load_title_assets(self):
        """1.png - 7.png arası harfleri yükler, boyutlandırır ve TitleLetter objelerine dönüştürür"""
        self.title_letters = []
        base_path = os.path.dirname(os.path.abspath(__file__))
        target_height = 80
        
        loaded_imgs = []
        
        # 1. Önce resimleri yükle
        for i in range(1, 8):
            try:
                path = os.path.join(base_path, "assets", f"{i}.png")
                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                    original_w = img.get_width()
                    original_h = img.get_height()
                    scale_factor = target_height / original_h
                    new_w = int(original_w * scale_factor)
                    new_h = int(target_height)
                    img = pygame.transform.smoothscale(img, (new_w, new_h))
                    loaded_imgs.append(img)
            except Exception as e: pass

        if not loaded_imgs: return

        # 2. Konumları Hesapla (Daha sıkı yerleşim)
        # Harfler arası boşluğu azaltmak için negatif değer kullanıyoruz (Overlap)
        spacing = -10  # Biraz daha sıkı olsun
        
        total_w = sum(img.get_width() for img in loaded_imgs) + (len(loaded_imgs) - 1) * spacing
        start_x = (VIRTUAL_W - total_w) // 2
        y_pos = (VIRTUAL_H // 2) - 100
        
        current_x = start_x
        
        # 3. Objeleri Oluştur
        for img in loaded_imgs:
            # Resmin merkezi, sol kenar + yarı genişliktir
            center_x = current_x + (img.get_width() // 2)
            center_y = y_pos
            
            letter = TitleLetter(img, center_x, center_y)
            self.title_letters.append(letter)
            
            current_x += img.get_width() + spacing

    def load_totem_assets(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        mapping = {
            'sniper': 'sniper.png', 'miner': 'miner.png', 'architect': 'architect.png',
            'void_walker': 'void_walker.png', 'midas': 'midas.png', 'recycler': 'recycler.png',
            'blood_pact': 'blood_pack.png'
        }
        for key, filename in mapping.items():
            try:
                path = os.path.join(base_path, "assets", filename)
                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                    img = pygame.transform.scale(img, (TOTEM_ICON_SIZE, TOTEM_ICON_SIZE))
                    self.totem_images[key] = img
            except Exception as e:
                print(f"Totem Load Error {filename}: {e}")

    def load_bg_assets(self):
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(base_path, "assets", "ra.png")
            if os.path.exists(path):
                sprite_sheet = pygame.image.load(path).convert()
                bg_color_key = sprite_sheet.get_at((0, 0))
                sprite_sheet.set_colorkey(bg_color_key)
                sheet_w, sheet_h = sprite_sheet.get_size()
                frame_w = sheet_w // 6; frame_h = sheet_h
                self.tile_w = frame_w; self.tile_h = frame_h
                for i in range(5): 
                    frame = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
                    frame.blit(sprite_sheet, (0, 0), (i * frame_w, 0, frame_w, frame_h))
                    self.ra_frames.append(frame)
        except: pass
        for name in ["img_1.png", "img_2.png", "img_3.png"]:
            try:
                path = os.path.join(base_path, "assets", name)
                if os.path.exists(path):
                    img = pygame.image.load(path).convert()
                    bg_color_key = img.get_at((0, 0))
                    img.set_colorkey(bg_color_key)
                    if self.tile_w > 0: img = pygame.transform.scale(img, (self.tile_w, self.tile_h))
                    self.symbol_images.append(img)
            except: pass
        if self.tile_w > 0:
            cols = VIRTUAL_W // self.tile_w + 1; rows = VIRTUAL_H // self.tile_h + 1
            for r in range(rows):
                row_data = []
                for c in range(cols):
                    tile_type = 'ra' if random.random() > 0.3 else 'symbol'
                    if tile_type == 'symbol' and not self.symbol_images: tile_type = 'ra'
                    tile = {'type': tile_type, 'is_hovered': False, 'frame': 0, 'animating': False, 'timer': 0, 'img_idx': 0, 'flipped_x': False}
                    if tile_type == 'symbol':
                        tile['img_idx'] = random.randint(0, len(self.symbol_images) - 1)
                        if random.random() > 0.5: tile['flipped_x'] = True
                    row_data.append(tile)
                self.bg_tiles.append(row_data)

    def update(self):
        self.void_widget.update()
        if self.bg_tiles:
            mx, my = pygame.mouse.get_pos()
            rows = len(self.bg_tiles); cols = len(self.bg_tiles[0])
            for r in range(rows):
                for c in range(cols):
                    tile = self.bg_tiles[r][c]
                    rect = pygame.Rect(c*self.tile_w, r*self.tile_h, self.tile_w, self.tile_h)
                    currently_hovering = rect.collidepoint(mx, my)
                    if tile['type'] == 'ra':
                        if currently_hovering and not tile['animating']:
                            tile['animating'] = True; tile['frame'] = 1
                        if tile['animating']:
                            tile['timer'] += 1
                            if tile['timer'] > 5:
                                tile['timer'] = 0; tile['frame'] += 1
                                if tile['frame'] >= len(self.ra_frames): tile['frame'] = 0; tile['animating'] = False
                    elif tile['type'] == 'symbol':
                        if currently_hovering and not tile['is_hovered']: tile['flipped_x'] = not tile['flipped_x']
                        tile['is_hovered'] = currently_hovering
        
        # Menü bloklarını güncelle
        for b in self.menu_blocks: b.update()
        
        # TITLE FİZİK GÜNCELLEMELERİ
        mouse_pressed = pygame.mouse.get_pressed()[0]
        mx, my = pygame.mouse.get_pos()
        
        # 1. Sürükleme Kontrolü
        dragging_any = False
        for l in self.title_letters:
            if l.dragging:
                dragging_any = True
                if not mouse_pressed: # Mouse bırakıldı
                    l.dragging = False
                break
        
        # Sürüklemeyi Başlat
        if not dragging_any and mouse_pressed:
            # Tersten (üsttekinden) başla
            for l in reversed(self.title_letters):
                # Rotasyonlu olduğu için basit rect collision bazen kaçırabilir ama genelde yeterlidir
                # Daha hassas olması için mesafe kontrolü de eklenebilir
                dist = math.sqrt((mx - l.x)**2 + (my - l.y)**2)
                if dist < l.width / 1.5: # Yarıçap kontrolü
                    l.dragging = True
                    l.drag_offset_x = mx - l.x
                    l.drag_offset_y = my - l.y
                    break
        
        # 2. Fizik Güncellemesi (Hareket ve Yay)
        for l in self.title_letters:
            l.update()

        # 3. Çarpışma Kontrolü (Collision Resolution)
        # Tüm harfleri birbirleriyle karşılaştır (Çift döngü)
        count = len(self.title_letters)
        for i in range(count):
            for j in range(i + 1, count):
                l1 = self.title_letters[i]
                l2 = self.title_letters[j]
                l1.resolve_collision(l2)

    def draw_bg(self, surface):
        surface.fill(BG_COLOR)
        if self.bg_tiles:
            rows = len(self.bg_tiles); cols = len(self.bg_tiles[0])
            for r in range(rows):
                for c in range(cols):
                    tile = self.bg_tiles[r][c]
                    x, y = c*self.tile_w, r*self.tile_h
                    img = None
                    if tile['type'] == 'ra' and self.ra_frames: img = self.ra_frames[tile['frame']]
                    elif tile['type'] == 'symbol' and self.symbol_images:
                        base_img = self.symbol_images[tile['img_idx']]
                        if tile['flipped_x']: img = pygame.transform.flip(base_img, True, False)
                        else: img = base_img
                    if img: surface.blit(img, (x, y))
        o = pygame.Surface((VIRTUAL_W, VIRTUAL_H), pygame.SRCALPHA)
        pygame.draw.rect(o, (10, 5, 20, 150), o.get_rect())
        surface.blit(o, (0,0))

    def draw_sidebar(self, surface, game):
        panel_rect = pygame.Rect(0, 0, SIDEBAR_WIDTH, VIRTUAL_H)
        pygame.draw.rect(surface, SIDEBAR_BG_COLOR, panel_rect)
        pygame.draw.line(surface, PANEL_BORDER, (SIDEBAR_WIDTH, 0), (SIDEBAR_WIDTH, VIRTUAL_H), 4)
        cx = SIDEBAR_WIDTH // 2; y_cursor = 30
        ante_txt = self.font_bold.render(f"ANTE {game.ante} / 8", True, (200, 200, 200))
        surface.blit(ante_txt, ante_txt.get_rect(center=(cx, y_cursor))); y_cursor += 30
        round_name = ["Small Blind", "Big Blind", "Boss Blind"][game.round - 1]
        round_col = TOTAL_COLOR
        if game.round == 3 and game.active_boss_effect:
            boss_key = game.active_boss_effect
            boss_info = BOSS_DATA.get(boss_key, {'color': (255,0,0), 'desc': 'Unknown'})
            round_name = boss_key; round_col = boss_info['color']
            desc_font = pygame.font.SysFont(FONT_NAME, 11, bold=True)
            desc_lbl = desc_font.render(boss_info['desc'], True, (255, 150, 150))
            surface.blit(desc_lbl, desc_lbl.get_rect(center=(cx, y_cursor + 20))); y_cursor += 15
        round_lbl = self.font_bold.render(round_name, True, round_col)
        surface.blit(round_lbl, round_lbl.get_rect(center=(cx, y_cursor))); y_cursor += 30
        goal_lbl = self.font_small.render(f"Goal: {game.level_target}", True, (150, 150, 150))
        surface.blit(goal_lbl, goal_lbl.get_rect(center=(cx, y_cursor))); y_cursor += 40
        score_box_h = 140
        score_box = pygame.Rect(10, y_cursor, SIDEBAR_WIDTH - 20, score_box_h)
        pygame.draw.rect(surface, SCORING_BOX_BG, score_box, border_radius=10)
        pygame.draw.rect(surface, PANEL_BORDER, score_box, 2, border_radius=10)
        box_cx = score_box.centerx; box_y = score_box.y + 15
        chips_val = game.scoring_data['base'] if game.state == STATE_SCORING else 0
        chips_txt = self.font_score.render(str(chips_val), True, CHIPS_COLOR)
        surface.blit(chips_txt, chips_txt.get_rect(midleft=(score_box.x + 15, box_y)))
        lbl_chips = self.font_small.render("Chips", True, CHIPS_COLOR)
        surface.blit(lbl_chips, lbl_chips.get_rect(midleft=(score_box.x + 15, box_y + 15)))
        x_txt = self.font_bold.render("X", True, (255,255,255))
        surface.blit(x_txt, x_txt.get_rect(center=(box_cx, box_y + 10)))
        mult_val = game.scoring_data['mult'] if game.state == STATE_SCORING else 0.0
        mult_txt = self.font_score.render(f"{mult_val:.1f}", True, MULT_COLOR)
        surface.blit(mult_txt, mult_txt.get_rect(midright=(score_box.right - 15, box_y)))
        lbl_mult = self.font_small.render("Mult", True, MULT_COLOR)
        surface.blit(lbl_mult, lbl_mult.get_rect(midright=(score_box.right - 15, box_y + 15)))
        box_y += 50
        total_lbl = self.font_reg.render("Total", True, (200, 200, 200))
        surface.blit(total_lbl, total_lbl.get_rect(center=(box_cx, box_y)))
        box_y += 30
        shake = 0
        if game.state == STATE_SCORING: shake = random.randint(-1, 1)
        hand_total = game.scoring_data['total'] if game.state == STATE_SCORING else 0
        total_txt = self.font_big.render(str(hand_total), True, TOTAL_COLOR)
        surface.blit(total_txt, total_txt.get_rect(center=(box_cx + shake, box_y + shake)))
        y_cursor += score_box_h + 20
        lbl_round_score = self.font_reg.render("Round Score", True, (150, 150, 150))
        surface.blit(lbl_round_score, lbl_round_score.get_rect(center=(cx, y_cursor))); y_cursor += 20
        sc_col = (255, 255, 255)
        if game.score >= game.level_target: sc_col = (100, 255, 100)
        curr_score_txt = self.font_score.render(str(game.score), True, sc_col)
        surface.blit(curr_score_txt, curr_score_txt.get_rect(center=(cx, y_cursor)))
        menu_btn = pygame.Rect(20, VIRTUAL_H - 50, SIDEBAR_WIDTH - 40, 35)
        col = (70, 60, 80)
        if menu_btn.collidepoint(pygame.mouse.get_pos()): col = (90, 80, 100)
        pygame.draw.rect(surface, col, menu_btn, border_radius=8)
        pygame.draw.rect(surface, (150, 150, 150), menu_btn, 1, border_radius=8)
        menu_txt = self.font_bold.render("MENU", True, (255, 255, 255))
        surface.blit(menu_txt, menu_txt.get_rect(center=menu_btn.center))
        game.menu_btn_rect = menu_btn

    def draw_hand_bg(self, surface):
        rect = pygame.Rect(SIDEBAR_WIDTH, VIRTUAL_H - HAND_BG_HEIGHT, PLAY_AREA_W, HAND_BG_HEIGHT)
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        s.fill((10, 5, 15, 200)) 
        surface.blit(s, rect.topleft)
        pygame.draw.line(surface, ACCENT_COLOR, rect.topleft, rect.topright, 2)

    def render_wrapped_text(self, surface, text, font, color, x, y, max_width, line_spacing=15):
        words = text.split(' ')
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            fw, fh = font.size(' '.join(current_line))
            if fw > max_width:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]
        lines.append(' '.join(current_line))
        for i, line in enumerate(lines):
            txt_surf = font.render(line, True, color)
            surface.blit(txt_surf, (x, y + i * line_spacing))
        return len(lines) * line_spacing

    def draw_top_bar(self, surface, game):
        if not game.totems: return
        count = len(game.totems)
        total_w = count * TOTEM_ICON_SIZE + (count - 1) * 10 
        screen_center_start = (VIRTUAL_W - total_w) // 2
        start_x = max(SIDEBAR_WIDTH + 10, screen_center_start)
        y_pos = 10
        mx, my = pygame.mouse.get_pos()
        for i, t in enumerate(game.totems):
            rect = pygame.Rect(start_x + i * (TOTEM_ICON_SIZE + 10), y_pos, TOTEM_ICON_SIZE, TOTEM_ICON_SIZE)
            if t.key in self.totem_images:
                surface.blit(self.totem_images[t.key], rect)
            else:
                pygame.draw.rect(surface, (50, 40, 60), rect, border_radius=5)
                letter = self.font_bold.render(t.name[0], True, (255,255,255))
                surface.blit(letter, letter.get_rect(center=rect.center))
            pygame.draw.rect(surface, ACCENT_COLOR, rect, 2, border_radius=5)
            if rect.collidepoint(mx, my):
                tooltip_w = 140; tooltip_h = 80
                tt_x = rect.centerx - tooltip_w // 2; tt_y = rect.bottom + 5
                if tt_x < SIDEBAR_WIDTH: tt_x = SIDEBAR_WIDTH + 5
                tt_rect = pygame.Rect(tt_x, tt_y, tooltip_w, tooltip_h)
                pygame.draw.rect(surface, (20, 20, 25), tt_rect, border_radius=5)
                pygame.draw.rect(surface, (100, 100, 100), tt_rect, 1, border_radius=5)
                name_txt = self.font_bold.render(t.name, True, TOTAL_COLOR)
                surface.blit(name_txt, (tt_rect.x + 5, tt_rect.y + 5))
                desc_font = pygame.font.SysFont(FONT_NAME, 12)
                self.render_wrapped_text(surface, t.desc, desc_font, (200, 200, 200), tt_rect.x + 5, tt_rect.y + 25, tooltip_w - 10)

    def draw_menu(self, surface, high_score):
        # Arkaplan zaten draw_bg ile çizildi (ra.png ve gözler)
        
        # 2. Uçuşan Bloklar (Title'ın arkasında ama BG'nin önünde)
        for b in self.menu_blocks: b.draw(surface)
            
        # 3. Logo (S P H E N K S) - ARTIK FİZİKLİ!
        cx, cy = VIRTUAL_W//2, VIRTUAL_H//2
        if self.title_letters:
            for l in self.title_letters:
                l.draw(surface)
        else:
            # Fallback
            title = self.title_font.render("SPHENKS", True, ACCENT_COLOR)
            surface.blit(title, title.get_rect(center=(cx, cy - 80)))

        # 4. Butonlar
        self.menu_buttons = [] 
        btns = [("PLAY", 20), ("EXIT", 90)]
        base_y = cy + 40
        for text, offset in btns:
            rect = pygame.Rect(0, 0, 220, 55)
            rect.center = (cx, base_y + offset)
            col = (40, 35, 50)
            border_col = (100, 100, 100)
            if rect.collidepoint(pygame.mouse.get_pos()): 
                col = (60, 50, 80); border_col = ACCENT_COLOR
            pygame.draw.rect(surface, col, rect, border_radius=12)
            pygame.draw.rect(surface, border_col, rect, 2, border_radius=12)
            txt = self.font_bold.render(text, True, (255,255,255))
            surface.blit(txt, txt.get_rect(center=rect.center))
            self.menu_buttons.append((rect, text))
            
        hs = self.font_small.render(f"BEST RUN: {high_score}", True, (255, 200, 50))
        surface.blit(hs, hs.get_rect(center=(cx, VIRTUAL_H - 30)))

    def draw_round_select(self, surface, game):
        overlay = pygame.Surface((VIRTUAL_W, VIRTUAL_H), pygame.SRCALPHA)
        overlay.fill((10, 10, 15, 240))
        surface.blit(overlay, (0,0))
        cx = VIRTUAL_W // 2
        title = self.title_font.render(f"ANTE {game.ante}", True, (255, 255, 255))
        surface.blit(title, title.get_rect(center=(cx, 50)))
        
        panel_w, panel_h = 200, 300
        gap = 30
        start_x = cx - (1.5 * panel_w) - gap
        blinds = ['Small Blind', 'Big Blind', 'Boss Blind']
        colors = [(100, 150, 255), (255, 150, 50), (255, 50, 50)]
        targets = [game.get_blind_target(1), game.get_blind_target(2), game.get_blind_target(3)]
        
        mx, my = pygame.mouse.get_pos()
        self.select_buttons = []
        
        for i in range(3):
            is_active = (game.round == (i + 1))
            is_passed = (game.round > (i + 1))
            x = start_x + i * (panel_w + gap)
            y = 100
            rect = pygame.Rect(x, y, panel_w, panel_h)
            bg_col = (30, 30, 40)
            if is_active: bg_col = (50, 50, 60)
            elif is_passed: bg_col = (20, 20, 25)
            pygame.draw.rect(surface, bg_col, rect, border_radius=15)
            border_col = (60, 60, 70)
            if is_active: border_col = colors[i]
            pygame.draw.rect(surface, border_col, rect, 3 if is_active else 1, border_radius=15)
            lbl = self.font_bold.render(blinds[i], True, colors[i] if not is_passed else (100,100,100))
            surface.blit(lbl, lbl.get_rect(center=(rect.centerx, rect.y + 30)))
            score_lbl = self.font_score.render(f"Score: {targets[i]}", True, (255,255,255))
            if is_passed: score_lbl.set_alpha(100)
            surface.blit(score_lbl, score_lbl.get_rect(center=(rect.centerx, rect.centery)))
            
            if i == 2:
                boss_name = game.boss_preview
                b_info = BOSS_DATA.get(boss_name, {'desc': '???'})
                b_txt = self.font_small.render(boss_name, True, (255, 100, 100))
                b_desc = self.font_small.render(b_info['desc'], True, (200, 100, 100))
                surface.blit(b_txt, b_txt.get_rect(center=(rect.centerx, rect.y + 60)))
                surface.blit(b_desc, b_desc.get_rect(center=(rect.centerx, rect.y + 80)))
            
            if is_active:
                btn_rect = pygame.Rect(0, 0, 140, 40)
                btn_rect.center = (rect.centerx, rect.bottom - 40)
                b_col = colors[i]
                if btn_rect.collidepoint(mx, my):
                    b_col = (min(255, b_col[0]+30), min(255, b_col[1]+30), min(255, b_col[2]+30))
                pygame.draw.rect(surface, b_col, btn_rect, border_radius=8)
                btn_txt = self.font_bold.render("SELECT", True, (0,0,0))
                surface.blit(btn_txt, btn_txt.get_rect(center=btn_rect.center))
                self.select_buttons.append(btn_rect)

    def draw_hud_elements(self, surface, game):
        self.void_widget.draw(surface)
        v_txt = self.font_bold.render(str(game.void_count), True, (255,255,255))
        surface.blit(v_txt, v_txt.get_rect(center=self.void_widget.rect.center))
        m_bg = pygame.Rect(VIRTUAL_W - 80, 10, 70, 30)
        pygame.draw.rect(surface, (20, 40, 20), m_bg, border_radius=15)
        pygame.draw.rect(surface, (50, 200, 50), m_bg, 2, border_radius=15)
        m_txt = self.font_bold.render(f"${game.credits}", True, (100, 255, 100))
        surface.blit(m_txt, m_txt.get_rect(center=m_bg.center))

    def draw_pause_overlay(self, surface):
        o = pygame.Surface((VIRTUAL_W, VIRTUAL_H), pygame.SRCALPHA)
        o.fill((0,0,0,200))
        surface.blit(o, (0,0))
        cx, cy = VIRTUAL_W//2, VIRTUAL_H//2
        box = pygame.Rect(0, 0, 400, 250)
        box.center = (cx, cy)
        pygame.draw.rect(surface, (30, 30, 40), box, border_radius=15)
        pygame.draw.rect(surface, (100, 100, 100), box, 2, border_radius=15)
        q = self.font_bold.render("Return to Main Menu?", True, (255, 255, 255))
        surface.blit(q, q.get_rect(center=(cx, cy - 40)))
        yes_btn = pygame.Rect(0, 0, 100, 40); yes_btn.center = (cx - 70, cy + 40)
        no_btn = pygame.Rect(0, 0, 100, 40); no_btn.center = (cx + 70, cy + 40)
        mx, my = pygame.mouse.get_pos()
        c_yes = (200, 50, 50)
        if yes_btn.collidepoint(mx, my): c_yes = (255, 80, 80)
        pygame.draw.rect(surface, c_yes, yes_btn, border_radius=5)
        yt = self.font_bold.render("YES", True, (255,255,255))
        surface.blit(yt, yt.get_rect(center=yes_btn.center))
        c_no = (50, 150, 50)
        if no_btn.collidepoint(mx, my): c_no = (80, 200, 80)
        pygame.draw.rect(surface, c_no, no_btn, border_radius=5)
        nt = self.font_bold.render("NO", True, (255,255,255))
        surface.blit(nt, nt.get_rect(center=no_btn.center))
        self.pause_buttons = {'YES': yes_btn, 'NO': no_btn}

    def draw_shop(self, surface, game):
        overlay = pygame.Surface((VIRTUAL_W, VIRTUAL_H), pygame.SRCALPHA)
        overlay.fill(SHOP_BG_COLOR)
        surface.blit(overlay, (0,0))
        lbl = self.font_big.render("BAZAAR", True, ACCENT_COLOR)
        surface.blit(lbl, lbl.get_rect(center=(VIRTUAL_W//2, 30)))
        credits_bg = pygame.Rect(VIRTUAL_W - 100, 10, 90, 35)
        pygame.draw.rect(surface, (20, 40, 20), credits_bg, border_radius=15)
        pygame.draw.rect(surface, (50, 200, 50), credits_bg, 2, border_radius=15)
        credits_txt = self.font_bold.render(f"${game.credits}", True, (100, 255, 100))
        surface.blit(credits_txt, credits_txt.get_rect(center=credits_bg.center))
        start_x = (VIRTUAL_W - (3*90)) // 2
        mx, my = pygame.mouse.get_pos()
        hovered_totem = None
        for i, totem in enumerate(game.shop_totems):
            rect = pygame.Rect(start_x + (i*90), 80, 70, 100)
            col = (50, 40, 60)
            is_hovered = rect.collidepoint(mx, my)
            if is_hovered: col = (70, 60, 80); hovered_totem = totem
            pygame.draw.rect(surface, col, rect, border_radius=4)
            pygame.draw.rect(surface, ACCENT_COLOR, rect, 1, border_radius=4)
            n = self.font_small.render(totem.name[:8], True, (255,255,255))
            p = self.font_bold.render(f"${totem.price}", True, (100, 255, 100))
            surface.blit(n, (rect.x + 2, rect.y + 5))
            surface.blit(p, (rect.x + 2, rect.bottom - 20))
            totem.rect = rect
        if hovered_totem:
            tooltip_w = 180; tooltip_h = 70
            tt_x = mx + 15; tt_y = my + 10
            if tt_x + tooltip_w > VIRTUAL_W: tt_x = mx - tooltip_w - 10
            if tt_y + tooltip_h > VIRTUAL_H: tt_y = my - tooltip_h - 10
            tt_rect = pygame.Rect(tt_x, tt_y, tooltip_w, tooltip_h)
            pygame.draw.rect(surface, (15, 15, 20), tt_rect, border_radius=6)
            pygame.draw.rect(surface, (100, 100, 120), tt_rect, 2, border_radius=6)
            name_txt = self.font_bold.render(hovered_totem.name, True, TOTAL_COLOR)
            surface.blit(name_txt, (tt_rect.x + 8, tt_rect.y + 8))
            desc_font = pygame.font.SysFont(FONT_NAME, 11)
            self.render_wrapped_text(surface, hovered_totem.desc, desc_font, (200, 200, 200), tt_rect.x + 8, tt_rect.y + 28, tooltip_w - 16, line_spacing=13)
        nxt = self.font_bold.render("NEXT ROUND >", True, (255,255,255))
        nxt_rect = nxt.get_rect(bottomright=(VIRTUAL_W - 30, VIRTUAL_H - 30))
        surface.blit(nxt, nxt_rect)

    def draw_game_over(self, surface, score):
        o = pygame.Surface((VIRTUAL_W, VIRTUAL_H), pygame.SRCALPHA)
        o.fill((0,0,0,220))
        surface.blit(o, (0,0))
        t = self.title_font.render("GAME OVER", True, (255, 50, 50))
        s = self.font_big.render(f"Score: {score}", True, (255, 255, 255))
        r = self.font_reg.render("Press R to Restart", True, (150, 150, 150))
        cx, cy = VIRTUAL_W//2, VIRTUAL_H//2
        surface.blit(t, t.get_rect(center=(cx, cy - 50)))
        surface.blit(s, s.get_rect(center=(cx, cy + 10)))
        surface.blit(r, r.get_rect(center=(cx, cy + 60)))