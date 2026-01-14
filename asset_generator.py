import pygame
import os
# Kendi dosyalarından verileri çekiyoruz
from runes import RUNE_DATA 

# Ayarlar
OUTPUT_SIZE = 512  # Çıktı görselinin boyutu (512x512 px)
SCALE_FACTOR = 10  # Oyundakinden kaç kat büyük olsun?
FONT_NAME = "Arial"

def export_runes():
    pygame.init()
    
    # Kayıt klasörü oluştur
    if not os.path.exists("exported_assets"):
        os.makedirs("exported_assets")
        
    print(f"Rünler dışa aktarılıyor... ({len(RUNE_DATA)} adet)")

    for key, data in RUNE_DATA.items():
        # 1. Şeffaf zemin oluştur
        surface = pygame.Surface((OUTPUT_SIZE, OUTPUT_SIZE), pygame.SRCALPHA)
        
        # Merkez noktası
        cx, cy = OUTPUT_SIZE // 2, OUTPUT_SIZE // 2
        
        # 2. Boyutları hesapla (Oyundaki değerlerin SCALE_FACTOR katı)
        # game.py'de radius yaklaşık 22-24 px civarındaydı
        radius = 22 * SCALE_FACTOR 
        border_width = 3 * SCALE_FACTOR
        font_size = 22 * SCALE_FACTOR

        # Renkleri al
        color = data['color']
        icon_char = data['icon']
        
        # --- ÇİZİM İŞLEMİ (Game.py mantığının aynısı ama devasa) ---
        
        # A. Arka Plan Dairesi (Koyu zemin)
        # game.py'de (20, 20, 30) kullanıyordun
        pygame.draw.circle(surface, (20, 20, 30), (cx, cy), radius + border_width) 

        # B. Renkli Çerçeve
        pygame.draw.circle(surface, color, (cx, cy), radius, border_width)
        
        # C. İkon Yazısı
        font = pygame.font.SysFont(FONT_NAME, font_size, bold=True)
        text_surf = font.render(icon_char, True, color) # Yazı rengi rün rengiyle aynı
        text_rect = text_surf.get_rect(center=(cx, cy))
        
        # Yazıyı merkeze koy
        surface.blit(text_surf, text_rect)
        
        # 3. Dosyayı Kaydet
        filename = f"exported_assets/{key}.png"
        pygame.image.save(surface, filename)
        print(f"Kaydedildi: {filename}")

    print("\n✅ Tüm rünler 'exported_assets' klasörüne kaydedildi!")
    pygame.quit()

if __name__ == "__main__":
    export_runes()