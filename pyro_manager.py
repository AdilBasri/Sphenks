"""Pyro Mode manager: block placement + enemy shooting."""

import pygame
import random
import math

from settings import (
    VIRTUAL_W,
    VIRTUAL_H,
    COLOR_1BIT_BG,
    COLOR_1BIT_FG,
    COLOR_1BIT_ENEMY,
    COLOR_PYRO_ACCENT,
    PYRO_ENEMY_SPEED,
    PYRO_SPAWN_DELAY,
    resource_path,
)
from block import Block, SHAPES


class PyroManager:
    def __init__(self, game):
        self.game = game

        # Grid configuration
        self.grid_size = 7
        self.cell_size = 50
        grid_w = self.grid_size * self.cell_size
        grid_h = self.grid_size * self.cell_size
        self.offset_x = (VIRTUAL_W - grid_w) // 2
        self.offset_y = (VIRTUAL_H - grid_h) // 2

        # Mask and data
        self.level_mask = self._create_pyramid_mask()
        self.grid_data = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]

        # Core at geometric center of grid (row 3, col 3 in 0-indexed 7x7)
        center_idx = self.grid_size // 2
        self.core_pos = (
            self.offset_x + center_idx * self.cell_size + self.cell_size // 2,
            self.offset_y + center_idx * self.cell_size + self.cell_size // 2,
        )

        # Enemies
        self.enemies = []
        self.spawn_timer = 0.0
        self.spawn_interval = PYRO_SPAWN_DELAY / 1000.0

        # Input / interaction
        self.hand = []
        self.dragging_block = None
        self.is_aiming = False
        self.prev_left = False
        self.prev_right = False

        # Sprites
        self.enemy_img = None  # Enemies manage their own animated frames
        self.crosshair_img = self._load_image("assets/crosshair.png", (32, 32))

        # Initialize level state (spawns hand internally)
        self.start_level(1)

    def start_level(self, level=1):
        """Reset Pyro mode state and start a level."""
        self.level = max(1, int(level))

        # Clear grid and enemies
        self.grid_data = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.enemies = []
        self.spawn_timer = 0.0

        # Slightly speed up spawns on higher levels
        base_interval = PYRO_SPAWN_DELAY / 1000.0
        self.spawn_interval = max(0.3, base_interval * (0.9 ** (self.level - 1)))

        # Reset player hand/interaction
        self.spawn_puzzle_hand()
        self.dragging_block = None
        self.is_aiming = False
        self.prev_left = False
        self.prev_right = False

    # ---------- Helpers ----------
    def _load_image(self, path, size):
        try:
            img = pygame.image.load(resource_path(path)).convert_alpha()
            return pygame.transform.smoothscale(img, size)
        except Exception:
            return None

    def _create_pyramid_mask(self):
        mask = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        for row in range(self.grid_size):
            if row == 0:
                width = 1
            elif row == 1:
                width = 3
            elif row == 2:
                width = 5
            else:
                width = 7
            start_col = (self.grid_size - width) // 2
            end_col = start_col + width
            for col in range(start_col, end_col):
                mask[row][col] = 1
        return mask

    def spawn_puzzle_hand(self):
        self.hand = []
        base_shapes = ['I', 'L', 'DOT']
        for shape_key in base_shapes:
            key = shape_key if shape_key in SHAPES else random.choice(list(SHAPES.keys()))
            b = Block(key)
            b.dragging = False
            self.hand.append(b)

    def _screen_to_grid(self, x, y):
        gx = (x - self.offset_x) // self.cell_size
        gy = (y - self.offset_y) // self.cell_size
        if gx < 0 or gy < 0 or gx >= self.grid_size or gy >= self.grid_size:
            return None, None
        return int(gy), int(gx)

    def _can_place(self, row, col):
        return (
            row is not None and col is not None and
            0 <= row < self.grid_size and 0 <= col < self.grid_size and
            self.level_mask[row][col] == 1 and
            self.grid_data[row][col] is None
        )

    def _hand_layout(self):
        gap = 16
        tile = self.cell_size
        total_w = len(self.hand) * tile + max(0, len(self.hand) - 1) * gap
        start_x = (VIRTUAL_W - total_w) // 2
        y = VIRTUAL_H - 90
        positions = []
        for i, b in enumerate(self.hand):
            x = start_x + i * (tile + gap)
            positions.append((b, pygame.Rect(x, y, tile, tile)))
        return positions

    # ---------- Core loop ----------
    def update(self, dt):
        mx, my = pygame.mouse.get_pos()
        left, _, right = pygame.mouse.get_pressed()

        # Enemy spawner
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0.0
            self._spawn_enemy()

        # Aiming state (right-click hold)
        self.is_aiming = right

        # Left click actions
        left_down = left and not self.prev_left
        left_up = (not left) and self.prev_left

        # Aiming shoot
        if self.is_aiming and left_down:
            hit_enemy = None
            for enemy in self.enemies:
                if enemy.rect.collidepoint(mx, my):
                    hit_enemy = enemy
                    break
            if hit_enemy:
                self.enemies.remove(hit_enemy)
                if hasattr(self.game, 'audio'):
                    try:
                        self.game.audio.play('hit')
                    except Exception:
                        pass
                if hasattr(self.game, 'particle_system'):
                    try:
                        self.game.particle_system.create_text(mx, my, "BOOM", COLOR_1BIT_ENEMY, font_path=None)
                    except Exception:
                        pass

        # Block dragging start (only when not aiming)
        if not self.is_aiming and left_down and self.dragging_block is None:
            for block, rect in self._hand_layout():
                if rect.collidepoint(mx, my):
                    self.dragging_block = block
                    block.dragging = True
                    block.offset_x = mx - rect.x
                    block.offset_y = my - rect.y
                    break

        # Dragging movement
        if self.dragging_block and left:
            self.dragging_block.rect = pygame.Rect(
                mx - self.dragging_block.offset_x,
                my - self.dragging_block.offset_y,
                self.cell_size,
                self.cell_size,
            )

        # Drop logic
        if self.dragging_block and left_up:
            row, col = self._screen_to_grid(mx, my)
            if self._can_place(row, col):
                self.grid_data[row][col] = self.dragging_block
                if self.dragging_block in self.hand:
                    self.hand.remove(self.dragging_block)
                self.dragging_block.dragging = False
                self.dragging_block.rect = pygame.Rect(
                    self.offset_x + col * self.cell_size,
                    self.offset_y + row * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                )
            else:
                # Return to hand
                self.dragging_block.dragging = False
            self.dragging_block = None

        # Update blocks in hand for idle animation
        for b in self.hand:
            if hasattr(b, 'update'):
                try:
                    b.update()
                except Exception:
                    pass

        # Update enemies
        for enemy in self.enemies[:]:
            enemy.move_towards(self.core_pos, speed=PYRO_ENEMY_SPEED)
            enemy.update(dt)
            ex, ey = enemy.rect.center
            if math.hypot(ex - self.core_pos[0], ey - self.core_pos[1]) < 15:
                print("[PYRO] GAME OVER - Core destroyed!")
                self.start_level(1)
                return

        # Prune off-screen
        self.enemies = [e for e in self.enemies if not e.is_off_screen()]

        self.prev_left = left
        self.prev_right = right

    def _spawn_enemy(self):
        margin = 40
        if random.random() < 0.5:
            x = -margin if random.random() < 0.5 else VIRTUAL_W + margin
            y = random.randint(0, VIRTUAL_H)
        else:
            x = random.randint(0, VIRTUAL_W)
            y = -margin if random.random() < 0.5 else VIRTUAL_H + margin
        enemy = PyroEnemy(x, y)
        self.enemies.append(enemy)

    # ---------- Rendering ----------
    def draw(self, surface):
        mx, my = pygame.mouse.get_pos()
        # 1) Background
        surface.fill(COLOR_1BIT_BG)

        # 2) Decorations
        ui = getattr(self.game, 'ui', None)
        if ui and getattr(ui, 'bg_tiles', None):
            rows = len(ui.bg_tiles)
            cols = len(ui.bg_tiles[0]) if rows > 0 else 0
            for r in range(rows):
                for c in range(cols):
                    tile = ui.bg_tiles[r][c]
                    x, y = c * ui.tile_w, r * ui.tile_h
                    img = None
                    if tile['type'] == 'ra' and ui.ra_frames:
                        img = ui.ra_frames[tile['frame']]
                    elif tile['type'] == 'symbol' and ui.symbol_images:
                        base_img = ui.symbol_images[tile['img_idx']]
                        img = pygame.transform.flip(base_img, True, False) if tile['flipped_x'] else base_img
                    if img:
                        surface.blit(img, (x, y))

        # 3) Global dimming
        dim = pygame.Surface((VIRTUAL_W, VIRTUAL_H), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 200))
        surface.blit(dim, (0, 0))

        # 4) Vignette/border
        vignette = pygame.Surface((VIRTUAL_W, VIRTUAL_H), pygame.SRCALPHA)
        pygame.draw.rect(vignette, (0, 0, 0, 120), vignette.get_rect(), 60)
        surface.blit(vignette, (0, 0))

        # 5) Grid & core
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.level_mask[row][col] == 1:
                    cell_x = self.offset_x + col * self.cell_size
                    cell_y = self.offset_y + row * self.cell_size
                    cell_rect = pygame.Rect(cell_x, cell_y, self.cell_size, self.cell_size)
                    pygame.draw.rect(surface, COLOR_PYRO_ACCENT, cell_rect, 2)

        pygame.draw.circle(surface, COLOR_1BIT_FG, self.core_pos, 8)

        # 6) Enemies (above dimming and vignette)
        for enemy in self.enemies:
            enemy.draw(surface, self.enemy_img)

        # 7) Hand blocks
        for block, rect in self._hand_layout():
            if block is self.dragging_block and block.dragging and hasattr(block, 'rect'):
                # Draw at current drag position
                block.draw(surface, block.rect.x, block.rect.y, 1.0, 255, 'default')
            else:
                block.rect = rect
                block.draw(surface, rect.x, rect.y, 1.0, 255, 'default')

        # 8) Crosshair
        if self.is_aiming:
            if self.crosshair_img:
                cx = mx - self.crosshair_img.get_width() // 2
                cy = my - self.crosshair_img.get_height() // 2
                surface.blit(self.crosshair_img, (cx, cy))
            else:
                pygame.draw.circle(surface, COLOR_PYRO_ACCENT, (mx, my), 12, 2)

        # 9) Scanlines/CRT overlay (last)
        scan = pygame.Surface((VIRTUAL_W, VIRTUAL_H), pygame.SRCALPHA)
        for y in range(0, VIRTUAL_H, 3):
            pygame.draw.line(scan, (0, 0, 0, 40), (0, y), (VIRTUAL_W, y))
        surface.blit(scan, (0, 0))


