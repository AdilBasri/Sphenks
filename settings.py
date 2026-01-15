# settings.py
import pygame
import os
import sys

# --- BU FONKSİYON EN ÜSTTE ---
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

# --- LANGUAGE SUPPORT ---
AVAILABLE_LANGUAGES = ["EN", "TR", "DE", "ES", "ZH", "PT", "FR", "IT"]
DEFAULT_LANGUAGE = "EN"

# --- EKRAN AYARLARI ---
# Native resolution for the game
VIRTUAL_W = 850
VIRTUAL_H = 480 
FPS = 60
TITLE = "SPHENKS: ROGUELIKE"

# --- WINDOW SETTINGS (same as native resolution - no virtual surface intermediary) ---
USE_FULLSCREEN = False  # Default to windowed mode
WINDOW_W = 850  # Same as VIRTUAL_W
WINDOW_H = 480  # Same as VIRTUAL_H

# --- SIDEBAR & LAYOUT ---
SIDEBAR_WIDTH = 220
PLAY_AREA_W = VIRTUAL_W - SIDEBAR_WIDTH
PLAY_AREA_H = VIRTUAL_H

# --- UI ELEMENTLERİ ---
TOTEM_ICON_SIZE = 40
HAND_BG_HEIGHT = 90

# --- MENÜ AYARLARI (EKSİK OLANLAR EKLENDİ) ---
LOGO_FILES = ["1.jpg", "2.jpg", "3.jpg", "4.jpg", "5.jpg", "6.jpg", "7.jpg"]
MAX_MENU_BLOCKS = 15

# --- GRID ---
# Calibrated cell size: 8 rows * 38 = 304px within 480px height
CELL_SIZE = 38
TILE_SIZE = CELL_SIZE
GRID_SIZE = 8
GRID_WIDTH = GRID_SIZE * TILE_SIZE
GRID_HEIGHT = GRID_SIZE * TILE_SIZE

# Center grid within the playable area (excluding sidebar)
CENTER_OFFSET = (PLAY_AREA_W - GRID_WIDTH) // 2
GRID_OFFSET_X = SIDEBAR_WIDTH + CENTER_OFFSET
GRID_OFFSET_Y = 60

# --- HAND LAYOUT ---
# Draw the hand strictly below the grid with proper gap
HAND_Y = GRID_OFFSET_Y + GRID_HEIGHT + 25

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

# 1-Bit Color Constants (Pyro Mode)
COLOR_1BIT_BG = (20, 0, 20)
COLOR_1BIT_FG = (230, 230, 230)
COLOR_1BIT_ENEMY = (255, 255, 255)
COLOR_PYRO_ACCENT = (222, 0, 177)

# Pyro Mode Game Balance
PYRO_ENEMY_SPEED = 1.5
PYRO_SPAWN_DELAY = 1500

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
SND_PLACE = resource_path('sounds/place.wav')
SND_CLEAR = resource_path('sounds/clear.wav')
SND_EXPLODE = resource_path('sounds/explosion.wav')
SND_GAMEOVER = resource_path('sounds/gameover.wav')
SND_SELECT = resource_path('sounds/select.wav')
SND_HIT = resource_path('sounds/hit.wav')

# --- STATES ---
STATE_INTRO = 'intro'
STATE_MENU = 'menu'
STATE_TRAINING = 'training'
STATE_ROUND_SELECT = 'round_select'
STATE_PLAYING = 'playing'
STATE_SCORING = 'scoring' 
STATE_SHOP = 'shop'
STATE_DEBT = 'state_debt'
STATE_COLLECTION = 'state_collection'
STATE_SETTINGS = 'state_settings'
STATE_LEVEL_COMPLETE = 'level_complete'
STATE_GAME_OVER = 'game_over'
STATE_PAUSE = 'pause'
STATE_DEMO_END = 'demo_end'
STATE_COMING_SOON = 'coming_soon'
STATE_PYRO = 'pyro_mode'
STATE_PYRO_DEATH = 'pyro_death'

# --- SETTINGS ---
RESOLUTIONS = [
    (850, 480),
    (1280, 720),
    (1920, 1080)
]

# --- DEBT SCREEN ---
PHARAOH_QUOTES = [
    "Work harder, slave.",
    "Your debt remains.",
    "The pyramid waits.",
    "Freedom is expensive.",
    "The sands remember all debts.",
    "Your labor pleases the gods.",
    "Only fools dream of freedom.",
    "The debt is eternal."
]

