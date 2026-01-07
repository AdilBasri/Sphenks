# crt.py
import pygame
from settings import *

class CRTManager:
    """Simplified CRT/VCR effect manager - only applies visual filters to screen"""
    def __init__(self):
        # Effect settings
        self.aberration_timer = 0
        self.aberration_amount = 0
        
        # Create scanline overlay (lightweight visual effect)
        self.scanline_overlay = None
        self.create_scanlines()

    def create_scanlines(self):
        """Create scanline texture for CRT effect"""
        self.scanline_overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        self.scanline_overlay.fill((0, 0, 0, 0))
        
        # Horizontal scanlines for CRT effect
        for y in range(0, WINDOW_H, 2):
            pygame.draw.line(self.scanline_overlay, (0, 0, 0, 8), (0, y), (WINDOW_W, y))

    def trigger_aberration(self, amount=2, duration=4):
        """Trigger RGB aberration effect for short duration"""
        self.aberration_timer = duration
        self.aberration_amount = min(amount, 3)

    def apply_aberration(self, screen):
        """Apply chromatic aberration (RGB shift) to screen"""
        if self.aberration_timer > 0:
            self.aberration_timer -= 1
            offset = self.aberration_amount
            
            # Save original content
            original = screen.copy()
            
            # Create color-separated channels
            red_channel = original.copy()
            red_channel.fill((255, 0, 0), special_flags=pygame.BLEND_MULT)
            
            blue_channel = original.copy()
            blue_channel.fill((0, 0, 255), special_flags=pygame.BLEND_MULT)
            
            green_channel = original.copy()
            green_channel.fill((0, 255, 0), special_flags=pygame.BLEND_MULT)
            
            # Clear and reconstruct with offset
            screen.fill((0, 0, 0))
            screen.blit(red_channel, (-offset, 0), special_flags=pygame.BLEND_RGB_ADD)
            screen.blit(green_channel, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
            screen.blit(blue_channel, (offset, 0), special_flags=pygame.BLEND_RGB_ADD)

    def draw(self, screen):
        """Apply visual effects to screen (scanlines and aberration)"""
        # Apply aberration if active
        if self.aberration_timer > 0:
            self.apply_aberration(screen)
        
        # Apply scanlines overlay
        if self.scanline_overlay:
            screen.blit(self.scanline_overlay, (0, 0))
