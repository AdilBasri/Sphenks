import threading
import time

class LeaderboardManager:
    def __init__(self):
        self.scores = []
        self.status = 'IDLE' 
        self.user_rank = '---'
        self.user_best = 0
        self.is_expanded = False
        
    def fetch_scores(self, local_user_data):
        """
        local_user_data: {'username': 'Adil', 'score': 2000, 'country': 'TR', 'id': '1234'}
        """
        if self.status == 'LOADING': return
        self.status = 'LOADING'
        
        # Thread başlatırken yerel veriyi de gönderelim
        t = threading.Thread(target=self._fetch_thread, args=(local_user_data,))
        t.daemon = True
        t.start()
        
    def _fetch_thread(self, local_user):
        try:
            time.sleep(0.5) # Gerçekçilik için minik gecikme
            
            # --- GERÇEKÇİ SABİT VERİLER ---
            # (İstediğin spesifik oyuncular)
            server_scores = [
                {'rank': 1, 'name': 'Fefe', 'id': '1905', 'score': 51054, 'country': 'TR'},
                {'rank': 2, 'name': 'BlackGhost', 'id': '0007', 'score': 36745, 'country': 'US'},
                {'rank': 3, 'name': 'OsiCardi', 'id': '1999', 'score': 33467, 'country': 'TR'},
                # Doldurmalık birkaç gerçekçi veri daha
                {'rank': 4, 'name': 'HansM', 'id': '4421', 'score': 28900, 'country': 'DE'},
                {'rank': 5, 'name': 'Sakura', 'id': '8888', 'score': 25400, 'country': 'JP'},
            ]
            
            # Yerel Oyuncuyu Listeye Dahil Etme Mantığı
            if local_user and local_user.get('username'):
                my_score = local_user['score']
                my_entry = {
                    'name': local_user['username'],
                    'id': local_user['id'],
                    'score': my_score,
                    'country': local_user['country'],
                    'is_me': True # Kendimiz olduğunu bilelim
                }
                server_scores.append(my_entry)
            
            # Puana göre sırala (Büyükten küçüğe)
            server_scores.sort(key=lambda x: x['score'], reverse=True)
            
            # Rankleri yeniden dağıt
            for i, s in enumerate(server_scores):
                s['rank'] = i + 1
                if s.get('is_me'):
                    self.user_rank = s['rank']
                    self.user_best = s['score']

            self.scores = server_scores
            self.status = 'READY'
            
        except Exception as e:
            print(f"Network Error: {e}")
            self.status = 'ERROR'
            
    def submit_score(self, name, score):
        # Burası ileride gerçek API'ye bağlanacak
        pass