# Quotes shown when debt is fully paid (freedom state)
FREEDOM_QUOTES = [
    "Artık özgürsün... ama ellerin hala titriyor.",
    "Borç bitti. Bloklar bitmedi.",
    "Özgürlük, başka bir hapishanedir.",
    "Blok dizmek alışkanlık olmuş olsa gerek...",
    "Firavun sustu. Şimdi sonsuzluk konuşuyor."
]

# --- COLLECTIBLES ---
COLLECTIBLES = [
    {
        'id': 'broken_vase',
        'name': 'Broken Vase',
        'unlock_at': 5000,
        'desc': 'A shattered vessel from the old kingdom.',
        'icon': '🏺'
    },
    {
        'id': 'sphinx',
        'name': 'Sphinx Head',
        'unlock_at': 10000,
        'desc': 'A crumbled relic.',
        'icon': '🗿'
    },
    {
        'id': 'scarab',
        'name': 'Golden Scarab',
        'unlock_at': 25000,
        'desc': 'Sacred beetle of transformation.',
        'icon': '🪲'
    },
    {
        'id': 'ankh',
        'name': 'Ankh of Life',
        'unlock_at': 50000,
        'desc': 'Symbol of eternal life.',
        'icon': '☥'
    },
    {
        'id': 'eye_ra',
        'name': 'Eye of Ra',
        'unlock_at': 100000,
        'desc': 'It sees all.',
        'icon': '👁'
    },
    {
        'id': 'crown',
        'name': 'Pharaoh Crown',
        'unlock_at': 250000,
        'desc': 'The double crown of upper and lower.',
        'icon': '👑'
    },
    {
        'id': 'scepter',
        'name': 'Royal Scepter',
        'unlock_at': 500000,
        'desc': 'Power flows through this staff.',
        'icon': '🪄'
    },
    {
        'id': 'freedom',
        'name': 'FREEDOM',
        'unlock_at': 1000000,
        'desc': 'You are free. The debt is paid.',
        'icon': '✨'
    }
]



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
    'CANDY': {'bg': (255, 240, 245), 'grid_bg': (255, 255, 255), 'line': (255, 180, 200), 'style': 'flat'},
    'TERMINAL': {'bg': (0, 0, 0), 'grid_bg': (0, 10, 0), 'line': (0, 255, 50), 'style': 'pixel'}
}

# --- VERİTABANLARI ---
TOTEM_DATA = {
    'sniper': {'name': 'Sniper', 'price': 6, 'desc': 'Edge x2 Mult', 'trigger': 'on_score', 'rarity': 'Common'},
    'miner': {'name': 'Miner', 'price': 4, 'desc': '+$1 per Stone', 'trigger': 'on_clear', 'rarity': 'Common'},
    'architect': {'name': 'Architect', 'price': 10, 'desc': '+50 Chips no clear', 'trigger': 'on_place', 'rarity': 'Rare'},
    'void_walker': {'name': 'Void Walker', 'price': 15, 'desc': 'x3 Mult if Void < 5', 'trigger': 'on_score', 'rarity': 'Rare'},
    'midas': {'name': 'King Midas', 'price': 25, 'desc': '+$0.5 per Block', 'trigger': 'on_clear', 'rarity': 'Legendary'},
    'recycler': {'name': 'Recycler', 'price': 12, 'desc': 'Free Discard', 'trigger': 'passive', 'rarity': 'Rare'},
    'blood_pact': {'name': 'Blood Pact', 'price': 3, 'desc': 'x4 Mult / -1 Void', 'trigger': 'on_score', 'rarity': 'Legendary'},
    'savings_bond': {'name': 'Savings Bond', 'price': 10, 'desc': '+20% interest', 'trigger': 'on_round_end', 'rarity': 'Rare'},
    'golden_ticket': {'name': 'Golden Ticket', 'price': 6, 'desc': '+$3 on GOLD block', 'trigger': 'on_place', 'rarity': 'Uncommon'},
    'gamblers_dice': {'name': "Gambler's Dice", 'price': 5, 'desc': '25% destroy/x5 score', 'trigger': 'on_place', 'rarity': 'Uncommon'},
    'ruby_lens': {'name': 'Ruby Lens', 'price': 6, 'desc': '+2 Mult for RED', 'trigger': 'on_score', 'rarity': 'Common'},
    'sapphire_lens': {'name': 'Sapphire Lens', 'price': 6, 'desc': '+2 Mult for BLUE', 'trigger': 'on_score', 'rarity': 'Common'},
    
    # --- OMEGA TOTEMLER (Yeni Dünya İçin) ---
    'dark_matter': {'name': 'Dark Matter', 'price': 40, 'desc': 'x10 Mult', 'trigger': 'on_score', 'rarity': 'Omega'},
    'infinity_stone': {'name': 'Infinity Stone', 'price': 35, 'desc': '+$5 & x2 Mult on clear', 'trigger': 'on_clear', 'rarity': 'Omega'},
    'chronos': {'name': 'Chronos', 'price': 30, 'desc': '+50% Interest', 'trigger': 'on_round_end', 'rarity': 'Omega'}
}

