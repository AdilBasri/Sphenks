# effects.py
import pygame
import random
from settings import *

class Shockwave:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.radius = 10
        self.width = 10
        self.alpha = 255

    def update(self):
        self.radius += 4        # Hızlı genişle
        self.width = max(1, self.width - 0.5) # Çizgi incelsin
        self.alpha -= 10        # Şeffaflaş
    
    def draw(self, surface):
        if self.alpha > 0 and self.width > 0:
            # Additive blending (Parlaklık hissi)
            s = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, int(self.alpha)), (self.radius, self.radius), int(self.radius), int(self.width))
            surface.blit(s, (self.x - self.radius, self.y - self.radius), special_flags=pygame.BLEND_RGBA_ADD)

class FloatingText:
    def __init__(self, x, y, text, color=(255, 255, 255), size_pop=True):
        self.x = x
        self.y = y
        self.text = str(text)
        self.color = color
        self.base_font = pygame.font.SysFont(FONT_NAME, 40, bold=True)
        self.life = 60
        self.y_offset = 0
        
        # Pop Efekti
        self.scale = 2.0 if size_pop else 1.0
        self.target_scale = 1.0

    def update(self):
        self.y_offset -= 1.5 
        self.life -= 1
        # Elastik küçülme animasyonu
        self.scale += (self.target_scale - self.scale) * 0.1

    def draw(self, surface):
        if self.life > 0:
            alpha = min(255, self.life * 5)
            s_font = pygame.font.SysFont(FONT_NAME, int(30 * self.scale), bold=True)
            text_surf = s_font.render(self.text, True, self.color)
            text_surf.set_alpha(alpha)
            
            # Gölge
            shadow_surf = s_font.render(self.text, True, (0,0,0))
            shadow_surf.set_alpha(alpha // 2)
            
            rect = text_surf.get_rect(center=(self.x, self.y + self.y_offset))
            surface.blit(shadow_surf, (rect.x + 2, rect.y + 2))
            surface.blit(text_surf, rect)

class Particle:
    def __init__(self, x, y, color, theme_style='glass'):
        self.x = x
        self.y = y
        self.color = color
        self.theme_style = theme_style
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-8, -2) # Yukarı doğru fırlasın
        self.gravity = 0.4
        self.life = random.randint(30, 60)
        self.size = random.randint(4, 8)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= 1
        self.size *= 0.95 

    def draw(self, surface):
        if self.life > 0:
            # Temaya göre şekil
            if self.theme_style == 'pixel':
                s = pygame.Surface((int(self.size)*2, int(self.size)*2), pygame.SRCALPHA)
                pygame.draw.rect(s, (*self.color, int(self.life*4)), (0,0, int(self.size)*2, int(self.size)*2))
                surface.blit(s, (self.x, self.y))
            else:
                s = pygame.Surface((int(self.size)*2, int(self.size)*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*self.color, min(255, self.life*5)), (int(self.size), int(self.size)), int(self.size))
                surface.blit(s, (self.x-self.size, self.y-self.size), special_flags=pygame.BLEND_RGBA_ADD)

class ParticleSystem:
    def __init__(self):
        self.particles = []
        self.texts = []
        self.shockwaves = []

    # HATA DÜZELTME: theme_style parametresi geri eklendi
    def create_explosion(self, x, y, color, count=10, theme_style='glass'):
        # 1. Şok Dalgası
        self.shockwaves.append(Shockwave(x, y, color))
        # 2. Partiküller
        for _ in range(count):
            self.particles.append(Particle(x, y, color, theme_style))
    
    def create_text(self, x, y, text, color=(255, 255, 255)):
        self.texts.append(FloatingText(x, y, text, color))

    def update(self):
        self.particles = [p for p in self.particles if p.life > 0]
        for p in self.particles: p.update()
        
        self.texts = [t for t in self.texts if t.life > 0]
        for t in self.texts: t.update()
        
        self.shockwaves = [s for s in self.shockwaves if s.alpha > 0]
        for s in self.shockwaves: s.update()

    def draw(self, surface):
        for s in self.shockwaves: s.draw(surface)
        for p in self.particles: p.draw(surface)
        for t in self.texts: t.draw(surface)