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
        play_area_center_x = SIDEBAR_WIDTH + (PLAY_AREA_W // 2)
        play_area_center_y = VIRTUAL_H // 2
        
        grid_x = play_area_center_x - (GRID_WIDTH // 2)
        grid_y = play_area_center_y - (GRID_HEIGHT // 2)
        
        self.grid_offset_x = grid_x
        self.grid_offset_y = grid_y
        self.grid.rect.topleft = (grid_x, grid_y)
        
        self.trash_rect = pygame.Rect(self.w - 100, self.h - 60, 40, 50)
        self.menu_btn_rect = pygame.Rect(0,0,0,0)
        
        self.state = STATE_MENU 
        self.init_game_session_data() 

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

    def init_game_session_data(self):
        self.credits = STARTING_CREDITS
        self.totems = [] 
        self.score = 0
        self.visual_score = 0
        self.ante = 1
        self.round = 1 
        
        self.screen_shake = 0
        self.combo_counter = 0
        self.scoring_data = {'base': 0, 'mult': 0, 'total': 0}
        
        self.grid.reset()
        self.blocks = []
        self.held_block = None
        self.void_count = BASE_VOID_COUNT

    def start_new_game(self):
        self.audio.play('select')
        self.init_game_session_data()
        self.start_round()

    def start_round(self):
        base_target = 300 * self.ante
        if self.round == 1: self.level_target = int(base_target * 1.0)
        elif self.round == 2: self.level_target = int(base_target * 1.5)
        elif self.round == 3: self.level_target = int(base_target * 2.5)
        
        round_bonus = 0
        if self.round == 1: round_bonus = 3
        elif self.round >= 2: round_bonus = 6
        
        self.void_count = BASE_VOID_COUNT + ((self.ante - 1) * 2) + round_bonus
        
        self.score = 0 
        self.visual_score = 0
        self.combo_counter = 0
        self.screen_shake = 0
        self.scoring_data = {'base': 0, 'mult': 0, 'total': 0}
        
        self.grid.reset()
        self.blocks = []
        self.held_block = None
        self.refill_hand()
        self.state = STATE_PLAYING

    def refill_hand(self):
        if not self.blocks and self.void_count > 0:
            count = min(3, self.void_count)
            keys = list(SHAPES.keys())
            for _ in range(count):
                self.blocks.append(Block(random.choice(keys)))
                self.void_count -= 1
            self.position_blocks_in_hand()
            
        elif not self.blocks and self.void_count == 0:
            self.check_round_end()

    def check_round_end(self):
        if self.score >= self.level_target:
            self.audio.play('select')
            self.state = STATE_LEVEL_COMPLETE
            self.generate_shop()
        else:
            self.audio.play('gameover')
            self.state = STATE_GAME_OVER
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()

    def next_level(self):
        if self.round < 3:
            self.round += 1
        else:
            self.round = 1
            self.ante += 1
        self.start_round()

    def position_blocks_in_hand(self):
        area_center_x = SIDEBAR_WIDTH + (PLAY_AREA_W // 2)
        total_width = PLAY_AREA_W * 0.7
        start_x = area_center_x - (total_width // 2)
        gap = total_width // 3
        y_pos = int(self.h * 0.85)
        
        for i, b in enumerate(self.blocks):
            if b != self.held_block:
                target_x = start_x + (i * gap) + (gap - b.width)//2
                target_y = y_pos
                b.rect.x = target_x
                b.rect.y = target_y
                b.original_pos = (target_x, target_y)
                b.visual_x = target_x
                b.visual_y = target_y

    def get_grid_pos(self, mx, my):
        rx, ry = mx - self.grid_offset_x, my - self.grid_offset_y
        if 0 <= rx < GRID_WIDTH and 0 <= ry < GRID_HEIGHT:
            return int(ry // TILE_SIZE), int(rx // TILE_SIZE)
        return None, None

    def calculate_totem_mult(self):
        mult = 1.0
        if self.combo_counter > 1: mult += (self.combo_counter - 1) * 0.5
        for t in self.totems:
            if t.trigger_type == 'on_score':
                mult, _ = TotemLogic.apply_on_score(t.key, mult, 0, self)
        return mult

    def generate_shop(self):
        self.shop_totems = []
        keys = list(TOTEM_DATA.keys())
        for _ in range(3): self.shop_totems.append(Totem(random.choice(keys), TOTEM_DATA[random.choice(keys)]))
        self.state = STATE_SHOP

    def buy_totem(self, t):
        if self.credits >= t.price and len(self.totems) < MAX_TOTEM_SLOTS:
            self.credits -= t.price
            self.totems.append(t)
            if t in self.shop_totems: self.shop_totems.remove(t)
            self.audio.play('clear')

    def handle_events(self):
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            
            # --- MENU BUTTONS ---
            if self.state == STATE_MENU:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if hasattr(self.ui, 'menu_buttons'):
                        for rect, text in self.ui.menu_buttons:
                            if rect.collidepoint(mx, my):
                                if text == "PLAY": self.start_new_game()
                                elif text == "EXIT": sys.exit()

            # --- PAUSE CONFIRM ---
            elif self.state == STATE_PAUSE:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if hasattr(self.ui, 'pause_buttons'):
                        yes = self.ui.pause_buttons['YES']
                        no = self.ui.pause_buttons['NO']
                        if yes.collidepoint(mx, my):
                            self.state = STATE_MENU 
                            self.init_game_session_data()
                        elif no.collidepoint(mx, my):
                            self.state = STATE_PLAYING 

            # --- OYUN İÇİ ---
            elif self.state == STATE_PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = STATE_PAUSE
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if hasattr(self, 'menu_btn_rect') and self.menu_btn_rect.collidepoint(mx, my):
                        self.state = STATE_PAUSE
                    
                    if event.button == 1: # Left Click
                        for b in self.blocks:
                            if b.rect.collidepoint(mx, my):
                                self.held_block = b
                                self.held_block.dragging = True
                                self.held_block.offset_x = mx - b.rect.x 
                                self.held_block.offset_y = my - b.rect.y
                                self.audio.play('place') 
                                break
                    elif event.button == 3 and self.held_block: # Right Click (Rotate)
                        self.held_block.rotate()
                    
                    elif event.button == 2 and self.held_block: # Middle Click (Flip)
                        self.held_block.flip() # BLOK AYNALAMA BURADA

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and self.held_block:
                        if self.trash_rect.collidepoint(mx, my):
                            if self.credits >= DISCARD_COST:
                                self.credits -= DISCARD_COST
                                self.blocks.remove(self.held_block)
                                self.refill_hand()
                                self.combo_counter = 0
                            self.held_block = None
                            return

                        cur_x = mx - self.held_block.offset_x
                        cur_y = my - self.held_block.offset_y
                        check_x = cur_x + (TILE_SIZE / 2)
                        check_y = cur_y + (TILE_SIZE / 2)
                        gr, gc = self.get_grid_pos(check_x, check_y)

                        if gr is not None and gc is not None:
                            target_px = self.grid_offset_x + gc * TILE_SIZE
                            target_py = self.grid_offset_y + gr * TILE_SIZE
                            self.held_block.rect.topleft = (target_px, target_py)
                            
                            if self.grid.is_valid_position(self.held_block, gr, gc):
                                self.grid.place_block(self.held_block, gr, gc)
                                self.last_grid_pos = (gr, gc)
                                self.audio.play('place')
                                
                                cells = sum(r.count(1) for r in self.held_block.matrix)
                                base_points = cells * SCORE_PER_BLOCK
                                
                                cr, cc = self.grid.check_clears()
                                total_clears = len(cr) + len(cc)
                                
                                if total_clears > 0:
                                    base_points += total_clears * SCORE_PER_LINE
                                    self.credits += total_clears
                                    self.combo_counter += 1
                                    self.screen_shake = 5 * total_clears
                                    self.audio.play('clear')
                                    
                                    theme = self.get_current_theme()
                                    for r in cr:
                                        py = self.grid_offset_y + r*TILE_SIZE + TILE_SIZE//2
                                        for c in range(GRID_SIZE):
                                            self.particle_system.create_explosion(self.grid_offset_x + c*TILE_SIZE, py, (255,255,200))
                                    for c in cc:
                                        px = self.grid_offset_x + c*TILE_SIZE + TILE_SIZE//2
                                        for r in range(GRID_SIZE):
                                            self.particle_system.create_explosion(px, self.grid_offset_y + r*TILE_SIZE, (200,255,255))

                                    mult = self.calculate_totem_mult()
                                    self.blocks.remove(self.held_block)
                                    self.held_block = None
                                    
                                    self.state = STATE_SCORING
                                    self.scoring_timer = 0
                                    self.scoring_data = {
                                        'base': base_points,
                                        'mult': mult,
                                        'total': int(base_points * mult)
                                    }
                                    return

                                else:
                                    self.score += base_points
                                    self.combo_counter = 0
                                    self.scoring_data = {'base': 0, 'mult': 0, 'total': 0}

                                self.blocks.remove(self.held_block)
                                if self.state != STATE_SCORING: self.refill_hand()
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

            elif self.state == STATE_SHOP:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for t in self.shop_totems:
                        if t.rect.collidepoint(mx, my): self.buy_totem(t)
                    if mx > self.w - 150 and my > self.h - 50: self.next_level()

            elif self.state == STATE_GAME_OVER:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.state = STATE_MENU
                    self.init_game_session_data()

    def update(self):
        self.ui.update()
        self.particle_system.update()
        if self.screen_shake > 0: self.screen_shake -= 1
        
        diff = self.score - self.visual_score
        if diff > 0: self.visual_score += max(1, diff // 5)
        
        if self.state == STATE_PLAYING:
            for b in self.blocks: b.update()
            
        elif self.state == STATE_SCORING:
            self.scoring_timer += 1
            if self.scoring_timer > 60:
                self.score += self.scoring_data['total']
                self.state = STATE_PLAYING
                self.refill_hand()
                if self.score >= self.level_target and not self.blocks and self.void_count == 0:
                     self.check_round_end()

    def draw(self):
        self.ui.draw_bg(self.screen)
        
        if self.state == STATE_MENU:
            self.ui.draw_menu(self.screen, self.high_score)
        else:
            self.ui.draw_sidebar(self.screen, self)
            theme = self.get_current_theme()
            off_x = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
            self.grid.draw(self.screen, off_x, 0, theme)
            
            # Ghost
            if self.held_block and self.held_block.dragging:
                cur_x = pygame.mouse.get_pos()[0] - self.held_block.offset_x
                cur_y = pygame.mouse.get_pos()[1] - self.held_block.offset_y
                check_x = cur_x + (TILE_SIZE / 2)
                check_y = cur_y + (TILE_SIZE / 2)
                gr, gc = self.get_grid_pos(check_x, check_y)
                
                if gr is not None and gc is not None:
                    target_px = self.grid_offset_x + gc * TILE_SIZE
                    target_py = self.grid_offset_y + gr * TILE_SIZE
                    orig = self.held_block.rect.topleft
                    self.held_block.rect.topleft = (target_px, target_py)
                    if self.grid.is_valid_position(self.held_block, gr, gc):
                        self.held_block.draw(self.screen, target_px, target_py, 1.0, 60, theme['style'])
                    self.held_block.rect.topleft = orig

            # Blocks
            for b in self.blocks:
                if b != self.held_block: b.draw(self.screen, 0, 0, 0.8, 255, theme['style'])
            if self.held_block: self.held_block.draw(self.screen, 0, 0, 1.0, 255, theme['style'])
            
            self.particle_system.draw(self.screen)
            self.ui.draw_hud_elements(self.screen, self)
            
            # OVERLAYS
            if self.state == STATE_SCORING:
                self.ui.draw_sidebar(self.screen, self) 
                
            elif self.state == STATE_SHOP:
                self.ui.draw_shop(self.screen, self)
                
            elif self.state == STATE_PAUSE:
                self.ui.draw_pause_overlay(self.screen)
                
            elif self.state == STATE_GAME_OVER:
                self.ui.draw_game_over(self.screen, self.score)

        self.crt.draw(self.screen)
        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)