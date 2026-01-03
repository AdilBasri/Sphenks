import pygame

# Ekran Ayarları
FPS = 60
TITLE = "SPHENKS: NEON GRID"

# Grid Ayarları
GRID_SIZE = 8
TILE_SIZE = 70
GRID_WIDTH = GRID_SIZE * TILE_SIZE
GRID_HEIGHT = GRID_SIZE * TILE_SIZE

# --- PREMIUM RENK PALETİ (NEON / DARK) ---
BG_COLOR = (10, 10, 18)          # Neredeyse siyah, çok hafif lacivert
GRID_BG_COLOR = (15, 15, 25)     # Grid zemini
GRID_LINE_COLOR = (30, 30, 45)   # Grid çizgileri
EMPTY_CELL_COLOR = (20, 20, 30)
STONE_COLOR = (80, 80, 90)       # <-- EKSİK OLAN KISIM BURASIYDI

# UI Renkleri
TEXT_COLOR = (255, 255, 255)
ACCENT_COLOR = (0, 255, 200)     # Turkuaz Neon
UI_ACCENT = (255, 0, 100)        # Pembe Neon
SHOP_BG_COLOR = (15, 12, 20)

# --- FONT ---
FONT_NAME = 'Arial' 
UI_FONT_SIZE = 22 
SCORE_FONT_SIZE = 40 

# Oyun Dengesi
SCORE_PER_BLOCK = 10
SCORE_PER_LINE = 100
COMBO_MULTIPLIER = 1.5
STARTING_CREDITS = 10

# Ses
SFX_VOLUME = 0.4
MUSIC_VOLUME = 0.2
SND_PLACE = 'sounds/place.wav'
SND_CLEAR = 'sounds/clear.wav'
SND_EXPLODE = 'sounds/explosion.wav'
SND_GAMEOVER = 'sounds/gameover.wav'
SND_SELECT = 'sounds/select.wav'
SND_HIT = 'sounds/hit.wav'