# --- NEW UNLOCKABLE TOTEMS ---
TOTEM_DATA.update({
    'tiny_bag': {
        'name': 'Tiny Bag',
        'price': 8,
        'desc': 'Start each round with +$10.',
        'trigger': 'passive',
        'rarity': 'Uncommon'
    },
    'blueprint': {
        'name': 'Blueprint',
        'price': 12,
        'desc': 'Architectural plans (passive — logic added later).',
        'trigger': 'passive',
        'rarity': 'Rare'
    },
    'gamblers_coin': {
        'name': "Gambler's Coin",
        'price': 10,
        'desc': 'Rerolls cost $1 less.',
        'trigger': 'passive',
        'rarity': 'Uncommon'
    },
    'obsidian_wall': {
        'name': 'Obsidian Wall',
        'price': 18,
        'desc': 'Pyro enemies move slower (x0.8).',
        'trigger': 'passive',
        'rarity': 'Rare'
    },
    'divine_smite': {
        'name': 'Divine Smite',
        'price': 35,
        'desc': 'Right-click: smite enemies (3 charges/round).',
        'trigger': 'passive',
        'rarity': 'Legendary'
    },
    'midas_hand': {
        'name': 'Midas Hand',
        'price': 30,
        'desc': '+$2 per unused block at round end.',
        'trigger': 'on_round_end',
        'rarity': 'Legendary'
    },
    'phoenix_feather': {
        'name': 'Phoenix Feather',
        'price': 45,
        'desc': 'Revive once on death (consumable).',
        'trigger': 'passive',
        'rarity': 'Legendary'
    },
    'eye_of_ra': {
        'name': 'Eye of Ra',
        'price': 60,
        'desc': 'Global 1.5x score multiplier.',
        'trigger': 'on_score',
        'rarity': 'Omega'
    }
})

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
# settings.py dosyasının en altına yapıştır:

# --- PYRO MODU / YENİ DÜNYA (ANTE 9+) AYARLARI ---
NEW_WORLD_ANTE = 9  # Bu seviye ve sonrasında oyun modu değişir

# Atmosfer Renkleri (Koyu Kırmızı/Siyah)
COLOR_PYRO_BG = (15, 0, 5)
COLOR_PYRO_GRID = (100, 0, 0)
COLOR_PYRO_ACCENT = (255, 50, 50)

