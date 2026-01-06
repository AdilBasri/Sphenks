# settings.py
import pygame

# --- EKRAN AYARLARI ---
VIRTUAL_W = 850
VIRTUAL_H = 480 
FPS = 60
TITLE = "SPHENKS: ROGUELIKE"

# --- SIDEBAR & LAYOUT ---
SIDEBAR_WIDTH = 190
PLAY_AREA_W = VIRTUAL_W - SIDEBAR_WIDTH
PLAY_AREA_H = VIRTUAL_H

# --- UI ELEMENTLERİ ---
TOTEM_ICON_SIZE = 40
HAND_BG_HEIGHT = 90

# --- GRID ---
TILE_SIZE = 30 
GRID_SIZE = 8
GRID_WIDTH = GRID_SIZE * TILE_SIZE
GRID_HEIGHT = GRID_SIZE * TILE_SIZE

# --- RENKLER ---
BG_COLOR = (20, 15, 30)          
SIDEBAR_BG_COLOR = (35, 30, 45) 
PANEL_BORDER = (60, 50, 70)
SCORING_BOX_BG = (25, 20, 30)

# Balatro Renkleri
CHIPS_COLOR = (0, 150, 255) # Mavi
MULT_COLOR = (255, 50, 50)  # Kırmızı
TOTAL_COLOR = (255, 200, 50) # Altın

# Konfeti Renkleri
CONFETTI_COLORS = [
    (255, 0, 85), (0, 255, 255), (255, 255, 0), 
    (170, 0, 255), (0, 255, 100), (255, 150, 0)
]

# Oyun İçi Renkler
GRID_BG_COLOR = (30, 25, 40)     
GRID_LINE_COLOR = (60, 50, 80)   
STONE_COLOR = (100, 100, 110)       
ACCENT_COLOR = (0, 255, 200)     
TEXT_COLOR = (255, 255, 255)
SHOP_BG_COLOR = (15, 10, 20)      
TRASH_COLOR = (200, 50, 50)
TRASH_HOVER_COLOR = (255, 100, 100)

# --- FONT ---
FONT_NAME = 'Arial' 
UI_FONT_SIZE = 16    
SCORE_FONT_SIZE = 24
BIG_FONT_SIZE = 40

# --- HYPE KELİMELERİ ---
HYPE_WORDS = ["HARİKA!", "EFSANE!", "MÜKEMMEL!", "GÜÜÜMM!", "ŞOV YAPTIN!", "DURDURULAMAZ!", "İNANILMAZ!"]

# --- OYUN AYARLARI ---
STARTING_CREDITS = 5
DISCARD_COST = 1
SCORE_PER_BLOCK = 5
SCORE_PER_LINE = 50
COLOR_MATCH_BONUS = 100 
MAX_TOTEM_SLOTS = 5
MAX_GLYPH_SLOTS = 3
VOID_REFILL_AMOUNT = 3 

# --- ANTE & ROUND AYARLARI ---
BASE_VOID_COUNT = 6 
ROUND_SCALING = 1.5 
NEW_WORLD_ANTE = 9  # Bu Ante'ye geçince oyun değişir

# --- SES ---
SFX_VOLUME = 0.4
SND_PLACE = 'sounds/place.wav'
SND_CLEAR = 'sounds/clear.wav'
SND_EXPLODE = 'sounds/explosion.wav'
SND_GAMEOVER = 'sounds/gameover.wav'
SND_SELECT = 'sounds/select.wav'
SND_HIT = 'sounds/hit.wav'

# --- STATES ---
STATE_MENU = 'menu'
STATE_ROUND_SELECT = 'round_select'
STATE_PLAYING = 'playing'
STATE_SCORING = 'scoring' 
STATE_SHOP = 'shop'
STATE_LEVEL_COMPLETE = 'level_complete'
STATE_GAME_OVER = 'game_over'
STATE_PAUSE = 'pause'

# --- BLOKLAR ---
SHAPES = {
    'I': [[1, 1, 1, 1]], 'O': [[1, 1], [1, 1]],
    'T': [[0, 1, 0], [1, 1, 1]], 'S': [[0, 1, 1], [1, 1, 0]],
    'Z': [[1, 1, 0], [0, 1, 1]], 'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]], 'DOT': [[1]]
}

SHAPE_COLORS = {
    'I': (0, 255, 255), 'O': (255, 220, 0), 'T': (200, 0, 255),
    'S': (0, 255, 100), 'Z': (255, 50, 50), 'J': (50, 100, 255),
    'L': (255, 150, 0), 'DOT': (200, 200, 200)
}

# --- BLOCK TAG SYSTEM ---
BLOCK_TAGS = ['NONE', 'RED', 'BLUE', 'GOLD']
BLOCK_TAG_COLORS = {
    'NONE': None,  
    'RED': (255, 80, 80),
    'BLUE': (80, 150, 255),
    'GOLD': (255, 215, 0)
}
BLOCK_TAG_WEIGHTS = {
    'NONE': 65,  
    'RED': 20,   
    'BLUE': 10,  
    'GOLD': 5    
}

