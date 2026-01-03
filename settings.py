# settings.py
import pygame

# --- EKRAN AYARLARI (KRİTİK) ---
# Oyunun hesaplandığı "Gerçek" Pixel Art Çözünürlüğü
VIRTUAL_W = 640
VIRTUAL_H = 360
FPS = 60
TITLE = "SPHENKS: LEGACY"

# --- GRID ---
# 360p ekranda 8x8 grid için ideal boyut
TILE_SIZE = 28  
GRID_SIZE = 8
GRID_WIDTH = GRID_SIZE * TILE_SIZE
GRID_HEIGHT = GRID_SIZE * TILE_SIZE

# --- RENKLER (Aydınlık & Neon) ---
BG_COLOR = (20, 15, 30)          # Morumsu Gri (Siyah Değil!)
GRID_BG_COLOR = (30, 25, 40)     
GRID_LINE_COLOR = (60, 50, 80)   
STONE_COLOR = (100, 100, 110)       
ACCENT_COLOR = (0, 255, 200)     # Neon Cyan
TEXT_COLOR = (255, 255, 255)
SHOP_BG_COLOR = (15, 10, 20)
TRASH_COLOR = (200, 50, 50)
TRASH_HOVER_COLOR = (255, 100, 100)

# --- FONT ---
FONT_NAME = 'Arial' 
UI_FONT_SIZE = 16    
SCORE_FONT_SIZE = 24 

# --- OYUN AYARLARI ---
STARTING_CREDITS = 4
DISCARD_COST = 1
SCORE_PER_BLOCK = 10
SCORE_PER_LINE = 100
COMBO_MULTIPLIER = 1.5
MAX_TOTEM_SLOTS = 5
MAX_GLYPH_SLOTS = 3
VOID_REFILL_AMOUNT = 8
ANIMATION_DELAY = 20

# VOID ANIMASYON AYARLARI (YENİ)
VOID_ANIMATION_SPEED = 100 # ms
VOID_UI_SCALE = 0.8       # UI'da ne kadar büyük görüneceği

# Ses
SFX_VOLUME = 0.4
SND_PLACE = 'sounds/place.wav'
SND_CLEAR = 'sounds/clear.wav'
SND_EXPLODE = 'sounds/explosion.wav'
SND_GAMEOVER = 'sounds/gameover.wav'
SND_SELECT = 'sounds/select.wav'
SND_HIT = 'sounds/hit.wav'

# States
STATE_MENU = 'menu'
STATE_PLAYING = 'playing'
STATE_SHOP = 'shop'
STATE_LEVEL_COMPLETE = 'level_complete'
STATE_GAME_OVER = 'game_over'
STATE_PAUSED = 'paused'
STATE_ANIMATING = 'animating'
STATE_TARGETING = 'targeting'

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

THEMES = {
    'NEON': {'bg': (20, 15, 30), 'grid_bg': (30, 25, 40), 'line': (60, 50, 80), 'style': 'glass'},
    'RETRO': {'bg': (40, 40, 40), 'grid_bg': (0, 0, 0), 'line': (0, 255, 0), 'style': 'pixel'},
    'CANDY': {'bg': (255, 240, 245), 'grid_bg': (255, 255, 255), 'line': (255, 180, 200), 'style': 'flat'}
}

# Veriler
TOTEM_DATA = {
    'sniper': {'name': 'Sniper', 'price': 6, 'desc': 'Edge x2 Mult', 'trigger': 'on_score', 'rarity': 'Common'},
    'miner': {'name': 'Miner', 'price': 8, 'desc': '+$1 per Stone', 'trigger': 'on_clear', 'rarity': 'Common'},
    'architect': {'name': 'Architect', 'price': 10, 'desc': '+50 Chips no clear', 'trigger': 'on_place', 'rarity': 'Rare'},
    'void_walker': {'name': 'Void Walker', 'price': 15, 'desc': 'x3 Mult if Void < 5', 'trigger': 'on_score', 'rarity': 'Rare'},
    'midas': {'name': 'King Midas', 'price': 25, 'desc': '+$0.5 per Block', 'trigger': 'on_clear', 'rarity': 'Legendary'},
    'recycler': {'name': 'Recycler', 'price': 12, 'desc': 'Free Discard', 'trigger': 'passive', 'rarity': 'Rare'},
    'blood_pact': {'name': 'Blood Pact', 'price': 0, 'desc': 'x4 Mult / -1 Void', 'trigger': 'on_score', 'rarity': 'Legendary'},
}

GLYPHS = {
    'BOMB': {'name': 'Bomb', 'price': 4, 'desc': 'Destroy 3x3', 'color': (255, 50, 50)},
    'RESET': {'name': 'Reset', 'price': 6, 'desc': 'New Hand', 'color': (50, 100, 255)},
    'REFILL': {'name': 'Refill', 'price': 5, 'desc': '+5 Ammo', 'color': (50, 255, 100)},
    'STONE_BREAKER': {'name': 'Drill', 'price': 3, 'desc': 'Crush Stones', 'color': (150, 150, 150)}
}