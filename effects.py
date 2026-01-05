# effects.py
import pygame
import random
import math
from settings import *

class Confetti:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = random.choice(CONFETTI_COLORS)
        
        # Fizik
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(3, 10)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - 5 # Yukarı fırlama
        self.gravity = 0.4
        self.friction = 0.95
        
        # Şekil
        self.size = random.randint(4, 8)
        self.angle = random.randint(0, 360)
        self.spin_speed = random.uniform(-15, 15)
        self.life = 255
        self.decay = random.randint(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.vx *= self.friction
        self.vy *= self.friction
        
        self.angle += self.spin_speed
        self.life -= self.decay

    def draw(self, surface):
        if self.life > 0:
            # Dönen kare çizimi
            s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.rect(s, (*self.color, int(self.life)), (0, 0, self.size, self.size))
            
            # Döndür
            rotated = pygame.transform.rotate(s, self.angle)
            rect = rotated.get_rect(center=(self.x, self.y))
            surface.blit(rotated, rect)

class HypeText:
    def __init__(self, x, y, text, color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.text = str(text)
        self.color = color
        # Daha büyük ve kalın font
        self.font = pygame.font.SysFont(FONT_NAME, 50, bold=True)
        self.life = 100
        self.scale = 0.1 # Küçük başla
        self.target_scale = 1.2 # Büyü (Pop)

    def update(self):
        self.life -= 1.5
        # Elastik Büyüme Efekti (Lerp)
        self.scale += (self.target_scale - self.scale) * 0.2
        if self.scale >= 1.1: self.target_scale = 1.0 # Biraz küçül (Bounce)
        
        self.y -= 0.5 # Yavaşça yukarı süzül

    def draw(self, surface):
        if self.life > 0:
            text_surf = self.font.render(self.text, True, self.color)
            # Gölge
            shadow_surf = self.font.render(self.text, True, (0,0,0))
            
            # Ölçeklendirme
            w = int(text_surf.get_width() * self.scale)
            h = int(text_surf.get_height() * self.scale)
            
            if w > 0 and h > 0:
                scaled_text = pygame.transform.scale(text_surf, (w, h))
                scaled_shadow = pygame.transform.scale(shadow_surf, (w, h))
                
                # Alpha (Solma)
                alpha = min(255, int(self.life * 3))
                scaled_text.set_alpha(alpha)
                scaled_shadow.set_alpha(alpha)
                
                rect = scaled_text.get_rect(center=(self.x, self.y))
                # Gölgeyi hafif kaydırarak çiz
                surface.blit(scaled_shadow, (rect.x + 3, rect.y + 3))
                surface.blit(scaled_text, rect)

class ParticleSystem:
    def __init__(self):
        self.particles = []
        self.texts = []

    def create_explosion(self, x, y, count=20):
        # Konfeti Patlaması
        for _ in range(count):
            self.particles.append(Confetti(x, y))
    
    def create_text(self, x, y, text, color=(255, 255, 255)):
        self.texts.append(HypeText(x, y, text, color))

    def update(self):
        self.particles = [p for p in self.particles if p.life > 0]
        for p in self.particles: p.update()
        
        self.texts = [t for t in self.texts if t.life > 0]
        for t in self.texts: t.update()

    def draw(self, surface):
        for p in self.particles: p.draw(surface)
        for t in self.texts: t.draw(surface)