# crt.py
import pygame
from settings import *

class CRTManager:
    def __init__(self):
        # --- EFEKT AYARLARI ---
        self.aberration_timer = 0
        self.aberration_amount = 0
        
        # Vignette ve Scanlines için overlay
        self.overlay = pygame.Surface((VIRTUAL_W, VIRTUAL_H), pygame.SRCALPHA)
        self.create_crt_overlay()

    def create_crt_overlay(self):
        """Scanlines ve Vignette oluşturur (Çok daha hafifletildi)"""
        # 1. Scanlines (Yatay Çizgiler) - Çok silik (Alpha 5)
        # Sadece çok hafif bir doku hissi verir, görüntüyü bozmaz.
        for y in range(0, VIRTUAL_H, 2):
            pygame.draw.line(self.overlay, (0, 0, 0, 5), (0, y), (VIRTUAL_W, y))
        
        # 2. Vignette (Köşe Karartma) - Daha yumuşak
        rect = self.overlay.get_rect()
        pygame.draw.rect(self.overlay, (0, 0, 0, 10), rect, 8) 
        pygame.draw.rect(self.overlay, (0, 0, 0, 30), rect, 2) 

        # Köşe maskeleri (Oval hissi)
        corner_size = 15
        color = (0, 0, 0)
        points = [
            [(0,0), (corner_size,0), (0,corner_size)],
            [(VIRTUAL_W,0), (VIRTUAL_W-corner_size,0), (VIRTUAL_W,corner_size)],
            [(0,VIRTUAL_H), (0,VIRTUAL_H-corner_size), (corner_size,VIRTUAL_H)],
            [(VIRTUAL_W,VIRTUAL_H), (VIRTUAL_W,VIRTUAL_H-corner_size), (VIRTUAL_W-corner_size,VIRTUAL_H)]
        ]
        for p in points:
            pygame.draw.polygon(self.overlay, color, p)

    def trigger_aberration(self, amount=2, duration=4):
        """Darbe anında renk kayması efektini başlatır (Kısa süreli)"""
        self.aberration_timer = duration
        self.aberration_amount = amount

    def apply_aberration(self, screen):
        """Kromatik Sapma (Sadece tetiklendiğinde çalışır)"""
        if self.aberration_timer > 0:
            self.aberration_timer -= 1
            offset = self.aberration_amount
            
            # Kırmızı Kanal
            red_channel = screen.copy()
            red_channel.fill((255, 0, 0), special_flags=pygame.BLEND_MULT)
            
            # Mavi Kanal
            blue_channel = screen.copy()
            blue_channel.fill((0, 0, 255), special_flags=pygame.BLEND_MULT)
            
            # Yeşil Kanal
            green_channel = screen.copy()
            green_channel.fill((0, 255, 0), special_flags=pygame.BLEND_MULT)
            
            screen.fill((0, 0, 0))
            
            # Kaydırma işlemi
            screen.blit(red_channel, (-offset, 0), special_flags=pygame.BLEND_RGB_ADD)
            screen.blit(green_channel, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
            screen.blit(blue_channel, (offset, 0), special_flags=pygame.BLEND_RGB_ADD)

    def draw(self, screen):
        # 1. Bloom KALDIRILDI (Netlik için)
        
        # 2. Aberration (Sadece patlamada anlık devreye girer)
        if self.aberration_timer > 0:
            self.apply_aberration(screen)
            
        # 3. CRT Çizgileri (Çok silik statik overlay)
        screen.blit(self.overlay, (0, 0))