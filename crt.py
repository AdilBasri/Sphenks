# crt.py
import pygame
from settings import *

class CRTManager:
    def __init__(self):
        # --- EFEKT AYARLARI ---
        self.aberration_timer = 0
        self.aberration_amount = 0
        
        # Pixel Mesh overlay (Sony Trinitron benzeri)
        self.mesh_overlay = pygame.Surface((VIRTUAL_W, VIRTUAL_H), pygame.SRCALPHA)
        self.create_pixel_mesh()

    def create_pixel_mesh(self):
        """Sony Trinitron benzeri yüksek çözünürlüklü piksel mesh efekti oluşturur.
        Görüntüyü bulanıklaştırmadan pikseller arası doku hissi verir."""
        
        # Mesh yüzeyini siyah ile doldur (tam şeffaf başla)
        self.mesh_overlay.fill((0, 0, 0, 0))
        
        # Dikey çizgiler - her 3 pikselde bir (çok silik)
        for x in range(0, VIRTUAL_W, 3):
            pygame.draw.line(self.mesh_overlay, (0, 0, 0, 12), (x, 0), (x, VIRTUAL_H))
        
        # Yatay çizgiler - her 2 pikselde bir (çok silik)
        for y in range(0, VIRTUAL_H, 2):
            pygame.draw.line(self.mesh_overlay, (0, 0, 0, 8), (0, y), (VIRTUAL_W, y))

    def trigger_aberration(self, amount=2, duration=4):
        """Patlama anında hafif RGB kayması efektini başlatır.
        Sadece renk kanallarını kaydırır, ölçekleme veya bulanıklık YOKTUR."""
        self.aberration_timer = duration
        self.aberration_amount = min(amount, 3)  # Maksimum 3 piksel kayma

    def apply_aberration(self, screen):
        """Kromatik Sapma - Sadece RGB kanallarını hafifçe kaydırır.
        Ölçekleme veya bulanıklık uygulamaz."""
        if self.aberration_timer > 0:
            self.aberration_timer -= 1
            offset = self.aberration_amount
            
            # Orijinal görüntüyü sakla
            original = screen.copy()
            
            # Kırmızı Kanal
            red_channel = original.copy()
            red_channel.fill((255, 0, 0), special_flags=pygame.BLEND_MULT)
            
            # Mavi Kanal
            blue_channel = original.copy()
            blue_channel.fill((0, 0, 255), special_flags=pygame.BLEND_MULT)
            
            # Yeşil Kanal (Kayma yok, merkez)
            green_channel = original.copy()
            green_channel.fill((0, 255, 0), special_flags=pygame.BLEND_MULT)
            
            # Ekranı temizle
            screen.fill((0, 0, 0))
            
            # Kaydırma işlemi - Sadece hafif yatay kayma
            screen.blit(red_channel, (-offset, 0), special_flags=pygame.BLEND_RGB_ADD)
            screen.blit(green_channel, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
            screen.blit(blue_channel, (offset, 0), special_flags=pygame.BLEND_RGB_ADD)

    def draw(self, screen):
        # 1. Aberration (Sadece patlamada anlık devreye girer)
        if self.aberration_timer > 0:
            self.apply_aberration(screen)
        
        # 2. Pixel Mesh (SRCALPHA overlay - şeffaf alanlar görüntüyü etkilemez)
        screen.blit(self.mesh_overlay, (0, 0))