# --- COUNTRIES (ISO Alpha-2, English name) ---
# Alfabetik sıraya sokalım ki klavye ile arama düzgün çalışsın
COUNTRIES = [
    ("AF", "Afghanistan"), ("AL", "Albania"), ("DZ", "Algeria"), ("AD", "Andorra"), ("AO", "Angola"),
    ("AG", "Antigua and Barbuda"), ("AR", "Argentina"), ("AM", "Armenia"), ("AU", "Australia"), ("AT", "Austria"),
    ("AZ", "Azerbaijan"), ("BS", "Bahamas"), ("BH", "Bahrain"), ("BD", "Bangladesh"), ("BB", "Barbados"),
    ("BY", "Belarus"), ("BE", "Belgium"), ("BZ", "Belize"), ("BJ", "Benin"), ("BT", "Bhutan"),
    ("BO", "Bolivia"), ("BA", "Bosnia and Herzegovina"), ("BW", "Botswana"), ("BR", "Brazil"), ("BN", "Brunei"),
    ("BG", "Bulgaria"), ("BF", "Burkina Faso"), ("BI", "Burundi"), ("CV", "Cabo Verde"), ("KH", "Cambodia"),
    ("CM", "Cameroon"), ("CA", "Canada"), ("CF", "Central African Republic"), ("TD", "Chad"), ("CL", "Chile"),
    ("CN", "China"), ("CO", "Colombia"), ("KM", "Comoros"), ("CG", "Congo"), ("CD", "Congo (Democratic Republic)"),
    ("CR", "Costa Rica"), ("CI", "Côte d'Ivoire"), ("HR", "Croatia"), ("CU", "Cuba"), ("CY", "Cyprus"),
    ("CZ", "Czechia"), ("DK", "Denmark"), ("DJ", "Djibouti"), ("DM", "Dominica"), ("DO", "Dominican Republic"),
    ("EC", "Ecuador"), ("EG", "Egypt"), ("SV", "El Salvador"), ("GQ", "Equatorial Guinea"), ("ER", "Eritrea"),
    ("EE", "Estonia"), ("SZ", "Eswatini"), ("ET", "Ethiopia"), ("FJ", "Fiji"), ("FI", "Finland"),
    ("FR", "France"), ("GA", "Gabon"), ("GM", "Gambia"), ("GE", "Georgia"), ("DE", "Germany"),
    ("GH", "Ghana"), ("GR", "Greece"), ("GD", "Grenada"), ("GT", "Guatemala"), ("GN", "Guinea"),
    ("GW", "Guinea-Bissau"), ("GY", "Guyana"), ("HT", "Haiti"), ("HN", "Honduras"), ("HU", "Hungary"),
    ("IS", "Iceland"), ("IN", "India"), ("ID", "Indonesia"), ("IR", "Iran"), ("IQ", "Iraq"),
    ("IE", "Ireland"), ("IL", "Israel"), ("IT", "Italy"), ("JM", "Jamaica"), ("JP", "Japan"),
    ("JO", "Jordan"), ("KZ", "Kazakhstan"), ("KE", "Kenya"), ("KI", "Kiribati"), ("KP", "Korea (North)"),
    ("KR", "Korea (South)"), ("XK", "Kosovo"), ("KW", "Kuwait"), ("KG", "Kyrgyzstan"), ("LA", "Laos"),
    ("LV", "Latvia"), ("LB", "Lebanon"), ("LS", "Lesotho"), ("LR", "Liberia"), ("LY", "Libya"),
    ("LI", "Liechtenstein"), ("LT", "Lithuania"), ("LU", "Luxembourg"), ("MG", "Madagascar"), ("MW", "Malawi"),
    ("MY", "Malaysia"), ("MV", "Maldives"), ("ML", "Mali"), ("MT", "Malta"), ("MH", "Marshall Islands"),
    ("MR", "Mauritania"), ("MU", "Mauritius"), ("MX", "Mexico"), ("FM", "Micronesia"), ("MD", "Moldova"),
    ("MC", "Monaco"), ("MN", "Mongolia"), ("ME", "Montenegro"), ("MA", "Morocco"), ("MZ", "Mozambique"),
    ("MM", "Myanmar"), ("NA", "Namibia"), ("NR", "Nauru"), ("NP", "Nepal"), ("NL", "Netherlands"),
    ("NZ", "New Zealand"), ("NI", "Nicaragua"), ("NE", "Niger"), ("NG", "Nigeria"), ("MK", "North Macedonia"),
    ("NO", "Norway"), ("OM", "Oman"), ("PK", "Pakistan"), ("PW", "Palau"), ("PA", "Panama"),
    ("PG", "Papua New Guinea"), ("PY", "Paraguay"), ("PE", "Peru"), ("PH", "Philippines"), ("PL", "Poland"),
    ("PT", "Portugal"), ("QA", "Qatar"), ("RO", "Romania"), ("RU", "Russia"), ("RW", "Rwanda"),
    ("KN", "Saint Kitts and Nevis"), ("LC", "Saint Lucia"), ("VC", "Saint Vincent and the Grenadines"),
    ("WS", "Samoa"), ("SM", "San Marino"), ("ST", "Sao Tome and Principe"), ("SA", "Saudi Arabia"),
    ("SN", "Senegal"), ("RS", "Serbia"), ("SC", "Seychelles"), ("SL", "Sierra Leone"), ("SG", "Singapore"),
    ("SK", "Slovakia"), ("SI", "Slovenia"), ("SB", "Solomon Islands"), ("SO", "Somalia"), ("ZA", "South Africa"),
    ("SS", "South Sudan"), ("ES", "Spain"), ("LK", "Sri Lanka"), ("SD", "Sudan"), ("SR", "Suriname"),
    ("SE", "Sweden"), ("CH", "Switzerland"), ("SY", "Syria"), ("TW", "Taiwan"), ("TJ", "Tajikistan"),
    ("TZ", "Tanzania"), ("TH", "Thailand"), ("TL", "Timor-Leste"), ("TG", "Togo"), ("TO", "Tonga"),
    ("TT", "Trinidad and Tobago"), ("TN", "Tunisia"), ("TR", "Turkey"), ("TM", "Turkmenistan"),
    ("TV", "Tuvalu"), ("UG", "Uganda"), ("UA", "Ukraine"), ("AE", "United Arab Emirates"),
    ("GB", "United Kingdom"), ("US", "United States"), ("UY", "Uruguay"), ("UZ", "Uzbekistan"),
    ("VU", "Vanuatu"), ("VA", "Vatican City"), ("VE", "Venezuela"), ("VN", "Vietnam"), ("YE", "Yemen"),
    ("ZM", "Zambia"), ("ZW", "Zimbabwe"), ("PS", "Palestine"), ("EH", "Western Sahara"), ("BQ", "Bonaire"),
    ("CW", "Curaçao"), ("SX", "Sint Maarten"), ("MF", "Saint Martin"), ("SS", "South Sudan"), ("XK", "Kosovo"),
    ("AX", "Åland Islands"), ("GG", "Guernsey"), ("IM", "Isle of Man"), ("JE", "Jersey"), ("BL", "Saint Barthélemy"),
    ("SH", "Saint Helena"), ("TC", "Turks and Caicos Islands"), ("IO", "British Indian Ocean Territory"),
    ("CK", "Cook Islands"), ("FK", "Falkland Islands"), ("GF", "French Guiana"), ("PF", "French Polynesia"),
    ("GP", "Guadeloupe"), ("MQ", "Martinique"), ("NC", "New Caledonia"), ("RE", "Réunion"), ("PM", "Saint Pierre and Miquelon"),
    ("GS", "South Georgia and the South Sandwich Islands"), ("TF", "French Southern Territories"), ("UM", "United States Minor Outlying Islands"),
    ("AQ", "Antarctica"), ("BV", "Bouvet Island"), ("HM", "Heard Island and McDonald Islands"), ("AX", "Aland Islands")
]
# Alfabetik sıraya sokalım ki klavye ile arama düzgün çalışsın
COUNTRIES.sort(key=lambda x: x[1])

