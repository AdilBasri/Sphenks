# totems.py
from settings import *

class Totem:
    def __init__(self, key, data):
        self.key = key
        self.name = data['name']
        self.price = data['price']
        self.desc = data['desc'] # description yerine desc kullanıyoruz
        self.trigger_type = data['trigger'] # 'on_score', 'on_clear', 'passive'
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
            # Son koyulan bloğun koordinatlarına bak
            if game_state.held_block: # Eğer o an bırakılan bloksa
                # Bu kontrol biraz zor çünkü blok grid'e çoktan girdi.
                # Grid üzerindeki son işlem yapılan yerlere bakabiliriz
                # Basit çözüm: Eğer son yerleştirme kenara değdiyse (game.py'de flag tutabiliriz)
                # Şimdilik grid boyutuna göre tahmini bir kontrol yerine
                # game_state.last_grid_pos bilgisini kullanalım
                r, c = game_state.last_grid_pos
                # Bloğun boyutu da önemli ama basitçe başlangıç noktası kenar mı?
                # Veya daha hassas: Bloğun herhangi bir parçası kenara değdi mi?
                # Bunu game.py içinde hesaplayıp 'is_edge_placement' diye göndermek daha sağlıklı.
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
    def apply_passive(key, game_state):
        """
        Sürekli aktif olanlar (Örn: Recycler)
        Genelde game.py içinde 'if has_totem' diye kontrol edilir.
        """
        pass