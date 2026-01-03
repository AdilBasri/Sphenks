# game.py
import pygame
import sys
import random
import math
import os
from settings import *
from grid import Grid
from block import Block
from effects import ParticleSystem
from totems import Totem, TotemLogic, TOTEM_DATA
from glyphs import Glyph, GLYPHS
from ui import UIManager       
from audio import AudioManager 
from crt import CRTManager 

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((VIRTUAL_W, VIRTUAL_H), pygame.SCALED | pygame.FULLSCREEN)
        
        self.w = VIRTUAL_W
        self.h = VIRTUAL_H
        
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        
        self.crt = CRTManager()
        self.audio = AudioManager()
        self.ui = UIManager()
        self.particle_system = ParticleSystem()
        self.high_score = self.load_high_score()
        
        self.grid = Grid()
        self.grid_offset_x, self.grid_offset_y = self.grid.update_position(self.w, self.h)
        self.grid.rect.topleft = (self.grid_offset_x, self.grid_offset_y)
        
        self.trash_rect = pygame.Rect(self.w - 40, self.h//2 - 20, 30, 40)

        self.state = STATE_MENU
        self.init_game_session()

    def load_high_score(self):
        if os.path.exists("highscore.txt"):
            try:
                with open("highscore.txt", "r") as f: return int(f.read())
            except: return 0
        return 0
    
    def save_high_score(self):
        with open("highscore.txt", "w") as f: f.write(str(self.high_score))

    def get_current_theme(self):
        return THEMES['NEON']

    def init_game_session(self):
        self.score = 0
        self.visual_score = 0
        self.level = 1
        self.level_target = 1000
        self.void_count = 15
        self.credits = STARTING_CREDITS
        
        self.totems = [] 
        self.shop_totems = [] 
        self.glyphs = [] 
        self.shop_glyphs = [] 
        self.active_glyph = None 
        self.current_boss = None
        self.screen_shake = 0
        self.combo_val = 0.0
        self.is_hyper = False
        self.clearing_rows = []
        self.clearing_cols = []
        self.pending_score = 0
        
        self.grid.reset()
        self.blocks = []
        self.held_block = None
        self.refill_hand()

    def start_new_game(self):
        self.audio.play('select')
        self.init_game_session()
        self.state = STATE_PLAYING

    def generate_shop(self):
        self.shop_totems = []
        keys = list(TOTEM_DATA.keys())
        for _ in range(3):
            k = random.choice(keys)
            self.shop_totems.append(Totem(k, TOTEM_DATA[k]))
        self.shop_glyphs = []
        keys = list(GLYPHS.keys())
        for _ in range(2):
            self.shop_glyphs.append(Glyph(random.choice(keys)))

    def buy_totem(self, t):
        if self.credits >= t.price and len(self.totems) < MAX_TOTEM_SLOTS:
            self.credits -= t.price
            self.totems.append(t)
            if t in self.shop_totems: self.shop_totems.remove(t)
            self.audio.play('clear')

    def refill_hand(self):
        if not self.blocks and self.void_count > 0:
            count = min(3, self.void_count)
            keys = list(SHAPES.keys())
            for _ in range(count):
                self.blocks.append(Block(random.choice(keys)))
                self.void_count -= 1
            self.position_blocks_in_hand()
        elif not self.blocks and self.void_count == 0:
            if self.score < self.level_target:
                self.audio.play('gameover')
                self.state = STATE_GAME_OVER
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.save_high_score()
            else:
                self.audio.play('select')
                self.state = STATE_LEVEL_COMPLETE
                self.generate_shop()

    def next_level(self):
        self.level += 1
        self.level_target = int(self.level_target * 1.5)
        self.void_count += VOID_REFILL_AMOUNT
        self.grid.reset()
        self.refill_hand()
        self.state = STATE_PLAYING

    def position_blocks_in_hand(self):
        section_w = self.w // 3
        y_pos = int(self.h * 0.8)
        for i, b in enumerate(self.blocks):
            if b != self.held_block:
                target_x = (i * section_w) + (section_w - b.width)//2
                target_y = y_pos
                
                # RECT ve VISUAL senkronize
                b.rect.x = target_x
                b.rect.y = target_y
                b.original_pos = (target_x, target_y)
                b.visual_x = target_x
                b.visual_y = target_y

    def get_grid_pos(self, mx, my):
        # Grid sınır kontrolü
        rx, ry = mx - self.grid_offset_x, my - self.grid_offset_y
        if 0 <= rx < GRID_WIDTH and 0 <= ry < GRID_HEIGHT:
            return int(ry // TILE_SIZE), int(rx // TILE_SIZE)
        return None, None

    def handle_events(self):
        mx, my = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.save_high_score(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: sys.exit()
                if event.key == pygame.K_r and self.state == STATE_GAME_OVER: self.start_new_game()

            if self.state == STATE_MENU:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    btn = pygame.Rect(0, 0, 100, 30)
                    btn.center = (self.w//2, self.h//2 + 40)
                    if btn.collidepoint(mx, my): self.start_new_game()

            elif self.state == STATE_SHOP:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for t in self.shop_totems:
                        if t.rect.collidepoint(mx, my): self.buy_totem(t)
                    if mx > self.w - 100 and my > self.h - 30: self.next_level()
            
            elif self.state == STATE_LEVEL_COMPLETE:
                if event.type == pygame.MOUSEBUTTONDOWN: self.state = STATE_SHOP

            elif self.state == STATE_PLAYING:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        gx, gy = 10, self.h - 100
                        for i in range(len(self.glyphs)):
                            if pygame.Rect(gx, gy + i*40, 30, 30).collidepoint(mx, my):
                                self.glyphs[i].activate(self)
                                self.glyphs.pop(i)
                                break
                        
                        for b in self.blocks:
                            if b.rect.collidepoint(mx, my):
                                self.held_block = b
                                self.held_block.dragging = True
                                
                                # Offset hesabı: Mouse ile bloğun SOL ÜSTÜ arasındaki fark
                                self.held_block.offset_x = mx - b.rect.x 
                                self.held_block.offset_y = my - b.rect.y
                                self.audio.play('place') 
                                break
                    elif event.button == 3 and self.held_block:
                        self.held_block.rotate()
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and self.held_block:
                        if self.trash_rect.collidepoint(mx, my):
                            if self.credits >= DISCARD_COST:
                                self.credits -= DISCARD_COST
                                self.blocks.remove(self.held_block)
                                self.refill_hand()
                            self.held_block = None
                            return

                        # --- GRID HİZALAMA ÇÖZÜMÜ ---
                        # Bloğun sol üst köşesi tam olarak nerede?
                        current_rect_x = mx - self.held_block.offset_x
                        current_rect_y = my - self.held_block.offset_y
                        
                        # --- DÜZELTME BURADA ---
                        # Eskiden: width / 2 yapıyorduk (Bloğun geneline bakıyorduk)
                        # Şimdi: TILE_SIZE / 2 yapıyoruz (Sadece İLK KARENİN merkezine bakıyoruz)
                        # Böylece bloğun ilk karesi hangi grid hücresindeyse orayı hedefliyor.
                        check_x = current_rect_x + (TILE_SIZE / 2)
                        check_y = current_rect_y + (TILE_SIZE / 2)
                        
                        gr, gc = self.get_grid_pos(check_x, check_y)
                        
                        if gr is not None and gc is not None:
                            # Rect'i geçici olarak hedefe taşı ve kontrol et
                            target_px = self.grid_offset_x + gc * TILE_SIZE
                            target_py = self.grid_offset_y + gr * TILE_SIZE
                            
                            original_pos = self.held_block.rect.topleft
                            self.held_block.rect.topleft = (target_px, target_py)
                            
                            if self.grid.is_valid_position(self.held_block, gr, gc):
                                self.grid.place_block(self.held_block, gr, gc)
                                self.audio.play('place')
                                
                                cells = sum(r.count(1) for r in self.held_block.matrix)
                                self.score += cells * SCORE_PER_BLOCK
                                self.particle_system.create_text(target_px, target_py, f"+{cells*SCORE_PER_BLOCK}", (200,200,200))
                                
                                cr, cc = self.grid.check_clears()
                                if cr or cc:
                                    self.score += (len(cr)+len(cc)) * SCORE_PER_LINE
                                    self.audio.play('clear') 
                                    theme = self.get_current_theme()
                                    for r in cr:
                                        py = self.grid_offset_y + r*TILE_SIZE + TILE_SIZE//2
                                        for c in range(GRID_SIZE):
                                            px = self.grid_offset_x + c*TILE_SIZE + TILE_SIZE//2
                                            self.particle_system.create_explosion(px, py, (255,255,200), 5, theme['style'])
                                    for c in cc:
                                        px = self.grid_offset_x + c*TILE_SIZE + TILE_SIZE//2
                                        for r in range(GRID_SIZE):
                                            py = self.grid_offset_y + r*TILE_SIZE + TILE_SIZE//2
                                            self.particle_system.create_explosion(px, py, (200,255,255), 5, theme['style'])

                                self.blocks.remove(self.held_block)
                                self.refill_hand()
                            else:
                                self.audio.play('hit')
                                self.held_block.rect.topleft = self.held_block.original_pos
                        else:
                             self.held_block.rect.topleft = self.held_block.original_pos
                        
                        self.held_block.dragging = False
                        self.held_block = None

                elif event.type == pygame.MOUSEMOTION:
                    if self.held_block and self.held_block.dragging:
                        self.held_block.rect.x = mx - self.held_block.offset_x
                        self.held_block.rect.y = my - self.held_block.offset_y

    def update(self):
        self.ui.update()
        self.particle_system.update()
        if self.screen_shake > 0: self.screen_shake -= 1
        
        diff = self.score - self.visual_score
        if diff > 0: self.visual_score += max(1, diff // 10)
        
        if self.state == STATE_PLAYING:
            for b in self.blocks:
                b.update()

    def draw(self):
        mx, my = pygame.mouse.get_pos()
        self.screen.fill(BG_COLOR)
        
        if self.state == STATE_MENU:
            self.ui.draw_bg(self.screen, (mx, my))
            self.ui.draw_menu(self.screen, self.high_score)
        
        elif self.state == STATE_SHOP:
            self.ui.draw_shop(self.screen, self)
            
        elif self.state == STATE_GAME_OVER:
            self.ui.draw_bg(self.screen, (mx, my))
            self.grid.draw(self.screen, 0, 0, self.get_current_theme())
            self.ui.draw_game_over(self.screen, self.score)
            
        else:
            self.ui.draw_bg(self.screen, (mx, my)) 
            theme = self.get_current_theme()
            off_x = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
            off_y = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
            self.grid.draw(self.screen, off_x, off_y, theme)
            
            # --- GHOST PIECE (Hayalet Blok) ---
            if self.held_block and self.held_block.dragging:
                # AYNI DÜZELTME BURADA DA YAPILDI
                current_rect_x = mx - self.held_block.offset_x
                current_rect_y = my - self.held_block.offset_y
                
                check_x = current_rect_x + (TILE_SIZE / 2)
                check_y = current_rect_y + (TILE_SIZE / 2)
                
                gr, gc = self.get_grid_pos(check_x, check_y)
                
                if gr is not None and gc is not None:
                    # Validasyon
                    test_rect_pos = (self.grid_offset_x + gc*TILE_SIZE, self.grid_offset_y + gr*TILE_SIZE)
                    
                    # Geçici olarak rect'i değiştirip kontrol et
                    original_pos = self.held_block.rect.topleft
                    self.held_block.rect.topleft = test_rect_pos
                    
                    if self.grid.is_valid_position(self.held_block, gr, gc):
                        # Gölgeyi çiz
                        self.held_block.draw(self.screen, test_rect_pos[0], test_rect_pos[1], 1.0, 60, theme['style'])
                    
                    # Rect'i geri al
                    self.held_block.rect.topleft = original_pos

            # Normal Bloklar
            for b in self.blocks:
                if b == self.held_block:
                    b.draw(self.screen, 0, 0, 1.0, 255, theme['style']) 
                else:
                    b.draw(self.screen, 0, 0, 0.8, 255, theme['style'])
            
            self.particle_system.draw(self.screen)
            
            real_s = self.score; self.score = self.visual_score
            self.ui.draw_hud(self.screen, self)
            self.score = real_s
            
            hover = self.trash_rect.collidepoint(mx, my)
            col = TRASH_HOVER_COLOR if hover else TRASH_COLOR
            pygame.draw.rect(self.screen, col, self.trash_rect, border_radius=4)
            pygame.draw.line(self.screen, (255,255,255), (self.trash_rect.x+5, self.trash_rect.y+5), (self.trash_rect.right-5, self.trash_rect.bottom-5), 2)
            pygame.draw.line(self.screen, (255,255,255), (self.trash_rect.right-5, self.trash_rect.y+5), (self.trash_rect.x+5, self.trash_rect.bottom-5), 2)

        self.crt.draw(self.screen)
        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)