# Düşman Ayarları
PYRO_ENEMY_SPEED = 0.3        # Düşmanların merkeze yürüme hızı
PYRO_SPAWN_DELAY = 120        # Kaç karede bir düşman çıkacağı (60 FPS'de ~2 sn)

# --- PHARAOH DIALOGUES ---
PHARAOH_SPEECH = {
    'IDLE': {
        'EN': [
            "Work faster, mortal!", "My pyramid is waiting...", "Do you call that placement?",
            "Less thinking, more stacking!", "Yawn...", "Are you sleeping?", "My cat plays better."
        ],
        'TR': [
            "Daha hızlı çalış köle!", "Piramidim bekliyor...", "Oraya mı koydun cidden?",
            "Az düşün çok iş yap!", "Esniyorum...", "Uyuyor musun?", "Kedim bile daha iyi oynar."
        ],
        'DE': [
            "Arbeite schneller, Sterblicher!", "Meine Pyramide wartet...", "Nennst du das Platzierung?",
            "Weniger denken, mehr stapeln!", "Gähn...", "Schläfst du?", "Meine Katze spielt besser."
        ],
        'ES': [
            "¡Trabaja más rápido, mortal!", "Mi pirámide está esperando...", "¿A eso llamas colocación?",
            "¡Menos pensar, más apilar!", "Bostezo...", "¿Estás durmiendo?", "Mi gato juega mejor."
        ],
        'ZH': [
            "工作快点，凡人！", "我的金字塔在等待...", "你叫这个放置？",
            "少想多做！", "哈欠...", "你在睡觉吗？", "我的猫都比你玩得好。"
        ],
        'PT': [
            "Trabalhe mais rápido, mortal!", "Minha pirâmide está esperando...", "Você chama isso de colocação?",
            "Menos pensar, mais empilhar!", "Bocejo...", "Você está dormindo?", "Meu gato joga melhor."
        ],
        'FR': [
            "Travaille plus vite, mortel!", "Ma pyramide attend...", "Tu appelles ça un placement?",
            "Moins réfléchir, plus empiler!", "Bâillement...", "Tu dors?", "Mon chat joue mieux."
        ],
        'IT': [
            "Lavora più veloce, mortale!", "La mia piramide sta aspettando...", "La chiami questa una posizione?",
            "Meno pensare, più impilare!", "Sbadiglio...", "Stai dormendo?", "Il mio gatto gioca meglio."
        ]
    },
    'PYRO': {
        'EN': [
            "WHAT DID YOU DO?!", "SYSTEM FAILURE!", "ERROR 404: REALITY NOT FOUND",
            "IT BURNS!", "DELETE THEM NOW!", "REBOOTING..."
        ],
        'TR': [
            "NE YAPTIN SEN?!", "SİSTEM ÇÖKÜYOR!", "HATA 404: GERÇEKLİK YOK",
            "YANIYOR! YANIYOR!", "SİL ONLARI ÇABUK!", "YENİDEN BAŞLATILIYOR..."
        ],
        'DE': [
            "WAS HAST DU GETAN?!", "SYSTEMFEHLER!", "FEHLER 404: REALITÄT NICHT GEFUNDEN",
            "ES BRENNT!", "LÖSCHE SIE JETZT!", "NEUSTART..."
        ],
        'ES': [
            "¡¿QUÉ HICISTE?!", "¡FALLO DEL SISTEMA!", "ERROR 404: REALIDAD NO ENCONTRADA",
            "¡ARDE!", "¡ELIMÍNALOS AHORA!", "REINICIANDO..."
        ],
        'ZH': [
            "你做了什么？！", "系统故障！", "错误404：现实未找到",
            "在燃烧！", "现在删除它们！", "重新启动中..."
        ],
        'PT': [
            "O QUE VOCÊ FEZ?!", "FALHA DO SISTEMA!", "ERRO 404: REALIDADE NÃO ENCONTRADA",
            "ESTÁ QUEIMANDO!", "DELETE-OS AGORA!", "REINICIANDO..."
        ],
        'FR': [
            "QU'AS-TU FAIT?!", "DÉFAILLANCE DU SYSTÈME!", "ERREUR 404: RÉALITÉ NON TROUVÉE",
            "ÇA BRÛLE!", "SUPPRIME-LES MAINTENANT!", "REDÉMARRAGE..."
        ],
        'IT': [
            "COSA HAI FATTO?!", "GUASTO DEL SISTEMA!", "ERRORE 404: REALTÀ NON TROVATA",
            "BRUCIA!", "ELIMINALI ORA!", "RIAVVIO..."
        ]
    },
    'COMBO': {
        'EN': ["IMPRESSIVE!", "A WORTHY OFFERING.", "THE GODS ARE PLEASED.", "DOUBLE CRUSH!", "MAGNIFICENT!"],
        'TR': ["ETKİLEYİCİ!", "LAYIK BİR SUNU.", "TANRILAR MEMNUN.", "ÇİFTE VURUŞ!", "MÜHTEŞEM!"],
        'DE': ["BEEINDRUCKEND!", "EIN WÜRDIGES OPFER.", "DIE GÖTTER SIND ERFREUT.", "DOPPELTER SCHLAG!", "GROSSARTIG!"],
        'ES': ["¡IMPRESIONANTE!", "UNA OFRENDA DIGNA.", "LOS DIOSES ESTÁN COMPLACIDOS.", "¡DOBLE GOLPE!", "¡MAGNÍFICO!"],
        'ZH': ["令人印象深刻！", "值得的祭品。", "诸神很高兴。", "双重粉碎！", "壮观！"],
        'PT': ["IMPRESSIONANTE!", "UMA OFERENDA DIGNA.", "OS DEUSES ESTÃO SATISFEITOS.", "GOLPE DUPLO!", "MAGNÍFICO!"],
        'FR': ["IMPRESSIONNANT!", "UNE OFFRANDE DIGNE.", "LES DIEUX SONT SATISFAITS.", "DOUBLE ÉCRASEMENT!", "MAGNIFIQUE!"],
        'IT': ["IMPRESSIONANTE!", "UN'OFFERTA DEGNA.", "GLI DEI SONO SODDISFATTI.", "DOPPIO COLPO!", "MAGNIFICO!"]
    }
}

