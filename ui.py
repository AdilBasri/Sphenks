# ui.py
import pygame
import os
import random
import math
from settings import *
from settings import STATE_PLAYING  # Tooltip kontrolü için
from languages import LANGUAGES

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

# --- PHARAOH ASSISTANT (Animated Character) ---
class PharaohAssistant:
    def __init__(self):
        # Load spritesheet (5 frames)
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(base_path, "assets", "pharaoh.png")
            sprite_sheet = pygame.image.load(path).convert_alpha()
            sheet_w = sprite_sheet.get_width()
            sheet_h = sprite_sheet.get_height()
            frame_w = sheet_w // 5  # 5 frames
            
            # Split spritesheet into frames
            self.frames = []
            for i in range(5):
                frame = sprite_sheet.subsurface((i * frame_w, 0, frame_w, sheet_h))
                self.frames.append(frame)
        except:
            # Fallback: create simple colored squares if image not found
            self.frames = []
            for i in range(5):
                surf = pygame.Surface((32, 32), pygame.SRCALPHA)
                surf.fill((200, 150, 50, 255))  # Gold color
                self.frames.append(surf)
        
        # Animation state
        self.frame_index = 0
        self.timer = 0  # Frame timer for animation
        self.anim_speed = 150  # 150ms per frame
        
        # Position: Top-left, just to the right of sidebar
        self.x = SIDEBAR_WIDTH + 25
        self.y = 65
        
        # Speech bubble system
        self.current_text = ""
        self.speech_timer = 0
        self.speech_duration = 180  # Default duration in frames
        
    def say(self, text, duration=180):
        """Make the Pharaoh say something"""
        self.current_text = text
        self.speech_timer = duration
        self.speech_duration = duration
        
    def update(self):
        """Update animation and speech timer"""
        # Update speech timer
        if self.speech_timer > 0:
            self.speech_timer -= 1
            if self.speech_timer <= 0:
                self.current_text = ""
            
            # Animate when speaking
            self.timer += 1
            if self.timer > 10:
                self.timer = 0
                if self.frames:
                    self.frame_index = (self.frame_index + 1) % len(self.frames)
        else:
            # Reset to idle frame (first frame) when silent
            self.frame_index = 0
            self.timer = 0
    
    def draw(self, surface):
        """Draw the Pharaoh sprite and speech bubble"""
        # Draw current animation frame
        current_frame = self.frames[self.frame_index]
        frame_rect = current_frame.get_rect(center=(self.x, self.y))
        surface.blit(current_frame, frame_rect)
        
        # Draw speech bubble if speaking
        if self.current_text and self.speech_timer > 0:
            self._draw_speech_bubble(surface)
    
    def _draw_speech_bubble(self, surface):
        """Draw speech bubble with auto-resizing (appears to the RIGHT)"""
        # Create font for speech text
        font = pygame.font.SysFont("Arial", 12, bold=True)
        
        # Render text to get dimensions
        text_surf = font.render(self.current_text, True, (0, 0, 0))
        text_w = text_surf.get_width()
        text_h = text_surf.get_height()
        
        # Bubble padding
        padding = 8
        bubble_w = text_w + padding * 2
        bubble_h = text_h + padding * 2
        
        # Position bubble to the RIGHT of Pharaoh
        bubble_x = self.x + 50  # To the right
        bubble_y = self.y - bubble_h // 2  # Centered vertically
        
        # Ensure bubble stays on screen
        bubble_x = max(5, min(bubble_x, VIRTUAL_W - bubble_w - 5))
        bubble_y = max(5, bubble_y)
        
        # Draw bubble background (rounded rectangle)
        bubble_rect = pygame.Rect(bubble_x, bubble_y, bubble_w, bubble_h)
        pygame.draw.rect(surface, (255, 255, 255), bubble_rect, border_radius=8)
        pygame.draw.rect(surface, (0, 0, 0), bubble_rect, 2, border_radius=8)
        
        # Draw small triangle pointing LEFT to character
        triangle_tip = (self.x + 35, self.y)  # Point at character
        triangle_top = (bubble_x, bubble_y + bubble_h // 2 - 8)
        triangle_bottom = (bubble_x, bubble_y + bubble_h // 2 + 8)
        pygame.draw.polygon(surface, (255, 255, 255), [triangle_tip, triangle_top, triangle_bottom])
        pygame.draw.line(surface, (0, 0, 0), triangle_top, triangle_tip, 2)
        pygame.draw.line(surface, (0, 0, 0), triangle_bottom, triangle_tip, 2)
        
        # Draw text centered in bubble
        text_x = bubble_x + padding
        text_y = bubble_y + padding
        surface.blit(text_surf, (text_x, text_y))


class UIManager:
    def __init__(self, game):
        self.game = game
        self.font_small = None
        self.font_reg = None
        self.font_bold = None
        self.font_score = None
        self.font_big = None
        self.title_font = None
        self.refresh_fonts()
        
        self.void_widget = VoidWidget(VIRTUAL_W - 20, VIRTUAL_H - 20, scale=0.8)
        self.pharaoh = PharaohAssistant()
        self.bg_tiles = []
        self.tile_w = 0; self.tile_h = 0
        self.ra_frames = []; self.symbol_images = []
        
        self.totem_images = {}
        self.title_letters = [] 
        
        # YENİ: Tooltip sistemi için
        self.pending_tooltip = None
        self.shop_tooltip = None
        
        # YENİ: Collection screen scrolling
        self.collection_scroll_y = 0
        
        self.load_bg_assets()
        self.load_totem_assets()
        
        # YENİ: Title ve Menu Block
        self.load_title_assets()
        self.menu_blocks = [MenuBlock(random.randint(0, VIRTUAL_W), random.randint(0, VIRTUAL_H)) for _ in range(15)]
        
        # Menu Background Randomization
        self.menu_bg_image = None
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            desert_path = os.path.join(base_path, "assets", "desert.png")
            room_path = os.path.join(base_path, "assets", "room.png")
            
            desert_img = pygame.image.load(desert_path).convert()
            room_img = pygame.image.load(room_path).convert()
            
            # Scale both to screen size
            desert_img = pygame.transform.scale(desert_img, (VIRTUAL_W, VIRTUAL_H))
            room_img = pygame.transform.scale(room_img, (VIRTUAL_W, VIRTUAL_H))
            
            # Randomly choose one (50% chance each)
            self.menu_bg_image = random.choice([desert_img, room_img])
        except Exception as e:
            # Fallback: If images are missing, continue without background
            self.menu_bg_image = None

    def _make_font(self, size, bold=False):
        base_size = max(1, size + getattr(self.game, 'font_size_offset', 0))
        try:
            font = pygame.font.Font(self.game.font_name, base_size)
        except FileNotFoundError:
            fallback_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "fonts", "pixel.ttf")
            print(f"Warning: Font {self.game.font_name} not found. Using fallback.")
            if not os.path.exists(fallback_path):
                fallback_path = None  # Use system default
            font = pygame.font.Font(fallback_path, base_size)
        font.set_bold(bold)
        return font

    def refresh_fonts(self):
        self.font_small = self._make_font(12)
        self.font_reg = self._make_font(14)
        self.font_bold = self._make_font(16, bold=True)
        self.font_score = self._make_font(22, bold=True)
        self.font_big = self._make_font(32, bold=True)
        self.title_font = self._make_font(60, bold=True)

    def t(self, key):
        return self.game.get_text(key)

    def wrap_text(self, text, font, max_width):
        """Splits text into lines that fit within max_width."""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            w, h = font.size(test_line)
            if w <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        return lines

    def draw_mouse_icon(self, surface, x, y, highlight='right', size=12):
        """
        Draw a procedural mouse icon with optional button highlight.
        highlight: 'right' for right button, 'middle' for middle/scroll wheel
        """
        # Mouse body (white outline)
        body_rect = pygame.Rect(x, y, size, size + 4)
        pygame.draw.ellipse(surface, (255, 255, 255), body_rect, 1)
        
        # Left button area
        left_btn = pygame.Rect(x + 2, y + 2, size // 2 - 1, size // 2 + 1)
        pygame.draw.rect(surface, (255, 255, 255), left_btn, 1)
        
        # Right button area
        right_btn = pygame.Rect(x + size // 2 + 1, y + 2, size // 2 - 2, size // 2 + 1)
        pygame.draw.rect(surface, (255, 255, 255), right_btn, 1)
        
        # Scroll wheel (small horizontal line in middle)
        scroll_y = y + size // 2 + 2
        pygame.draw.line(surface, (255, 255, 255), (x + 3, scroll_y), (x + size - 3, scroll_y), 1)
        
        # Highlight specified button or scroll
        if highlight == 'right':
            pygame.draw.rect(surface, (220, 70, 70), right_btn, 1)  # Red
            pygame.draw.rect(surface, (220, 70, 70), right_btn)
        elif highlight == 'middle':
            # Highlight scroll wheel area
            scroll_rect = pygame.Rect(x + 2, scroll_y - 1, size - 4, 2)
            pygame.draw.rect(surface, (220, 70, 70), scroll_rect)  # Red

    def load_title_assets(self):
        """1.png - 7.png arası harfleri yükler, boyutlandırır ve TitleLetter objelerine dönüştürür"""
        self.title_letters = []
        base_path = os.path.dirname(os.path.abspath(__file__))
        target_height = 120
        
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
        y_pos = (VIRTUAL_H // 2) - 60
        
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
                    # smoothscale yerine scale kullan - piksel netliği için
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
        self.pharaoh.update()
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
        pygame.draw.rect(surface, (30, 25, 40), panel_rect)
        pygame.draw.rect(surface, (100, 90, 110), panel_rect, 4)
        cx = SIDEBAR_WIDTH // 2

        # Color palette
        gold = (255, 215, 140)
        crimson = (220, 70, 70)
        cyan = (90, 200, 255)
        gray = (180, 180, 190)

        layer_font = self._make_font(24, bold=True)
        desc_font = self._make_font(12, bold=True)

        # Layer label at top
        if game.state == STATE_TRAINING:
            layer_txt = layer_font.render(self.t('TRAINING'), True, cyan)
        elif game.endless_mode:
            layer_txt = layer_font.render(f"{self.t('LAYER')} ∞", True, gold)
        else:
            max_ante = 16 if game.ante > 8 else 8
            layer_txt = layer_font.render(f"{self.t('LAYER')} {game.ante} / {max_ante}", True, gold)
        surface.blit(layer_txt, layer_txt.get_rect(center=(cx, 35)))

        # Info section
        y_cursor = 80
        boss_desc = None
        round_key_list = ['QUOTA', 'TRIBUTE', 'JUDGMENT']
        round_name = self.t(round_key_list[game.round - 1]) if 0 <= game.round - 1 < len(round_key_list) else ""
        round_col = TOTAL_COLOR
        if game.round == 3 and game.active_boss_effect:
            boss_key = game.active_boss_effect
            boss_info = BOSS_DATA.get(boss_key, {'color': crimson, 'desc': 'Unknown'})
            round_name = boss_key
            round_col = boss_info.get('color', crimson)
            boss_desc = boss_info.get('desc', '')
        name_txt = self.font_bold.render(round_name, True, round_col)
        surface.blit(name_txt, name_txt.get_rect(center=(cx, y_cursor)))
        y_cursor += 25
        if boss_desc:
            desc_lbl = desc_font.render(boss_desc, True, gray)
            surface.blit(desc_lbl, desc_lbl.get_rect(center=(cx, y_cursor)))
            y_cursor += 30
        else:
            y_cursor += 40

        quota_lbl = self.font_small.render(self.t('QUOTA'), True, gray)
        surface.blit(quota_lbl, quota_lbl.get_rect(center=(cx, y_cursor)))
        y_cursor += 14
        
        # Control indicators with procedural mouse icons (LEFT ALIGNED)
        control_x = 15  # Left edge padding
        control_icon_y = y_cursor
        
        # [R] Rotate with mouse icon (right button highlighted)
        self.draw_mouse_icon(surface, control_x, control_icon_y, highlight='right', size=10)
        rotate_text = f"[R] {self.game.get_text('LBL_ROTATE')}"
        rotate_txt = self.font_small.render(rotate_text, True, (255, 200, 50))
        surface.blit(rotate_txt, (control_x + 18, control_icon_y - 1))
        control_icon_y += 15
        
        # [E] Flip with mouse icon (middle/scroll highlighted)
        self.draw_mouse_icon(surface, control_x, control_icon_y, highlight='middle', size=10)
        flip_text = f"[E] {self.game.get_text('LBL_FLIP')}"
        flip_txt = self.font_small.render(flip_text, True, (255, 200, 50))
        surface.blit(flip_txt, (control_x + 18, control_icon_y - 1))
        
        # Quota value (CENTERED, pushed down to avoid control hints)
        y_cursor += 32  # Push down to clear control hints
        goal_val = self.font_bold.render(str(game.level_target), True, gold)
        surface.blit(goal_val, goal_val.get_rect(center=(cx, y_cursor)))
        y_cursor += 20  # Padding after quota value

        # Separator line
        pygame.draw.line(surface, (100, 90, 110), (8, y_cursor + 8), (SIDEBAR_WIDTH - 8, y_cursor + 8), 3)

        # Stone tablet scoring panel (dynamic Y position with 15px gap)
        y_cursor += 15  # 15px gap below separator
        tablet_rect = pygame.Rect(10, y_cursor, SIDEBAR_WIDTH - 20, 145)
        pygame.draw.rect(surface, (40, 34, 48), tablet_rect, border_radius=12)
        pygame.draw.rect(surface, (100, 90, 110), tablet_rect, 3, border_radius=12)
        inner_rect = tablet_rect.inflate(-12, -12)
        pygame.draw.rect(surface, (25, 22, 32), inner_rect, border_radius=10)

        # Titles row
        title_y = inner_rect.y + 8
        third = inner_rect.width // 3
        left_x = inner_rect.x + third // 2
        mid_x = inner_rect.centerx
        right_x = inner_rect.right - third // 2
        labor_lbl = self.font_small.render(self.t('LABOR'), True, cyan)
        favor_lbl = self.font_small.render(self.t('FAVOR'), True, crimson)
        x_lbl = self.font_small.render("X", True, (240, 240, 240))
        surface.blit(labor_lbl, labor_lbl.get_rect(center=(left_x, title_y)))
        surface.blit(x_lbl, x_lbl.get_rect(center=(mid_x, title_y)))
        surface.blit(favor_lbl, favor_lbl.get_rect(center=(right_x, title_y)))

        # Values row
        val_y = title_y + 22
        chips_val = game.scoring_data['base'] if game.state == STATE_SCORING else 0
        mult_val = game.scoring_data['mult'] if game.state == STATE_SCORING else 0.0
        hand_total = game.scoring_data['total'] if game.state == STATE_SCORING else 0
        labor_val = self.font_score.render(str(chips_val), True, cyan)
        favor_val = self.font_score.render(f"{mult_val:.1f}", True, crimson)
        surface.blit(labor_val, labor_val.get_rect(center=(left_x, val_y)))
        surface.blit(favor_val, favor_val.get_rect(center=(right_x, val_y)))

        # Divider under values
        divider_y = val_y + 22
        pygame.draw.line(surface, (80, 70, 90), (inner_rect.left + 10, divider_y), (inner_rect.right - 10, divider_y), 2)

        # Total score
        total_label = self.font_reg.render(f"{self.t('TOTAL')} SCORE", True, gold)
        total_y = divider_y + 14
        surface.blit(total_label, total_label.get_rect(center=(mid_x, total_y)))
        shake = random.randint(-1, 1) if game.state == STATE_SCORING else 0
        total_txt = self.font_big.render(str(hand_total), True, TOTAL_COLOR)
        surface.blit(total_txt, total_txt.get_rect(center=(mid_x + shake, total_y + 24 + shake)))

        # Menu button (define first to calculate available gap)
        menu_btn = pygame.Rect(20, VIRTUAL_H - 45, SIDEBAR_WIDTH - 40, 35)
        
        # Calculate available gap between tablet and menu button
        gap_height = menu_btn.top - tablet_rect.bottom
        
        # Calculate height of 'Shift Score' content
        label_height = self.font_reg.get_height()
        value_height = self.font_score.get_height()
        content_spacing = 10  # Compact spacing between label and value
        total_content_height = label_height + content_spacing + value_height
        
        # Center the content in the available gap
        start_y = tablet_rect.bottom + (gap_height - total_content_height) // 2
        
        # Draw 'Shift Score' label
        lbl_round_score = self.font_reg.render(self.t('SHIFT_SCORE'), True, gray)
        surface.blit(lbl_round_score, lbl_round_score.get_rect(center=(cx, start_y)))
        
        # Draw current score value
        sc_col = (255, 255, 255) if game.score < game.level_target else (100, 255, 100)
        curr_score_txt = self.font_score.render(str(game.score), True, sc_col)
        surface.blit(curr_score_txt, curr_score_txt.get_rect(center=(cx, start_y + label_height + content_spacing)))

        # Draw menu button
        col = (70, 60, 80)
        if menu_btn.collidepoint(pygame.mouse.get_pos()): col = (90, 80, 100)
        pygame.draw.rect(surface, col, menu_btn, border_radius=8)
        pygame.draw.rect(surface, (150, 150, 150), menu_btn, 1, border_radius=8)
        menu_txt = self.font_bold.render(self.t('MENU'), True, (255, 255, 255))
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

    def calculate_wrapped_text_height(self, text, font, max_width, line_spacing=15):
        """Metin kaydırılınca ne kadar yükseklik kaplayacağını hesapla (Dinamik tooltip boyutu için)"""
        words = text.split(' ')
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            fw, fh = font.size(' '.join(current_line))
            if fw > max_width:
                current_line.pop()
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        return max(len(lines), 1) * line_spacing

    def draw_dynamic_tooltip(self, surface, title, desc, mx, my, title_color=None, has_image=False, image=None, extra_line=None, extra_color=None):
        """Dinamik boyutlu tooltip çizer - İçeriğe göre yükseklik ayarlar"""
        if title_color is None:
            title_color = TOTAL_COLOR
        
        padding = 10
        tooltip_w = 160
        desc_font = self._make_font(11)
        
        # Yükseklik hesapla
        title_h = 18
        desc_h = self.calculate_wrapped_text_height(desc, desc_font, tooltip_w - (padding * 2), line_spacing=13)
        image_h = 48 if has_image else 0
        extra_h = 16 if extra_line else 0
        
        tooltip_h = padding + title_h + 4 + desc_h + extra_h + padding
        if has_image:
            tooltip_h += image_h + 4
        
        # Konum hesapla (ekran sınırları içinde kal)
        tt_x = mx + 15
        tt_y = my + 10
        if tt_x + tooltip_w > VIRTUAL_W:
            tt_x = mx - tooltip_w - 10
        if tt_y + tooltip_h > VIRTUAL_H:
            tt_y = my - tooltip_h - 10
        if tt_x < SIDEBAR_WIDTH:
            tt_x = SIDEBAR_WIDTH + 5
        if tt_y < 5:
            tt_y = 5
            
        tt_rect = pygame.Rect(tt_x, tt_y, tooltip_w, tooltip_h)
        
        # Arka plan çiz
        pygame.draw.rect(surface, (15, 15, 20), tt_rect, border_radius=6)
        pygame.draw.rect(surface, (100, 100, 120), tt_rect, 2, border_radius=6)
        
        y_cursor = tt_rect.y + padding
        
        # Resim varsa çiz
        if has_image and image:
            img_rect = image.get_rect(centerx=tt_rect.centerx, top=y_cursor)
            surface.blit(image, img_rect)
            y_cursor += image_h + 4
        
        # Başlık
        name_txt = self.font_bold.render(title, True, title_color)
        surface.blit(name_txt, (tt_rect.x + padding, y_cursor))
        y_cursor += title_h + 4
        
        # Açıklama
        self.render_wrapped_text(surface, desc, desc_font, (200, 200, 200), tt_rect.x + padding, y_cursor, tooltip_w - (padding * 2), line_spacing=13)
        y_cursor += desc_h
        
        # Ekstra satır (fiyat vs.)
        if extra_line:
            extra_txt = self.font_bold.render(extra_line, True, extra_color if extra_color else (100, 255, 100))
            surface.blit(extra_txt, (tt_rect.x + padding, y_cursor))
        
        return tt_rect

    def draw_top_bar(self, surface, game):
        """Totemler için üst bar - Tooltip verisi ayrı saklanır, draw sonunda çizilir"""
        self.pending_tooltip = None  # Tooltip bilgisi - draw döngüsünün sonunda çizilecek
        
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
            
            # Tooltip verisini sakla - çizim döngüsünün sonunda render edilecek
            if rect.collidepoint(mx, my):
                img = self.totem_images.get(t.key, None)
                # Get localized item info
                item_info = game.get_item_info(t.key)
                self.pending_tooltip = {
                    'type': 'totem',
                    'title': item_info['name'],
                    'desc': item_info['desc'],
                    'mx': mx,
                    'my': my,
                    'image': img
                }

    def draw_menu(self, surface, high_score):
        # Draw random menu background if available
        if self.menu_bg_image:
            surface.blit(self.menu_bg_image, (0, 0))
        # Background already drawn via draw_bg (ra.png and eyes)
        
        # Floating decorative blocks (behind title but in front of BG)
        for b in self.menu_blocks: b.draw(surface)
            
        # Logo (S P H E N K S) - Physics-based!
        cx, cy = VIRTUAL_W//2, VIRTUAL_H//2
        center_y = VIRTUAL_H // 2
        
        if self.title_letters:
            for l in self.title_letters:
                l.draw(surface)
        else:
            # Fallback
            title = self.title_font.render("SPHENKS", True, ACCENT_COLOR)
            surface.blit(title, title.get_rect(center=(cx, center_y - 120)))

        # === POLISHED BUTTON PANEL (Professional Menu Layout) ===
        # Fixed Layout Constants
        PANEL_H = 120
        BTN_H = 60
        BTN_MARGIN = 18
        W_LARGE = 240    # PLAY - Primary action
        W_MEDIUM = 180   # TRAINING, COLLECTION - Secondary actions
        W_SMALL = 80     # SETTINGS, EXIT - Utility buttons
        
        # Panel positioning
        panel_top = VIRTUAL_H - PANEL_H
        button_top = panel_top + (PANEL_H // 2) - (BTN_H // 2)
        
        # Get mouse for hover detection
        mx, my = pygame.mouse.get_pos()
        
        # Button configuration: (label, width, color_norm, color_hover, border_norm, border_hover, text_color, font_size)
        buttons_config = [
            ("EXIT", W_SMALL, (60, 25, 25), (90, 40, 40), (100, 50, 50), (200, 80, 80), (255, 200, 200), 14),
            ("PLAY", W_LARGE, (0, 200, 160), ACCENT_COLOR, ACCENT_COLOR, (255, 255, 255), (20, 15, 30), 16),
            ("TRAINING", W_MEDIUM, (50, 45, 60), (70, 65, 80), (100, 100, 100), (150, 150, 150), (255, 255, 255), 14),
            ("COLLECTION", W_MEDIUM, (50, 45, 60), (70, 65, 80), (100, 100, 100), (150, 150, 150), (255, 255, 255), 14),
            ("SETTINGS", W_SMALL, (50, 45, 60), (70, 65, 80), (100, 100, 100), (150, 150, 150), (255, 255, 255), 14),
        ]
        
        # Calculate total width for proper centering
        total_width = sum(btn[1] for btn in buttons_config) + (len(buttons_config) - 1) * BTN_MARGIN
        panel_start_x = (VIRTUAL_W - total_width) // 2
        
        self.menu_buttons = []
        current_x = panel_start_x
        
        for label, width, color_norm, color_hover, border_norm, border_hover, text_color, font_size in buttons_config:
            # Create button rectangle
            btn_rect = pygame.Rect(current_x, button_top, width, BTN_H)
            
            # Detect hover state
            is_hovered = btn_rect.collidepoint(mx, my)
            btn_fill_color = color_hover if is_hovered else color_norm
            btn_border_color = border_hover if is_hovered else border_norm
            
            # Draw button fill (rounded)
            pygame.draw.rect(surface, btn_fill_color, btn_rect, border_radius=12)
            
            # Draw main border (3px)
            pygame.draw.rect(surface, btn_border_color, btn_rect, 3, border_radius=12)
            
            # Draw darker outline for definition (1px, darker shade)
            darker_border = tuple(max(0, c - 40) for c in btn_border_color)
            outline_rect = btn_rect.inflate(-2, -2)  # Shrink slightly for inner outline
            pygame.draw.rect(surface, darker_border, outline_rect, 1, border_radius=10)
            
            # Render text with proper font scaling (localized)
            display_label = self.t(label)
            text_font = self._make_font(font_size, bold=True)
            text_surface = text_font.render(display_label, True, text_color)
            
            # Check if text fits - if not, use smaller font
            if text_surface.get_width() > width - 16:  # 8px padding on each side
                text_font = self._make_font(max(10, font_size - 2), bold=True)
                text_surface = text_font.render(display_label, True, text_color)
            
            # Center text both horizontally and vertically in button
            text_rect = text_surface.get_rect(center=btn_rect.center)
            surface.blit(text_surface, text_rect)
            
            # Store button for click detection (store key, not localized text)
            self.menu_buttons.append((btn_rect, label))
            
            # Move to next button position
            current_x += width + BTN_MARGIN
        
        # High Score Display (top-right corner, subtle) - Localized
        best_run_label = self.game.get_text('BEST_RUN')
        hs = self.font_small.render(f"{best_run_label}: {high_score}", True, (255, 200, 50))
        surface.blit(hs, (VIRTUAL_W - hs.get_width() - 20, 20))
        
        # Reset Button (top-left corner, red)
        reset_btn_w, reset_btn_h = 120, 40
        reset_btn_x, reset_btn_y = 20, 20
        self.reset_btn_rect = pygame.Rect(reset_btn_x, reset_btn_y, reset_btn_w, reset_btn_h)
        
        is_reset_hovered = self.reset_btn_rect.collidepoint(mx, my)
        reset_btn_fill = (120, 40, 40) if is_reset_hovered else (80, 20, 20)
        reset_btn_border = (200, 80, 80) if is_reset_hovered else (150, 50, 50)
        
        pygame.draw.rect(surface, reset_btn_fill, self.reset_btn_rect, border_radius=8)
        pygame.draw.rect(surface, reset_btn_border, self.reset_btn_rect, 2, border_radius=8)
        
        reset_text = self.font_bold.render(self.game.get_text("RESET_BTN"), True, (255, 200, 200))
        surface.blit(reset_text, reset_text.get_rect(center=self.reset_btn_rect.center))
        
        # Coming Soon Button (below Reset Button, top-left)
        coming_soon_btn_w, coming_soon_btn_h = 120, 40
        coming_soon_btn_x, coming_soon_btn_y = 20, 70
        self.coming_soon_btn_rect = pygame.Rect(coming_soon_btn_x, coming_soon_btn_y, coming_soon_btn_w, coming_soon_btn_h)
        
        is_coming_soon_hovered = self.coming_soon_btn_rect.collidepoint(mx, my)
        coming_soon_btn_fill = (220, 180, 70) if is_coming_soon_hovered else (200, 160, 50)
        coming_soon_btn_border = (255, 220, 100) if is_coming_soon_hovered else (200, 180, 80)
        
        pygame.draw.rect(surface, coming_soon_btn_fill, self.coming_soon_btn_rect, border_radius=8)
        pygame.draw.rect(surface, coming_soon_btn_border, self.coming_soon_btn_rect, 2, border_radius=8)
        
        coming_soon_text = self.font_bold.render(self.game.get_text("BTN_COMING_SOON"), True, (50, 40, 20))
        surface.blit(coming_soon_text, coming_soon_text.get_rect(center=self.coming_soon_btn_rect.center))

    def draw_round_select(self, surface, game):
        overlay = pygame.Surface((VIRTUAL_W, VIRTUAL_H), pygame.SRCALPHA)
        overlay.fill((10, 10, 15, 240))
        surface.blit(overlay, (0,0))
        cx = VIRTUAL_W // 2
        title = self.title_font.render(f"{self.t('LAYER')} {game.ante}", True, (255, 255, 255))
        surface.blit(title, title.get_rect(center=(cx, 50)))
        
        panel_w, panel_h = 200, 300
        gap = 30
        start_x = cx - (1.5 * panel_w) - gap
        blind_keys = ['QUOTA', 'TRIBUTE', 'JUDGMENT']
        blinds = [self.t(k) for k in blind_keys]
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
            score_lbl = self.font_score.render(f"{self.t('TOTAL')}: {targets[i]}", True, (255,255,255))
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
                btn_txt = self.font_bold.render(self.t('SELECT'), True, (0,0,0))
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
        o.fill((0, 0, 0, 200))
        surface.blit(o, (0,0))
        cx, cy = VIRTUAL_W//2, VIRTUAL_H//2
        box = pygame.Rect(0, 0, 400, 250)
        box.center = (cx, cy)
        pygame.draw.rect(surface, (30, 30, 40), box, border_radius=15)
        pygame.draw.rect(surface, (100, 100, 100), box, 2, border_radius=15)
        q = self.font_bold.render(self.t('PAUSE_MSG'), True, (255, 255, 255))
        surface.blit(q, q.get_rect(center=(cx, cy - 40)))
        yes_btn = pygame.Rect(0, 0, 100, 40); yes_btn.center = (cx - 70, cy + 40)
        no_btn = pygame.Rect(0, 0, 100, 40); no_btn.center = (cx + 70, cy + 40)
        mx, my = pygame.mouse.get_pos()
        c_yes = (200, 50, 50)
        if yes_btn.collidepoint(mx, my): c_yes = (255, 80, 80)
        pygame.draw.rect(surface, c_yes, yes_btn, border_radius=5)
        yt = self.font_bold.render(self.t('YES'), True, (255,255,255))
        surface.blit(yt, yt.get_rect(center=yes_btn.center))
        c_no = (50, 150, 50)
        if no_btn.collidepoint(mx, my): c_no = (80, 200, 80)
        pygame.draw.rect(surface, c_no, no_btn, border_radius=5)
        nt = self.font_bold.render(self.t('NO'), True, (255,255,255))
        surface.blit(nt, nt.get_rect(center=no_btn.center))
        self.pause_buttons = {'YES': yes_btn, 'NO': no_btn}

    def draw_reset_confirm_overlay(self, surface):
        """Confirmation dialog for resetting progress"""
        # Dark overlay
        o = pygame.Surface((VIRTUAL_W, VIRTUAL_H), pygame.SRCALPHA)
        o.fill((0, 0, 0, 200))
        surface.blit(o, (0, 0))
        
        cx, cy = VIRTUAL_W // 2, VIRTUAL_H // 2
        box = pygame.Rect(0, 0, 450, 280)
        box.center = (cx, cy)
        
        # Draw box background and border
        pygame.draw.rect(surface, (40, 20, 20), box, border_radius=15)
        pygame.draw.rect(surface, (200, 80, 80), box, 3, border_radius=15)
        
        # Title
        title = self.font_bold.render(self.game.get_text('RESET_CONFIRM_TITLE'), True, (255, 100, 100))
        surface.blit(title, title.get_rect(center=(cx, cy - 80)))
        
        # Message (wrapped)
        msg_lines = self.game.get_text('RESET_CONFIRM_MSG').split('\n')
        msg_y = cy - 40
        for line in msg_lines:
            msg_surf = self.font_small.render(line, True, (255, 200, 200))
            surface.blit(msg_surf, msg_surf.get_rect(center=(cx, msg_y)))
            msg_y += 25
        
        # YES/NO buttons
        yes_btn = pygame.Rect(0, 0, 100, 45)
        yes_btn.center = (cx - 85, cy + 70)
        no_btn = pygame.Rect(0, 0, 100, 45)
        no_btn.center = (cx + 85, cy + 70)
        
        mx, my = pygame.mouse.get_pos()
        
        # YES button (red)
        yes_color = (200, 50, 50)
        if yes_btn.collidepoint(mx, my):
            yes_color = (255, 80, 80)
        pygame.draw.rect(surface, yes_color, yes_btn, border_radius=6)
        pygame.draw.rect(surface, (255, 255, 255), yes_btn, 2, border_radius=6)
        yes_text = self.font_bold.render(self.game.get_text('YES'), True, (255, 255, 255))
        surface.blit(yes_text, yes_text.get_rect(center=yes_btn.center))
        
        # NO button (green)
        no_color = (50, 150, 50)
        if no_btn.collidepoint(mx, my):
            no_color = (80, 200, 80)
        pygame.draw.rect(surface, no_color, no_btn, border_radius=6)
        pygame.draw.rect(surface, (255, 255, 255), no_btn, 2, border_radius=6)
        no_text = self.font_bold.render(self.game.get_text('NO'), True, (255, 255, 255))
        surface.blit(no_text, no_text.get_rect(center=no_btn.center))
        
        # Store button rects for event handling
        self.reset_confirm_buttons = {'YES': yes_btn, 'NO': no_btn}

    def draw_coming_soon(self, surface):
        """Coming Soon feature showcase"""
        # Dark overlay
        overlay = pygame.Surface((VIRTUAL_W, VIRTUAL_H), pygame.SRCALPHA)
        overlay.fill((10, 10, 15, 250))
        surface.blit(overlay, (0, 0))
        
        cx = VIRTUAL_W // 2
        
        # Title
        title_text = self.game.get_text('COMING_SOON_TITLE')
        title = self.title_font.render(title_text, True, (255, 215, 0))
        surface.blit(title, title.get_rect(center=(cx, 60)))
        
        # Features list
        features = [
            self.game.get_text('CS_PYRO'),
            self.game.get_text('CS_LANGS'),
            self.game.get_text('CS_STORY'),
            self.game.get_text('CS_VISUALS'),
            self.game.get_text('CS_MORE'),
        ]
        
        feature_y = 160
        feature_gap = 50
        
        for feature in features:
            feature_text = self.font_score.render(feature, True, (200, 200, 200))
            surface.blit(feature_text, feature_text.get_rect(center=(cx, feature_y)))
            feature_y += feature_gap
        
        # Back button
        back_btn_w, back_btn_h = 120, 40
        back_btn_x = cx - (back_btn_w // 2)
        back_btn_y = VIRTUAL_H - 80
        self.coming_soon_back_btn = pygame.Rect(back_btn_x, back_btn_y, back_btn_w, back_btn_h)
        
        mx, my = pygame.mouse.get_pos()
        is_hovered = self.coming_soon_back_btn.collidepoint(mx, my)
        btn_color = (80, 80, 100) if is_hovered else (60, 60, 80)
        border_color = (150, 150, 150) if is_hovered else (100, 100, 100)
        
        pygame.draw.rect(surface, btn_color, self.coming_soon_back_btn, border_radius=8)
        pygame.draw.rect(surface, border_color, self.coming_soon_back_btn, 2, border_radius=8)
        
        back_text = self.font_bold.render(self.game.get_text('BACK'), True, (255, 255, 255))
        surface.blit(back_text, back_text.get_rect(center=self.coming_soon_back_btn.center))

    def draw_training_overlay(self, surface, game, step):
        """Interactive tutorial overlay mapped to localized tutorial steps"""
        if not getattr(game, 'tutorial_active', True):
            return

        # Right-side panel geometry (adjusted per step to avoid covering key areas)
        panel_w = 230
        panel_x = VIRTUAL_W - panel_w - 10
        panel_y = 20
        base_panel_h = VIRTUAL_H - 140  # default height leaves room above hand
        if step == 2:
            panel_h = VIRTUAL_H - 240  # Keep clear of trash/void area
        elif step == 5:
            panel_h = VIRTUAL_H - 200  # Keep clear of hand/blocks area
        else:
            panel_h = base_panel_h

        # Localized keys per tutorial step
        step_keys = {
            0: ("TUT_STEP0_TITLE", "TUT_STEP0_MSG"),
            1: ("TUT_STEP1_TITLE", "TUT_STEP1_MSG"),
            2: ("TUT_STEP2_TITLE", "TUT_STEP2_MSG"),
            3: ("TUT_STEP3_TITLE", "TUT_STEP3_MSG"),
            4: ("TUT_STEP4_TITLE", "TUT_STEP4_MSG"),
            5: ("TUT_STEP5_TITLE", "TUT_STEP5_MSG"),
            6: ("TUT_STEP6_TITLE", "TUT_STEP6_MSG"),
        }

        def step_text(step_id):
            t_key, m_key = step_keys.get(step_id, step_keys[0])
            return self.t(t_key), self.t(m_key)

        # Define tutorial content for all 7 steps (0-based)
        tutorial_data = {
            0: {
                'title': step_text(0)[0],
                'text': step_text(0)[1],
                'highlight': pygame.Rect(SIDEBAR_WIDTH, VIRTUAL_H - HAND_BG_HEIGHT, PLAY_AREA_W, HAND_BG_HEIGHT),
                'show_continue': False,
                'condition_text': None
            },
            1: {
                'title': step_text(1)[0],
                'text': step_text(1)[1],
                'highlight': pygame.Rect(SIDEBAR_WIDTH, VIRTUAL_H - HAND_BG_HEIGHT, PLAY_AREA_W, HAND_BG_HEIGHT),
                'show_continue': False,
                'condition_text': self.t('TUT_STEP1_COND')
            },
            2: {
                'title': step_text(2)[0],
                'text': step_text(2)[1],
                'highlight': game.trash_rect.inflate(10, 10),
                'show_continue': False,
                'condition_text': None
            },
            3: {
                'title': step_text(3)[0],
                'text': step_text(3)[1],
                'highlight': pygame.Rect(SIDEBAR_WIDTH + 50, 50, GRID_WIDTH + 50, GRID_HEIGHT + 50),
                'show_continue': True,
                'condition_text': None
            },
            4: {
                'title': step_text(4)[0],
                'text': step_text(4)[1],
                'highlight': pygame.Rect(SIDEBAR_WIDTH, 50, SIDEBAR_WIDTH - 10, 120),
                'show_continue': True,
                'condition_text': None
            },
            5: {
                'title': step_text(5)[0],
                'text': step_text(5)[1],
                'highlight': None,  # Will be drawn dynamically below
                'show_continue': False,
                'condition_text': self.t('TUT_STEP5_COND'),
                'draw_rune_highlight': True  # Special flag for rune highlighting
            },
            6: {
                'title': step_text(6)[0],
                'text': step_text(6)[1],
                'highlight': None,
                'show_continue': True,
                'condition_text': None
            }
        }

        current = tutorial_data.get(step, tutorial_data[0])
        
        # Draw highlight around important areas (if specified)
        if current['highlight']:
            highlight_rect = current['highlight']
            
            # Draw bright border around highlighted area
            pygame.draw.rect(surface, ACCENT_COLOR, highlight_rect, 4, border_radius=10)
            
            # Pulsing glow effect
            import math
            import time
            pulse = abs(math.sin(time.time() * 3)) * 0.5 + 0.5
            glow_color = (*ACCENT_COLOR, int(100 * pulse))
            for i in range(3):
                glow_rect = highlight_rect.inflate(i * 8, i * 8)
                pygame.draw.rect(surface, glow_color, glow_rect, 2, border_radius=12)
        
        # Draw right-side panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        
        # Semi-transparent dark background for panel only
        panel_surface = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel_surface.fill((15, 10, 25, 220))
        surface.blit(panel_surface, (panel_x, panel_y))
        
        # Panel border
        pygame.draw.rect(surface, ACCENT_COLOR, panel_rect, 3, border_radius=12)
        
        # Title at top of panel
        title = self.font_bold.render("TUTORIAL", True, ACCENT_COLOR)
        title_rect = title.get_rect(centerx=panel_rect.centerx, top=panel_rect.top + 15)
        surface.blit(title, title_rect)
        
        # Step indicator
        step_text = self.font_small.render(f"Step {step + 1}/7", True, (150, 150, 150))
        step_rect = step_text.get_rect(centerx=panel_rect.centerx, top=title_rect.bottom + 5)
        surface.blit(step_text, step_rect)
        
        # Separator line
        line_y = step_rect.bottom + 10
        pygame.draw.line(surface, ACCENT_COLOR, (panel_x + 15, line_y), (panel_x + panel_w - 15, line_y), 2)
        
        # Content area
        content_y = line_y + 15
        content_x = panel_x + 10
        content_w = panel_w - 20
        
        # Step title
        step_title_lines = self._wrap_text(current['title'], content_w - 10, self.font_bold)
        for line in step_title_lines:
            line_surf = self.font_bold.render(line, True, (255, 200, 100))
            surface.blit(line_surf, (content_x + 5, content_y))
            content_y += 20
        
        content_y += 10
        
        # Instruction text (wrapped)
        instruction_lines = current['text'].split('\n')
        for paragraph in instruction_lines:
            if paragraph.strip():
                wrapped_lines = self._wrap_text(paragraph.strip(), content_w - 10, self.font_small)
                for line in wrapped_lines:
                    line_surf = self.font_small.render(line, True, (220, 220, 220))
                    surface.blit(line_surf, (content_x + 5, content_y))
                    content_y += 18
            else:
                content_y += 10  # Blank line spacing
        
        # Condition text or continue indicator at bottom
        import math
        import time
        if current['condition_text']:
            pulse = abs(math.sin(time.time() * 4)) * 0.3 + 0.7
            condition_color = (int(255 * pulse), int(200 * pulse), int(50 * pulse))
            condition_lines = self._wrap_text(current['condition_text'], content_w - 10, self.font_small)
            cond_y = panel_rect.bottom - 40 - (len(condition_lines) * 18)
            for line in condition_lines:
                condition_text = self.font_small.render(line, True, condition_color)
                surface.blit(condition_text, (content_x + 5, cond_y))
                cond_y += 18
        elif current['show_continue']:
            pulse = abs(math.sin(time.time() * 4)) * 0.3 + 0.7
            continue_color = (int(255 * pulse), int(255 * pulse), int(100 * pulse))
            continue_text = self.font_small.render("CLICK TO CONTINUE", True, continue_color)
            surface.blit(continue_text, (content_x + 5, panel_rect.bottom - 30))
        
        # Special: Draw flashing highlight around rune in step 4
        if current.get('draw_rune_highlight', False):
            import math
            import time
            # Calculate rune position (same as in game.py drawing code)
            start_x = SIDEBAR_WIDTH + 20
            start_y = 60
            rune_size = 40
            
            # Draw bright flashing rectangle around first rune position
            pulse = abs(math.sin(time.time() * 5)) * 0.5 + 0.5
            highlight_color = (int(255 * pulse), int(200 * pulse), int(50 * pulse))
            rune_rect = pygame.Rect(start_x - 5, start_y - 5, rune_size + 10, rune_size + 10)
            pygame.draw.rect(surface, highlight_color, rune_rect, 4, border_radius=25)
            
            # Outer glow effect
            for i in range(3):
                glow_rect = rune_rect.inflate(i * 6, i * 6)
                glow_alpha = int(80 * pulse / (i + 1))
                glow_color = (*highlight_color, glow_alpha)
                pygame.draw.rect(surface, glow_color, glow_rect, 2, border_radius=25)

    def draw_shop(self, surface, game):
        """Market ekranı - Balatro tarzı kart görünümü"""
        overlay = pygame.Surface((VIRTUAL_W, VIRTUAL_H), pygame.SRCALPHA)
        overlay.fill(SHOP_BG_COLOR)
        surface.blit(overlay, (0,0))
        
        lbl = self.font_big.render(self.t('BAZAAR'), True, ACCENT_COLOR)
        surface.blit(lbl, lbl.get_rect(center=(VIRTUAL_W//2, 30)))
        
        # Kredi Göstergesi
        credits_bg = pygame.Rect(VIRTUAL_W - 100, 10, 90, 35)
        pygame.draw.rect(surface, (20, 40, 20), credits_bg, border_radius=15)
        pygame.draw.rect(surface, (50, 200, 50), credits_bg, 2, border_radius=15)
        credits_txt = self.font_bold.render(f"${game.credits}", True, (100, 255, 100))
        surface.blit(credits_txt, credits_txt.get_rect(center=credits_bg.center))
        
        mx, my = pygame.mouse.get_pos()
        self.shop_tooltip = None  # Shop tooltip verisi
        
        # --- TOTEMLER: BALATRO TARZI KART GÖRÜNÜMÜ ---
        card_w = 100
        card_h = 150
        card_gap = 15
        totem_count = len(game.shop_totems)
        total_cards_w = totem_count * card_w + (totem_count - 1) * card_gap
        start_x = (VIRTUAL_W - total_cards_w) // 2
        card_y = 60
        
        # Totem Başlığı
        totem_header = self.font_bold.render(self.t('TOTEMS'), True, (200, 200, 200))
        surface.blit(totem_header, (start_x, card_y - 20))
        
        for i, totem in enumerate(game.shop_totems):
            card_x = start_x + i * (card_w + card_gap)
            card_rect = pygame.Rect(card_x, card_y, card_w, card_h)
            
            # Hover kontrolü
            is_hovered = card_rect.collidepoint(mx, my)
            
            # Kart arka planı
            bg_col = (50, 45, 60) if not is_hovered else (70, 65, 85)
            pygame.draw.rect(surface, bg_col, card_rect, border_radius=8)
            
            # Kart çerçevesi - alınabilirlik durumuna göre renk
            border_col = ACCENT_COLOR if game.credits >= totem.price else (100, 60, 60)
            pygame.draw.rect(surface, border_col, card_rect, 2, border_radius=8)
            
            # --- KART İÇERİĞİ ---
            content_y = card_rect.y + 8
            
            # 1. Görsel (varsa)
            if totem.key in self.totem_images:
                img = self.totem_images[totem.key]
                # Kartın merkezine büyük ikon
                img_scaled = pygame.transform.scale(img, (48, 48))
                img_rect = img_scaled.get_rect(centerx=card_rect.centerx, top=content_y)
                surface.blit(img_scaled, img_rect)
                content_y += 52
            else:
                # Görsel yoksa placeholder
                placeholder_rect = pygame.Rect(card_rect.centerx - 24, content_y, 48, 48)
                pygame.draw.rect(surface, (40, 35, 50), placeholder_rect, border_radius=6)
                letter = self.font_big.render(totem.name[0], True, (150, 150, 150))
                surface.blit(letter, letter.get_rect(center=placeholder_rect.center))
                content_y += 52
            
            # 2. İsim (kart genişliğine göre kısaltılmış) - Localized via get_item_info
            item_info = self.game.get_item_info(totem.key)
            max_name_width = card_w - 10  # Kartın kenar boşlukları
            name_display = item_info['name']
            name_txt = self.font_bold.render(name_display, True, TOTAL_COLOR)
            
            # Metin genişliği kartı aşıyorsa kısalt
            while name_txt.get_width() > max_name_width and len(name_display) > 4:
                name_display = name_display[:-1]
                name_txt = self.font_bold.render(name_display + "..", True, TOTAL_COLOR)
            
            if name_display != item_info['name']:
                name_txt = self.font_bold.render(name_display + "..", True, TOTAL_COLOR)
            
            name_rect = name_txt.get_rect(centerx=card_rect.centerx, top=content_y)
            surface.blit(name_txt, name_rect)
            content_y += 18
            
            # 3. Kısa Açıklama (1-2 satır) - Localized from get_item_info
            desc_font = self._make_font(10)
            localized_desc = item_info['desc']
            desc_short = localized_desc[:20] + ".." if len(localized_desc) > 22 else localized_desc
            desc_txt = desc_font.render(desc_short, True, (180, 180, 180))
            desc_rect = desc_txt.get_rect(centerx=card_rect.centerx, top=content_y)
            surface.blit(desc_txt, desc_rect)
            
            # 4. Fiyat (En altta)
            price_y = card_rect.bottom - 25
            price_bg = pygame.Rect(card_rect.x + 10, price_y, card_w - 20, 20)
            price_col = (30, 60, 30) if game.credits >= totem.price else (60, 30, 30)
            pygame.draw.rect(surface, price_col, price_bg, border_radius=4)
            price_txt = self.font_bold.render(f"${totem.price}", True, (100, 255, 100) if game.credits >= totem.price else (255, 100, 100))
            surface.blit(price_txt, price_txt.get_rect(center=price_bg.center))
            
            totem.rect = card_rect
            
            # Hover durumunda tooltip verisi sakla - Use localized info
            if is_hovered:
                img = self.totem_images.get(totem.key, None)
                self.shop_tooltip = {
                    'type': 'totem',
                    'title': item_info['name'],
                    'desc': item_info['desc'],
                    'mx': mx,
                    'my': my,
                    'image': img
                }
        
        # --- RÜNLER: KART GÖRÜNÜMÜ ---
        rune_card_w = 80
        rune_card_h = 120
        rune_count = len(game.shop_runes)
        if rune_count > 0:
            rune_header = self.font_bold.render(self.t('RUNES'), True, (200, 200, 200))
            rune_header_y = card_y + card_h + 30
            surface.blit(rune_header, (start_x, rune_header_y - 20))
            
            total_runes_w = rune_count * rune_card_w + (rune_count - 1) * card_gap
            rune_start_x = (VIRTUAL_W - total_runes_w) // 2
            rune_y = rune_header_y
            
            for i, rune in enumerate(game.shop_runes):
                rx = rune_start_x + i * (rune_card_w + card_gap)
                rune_rect = pygame.Rect(rx, rune_y, rune_card_w, rune_card_h)
                
                is_hovered = rune_rect.collidepoint(mx, my)
                
                # Kart arka planı
                bg_col = (40, 35, 50) if not is_hovered else (60, 55, 75)
                pygame.draw.rect(surface, bg_col, rune_rect, border_radius=8)
                
                # Çerçeve rengi
                border_col = rune.color if game.credits >= rune.price else (100, 60, 60)
                pygame.draw.rect(surface, border_col, rune_rect, 2, border_radius=8)
                
                # Rün Simgesi (Büyük daire)
                circle_y = rune_rect.y + 35
                pygame.draw.circle(surface, (20, 20, 30), (rune_rect.centerx, circle_y), 25)
                pygame.draw.circle(surface, rune.color, (rune_rect.centerx, circle_y), 23, 3)
                
                icon_font = self._make_font(24, bold=True)
                icon_txt = icon_font.render(rune.icon, True, rune.color)
                surface.blit(icon_txt, icon_txt.get_rect(center=(rune_rect.centerx, circle_y)))
                
                # Rün ismi - Localized via get_item_info
                rune_info = self.game.get_item_info(rune.key)
                rune_name_display = rune_info['name'][:10]
                name_txt = self.font_small.render(rune_name_display, True, (255, 255, 255))
                surface.blit(name_txt, name_txt.get_rect(centerx=rune_rect.centerx, top=rune_rect.y + 65))
                
                # Fiyat
                price_y = rune_rect.bottom - 25
                price_bg = pygame.Rect(rune_rect.x + 8, price_y, rune_card_w - 16, 18)
                price_col = (30, 60, 30) if game.credits >= rune.price else (60, 30, 30)
                pygame.draw.rect(surface, price_col, price_bg, border_radius=4)
                price_txt = self.font_bold.render(f"${rune.price}", True, (100, 255, 100) if game.credits >= rune.price else (255, 100, 100))
                surface.blit(price_txt, price_txt.get_rect(center=price_bg.center))
                
                rune.rect = rune_rect
                
                # Hover durumunda tooltip verisi sakla - Use localized info
                if is_hovered:
                    self.shop_tooltip = {
                        'type': 'rune',
                        'title': rune_info['name'],
                        'desc': rune_info['desc'],
                        'mx': mx,
                        'my': my,
                        'color': rune.color,
                        'price': rune.price
                    }
        
        # --- TOOLTIP ÇİZİMİ (En son, her şeyin üstünde) ---
        if self.shop_tooltip:
            tt = self.shop_tooltip
            if tt['type'] == 'totem':
                self.draw_dynamic_tooltip(surface, tt['title'], tt['desc'], tt['mx'], tt['my'], 
                                         title_color=TOTAL_COLOR, has_image=bool(tt.get('image')), image=tt.get('image'))
            elif tt['type'] == 'rune':
                self.draw_dynamic_tooltip(surface, tt['title'], tt['desc'], tt['mx'], tt['my'],
                                         title_color=tt.get('color', ACCENT_COLOR))
        
        # Next Round butonu - Localized
        nxt_rect = pygame.Rect(VIRTUAL_W - 160, VIRTUAL_H - 50, 140, 35)
        nxt_hovered = nxt_rect.collidepoint(mx, my)
        nxt_col = (60, 80, 60) if nxt_hovered else (40, 60, 40)
        pygame.draw.rect(surface, nxt_col, nxt_rect, border_radius=8)
        pygame.draw.rect(surface, (100, 200, 100), nxt_rect, 2, border_radius=8)
        nxt = self.font_bold.render(self.game.get_text('NEXT_ROUND'), True, (255,255,255))
        surface.blit(nxt, nxt.get_rect(center=nxt_rect.center))

    def draw_game_over(self, surface, score):
        o = pygame.Surface((VIRTUAL_W, VIRTUAL_H), pygame.SRCALPHA)
        o.fill((0,0,0,220))
        surface.blit(o, (0,0))
        t = self.title_font.render(self.t('GAME OVER'), True, (255, 50, 50))
        s = self.font_big.render(f"{self.t('TOTAL')}: {score}", True, (255, 255, 255))
        r = self.font_reg.render(self.t('Press R to Restart'), True, (150, 150, 150))
        cx, cy = VIRTUAL_W//2, VIRTUAL_H//2
        surface.blit(t, t.get_rect(center=(cx, cy - 50)))
        surface.blit(s, s.get_rect(center=(cx, cy + 10)))
        surface.blit(r, r.get_rect(center=(cx, cy + 60)))

    def draw_debt_screen(self, surface, game):
        """Dramatic debt repayment screen with animations"""
        
        # Black background with fade
        alpha = min(255, game.debt_animation_timer * 10)
        overlay = pygame.Surface((VIRTUAL_W, VIRTUAL_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        surface.blit(overlay, (0, 0))
        
        cx, cy = VIRTUAL_W // 2, VIRTUAL_H // 2
        
        # Payment amount indicator (top)
        if game.debt_animation_timer > 10:
            payment_label = f"{self.t('PAYMENT')}: -{game.debt_payment_amount:,}"
            payment_text = self.font_bold.render(payment_label, True, (100, 255, 100))
            surface.blit(payment_text, payment_text.get_rect(center=(cx, 60)))
        
        # Debt number with shake and scale
        if game.debt_animation_timer > 20:
            is_animating = game.debt_displayed_value > (game.debt_old_value - game.debt_payment_amount)
            
            # Determine color
            if is_animating:
                color = (255, 255, 255)
            else:
                # Flash red when finished
                if game.debt_animation_timer < 80:
                    color = (255, 50, 50)
                else:
                    color = (255, 255, 255)
            
            # Create debt text with scale
            debt_str = f"{int(game.debt_displayed_value):,}"
            debt_font_size = int(80 * game.debt_scale)
            
            # Use existing title font as base, scaled
            debt_surface = self.title_font.render(debt_str, True, color)
            
            # Scale the surface
            if game.debt_scale != 1.0:
                original_size = debt_surface.get_size()
                new_size = (int(original_size[0] * game.debt_scale), int(original_size[1] * game.debt_scale))
                debt_surface = pygame.transform.scale(debt_surface, new_size)
            
            # Apply shake
            shake_x = game.debt_shake_intensity
            shake_y = game.debt_shake_intensity
            
            surface.blit(debt_surface, debt_surface.get_rect(center=(cx + shake_x, cy - 40 + shake_y)))
            
            # "TOTAL DEBT" label
            label = self.font_bold.render(self.t('TOTAL_DEBT'), True, (150, 150, 150))
            surface.blit(label, label.get_rect(center=(cx, cy - 120)))
        
        # Pharaoh / Freedom quote with typewriter effect (bottom)
        # Now uses localized text from current_quote_text
        if game.debt_animation_timer > 90:
            displayed_quote = game.current_quote_text[:game.debt_quote_char_index]
            
            quote_text = self.font_reg.render(displayed_quote, True, (200, 150, 50))
            surface.blit(quote_text, quote_text.get_rect(center=(cx, cy + 100)))
        
        # Unlock notification (if any items were unlocked)
        if game.debt_animation_timer > 80 and hasattr(game, 'newly_unlocked_items') and game.newly_unlocked_items:
            for i, item in enumerate(game.newly_unlocked_items):
                unlock_y = cy + 50 + (i * 30)
                unlock_text = self.font_bold.render(f"{self.t('UNLOCKED')}: {item['name']}", True, (255, 215, 0))
                surface.blit(unlock_text, unlock_text.get_rect(center=(cx, unlock_y)))
                
                desc_text = self.font_small.render("Keep working!", True, (200, 200, 200))
                surface.blit(desc_text, desc_text.get_rect(center=(cx, unlock_y + 20)))
        
        # Continue button (bottom right) - only show after animation completes
        if game.debt_animation_timer > 120:
            btn_w, btn_h = 150, 50
            btn_x = VIRTUAL_W - btn_w - 30
            btn_y = VIRTUAL_H - btn_h - 30
            
            btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
            self.debt_continue_button = btn_rect  # Store for event handling
            
            mx, my = pygame.mouse.get_pos()
            hover = btn_rect.collidepoint(mx, my)
            
            btn_color = (80, 60, 100) if hover else (50, 40, 70)
            border_color = ACCENT_COLOR if hover else (100, 100, 100)
            
            pygame.draw.rect(surface, btn_color, btn_rect, border_radius=8)
            pygame.draw.rect(surface, border_color, btn_rect, 2, border_radius=8)
            
            btn_text = self.font_bold.render(self.t('CONTINUE'), True, (255, 255, 255))
            surface.blit(btn_text, btn_text.get_rect(center=btn_rect.center))

    def draw_demo_end(self, surface, game):
        """Demo ending screen - Thank you for playing message with endless mode option"""
        # Dark overlay
        overlay = pygame.Surface((VIRTUAL_W, VIRTUAL_H), pygame.SRCALPHA)
        overlay.fill((5, 5, 10, 240))
        surface.blit(overlay, (0, 0))
        
        cx = VIRTUAL_W // 2
        cy = VIRTUAL_H // 2
        
        # Title
        title = self.title_font.render(self.t('DEMO_TITLE'), True, ACCENT_COLOR)
        surface.blit(title, title.get_rect(center=(cx, cy - 140)))

        # Localized message body
        msg_lines = self.t('DEMO_MSG').split('\n')
        start_y = cy - 70
        for i, line in enumerate(msg_lines):
            line_font = self.font_big if i == 0 else self.font_reg
            line_surface = line_font.render(line, True, (255, 255, 255))
            surface.blit(line_surface, line_surface.get_rect(center=(cx, start_y + i * 35)))
        
        # Endless mode button
        btn_w, btn_h = 300, 60
        btn_x = cx - (btn_w // 2)
        btn_y = cy + 100
        
        btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        self.demo_end_button = btn_rect  # Store for event handling
        
        mx, my = pygame.mouse.get_pos()
        hover = btn_rect.collidepoint(mx, my)
        
        # Glowing effect for button
        btn_color = (100, 50, 150) if hover else (60, 30, 100)
        border_color = (255, 200, 50) if hover else ACCENT_COLOR
        
        pygame.draw.rect(surface, btn_color, btn_rect, border_radius=12)
        pygame.draw.rect(surface, border_color, btn_rect, 3, border_radius=12)
        
        btn_text = self.font_big.render(self.t('ENTER_ETERNITY'), True, (255, 255, 255))
        surface.blit(btn_text, btn_text.get_rect(center=btn_rect.center))
        
        # Hint text (localized)
        hint = self.font_small.render(self.game.get_text("DEMO_HINT_MSG"), True, (150, 150, 150))
        surface.blit(hint, hint.get_rect(center=(cx, btn_y + btn_h + 20)))

    def draw_collection(self, surface, game):
        """Collection screen showing unlocked items with scrolling support"""
        from settings import COLLECTIBLES
        
        # Dark background
        overlay = pygame.Surface((VIRTUAL_W, VIRTUAL_H), pygame.SRCALPHA)
        overlay.fill((10, 10, 15, 250))
        surface.blit(overlay, (0, 0))
        
        cx = VIRTUAL_W // 2
        
        # Title
        title = self.title_font.render(self.t('COLLECTION'), True, ACCENT_COLOR)
        surface.blit(title, title.get_rect(center=(cx, 40)))
        
        # Progress indicator
        save_data = game.save_manager.get_data()
        total_paid = save_data['debt_paid']
        total_debt = save_data['total_debt']
        remaining = max(0, total_debt - total_paid)
        unlocked_count = len([item for item in COLLECTIBLES if game.save_manager.is_unlocked(item['id'])])
        
        progress_text = self.font_bold.render(f"{self.t('Unlocked')}: {unlocked_count}/{len(COLLECTIBLES)}", True, (255, 255, 255))
        surface.blit(progress_text, progress_text.get_rect(center=(cx, 80)))
        
        debt_text = self.font_reg.render(f"{self.t('Debt Paid')}: {total_paid:,} / {total_debt:,}", True, (200, 200, 200))
        surface.blit(debt_text, debt_text.get_rect(center=(cx, 105)))
        
        # Grid of collectibles (2 columns, 4 rows = 8 items)
        cols = 2
        rows = 4
        card_w = 180
        card_h = 140
        gap_x = 30
        gap_y = 20
        
        # Calculate total content height
        total_content_height = rows * card_h + (rows - 1) * gap_y
        
        # Scrolling area parameters
        scroll_area_top = 140
        scroll_area_height = VIRTUAL_H - scroll_area_top - 80  # Leave room for title and back button
        
        # Calculate max scroll (clamp so content doesn't scroll too far)
        max_scroll = max(0, total_content_height - scroll_area_height)
        
        # Clamp scroll value
        self.collection_scroll_y = max(0, min(self.collection_scroll_y, max_scroll))
        
        start_x = cx - (cols * card_w + (cols - 1) * gap_x) // 2
        start_y = scroll_area_top - self.collection_scroll_y
        
        mx, my = pygame.mouse.get_pos()
        
        for i, item in enumerate(COLLECTIBLES):
            row = i // cols
            col = i % cols
            
            x = start_x + col * (card_w + gap_x)
            y = start_y + row * (card_h + gap_y)
            
            # Only draw if visible on screen
            if y + card_h < scroll_area_top or y > VIRTUAL_H - 80:
                continue
            
            card_rect = pygame.Rect(x, y, card_w, card_h)
            
            is_unlocked = game.save_manager.is_unlocked(item['id'])
            hover = card_rect.collidepoint(mx, my)
            
            # Card background
            if is_unlocked:
                bg_color = (40, 40, 50) if not hover else (50, 50, 65)
                border_color = (100, 100, 100) if not hover else ACCENT_COLOR
            else:
                bg_color = (20, 20, 25)
                border_color = (50, 50, 50)
            
            pygame.draw.rect(surface, bg_color, card_rect, border_radius=10)
            pygame.draw.rect(surface, border_color, card_rect, 2, border_radius=10)
            
            if is_unlocked:
                # Show icon (emoji)
                icon_font = self._make_font(48)
                icon_surface = icon_font.render(item['icon'], True, (255, 255, 255))
                surface.blit(icon_surface, icon_surface.get_rect(center=(card_rect.centerx, card_rect.y + 40)))
                
                # Name
                name_text = self.font_bold.render(item['name'], True, (255, 255, 255))
                surface.blit(name_text, name_text.get_rect(center=(card_rect.centerx, card_rect.y + 85)))
                
                # Description
                desc_lines = self._wrap_text(item['desc'], card_w - 20, self.font_small)
                for j, line in enumerate(desc_lines):
                    desc_surface = self.font_small.render(line, True, (150, 150, 150))
                    surface.blit(desc_surface, desc_surface.get_rect(center=(card_rect.centerx, card_rect.y + 105 + j * 15)))
            else:
                # Locked silhouette
                lock_icon = self.font_big.render("🔒", True, (80, 80, 80))
                surface.blit(lock_icon, lock_icon.get_rect(center=(card_rect.centerx, card_rect.centery - 10)))
                
                # Unlock requirement
                req_text = self.font_small.render(f"Pay {item['unlock_at']:,}", True, (100, 100, 100))
                surface.blit(req_text, req_text.get_rect(center=(card_rect.centerx, card_rect.centery + 25)))
        
        # Draw scrollbar on the right side
        if max_scroll > 0:
            scrollbar_x = VIRTUAL_W - 20
            scrollbar_w = 8
            scrollbar_h = scroll_area_height
            
            # Background track
            track_rect = pygame.Rect(scrollbar_x - scrollbar_w // 2, scroll_area_top, scrollbar_w, scrollbar_h)
            pygame.draw.rect(surface, (40, 40, 50), track_rect, border_radius=4)
            
            # Scroll thumb (handle)
            thumb_height = max(20, scrollbar_h * scrollbar_h // total_content_height)
            thumb_y = scroll_area_top + (self.collection_scroll_y / max_scroll) * (scrollbar_h - thumb_height)
            thumb_rect = pygame.Rect(scrollbar_x - scrollbar_w // 2, thumb_y, scrollbar_w, thumb_height)
            
            thumb_color = ACCENT_COLOR if thumb_rect.collidepoint(mx, my) else (100, 100, 100)
            pygame.draw.rect(surface, thumb_color, thumb_rect, border_radius=4)
        
        # Back button
        btn_w, btn_h = 120, 50
        btn_x = 30
        btn_y = VIRTUAL_H - btn_h - 30
        
        back_btn = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        self.collection_back_button = back_btn
        
        hover_back = back_btn.collidepoint(mx, my)
        btn_color = (80, 60, 100) if hover_back else (50, 40, 70)
        border_color = ACCENT_COLOR if hover_back else (100, 100, 100)
        
        pygame.draw.rect(surface, btn_color, back_btn, border_radius=8)
        pygame.draw.rect(surface, border_color, back_btn, 2, border_radius=8)
        
        back_text = self.font_bold.render(self.t('BACK'), True, (255, 255, 255))
        surface.blit(back_text, back_text.get_rect(center=back_btn.center))
    
    def _wrap_text(self, text, max_width, font):
        """Helper to wrap text into multiple lines"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines[:2]  # Max 2 lines

    def draw_settings(self, surface, game):
        """Settings screen with resolution, fullscreen, and volume controls"""
        from settings import RESOLUTIONS
        
        # Dark background
        overlay = pygame.Surface((VIRTUAL_W, VIRTUAL_H), pygame.SRCALPHA)
        overlay.fill((10, 10, 15, 250))
        surface.blit(overlay, (0, 0))
        
        cx = VIRTUAL_W // 2
        cy = VIRTUAL_H // 2
        
        # Title
        title = self.title_font.render(self.t('SETTINGS'), True, ACCENT_COLOR)
        surface.blit(title, title.get_rect(center=(cx, 40)))
        
        # Panel
        panel_w = 500
        panel_h = 400
        panel_x = cx - panel_w // 2
        panel_y = 100
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        pygame.draw.rect(surface, (30, 30, 40), panel_rect, border_radius=15)
        pygame.draw.rect(surface, (100, 100, 100), panel_rect, 2, border_radius=15)
        
        # Get current settings
        save_data = game.save_manager.get_data()
        settings = save_data['settings']
        
        # Track temp settings if not already initialized
        if not hasattr(game, 'temp_settings'):
            game.temp_settings = {
                'fullscreen': settings.get('fullscreen', False),
                'volume': settings.get('volume', 0.5),
                'resolution_index': self._get_resolution_index(game),
                'language': settings.get('language', game.current_language)
            }
        
        mx, my = pygame.mouse.get_pos()
        
        # --- FULLSCREEN TOGGLE ---
        y_offset = panel_y + 60
        label = self.font_bold.render("Fullscreen:", True, (255, 255, 255))
        surface.blit(label, (panel_x + 50, y_offset))
        
        # Toggle button
        toggle_x = panel_x + panel_w - 150
        toggle_w = 80
        toggle_h = 35
        toggle_rect = pygame.Rect(toggle_x, y_offset - 5, toggle_w, toggle_h)
        
        is_on = game.temp_settings['fullscreen']
        toggle_color = (50, 200, 50) if is_on else (200, 50, 50)
        hover_toggle = toggle_rect.collidepoint(mx, my)
        if hover_toggle:
            toggle_color = tuple(min(255, c + 30) for c in toggle_color)
        
        pygame.draw.rect(surface, toggle_color, toggle_rect, border_radius=17)
        toggle_text = self.font_bold.render("ON" if is_on else "OFF", True, (255, 255, 255))
        surface.blit(toggle_text, toggle_text.get_rect(center=toggle_rect.center))
        
        # Store for event handling
        if not hasattr(self, 'settings_buttons'):
            self.settings_buttons = {}
        self.settings_buttons['fullscreen'] = toggle_rect

        # --- LANGUAGE SELECTOR ---
        y_offset += 60
        lang_label = self.font_bold.render(f"{self.t('LANGUAGE') if self.t('LANGUAGE') else 'Language'}:", True, (255, 255, 255))
        surface.blit(lang_label, (panel_x + 50, y_offset))

        lang_code = game.temp_settings.get('language', game.current_language)
        lang_name = LANGUAGES.get(lang_code, {}).get('name', lang_code)
        lang_rect = pygame.Rect(panel_x + panel_w - 220, y_offset - 10, 180, 40)
        hover_lang = lang_rect.collidepoint(mx, my)
        lang_bg = (60, 60, 80) if hover_lang else (40, 40, 55)
        pygame.draw.rect(surface, lang_bg, lang_rect, border_radius=8)
        pygame.draw.rect(surface, ACCENT_COLOR if hover_lang else (120, 120, 140), lang_rect, 2, border_radius=8)
        lang_text = self.font_bold.render(f"{lang_name}", True, (255, 255, 255))
        surface.blit(lang_text, lang_text.get_rect(center=lang_rect.center))
        self.settings_buttons['language'] = lang_rect
        
        # --- VOLUME SLIDER ---
        y_offset += 80
        label = self.font_bold.render("Master Volume:", True, (255, 255, 255))
        surface.blit(label, (panel_x + 50, y_offset))
        
        # Slider
        slider_x = panel_x + 50
        slider_y = y_offset + 35
        slider_w = panel_w - 100
        slider_h = 10
        
        # Background track
        track_rect = pygame.Rect(slider_x, slider_y, slider_w, slider_h)
        pygame.draw.rect(surface, (50, 50, 50), track_rect, border_radius=5)
        
        # Filled portion
        volume = game.temp_settings['volume']
        fill_w = int(slider_w * volume)
        fill_rect = pygame.Rect(slider_x, slider_y, fill_w, slider_h)
        pygame.draw.rect(surface, ACCENT_COLOR, fill_rect, border_radius=5)
        
        # Handle (circle)
        handle_x = slider_x + fill_w
        handle_y = slider_y + slider_h // 2
        handle_radius = 12
        handle_rect = pygame.Rect(handle_x - handle_radius, handle_y - handle_radius, 
                                   handle_radius * 2, handle_radius * 2)
        
        hover_handle = handle_rect.collidepoint(mx, my) or track_rect.collidepoint(mx, my)
        handle_color = (255, 255, 255) if hover_handle else (200, 200, 200)
        pygame.draw.circle(surface, handle_color, (handle_x, handle_y), handle_radius)
        pygame.draw.circle(surface, ACCENT_COLOR, (handle_x, handle_y), handle_radius - 2)
        
        # Volume percentage
        vol_text = self.font_bold.render(f"{int(volume * 100)}%", True, (255, 255, 255))
        surface.blit(vol_text, (panel_x + panel_w - 80, y_offset))
        
        # Store slider info for dragging
        self.settings_buttons['volume_slider'] = track_rect
        self.settings_buttons['volume_handle'] = handle_rect
        
        # --- RESOLUTION SELECTOR ---
        y_offset += 80
        label = self.font_bold.render("Resolution:", True, (255, 255, 255))
        surface.blit(label, (panel_x + 50, y_offset))
        
        # Current resolution
        res_index = game.temp_settings['resolution_index']
        current_res = RESOLUTIONS[res_index]
        res_text = f"{current_res[0]} x {current_res[1]}"
        
        # Left arrow
        left_arrow_x = panel_x + panel_w - 250
        arrow_w = 40
        arrow_h = 35
        left_rect = pygame.Rect(left_arrow_x, y_offset - 5, arrow_w, arrow_h)
        
        hover_left = left_rect.collidepoint(mx, my)
        arrow_color = ACCENT_COLOR if hover_left else (100, 100, 100)
        pygame.draw.rect(surface, arrow_color, left_rect, border_radius=5)
        left_text = self.font_bold.render("<", True, (255, 255, 255))
        surface.blit(left_text, left_text.get_rect(center=left_rect.center))
        
        # Resolution text
        res_display = self.font_bold.render(res_text, True, (255, 255, 255))
        surface.blit(res_display, res_display.get_rect(center=(left_arrow_x + arrow_w + 70, y_offset + 15)))
        
        # Right arrow
        right_arrow_x = left_arrow_x + arrow_w + 140 + 20
        right_rect = pygame.Rect(right_arrow_x, y_offset - 5, arrow_w, arrow_h)
        
        hover_right = right_rect.collidepoint(mx, my)
        arrow_color = ACCENT_COLOR if hover_right else (100, 100, 100)
        pygame.draw.rect(surface, arrow_color, right_rect, border_radius=5)
        right_text = self.font_bold.render(">", True, (255, 255, 255))
        surface.blit(right_text, right_text.get_rect(center=right_rect.center))
        
        self.settings_buttons['res_left'] = left_rect
        self.settings_buttons['res_right'] = right_rect
        
        # --- SAVE & BACK BUTTON ---
        # Position dynamically: 50 pixels below the Resolution selector row
        btn_w = 180
        btn_h = 50
        btn_x = cx - btn_w // 2
        btn_y = y_offset + 50
        
        save_btn = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        self.settings_buttons['save'] = save_btn
        
        hover_save = save_btn.collidepoint(mx, my)
        btn_color = (80, 60, 100) if hover_save else (50, 40, 70)
        border_color = ACCENT_COLOR if hover_save else (100, 100, 100)
        
        pygame.draw.rect(surface, btn_color, save_btn, border_radius=8)
        pygame.draw.rect(surface, border_color, save_btn, 2, border_radius=8)
        
        save_text = self.font_bold.render("SAVE & BACK", True, (255, 255, 255))
        surface.blit(save_text, save_text.get_rect(center=save_btn.center))
        
        # Back button (no save)
        back_btn_w = 120
        back_btn_h = 50
        back_btn_x = 30
        back_btn_y = VIRTUAL_H - back_btn_h - 30
        
        back_btn = pygame.Rect(back_btn_x, back_btn_y, back_btn_w, back_btn_h)
        self.settings_buttons['back'] = back_btn
        
        hover_back = back_btn.collidepoint(mx, my)
        btn_color = (60, 40, 40) if hover_back else (40, 30, 30)
        border_color = (200, 100, 100) if hover_back else (100, 100, 100)
        
        pygame.draw.rect(surface, btn_color, back_btn, border_radius=8)
        pygame.draw.rect(surface, border_color, back_btn, 2, border_radius=8)
        
        back_text = self.font_bold.render("CANCEL", True, (255, 255, 255))
        surface.blit(back_text, back_text.get_rect(center=back_btn.center))
    
    def _get_resolution_index(self, game):
        """Get current resolution index from actual screen size"""
        from settings import RESOLUTIONS
        screen_size = (game.screen.get_width(), game.screen.get_height())
        
        # Try to match current screen size to resolutions list
        for i, res in enumerate(RESOLUTIONS):
            if res == screen_size:
                return i
        
        # Default to first resolution if no match
        return 0

    def _wrap_text(self, text, max_width, font):
        """Wrap text to fit within max_width pixels"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surf = font.render(test_line, True, (255, 255, 255))
            
            if test_surf.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines if lines else [text]
    
    def check_rune_hover(self, game):
        """Oyun sırasında rünler üzerine hover kontrolü - tooltip verisi döndürür"""
        mx, my = pygame.mouse.get_pos()
        for r in game.consumables:
            if r.rect and r.rect.collidepoint(mx, my) and not r.dragging:
                # Get localized item info
                item_info = game.get_item_info(r.key)
                return {
                    'type': 'rune',
                    'title': item_info['name'],
                    'desc': item_info['desc'],
                    'mx': mx,
                    'my': my,
                    'color': r.color
                }
        return None

    def draw_final_tooltip_layer(self, surface, game):
        """Tüm çizimlerden sonra çağrılır - Tooltip'ler her şeyin üstünde görünür"""
        # Önce totem tooltip'lerini kontrol et (draw_top_bar'dan)
        if hasattr(self, 'pending_tooltip') and self.pending_tooltip:
            tt = self.pending_tooltip
            img = tt.get('image', None)
            self.draw_dynamic_tooltip(surface, tt['title'], tt['desc'], tt['mx'], tt['my'], 
                                     title_color=TOTAL_COLOR, has_image=bool(img), image=img)
            return  # Bir tooltip çizildiyse diğerlerini kontrol etme
        
        # Oyun durumunda rün tooltip'lerini kontrol et
        if game.state == STATE_PLAYING:
            rune_tt = self.check_rune_hover(game)
            if rune_tt:
                self.draw_dynamic_tooltip(surface, rune_tt['title'], rune_tt['desc'], 
                                         rune_tt['mx'], rune_tt['my'], 
                                         title_color=rune_tt.get('color', ACCENT_COLOR))

    def draw_overlay_elements(self, surface):
        """Draw elements that should appear on top of everything else"""
        self.pharaoh.draw(surface)