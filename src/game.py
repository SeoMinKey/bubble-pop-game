# src/game.py
import math
import random
import os
import pygame
from typing import List, Tuple, Optional, Set

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    CELL_SIZE, BUBBLE_RADIUS, BUBBLE_SPEED,
    LAUNCH_COOLDOWN, WALL_DROP_PIXELS, MAP_ROWS, MAP_COLS,
    NEXT_BUBBLE_X, NEXT_BUBBLE_Y_OFFSET
)
from game_settings import END_SCREEN_DELAY, POP_SOUND_VOLUME, TAP_SOUND_VOLUME
from asset_paths import ASSET_PATHS
from color_settings import COLORS, COLOR_MAP

# --- 유틸리티 ---
def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))

# --- 버블 클래스 ---
class Bubble:
    def __init__(self, x: float, y: float, color: str, radius: int = BUBBLE_RADIUS):
        self.x = x
        self.y = y
        self.color = color
        self.radius = radius
        self.in_air = False
        self.is_attached = False
        self.angle_degree = 90
        self.speed = BUBBLE_SPEED
        self.row_idx = -1
        self.col_idx = -1

    def draw(self, screen: pygame.Surface, bubble_images: Optional[dict]):
        if bubble_images:
            img = bubble_images.get(self.color)
            if img:
                rect = img.get_rect(center=(int(self.x), int(self.y)))
                screen.blit(img, rect)
                return
        pygame.draw.circle(screen, COLORS[self.color], (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (255,255,255), (int(self.x), int(self.y)), self.radius, 2)

    def set_angle(self, angle_degree: float):
        self.angle_degree = angle_degree

    def set_grid_index(self, r: int, c: int):
        self.row_idx = r
        self.col_idx = c

    def move(self):
        rad = math.radians(self.angle_degree)
        dx = self.speed * math.cos(rad)
        dy = -self.speed * math.sin(rad)
        self.x += dx
        self.y += dy

# --- Cannon ---
class Cannon:
    def __init__(self, x:int, y:int, asset_paths:dict):
        self.x = x
        self.y = y
        self.angle = 90
        self.min_angle = 10
        self.max_angle = 170
        self.angle_speed = 4.0
        self.asset_paths = asset_paths
        try:
            self.arrow_image = pygame.image.load(asset_paths['cannon_arrow']).convert_alpha()
            self.arrow_image = pygame.transform.smoothscale(self.arrow_image, (152, 317))
        except Exception:
            self.arrow_image = None

    def rotate(self, delta):
        self.angle += delta
        self.angle = clamp(self.angle, self.min_angle, self.max_angle)

    def draw(self, screen):
        if self.arrow_image:
            rotated = pygame.transform.rotate(self.arrow_image, self.angle - 90)
            rect = rotated.get_rect(center=(self.x, self.y))
            screen.blit(rotated, rect)
        else:
            length = 100
            rad = math.radians(self.angle)
            end_x = self.x + length * math.cos(rad)
            end_y = self.y - length * math.sin(rad)
            pygame.draw.line(screen, (255,255,255), (self.x, self.y), (end_x, end_y), 4)
            pygame.draw.circle(screen, (255,0,0), (self.x, self.y), 6)

# --- HexGrid (간소화된 버전) ---
class HexGrid:
    def __init__(self, rows:int, cols:int, cell_size:int, wall_offset:int=0, x_offset:int=0, y_offset:int=0):
        self.rows = rows
        self.cols = cols
        self.cell = cell_size
        self.wall_offset = wall_offset
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.map = [['.' for _ in range(cols)] for _ in range(rows)]
        self.bubble_list: List[Bubble] = []

    def load_from_stage(self, stage_map: List[List[str]]):
        self.map = [row[:] for row in stage_map]
        self.bubble_list = []
        for r in range(self.rows):
            if r >= len(self.map): break
            for c in range(self.cols):
                if c < len(self.map[r]):
                    ch = self.map[r][c]
                else:
                    ch = '.'
                if ch in COLORS:
                    x, y = self.get_cell_center(r, c)
                    b = Bubble(x, y, ch)
                    b.is_attached = True
                    b.set_grid_index(r, c)
                    self.bubble_list.append(b)

    def get_cell_center(self, r:int, c:int) -> Tuple[int,int]:
        x = c * self.cell + self.cell//2 + self.x_offset
        y = r * self.cell + self.cell//2 + self.wall_offset + self.y_offset
        if r % 2 == 1:
            x += self.cell//2
        return x, y

    def screen_to_grid(self, x: float, y: float) -> Tuple[int,int]:
        r = int((y - self.wall_offset - self.y_offset) // self.cell)
        if r < 0: r = 0
        c_base = x - self.x_offset
        if r % 2 == 1:
            c = int((c_base - self.cell//2) // self.cell)
        else:
            c = int(c_base // self.cell)
        c = int(clamp(c, 0, self.cols-1))
        r = int(clamp(r, 0, self.rows-1))
        return r, c

    def place_bubble(self, bubble: Bubble, r:int, c:int):
        if r < 0 or r >= self.rows or c < 0 or c >= self.cols:
            return
        self.map[r][c] = bubble.color
        cx, cy = self.get_cell_center(r, c)
        bubble.x, bubble.y = cx, cy
        bubble.is_attached = True
        bubble.in_air = False
        bubble.set_grid_index(r, c)
        self.bubble_list.append(bubble)

    def nearest_grid_to_point(self, x: float, y: float) -> Tuple[int,int]:
        r, c = self.screen_to_grid(x, y)
        if not self.is_in_bounds(r, c):
            return (0, clamp(c, 0, self.cols-1))
        if self.map[r][c] in COLORS:
            neighbors = self.get_neighbors(r, c)
            best = (r, c)
            mind = float('inf')
            found = False
            for nr, nc in neighbors:
                if self.is_in_bounds(nr, nc) and self.map[nr][nc] == '.':
                    nx, ny = self.get_cell_center(nr, nc)
                    d = (x-nx)**2 + (y-ny)**2
                    if d < mind:
                        mind = d
                        best = (nr, nc)
                        found = True
            if found: return best
        if self.is_in_bounds(r, c) and self.map[r][c] == '.':
            return r, c
        return r, c

    def is_in_bounds(self, r:int, c:int) -> bool:
        return 0 <= r < self.rows and 0 <= c < self.cols

    def get_neighbors(self, r:int, c:int):
        if r % 2 == 0:
            dr = [0, -1, -1, 0, 1, 1]
            dc = [-1, -1, 0, 1, 0, -1]
        else:
            dr = [0, -1, -1, 0, 1, 1]
            dc = [-1, 0, 1, 1, 1, 0]
        return [(r + dr[i], c + dc[i]) for i in range(6)]

    def dfs_same_color(self, row:int, col:int, color:str, visited:Set[Tuple[int,int]]):
        stack = [(row, col)]
        while stack:
            r, c = stack.pop()
            if not self.is_in_bounds(r,c) or (r,c) in visited:
                continue
            if r >= len(self.map) or c >= len(self.map[r]):
                continue
            if self.map[r][c] != color:
                continue
            visited.add((r,c))
            for nr, nc in self.get_neighbors(r,c):
                stack.append((nr, nc))

    def remove_cells(self, cells:Set[Tuple[int,int]]):
        s = set(cells)
        for (r, c) in s:
            if self.is_in_bounds(r,c):
                self.map[r][c] = '.'
        self.bubble_list = [b for b in self.bubble_list if (b.row_idx, b.col_idx) not in s]

    def flood_from_top(self) -> Set[Tuple[int,int]]:
        visited = set()
        for c in range(self.cols):
            if 0 < len(self.map) and c < len(self.map[0]):
                if self.map[0][c] in COLORS:
                    self._dfs_reachable(0, c, visited)
        return visited

    def _dfs_reachable(self, row:int, col:int, visited:Set[Tuple[int,int]]):
        if not self.is_in_bounds(row, col) or (row, col) in visited:
            return
        if row >= len(self.map) or col >= len(self.map[row]):
            return
        if self.map[row][col] not in COLORS:
            return
        visited.add((row, col))
        for nr, nc in self.get_neighbors(row, col):
            self._dfs_reachable(nr, nc, visited)

    def remove_hanging(self):
        connected = self.flood_from_top()
        not_connected = []
        for r in range(self.rows):
            if r >= len(self.map): break
            for c in range(self.cols):
                if c >= len(self.map[r]): break
                if self.map[r][c] in COLORS and (r, c) not in connected:
                    not_connected.append((r, c))
        if not_connected:
            self.remove_cells(set(not_connected))

    def draw(self, screen, bubble_images):
        for b in self.bubble_list:
            b.draw(screen, bubble_images)

    def drop_wall(self):
        self.wall_offset += WALL_DROP_PIXELS
        for b in self.bubble_list:
            cx, cy = self.get_cell_center(b.row_idx, b.col_idx)
            b.x, b.y = cx, cy

# --- ScoreDisplay ---
class ScoreDisplay:
    def __init__(self):
        self.score = 0
        try:
            self.font = pygame.font.Font(ASSET_PATHS['font'], 50) if ASSET_PATHS.get('font') else pygame.font.Font(None, 50)
        except:
            self.font = pygame.font.Font(None, 50)

    def add(self, points:int):
        self.score += points

    def draw(self, screen, level:int):
        score_txt = self.font.render(f'SCORE : {self.score}', True, (0,0,0))
        level_txt = self.font.render(f'LEVEL : {level}', True, (0,0,0))
        screen.blit(score_txt, (30, 30))
        screen.blit(level_txt, (30, 80))

# --- Game (Scene) ---
class Game:
    def __init__(self, manager):
        self.manager = manager
        # 화면 참조는 draw(screen)로 받음 — 내부에서 set_mode 사용하지 않음
        # 레이아웃, 오프셋 계산
        map_pixel_width = (MAP_COLS * CELL_SIZE) + (CELL_SIZE // 2)
        self.grid_x_offset = ((SCREEN_WIDTH - map_pixel_width) // 2) + 25
        self.grid_y_offset = 30
        padding = 10
        game_area_w = map_pixel_width + (padding * 2)
        game_area_h = SCREEN_HEIGHT - self.grid_y_offset
        game_area_x = (SCREEN_WIDTH - game_area_w) // 2
        game_area_y = self.grid_y_offset - padding
        self.game_rect = pygame.Rect(game_area_x, game_area_y, game_area_w, game_area_h)

        self.grid = HexGrid(MAP_ROWS, MAP_COLS, CELL_SIZE, 0, self.grid_x_offset, self.grid_y_offset)
        cannon_x = self.game_rect.centerx
        cannon_y = self.game_rect.bottom - 170
        self.cannon = Cannon(cannon_x, cannon_y, ASSET_PATHS)

        self.game_over_line = self.cannon.y - CELL_SIZE * 0.5
        self.score_ui = ScoreDisplay()

        # 에셋 로드(간단)
        self.bubble_images = {}
        try:
            self.bubble_images = {
                'R': pygame.image.load(ASSET_PATHS['bubble_red']),
                'Y': pygame.image.load(ASSET_PATHS['bubble_yellow']),
                'B': pygame.image.load(ASSET_PATHS['bubble_blue']),
                'G': pygame.image.load(ASSET_PATHS['bubble_green']),
            }
            target = BUBBLE_RADIUS * 2
            for k in list(self.bubble_images.keys()):
                self.bubble_images[k] = pygame.transform.smoothscale(self.bubble_images[k], (target, target))
        except Exception:
            self.bubble_images = None

        # 사운드 로드
        try:
            pygame.mixer.music.load(ASSET_PATHS['bgm'])
            pygame.mixer.music.set_volume(0.1)
            pygame.mixer.music.play(-1)
        except Exception:
            pass

        self.pop_sounds = []
        for s in ASSET_PATHS.get('pop_sounds', []):
            try:
                snd = pygame.mixer.Sound(s)
                snd.set_volume(POP_SOUND_VOLUME)
                self.pop_sounds.append(snd)
            except Exception:
                pass
        try:
            self.tap_sound = pygame.mixer.Sound(ASSET_PATHS['tap_sound'])
            self.tap_sound.set_volume(TAP_SOUND_VOLUME)
        except Exception:
            self.tap_sound = None

        self.current_stage = 0
        self.current_bubble = None
        self.next_bubble = None
        self.fire_in_air = False
        self.fire_count = 0
        self.running = True

        self.load_stage(self.current_stage)

    # --- 스테이지/버블 준비 ---
    def load_stage(self, stage_index:int):
        from main_v2 import load_stage_from_csv  # 재사용: 업로드 파일 내 함수 재사용 (혹시 분리했으면 직접 로드로 바꿔도 됨)
        stage_map = load_stage_from_csv(stage_index)
        if not stage_map or all(all(cell == '.' for cell in row) for row in stage_map):
            next_csv = f'assets/map_data/stage{stage_index+2}.csv'
            if not os.path.exists(next_csv):
                self.running = False
                return
        self.grid.wall_offset = 0
        self.grid.y_offset = self.grid_y_offset
        self.grid.load_from_stage(stage_map)
        self.current_bubble = None
        self.next_bubble = None
        self.fire_in_air = False
        self.fire_count = 0
        self.prepare_bubbles()

    def random_color_from_map(self) -> str:
        colors = set()
        for bubble in self.grid.bubble_list:
            if bubble.color in COLORS:
                colors.add(bubble.color)
        if not colors:
            colors = set(COLORS.keys())
        return random.choice(list(colors))

    def create_bubble(self) -> Bubble:
        color = self.random_color_from_map()
        return Bubble(self.cannon.x, self.cannon.y, color)

    def prepare_bubbles(self):
        if self.next_bubble is not None:
            self.current_bubble = self.next_bubble
        else:
            self.current_bubble = self.create_bubble()
        self.current_bubble.x, self.current_bubble.y = self.cannon.x, self.cannon.y
        self.current_bubble.in_air = False
        self.next_bubble = self.create_bubble()

    def process_collision_and_attach(self) -> bool:
        if self.current_bubble is None: return False
        if self.current_bubble.y - self.current_bubble.radius <= (self.grid.y_offset + self.grid.wall_offset):
            r, c = self.grid.nearest_grid_to_point(self.current_bubble.x, self.current_bubble.y)
            r = 0
            self.grid.place_bubble(self.current_bubble, r, c)
            popped = self.pop_if_match(r, c)
            if popped == 0 and self.tap_sound:
                try: self.tap_sound.play()
                except: pass
            return True
        for b in self.grid.bubble_list:
            dist = math.hypot(self.current_bubble.x - b.x, self.current_bubble.y - b.y)
            if dist <= self.current_bubble.radius + b.radius - 2:
                r, c = self.grid.nearest_grid_to_point(self.current_bubble.x, self.current_bubble.y)
                self.grid.place_bubble(self.current_bubble, r, c)
                popped = self.pop_if_match(r, c)
                if popped == 0 and self.tap_sound:
                    try: self.tap_sound.play()
                    except: pass
                return True
        return False

    def pop_if_match(self, row:int, col:int) -> int:
        if self.current_bubble is None: return 0
        if not self.grid.is_in_bounds(row, col): return 0
        color = self.grid.map[row][col]
        if color not in COLORS: return 0
        visited = set()
        self.grid.dfs_same_color(row, col, color, visited)
        if len(visited) >= 3:
            self.grid.remove_cells(visited)
            self.grid.remove_hanging()
            self.score_ui.add(len(visited) * 10)
            if self.pop_sounds:
                try:
                    random.choice(self.pop_sounds).play()
                except: pass
            return len(visited)
        return 0

    # --- 씬 인터페이스: 이벤트 수신 ---
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # 메뉴로 복귀
                self.manager.change("menu")
                return
            if event.key == pygame.K_SPACE:
                if self.current_bubble and not self.fire_in_air:
                    self.fire_in_air = True
                    self.current_bubble.in_air = True
                    self.current_bubble.set_angle(self.cannon.angle)

    # --- per-frame 업데이트 ---
    def update(self, dt=None):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.cannon.rotate(+self.cannon.angle_speed)
        if keys[pygame.K_RIGHT]:
            self.cannon.rotate(-self.cannon.angle_speed)

        if self.current_bubble and self.fire_in_air:
            self.current_bubble.move()
            if self.current_bubble.y < -BUBBLE_RADIUS:
                self.fire_in_air = False
                self.prepare_bubbles()
                return
            if self.process_collision_and_attach():
                self.fire_count += 1
                if self.fire_count >= LAUNCH_COOLDOWN:
                    self.grid.drop_wall()
                    self.fire_count = 0
                self.current_bubble = None
                self.fire_in_air = False
                self.prepare_bubbles()

        # 스테이지 클리어 검사
        if self.is_stage_cleared():
            self.show_stage_clear()
            self.current_stage += 1
            next_csv_path = f'assets/map_data/stage{self.current_stage + 1}.csv'
            if not os.path.exists(next_csv_path):
                self.running = False
            else:
                self.load_stage(self.current_stage)

        if self.lowest_bubble_bottom() > self.game_over_line:
            self.running = False

    def is_stage_cleared(self):
        for r in range(self.grid.rows):
            if r >= len(self.grid.map): continue
            for c in range(self.grid.cols):
                if c >= len(self.grid.map[r]): continue
                if self.grid.map[r][c] in COLORS:
                    return False
        return True

    def lowest_bubble_bottom(self):
        if not self.grid.bubble_list: return 0
        bottoms = [b.y + b.radius for b in self.grid.bubble_list]
        return max(bottoms)

    # --- draw: 반드시 외부에서 screen을 주입받음 ---
    def draw(self, screen: pygame.Surface):
        # 배경
        try:
            bg = pygame.image.load(ASSET_PATHS['background']).convert()
            bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(bg, (0,0))
        except:
            screen.fill((10,20,30))

        pygame.draw.rect(screen, (0,100,200), self.game_rect)
        pygame.draw.line(screen, (0,255,3),
                         (self.game_rect.left, self.game_over_line),
                         (self.game_rect.right, self.game_over_line), 10)

        self.grid.draw(screen, self.bubble_images)
        self.cannon.draw(screen)
        if self.current_bubble:
            self.current_bubble.draw(screen, self.bubble_images)

        # NEXT bubble
        if self.next_bubble:
            next_x = NEXT_BUBBLE_X
            next_y = SCREEN_HEIGHT + NEXT_BUBBLE_Y_OFFSET if NEXT_BUBBLE_Y_OFFSET < 0 else NEXT_BUBBLE_Y_OFFSET
            try:
                font = pygame.font.Font(ASSET_PATHS['font'], 40) if ASSET_PATHS.get('font') else pygame.font.Font(None, 40)
            except:
                font = pygame.font.Font(None, 40)
            txt = font.render("NEXT", True, (0,0,0))
            screen.blit(txt, (next_x - txt.get_width()//2, next_y - 70))
            ox, oy = self.next_bubble.x, self.next_bubble.y
            self.next_bubble.x, self.next_bubble.y = next_x, next_y
            self.next_bubble.draw(screen, self.bubble_images)
            self.next_bubble.x, self.next_bubble.y = ox, oy

        # score
        self.score_ui.draw(screen, self.current_stage + 1)

    def show_stage_clear(self):
        # 단순한 오버레이
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0,0,0))
        # 화면은 draw()에서 처리되므로 여긴 단순 일시정지(메인 루프가 flip 함)
        pygame.display.get_surface().blit(overlay, (0,0))
        try:
            font = pygame.font.Font(ASSET_PATHS['font'], 120)
        except:
            font = pygame.font.Font(None, 80)
        text = font.render('CLEAR!', True, (100,255,100))
        rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        pygame.display.get_surface().blit(text, rect)
        pygame.display.flip()
        pygame.time.delay(1000)