PHARAOH_TUTORIAL = {
    0: "Welcome, slave. Build my legacy.",
    1: "Drag that block. Don't be clumsy.",
    2: "Garbage goes to the trash. Like you.",
    3: "Good. Now work faster."
}

# --- DEATH QUOTES ---
DEATH_QUOTES = {
    'EN': [
        "Your back broke from the weight...",
        "The system purged you.",
        "You were too slow...",
        "Simulation Resetting...",
        "Critical Failure."
    ],
    'TR': [
        "Sırtın yükü taşıyamadı...",
        "Sistem seni sildi.",
        "Çok yavaştın...",
        "Simülasyon Sıfırlanıyor...",
        "Kritik Hata: Beden Bulunamadı."
    ],
    'DE': [
        "Dein Rücken brach unter dem Gewicht...",
        "Das System löschte dich.",
        "Du warst zu langsam...",
        "Simulation wird zurückgesetzt...",
        "Kritischer Fehler."
    ],
    'ES': [
        "Tu espalda se rompió bajo el peso...",
        "El sistema te purificó.",
        "Eras demasiado lento...",
        "Reiniciando simulación...",
        "Fallo crítico."
    ],
    'ZH': [
        "你的背部无法承载重量...",
        "系统将你清除了。",
        "你太慢了...",
        "模拟重置中...",
        "致命错误。"
    ],
    'PT': [
        "Suas costas quebraram sob o peso...",
        "O sistema o purificou.",
        "Você era muito lento...",
        "Reiniciando simulação...",
        "Falha crítica."
    ],
    'FR': [
        "Ton dos s'est cassé sous le poids...",
        "Le système t'a purifié.",
        "Tu étais trop lent...",
        "Réinitialisation de la simulation...",
        "Erreur critique."
    ],
    'IT': [
        "La tua schiena si è rotta sotto il peso...",
        "Il sistema ti ha purificato.",
        "Eri troppo lento...",
        "Reinizializzazione della simulazione...",
        "Errore critico."
    ]
}


