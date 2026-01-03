import pygame
import sys
import random
import math
import os
from settings import *
from grid import Grid
from block import Block
from effects import ParticleSystem, render_with_glitch
from totems import Totem, TotemLogic, TOTEM_DATA
from glyphs import Glyph
from ui import UIManager       
from audio import AudioManager 

BOSS_NONE = None
BOSS_WALL = "THE WALL"
BOSS_FOG = "THE FOG"
BOSS_GRAVITY = "HEAVY GRAVITY"

STATE_TARGETING = 'targeting'

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.w, self.h = self.screen.get_size()
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        
        self.audio = AudioManager()
        self.ui = UIManager(self.screen)
        self.score_font = pygame.font.SysFont(FONT_NAME, SCORE_FONT_SIZE, bold=True)
        
        self.high_score = self.load_high_score()
        self.particle_system = ParticleSystem()
        
        self.grid = Grid()
        self.grid_offset_x, self.grid_offset_y = self.grid.update_position(self.w, self.h)
        self.grid_offset_y = int(self.h * 0.15) 
        self.grid.rect.topleft = (self.grid_offset_x, self.grid_offset_y)
        
        trash_w, trash_h = 80, 80
        trash_x = self.w - trash_w - 20
        trash_y = (self.h // 2) - (trash_h // 2)
        self.trash_rect = pygame.Rect(trash_x, trash_y, trash_w, trash_h)

        self.state = STATE_MENU
        self.init_game_session()

    def get_current_theme(self):
        if self.level <= 3: return THEMES['NEON']
        elif self.level <= 6: return THEMES['RETRO']
        else: return THEMES['CANDY']

    def load_high_score(self):
        if os.path.exists("highscore.txt"):
            try:
                with open("highscore.txt", "r") as f:
                    return int(f.read())
            except:
                return 0
        return 0

    def save_high_score(self):
        with open("highscore.txt", "w") as f: f.write(str(self.high_score))

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
        self.last_grid_pos = (0,0)
        
        self.current_boss = BOSS_NONE
        self.screen_shake = 0
        self.portal_angle = 0 
        self.pulse_val = 0 
        self.game_over = False
        
        self.combo_val = 0.0
        self.max_combo = 100.0
        self.is_hyper = False
        self.hyper_timer = 0
        
        self.anim_timer = 0
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
        t_keys = list(TOTEM_DATA.keys())
        for _ in range(3):
            key = random.choice(t_keys)
            self.shop_totems.append(Totem(key, TOTEM_DATA[key]))
            
        self.shop_glyphs = []
        g_keys = list(GLYPHS.keys())
        for _ in range(2):
            self.shop_glyphs.append(Glyph(random.choice(g_keys)))

    def buy_totem(self, totem):
        if self.credits >= totem.price:
            if len(self.totems) < MAX_TOTEM_SLOTS:
                self.audio.play('clear')
                self.credits -= totem.price
                self.totems.append(totem)
                self.shop_totems.remove(totem)
                self.particle_system.create_text(self.w//2, self.h//2, "TOTEM ACQUIRED!", (100, 255, 255))
            else:
                self.audio.play('hit'); self.particle_system.create_text(self.w//2, self.h//2, "SLOTS FULL!", (255, 50, 50))
        else: self.audio.play('hit')

    def buy_glyph(self, glyph):
        if self.credits >= glyph.price:
            if len(self.glyphs) < MAX_GLYPH_SLOTS:
                self.audio.play('clear')
                self.credits -= glyph.price
                self.glyphs.append(glyph)
                self.shop_glyphs.remove(glyph)
                self.particle_system.create_text(self.w//2, self.h//2, "GLYPH ACQUIRED!", glyph.color)
            else:
                self.audio.play('hit'); self.particle_system.create_text(self.w//2, self.h//2, "GLYPHS FULL!", (255, 50, 50))
        else: self.audio.play('hit')

    def use_glyph(self, index):
        if index < len(self.glyphs):
            glyph = self.glyphs[index]
            if glyph.key == 'BOMB':
                self.active_glyph = glyph
                self.state = STATE_TARGETING 
                self.particle_system.create_text(self.w//2, self.h//2, "SELECT TARGET", glyph.color)
            else:
                if glyph.activate(self):
                    self.audio.play('place') 
                    self.glyphs.pop(index) 

    def refill_hand(self):
        if len(self.blocks) == 0 and self.void_count > 0:
            draw_count = min(3, self.void_count)
            keys = list(SHAPES.keys())
            for _ in range(draw_count):
                self.blocks.append(Block(random.choice(keys)))
                self.void_count -= 1
            self.position_blocks_in_hand()
        elif len(self.blocks) == 0 and self.void_count == 0:
            if self.score < self.level_target: self.handle_game_over()

    def handle_game_over(self):
        self.audio.play('gameover'); self.state = STATE_GAME_OVER
        if self.score > self.high_score: self.high_score = self.score; self.save_high_score()

    def check_level_complete(self):
        if self.score >= self.level_target:
            self.audio.play('select'); self.state = STATE_LEVEL_COMPLETE; self.generate_shop()
            bonus = max(0, self.void_count // 2)
            if bonus > 0: self.credits += bonus; self.particle_system.create_text(self.w//2, self.h//2 + 100, f"Bonus: +${bonus}", (100, 255, 100))

    def next_level(self):
        self.audio.play('select')
        self.level += 1
        self.level_target = int(self.level_target * 1.5)
        self.void_count += VOID_REFILL_AMOUNT 
        self.grid.reset()
        if self.level % 3 == 0:
            self.current_boss = random.choice([BOSS_WALL, BOSS_FOG, BOSS_GRAVITY])
            if self.current_boss == BOSS_WALL: self.grid.place_stones(min(12, 3 + (self.level // 2)))
        else: self.current_boss = BOSS_NONE
        self.refill_hand(); self.state = STATE_PLAYING

    def check_game_over_condition(self):
        if not self.blocks: return False
        for block in self.blocks:
            can_fit = False
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    if self.grid.is_valid_position(block, r, c): can_fit = True; break
                if can_fit: break
            if can_fit: return False 
        return True 

    def position_blocks_in_hand(self):
        total_width = self.w; section_width = total_width // 3; y_pos = int(self.h * 0.80)
        for i, block in enumerate(self.blocks):
            if block != self.held_block:
                preview_scale = 0.7 
                center_x = (i * section_width) + (section_width - (block.width * preview_scale)) // 2
                block.rect.x = center_x; block.rect.y = y_pos; block.original_pos = (center_x, y_pos)

    def get_grid_pos(self, mouse_x, mouse_y):
        rel_x = mouse_x - self.grid_offset_x; rel_y = mouse_y - self.grid_offset_y
        if 0 <= rel_x < GRID_WIDTH and 0 <= rel_y < GRID_HEIGHT: return int(rel_y // TILE_SIZE), int(rel_x // TILE_SIZE)
        return None, None

    def process_clears(self, check_x, check_y):
        cleared_rows, cleared_cols = self.grid.check_clears()
        total_cleared = len(cleared_rows) + len(cleared_cols)
        if total_cleared > 0:
            self.state = STATE_ANIMATING; self.anim_timer = ANIMATION_DELAY; self.clearing_rows = cleared_rows; self.clearing_cols = cleared_cols
            base_chips = total_cleared * SCORE_PER_LINE
            mult = 1 + (total_cleared - 1) * COMBO_MULTIPLIER if total_cleared > 1 else 1
            if self.is_hyper: mult *= 2
            
            extra_money = 0
            for t in self.totems:
                if t.trigger_type == 'on_clear': extra_money += TotemLogic.apply_on_clear(t.key, self, total_cleared * GRID_SIZE, 0)
            self.credits += int(extra_money)
            if extra_money > 0: self.particle_system.create_text(check_x, check_y - 80, f"Totem: +${int(extra_money)}", (100, 255, 100))

            final_score = int(base_chips * mult)
            self.pending_score = final_score
            self.screen_shake = min(20, 5 + (total_cleared * 3))
            if self.is_hyper: self.screen_shake += 5
            self.particle_system.create_text(check_x, check_y, f"+{final_score}", (255, 215, 0))
            if mult > 1: self.particle_system.create_text(check_x, check_y - 30, f"{mult:.1f}x MULT!", (255, 50, 50))
            self.combo_val = min(self.max_combo, self.combo_val + (20 * total_cleared))
            if self.combo_val >= self.max_combo: self.is_hyper = True; self.hyper_timer = 600; self.particle_system.create_text(self.w//2, self.h//2, "HYPER MODE!", (255, 0, 255)); self.audio.play('explode')
            self.audio.play('place')
        else: self.pending_score = 0

    def finalize_clears(self):
        theme = self.get_current_theme()
        if len(self.clearing_rows) + len(self.clearing_cols) >= 2: self.audio.play('explode')
        else: self.audio.play('clear')
        for r in self.clearing_rows:
            y = self.grid_offset_y + (r * TILE_SIZE) + (TILE_SIZE // 2)
            for c in range(GRID_SIZE): self.particle_system.create_explosion(self.grid_offset_x + (c * TILE_SIZE) + (TILE_SIZE // 2), y, (255, 255, 200), count=5, theme_style=theme['style'])
        for c in self.clearing_cols:
            x = self.grid_offset_x + (c * TILE_SIZE) + (TILE_SIZE // 2)
            for r in range(GRID_SIZE): self.particle_system.create_explosion(x, self.grid_offset_y + (r * TILE_SIZE) + (TILE_SIZE // 2), (200, 255, 255), count=5, theme_style=theme['style'])
        self.score += self.pending_score; self.pending_score = 0; self.state = STATE_PLAYING; self.check_level_complete()
        if self.state == STATE_PLAYING and self.check_game_over_condition(): self.handle_game_over()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.save_high_score(); pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.audio.play('select')
                    if self.state == STATE_PLAYING: self.state = STATE_PAUSED
                    elif self.state == STATE_PAUSED: self.state = STATE_PLAYING
                    elif self.state == STATE_MENU: self.save_high_score(); pygame.quit(); sys.exit()
                    elif self.state == STATE_TARGETING: self.state = STATE_PLAYING; self.active_glyph = None 
                if event.key == pygame.K_r and self.state == STATE_GAME_OVER: self.start_new_game() 
                if event.key == pygame.K_n and self.state == STATE_PLAYING: self.score = self.level_target; self.check_level_complete()

            if self.state == STATE_MENU:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if pygame.Rect(self.w//2 - 100, self.h//2, 200, 60).collidepoint(mx, my): self.start_new_game()
                    if pygame.Rect(self.w//2 - 100, self.h//2 + 80, 200, 60).collidepoint(mx, my): self.save_high_score(); pygame.quit(); sys.exit()

            elif self.state == STATE_PAUSED:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if pygame.Rect(self.w//2 - 100, self.h//2, 200, 60).collidepoint(mx, my): self.audio.play('select'); self.state = STATE_PLAYING
                    if pygame.Rect(self.w//2 - 100, self.h//2 + 80, 200, 60).collidepoint(mx, my): self.audio.play('select'); self.state = STATE_MENU

            elif self.state == STATE_SHOP:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    for totem in self.shop_totems:
                        if totem.rect.collidepoint(mx, my): self.buy_totem(totem)
                    if pygame.Rect(self.w - 220, self.h - 100, 200, 60).collidepoint(mx, my): self.next_level()

            elif self.state == STATE_LEVEL_COMPLETE:
                if event.type == pygame.MOUSEBUTTONDOWN: self.audio.play('select'); self.state = STATE_SHOP

            elif self.state == STATE_PLAYING:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: 
                        mouse_pos = pygame.mouse.get_pos()
                        
                        start_x = 50; start_y = self.h - 220
                        for i in range(len(self.glyphs)):
                            slot_rect = pygame.Rect(start_x, start_y + (i * 60), 50, 50)
                            if slot_rect.collidepoint(mouse_pos): self.use_glyph(i); break
                        
                        for block in self.blocks:
                            if block.rect.collidepoint(mouse_pos):
                                self.held_block = block; self.held_block.dragging = True
                                self.held_block.offset_x = mouse_pos[0] - block.rect.x
                                self.held_block.offset_y = mouse_pos[1] - block.rect.y
                                self.audio.play('place'); break
                    elif event.button == 3 and self.held_block: 
                        if self.current_boss != BOSS_GRAVITY: self.held_block.rotate()
                    elif event.button == 2 and self.held_block:
                        if self.current_boss != BOSS_GRAVITY: self.held_block.flip()

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and self.held_block:
                        mouse_pos = pygame.mouse.get_pos()
                        if self.trash_rect.collidepoint(mouse_pos):
                            has_recycler = any(t.key == 'recycler' for t in self.totems)
                            cost = 0 if has_recycler else DISCARD_COST
                            if self.credits >= cost:
                                self.credits -= cost; self.audio.play('explode')
                                theme = self.get_current_theme()
                                self.particle_system.create_explosion(self.trash_rect.centerx, self.trash_rect.centery, (255, 50, 50), count=15, theme_style=theme['style'])
                                self.particle_system.create_text(self.trash_rect.centerx, self.trash_rect.y - 20, "SACRIFICED", (255, 100, 100))
                                self.blocks.remove(self.held_block); self.held_block = None; self.refill_hand(); return
                            else: self.audio.play('hit'); self.particle_system.create_text(self.trash_rect.centerx, self.trash_rect.y - 20, "NO CREDITS!", (150, 150, 150))

                        check_x = self.held_block.rect.x + (TILE_SIZE // 2); check_y = self.held_block.rect.y + (TILE_SIZE // 2)
                        grid_r, grid_c = self.get_grid_pos(check_x, check_y)
                        placed = False
                        if grid_r is not None and grid_c is not None:
                            if self.grid.is_valid_position(self.held_block, grid_r, grid_c):
                                self.grid.place_block(self.held_block, grid_r, grid_c)
                                placed = True; self.last_grid_pos = (grid_r, grid_c); self.audio.play('place')
                                self.screen_shake = 3
                                theme = self.get_current_theme()
                                for br in range(self.held_block.rows):
                                    for bc in range(self.held_block.cols):
                                        if self.held_block.matrix[br][bc] == 1:
                                            ex = self.grid_offset_x + ((grid_c + bc) * TILE_SIZE) + (TILE_SIZE // 2)
                                            ey = self.grid_offset_y + ((grid_r + br) * TILE_SIZE) + (TILE_SIZE // 2)
                                            self.particle_system.create_explosion(ex, ey, (200, 255, 255), count=3, theme_style=theme['style'])
                                
                                block_cells = sum(row.count(1) for row in self.held_block.matrix)
                                chips = block_cells * SCORE_PER_BLOCK
                                mult = 1.0
                                for t in self.totems:
                                    if t.trigger_type == 'on_place': chips += TotemLogic.apply_on_place(t.key, self, 0)
                                for t in self.totems:
                                    if t.trigger_type == 'on_score': mult, chips = TotemLogic.apply_on_score(t.key, mult, chips, self)
                                if self.is_hyper: mult *= 2
                                move_score = int(chips * mult)
                                self.score += move_score
                                self.particle_system.create_text(check_x, check_y, f"+{move_score}", (200, 200, 200))
                                self.blocks.remove(self.held_block); self.refill_hand(); self.process_clears(check_x, check_y)
                                if self.state == STATE_PLAYING and self.check_game_over_condition(): self.handle_game_over()

                        if not placed: self.audio.play('hit'); self.held_block.dragging = False; self.held_block.rect.topleft = self.held_block.original_pos
                        self.held_block = None

                elif event.type == pygame.MOUSEMOTION:
                    if self.held_block and self.held_block.dragging:
                        mx, my = pygame.mouse.get_pos()
                        self.held_block.rect.x = mx - self.held_block.offset_x
                        self.held_block.rect.y = my - self.held_block.offset_y
                        if random.random() < 0.3: self.particle_system.create_trail(self.held_block)
            
            elif self.state == STATE_TARGETING:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: 
                        mx, my = pygame.mouse.get_pos(); check_x = mx; check_y = my
                        grid_r, grid_c = self.get_grid_pos(check_x, check_y)
                        if grid_r is not None and grid_c is not None:
                            self.audio.play('explode'); self.screen_shake = 10
                            for r in range(max(0, grid_r-1), min(GRID_SIZE, grid_r+2)):
                                for c in range(max(0, grid_c-1), min(GRID_SIZE, grid_c+2)):
                                    if self.grid.grid[r][c] is not None:
                                        self.grid.grid[r][c] = None
                                        ex = self.grid_offset_x + (c * TILE_SIZE) + TILE_SIZE//2
                                        ey = self.grid_offset_y + (r * TILE_SIZE) + TILE_SIZE//2
                                        self.particle_system.create_explosion(ex, ey, (255, 100, 50))
                            if self.active_glyph in self.glyphs: self.glyphs.remove(self.active_glyph)
                            self.active_glyph = None; self.state = STATE_PLAYING
                    elif event.button == 3: self.active_glyph = None; self.state = STATE_PLAYING

    def update(self):
        self.particle_system.update()
        if self.screen_shake > 0: self.screen_shake -= 1
        self.portal_angle += 0.02
        diff = self.score - self.visual_score
        if diff > 0: self.visual_score += max(1, diff // 10)
        
        if self.state == STATE_ANIMATING:
            self.anim_timer -= 1
            if self.anim_timer <= 0: self.finalize_clears(); return

        if self.combo_val > 0 and not self.is_hyper: self.combo_val -= 0.2
        if self.is_hyper:
            self.hyper_timer -= 1; self.pulse_val += 0.2
            if self.hyper_timer <= 0: self.is_hyper = False; self.combo_val = 0
        else:
            pulse_speed = 0.03 + (0.1 * (1 - (min(self.void_count, 15) / 15.0)))
            self.pulse_val += pulse_speed
        
        if self.state == STATE_MENU and random.random() < 0.1: self.particle_system.create_explosion(random.randint(0, self.w), -10, (100, 100, 150), count=1)
        if self.state == STATE_SHOP:
            mx, my = pygame.mouse.get_pos()
            for relic in self.shop_totems: relic.hovered = relic.rect.collidepoint(mx, my)
        
        if self.state == STATE_PLAYING:
            time_now = pygame.time.get_ticks()
            for i, block in enumerate(self.blocks):
                if not block.dragging:
                    offset = math.sin((time_now + i * 500) * 0.005) * 5 
                    block.rect.y = block.original_pos[1] + offset
        
        if self.state == STATE_PLAYING:
            mx, my = pygame.mouse.get_pos()
            start_x = 50; start_y = self.h - 220
            for i, g in enumerate(self.glyphs):
                r = pygame.Rect(start_x, start_y + (i * 60), 50, 50)
                g.hovered = r.collidepoint(mx, my)

    def draw_game_elements(self):
        self.ui.draw_sphenks_background()
        
        current_theme = self.get_current_theme()
        theme_style = current_theme['style']
        
        off_x = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        off_y = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        
        h_rows, h_cols = [], []
        ghost_valid = False
        ghost_x, ghost_y = 0, 0

        if self.state == STATE_PLAYING and self.held_block and self.held_block.dragging:
            check_x = self.held_block.rect.x + (TILE_SIZE // 2); check_y = self.held_block.rect.y + (TILE_SIZE // 2)
            grid_r, grid_c = self.get_grid_pos(check_x, check_y)
            if grid_r is not None and grid_c is not None:
                if self.grid.is_valid_position(self.held_block, grid_r, grid_c):
                    ghost_valid = True
                    ghost_x = self.grid_offset_x + (grid_c * TILE_SIZE) + off_x
                    ghost_y = self.grid_offset_y + (grid_r * TILE_SIZE) + off_y
                    h_rows, h_cols = self.grid.get_potential_clears(self.held_block, grid_r, grid_c)

        if self.state == STATE_ANIMATING: h_rows = self.clearing_rows; h_cols = self.clearing_cols

        self.grid.draw(self.screen, off_x, off_y, theme_data=current_theme, highlight_rows=h_rows, highlight_cols=h_cols)
        line_y = self.grid.rect.bottom + (self.h * 0.05)
        pygame.draw.line(self.screen, GRID_LINE_COLOR, (50, line_y), (self.w - 50, line_y), 2)

        if self.state != STATE_GAME_OVER:
            if ghost_valid and self.state == STATE_PLAYING:
                self.held_block.draw(self.screen, ghost_x, ghost_y, scale=1.0, alpha=100, theme_type=theme_style)
            for block in self.blocks:
                scale = 1.0 if block == self.held_block else 0.7
                if self.current_boss == BOSS_FOG and block != self.held_block:
                    rect = pygame.Rect(block.rect.x, block.rect.y, block.width*scale, block.height*scale)
                    pygame.draw.rect(self.screen, (50, 50, 60), rect, border_radius=8)
                    q_text = self.score_font.render("?", True, (100, 100, 120))
                    self.screen.blit(q_text, q_text.get_rect(center=rect.center))
                else:
                    block.draw(self.screen, block.rect.x, block.rect.y, scale=scale, theme_type=theme_style)
        self.particle_system.draw(self.screen)

    def draw(self):
        if self.state == STATE_MENU: self.ui.draw_menu(self.high_score); self.particle_system.draw(self.screen)
        elif self.state == STATE_PAUSED: self.ui.draw_pause()
        elif self.state == STATE_SHOP: self.ui.draw_shop(self); self.particle_system.draw(self.screen)
        elif self.state == STATE_LEVEL_COMPLETE: self.draw_game_elements(); self.ui.draw_level_complete(self)
        elif self.state == STATE_GAME_OVER: self.draw_game_elements(); self.ui.draw_game_over(self)
        else:
            self.draw_game_elements()
            if self.screen_shake > 5: render_with_glitch(self.screen, self.screen_shake)
            
            real_score = self.score; self.score = self.visual_score
            self.ui.draw_hud(self)
            self.score = real_score 
            
            for i, totem in enumerate(self.totems): totem.draw(self.screen, 50 + (i*50), 50)
            self.ui.draw_combo_bar(self.combo_val, self.max_combo, self.is_hyper)
            self.ui.draw_glyphs(self)
            
            if self.state == STATE_TARGETING:
                mx, my = pygame.mouse.get_pos()
                pygame.draw.circle(self.screen, (255, 0, 0), (mx, my), 30, 2)
                pygame.draw.line(self.screen, (255,0,0), (mx-10, my), (mx+10, my)); pygame.draw.line(self.screen, (255,0,0), (mx, my-10), (mx, my+10))

            mx, my = pygame.mouse.get_pos(); is_hovered = False
            if self.held_block and self.trash_rect.collidepoint(mx, my): is_hovered = True
            self.ui.draw_trash_bin(hovered=is_hovered)
            
        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)