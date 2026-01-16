# debug_lb.py
import requests
import sys

print("--- LEADERBOARD TANI TESTİ ---")

# 1. settings.py'dan verileri çekmeyi dene
try:
    from settings import LB_PUBLIC_KEY, LB_PRIVATE_KEY, LB_URL
    print(f"[OK] settings.py bulundu.")
    print(f"     Public Key: {LB_PUBLIC_KEY[:5]}...")
except ImportError:
    print("[HATA] settings.py içinde LB_PUBLIC_KEY bulunamadı!")
    print("       Lütfen settings.py dosyasının en altına kodları eklediğinden emin ol.")
    sys.exit()

# 2. Sunucuya Bağlanma Testi (Okuma)
print("\n[INFO] Sunucuya bağlanılıyor (Veri Çekme)...")
try:
    url = f"{LB_URL}/{LB_PUBLIC_KEY}/json"
    print(f"       URL deneniyor: {url}")
    resp = requests.get(url, timeout=10)
    
    if resp.status_code == 200:
        print(f"[OK] Bağlantı Başarılı! (Kod: 200)")
        data = resp.json()
        print(f"     Gelen Veri: {str(data)[:100]}...") # Verinin başını göster
    else:
        print(f"[HATA] Sunucu Hatası: {resp.status_code}")

except Exception as e:
    print(f"[KRİTİK HATA] Bağlantı kurulamadı: {e}")
    print("       İnternet bağlantını veya güvenlik duvarını kontrol et.")

# 3. Yazma Testi
print("\n[INFO] Yazma Testi (Skor Gönderme)...")
try:
    test_url = f"{LB_URL}/{LB_PRIVATE_KEY}/add/TR-Debug_Test-000/1"
    resp = requests.get(test_url, timeout=10)
    if resp.text.strip() == "OK":
        print("[OK] Yazma Başarılı!")
    else:
        print(f"[HATA] Yazma Başarısız. Cevap: {resp.text}")
except Exception as e:
    print(f"[HATA] Yazma sırasında hata: {e}")

input("\nÇıkmak için Enter'a bas...")