THEMES = {
    'NEON': {'bg': (20, 15, 30), 'grid_bg': (30, 25, 40), 'line': (60, 50, 80), 'style': 'glass'},
    'RETRO': {'bg': (40, 40, 40), 'grid_bg': (0, 0, 0), 'line': (0, 255, 0), 'style': 'pixel'},
    'CRIMSON': {'bg': (30, 0, 0), 'grid_bg': (10, 0, 0), 'line': (255, 50, 50), 'style': 'pixel'}, # Yeni Dünya Teması
    'CANDY': {'bg': (255, 240, 245), 'grid_bg': (255, 255, 255), 'line': (255, 180, 200), 'style': 'flat'}
}

# --- VERİTABANLARI ---
TOTEM_DATA = {
    'sniper': {'name': 'Sniper', 'price': 6, 'desc': 'Edge x2 Mult', 'trigger': 'on_score', 'rarity': 'Common'},
    'miner': {'name': 'Miner', 'price': 8, 'desc': '+$1 per Stone', 'trigger': 'on_clear', 'rarity': 'Common'},
    'architect': {'name': 'Architect', 'price': 10, 'desc': '+50 Chips no clear', 'trigger': 'on_place', 'rarity': 'Rare'},
    'void_walker': {'name': 'Void Walker', 'price': 15, 'desc': 'x3 Mult if Void < 5', 'trigger': 'on_score', 'rarity': 'Rare'},
    'midas': {'name': 'King Midas', 'price': 25, 'desc': '+$0.5 per Block', 'trigger': 'on_clear', 'rarity': 'Legendary'},
    'recycler': {'name': 'Recycler', 'price': 12, 'desc': 'Free Discard', 'trigger': 'passive', 'rarity': 'Rare'},
    'blood_pact': {'name': 'Blood Pact', 'price': 0, 'desc': 'x4 Mult / -1 Void', 'trigger': 'on_score', 'rarity': 'Legendary'},
    'savings_bond': {'name': 'Savings Bond', 'price': 10, 'desc': '+20% interest', 'trigger': 'on_round_end', 'rarity': 'Rare'},
    'golden_ticket': {'name': 'Golden Ticket', 'price': 8, 'desc': '+$3 on GOLD block', 'trigger': 'on_place', 'rarity': 'Uncommon'},
    'gamblers_dice': {'name': "Gambler's Dice", 'price': 5, 'desc': '25% destroy/x5 score', 'trigger': 'on_place', 'rarity': 'Uncommon'},
    'ruby_lens': {'name': 'Ruby Lens', 'price': 7, 'desc': '+2 Mult for RED', 'trigger': 'on_score', 'rarity': 'Common'},
    'sapphire_lens': {'name': 'Sapphire Lens', 'price': 7, 'desc': '+2 Mult for BLUE', 'trigger': 'on_score', 'rarity': 'Common'},
    
    # --- OMEGA TOTEMLER (Yeni Dünya İçin) ---
    'dark_matter': {'name': 'Dark Matter', 'price': 40, 'desc': 'x10 Mult', 'trigger': 'on_score', 'rarity': 'Omega'},
    'infinity_stone': {'name': 'Infinity Stone', 'price': 35, 'desc': '+$5 & x2 Mult on clear', 'trigger': 'on_clear', 'rarity': 'Omega'},
    'chronos': {'name': 'Chronos', 'price': 30, 'desc': '+50% Interest', 'trigger': 'on_round_end', 'rarity': 'Omega'}
}

# Sadece Dükkan üretimi için ayrılmış liste
OMEGA_KEYS = ['dark_matter', 'infinity_stone', 'chronos']

GLYPHS = {
    'BOMB': {'name': 'Bomb', 'price': 4, 'desc': 'Destroy 3x3', 'color': (255, 50, 50)},
    'RESET': {'name': 'Reset', 'price': 6, 'desc': 'New Hand', 'color': (50, 100, 255)},
    'REFILL': {'name': 'Refill', 'price': 5, 'desc': '+5 Ammo', 'color': (50, 255, 100)},
    'STONE_BREAKER': {'name': 'Drill', 'price': 3, 'desc': 'Crush Stones', 'color': (150, 150, 150)}
}

RELICS = {
    'golden_skull': {'name': 'Golden Skull', 'price': 50, 'desc': 'A shiny ancient skull.', 'type': 'treasure', 'value': 100},
    'dusty_map': {'name': 'Dusty Map', 'price': 10, 'desc': 'Reveals secrets.', 'type': 'passive', 'value': 0}
}

BOSS_DATA = {
    'The Wall': {'desc': 'Start with 3 Stones', 'color': (100, 100, 100)},
    'The Haze': {'desc': 'No Ghost Block', 'color': (150, 50, 150)},
    'The Drain': {'desc': 'Discard costs $3', 'color': (50, 150, 50)},
    'The Shrink': {'desc': 'Hand Size -1', 'color': (200, 100, 50)}
}