# --- BLOK ŞEKİLLERİ ---
SHAPES = {
    '1': [[1]],
    '2': [[1, 1]],
    '3': [[1, 1, 1]],
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'L': [[1, 0], [1, 0], [1, 1]],
    'J': [[0, 1], [0, 1], [1, 1]],
    'T': [[1, 1, 1], [0, 1, 0]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'Z': [[1, 1, 0], [0, 1, 1]],
    'C': [[1, 1], [1, 0]]
}

# --- NEON RENKLER ---
SHAPE_COLORS = {
    '1': (200, 200, 255), # Buz Mavisi
    '2': (255, 80, 80),   # Neon Kırmızı
    '3': (80, 255, 80),   # Neon Yeşil
    'I': (0, 255, 255),   # Cyan
    'O': (255, 255, 0),   # Sarı
    'L': (255, 150, 0),   # Turuncu
    'J': (50, 100, 255),  # Elektrik Mavisi
    'T': (180, 50, 255),  # Mor
    'S': (0, 255, 128),   # Spring Green
    'Z': (255, 0, 100),   # Hot Pink
    'C': (255, 100, 200)  # Pembe
}

# Relicler
RELICS = {
    'RUBY': {'name': 'Ruby Crystal', 'price': 5, 'desc': '+0.5x Global Mult', 'type': 'mult_add', 'value': 0.5},
    'GOLD': {'name': 'Midas Glove', 'price': 8, 'desc': '+$2 Per Clear', 'type': 'money_add', 'value': 2},
    'AMETHYST': {'name': 'Void Essence', 'price': 10, 'desc': '+50 Base Score', 'type': 'score_add', 'value': 50},
    'DIAMOND': {'name': 'Prism Shard', 'price': 15, 'desc': 'x1.5 Final Score', 'type': 'final_mult', 'value': 1.5},
    'EMERALD': {'name': 'Recycler', 'price': 12, 'desc': '+2 Extra Void Ammo', 'type': 'ammo_bonus', 'value': 2}
}

# Oyun Durumları
STATE_MENU = 'menu'
STATE_PLAYING = 'playing'
STATE_SHOP = 'shop'
STATE_LEVEL_COMPLETE = 'level_complete'
STATE_GAME_OVER = 'game_over'
STATE_PAUSED = 'paused'

# settings.py (GÜNCELLE)

# ... (Eski kodlar aynı kalacak, sadece aşağıdakileri güncelle/ekle) ...

# --- OYUN DENGESİ (BALANCING) ---
STARTING_CREDITS = 2       # 10'dan 2'ye düşürdük. Fakir başlıyoruz.
SCORE_PER_BLOCK = 5        # 10'dan 5'e.
SCORE_PER_LINE = 50        # 100'den 50'ye. Puan kasmak zorlaşsın.
VOID_REFILL_AMOUNT = 10    # 12'den 10'a. Stok yönetimi kritiğe binsin.

# Relic Fiyatlarını Zamlayalım (Enflasyon!)
RELICS = {
    'RUBY': {'name': 'Ruby Crystal', 'price': 15, 'desc': '+0.5x Global Mult', 'type': 'mult_add', 'value': 0.5},
    'GOLD': {'name': 'Midas Glove', 'price': 25, 'desc': '+$2 Per Clear', 'type': 'money_add', 'value': 2}, # Çok güçlüydü
    'AMETHYST': {'name': 'Void Essence', 'price': 20, 'desc': '+50 Base Score', 'type': 'score_add', 'value': 50},
    'DIAMOND': {'name': 'Prism Shard', 'price': 40, 'desc': 'x1.5 Final Score', 'type': 'final_mult', 'value': 1.5},
    'EMERALD': {'name': 'Recycler', 'price': 30, 'desc': '+3 Extra Void Ammo', 'type': 'ammo_bonus', 'value': 3}
}

# --- TEMA TANIMLARI (WORLD SYSTEMS) ---
THEMES = {
    'NEON': {
        'bg': (10, 10, 18),
        'grid_bg': (15, 15, 25),
        'line': (30, 30, 45),
        'style': 'glass' # Parlak, cam gibi
    },
    'RETRO': {
        'bg': (40, 40, 40), # Gri beton
        'grid_bg': (0, 0, 0), # Simsiyah grid içi
        'line': (0, 255, 0), # Matrix yeşili çizgiler
        'style': 'pixel' # Keskin kenarlar, siyah kontür
    },
    'CANDY': {
        'bg': (255, 240, 245), # Açık pembe
        'grid_bg': (255, 255, 255),
        'line': (255, 180, 200),
        'style': 'flat' # Yumuşak, gölgesiz, pastel
    }
}

# settings.py İÇİNE EKLE:

# --- MECHANICS ---
DISCARD_COST = 2  # Bir bloğu çöpe atmanın bedeli (Kredi)

# --- COLORS ---
TRASH_COLOR = (255, 50, 50)     # Kırmızı
TRASH_HOVER_COLOR = (255, 100, 100)
PULSE_COLOR = (20, 20, 40)      # Arka planın yanıp söneceği renk

# settings.py İÇİNE EKLE:

STATE_ANIMATING = 'animating' # Patlama animasyonu oynarken kilitlenen durum
ANIMATION_DELAY = 20          # Kaç kare (frame) bekleyecek? (60 FPS'de 20 = 0.3 sn)
SCORE_SPEED = 10              # Puan sayacının artış hızı

# settings.py GÜNCELLEME

# --- OYUN YAPISI ---
MAX_TOTEM_SLOTS = 5  # Balatro usulü 5 slot
DISCARD_COST = 2

# Eski RELICS sözlüğünü SİL veya yorum satırına al. Artık TOTEM_DATA kullanacağız.

# settings.py GÜNCELLEME

# --- RENKLER ---
PYRAMID_COLOR = (40, 0, 60)      # Koyu Mor Piramit
PYRAMID_GLOW = (150, 0, 255)     # Neon Mor Çizgiler
EYE_COLOR = (0, 255, 255)        # Piramidin Gözü (Cyan)

# --- MECHANICS ---
MAX_GLYPH_SLOTS = 3 # En fazla 3 büyü taşıyabilirsin

# --- GLYPHS (RÜNLER - TEK KULLANIMLIK) ---
GLYPHS = {
    'BOMB': {'name': 'Void Bomb', 'price': 4, 'desc': 'Destroy 3x3 Area', 'color': (255, 50, 50)},
    'RESET': {'name': 'Time Warp', 'price': 6, 'desc': 'Reroll Hand Blocks', 'color': (50, 100, 255)},
    'REFILL': {'name': 'Dark Matter', 'price': 5, 'desc': '+5 Void Ammo Instantly', 'color': (50, 255, 100)},
    'STONE_BREAKER': {'name': 'Drill', 'price': 3, 'desc': 'Destroy All Stones', 'color': (150, 150, 150)}
}