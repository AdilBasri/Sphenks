import threading
import time

class LeaderboardManager:
    def __init__(self):
        self.scores = []
        self.status = 'IDLE' 
        self.user_rank = '---'
        self.user_best = 0
        self.is_expanded = False # Widget açık mı?
        
    def fetch_scores(self):
        if self.status == 'LOADING': return
        self.status = 'LOADING'
        t = threading.Thread(target=self._fetch_thread)
        t.daemon = True
        t.start()
        
    def _fetch_thread(self):
        try:
            time.sleep(1) # Gecikme simülasyonu
            # DUMMY VERİ (Şimdilik)
            self.scores = [
                {'rank': 1, 'name': 'Firavun', 'score': 999999, 'country': 'EG'},
                {'rank': 2, 'name': 'Adil', 'score': 150000, 'country': 'TR'},
                {'rank': 3, 'name': 'PlayerX', 'score': 120000, 'country': 'US'},
                {'rank': 4, 'name': 'Sphenks', 'score': 98000, 'country': 'DE'},
                {'rank': 1500, 'name': 'SEN', 'score': 24540, 'country': 'TR'},
            ]
            self.status = 'READY'
            # Seni bulalım
            for s in self.scores:
                if s['name'] == 'SEN':
                    self.user_rank = s['rank']
                    self.user_best = s['score']
        except Exception as e:
            print(f"Network Error: {e}")
            self.status = 'ERROR'
            
    def submit_score(self, name, score):
        print(f"SKOR GÖNDERİLDİ: {name} -> {score}")