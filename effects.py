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


class FlashParticle:
    """A quick white flash circle that shrinks rapidly to simulate impact frames."""
    def __init__(self, x, y, size=40):
        self.x = x
        self.y = y
        self.size = size

    def update(self):
        self.size -= 5

    def draw(self, surface):
        if self.size > 0:
            try:
                pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), int(self.size))
            except Exception:
                pass

class HypeText:
    def __init__(self, x, y, text, color=(255, 255, 255), font_path=None):
        self.x = x
        self.y = y
        self.text = str(text)
        self.color = color
        # Daha büyük ve kalın font
        try:
            if font_path:
                self.font = pygame.font.Font(font_path, 50)
            else:
                raise FileNotFoundError
        except FileNotFoundError:
            self.font = pygame.font.SysFont(FONT_NAME, 50, bold=True)
        self.font.set_bold(True)
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

class PyroBackground:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        try:
            self.font = pygame.font.SysFont("Courier", 16, bold=True)
        except Exception:
            self.font = pygame.font.Font(None, 16)
        
        # 1. Digital Streams (Matrix Rain moving UP)
        self.streams = []
        self.columns = max(1, int(w / 20))
        for i in range(self.columns):
            self.streams.append({
                'x': i * 20,
                'y': random.randint(-500, h),
                'speed': random.uniform(2.0, 5.0),
                'chars': [str(random.randint(0, 1)) for _ in range(random.randint(5, 15))],
                'alpha': random.randint(50, 150) # Faint visibility
            })
            
        # 2. Vignette Surface (Pre-calculated gradient)
        self.vignette = pygame.Surface((w, h), pygame.SRCALPHA)
        self._create_radial_gradient()
        
        self.pulse_timer = 0.0
        # Shake support for compatibility with existing calls
        self.shake_timer = 0
        self.shake_magnitude = 0

    def _create_radial_gradient(self):
        # Create a transparent center and dark red corners
        center = (self.w // 2, self.h // 2)
        max_dist = math.hypot(center[0], center[1])
        for y in range(self.h):
            for x in range(self.w):
                dist = math.hypot(x - center[0], y - center[1])
                # Normalize distance (0.0 center, 1.0 corners)
                norm = dist / (max_dist * 0.7)
                if norm > 1: norm = 1
                if norm < 0.4: # Safe zone in middle
                    alpha = 0
                else:
                    # Smooth step for edges
                    alpha = int((norm - 0.4) * 2 * 255)
                if alpha > 0:
                    # Deep Dark Red
                    try:
                        self.vignette.set_at((x, y), (50, 0, 10, min(255, alpha)))
                    except Exception:
                        # set_at can be slow; ignore failures on systems without per-pixel alpha support
                        pass

    def update(self):
        self.pulse_timer += 0.05
        
        # Move streams up
        for s in self.streams:
            s['y'] -= s['speed']
            # Reset if fully off screen
            if s['y'] < -300:
                s['y'] = self.h + random.randint(10, 100)
                s['speed'] = random.uniform(2.0, 5.0)
                # Randomize content occasionally
                if random.random() < 0.1:
                    s['chars'] = [str(random.randint(0, 1)) for _ in range(random.randint(5, 15))]

    def trigger_shake(self, duration=15, magnitude=5):
        self.shake_timer = duration
        self.shake_magnitude = magnitude

    def get_shake_offset(self):
        if self.shake_timer > 0:
            self.shake_timer -= 1
            offset_x = random.randint(-self.shake_magnitude, self.shake_magnitude)
            offset_y = random.randint(-self.shake_magnitude, self.shake_magnitude)
            return offset_x, offset_y
        return 0, 0

    def draw(self, surface):
        # 1. Draw Digital Streams
        for s in self.streams:
            for i, char in enumerate(s['chars']):
                # Fade out tail
                alpha = s['alpha'] - (i * 10)
                if alpha <= 0: continue
                txt = self.font.render(char, True, (200, 50, 50)) # Bright Red Text
                try:
                    txt.set_alpha(alpha)
                except Exception:
                    pass
                surface.blit(txt, (s['x'], s['y'] + (i * 14)))
        # 2. Draw Pulsing Vignette
        # Sine wave breathing: 0.8 to 1.2 scale of alpha
        pulse = (math.sin(self.pulse_timer) + 1) * 0.5 # 0.0 to 1.0
        current_alpha = 150 + int(pulse * 105) # 150 to 255
        # Draw cached vignette
        try:
            surface.blit(self.vignette, (0,0))
        except Exception:
            pass
        # Dynamic RED flash overlay at peaks
        if pulse > 0.8: # Peak of breath -> Danger Flash
            flash = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            flash.fill((255, 0, 0, int((pulse-0.8)*5 * 50)))
            surface.blit(flash, (0,0))

class ParticleSystem:
    def __init__(self):
        self.particles = []
        self.texts = []
        self.atmosphere = PyroBackground(VIRTUAL_W, VIRTUAL_H) # Yeni
        self.flashes = []

    def create_explosion(self, x, y, count=20):
        # Impact flash for explosion
        try:
            self.create_flash(x, y)
        except Exception:
            pass
        for _ in range(count):
            self.particles.append(Confetti(x, y))

    def create_flash(self, x, y, intensity=1):
        '''Create 1 or 2 flash particles based on intensity (1 = small, 2 = bigger).'''
        num = 1 if intensity <= 1 else 2
        for i in range(num):
            size = int(30 * intensity * (1.0 + (0.3 * i)))
            self.flashes.append(FlashParticle(x, y, size=size))
    
    def create_text(self, x, y, text, color=(255, 255, 255), font_path=None):
        self.texts.append(HypeText(x, y, text, color, font_path=font_path))

    def update(self):
        self.particles = [p for p in self.particles if p.life > 0]
        for p in self.particles: p.update()
        
        self.texts = [t for t in self.texts if t.life > 0]
        for t in self.texts: t.update()
        
        # Update flashes (shrink and remove when done)
        new_flashes = []
        for f in self.flashes:
            f.update()
            if getattr(f, 'size', 0) > 0:
                new_flashes.append(f)
        self.flashes = new_flashes

    def draw(self, surface):
        for p in self.particles: p.draw(surface)
        for t in self.texts: t.draw(surface)
        # Draw flashes on top for impact
        for f in self.flashes:
            f.draw(surface)