class PyroEnemy:
    _frames = None
    _anim_sequence = [0, 1, 2, 3, 2, 1]

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)  # Logical hitbox
        self.x = float(x)
        self.y = float(y)
        self.anim_index = 0
        self.anim_timer = 0.0
        self.frame_interval = 0.1  # 100 ms

        # Lazy-load and slice sprite sheet once
        if PyroEnemy._frames is None:
            PyroEnemy._frames = self._slice_frames()

    def _slice_frames(self):
        frames = []
        try:
            sheet = pygame.image.load(resource_path("assets/alien.png")).convert_alpha()
            frame_w, frame_h = 64, 64
            for i in range(4):
                sub = sheet.subsurface(pygame.Rect(i * frame_w, 0, frame_w, frame_h)).copy()
                sub = pygame.transform.smoothscale(sub, (40, 40))
                sub.set_alpha(255)
                frames.append(sub)
        except Exception:
            frames = None
        return frames

    def update(self, dt):
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        # Advance animation timer
        if PyroEnemy._frames:
            self.anim_timer += dt
            if self.anim_timer >= self.frame_interval:
                self.anim_timer -= self.frame_interval
                self.anim_index = (self.anim_index + 1) % len(self._anim_sequence)

    def move_towards(self, target_pos, speed=PYRO_ENEMY_SPEED):
        tx, ty = target_pos
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            nx = dx / dist
            ny = dy / dist
            self.x += nx * speed
            self.y += ny * speed

    def is_off_screen(self):
        return (
            self.rect.right < -50 or self.rect.left > VIRTUAL_W + 50 or
            self.rect.bottom < -50 or self.rect.top > VIRTUAL_H + 50
        )

    def draw(self, surface, img=None):
        if PyroEnemy._frames:
            frame_idx = self._anim_sequence[self.anim_index]
            frame = PyroEnemy._frames[frame_idx]
            surface.blit(frame, self.rect)
        else:
            pygame.draw.rect(surface, COLOR_1BIT_ENEMY, self.rect)
            pygame.draw.rect(surface, COLOR_1BIT_FG, self.rect, 1)
