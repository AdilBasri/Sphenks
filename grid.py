# grid.py
import pygame
import sys
from settings import *

class Grid:
    def __init__(self):
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.surface = pygame.Surface((GRID_WIDTH, GRID_HEIGHT))
        self.rect = pygame.Rect(GRID_OFFSET_X, GRID_OFFSET_Y, GRID_WIDTH, GRID_HEIGHT)
        
        # Ekstra Veri Katmanları
        self.grid_tags = [['NONE' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.grid_runes = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)] # YENİ: Rün katmanı
        
        # --- REAKTİF ÖZELLİKLER ---
        self.pulse_intensity = 0 
        self.border_pulse = 0 

    def update_position(self, screen_width, screen_height):
        # Position is controlled by settings; return current offsets
        self.rect.topleft = (GRID_OFFSET_X, GRID_OFFSET_Y)
        return GRID_OFFSET_X, GRID_OFFSET_Y

    def reset(self):
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.grid_tags = [['NONE' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.grid_runes = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    def trigger_beat(self, intensity=1.0):
        """Sadece patlama anında çağrılır."""
        self.pulse_intensity = 120 
        self.border_pulse = 6 

    def update(self):
        """Parlaklığı normale döndür"""
        if self.pulse_intensity > 0:
            self.pulse_intensity -= 8 
            if self.pulse_intensity < 0: self.pulse_intensity = 0
            
        if self.border_pulse > 0:
            self.border_pulse -= 0.8 
            if self.border_pulse < 0: self.border_pulse = 0

    def place_stones(self, count):
        import random
        placed = 0
        while placed < count:
            r = random.randint(0, GRID_SIZE - 1)
            c = random.randint(0, GRID_SIZE - 1)
            if self.grid[r][c] is None:
                self.grid[r][c] = STONE_COLOR
                self.grid_tags[r][c] = 'STONE'
                placed += 1

    def is_valid_position(self, block, grid_row, grid_col):
        for r in range(block.rows):
            for c in range(block.cols):
                if block.matrix[r][c] == 1:
                    if not (0 <= grid_row + r < GRID_SIZE and 0 <= grid_col + c < GRID_SIZE):
                        return False
                    if self.grid[grid_row + r][grid_col + c] is not None:
                        return False
        return True

    def place_block(self, block, grid_row, grid_col):
        for r in range(block.rows):
            for c in range(block.cols):
                if block.matrix[r][c] == 1:
                    # Renk
                    self.grid[grid_row + r][grid_col + c] = block.color
                    # Tag
                    tag = getattr(block, 'tag', 'NONE')
                    self.grid_tags[grid_row + r][grid_col + c] = tag
                    # Rune (Çoklu Rün Sistemi - Hücre Bazlı)
                    rune_at_cell = block.runes.get((r, c), None)
                    self.grid_runes[grid_row + r][grid_col + c] = rune_at_cell

    def check_clears(self):
        """
        Dolu satır/sütunları bulur ve temizler.
        Returns: rows_to_clear, cols_to_clear, color_bonus, match_count, rune_bonuses
        """
        rows_to_clear = []
        cols_to_clear = []
        
        total_color_bonus = 0
        match_count = 0
        
        # Rün Bonusları
        rune_bonuses = {
            'chips': 0,
            'mult_add': 0,
            'mult_x': 1.0,
            'money': 0
        }

        # --- SATIR KONTROLÜ ---
        for r in range(GRID_SIZE):
            if all(self.grid[r][c] is not None for c in range(GRID_SIZE)):
                rows_to_clear.append(r)
                current_color = None
                consecutive = 0
                for c in range(GRID_SIZE):
                    val = self.grid[r][c]
                    if val != STONE_COLOR and val == current_color:
                        consecutive += 1
                    else:
                        if consecutive >= 3:
                            total_color_bonus += COLOR_MATCH_BONUS * consecutive
                            match_count += 1
                        current_color = val
                        consecutive = 1 if val != STONE_COLOR else 0
                if consecutive >= 3:
                    total_color_bonus += COLOR_MATCH_BONUS * consecutive
                    match_count += 1

        # --- SÜTUN KONTROLÜ ---
        for c in range(GRID_SIZE):
            if all(self.grid[r][c] is not None for r in range(GRID_SIZE)):
                cols_to_clear.append(c)
                current_color = None
                consecutive = 0
                for r in range(GRID_SIZE):
                    val = self.grid[r][c]
                    if val != STONE_COLOR and val == current_color:
                        consecutive += 1
                    else:
                        if consecutive >= 3:
                            total_color_bonus += COLOR_MATCH_BONUS * consecutive
                            match_count += 1
                        current_color = val
                        consecutive = 1 if val != STONE_COLOR else 0
                if consecutive >= 3:
                    total_color_bonus += COLOR_MATCH_BONUS * consecutive
                    match_count += 1

        # --- TEMİZLEME VE RÜN HESAPLAMA ---
        cells_to_process = []
        for r in rows_to_clear:
            for c in range(GRID_SIZE): cells_to_process.append((r, c))
        for c in cols_to_clear:
            for r in range(GRID_SIZE): cells_to_process.append((r, c))
            
        unique_cells = set(cells_to_process)
        
        for r, c in unique_cells:
            # Rün var mı?
            rune = self.grid_runes[r][c]
            if rune:
                if rune.effect == 'add_chips': rune_bonuses['chips'] += rune.value
                elif rune.effect == 'add_mult': rune_bonuses['mult_add'] += rune.value
                elif rune.effect == 'multiply_mult': rune_bonuses['mult_x'] *= rune.value
                elif rune.effect == 'add_money': rune_bonuses['money'] += rune.value
            
            # Temizle
            self.grid[r][c] = None
            self.grid_tags[r][c] = 'NONE'
            self.grid_runes[r][c] = None
                
        return rows_to_clear, cols_to_clear, total_color_bonus, match_count, rune_bonuses

    def draw(self, screen, theme_data=None, highlight_rows=None, highlight_cols=None):
        if theme_data is None: theme_data = THEMES['NEON']
        if highlight_rows is None: highlight_rows = []
        if highlight_cols is None: highlight_cols = []
        bg_col = theme_data['grid_bg']
        style = theme_data['style']
        base_line_col = theme_data['line']

        self.surface.fill(bg_col)

        current_line_col = (
            min(255, base_line_col[0] + self.pulse_intensity),
            min(255, base_line_col[1] + self.pulse_intensity),
            min(255, base_line_col[2] + self.pulse_intensity)
        )

        # Çizgiler
        for i in range(GRID_SIZE + 1):
            x = i * TILE_SIZE
            width = 3 if (i == 0 or i == GRID_SIZE) else 1
            pygame.draw.line(self.surface, current_line_col, (x, 0), (x, GRID_HEIGHT), width)
        for i in range(GRID_SIZE + 1):
            y = i * TILE_SIZE
            width = 3 if (i == 0 or i == GRID_SIZE) else 1
            pygame.draw.line(self.surface, current_line_col, (0, y), (GRID_WIDTH, y), width)

        # Highlight
        if highlight_rows or highlight_cols:
            highlight_surface = pygame.Surface((GRID_WIDTH, GRID_HEIGHT), pygame.SRCALPHA)
            for r in highlight_rows:
                rect = pygame.Rect(0, r * TILE_SIZE, GRID_WIDTH, TILE_SIZE)
                pygame.draw.rect(highlight_surface, (255, 255, 255, 60), rect)
            for c in highlight_cols:
                rect = pygame.Rect(c * TILE_SIZE, 0, TILE_SIZE, GRID_HEIGHT)
                pygame.draw.rect(highlight_surface, (255, 255, 255, 60), rect)
            self.surface.blit(highlight_surface, (0,0))

        # Bloklar
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = col * TILE_SIZE
                y = row * TILE_SIZE
                gap = 0
                if style == 'glass': gap = int(TILE_SIZE * 0.1)
                elif style == 'pixel': gap = 0
                elif style == 'flat': gap = int(TILE_SIZE * 0.15)
                
                draw_x = x + (gap // 2); draw_y = y + (gap // 2)
                block_size = TILE_SIZE - gap
                rect = pygame.Rect(draw_x, draw_y, block_size, block_size)
                
                cell_color = self.grid[row][col]
                if cell_color:
                    if cell_color == STONE_COLOR:
                        pygame.draw.rect(self.surface, (60, 60, 70), rect, border_radius=4)
                        pygame.draw.line(self.surface, (0,0,0), rect.topleft, rect.bottomright, 2)
                        pygame.draw.rect(self.surface, (100, 100, 110), rect, 1, border_radius=4)
                    else:
                        if style == 'glass':
                            dark_color = (max(0, cell_color[0]-60), max(0, cell_color[1]-60), max(0, cell_color[2]-60))
                            pygame.draw.rect(self.surface, dark_color, rect, border_radius=8)
                            center_rect = rect.inflate(-15, -15)
                            bright_color = (min(255, cell_color[0]+40), min(255, cell_color[1]+40), min(255, cell_color[2]+40))
                            pygame.draw.rect(self.surface, bright_color, center_rect, border_radius=6)
                            reflection_points = [(draw_x + 6, draw_y + 18), (draw_x + 6, draw_y + 6), (draw_x + 18, draw_y + 6)]
                            pygame.draw.lines(self.surface, (255, 255, 255, 140), False, reflection_points, 2)
                            pygame.draw.rect(self.surface, cell_color, rect, 2, border_radius=8)
                        elif style == 'pixel':
                            pygame.draw.rect(self.surface, cell_color, rect)
                            pygame.draw.rect(self.surface, (0,0,0), rect, 3)
                        elif style == 'flat':
                            pastel = ((cell_color[0]+255)//2, (cell_color[1]+255)//2, (cell_color[2]+255)//2)
                            pygame.draw.rect(self.surface, pastel, rect, border_radius=15)
                        
                        # RÜN İKONU (Grid üzerinde)
                        rune = self.grid_runes[row][col]
                        if rune:
                            pygame.draw.circle(self.surface, (0,0,0,100), rect.center, 6)
                            pygame.draw.circle(self.surface, rune.color, rect.center, 4)

        draw_rect = self.rect
        border_thickness = 3 + int(self.border_pulse)
        pygame.draw.rect(screen, ACCENT_COLOR, draw_rect.inflate(6 + self.border_pulse, 6 + self.border_pulse), border_thickness, border_radius=8)
        
        shadow_rect = draw_rect.move(10, 10)
        shadow_surf = pygame.Surface(draw_rect.size, pygame.SRCALPHA)
        shadow_surf.fill((0, 0, 0, 100))
        screen.blit(shadow_surf, shadow_rect)
        screen.blit(self.surface, draw_rect)