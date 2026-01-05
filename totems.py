# totems.py
import random
from settings import *

class Totem:
    def __init__(self, key, data):
        self.key = key
        self.name = data['name']
        self.price = data['price']
        self.desc = data['desc'] # description yerine desc kullanıyoruz
        self.trigger_type = data['trigger'] # 'on_score', 'on_clear', 'passive', 'on_round_end', 'on_place'
        self.rarity = data['rarity']
        self.rect = None # UI için

class TotemLogic:
    @staticmethod
    def apply_on_score(key, current_mult, current_bonus, game_state):
        """
        Skor hesaplama anında (Time Stop) çalışan jokerler.
        """
        new_mult = current_mult
        new_bonus = current_bonus
        triggered = False # Görsel efekt için (İlerde eklenebilir)

        # 1. SNIPER: Kenarlara temas eden blok varsa x2
        if key == 'sniper':
            # is_edge_placement flag'ini game.py içinde hesaplayıp 'is_edge_placement' diye göndermek daha sağlıklı.
            if getattr(game_state, 'is_edge_placement', False):
                new_mult += 1.0 # x2 olması için +1 ekliyoruz (Base 1.0 + 1.0 = 2.0)
        
        # 2. VOID WALKER: Void < 5 ise x3
        elif key == 'void_walker':
            if game_state.void_count < 5:
                new_mult += 2.0 # x3 olması için +2 ekle
        
        # 3. BLOOD PACT: x4 Mult ama -1 Void
        elif key == 'blood_pact':
            new_mult += 3.0 # x4 olması için +3 ekle
            # Void eksiltme işlemi game.py'de puan eklendikten sonra yapılır
            # Burası sadece hesaplama.
        
        # 4. RUBY LENS: RED bloklar için +2 Mult
        elif key == 'ruby_lens':
            last_tag = getattr(game_state, 'last_placed_block_tag', 'NONE')
            if last_tag == 'RED':
                new_mult += 2.0
        
        # 5. SAPPHIRE LENS: BLUE bloklar için +2 Mult
        elif key == 'sapphire_lens':
            last_tag = getattr(game_state, 'last_placed_block_tag', 'NONE')
            if last_tag == 'BLUE':
                new_mult += 2.0
            
        return new_mult, new_bonus

    @staticmethod
    def apply_on_clear(key, game_state, cleared_cells, stones_destroyed):
        """
        Patlama anında (Para/Puan verme) çalışanlar.
        """
        money_gain = 0
        
        # 1. MINER: Taş başına $1
        if key == 'miner':
            if stones_destroyed > 0:
                money_gain += stones_destroyed * 1
        
        # 2. MIDAS: Patlayan her blok karesi için $0.5
        elif key == 'midas':
            if cleared_cells > 0:
                money_gain += cleared_cells * 0.5
                
        return money_gain

    @staticmethod
    def apply_round_end(key, game_state):
        """
        Round sonunda çalışan ekonomi totemleri.
        Returns: (money_gain, description_text)
        """
        money_gain = 0
        desc = ""
        
        # SAVINGS BOND: Mevcut kredinin %20'si kadar faiz
        if key == 'savings_bond':
            interest = int(game_state.credits * 0.20)
            if interest > 0:
                money_gain = interest
                desc = f"+${interest} Interest"
        
        return money_gain, desc

    @staticmethod
    def check_gambling(key, game_state):
        """
        Kumar totemi kontrolü.
        Returns: (should_destroy, bonus_score)
        GAMBLER'S DICE: %25 şansla blok yok edilir ve x5 skor kazanılır.
        """
        if key == 'gamblers_dice':
            if random.random() < 0.25:  # %25 şans
                # Bloğun baz puanını hesapla ve x5 yap
                if game_state.held_block:
                    cells = sum(r.count(1) for r in game_state.held_block.matrix)
                    base_points = cells * SCORE_PER_BLOCK
                    bonus_score = base_points * 5
                    return True, bonus_score
        return False, 0

    @staticmethod
    def apply_on_place(key, game_state):
        """
        Blok yerleştirme anında çalışanlar (renk sinerji ödülleri).
        Returns: money_gain
        """
        money_gain = 0
        
        # GOLDEN TICKET: GOLD blok yerleştirildiğinde +$3
        if key == 'golden_ticket':
            last_tag = getattr(game_state, 'last_placed_block_tag', 'NONE')
            if last_tag == 'GOLD':
                money_gain = 3
        
        return money_gain

    @staticmethod
    def apply_passive(key, game_state):
        """
        Sürekli aktif olanlar (Örn: Recycler)
        Genelde game.py içinde 'if has_totem' diye kontrol edilir.
        """
        pass