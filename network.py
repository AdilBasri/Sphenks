import threading
import requests
import json
from settings import LB_URL, LB_PUBLIC_KEY, LB_PRIVATE_KEY

class LeaderboardManager:
    def __init__(self):
        self.scores = []
        self.status = 'IDLE' 
        self.user_rank = '---'
        self.user_best = 0
        self.is_expanded = False
        
    def fetch_scores(self, local_user_data=None):
        if self.status == 'LOADING': return
        self.status = 'LOADING'
        t = threading.Thread(target=self._fetch_thread, args=(local_user_data,))
        t.daemon = True
        t.start()
        
    def _fetch_thread(self, local_user):
        try:
            resp = requests.get(f"{LB_URL}/{LB_PUBLIC_KEY}/json", timeout=5)
            
            if resp.status_code != 200:
                self.status = 'ERROR'
                return

            data = resp.json()
            server_scores = []
            
            if 'dreamlo' in data and 'leaderboard' in data['dreamlo']:
                entries = data['dreamlo']['leaderboard']
                if entries is None: # Liste boşsa
                    entries = {}
                
                if 'entry' in entries:
                    entry_list = entries['entry']
                    if isinstance(entry_list, dict): entry_list = [entry_list]
                else:
                    entry_list = []

                for entry in entry_list:
                    raw_name = entry['name']
                    score = int(entry['score'])
                    
                    # FORMAT DEĞİŞİKLİĞİ: Artık "-" (tire) ile ayırıyoruz
                    # Örnek: TR-Adil-1234
                    parts = raw_name.split('-')
                    
                    if len(parts) >= 3:
                        country = parts[0]
                        uid = parts[-1] # Son parça ID'dir
                        # İsim arada kalan her şey olabilir (İsimde tire varsa bozulmasın)
                        name = "-".join(parts[1:-1]) 
                    else:
                        country, name, uid = "UNK", raw_name, "????"

                    server_scores.append({'name': name, 'country': country, 'id': uid, 'score': score})

            self.scores = server_scores
            
            # Kendi sıranı bul
            self.user_rank = '---'
            if local_user and local_user.get('id'):
                for i, s in enumerate(self.scores):
                    s['rank'] = i + 1
                    if str(s['id']) == str(local_user['id']):
                        self.user_rank = s['rank']
                        self.user_best = s['score']
                        s['is_me'] = True
            
            self.status = 'READY'
            
        except Exception as e:
            print(f"Network Error: {e}")
            self.status = 'ERROR'
            
    def submit_score(self, username, score, country="TR", uid="0000"):
        print(f"\n[NETWORK DEBUG] submit_score ÇAĞRILDI!")
        print(f"   -> İsim: {username}, Puan: {score}, Ülke: {country}, ID: {uid}")
        
        # Thread yerine direkt çağırıyoruz (Oyun kapanmadan gitsin diye)
        self._submit_thread(username, score, country, uid)

    def _submit_thread(self, username, score, country, uid):
        try:
            # GÜVENLİK: İki nokta ve boşlukları temizle
            safe_username = str(username).replace("-", "_").replace(":", "").replace(" ", "_")
            safe_name = f"{country}-{safe_username}-{uid}"
            
            url = f"{LB_URL}/{LB_PRIVATE_KEY}/add/{safe_name}/{score}"
            
            print(f"   -> URL Oluşturuldu: {url}")
            print("   -> İstek gönderiliyor...")
            
            resp = requests.get(url, timeout=5)
            
            print(f"   -> SUNUCU CEVABI: {resp.status_code} - {resp.text}")
            
            if resp.status_code == 200:
                print("   -> [BAŞARILI] Skor Dreamlo'ya ulaştı.")
            else:
                print("   -> [HATA] Sunucu 200 dönmedi.")
                
        except Exception as e:
            print(f"   -> [KRİTİK HATA] Network hatası: {e}")