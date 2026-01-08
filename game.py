# game.py
import pygame
import sys
import random
import math
import os
from settings import *
from settings import USE_FULLSCREEN, WINDOW_W, WINDOW_H, STATE_DEBT, PHARAOH_QUOTES, COLLECTIBLES, STATE_COLLECTION, STATE_SETTINGS, STATE_TRAINING, RESOLUTIONS
from grid import Grid
from block import Block
from effects import ParticleSystem, BossAtmosphere
from totems import Totem, TotemLogic, TOTEM_DATA, OMEGA_KEYS
from runes import Rune, RUNE_DATA
from ui import UIManager       
from audio import AudioManager 
from crt import CRTManager
from save_data import SaveManager 

class Game:
    def __init__(self):
        # Center window on screen
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        
        pygame.init()
        
        # Load save data FIRST (before window creation) to check fullscreen preference
        self.save_manager = SaveManager()
        saved_settings = self.save_manager.data.get('settings', {})
        saved_fullscreen = saved_settings.get('fullscreen', False)
        
        # --- EKRAN AYARLARI ---
        # Always start in windowed mode (SCALED | RESIZABLE only)
        # pygame.SCALED automatically scales to window size without manual virtual surface
        # pygame.RESIZABLE allows window resizing
        # vsync=1 prevents screen tearing
        flags = pygame.SCALED | pygame.RESIZABLE
        
        self.screen = pygame.display.set_mode((VIRTUAL_W, VIRTUAL_H), flags, vsync=1)
        self.fullscreen = False
        
        # Apply fullscreen AFTER initialization if saved preference was True
        # This "late toggle" avoids Mac Retina scaling glitches
        if saved_fullscreen:
            self.toggle_fullscreen()
        
        self.w = VIRTUAL_W
        self.h = VIRTUAL_H
        
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        
        self.crt = CRTManager()
        self.audio = AudioManager()
        self.ui = UIManager()
        self.particle_system = ParticleSystem()
        self.high_score = self.load_high_score()
        
        # Load save data and apply settings
        self.save_data = self.save_manager.get_data()
        self._apply_saved_settings()
        
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
        
        self.force_omega_shop = False 
        
        self.input_cooldown = 0
        self.tutorial_step = 0  # Tutorial progress tracker
        
        # Check if player has completed tutorial
        if not self.save_manager.data.get('tutorial_complete', False):
            self.state = STATE_TRAINING  # New player -> Training mode
        else:
            self.state = STATE_MENU  # Returning player -> Main menu
        
        self.init_game_session_data()
        
        # Initialize tutorial mode if needed
        if self.state == STATE_TRAINING:
            self.init_tutorial_mode() 

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
        if self.ante >= NEW_WORLD_ANTE:
            return THEMES['CRIMSON']
        return THEMES['NEON']

    def init_game_session_data(self):
        self.credits = STARTING_CREDITS
        self.totems = [] 
        
        # --- YENİ: RÜN ENVANTERİ ---
        self.consumables = [] 
        self.max_consumables = 3
        self.held_rune = None # Sürüklenen rün
        
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
        
        # --- DEBT SCREEN VARIABLES ---
        self.debt_old_value = 0
        self.debt_displayed_value = 0
        self.debt_animation_timer = 0
        self.debt_payment_amount = 0
        self.debt_shake_intensity = 0
        self.debt_scale = 1.0
        self.debt_quote_index = 0
        self.debt_quote_char_index = 0
        self.debt_quote_timer = 0
        self.newly_unlocked_items = []  # Items unlocked in this debt screen

    def init_tutorial_mode(self):
        """Initialize the tutorial with a simple setup for learning"""
        # Reset tutorial progress
        self.tutorial_step = 0
        
        # Give player some simple blocks to start
        self.grid.reset()
        self.blocks = []
        self.held_block = None
        
        # Add 3 simple blocks to hand
        tutorial_shapes = ['I', 'DOT', 'L']  # Simple shapes for learning
        for shape in tutorial_shapes:
            self.blocks.append(Block(shape))
        
        self.position_blocks_in_hand()
        
        # Set up simple game state
        self.score = 0
        self.visual_score = 0
        self.void_count = 20  # Plenty for tutorial
        self.combo_counter = 0
        self.level_target = 100  # Tutorial target (not enforced)

    def get_blind_target(self, round_num):
        base_target = 300 * (self.ante ** 1.3)
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
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.grid.grid[r][c] is None: empty_cells += 1
        weights = {k: 10 for k in keys}
        if empty_cells < (GRID_SIZE * GRID_SIZE * 0.3):
            weights['DOT'] += 30; weights['I'] += 10; weights['O'] -= 5; weights['J'] -= 5; weights['L'] -= 5
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
        # Calculate debt payment (based on round score)
        self.debt_payment_amount = self.score
        
        # Save old debt value for animation
        save_data = self.save_manager.get_data()
        self.debt_old_value = save_data['total_debt'] - save_data['debt_paid']
        
        # Pay the debt
        result = self.save_manager.pay_debt(self.debt_payment_amount)
        self.debt_displayed_value = self.debt_old_value  # Start animation from old value
        
        # Initialize debt screen animation
        self.debt_animation_timer = 0
        self.debt_shake_intensity = 0
        self.debt_scale = 1.0
        self.debt_quote_index = random.randint(0, len(PHARAOH_QUOTES) - 1)
        self.debt_quote_char_index = 0
        self.debt_quote_timer = 0
        self.newly_unlocked_items = []  # Reset newly unlocked items
        if hasattr(self, '_unlocks_checked'):
            delattr(self, '_unlocks_checked')  # Reset unlock check flag
        
        # Transition to debt screen
        self.state = STATE_DEBT
        
    def continue_from_debt(self):
        """Called when player clicks continue on debt screen"""
        if self.round < 3:
            self.round += 1
        else:
            self.round = 1
            self.ante += 1
            self.boss_preview = random.choice(list(BOSS_DATA.keys()))
            if self.ante == NEW_WORLD_ANTE:
                self.audio.play('explode')
                self.particle_system.atmosphere.trigger_shake(30, 10)
                self.crt.trigger_aberration(amount=5, duration=60)
                if self.totems:
                    removed = self.totems.pop(random.randrange(len(self.totems)))
                    self.particle_system.create_text(self.w//2, self.h//2, f"WORLD SHIFT: {removed.name} DESTROYED!", (255, 50, 50))
                self.force_omega_shop = True
                
        self.state = STATE_ROUND_SELECT
    
    def _check_collectible_unlocks(self):
        """Check if any collectibles were unlocked by the recent debt payment"""
        save_data = self.save_manager.get_data()
        total_paid = save_data['debt_paid']
        old_paid = total_paid - self.debt_payment_amount
        
        self.newly_unlocked_items = []
        
        for item in COLLECTIBLES:
            # Check if this payment crossed the unlock threshold
            if old_paid < item['unlock_at'] <= total_paid:
                # New unlock!
                if not self.save_manager.is_unlocked(item['id']):
                    self.save_manager.unlock_item(item['id'])
                    self.newly_unlocked_items.append(item)
                    # Play sound effect if available
                    if hasattr(self.audio, 'play'):
                        self.audio.play('clear')  # Use existing sound for now
    
    def apply_settings(self):
        """Apply settings from temp_settings to game and save to file"""
        if not hasattr(self, 'temp_settings'):
            return
        
        # Get current save data
        save_data = self.save_manager.get_data()
        
        # Update settings in save data
        save_data['settings']['fullscreen'] = self.temp_settings['fullscreen']
        save_data['settings']['volume'] = self.temp_settings['volume']
        
        # Apply resolution
        res_index = self.temp_settings['resolution_index']
        resolution = RESOLUTIONS[res_index]
        
        # Apply display mode
        if self.temp_settings['fullscreen']:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(resolution)
        
        # Apply volume
        if hasattr(self.audio, 'set_volume'):
            self.audio.set_volume(self.temp_settings['volume'])
        
        # Save to file
        self.save_manager.save_data(save_data)
        
        # Clean up temp settings
        delattr(self, 'temp_settings')
    
    def _apply_saved_settings(self):
        """Apply settings from save file on startup (volume only - screen already set)"""
        save_data = self.save_manager.get_data()
        settings = save_data.get('settings', {})
        
        # Apply volume
        volume = settings.get('volume', 0.5)
        if hasattr(self.audio, 'set_volume'):
            self.audio.set_volume(volume)

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
        if self.force_omega_shop:
            for k in OMEGA_KEYS:
                self.shop_totems.append(Totem(k, TOTEM_DATA[k]))
            self.force_omega_shop = False 
        else:
            normal_keys = [k for k in TOTEM_DATA.keys() if k not in OMEGA_KEYS]
            for _ in range(3):
                k = random.choice(normal_keys)
                self.shop_totems.append(Totem(k, TOTEM_DATA[k]))
        
        # --- RÜN DÜKKANI ---
        self.shop_runes = []
        r_keys = list(RUNE_DATA.keys())
        for _ in range(2):
            rk = random.choice(r_keys)
            self.shop_runes.append(Rune(rk))
            
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

    def buy_rune(self, r):
        if self.credits >= r.price and len(self.consumables) < self.max_consumables:
            self.credits -= r.price
            self.consumables.append(r)
            if r in self.shop_runes: self.shop_runes.remove(r)
            self.audio.play('select')

    def toggle_fullscreen(self):
        """Toggle between windowed and fullscreen mode"""
        self.fullscreen = not self.fullscreen
        
        try:
            # Try using pygame's toggle_fullscreen method (Pygame 2.0+)
            pygame.display.toggle_fullscreen()
        except AttributeError:
            # Fallback for older pygame versions: recreate display with new flags
            flags = pygame.SCALED | pygame.RESIZABLE
            if self.fullscreen:
                flags |= pygame.FULLSCREEN
            self.screen = pygame.display.set_mode((VIRTUAL_W, VIRTUAL_H), flags, vsync=1)
        
        # Save fullscreen preference immediately
        self.save_manager.data['settings']['fullscreen'] = self.fullscreen
        self.save_manager.save_data()

    def handle_events(self):
        # CRITICAL: Prevent ghost clicks during state transitions
        if self.input_cooldown > 0:
            pygame.event.clear()  # Discard events during cooldown
            return
        
        # Get mouse position directly - no coordinate conversion needed
        self.mouse_x, self.mouse_y = pygame.mouse.get_pos()
        mx, my = self.mouse_x, self.mouse_y
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            
            # Handle window resize with automatic scaling
            if event.type == pygame.VIDEORESIZE:
                # pygame.SCALED automatically handles coordinate mapping
                pygame.display.flip()
            
            # Handle fullscreen toggle with F or F11 key
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f or event.key == pygame.K_F11:
                    self.toggle_fullscreen()
            
            if self.state == STATE_SCORING: return 

            if self.state == STATE_MENU:
                # Handle menu button clicks - only on MOUSEBUTTONUP (not MOUSEBUTTONDOWN)
                # This prevents double-click issues
                if event.type == pygame.MOUSEBUTTONUP:
                    if hasattr(self.ui, 'menu_buttons'):
                        for rect, text in self.ui.menu_buttons:
                            if rect.collidepoint(mx, my):
                                if text == "PLAY": 
                                    self.start_new_game()
                                elif text == "SETTINGS":
                                    self.audio.play('select')
                                    # Clean temp settings when entering
                                    if hasattr(self, 'temp_settings'):
                                        delattr(self, 'temp_settings')
                                    self.state = STATE_SETTINGS
                                elif text == "COLLECTION":
                                    self.audio.play('select')
                                    self.state = STATE_COLLECTION
                                elif text == "TRAINING":
                                    self.audio.play('select')
                                    self.state = STATE_TRAINING
                                    self.input_cooldown = 15  # Prevent accidental clicks during transition
                                    self.init_tutorial_mode()  # Initialize practice session (no save data affected)
                                elif text == "EXIT": 
                                    sys.exit()

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
                            self.state = STATE_MENU
                            self.init_game_session_data()
                            self.input_cooldown = 15  # Prevent ghost click on PLAY button
                        elif no.collidepoint(mx, my): self.state = STATE_PLAYING
            
            elif self.state == STATE_TRAINING:
                # Tutorial event handling
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Step 0: Drag block to grid
                    if self.tutorial_step == 0:
                        for b in self.blocks:
                            if b.rect.collidepoint(mx, my):
                                self.held_block = b
                                b.dragging = True
                                b.offset_x = mx - b.rect.x
                                b.offset_y = my - b.rect.y
                                self.audio.play('select')
                    
                    # Steps 1-2: Click to continue
                    elif self.tutorial_step in [1, 2]:
                        self.tutorial_step += 1
                        self.audio.play('select')
                    
                    # Step 3: Finish tutorial
                    elif self.tutorial_step == 3:
                        self.save_manager.data['tutorial_complete'] = True
                        self.save_manager.save_data()
                        self.state = STATE_MENU
                        self.init_game_session_data()
                        self.tutorial_step = 0
                        self.input_cooldown = 15
                        self.audio.play('select')
                
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    # Step 0: Complete when block placed on grid
                    if self.tutorial_step == 0 and self.held_block:
                        cur_x = mx - self.held_block.offset_x
                        cur_y = my - self.held_block.offset_y
                        check_x = cur_x + (TILE_SIZE / 2)
                        check_y = cur_y + (TILE_SIZE / 2)
                        gr, gc = self.get_grid_pos(check_x, check_y)
                        
                        if gr is not None and gc is not None:
                            if self.grid.is_valid_position(self.held_block, gr, gc):
                                self.grid.place_block(self.held_block, gr, gc)
                                self.blocks.remove(self.held_block)
                                self.audio.play('place')
                                self.held_block = None
                                self.tutorial_step = 1  # Advance to next step
                            else:
                                self.held_block.dragging = False
                                self.position_blocks_in_hand()
                                self.held_block = None
                        else:
                            self.held_block.dragging = False
                            self.position_blocks_in_hand()
                            self.held_block = None
                
                elif event.type == pygame.MOUSEMOTION:
                    if self.held_block and self.held_block.dragging:
                        # Block dragging handled in update
                        pass 

            elif self.state == STATE_PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: self.state = STATE_PAUSE
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if hasattr(self, 'menu_btn_rect') and self.menu_btn_rect.collidepoint(mx, my): self.state = STATE_PAUSE
                    if event.button == 1: 
                        # --- 1. Rünleri Kontrol Et (Sürükleme) ---
                        rune_clicked = False
                        for r in self.consumables:
                            if r.rect and r.rect.collidepoint(mx, my):
                                self.held_rune = r
                                self.held_rune.dragging = True
                                rune_clicked = True
                                break
                        
                        if not rune_clicked:
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
                    # --- Rün Bırakma Mantığı (Çoklu Rün Sistemi) ---
                    if self.held_rune:
                        dropped_on_block = False
                        for b in self.blocks:
                            if b.rect.collidepoint(mx, my):
                                # Hangi hücreye bırakıldığını hesapla
                                rel_x = mx - b.visual_x
                                rel_y = my - b.visual_y
                                cell_col = int(rel_x // TILE_SIZE)
                                cell_row = int(rel_y // TILE_SIZE)
                                
                                # Hücrenin geçerli olup olmadığını kontrol et (matris sınırları içinde ve dolu mu)
                                if 0 <= cell_row < b.rows and 0 <= cell_col < b.cols:
                                    if b.matrix[cell_row][cell_col] == 1:
                                        # Rünü hücreye ata (aynı hücrede varsa üzerine yazar)
                                        b.runes[(cell_row, cell_col)] = self.held_rune
                                        self.consumables.remove(self.held_rune)
                                        self.particle_system.create_text(mx, my, "RUNE APPLIED!", self.held_rune.color)
                                        self.audio.play('select')
                                        dropped_on_block = True
                                
                                break
                        self.held_rune.dragging = False
                        self.held_rune = None
                        if dropped_on_block: return

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
                                self.last_placed_block_tag = getattr(self.held_block, 'tag', 'NONE')
                                
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
                                
                                # --- PATLAMA KONTROLÜ (RÜN DESTEKLİ) ---
                                cr, cc, col_bonus, match_cnt, rune_bonuses = self.grid.check_clears()
                                
                                stones_before = sum(row.count(STONE_COLOR) for row in self.grid.grid if row)
                                stones_after = sum(row.count(STONE_COLOR) for row in self.grid.grid if row) # Hatalı logic düzeltildi (stones count logic was slightly off in previous iterations, keep simple)
                                stones_destroyed = 0 # Basit tutalım şimdilik
                                
                                total_clears = len(cr) + len(cc)
                                cleared_cells_count = total_clears * GRID_SIZE
                                
                                if total_clears > 0:
                                    self.grid.trigger_beat() 
                                    self.crt.trigger_aberration(amount=2, duration=5)

                                    base_points += total_clears * SCORE_PER_LINE
                                    if col_bonus > 0:
                                        base_points += col_bonus
                                        self.particle_system.create_text(mx, my - 50, f"COLOR MATCH! +{col_bonus}", (255, 215, 0))
                                    
                                    # Rün Bonusları
                                    base_points += rune_bonuses['chips']
                                    if rune_bonuses['chips'] > 0:
                                        self.particle_system.create_text(mx, my-70, f"RUNE CHIPS! +{rune_bonuses['chips']}", (100, 200, 255))

                                    self.credits += total_clears
                                    self.credits += rune_bonuses['money']
                                    
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
                                    
                                    # Mult Hesapla (Rünler Dahil)
                                    mult = self.calculate_totem_mult()
                                    mult += rune_bonuses['mult_add']
                                    mult *= rune_bonuses['mult_x']

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
                    # Rün Satın Alma
                    for r in self.shop_runes:
                        if r.rect and r.rect.collidepoint(mx, my): self.buy_rune(r)
                        
                    if mx > self.w - 150 and my > self.h - 50: self.next_level()
            
            elif self.state == STATE_DEBT:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if continue button was clicked (handled by UI)
                    if hasattr(self.ui, 'debt_continue_button'):
                        if self.ui.debt_continue_button.collidepoint(mx, my):
                            self.audio.play('select')
                            self.continue_from_debt()
                            self.state = STATE_ROUND_SELECT
                            self.input_cooldown = 15  # Prevent ghost click on round select
            
            elif self.state == STATE_COLLECTION:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if back button was clicked
                    if hasattr(self.ui, 'collection_back_button'):
                        if self.ui.collection_back_button.collidepoint(mx, my):
                            self.audio.play('select')
                            self.state = STATE_MENU
                
                elif event.type == pygame.MOUSEWHEEL:
                    # Handle collection scroll
                    if event.y > 0:  # Scroll up
                        self.ui.collection_scroll_y -= 30
                    elif event.y < 0:  # Scroll down
                        self.ui.collection_scroll_y += 30
                    
                    # Clamp scroll value (max scroll will be calculated in draw_collection)
                    self.ui.collection_scroll_y = max(0, self.ui.collection_scroll_y)
            
            elif self.state == STATE_SETTINGS:
                if event.type == pygame.MOUSEBUTTONDOWN and hasattr(self.ui, 'settings_buttons'):
                    btns = self.ui.settings_buttons
                    
                    # Fullscreen toggle
                    if 'fullscreen' in btns and btns['fullscreen'].collidepoint(mx, my):
                        self.temp_settings['fullscreen'] = not self.temp_settings['fullscreen']
                        self.audio.play('select')
                    
                    # Resolution arrows
                    elif 'res_left' in btns and btns['res_left'].collidepoint(mx, my):
                        self.temp_settings['resolution_index'] = (self.temp_settings['resolution_index'] - 1) % len(RESOLUTIONS)
                        self.audio.play('select')
                    
                    elif 'res_right' in btns and btns['res_right'].collidepoint(mx, my):
                        self.temp_settings['resolution_index'] = (self.temp_settings['resolution_index'] + 1) % len(RESOLUTIONS)
                        self.audio.play('select')
                    
                    # Save button
                    elif 'save' in btns and btns['save'].collidepoint(mx, my):
                        self.apply_settings()
                        self.audio.play('clear')
                        self.state = STATE_MENU
                    
                    # Cancel button
                    elif 'back' in btns and btns['back'].collidepoint(mx, my):
                        # Discard temp settings
                        if hasattr(self, 'temp_settings'):
                            delattr(self, 'temp_settings')
                        self.audio.play('select')
                        self.state = STATE_MENU
                
                # Volume slider dragging
                elif event.type == pygame.MOUSEMOTION:
                    if pygame.mouse.get_pressed()[0] and hasattr(self.ui, 'settings_buttons'):
                        slider = self.ui.settings_buttons.get('volume_slider')
                        if slider and slider.collidepoint(mx, my):
                            # Calculate volume from mouse position
                            relative_x = mx - slider.x
                            volume = max(0.0, min(1.0, relative_x / slider.width))
                            self.temp_settings['volume'] = volume

            elif self.state == STATE_GAME_OVER:
                if event.type == pygame.MOUSEBUTTONDOWN: self.state = STATE_MENU; self.init_game_session_data()

    def update(self):
        # Decrease input cooldown
        if self.input_cooldown > 0:
            self.input_cooldown -= 1
        
        self.ui.update()
        self.particle_system.update()
        if self.screen_shake > 0: self.screen_shake -= 1
        
        self.grid.update()
        
        diff = self.score - self.visual_score
        if diff > 0: self.visual_score += max(1, diff // 5)
        
        if self.state == STATE_TRAINING:
            # Tutorial mode - similar updates to PLAYING but controlled progression
            for b in self.blocks: b.update()
            if self.held_rune and self.held_rune.dragging:
                mx, my = pygame.mouse.get_pos()
                self.held_rune.x = mx
                self.held_rune.y = my
        
        elif self.state == STATE_PLAYING:
            for b in self.blocks: b.update()
            # Rune dragging - use direct mouse coordinates (no conversion needed)
            if self.held_rune and self.held_rune.dragging:
                mx, my = pygame.mouse.get_pos()
                self.held_rune.x = mx
                self.held_rune.y = my
        
        elif self.state == STATE_DEBT:
            # Debt screen animation logic
            self.debt_animation_timer += 1
            
            # Countdown animation (fast)
            if self.debt_displayed_value > (self.debt_old_value - self.debt_payment_amount):
                decrement = max(1, self.debt_payment_amount // 60)  # Complete in ~60 frames
                self.debt_displayed_value -= decrement
                if self.debt_displayed_value < (self.debt_old_value - self.debt_payment_amount):
                    self.debt_displayed_value = self.debt_old_value - self.debt_payment_amount
                
                # Shake effect while counting
                self.debt_shake_intensity = random.randint(-2, 2)
            else:
                # Countdown finished
                self.debt_shake_intensity = 0
                
                # Check for unlocks (only once, right when countdown finishes)
                if self.debt_animation_timer == 60 and not hasattr(self, '_unlocks_checked'):
                    self._check_collectible_unlocks()
                    self._unlocks_checked = True
                
                # Pop effect (happens once)
                if self.debt_animation_timer == 61:  # Right after countdown
                    self.debt_scale = 1.3  # Scale up
                elif self.debt_animation_timer > 61:
                    # Scale back down smoothly
                    self.debt_scale = max(1.0, self.debt_scale - 0.02)
            
            # Typewriter effect for quote
            self.debt_quote_timer += 1
            if self.debt_quote_timer >= 3:  # Add character every 3 frames
                self.debt_quote_timer = 0
                if self.debt_quote_char_index < len(PHARAOH_QUOTES[self.debt_quote_index]):
                    self.debt_quote_char_index += 1
            
        elif self.state == STATE_SCORING:
            self.scoring_timer += 1
            if self.scoring_timer > 60:
                self.score += self.scoring_data['total']
                self.state = STATE_PLAYING
                self.refill_hand()
                if self.score >= self.level_target and not self.blocks and self.void_count == 0: self.check_round_end()

    def draw(self):
        # All rendering goes directly to screen
        self.ui.draw_bg(self.screen)
        
        if self.state == STATE_MENU:
            self.ui.draw_menu(self.screen, self.high_score)
        elif self.state == STATE_TRAINING:
            # Draw training mode (game board + tutorial overlay)
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
            
            for b in self.blocks:
                if b != self.held_block: b.draw(self.screen, 0, 0, 0.8, 255, theme['style'])
            
            if self.held_block and self.held_block.dragging:
                cur_x = self.mouse_x - self.held_block.offset_x
                cur_y = self.mouse_y - self.held_block.offset_y
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
            
            self.particle_system.draw(self.screen)
            self.ui.draw_hud_elements(self.screen, self)
            
            # Draw tutorial overlay on top
            self.ui.draw_training_overlay(self.screen, self.tutorial_step)
        elif self.state == STATE_ROUND_SELECT:
            self.ui.draw_round_select(self.screen, self)
        elif self.state == STATE_DEBT:
            self.ui.draw_debt_screen(self.screen, self)
        elif self.state == STATE_COLLECTION:
            self.ui.draw_collection(self.screen, self)
        elif self.state == STATE_SETTINGS:
            self.ui.draw_settings(self.screen, self)
        else:
            boss_shake_x, boss_shake_y = self.particle_system.atmosphere.get_shake_offset()
            normal_shake_x = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
            normal_shake_y = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
            
            total_shake_x = boss_shake_x + normal_shake_x
            total_shake_y = boss_shake_y + normal_shake_y

            self.ui.draw_sidebar(self.screen, self)
            self.ui.draw_hand_bg(self.screen)
            self.ui.draw_top_bar(self.screen, self)
            
            # --- RÜNLERİ ÇİZ (Envanter - Sürüklenmeyen) ---
            if self.state == STATE_PLAYING:
                start_x = SIDEBAR_WIDTH + 20
                start_y = 60 # Totemlerin altı
                for i, r in enumerate(self.consumables):
                    if not r.dragging:
                        r.x = start_x + i * 50
                        r.y = start_y
                        r.rect = pygame.Rect(r.x, r.y, 40, 40)
                        # Basit Rün Çizimi (Yuvarlak)
                        pygame.draw.circle(self.screen, (20,20,30), (r.x+20, r.y+20), 20)
                        pygame.draw.circle(self.screen, r.color, (r.x+20, r.y+20), 18)
                        font = pygame.font.SysFont("Arial", 20, bold=True)
                        txt = font.render(r.icon, True, (255,255,255))
                        self.screen.blit(txt, txt.get_rect(center=(r.x+20, r.y+20)))

            theme = self.get_current_theme()
            self.grid.draw(self.screen, total_shake_x, total_shake_y, theme)
            
            if self.active_boss_effect != 'The Haze': 
                if self.held_block and self.held_block.dragging:
                    # Get mouse position directly
                    cur_x = self.mouse_x - self.held_block.offset_x
                    cur_y = self.mouse_y - self.held_block.offset_y
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
            
            # --- SÜRÜKLENEN RÜN ÇİZİMİ (Grid ve blokların ÜSTÜnde - Z-Index Fix) ---
            if self.state == STATE_PLAYING and self.held_rune and self.held_rune.dragging:
                rx, ry = self.held_rune.x, self.held_rune.y
                # Biraz büyük çiz (sürüklenirken)
                pygame.draw.circle(self.screen, (20, 20, 30), (rx, ry), 24)
                pygame.draw.circle(self.screen, self.held_rune.color, (rx, ry), 22, 3)
                font = pygame.font.SysFont("Arial", 22, bold=True)
                txt = font.render(self.held_rune.icon, True, self.held_rune.color)
                self.screen.blit(txt, txt.get_rect(center=(rx, ry)))
            
            danger_level = 0.0
            if self.active_boss_effect: danger_level = 0.2 
            self.particle_system.atmosphere.draw_overlay(self.screen, danger_level)
            
            self.particle_system.draw(self.screen)
            self.ui.draw_hud_elements(self.screen, self)
            
            if self.state == STATE_SHOP:
                self.ui.draw_shop(self.screen, self)
                # NOT: Rünler artık sadece ui.draw_shop içinde çiziliyor (çift çizim kaldırıldı)

            elif self.state == STATE_PAUSE: self.ui.draw_pause_overlay(self.screen)
            elif self.state == STATE_GAME_OVER: self.ui.draw_game_over(self.screen, self.score)
            
            # --- TOOLTIP KATMANI (En son çizilir - Z-Index düzeltmesi) ---
            # Shop ekranı kendi tooltip'ini çiziyor, diğer durumlar için bu katmanı kullan
            if self.state != STATE_SHOP:
                self.ui.draw_final_tooltip_layer(self.screen, self)
            
            # --- SÜRÜKLENEN BLOK ÇİZİMİ (En son çizilir - Tüm nesnelerin üstünde) ---
            # Held block is drawn last so it appears on top of everything
            if self.held_block: 
                self.held_block.draw(self.screen, 0, 0, 1.0, 255, theme['style'])
        
        # Apply CRT effects to screen
        self.crt.draw(self.screen)
        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)