# game.py
import pygame
import sys
import random
import math
import os
from settings import *
from settings import USE_FULLSCREEN, WINDOW_W, WINDOW_H, STATE_DEBT, COLLECTIBLES, STATE_COLLECTION, STATE_SETTINGS, STATE_TRAINING, RESOLUTIONS, STATE_INTRO, STATE_DEMO_END, STATE_COMING_SOON
from languages import LANGUAGES
from grid import Grid
import intro
from block import Block
from effects import ParticleSystem, PyroBackground
from totems import Totem, TotemLogic, TOTEM_DATA, OMEGA_KEYS
from runes import Rune, RUNE_DATA
from ui import UIManager       
from audio import AudioManager 
from crt import CRTManager
from save_data import SaveManager
from pyro_manager import PyroManager

def resource_path(relative_path):
    """ Dosyanın nerede olduğunu akıllıca bulur """
    # 1. Önce PyInstaller'ın içindeki (_internal) klasöre bak
    if hasattr(sys, '_MEIPASS'):
        path_in_meipass = os.path.join(sys._MEIPASS, relative_path)
        if os.path.exists(path_in_meipass):
            return path_in_meipass

    # 2. Orada yoksa EXE'nin yanındaki klasöre bak
    try:
        base_path = os.path.dirname(sys.executable)
    except:
        base_path = os.path.abspath(".")
    
    path_next_to_exe = os.path.join(base_path, relative_path)
    if os.path.exists(path_next_to_exe):
        return path_next_to_exe
        
    # 3. Hiçbiri değilse geliştirme ortamıdır
    return os.path.join(os.path.abspath("."), relative_path)

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
        self.debt_shake_intensity = 0
        self.debt_scale = 1.0
        self.debt_quote_index = 0
        self.debt_quote_char_index = 0
        self.debt_quote_timer = 0
        # Active quote text for debt typewriter effect (defaults safe)
        self.current_quote_key = "PHARAOH_1"  # Default key for quote lookup
        self.current_quote_text = "..."
        self.newly_unlocked_items = []  # Items unlocked in this debt screen
        # Global input guard to prevent ghost clicks after state changes
        self.input_cooldown = 0
        # Reset progress confirmation flag
        self.show_reset_confirm = False

        # Core game state defaults
        self.state = STATE_INTRO
        self.ante = 1
        self.round = 1
        self.endless_mode = False
        self.force_omega_shop = False
        self.max_consumables = 5
        self.credits = 0
        self.high_score = self.save_manager.data.get('high_score', 0)
        self.shake_intensity = 0.0
        self.scoring_data = {'base': 0, 'mult': 0, 'total': 0}
        # Apply saved fullscreen preference loaded earlier
        self.fullscreen = bool(saved_fullscreen)
        self.theme = 'NEON'

        # Language / font setup with saved preference and safety fallback
        initial_lang = saved_settings.get('language', DEFAULT_LANGUAGE) if isinstance(saved_settings, dict) else DEFAULT_LANGUAGE
        if initial_lang not in AVAILABLE_LANGUAGES:
            initial_lang = DEFAULT_LANGUAGE
        self.current_language = initial_lang
        lang_meta = LANGUAGES.get(self.current_language, next(iter(LANGUAGES.values())))
        self.font_name = lang_meta.get('font', pygame.font.get_default_font())
        self.font_size_offset = lang_meta.get('size_offset', 0)

        # Display / systems
        # Start with saved fullscreen preference applied to flags
        flags = pygame.SCALED | pygame.RESIZABLE
        if getattr(self, 'fullscreen', False):
            try:
                flags |= pygame.FULLSCREEN
            except Exception:
                pass
        self.screen = pygame.display.set_mode((VIRTUAL_W, VIRTUAL_H), flags, vsync=1)
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        # Cache virtual dimensions for convenience where used
        self.w = VIRTUAL_W
        self.h = VIRTUAL_H
        self.audio = AudioManager()
        self.ui = UIManager(self)
        self.pyro_manager = PyroManager(self)
        self.crt = CRTManager()

        # PYRO MODU DEĞİŞKENLERİ
        self.enemies = []  # Düşman listesi
        self.pyro_spawn_timer = 0
        self.pyro_flash_timer = 0 # Hasar alınca ekranın kızarması için
        self.pharaoh_timer = 0  # Pharaoh dialogue timer
        # Tutorial-specific state (safety defaults)
        self.tutorial_step = 0
        self.tutorial_enemy = None
        try:
            # Crosshair (Nişangah) yükle, yoksa None kalsın (draw'da çizeriz)
            self.crosshair_img = pygame.image.load(resource_path('assets/crosshair.png')).convert_alpha()
            self.crosshair_img = pygame.transform.scale(self.crosshair_img, (32, 32))
        except:
            self.crosshair_img = None
        
        # Initialize intro video manager (after screen creation)
        self.intro_manager = intro.IntroManager(self.screen, resource_path("assets/sphenks_video.mp4"))
        # Play intro audio immediately
        pygame.mixer.music.load(resource_path("assets/intro_audio.mp3"))
        pygame.mixer.music.play()
        self.particle_system = ParticleSystem()
        # Pyro background (dynamic atmosphere for Round 3)
        try:
            self.pyro_bg = PyroBackground(VIRTUAL_W, VIRTUAL_H)
        except Exception:
            self.pyro_bg = None

        # Grid and positioning
        self.grid = Grid()
        self.grid.reset()
        self.grid_offset_x = GRID_OFFSET_X
        self.grid_offset_y = GRID_OFFSET_Y
        self.held_block = None
        self.held_rune = None
        self.blocks = []
        self.consumables = []
        self.totems = []
        self.shop_totems = []
        self.shop_runes = []
        self.active_boss_effect = None
        self.boss_preview = None
        self.trash_rect = pygame.Rect(SIDEBAR_WIDTH + PLAY_AREA_W - 50, VIRTUAL_H - HAND_BG_HEIGHT + 10, 40, 40)

        # Core gameplay counters
        self.score = 0
        self.visual_score = 0
        self.combo_counter = 0
        self.level_target = 0
        self.void_count = 0

        # Apply persisted audio/language preferences after subsystems exist
        self._apply_saved_settings()

    # YENİ FONKSİYON: Düşman mantığını buraya taşıyoruz
    def update_pyro_enemies(self):
        if self.round != 3: return

        # 1. Düşman Spawn
        self.pyro_spawn_timer += 1
        if self.pyro_spawn_timer >= PYRO_SPAWN_DELAY:
            self.pyro_spawn_timer = 0
            side = random.choice(['top', 'bottom', 'left', 'right'])
            if side == 'top': ex, ey = random.randint(0, VIRTUAL_W), -40
            elif side == 'bottom': ex, ey = random.randint(0, VIRTUAL_W), VIRTUAL_H + 40
            elif side == 'left': ex, ey = -40, random.randint(0, VIRTUAL_H)
            else: ex, ey = VIRTUAL_W + 40, random.randint(0, VIRTUAL_H)
            self.enemies.append({'x': float(ex), 'y': float(ey), 'rect': pygame.Rect(ex, ey, 30, 30)})

        # 2. Düşman Hareketi
        center_x, center_y = VIRTUAL_W // 2, VIRTUAL_H // 2
        for enemy in self.enemies[:]:
            dx = center_x - enemy['x']
            dy = center_y - enemy['y']
            dist = math.hypot(dx, dy)
            if dist != 0:
                enemy['x'] += (dx / dist) * PYRO_ENEMY_SPEED
                enemy['y'] += (dy / dist) * PYRO_ENEMY_SPEED
                enemy['rect'].center = (int(enemy['x']), int(enemy['y']))
            
            if dist < 40:
                # Collision => Pyro death screen
                self.enemies.clear()
                self.pyro_spawn_timer = 0
                self.pyro_flash_timer = 0
                self.shake_intensity = 0.0
                self.trigger_pyro_death()
                return

    def trigger_pyro_death(self):
        """Handle player death when Pyro enemies reach the core.
        Sets the game to the pyro-death state, clears enemies, and
        triggers audio/visual feedback.
        """
        try:
            # Clear enemy state
            self.enemies.clear()
        except Exception:
            pass
        try:
            self.tutorial_enemy = None
        except Exception:
            pass

        # Reset spawn timers and effects
        self.pyro_spawn_timer = 0
        self.pyro_flash_timer = 30
        self.shake_intensity = max(getattr(self, 'shake_intensity', 0.0), 12.0)

        # Select a dramatic quote if available
        try:
            import random as _rand
            if 'PHARAOH_QUOTES' in globals() and PHARAOH_QUOTES:
                self.current_death_quote = _rand.choice(PHARAOH_QUOTES)
            else:
                self.current_death_quote = self.get_text('PHARAOH_1') if hasattr(self, 'get_text') else "You died."
        except Exception:
            self.current_death_quote = "You died."

        # Play sound and particles where possible
        try:
            if hasattr(self, 'audio'):
                self.audio.play('explode')
        except Exception:
            pass
        try:
            if hasattr(self, 'particle_system'):
                self.particle_system.create_text(self.w//2, self.h//2, self.current_death_quote, (255, 80, 80), font_path=self.font_name)
        except Exception:
            pass

        # Enter pyro death state (UI will draw the death screen)
        self.state = STATE_PYRO_DEATH
        # Short cooldown to avoid immediate clicks
        self.input_cooldown = 30
        return

    def get_text(self, key):
        """Return localized text for current language, fallback to key."""
        lang_pack = LANGUAGES.get(self.current_language, LANGUAGES.get(DEFAULT_LANGUAGE, {}))
        return lang_pack.get("text", {}).get(key, key)

    def get_item_info(self, item_key):
        """
        Returns the localized name and description for an item.
        Usage: info = game.get_item_info('sniper') -> {'name': 'SNIPER', 'desc': '...'}
        """
        # Get current language pack
        lang_pack = LANGUAGES.get(self.current_language, LANGUAGES.get(DEFAULT_LANGUAGE, {}))
        items_dict = lang_pack.get("text", {}).get("ITEMS", {})
        
        # If key exists, return it
        if item_key in items_dict:
            return items_dict[item_key]
        
        # Fallback to English
        en_pack = LANGUAGES.get("EN", {})
        en_items = en_pack.get("text", {}).get("ITEMS", {})
        if item_key in en_items:
            return en_items[item_key]
        
        # Default fallback
        return {"name": item_key.upper(), "desc": "Unknown item"}

    def set_language(self, lang_code, play_sound=True):
        """Switch active language, update fonts, and optionally play select sound."""
        target = lang_code if lang_code in LANGUAGES else DEFAULT_LANGUAGE
        self.current_language = target
        meta = LANGUAGES.get(target, LANGUAGES.get(DEFAULT_LANGUAGE, {}))
        self.font_name = meta.get("font", pygame.font.get_default_font())
        self.font_size_offset = meta.get("size_offset", 0)
        if hasattr(self, 'ui'):
            self.ui.refresh_fonts()
        # Persist language choice immediately
        try:
            if hasattr(self, 'save_manager') and hasattr(self.save_manager, 'data'):
                if 'settings' not in self.save_manager.data or not isinstance(self.save_manager.data['settings'], dict):
                    self.save_manager.data['settings'] = {}
                self.save_manager.data['settings']['language'] = target
                self.save_manager.save_data()
        except Exception:
            pass
        if play_sound and hasattr(self.audio, 'play'):
            self.audio.play('select')

    def init_tutorial_mode(self):
        self.tutorial_step = 0
        self.input_cooldown = 20
        self.tutorial_key_pressed = False
        self.tutorial_rune_applied = False
        self.tutorial_active = True
        self.tutorial_enemy = None # Reset enemy

        # Reset Grid & Hand
        self.grid.reset()
        self.blocks = []
        self.held_block = None
        self.held_rune = None

        # Create Blocks
        tutorial_shapes = ['I', 'DOT', 'L']
        for shape in tutorial_shapes:
            self.blocks.append(Block(shape))
        self.position_blocks_in_hand()

        # --- CRITICAL FIX: SPAWN RUNE ---
        from runes import Rune
        self.consumables = [] # Clear old
        # Create a Rune manually
        r = Rune('rune_fire')
        # Set position explicitly
        r.x = SIDEBAR_WIDTH + 20
        r.y = 60
        r.dragging = False
        r.rect = pygame.Rect(r.x, r.y, 40, 40)
        self.consumables.append(r)

        # Game Params
        self.score = 0
        self.credits = 100
        self.void_count = 20

    def _spawn_tutorial_rune(self):
        """Spawn a single demo rune for tutorial steps."""
        from runes import Rune
        self.consumables.clear()
        self.consumables.append(Rune('rune_fire'))
        self.tutorial_rune_applied = False
        for r in self.consumables:
            r.x = SIDEBAR_WIDTH + 20
            r.y = 60
            r.rect = pygame.Rect(r.x, r.y, 40, 40)

    def get_blind_target(self, round_num):
        base_target = 300 * (self.ante ** 1.3)
        totem_penalty = 1.0 + (len(self.totems) * 0.15) 
        adjusted_target = int(base_target * totem_penalty)

        # Reduce difficulty by 20% in Pyro Mode (Ante 9+)
        if self.ante >= NEW_WORLD_ANTE:
            adjusted_target = int(adjusted_target * 0.8)

        if round_num == 1: return int(adjusted_target * 1.0)
        elif round_num == 2: return int(adjusted_target * 1.5)
        elif round_num == 3: return int(adjusted_target * 2.5)
        return 0

    def init_game_session_data(self):
        """Reset per-session data for a fresh run"""
        self.round = 1
        self.ante = 1
        self.score = 0
        self.visual_score = 0
        self.combo_counter = 0
        self.level_target = self.get_blind_target(self.round)
        self.void_count = BASE_VOID_COUNT
        self.shake_intensity = 0.0
        self.scoring_data = {'base': 0, 'mult': 0, 'total': 0}
        self.active_boss_effect = None
        self.boss_preview = random.choice(list(BOSS_DATA.keys())) if 'BOSS_DATA' in globals() else None
        self.blocks = []
        self.consumables = []
        self.totems = []
        self.shop_totems = []
        self.shop_runes = []
        self.held_block = None
        self.held_rune = None
        self.grid.reset()
        self.position_blocks_in_hand()

    def start_new_game(self):
        self.audio.play('select')
        self.init_game_session_data()
        self.state = STATE_ROUND_SELECT

    def start_round(self):
        # Universal Reset - Clean slate for every round
        self.state = STATE_PLAYING
        self.score = 0
        self.visual_score = 0
        self.combo_counter = 0
        self.enemies = []  # CRITICAL: Clear enemies every round
        self.pyro_spawn_timer = 0
        self.pyro_flash_timer = 0
        self.shake_intensity = 0.0
        self.scoring_data = {'base': 0, 'mult': 0, 'total': 0}
        self.grid.reset()
        self.blocks = []
        self.held_block = None
        self.current_boss = None
        
        # Difficulty Setup
        self.level_target = self.get_blind_target(self.round)
        round_bonus = 3 if self.round == 1 else 6
        self.void_count = BASE_VOID_COUNT + ((self.ante - 1) * 2) + round_bonus
        
        # Boss Check
        if self.round == 3:
            self.active_boss_effect = 'Pyro Boss'
        else:
            self.active_boss_effect = None
        
        self.refill_hand()

    def start_pyro_mode(self):
        self.tutorial_step = 0
        self.input_cooldown = 20
        self.tutorial_active = True
        self.tutorial_enemy = None

        # Reset Grid & Hand
        self.grid.reset()
        self.blocks = []
        self.held_block = None
        self.held_rune = None

        # Create Blocks
        tutorial_shapes = ['I', 'DOT', 'L']
        for shape in tutorial_shapes:
            self.blocks.append(Block(shape))
        self.position_blocks_in_hand()

        # --- CRITICAL FIX: SPAWN RUNE ---
        from runes import Rune
        self.consumables = []
        r = Rune('rune_fire')
        r.x = SIDEBAR_WIDTH + 20
        r.y = 60
        r.rect = pygame.Rect(r.x, r.y, 40, 40)
        self.consumables.append(r)

        # Game Params
        self.score = 0
        self.credits = 100
        self.void_count = 20

    def refill_hand(self):
        max_hand = 3
        if self.active_boss_effect == 'The Shrink': max_hand = 2
        # Top up hand to max_hand instead of blindly appending
        to_add = max(0, max_hand - len(self.blocks))
        to_add = min(to_add, self.void_count)
        for _ in range(to_add):
            shape = self.get_smart_block_key()
            self.blocks.append(Block(shape))
            self.void_count -= 1
        self.position_blocks_in_hand()
        
        if not self.blocks and self.void_count == 0:
            self.check_round_end()

    def get_smart_block_key(self):
        """Return a sensible block key. Falls back to random SHAPES key."""
        try:
            base_choices = ['I', 'DOT', 'L', 'T', 'S', 'Z', 'J', 'O']
            # Prefer defined shapes that exist in SHAPES
            valid = [k for k in base_choices if k in SHAPES]
            if valid:
                return random.choice(valid)
            return random.choice(list(SHAPES.keys()))
        except Exception:
            return random.choice(list(SHAPES.keys()))

    def check_round_end(self):
        if self.score >= self.level_target:
            self.audio.play('select')
            for t in self.totems:
                if t.trigger_type == 'on_round_end':
                    money, desc = TotemLogic.apply_round_end(t.key, self)
                    if money > 0:
                        self.credits += money
                        self.particle_system.create_text(self.w//2, self.h//2, desc, (100, 255, 100), font_path=self.font_name)
            
            # Check for Demo End (Ante 8 Boss completion)
            if self.ante == 8 and self.round == 3 and not self.endless_mode:
                self.state = STATE_DEMO_END
            else:
                self.state = STATE_LEVEL_COMPLETE
                self.generate_shop()
        else:
            self.audio.play('gameover')
            self.state = STATE_GAME_OVER
            self.crt.trigger_aberration(amount=3, duration=20)
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()

    def save_high_score(self):
        """Persist the current high score to save data."""
        try:
            prev = self.save_manager.data.get('high_score', 0)
            if self.high_score > prev:
                self.save_manager.data['high_score'] = self.high_score
                self.save_manager.save_data()
        except Exception as e:
            print(f"Warning: could not save high score: {e}")

    def next_level(self):
        # Calculate debt payment (based on round score)
        self.debt_payment_amount = self.score

        # Step 1-3: snapshot current debt (clamped) and set display start
        current_debt = self.save_manager.get_remaining_debt()
        self.debt_old_value = current_debt
        self.debt_displayed_value = current_debt

        # Step 4-5: apply payment and compute new debt
        self.save_manager.pay_debt(self.debt_payment_amount)
        new_debt = self.save_manager.get_remaining_debt()

        # Step 6: choose quotes based on freedom state and set active text
        self.debt_freedom = (new_debt == 0)
        # Define quote keys for localization
        freedom_keys = ["FREEDOM_1", "FREEDOM_2"]
        pharaoh_keys = ["PHARAOH_1", "PHARAOH_2"]
        # Select appropriate key based on debt state
        quote_keys = freedom_keys if self.debt_freedom else pharaoh_keys
        self.current_quote_key = random.choice(quote_keys)
        # Fetch localized text immediately
        self.current_quote_text = self.get_text(self.current_quote_key)

        # Step 7: initialize animation timers
        self.debt_animation_timer = 0
        self.debt_shake_intensity = 0
        self.debt_scale = 1.0
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
                    self.particle_system.create_text(self.w//2, self.h//2, f"WORLD SHIFT: {removed.name} DESTROYED!", (255, 50, 50), font_path=self.font_name)
                self.force_omega_shop = True
                
        self.state = STATE_ROUND_SELECT
    
    def continue_to_endless(self):
        """Called when player enters endless mode from demo end screen"""
        self.endless_mode = True
        self.ante += 1  # Now Ante 9, but will show as ∞
        self.round = 1
        self.audio.play('select')
        self.state = STATE_SHOP
        self.generate_shop()
    
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
        save_data['settings']['music_volume'] = self.temp_settings.get('music_volume', 0.5)
        save_data['settings']['language'] = self.temp_settings.get('language', self.current_language)
        
        # Apply resolution
        res_index = self.temp_settings['resolution_index']
        resolution = RESOLUTIONS[res_index]
        
        # Do NOT recreate display or change flags here; use safe toggle only
        # Apply fullscreen preference safely if it differs
        try:
            current_full = bool(self.screen.get_flags() & pygame.FULLSCREEN)
        except Exception:
            current_full = self.fullscreen
        desired_full = bool(self.temp_settings['fullscreen'])
        if desired_full != current_full:
            self.set_fullscreen(desired_full)
        
        # Apply SFX volume
        if hasattr(self.audio, 'set_volume'):
            self.audio.set_volume(self.temp_settings['volume'])

        # Apply music volume
        try:
            pygame.mixer.music.set_volume(self.temp_settings.get('music_volume', 0.5))
        except Exception:
            pass

        # Apply language immediately
        self.set_language(save_data['settings']['language'], play_sound=False)
        
        # Save to file
        self.save_manager.save_data(save_data)
        
        # Clean up temp settings
        delattr(self, 'temp_settings')
    
    def _apply_saved_settings(self):
        """Apply settings from save file on startup (volume only - screen already set)"""
        save_data = self.save_manager.get_data()
        settings = save_data.get('settings', {})
        
        # Apply SFX volume
        volume = settings.get('volume', 0.5)
        if hasattr(self.audio, 'set_volume'):
            self.audio.set_volume(volume)

        # Apply music volume
        music_volume = settings.get('music_volume', 0.5)
        try:
            pygame.mixer.music.set_volume(music_volume)
        except Exception:
            pass

        # Apply language (refresh fonts without playing sounds on startup)
        lang_code = settings.get('language', DEFAULT_LANGUAGE)
        self.set_language(lang_code, play_sound=False)

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
                # Always snap visual position for non-dragging blocks to avoid stray visuals
                if not getattr(b, 'dragging', False):
                    b.visual_x = target_x
                    b.visual_y = target_y

    def rotate_held_block(self):
        """Rotate the currently held block (90 degrees clockwise)"""
        if self.held_block:
            self.held_block.rotate()
            self.audio.play('select')

    def flip_held_block(self):
        """Flip the currently held block horizontally"""
        if self.held_block:
            # Flip the block matrix horizontally
            self.held_block.matrix = [row[::-1] for row in self.held_block.matrix]
            self.held_block.update_dimensions()
            self.held_block.rect.width = self.held_block.width
            self.held_block.rect.height = self.held_block.height
            self.audio.play('select')

    def get_grid_pos(self, mx, my):
        rx, ry = mx - GRID_OFFSET_X, my - GRID_OFFSET_Y
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
                    self.particle_system.create_text(self.w//2, 100, "+$2 Cashback", (100, 255, 100), font_path=self.font_name)
            if t in self.shop_totems: self.shop_totems.remove(t)
            self.audio.play('clear')

    def buy_rune(self, r):
        if self.credits >= r.price and len(self.consumables) < self.max_consumables:
            self.credits -= r.price
            self.consumables.append(r)
            if r in self.shop_runes: self.shop_runes.remove(r)
            self.audio.play('select')

    def get_current_theme(self):
        """Return active theme definition"""
        # Force Terminal theme in Pyro Mode (Ante 9+)
        if self.ante >= NEW_WORLD_ANTE:
            return THEMES['TERMINAL']
        
        key = getattr(self, 'theme', 'NEON')
        if key in THEMES:
            return THEMES[key]
        # Fallback to first theme
        return list(THEMES.values())[0]

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

    def set_fullscreen(self, enabled: bool):
        """Safely set fullscreen on/off using toggle, without recreating display.
        - Does not call set_mode; avoids breaking the SCALED context on macOS Retina.
        """
        try:
            current = bool(self.screen.get_flags() & pygame.FULLSCREEN)
        except Exception:
            current = self.fullscreen

        if enabled != current:
            # Use the safe SDL toggle path; do not change flags via set_mode
            pygame.display.toggle_fullscreen()
            self.fullscreen = enabled
            # Persist preference
            self.save_manager.data['settings']['fullscreen'] = self.fullscreen
            self.save_manager.save_data()

    def handle_events(self):
        # Note: Do not discard events during cooldown; gate actions instead
        
        # NOTE: Use event.pos for mouse coordinates (Retina accuracy).
        # Do NOT call pygame.event.get() more than once per frame.
        
        for event in pygame.event.get():
            # Default mouse position (fallback). Prefer `event.pos` when present.
            mx, my = pygame.mouse.get_pos()
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

            if self.state == STATE_INTRO:
                # Allow skipping intro with any key press or mouse click
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    if self.input_cooldown == 0:
                        self.input_cooldown = 20  # Prevent ghost clicks after skip
                        pygame.mixer.music.stop()  # Stop intro audio
                        self.intro_manager.active = False
                        self.intro_manager.close()
                        self.state = STATE_MENU
                        # Start background music
                        pygame.mixer.music.load(resource_path("assets/music.mp3"))
                        pygame.mixer.music.play(-1)
                        self.audio.play('select')

            if self.state == STATE_MENU:
                # Handle reset confirmation first (if active)
                if self.show_reset_confirm:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mx, my = event.pos
                        if hasattr(self.ui, 'reset_confirm_buttons'):
                            yes_btn = self.ui.reset_confirm_buttons['YES']
                            no_btn = self.ui.reset_confirm_buttons['NO']
                            if yes_btn.collidepoint(mx, my) and self.input_cooldown == 0:
                                # Confirm reset
                                self.save_manager.reset_progress()
                                # Reload save data and update UI
                                self.save_manager.data = self.save_manager._load_or_create()
                                self.high_score = self.save_manager.data.get('high_score', 0)
                                self.show_reset_confirm = False
                                self.input_cooldown = 15
                                self.audio.play('break')
                            elif no_btn.collidepoint(mx, my) and self.input_cooldown == 0:
                                # Cancel reset
                                self.show_reset_confirm = False
                                self.input_cooldown = 10
                                self.audio.play('select')
                else:
                    # Normal menu handling
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        # Check reset button first
                        if hasattr(self.ui, 'reset_btn_rect'):
                            if self.ui.reset_btn_rect.collidepoint(mx, my) and self.input_cooldown == 0:
                                self.show_reset_confirm = True
                                self.input_cooldown = 10
                                self.audio.play('select')
                        
                        # Check coming soon button
                        if hasattr(self.ui, 'coming_soon_btn_rect'):
                            if self.ui.coming_soon_btn_rect.collidepoint(mx, my) and self.input_cooldown == 0:
                                self.audio.play('select')
                                self.state = STATE_COMING_SOON
                                self.input_cooldown = 10
                        
                        # Then check menu buttons
                        if hasattr(self.ui, 'menu_buttons'):
                            for rect, text in self.ui.menu_buttons:
                                if rect.collidepoint(mx, my) and self.input_cooldown == 0:
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
                    mx, my = event.pos
                    if hasattr(self.ui, 'select_buttons'):
                        for btn in self.ui.select_buttons:
                            if btn.collidepoint(mx, my) and self.input_cooldown == 0:
                                self.start_round()

            elif self.state == STATE_PAUSE:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    if hasattr(self.ui, 'pause_buttons'):
                        yes = self.ui.pause_buttons['YES']
                        no = self.ui.pause_buttons['NO']
                        if yes.collidepoint(mx, my) and self.input_cooldown == 0:
                            self.state = STATE_MENU
                            self.init_game_session_data()
                            self.input_cooldown = 15  # Prevent ghost click on PLAY button
                        elif no.collidepoint(mx, my) and self.input_cooldown == 0:
                            self.state = STATE_PLAYING
            
            elif self.state == STATE_COMING_SOON:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    if hasattr(self.ui, 'coming_soon_back_btn'):
                        if self.ui.coming_soon_back_btn.collidepoint(mx, my) and self.input_cooldown == 0:
                            self.audio.play('select')
                            self.state = STATE_MENU
                            self.input_cooldown = 10
            
            elif self.state == STATE_TRAINING:
                # --- Generic input handling first to avoid softlocks ---
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_r, pygame.K_e):
                        if self.tutorial_step == 1:
                            self.tutorial_key_pressed = True
                            self.tutorial_step = 2
                            try: self.audio.play('select')
                            except Exception: pass
                        if self.held_block:
                            if event.key == pygame.K_r:
                                self.rotate_held_block()
                            elif event.key == pygame.K_e:
                                self.flip_held_block()

                # 1. Right Click (Defense Step ONLY)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    mx, my = event.pos
                    if self.tutorial_step == 6 and getattr(self, 'tutorial_enemy', None):
                        if self.tutorial_enemy['rect'].collidepoint(mx, my):
                            try: self.audio.play('explode')
                            except Exception: pass
                            try: self.particle_system.create_explosion(mx, my, count=20)
                            except Exception: pass
                            self.tutorial_enemy = None
                            self.tutorial_step = 7
                            self.input_cooldown = 20

                # 2. Left Click (Progression and Dragging)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    # Preserve tutorial cooldown gating to avoid ghost clicks
                    if self.input_cooldown > 0:
                        continue
                    item_clicked = False
                    # Check Runes
                    for r in self.consumables:
                        if getattr(r, 'rect', None) and r.rect.collidepoint(mx, my):
                            self.held_rune = r
                            self.held_rune.dragging = True
                            item_clicked = True
                            try: self.audio.play('select')
                            except Exception: pass
                            break
                    # Check Blocks
                    if not item_clicked:
                        for b in self.blocks:
                            if b.rect.collidepoint(mx, my):
                                self.held_block = b; self.held_block.dragging = True
                                # Use visual offsets for consistency with drawing
                                self.held_block.offset_x = mx - b.visual_x; self.held_block.offset_y = my - b.visual_y
                                self.audio.play('select')
                                item_clicked = True; break

                    # -- STEP PROGRESSION (Only if NOT dragging an item) --
                    if not item_clicked:
                        # Steps 0-4: click anywhere to advance
                        if self.tutorial_step in [0, 1, 2, 3, 4]:
                            self.tutorial_step += 1
                            self.input_cooldown = 20
                            try: self.audio.play('select')
                            except Exception: pass
                        # Step 5: Do NOT advance on click (handled on MOUSEBUTTONUP)
                        # Step 6: Do NOT advance on Left Click (handled by Right Click)
                        # Step 7: Click to Finish and return to menu
                        elif self.tutorial_step == 7:
                            try:
                                self.save_manager.data['tutorial_complete'] = True
                                self.save_manager.save_data()
                            except Exception:
                                pass
                            try: self.audio.play('select')
                            except Exception: pass
                            self.state = STATE_MENU
                            self.tutorial_active = False
                            # Long cooldown to avoid ghost-clicking UI buttons right after tutorial
                            self.input_cooldown = 60

                # 3. Mouse Release (Drop Logic)
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    mx, my = event.pos
                    if self.held_rune and self.held_rune.dragging:
                        applied = False
                        for b in self.blocks:
                            if b.rect.collidepoint(mx, my):
                                rel_x = mx - b.visual_x
                                rel_y = my - b.visual_y
                                cell_col = int(rel_x // TILE_SIZE)
                                cell_row = int(rel_y // TILE_SIZE)
                                if 0 <= cell_row < b.rows and 0 <= cell_col < b.cols:
                                    if b.matrix[cell_row][cell_col] == 1:
                                        b.runes[(cell_row, cell_col)] = self.held_rune
                                        if self.held_rune in self.consumables:
                                            self.consumables.remove(self.held_rune)
                                        applied = True
                                        try: self.audio.play('select')
                                        except Exception: pass
                                        break
                        if applied and self.tutorial_step == 5:
                            self.tutorial_rune_applied = True
                            self.tutorial_step = 6
                            self.input_cooldown = 20
                        self.held_rune = None

                    if self.held_block:
                        # Handle trash discard or place logic
                        if self.tutorial_step == 2 and self.trash_rect.collidepoint(mx, my):
                            self.held_block.dragging = False
                            self.held_block = None
                            self.blocks.clear()
                            tutorial_shapes = ['I', 'DOT', 'L']
                            while len(self.blocks) < 3:
                                try:
                                    new_shape = self.get_smart_block_key()
                                except Exception:
                                    new_shape = random.choice(tutorial_shapes)
                                self.blocks.append(Block(new_shape))
                            self.position_blocks_in_hand()
                            try: self.audio.play('select')
                            except Exception: pass
                            self.tutorial_step = 3
                            return
                        else:
                            cur_x = mx - self.held_block.offset_x
                            cur_y = my - self.held_block.offset_y
                            check_x = cur_x + (TILE_SIZE / 2)
                            check_y = cur_y + (TILE_SIZE / 2)
                            gr, gc = self.get_grid_pos(check_x, check_y)
                            if gr is not None and gc is not None and self.grid.is_valid_position(self.held_block, gr, gc):
                                self.grid.place_block(self.held_block, gr, gc)
                                # Placement bump disabled: constant small shakes are tiring
                                # try:
                                #     self.grid.trigger_bump(0.05)
                                # except Exception:
                                #     pass
                                if self.held_block in self.blocks:
                                    self.blocks.remove(self.held_block)
                                try: self.audio.play('place')
                                except Exception: pass
                                self.held_block = None
                            else:
                                self.held_block.dragging = False
                                self.position_blocks_in_hand()
                                self.held_block = None

            elif self.state == STATE_PLAYING:
            
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: self.state = STATE_PAUSE
                    if event.key == pygame.K_r and self.held_block:
                        self.rotate_held_block()
                    if event.key == pygame.K_e and self.held_block:
                        self.flip_held_block()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    if hasattr(self, 'menu_btn_rect') and self.menu_btn_rect.collidepoint(mx, my) and self.input_cooldown == 0:
                        self.state = STATE_PAUSE
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
                    mx, my = event.pos

                    if event.button == 3 and (self.round == 3 or self.ante >= NEW_WORLD_ANTE):
                        hit = False
                        for enemy in self.enemies[:]:
                            if enemy['rect'].collidepoint(mx, my):
                                self.enemies.remove(enemy)
                                hit = True
                                self.audio.play('explode')
                                self.particle_system.create_explosion(mx, my, count=10)
                                self.particle_system.create_text(mx, my, "HIT!", (255, 50, 50), font_path=self.font_name)

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
                                        self.particle_system.create_text(mx, my, self.get_text('RUNE_APPLIED'), self.held_rune.color, font_path=self.font_name)
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
                                    self.particle_system.create_text(mx, my, self.get_text('REROLL'), (200, 200, 200), font_path=self.font_name)
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
                            target_px = GRID_OFFSET_X + gc * TILE_SIZE
                            target_py = GRID_OFFSET_Y + gr * TILE_SIZE
                            orig_pos = self.held_block.rect.topleft
                            self.held_block.rect.topleft = (target_px, target_py)
                            
                            if self.grid.is_valid_position(self.held_block, gr, gc):
                                for t in self.totems:
                                    if t.key == 'gamblers_dice':
                                        triggered, bonus = TotemLogic.check_gambling(t.key, self)
                                        if triggered:
                                            self.particle_system.create_text(mx, my, f"{self.get_text('GAMBLE_WIN')} x5", (255, 215, 0), font_path=self.font_name)
                                            self.score += int(bonus)
                                            self.combo_counter += 1
                                            self.audio.play('clear')
                                            self.blocks.remove(self.held_block)
                                            self.held_block = None
                                            self.state = STATE_SCORING
                                            self.scoring_data = {'base': 100, 'mult': 5.0, 'total': int(bonus)}
                                            return 

                                self.grid.place_block(self.held_block, gr, gc)
                                # Placement bump disabled: constant small shakes are tiring
                                # try:
                                #     self.grid.trigger_bump(0.05)
                                # except Exception:
                                #     pass
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

                                # --- PERFECT CLEAR CHECK ---
                                is_empty = True
                                for rr in range(GRID_SIZE):
                                    for cc_i in range(GRID_SIZE):
                                        if self.grid.grid[rr][cc_i] is not None:
                                            is_empty = False
                                            break
                                    if not is_empty:
                                        break
                                if is_empty:
                                    try:
                                        self.particle_system.trigger_board_clear(GRID_OFFSET_X, GRID_OFFSET_Y, TILE_SIZE)
                                    except Exception:
                                        pass
                                    try:
                                        self.particle_system.create_text(self.w//2, self.h//2, "PERFECT!", (255, 215, 0), font_path=self.font_name)
                                    except Exception:
                                        pass
                                    # Large shake + cap
                                    self.shake_intensity = min(50.0, getattr(self, 'shake_intensity', 0.0) + 30.0)
                                    try:
                                        self.audio.play('clear')
                                    except Exception:
                                        pass
                                    try:
                                        self.score += 5000
                                    except Exception:
                                        pass
                                
                                # Trigger Pharaoh speech on big plays
                                if total_clears >= 2:
                                    lang = getattr(self, 'current_language', 'EN')
                                    speech_list = PHARAOH_SPEECH['COMBO'].get(lang, PHARAOH_SPEECH['COMBO']['EN'])
                                    if speech_list:
                                        self.ui.pharaoh.say(random.choice(speech_list))
                                
                                if total_clears > 0:
                                    self.grid.trigger_beat()
                                    try:
                                        self.grid.trigger_bump(0.2)
                                    except Exception:
                                        pass
                                    self.crt.trigger_aberration(amount=2, duration=5)

                                    base_points += total_clears * SCORE_PER_LINE
                                    if col_bonus > 0:
                                        base_points += col_bonus
                                        self.particle_system.create_text(mx, my - 50, f"{self.get_text('COLOR_MATCH')} +{col_bonus}", (255, 215, 0), font_path=self.font_name)
                                    
                                    # Rün Bonusları
                                    base_points += rune_bonuses['chips']
                                    if rune_bonuses['chips'] > 0:
                                        self.particle_system.create_text(mx, my-70, f"{self.get_text('RUNE_CHIPS')} +{rune_bonuses['chips']}", (100, 200, 255), font_path=self.font_name)

                                    self.credits += total_clears
                                    self.credits += rune_bonuses['money']
                                    
                                    self.combo_counter += 1
                                    # small shake for clears
                                    self.shake_intensity = min(50.0, getattr(self, 'shake_intensity', 0.0) + (2 * total_clears))
                                    self.particle_system.atmosphere.trigger_shake(10, 3) 
                                    self.audio.play('clear')
                                    
                                    theme = self.get_current_theme()
                                    for r in cr:
                                        py = GRID_OFFSET_Y + r*TILE_SIZE + TILE_SIZE//2
                                        for c in range(GRID_SIZE): self.particle_system.create_explosion(GRID_OFFSET_X + c*TILE_SIZE, py, count=5)
                                    for c in cc:
                                        px = GRID_OFFSET_X + c*TILE_SIZE + TILE_SIZE//2
                                        for r in range(GRID_SIZE): self.particle_system.create_explosion(px, GRID_OFFSET_Y + r*TILE_SIZE, count=5)
                                    
                                    extra_cash = 0
                                    for t in self.totems:
                                        if t.trigger_type == 'on_clear':
                                            gain = TotemLogic.apply_on_clear(t.key, self, cleared_cells_count, stones_destroyed)
                                            extra_cash += gain
                                    if extra_cash > 0:
                                        self.credits += int(extra_cash)
                                        self.particle_system.create_text(self.w-100, 100, f"+${extra_cash}", (100, 255, 100), font_path=self.font_name)
                                    
                                    # Mult Hesapla (Rünler Dahil)
                                    mult = self.calculate_totem_mult()
                                    mult += rune_bonuses['mult_add']
                                    mult *= rune_bonuses['mult_x']

                                    hype_list = LANGUAGES.get(self.current_language, {}).get("HYPE_WORDS", ["WOW"])
                                    hype_word = random.choice(hype_list)
                                    self.particle_system.create_text(self.w//2, self.h//2 - 50, hype_word, (255, 215, 0), font_path=self.font_name)
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
                                            self.particle_system.create_text(target_px, target_py, f"+50 {self.get_text('ARCH_BONUS')}", (100, 100, 255), font_path=self.font_name)
                                    self.score += base_points + arch_bonus
                                    self.combo_counter = 0
                                    self.scoring_data = {'base': 0, 'mult': 0, 'total': 0}
                                
                                self.blocks.remove(self.held_block)
                                if self.state != STATE_SCORING: self.refill_hand()
                            else:
                                self.audio.play('hit')
                                self.held_block.rect.topleft = self.held_block.original_pos
                                
                        self.held_block.dragging = False
                        self.held_block = None

                elif event.type == pygame.MOUSEMOTION:
                    pass

            elif self.state == STATE_SHOP:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    if self.input_cooldown > 0:
                        continue
                    for t in self.shop_totems:
                        if t.rect.collidepoint(mx, my): self.buy_totem(t)
                    # Rün Satın Alma
                    for r in self.shop_runes:
                        if r.rect and r.rect.collidepoint(mx, my): self.buy_rune(r)
                        
                    if mx > self.w - 150 and my > self.h - 50: self.next_level()
            
            elif self.state == STATE_DEBT:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    # Check if continue button was clicked (handled by UI)
                    if hasattr(self.ui, 'debt_continue_button'):
                        if self.ui.debt_continue_button.collidepoint(mx, my) and self.input_cooldown == 0:
                            self.audio.play('select')
                            self.continue_from_debt()
                            self.state = STATE_ROUND_SELECT
                            self.input_cooldown = 15  # Prevent ghost click on round select
            
            elif self.state == STATE_DEMO_END:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    # Check if endless mode button was clicked
                    if hasattr(self.ui, 'demo_end_button'):
                        if self.ui.demo_end_button.collidepoint(mx, my) and self.input_cooldown == 0:
                            self.audio.play('select')
                            self.continue_to_endless()
                            self.input_cooldown = 15
            
            elif self.state == STATE_COLLECTION:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    # Check if back button was clicked
                    if hasattr(self.ui, 'collection_back_button'):
                        if self.ui.collection_back_button.collidepoint(mx, my) and self.input_cooldown == 0:
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
                    mx, my = event.pos
                    if self.input_cooldown > 0:
                        continue
                    btns = self.ui.settings_buttons
                    
                    # Fullscreen toggle
                    if 'fullscreen' in btns and btns['fullscreen'].collidepoint(mx, my):
                        new_value = not self.temp_settings['fullscreen']
                        # Apply safely immediately; do not recreate display or change flags directly
                        self.set_fullscreen(new_value)
                        self.temp_settings['fullscreen'] = new_value
                        self.audio.play('select')

                    # Language cycle
                    elif 'language' in btns and btns['language'].collidepoint(mx, my):
                        current = self.temp_settings.get('language', self.current_language)
                        try:
                            idx = AVAILABLE_LANGUAGES.index(current)
                        except ValueError:
                            idx = 0
                        next_lang = AVAILABLE_LANGUAGES[(idx + 1) % len(AVAILABLE_LANGUAGES)]
                        self.temp_settings['language'] = next_lang
                        self.set_language(next_lang)
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
                        # SFX Volume slider
                        slider = self.ui.settings_buttons.get('volume_slider')
                        if slider and slider.collidepoint(mx, my):
                            # Calculate volume from mouse position
                            relative_x = mx - slider.x
                            volume = max(0.0, min(1.0, relative_x / slider.width))
                            self.temp_settings['volume'] = volume
                        
                        # Music Volume slider
                        music_slider = self.ui.settings_buttons.get('music_slider')
                        if music_slider and music_slider.collidepoint(mx, my):
                            # Calculate music volume from mouse position
                            relative_x = mx - music_slider.x
                            music_volume = max(0.0, min(1.0, relative_x / music_slider.width))
                            self.temp_settings['music_volume'] = music_volume

            elif self.state == STATE_PYRO_DEATH:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if TRY AGAIN button was clicked
                    if hasattr(self.ui, 'pyro_death_button'):
                        if self.ui.pyro_death_button.collidepoint(mx, my) and self.input_cooldown == 0:
                            self.audio.play('select')
                            # Trigger clean round reset (includes enemy clear)
                            self.start_round()
                            self.input_cooldown = 15

            elif self.state == STATE_GAME_OVER:
                if event.type == pygame.MOUSEBUTTONDOWN: self.state = STATE_MENU; self.init_game_session_data()

    def update(self):
        # Decrease input cooldown
        if self.input_cooldown > 0:
            self.input_cooldown -= 1
        
        self.ui.update()
        self.particle_system.update()
        # Update pyro atmosphere if present
        if getattr(self, 'pyro_bg', None):
            try:
                self.pyro_bg.update()
            except Exception:
                pass
        # Decaying vector shake
        if getattr(self, 'shake_intensity', 0.0) > 0:
            self.shake_intensity *= 0.9
            if self.shake_intensity < 0.5:
                self.shake_intensity = 0.0
        
        self.grid.update()
        
        diff = self.score - self.visual_score
        if diff > 0: self.visual_score += max(1, diff // 5)
        
        TOTAL_TUTORIAL_STEPS = 7

        if self.state == STATE_INTRO:
            playing = self.intro_manager.update()

            if not playing:
                self.intro_manager.close()
                self.state = STATE_MENU
                pygame.mixer.music.load(resource_path("assets/music.mp3"))
                pygame.mixer.music.play(-1)

            return

        elif self.state == STATE_TRAINING:
            # Tutorial mode - update blocks and runes for animation
            for b in self.blocks: 
                b.update()
            
            # Update rune dragging
            if self.held_rune and self.held_rune.dragging:
                mx, my = pygame.mouse.get_pos()
                self.held_rune.x = mx
                self.held_rune.y = my
            
            # Fix for tutorial_step 2 (discard teaching): Prevent softlock when hand is empty
            if self.tutorial_step == 2 and len(self.blocks) == 0:
                # Create 3 new blocks to allow player to practice discarding
                for _ in range(3):
                    try:
                        new_shape = self.get_smart_block_key()
                    except Exception:
                        new_shape = random.choice(['I', 'DOT', 'L'])
                    self.blocks.append(Block(new_shape))
                self.position_blocks_in_hand()
            
            # Step 5 progression: Advance when rune is applied
            if self.tutorial_step == 5 and self.tutorial_rune_applied:
                self.tutorial_step = 6
                self.tutorial_rune_applied = False
                self.audio.play('select')

            # Step 6: Defense tutorial enemy logic
            if self.tutorial_step == 6:
                # Ensure a tutorial rune exists in the sidebar for practice
                if not getattr(self, 'consumables', None) or len(self.consumables) == 0:
                    try:
                        self._spawn_tutorial_rune()
                    except Exception:
                        pass
                center_x, center_y = VIRTUAL_W // 2, VIRTUAL_H // 2
                # Spawn enemy if missing
                if self.tutorial_enemy is None:
                    sx, sy = 100.0, 100.0
                    self.tutorial_enemy = {'x': sx, 'y': sy, 'rect': pygame.Rect(int(sx), int(sy), 30, 30)}
                else:
                    ex = self.tutorial_enemy['x']
                    ey = self.tutorial_enemy['y']
                    dx = center_x - ex
                    dy = center_y - ey
                    dist = math.hypot(dx, dy)
                    if dist != 0:
                        # Move towards center using pyro enemy speed
                        self.tutorial_enemy['x'] += (dx / dist) * PYRO_ENEMY_SPEED
                        self.tutorial_enemy['y'] += (dy / dist) * PYRO_ENEMY_SPEED
                        self.tutorial_enemy['rect'].center = (int(self.tutorial_enemy['x']), int(self.tutorial_enemy['y']))

                    # If it reaches the core, play hit feedback and reset to start
                    if dist < 40:
                        try:
                            if hasattr(self.audio, 'play'):
                                self.audio.play('hit')
                        except Exception:
                            pass
                        # Small screen shake and reset position to loop until shot
                        try:
                            self.particle_system.atmosphere.trigger_shake(15, 6)
                        except Exception:
                            self.shake_intensity = min(50.0, getattr(self, 'shake_intensity', 0.0) + 6.0)
                        # Reset position
                        self.tutorial_enemy['x'] = 100.0
                        self.tutorial_enemy['y'] = 100.0
                        self.tutorial_enemy['rect'].center = (100, 100)

            # Clamp and deactivate overlay when finished, then start a real run
            if self.tutorial_step >= TOTAL_TUTORIAL_STEPS:
                self.tutorial_step = TOTAL_TUTORIAL_STEPS
                self.tutorial_active = False
                # Save tutorial completion and begin a normal game run (Ante 1)
                try:
                    self.save_manager.data['tutorial_complete'] = True
                    self.save_manager.save_data()
                except Exception:
                    pass
                # Optional start sound
                if hasattr(self.audio, 'play'):
                    self.audio.play('clear')
                # Start a new game flow (round select)
                self.start_new_game()
        
        elif self.state == STATE_PLAYING:
            for b in self.blocks: b.update()
            # Update Pyro enemies (round 3 or Ante 9+ overlay mode)
            self.update_pyro_enemies()
            # Rune dragging - use direct mouse coordinates (no conversion needed)
            if self.held_rune and self.held_rune.dragging:
                mx, my = pygame.mouse.get_pos()
                self.held_rune.x = mx
                self.held_rune.y = my
        
        elif self.state == STATE_DEBT:
            # Debt screen animation logic
            self.debt_animation_timer += 1

            # Countdown animation (fast) towards actual remaining debt (already clamped)
            target_value = self.save_manager.get_remaining_debt()
            if self.debt_displayed_value > target_value:
                decrement = max(1, self.debt_payment_amount // 60)  # Complete in ~60 frames
                self.debt_displayed_value = max(target_value, self.debt_displayed_value - decrement)
                
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
                # Check length of the ACTUAL text being displayed
                if self.debt_quote_char_index < len(self.current_quote_text):
                    self.debt_quote_char_index += 1
            
        elif self.state == STATE_SCORING:
            self.scoring_timer += 1
            if self.scoring_timer > 60:
                self.score += self.scoring_data['total']
                self.state = STATE_PLAYING
                self.refill_hand()
                if self.score >= self.level_target and not self.blocks and self.void_count == 0: self.check_round_end()

    def draw(self):
        # 1. Intro Check (Stop everything else)
        if self.state == STATE_INTRO:
            if self.intro_manager:
                self.intro_manager.draw()
            pygame.display.flip()
            return

        # 2. Global Background (Applied to all states)
        self.ui.draw_bg(self.screen)

        # 3. STATE MACHINE (Strict Separation)

        # --- MENU STATE ---
        if self.state == STATE_MENU:
            self.ui.draw_menu(self.screen, self.high_score)
            if self.show_reset_confirm:
                self.ui.draw_reset_confirm_overlay(self.screen)
        # --- COMING SOON ---
        elif self.state == STATE_COMING_SOON:
            self.ui.draw_coming_soon(self.screen)
        # --- SETTINGS ---
        elif self.state == STATE_SETTINGS:
            self.ui.draw_settings(self.screen, self)
        # --- COLLECTION ---
        elif self.state == STATE_COLLECTION:
            self.ui.draw_collection(self.screen, self)
        # --- TRAINING STATE (Tutorial) ---
        elif self.state == STATE_TRAINING:
            # A. Grid (Bottom)
            theme = self.get_current_theme()
            self.grid.draw(self.screen, theme)
            # B. Tutorial Enemy (Under UI)
            if getattr(self, 'tutorial_step', 0) == 6:
                s = pygame.Surface((VIRTUAL_W, VIRTUAL_H), pygame.SRCALPHA)
                s.fill((255, 0, 0, 50))
                self.screen.blit(s, (0,0))
                if getattr(self, 'tutorial_enemy', None):
                    ex, ey = self.tutorial_enemy['rect'].center
                    pygame.draw.circle(self.screen, (0,0,0,100), (ex+4, ey+4), 18)
                    pygame.draw.circle(self.screen, (160,0,0), (ex, ey), 16)
                    pygame.draw.circle(self.screen, (255,255,255), (ex, ey), 10)
                    pygame.draw.circle(self.screen, (0,0,0), (ex, ey), 4)
            # C. UI Layers (Sidebar covers enemy)
            self.ui.draw_sidebar(self.screen, self)
            self.ui.draw_hand_bg(self.screen)
            self.ui.draw_top_bar(self.screen, self)
            self.ui.draw_hud_elements(self.screen, self)
            # D. Hand Items & Particles
            self._draw_hand_items(theme)
            self.particle_system.draw(self.screen)
            # E. Tutorial Text (Top)
            if getattr(self, 'tutorial_active', True):
                self.ui.draw_training_overlay(self.screen, self, self.tutorial_step)
            # F. Dragged Items
            # F. Dragged Items (draw order unified at end)
            # NOTE: actual drawing of dragged items (held_block / held_rune)
            # is handled after the state switch to ensure they render on top.
        # --- PLAYING / SCORING / PYRO ---
        elif self.state in [STATE_PLAYING, STATE_SCORING, STATE_PYRO, STATE_PYRO_DEATH, STATE_LEVEL_COMPLETE, STATE_GAME_OVER]:
            # Standard Game Loop Drawing
            self._draw_gameplay_elements()
        # --- OTHER STATES ---
        elif self.state == STATE_ROUND_SELECT:
            self.ui.draw_round_select(self.screen, self)
        elif self.state == STATE_DEBT:
            self.ui.draw_debt_screen(self.screen, self)
        elif self.state == STATE_DEMO_END:
            self.ui.draw_demo_end(self.screen, self)
        elif self.state == STATE_PAUSE:
            # Draw game under pause
            self._draw_gameplay_elements()
            self.ui.draw_pause_overlay(self.screen)
        elif self.state == STATE_SHOP:
            self.ui.draw_shop(self.screen, self)

        # Global Overlays (CRT, Pharaoh, Cursor)
        self.crt.draw(self.screen)
        if self.state in [STATE_PLAYING, STATE_SCORING, STATE_TRAINING]:
            self.ui.draw_overlay_elements(self.screen)

        # --- Draw dragged items on top of everything ---
        try:
            mx, my = pygame.mouse.get_pos()
            theme = None
            try:
                theme = self.get_current_theme()
            except Exception:
                theme = None

            # Held block dragging (draw above all layers)
            if hasattr(self, 'held_block') and self.held_block and getattr(self.held_block, 'dragging', False):
                hb = self.held_block
                ox = getattr(hb, 'offset_x', 0)
                oy = getattr(hb, 'offset_y', 0)
                cur_x = mx - ox
                cur_y = my - oy
                try:
                    hb.draw(self.screen, cur_x, cur_y, 1.0, 255, theme['style'] if theme else 'default')
                except Exception:
                    try:
                        hb.draw(self.screen, cur_x, cur_y, 1.0, 255, 'default')
                    except Exception:
                        pass

            # Held rune dragging (draw above all layers)
            if hasattr(self, 'held_rune') and self.held_rune and getattr(self.held_rune, 'dragging', False):
                rx, ry = mx, my
                try:
                    pygame.draw.circle(self.screen, (20, 20, 30), (rx, ry), 24)
                    pygame.draw.circle(self.screen, self.held_rune.color, (rx, ry), 22, 3)
                    font = pygame.font.SysFont("Arial", 22, bold=True)
                    txt = font.render(self.held_rune.icon, True, self.held_rune.color)
                    self.screen.blit(txt, txt.get_rect(center=(rx, ry)))
                except Exception:
                    pass

        except Exception:
            pass

        # Apply decaying vector shake by shifting the final framebuffer if needed
        try:
            if getattr(self, 'shake_intensity', 0.0) > 0 and self.state in [STATE_PLAYING, STATE_TRAINING, STATE_SCORING, STATE_PYRO, STATE_PYRO_DEATH]:
                sx = random.uniform(-self.shake_intensity, self.shake_intensity)
                sy = random.uniform(-self.shake_intensity, self.shake_intensity)
                buf = self.screen.copy()
                # Clear screen to avoid ghosting; UI background will be mostly filled by blit
                self.screen.fill((0,0,0))
                self.screen.blit(buf, (int(sx), int(sy)))
        except Exception:
            pass

        pygame.display.flip()

    # Helper to prevent duplication
    def _draw_hand_items(self, theme):
        start_x = SIDEBAR_WIDTH + 20
        start_y = 60
        for i, r in enumerate(self.consumables):
            if not r.dragging:
                r.x = start_x + i * 50
                r.y = start_y
                r.rect = pygame.Rect(r.x, r.y, 40, 40)
                pygame.draw.circle(self.screen, (20, 20, 30), (r.x+20, r.y+20), 20)
                pygame.draw.circle(self.screen, r.color, (r.x+20, r.y+20), 18)
                font = pygame.font.SysFont("Arial", 20, bold=True)
                txt = font.render(r.icon, True, (255,255,255))
                self.screen.blit(txt, txt.get_rect(center=(r.x+20, r.y+20)))
        for b in self.blocks:
            if b != self.held_block:
                b.draw(self.screen, 0, 0, 0.8, 255, theme['style'])

    def _draw_dragged_items(self, theme):
        if self.held_block and self.held_block.dragging:
            try:
                mx, my = pygame.mouse.get_pos()
            except Exception:
                mx, my = 0, 0
            cur_x = mx - getattr(self.held_block, 'offset_x', 0)
            cur_y = my - getattr(self.held_block, 'offset_y', 0)
            try:
                self.held_block.draw(self.screen, cur_x, cur_y, 1.0, 255, theme['style'])
            except Exception:
                try:
                    self.held_block.draw(self.screen, cur_x, cur_y, 1.0, 255, 'default')
                except Exception:
                    pass

    def _draw_gameplay_elements(self):
        theme = self.get_current_theme()
        # Tick shake on pyro atmosphere (compat)
        try:
            if getattr(self.particle_system, 'atmosphere', None):
                self.particle_system.atmosphere.get_shake_offset()
        except Exception:
            pass

        # Calculate per-frame shake offsets
        shake_x = 0
        shake_y = 0
        if getattr(self, 'shake_intensity', 0.0) > 0:
            shake_x = random.uniform(-self.shake_intensity, self.shake_intensity)
            shake_y = random.uniform(-self.shake_intensity, self.shake_intensity)

        # Draw grid shifted by shake
        try:
            # grid.draw does not accept offset, so temporarily blit via an intermediate surface shift
            self.grid.draw(self.screen, theme)
            # Note: For more precise control we could modify Grid.draw to accept offsets.
        except Exception:
            self.grid.draw(self.screen, theme)

        # --- PYRO ATMOSPHERE (Round 3 Only) ---
        if self.round == 3 and self.state in [STATE_PLAYING, STATE_SCORING]:
            if getattr(self, 'pyro_bg', None):
                try:
                    self.pyro_bg.draw(self.screen)
                except Exception:
                    pass

            # Draw Pyro Enemies (if they exist in list) on top of the background
            for enemy in self.enemies:
                ex, ey = enemy['rect'].center
                pygame.draw.circle(self.screen, (0,0,0), (ex+2, ey+2), 16) # Shadow
                pygame.draw.circle(self.screen, (180,20,20), (ex, ey), 15) # Body
                pygame.draw.circle(self.screen, (255,255,255), (ex, ey), 10) # Eye
        self.ui.draw_sidebar(self.screen, self)
        self.ui.draw_hand_bg(self.screen)
        self.ui.draw_top_bar(self.screen, self)
        self.ui.draw_hud_elements(self.screen, self)
        self._draw_hand_items(theme)
        self.particle_system.draw(self.screen)
        
        if self.state == STATE_PYRO_DEATH: self.ui.draw_pyro_death(self.screen, self)
        elif self.state == STATE_GAME_OVER: self.ui.draw_game_over(self.screen, self.score)
        
        if self.state != STATE_SHOP: self.ui.draw_final_tooltip_layer(self.screen, self)
        self._draw_dragged_items(theme)

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)