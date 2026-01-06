# totems.py
import random
from settings import *

class Totem:
    def __init__(self, key, data):
        self.key = key
        self.name = data['name']
        self.price = data['price']
        self.desc = data['desc'] 
        self.trigger_type = data['trigger'] 
        self.rarity = data['rarity']
        self.rect = None 

class TotemLogic:
    @staticmethod
    def apply_on_score(key, current_mult, current_bonus, game_state):
        new_mult = current_mult
        new_bonus = current_bonus
        
        # --- MEVCUT TOTEMLER ---
        if key == 'sniper':
            if getattr(game_state, 'is_edge_placement', False):
                new_mult += 1.0 
        elif key == 'void_walker':
            if game_state.void_count < 5:
                new_mult += 2.0 
        elif key == 'blood_pact':
            new_mult += 3.0 
        elif key == 'ruby_lens':
            last_tag = getattr(game_state, 'last_placed_block_tag', 'NONE')
            if last_tag == 'RED': new_mult += 2.0
        elif key == 'sapphire_lens':
            last_tag = getattr(game_state, 'last_placed_block_tag', 'NONE')
            if last_tag == 'BLUE': new_mult += 2.0
            
        # --- OMEGA TOTEMLER ---
        elif key == 'dark_matter':
            new_mult += 9.0 # x10 Olması için +9 (Base 1 + 9 = 10)
            
        return new_mult, new_bonus

    @staticmethod
    def apply_on_clear(key, game_state, cleared_cells, stones_destroyed):
        money_gain = 0
        
        if key == 'miner':
            if stones_destroyed > 0: money_gain += stones_destroyed * 1
        elif key == 'midas':
            if cleared_cells > 0: money_gain += cleared_cells * 0.5
            
        # --- OMEGA TOTEMLER ---
        elif key == 'infinity_stone':
            # Hem para veriyor hem de o anki çarpanı artırıyor (Game loop içinde mult işlenir)
            # Burada sadece parayı döndürüyoruz, mult etkisi için game.py'de özel kontrol yapılabilir 
            # veya basitleştirmek için sadece para:
            if cleared_cells > 0:
                money_gain += 5 # Her patlatmada sabit $5
                
        return money_gain

    @staticmethod
    def apply_round_end(key, game_state):
        money_gain = 0
        desc = ""
        
        if key == 'savings_bond':
            interest = int(game_state.credits * 0.20)
            if interest > 0:
                money_gain = interest
                desc = f"+${interest} Interest"
        
        # --- OMEGA TOTEMLER ---
        elif key == 'chronos':
            interest = int(game_state.credits * 0.50) # %50 Faiz
            if interest > 0:
                money_gain = interest
                desc = f"+${interest} MAX Interest"
        
        return money_gain, desc

    @staticmethod
    def check_gambling(key, game_state):
        if key == 'gamblers_dice':
            if random.random() < 0.25:  
                if game_state.held_block:
                    cells = sum(r.count(1) for r in game_state.held_block.matrix)
                    base_points = cells * SCORE_PER_BLOCK
                    bonus_score = base_points * 5
                    return True, bonus_score
        return False, 0

    @staticmethod
    def apply_on_place(key, game_state):
        money_gain = 0
        if key == 'golden_ticket':
            last_tag = getattr(game_state, 'last_placed_block_tag', 'NONE')
            if last_tag == 'GOLD':
                money_gain = 3
        return money_gain

    @staticmethod
    def apply_passive(key, game_state):
        pass