# --- ACHIEVEMENTS & UNLOCKS ---
UNLOCKS = {
    'tiny_bag': {
        'threshold': 5000,
        'name': 'POCKET MONEY',
        'desc': 'Paid 5k Debt',
        'reward': 'Unlocks: Start with +$10 & Free Rune'
    },
    'blueprint': {
        'threshold': 10000,
        'name': 'ARCHITECT',
        'desc': 'Paid 10k Debt',
        'reward': 'Unlocks: Blueprint Totem (Mirror Blocks)'
    },
    'gamblers_coin': {
        'threshold': 25000,
        'name': 'HIGH ROLLER',
        'desc': 'Paid 25k Debt',
        'reward': 'Unlocks: Gambler Coin (Cheaper Rerolls)'
    },
    'obsidian_wall': {
        'threshold': 50000,
        'name': 'DEFENDER',
        'desc': 'Paid 50k Debt',
        'reward': 'Unlocks: Obsidian Wall (Slows Enemies)'
    },
    'divine_smite': {
        'threshold': 100000,
        'name': 'THE PURGER',
        'desc': 'Paid 100k Debt',
        'reward': 'Unlocks: Divine Smite (Right-Click Destroy)'
    },
    'midas_hand': {
        'threshold': 250000,
        'name': 'GOLDEN TOUCH',
        'desc': 'Paid 250k Debt',
        'reward': 'Unlocks: Midas Hand (Passive Income)'
    },
    'phoenix_feather': {
        'threshold': 500000,
        'name': 'IMMORTAL',
        'desc': 'Paid 500k Debt',
        'reward': 'Unlocks: Phoenix Feather (Revive 1x)'
    },
    'eye_of_ra': {
        'threshold': 1000000,
        'name': 'FREEDOM',
        'desc': 'Debt Cleared',
        'reward': 'Unlocks: Eye of Ra (1.5x Global Mult)'
    }
}