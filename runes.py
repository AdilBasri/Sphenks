# runes.py
import pygame

# Rün Veritabanı
RUNE_DATA = {
    'rune_fire': {
        'name': 'Magma Rune',
        'desc': '+4 Mult',
        'color': (255, 80, 0), # Turuncu
        'icon': 'M',
        'price': 4,
        'effect': 'add_mult',
        'value': 4
    },
    'rune_ice': {
        'name': 'Glacier Rune',
        'desc': '+20 Chips',
        'color': (100, 200, 255), # Buz Mavisi
        'icon': 'C',
        'price': 4,
        'effect': 'add_chips',
        'value': 20
    },
    'rune_void': {
        'name': 'Void Rune',
        'desc': 'x1.2 Mult',
        'color': (150, 50, 200), # Mor
        'icon': 'X',
        'price': 6,
        'effect': 'multiply_mult',
        'value': 1.2
    },
    'rune_gold': {
        'name': 'Midas Rune',
        'desc': '+$1 on clear',
        'color': (255, 215, 0), # Altın
        'icon': '$',
        'price': 5,
        'effect': 'add_money',
        'value': 1
    }
}

class Rune:
    def __init__(self, key):
        self.key = key
        data = RUNE_DATA[key]
        self.name = data['name']
        self.desc = data['desc']
        self.color = data['color']
        self.icon = data['icon']
        self.price = data['price']
        self.effect = data['effect']
        self.value = data['value']
        
        # UI Etkileşimi İçin
        self.rect = None
        self.dragging = False
        self.original_pos = (0, 0)
        self.x = 0
        self.y = 0