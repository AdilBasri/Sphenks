import pygame
import random
from settings import *

class Particle:
    def __init__(self, x, y, color, theme_style='glass'):
        self.x = x
        self.y = y
        self.color = color
        self.theme_style = theme_style
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-8, -2)
        self.gravity = 0.5
        self.size = random.randint(4, 10)
        self.life = 255
        self.decay = random.randint(8, 15)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= self.decay
        self.size -= 0.1

    def draw(self, surface):
        if self.life > 0 and self.size > 0:
            # Temaya göre şekil
            if self.theme_style == 'pixel':
                # Retro: Kare Partikül
                s = pygame.Surface((int(self.size)*2, int(self.size)*2), pygame.SRCALPHA)
                pygame.draw.rect(s, (*self.color, int(self.life)), (0,0, int(self.size)*2, int(self.size)*2))
            else:
                # Neon/Candy: Yuvarlak
                s = pygame.Surface((int(self.size)*2, int(self.size)*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*self.color, int(self.life)), (int(self.size), int(self.size)), int(self.size))
            
            surface.blit(s, (self.x, self.y))

class FloatingText:
    def __init__(self, x, y, text, color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.text = str(text)
        self.color = color
        self.font = pygame.font.SysFont(FONT_NAME, 30, bold=True)
        self.life = 255
        self.y_offset = 0
        self.scale = 1.0 # Büyüyüp küçülme efekti için

    def update(self):
        self.y_offset -= 1.0
        self.life -= 4
        if self.life > 200: self.scale += 0.05 # Patlayarak çıkış
        else: self.scale = max(0, self.scale - 0.02)

    def draw(self, surface):
        if self.life > 0:
            text_surf = self.font.render(self.text, True, self.color)
            # Scale işlemi
            w = int(text_surf.get_width() * self.scale)
            h = int(text_surf.get_height() * self.scale)
            if w > 0 and h > 0:
                text_surf = pygame.transform.scale(text_surf, (w, h))
                text_surf.set_alpha(self.life)
                surface.blit(text_surf, (self.x - w//2, self.y + self.y_offset))

class TrailParticle:
    def __init__(self, rect, color, life=100):
        self.rect = rect.copy()
        self.color = color
        self.life = life
        self.max_life = life

    def update(self):
        self.life -= 10 

    def draw(self, surface):
        if self.life > 0:
            alpha = int((self.life / self.max_life) * 100)
            s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            pygame.draw.rect(s, (*self.color, alpha), (0, 0, self.rect.width, self.rect.height), border_radius=8)
            surface.blit(s, self.rect.topleft)

class ParticleSystem:
    def __init__(self):
        self.particles = []
        self.texts = []
        self.trails = []

    def create_explosion(self, x, y, color, count=10, theme_style='glass'):
        for _ in range(count):
            self.particles.append(Particle(x, y, color, theme_style))
    
    def create_text(self, x, y, text, color=(255, 255, 255)):
        self.texts.append(FloatingText(x, y, text, color))

    def create_trail(self, block):
        for r in range(block.rows):
            for c in range(block.cols):
                if block.matrix[r][c] == 1:
                    bx = block.rect.x + (c * block.width // block.cols)
                    by = block.rect.y + (r * block.height // block.rows)
                    cell_w = block.width // block.cols
                    gap = int(cell_w * 0.1)
                    rect = pygame.Rect(bx + gap//2, by + gap//2, cell_w - gap, cell_w - gap)
                    self.trails.append(TrailParticle(rect, block.color))

    def update(self):
        self.particles = [p for p in self.particles if p.life > 0]
        for p in self.particles: p.update()
        self.texts = [t for t in self.texts if t.life > 0]
        for t in self.texts: t.update()
        self.trails = [t for t in self.trails if t.life > 0]
        for t in self.trails: t.update()

    def draw(self, surface):
        for t in self.trails: t.draw(surface)
        for p in self.particles: p.draw(surface)
        for t in self.texts: t.draw(surface)

def render_with_glitch(screen, shake_intensity):
    if shake_intensity <= 2: return 
    offset = int(shake_intensity * 0.5)
    display_surf = screen.copy()
    screen.fill((0,0,0)) 
    screen.blit(display_surf, (-offset, -offset), special_flags=pygame.BLEND_RGBA_ADD)
    glitch_surf = display_surf.copy()
    glitch_surf.fill((0, 255, 255), special_flags=pygame.BLEND_RGBA_MULT) 
    screen.blit(glitch_surf, (offset, offset), special_flags=pygame.BLEND_RGBA_ADD)
    glitch_surf2 = display_surf.copy()
    glitch_surf2.fill((255, 0, 0), special_flags=pygame.BLEND_RGBA_MULT) 
    screen.blit(glitch_surf2, (-offset, -offset), special_flags=pygame.BLEND_RGBA_ADD)