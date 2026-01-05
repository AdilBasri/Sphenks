import pygame
from settings import *

class Grid:
    def __init__(self):
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.surface = pygame.Surface((GRID_WIDTH, GRID_HEIGHT))
        self.rect = self.surface.get_rect(topleft=(0, 0))
        
        # --- REAKTİF ÖZELLİKLER ---
        self.pulse_intensity = 0 
        self.border_pulse = 0 

    def update_position(self, screen_width, screen_height):
        center_x = (screen_width - GRID_WIDTH) // 2
        center_y = (screen_height - GRID_HEIGHT) // 2 - 40 
        self.rect.topleft = (center_x, center_y)
        return center_x, center_y

    def reset(self):
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    def trigger_beat(self, intensity=1.0):
        """
        Sadece patlama anında çağrılır.
        Gridi anlık olarak çok parlak yapar ve çerçeveyi kalınlaştırır.
        """
        self.pulse_intensity = 120 # Maksimum parlaklık (daha sert)
        self.border_pulse = 6 # Çerçeve daha belirgin zıplasın

    def update(self):
        """Parlaklığı normale döndür (Hızlı sönümleme)"""
        if self.pulse_intensity > 0:
            self.pulse_intensity -= 8 # Daha hızlı normale dönsün (Snappy his)
            if self.pulse_intensity < 0: self.pulse_intensity = 0
            
        if self.border_pulse > 0:
            self.border_pulse -= 0.8 # Çerçeve de hızlı insin
            if self.border_pulse < 0: self.border_pulse = 0

    def place_stones(self, count):
        import random
        placed = 0
        while placed < count:
            r = random.randint(0, GRID_SIZE - 1)
            c = random.randint(0, GRID_SIZE - 1)
            if self.grid[r][c] is None:
                self.grid[r][c] = STONE_COLOR
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
                    self.grid[grid_row + r][grid_col + c] = block.color

    def get_potential_clears(self, block, grid_row, grid_col):
        rows_to_shine = []
        cols_to_shine = []
        block_cells = []
        for r in range(block.rows):
            for c in range(block.cols):
                if block.matrix[r][c] == 1:
                    block_cells.append((grid_row + r, grid_col + c))
        for r in range(GRID_SIZE):
            is_full = True
            for c in range(GRID_SIZE):
                if self.grid[r][c] is None and (r, c) not in block_cells:
                    is_full = False
                    break
            if is_full: rows_to_shine.append(r)
        for c in range(GRID_SIZE):
            is_full = True
            for r in range(GRID_SIZE):
                if self.grid[r][c] is None and (r, c) not in block_cells:
                    is_full = False
                    break
            if is_full: cols_to_shine.append(c)
        return rows_to_shine, cols_to_shine

    def check_clears(self):
        rows_to_clear = []
        cols_to_clear = []
        for r in range(GRID_SIZE):
            if all(self.grid[r][c] is not None for c in range(GRID_SIZE)):
                rows_to_clear.append(r)
        for c in range(GRID_SIZE):
            if all(self.grid[r][c] is not None for r in range(GRID_SIZE)):
                cols_to_clear.append(c)

        for r in rows_to_clear:
            for c in range(GRID_SIZE): self.grid[r][c] = None
        for c in cols_to_clear:
            for r in range(GRID_SIZE): self.grid[r][c] = None
                
        return rows_to_clear, cols_to_clear

    def draw(self, screen, offset_x=0, offset_y=0, theme_data=None, highlight_rows=[], highlight_cols=[]):
        if theme_data is None: theme_data = THEMES['NEON']
        bg_col = theme_data['grid_bg']
        style = theme_data['style']
        base_line_col = theme_data['line']

        # 1. Zemini Temizle
        self.surface.fill(bg_col)

        # --- 2. GRID ÇİZGİLERİ ---
        # Sadece patlama olduğunda pulse_intensity yüksek olur, diğer zamanlar 0'dır.
        current_line_col = (
            min(255, base_line_col[0] + self.pulse_intensity),
            min(255, base_line_col[1] + self.pulse_intensity),
            min(255, base_line_col[2] + self.pulse_intensity)
        )

        # Dikey çizgiler
        for i in range(GRID_SIZE + 1):
            x = i * TILE_SIZE
            width = 3 if (i == 0 or i == GRID_SIZE) else 1
            pygame.draw.line(self.surface, current_line_col, (x, 0), (x, GRID_HEIGHT), width)

        # Yatay çizgiler
        for i in range(GRID_SIZE + 1):
            y = i * TILE_SIZE
            width = 3 if (i == 0 or i == GRID_SIZE) else 1
            pygame.draw.line(self.surface, current_line_col, (0, y), (GRID_WIDTH, y), width)

        # --- 3. BLOKLAR VE İÇERİK ---
        if highlight_rows or highlight_cols:
            highlight_surface = pygame.Surface((GRID_WIDTH, GRID_HEIGHT), pygame.SRCALPHA)
            for r in highlight_rows:
                rect = pygame.Rect(0, r * TILE_SIZE, GRID_WIDTH, TILE_SIZE)
                pygame.draw.rect(highlight_surface, (255, 255, 255, 60), rect)
            for c in highlight_cols:
                rect = pygame.Rect(c * TILE_SIZE, 0, TILE_SIZE, GRID_HEIGHT)
                pygame.draw.rect(highlight_surface, (255, 255, 255, 60), rect)
            self.surface.blit(highlight_surface, (0,0))

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

        draw_rect = self.rect.move(offset_x, offset_y)
        border_thickness = 3 + int(self.border_pulse)
        pygame.draw.rect(screen, ACCENT_COLOR, draw_rect.inflate(6 + self.border_pulse, 6 + self.border_pulse), border_thickness, border_radius=8)
        
        shadow_rect = draw_rect.move(10, 10)
        shadow_surf = pygame.Surface(draw_rect.size, pygame.SRCALPHA)
        shadow_surf.fill((0, 0, 0, 100))
        screen.blit(shadow_surf, shadow_rect)
        screen.blit(self.surface, draw_rect)