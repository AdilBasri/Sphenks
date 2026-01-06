# game.py
import pygame
import sys
import random
import math
import os
from settings import *
from grid import Grid
from block import Block
from effects import ParticleSystem, BossAtmosphere
from totems import Totem, TotemLogic, TOTEM_DATA, OMEGA_KEYS
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
        grid_y = play_area_center_y - (GRID_HEIGHT // 2) - 20 
        
        self.grid_offset_x = grid_x
        self.grid_offset_y = grid_y
        self.grid.rect.topleft = (grid_x, grid_y)
        
        self.trash_rect = pygame.Rect(self.w - 80, self.h - 80, 40, 50)
        self.menu_btn_rect = pygame.Rect(0,0,0,0)
        
        self.force_omega_shop = False # Yeni Dünya dükkanı için bayrak
        
        self.state = STATE_MENU 
        self.init_game_session_data() 

    def load_high_score(self):
        if os.path.exists("highscore.txt"):
            try:
                with open("highscore.txt", "r") as f:
                    return int(f.read())
            except: return 0
        return 0
    
    def save_high_score(self):
        with open("highscore.txt", "w") as f: f.write(str(self.high_score))

    def get_current_theme(self):
        # Ante 9 ve sonrası için yeni dünya teması
        if self.ante >= NEW_WORLD_ANTE:
            return THEMES['CRIMSON']
        return THEMES['NEON']

    def init_game_session_data(self):
        self.credits = STARTING_CREDITS
        self.totems = [] 
        self.score = 0
        self.visual_score = 0
        self.ante = 1
        self.round = 1 
        self.force_omega_shop = False
        
        self.boss_preview = random.choice(list(BOSS_DATA.keys()))
        
        self.screen_shake = 0
        self.combo_counter = 0
        self.scoring_data = {'base': 0, 'mult': 0, 'total': 0}
        
        self.current_boss = None 
        self.active_boss_effect = None 
        
        self.grid.reset()
        self.blocks = []
        self.held_block = None
        self.void_count = BASE_VOID_COUNT
        self.is_edge_placement = False
        self.last_placed_block_tag = 'NONE'

    def get_blind_target(self, round_num):
        # --- ZORLUK DENGELEME FORMÜLÜ ---
        # 1. Base Scaling: Ante arttıkça katlanarak artar (Üs: 1.2)
        base_target = 300 * (self.ante ** 1.3)
        
        # 2. Totem Scaling: Oyuncu güçlendikçe (Totem sayısı arttıkça) hedef zorlaşır
        # 5 Totem varsa hedef %75 daha fazla olur.
        totem_penalty = 1.0 + (len(self.totems) * 0.15) 
        
        adjusted_target = int(base_target * totem_penalty)

        if round_num == 1: return int(adjusted_target * 1.0)
        elif round_num == 2: return int(adjusted_target * 1.5)
        elif round_num == 3: return int(adjusted_target * 2.5)
        return 0

    def start_new_game(self):
        self.audio.play('select')
        self.init_game_session_data()
        self.state = STATE_ROUND_SELECT

    def start_round(self):
        self.active_boss_effect = None
        if self.round == 3:
            self.current_boss = self.boss_preview
            self.active_boss_effect = self.current_boss
        else:
            self.current_boss = None

        self.level_target = self.get_blind_target(self.round)
        
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
        
        if self.active_boss_effect == 'The Wall':
            self.grid.place_stones(3)
            self.particle_system.create_text(self.w//2, self.h//2, "BOSS: THE WALL", (150, 150, 150))
            self.particle_system.atmosphere.trigger_shake(10, 4) 
            self.crt.trigger_aberration(amount=2, duration=10)

        self.refill_hand()
        self.state = STATE_PLAYING

    def get_smart_block_key(self):
        keys = list(SHAPES.keys())
        empty_cells = 0
        single_holes = 0
        
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.grid.grid[r][c] is None:
                    empty_cells += 1
                    neighbors = 0
                    if r > 0 and self.grid.grid[r-1][c]: neighbors += 1
                    if r < GRID_SIZE-1 and self.grid.grid[r+1][c]: neighbors += 1
                    if c > 0 and self.grid.grid[r][c-1]: neighbors += 1
                    if c < GRID_SIZE-1 and self.grid.grid[r][c+1]: neighbors += 1
                    if neighbors >= 3: single_holes += 1

        weights = {k: 10 for k in keys}
        if empty_cells < (GRID_SIZE * GRID_SIZE * 0.3):
            weights['DOT'] += 30; weights['I'] += 10; weights['O'] -= 5; weights['J'] -= 5; weights['L'] -= 5
        if single_holes > 0: weights['DOT'] += 50 * single_holes
        
        population = list(weights.keys())
        w_list = [max(1, weights[k]) for k in population]
        return random.choices(population, weights=w_list, k=1)[0]

    def refill_hand(self):
        if not self.blocks and self.void_count > 0:
            max_hand = 3
            if self.active_boss_effect == 'The Shrink': max_hand = 2
            
            count = min(max_hand, self.void_count)
            for _ in range(count):
                shape = self.get_smart_block_key()
                self.blocks.append(Block(shape))
                self.void_count -= 1
            self.position_blocks_in_hand()
            
        elif not self.blocks and self.void_count == 0:
            self.check_round_end()

    def check_round_end(self):
        if self.score >= self.level_target:
            self.audio.play('select')
            for t in self.totems:
                if t.trigger_type == 'on_round_end':
                    money, desc = TotemLogic.apply_round_end(t.key, self)
                    if money > 0:
                        self.credits += money
                        self.particle_system.create_text(self.w//2, self.h//2, desc, (100, 255, 100))
            self.state = STATE_LEVEL_COMPLETE
            self.generate_shop()
        else:
            self.audio.play('gameover')
            self.state = STATE_GAME_OVER
            self.crt.trigger_aberration(amount=3, duration=20)
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()

    def next_level(self):
        if self.round < 3:
            self.round += 1
        else:
            self.round = 1
            self.ante += 1
            self.boss_preview = random.choice(list(BOSS_DATA.keys()))
            
            # --- YENİ DÜNYAYA GEÇİŞ KONTROLÜ (ANTE 8 -> 9) ---
            if self.ante == NEW_WORLD_ANTE:
                self.audio.play('explode') # Dramatik ses efekti
                self.particle_system.atmosphere.trigger_shake(30, 10)
                self.crt.trigger_aberration(amount=5, duration=60)
                
                # 1. Totem Yok Etme (Cezalandırma)
                if self.totems:
                    removed = self.totems.pop(random.randrange(len(self.totems)))
                    self.particle_system.create_text(self.w//2, self.h//2, f"WORLD SHIFT: {removed.name} DESTROYED!", (255, 50, 50))
                else:
                    self.particle_system.create_text(self.w//2, self.h//2, "WORLD SHIFT: DARKNESS FALLS", (255, 50, 50))
                
                # 2. Özel Dükkanı Tetikle
                self.force_omega_shop = True
                
        self.state = STATE_ROUND_SELECT

    def position_blocks_in_hand(self):
        area_center_x = SIDEBAR_WIDTH + (PLAY_AREA_W // 2)
        total_width = PLAY_AREA_W * 0.6
        start_x = area_center_x - (total_width // 2)
        gap = total_width // 3
        
        bg_y = VIRTUAL_H - HAND_BG_HEIGHT
        center_y = bg_y + (HAND_BG_HEIGHT // 2)
        
        for i, b in enumerate(self.blocks):
            if b != self.held_block:
                target_x = start_x + (i * gap) + (gap - b.width)//2
                target_y = center_y - (b.height // 2)
                b.rect.x = target_x
                b.rect.y = target_y
                b.original_pos = (target_x, target_y)
                if b.visual_x == 0 and b.visual_y == 0:
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
                if t.key == 'blood_pact' and self.void_count > 0:
                    self.void_count -= 1
        return mult

    def generate_shop(self):
        self.shop_totems = []
        
        # --- OMEGA SHOP (DÜNYA GEÇİŞİNDE) ---
        if self.force_omega_shop:
            # Sadece 3 özel Omega totemi koy
            for k in OMEGA_KEYS:
                self.shop_totems.append(Totem(k, TOTEM_DATA[k]))
            self.force_omega_shop = False # Bayrağı kapat, sonraki dükkanlar normal olsun
        else:
            # --- NORMAL SHOP ---
            # Omega totemleri normal havuzdan çıkar (Sadece özel dükkanda çıksınlar)
            normal_keys = [k for k in TOTEM_DATA.keys() if k not in OMEGA_KEYS]
            for _ in range(3):
                k = random.choice(normal_keys)
                self.shop_totems.append(Totem(k, TOTEM_DATA[k]))
        
        self.state = STATE_SHOP

    def buy_totem(self, t):
        if self.credits >= t.price and len(self.totems) < MAX_TOTEM_SLOTS:
            self.credits -= t.price
            self.totems.append(t)
            for owned in self.totems:
                if owned.key == 'cashback':
                    self.credits += 2
                    self.particle_system.create_text(self.w//2, 100, "+$2 Cashback", (100, 255, 100))
            if t in self.shop_totems: self.shop_totems.remove(t)
            self.audio.play('clear')

    def handle_events(self):
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if self.state == STATE_SCORING: return 

            if self.state == STATE_MENU:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if hasattr(self.ui, 'menu_buttons'):
                        for rect, text in self.ui.menu_buttons:
                            if rect.collidepoint(mx, my):
                                if text == "PLAY": self.start_new_game()
                                elif text == "EXIT": sys.exit()

            elif self.state == STATE_ROUND_SELECT:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if hasattr(self.ui, 'select_buttons'):
                        for btn in self.ui.select_buttons:
                            if btn.collidepoint(mx, my):
                                self.start_round()

            elif self.state == STATE_PAUSE:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if hasattr(self.ui, 'pause_buttons'):
                        yes = self.ui.pause_buttons['YES']
                        no = self.ui.pause_buttons['NO']
                        if yes.collidepoint(mx, my):
                            self.state = STATE_MENU; self.init_game_session_data()
                        elif no.collidepoint(mx, my): self.state = STATE_PLAYING 

            elif self.state == STATE_PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: self.state = STATE_PAUSE
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if hasattr(self, 'menu_btn_rect') and self.menu_btn_rect.collidepoint(mx, my): self.state = STATE_PAUSE
                    if event.button == 1: 
                        for b in self.blocks:
                            if b.rect.collidepoint(mx, my):
                                self.held_block = b
                                self.held_block.dragging = True
                                self.held_block.offset_x = mx - b.visual_x 
                                self.held_block.offset_y = my - b.visual_y
                                self.audio.play('place')
                                break
                    elif event.button == 3 and self.held_block: self.held_block.rotate()
                    elif event.button == 2 and self.held_block: self.held_block.flip()

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and self.held_block:
                        if self.trash_rect.collidepoint(mx, my):
                            current_cost = DISCARD_COST
                            if any(t.key == 'recycler' for t in self.totems): current_cost = 0
                            if self.active_boss_effect == 'The Drain': current_cost = 3
                            if self.credits >= current_cost:
                                self.credits -= current_cost
                                try:
                                    self.blocks.remove(self.held_block)
                                    new_shape = self.get_smart_block_key()
                                    self.blocks.append(Block(new_shape))
                                    self.position_blocks_in_hand()
                                    self.combo_counter = 0
                                    self.particle_system.create_text(mx, my, "REROLL!", (200, 200, 200))
                                except: pass
                            else: self.audio.play('hit')
                            self.held_block.dragging = False
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
                            orig_pos = self.held_block.rect.topleft
                            self.held_block.rect.topleft = (target_px, target_py)
                            
                            if self.grid.is_valid_position(self.held_block, gr, gc):
                                for t in self.totems:
                                    if t.key == 'gamblers_dice':
                                        triggered, bonus = TotemLogic.check_gambling(t.key, self)
                                        if triggered:
                                            self.particle_system.create_text(mx, my, "GAMBLE WIN! x5", (255, 215, 0))
                                            self.score += int(bonus)
                                            self.combo_counter += 1
                                            self.audio.play('clear')
                                            self.blocks.remove(self.held_block)
                                            self.held_block = None
                                            self.state = STATE_SCORING
                                            self.scoring_data = {'base': 100, 'mult': 5.0, 'total': int(bonus)}
                                            return 

                                self.grid.place_block(self.held_block, gr, gc)
                                self.last_grid_pos = (gr, gc)
                                self.last_placed_block_tag = self.held_block.tag
                                
                                for t in self.totems: TotemLogic.apply_on_place(t.key, self)

                                self.is_edge_placement = False
                                for r in range(self.held_block.rows):
                                    for c in range(self.held_block.cols):
                                        if self.held_block.matrix[r][c] == 1:
                                            abs_r = gr + r; abs_c = gc + c
                                            if abs_r == 0 or abs_r == GRID_SIZE-1 or abs_c == 0 or abs_c == GRID_SIZE-1:
                                                self.is_edge_placement = True
                                
                                self.audio.play('place')
                                cells = sum(r.count(1) for r in self.held_block.matrix)
                                base_points = cells * SCORE_PER_BLOCK
                                
                                stones_before = sum(row.count(STONE_COLOR) for row in self.grid.grid if row)
                                
                                cr, cc, col_bonus, match_cnt = self.grid.check_clears()
                                
                                stones_after = sum(row.count(STONE_COLOR) for row in self.grid.grid if row)
                                stones_destroyed = stones_before - stones_after
                                total_clears = len(cr) + len(cc)
                                cleared_cells_count = total_clears * GRID_SIZE
                                
                                if total_clears > 0:
                                    self.grid.trigger_beat() 
                                    self.crt.trigger_aberration(amount=2, duration=5)

                                    base_points += total_clears * SCORE_PER_LINE
                                    if col_bonus > 0:
                                        base_points += col_bonus
                                        self.particle_system.create_text(mx, my - 50, f"COLOR MATCH! +{col_bonus}", (255, 215, 0))

                                    self.credits += total_clears
                                    self.combo_counter += 1
                                    self.screen_shake = 2 * total_clears
                                    self.particle_system.atmosphere.trigger_shake(10, 3) 
                                    self.audio.play('clear')
                                    
                                    theme = self.get_current_theme()
                                    for r in cr:
                                        py = self.grid_offset_y + r*TILE_SIZE + TILE_SIZE//2
                                        for c in range(GRID_SIZE): self.particle_system.create_explosion(self.grid_offset_x + c*TILE_SIZE, py, count=5)
                                    for c in cc:
                                        px = self.grid_offset_x + c*TILE_SIZE + TILE_SIZE//2
                                        for r in range(GRID_SIZE): self.particle_system.create_explosion(px, self.grid_offset_y + r*TILE_SIZE, count=5)
                                    
                                    extra_cash = 0
                                    for t in self.totems:
                                        if t.trigger_type == 'on_clear':
                                            gain = TotemLogic.apply_on_clear(t.key, self, cleared_cells_count, stones_destroyed)
                                            extra_cash += gain
                                    if extra_cash > 0:
                                        self.credits += int(extra_cash)
                                        self.particle_system.create_text(self.w-100, 100, f"+${extra_cash}", (100, 255, 100))
                                    
                                    # Infinity Stone ekstra çarpanı için basit hack:
                                    # Eğer infinity_stone varsa burada ek mult verebiliriz ama TotemLogic'te sadece para verdik.
                                    # İstersen şuraya ekleyebilirsin:
                                    inf_mult = 0
                                    for t in self.totems:
                                        if t.key == 'infinity_stone': inf_mult += 2.0
                                    
                                    mult = self.calculate_totem_mult() + inf_mult

                                    hype_word = random.choice(HYPE_WORDS)
                                    self.particle_system.create_text(self.w//2, self.h//2 - 50, hype_word, (255, 215, 0))
                                    self.blocks.remove(self.held_block)
                                    self.held_block = None
                                    self.state = STATE_SCORING
                                    self.scoring_timer = 0
                                    self.scoring_data = {'base': base_points, 'mult': mult, 'total': int(base_points * mult)}
                                    return
                                else:
                                    arch_bonus = 0
                                    for t in self.totems:
                                        if t.key == 'architect':
                                            arch_bonus += 50
                                            self.particle_system.create_text(target_px, target_py, "+50 Arch", (100, 100, 255))
                                    self.score += base_points + arch_bonus
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
                    pass

            elif self.state == STATE_SHOP:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for t in self.shop_totems:
                        if t.rect.collidepoint(mx, my): self.buy_totem(t)
                    if mx > self.w - 150 and my > self.h - 50: self.next_level()

            elif self.state == STATE_GAME_OVER:
                if event.type == pygame.MOUSEBUTTONDOWN: self.state = STATE_MENU; self.init_game_session_data()

    def update(self):
        self.ui.update()
        self.particle_system.update()
        if self.screen_shake > 0: self.screen_shake -= 1
        
        self.grid.update()
        
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
                if self.score >= self.level_target and not self.blocks and self.void_count == 0: self.check_round_end()

    def draw(self):
        self.ui.draw_bg(self.screen)
        
        if self.state == STATE_MENU:
            self.ui.draw_menu(self.screen, self.high_score)
        elif self.state == STATE_ROUND_SELECT:
            self.ui.draw_round_select(self.screen, self)
        else:
            boss_shake_x, boss_shake_y = self.particle_system.atmosphere.get_shake_offset()
            normal_shake_x = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
            normal_shake_y = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
            
            total_shake_x = boss_shake_x + normal_shake_x
            total_shake_y = boss_shake_y + normal_shake_y

            self.ui.draw_sidebar(self.screen, self)
            self.ui.draw_hand_bg(self.screen)
            self.ui.draw_top_bar(self.screen, self)
            
            theme = self.get_current_theme()
            
            self.grid.draw(self.screen, total_shake_x, total_shake_y, theme)
            
            if self.active_boss_effect != 'The Haze': 
                if self.held_block and self.held_block.dragging:
                    cur_x = pygame.mouse.get_pos()[0] - self.held_block.offset_x
                    cur_y = pygame.mouse.get_pos()[1] - self.held_block.offset_y
                    check_x = cur_x + (TILE_SIZE / 2); check_y = cur_y + (TILE_SIZE / 2)
                    gr, gc = self.get_grid_pos(check_x, check_y)
                    if gr is not None and gc is not None:
                        target_px = self.grid_offset_x + gc * TILE_SIZE
                        target_py = self.grid_offset_y + gr * TILE_SIZE
                        orig = self.held_block.rect.topleft
                        self.held_block.rect.topleft = (target_px, target_py)
                        if self.grid.is_valid_position(self.held_block, gr, gc):
                            self.held_block.draw(self.screen, target_px, target_py, 1.0, 60, theme['style'])
                        self.held_block.rect.topleft = orig
            
            for b in self.blocks:
                if b != self.held_block: b.draw(self.screen, 0, 0, 0.8, 255, theme['style'])
            if self.held_block: self.held_block.draw(self.screen, 0, 0, 1.0, 255, theme['style'])
            
            danger_level = 0.0
            if self.active_boss_effect: danger_level = 0.2 
            self.particle_system.atmosphere.draw_overlay(self.screen, danger_level)
            
            self.particle_system.draw(self.screen)
            self.ui.draw_hud_elements(self.screen, self)
            if self.state == STATE_SHOP: self.ui.draw_shop(self.screen, self)
            elif self.state == STATE_PAUSE: self.ui.draw_pause_overlay(self.screen)
            elif self.state == STATE_GAME_OVER: self.ui.draw_game_over(self.screen, self.score)
        
        self.crt.draw(self.screen)
        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)