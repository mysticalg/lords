import pygame
import sys
import random
import math
import copy
import os

# --- Global Constants (same as before) ---
TILE_SIZE = 40
GRID_WIDTH, GRID_HEIGHT = 50, 50
WORLD_WIDTH = TILE_SIZE * GRID_WIDTH   # 2000 pixels wide
WORLD_HEIGHT = TILE_SIZE * GRID_HEIGHT   # 2000 pixels tall

GAME_VIEW_WIDTH, GAME_VIEW_HEIGHT = 600, 600
SIDEBAR_WIDTH, SIDEBAR_HEIGHT = 200, 600
SCREEN_WIDTH, SCREEN_HEIGHT = GAME_VIEW_WIDTH + SIDEBAR_WIDTH, 600

FPS = 60

# Colors (for UI and debug outlines)
WHITE      = (255, 255, 255)
BLACK      = (0, 0, 0)
RED        = (255, 0, 0)
BLUE       = (0, 0, 255)
PURPLE     = (128, 0, 128)
GREEN      = (0, 255, 0)
ORANGE     = (255, 165, 0)
DARK_GREEN = (0, 100, 0)
YELLOW     = (255, 255, 0)
GRAY       = (128, 128, 128)
DARK_GRAY  = (30, 30, 30)

# --- Base Stats & Costs (same as before) ---
BASE_WIZARD_CONFIG = {
    "max_mana": 100,
    "max_ap": 5,
    "strength": 5,
    "stamina": 100  # HP
}
WIZARD_SPEED = 3

ALLY_TYPES = {
    "Imp": {
         "color": ORANGE,  # no longer used for drawing, now we use images
         "max_ap": 5,
         "hp": 10,
         "strength": 5,
         "speed": 3,
         "intelligence": 3,
         "auto_roam": False,
         "mana_cost": 20
    },
    "Ogre": {
         "color": DARK_GREEN,
         "max_ap": 3,
         "hp": 20,
         "strength": 10,
         "speed": 2,
         "intelligence": 1,
         "auto_roam": False,
         "mana_cost": 40
    },
    "Goblin": {
         "color": YELLOW,
         "max_ap": 6,
         "hp": 8,
         "strength": 4,
         "speed": 4,
         "intelligence": 4,
         "auto_roam": True,
         "mana_cost": 15
    }
}
ALLY_PURCHASE_COSTS = {"Imp": 30, "Ogre": 50, "Goblin": 25}
UPGRADE_COSTS = {"max_mana": 20, "max_ap": 15, "strength": 25, "stamina": 25}

ENEMY_STATS = {"color": RED, "max_ap": 2, "hp": 15, "strength": 5}

XP_PER_ENEMY = 10
XP_LEVEL_BONUS = 50
BASE_TURN_LIMIT = 50
ENEMY_SPAWN_BASE = 10
MAX_LEVEL = 100
PORTAL_COUNTDOWN = 10

# --- Asset Loader ---
def load_image(name):
    path = os.path.join("assets", name)
    try:
        image = pygame.image.load(path)
    except Exception as e:
        print(f"Error loading image {path}: {e}")
        image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        image.fill(RED)
    return image

def load_assets():
    assets = {}
    def load_anim(name):
        # Load two frames for the given animation base name.
        return [load_image(f"{name}_0.png"), load_image(f"{name}_1.png")]
    assets["wizard"] = load_anim("wizard")
    assets["imp"] = load_anim("imp")
    assets["ogre"] = load_anim("ogre")
    assets["goblin"] = load_anim("goblin")
    assets["enemy"] = load_anim("enemy")
    assets["grass_tile"] = load_image("grass_tile.png")
    assets["tree_tile"] = load_image("tree_tile.png")
    assets["building_tile"] = load_image("building_tile.png")
    assets["swamp_tile"] = load_image("swamp_tile.png")
    return assets

ASSETS = load_assets()

# --- Helper Functions (same as before) ---
def is_tile_walkable(x, y, obstacles):
    if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
        return False
    for obs in obstacles:
        if (x >= obs.grid_x and x < obs.grid_x + obs.grid_width and
            y >= obs.grid_y and y < obs.grid_y + obs.grid_height):
            return False
    return True

def get_line(x0, y0, x1, y1):
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x, y = x0, y0
    sx = -1 if x0 > x1 else 1
    sy = -1 if y0 > y1 else 1
    if dx > dy:
        err = dx / 2.0
        while x != x1:
            points.append((x, y))
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy / 2.0
        while y != y1:
            points.append((x, y))
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy
    points.append((x1, y1))
    return points

def line_of_sight(x0, y0, x1, y1, obstacles):
    line = get_line(x0, y0, x1, y1)
    for (x, y) in line:
        for obs in obstacles:
            if (x >= obs.grid_x and x < obs.grid_x + obs.grid_width and
                y >= obs.grid_y and y < obs.grid_y + obs.grid_height):
                return False
    return True

# --- Attack Visual Effect Class (same as before) ---
class AttackEffect:
    def __init__(self, grid_x, grid_y):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.start_time = pygame.time.get_ticks()
        self.duration = 200  # milliseconds
    def is_active(self):
        return pygame.time.get_ticks() - self.start_time < self.duration

# --- Entity Classes with Animation ---
class Wizard:
    def __init__(self, grid_x, grid_y, config):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.max_mana = config["max_mana"]
        self.mana = config["max_mana"]
        self.max_ap = config["max_ap"]
        self.ap = config["max_ap"]
        self.hp = config["stamina"]
        self.strength = config["strength"]
        self.speed = WIZARD_SPEED
        self.frames = ASSETS["wizard"]
        self.color = PURPLE  # fallback
    def reset_ap(self):
        self.ap = self.max_ap

class Ally:
    def __init__(self, grid_x, grid_y, ally_type):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.type = ally_type
        stats = ALLY_TYPES[ally_type]
        self.hp = stats["hp"]
        self.max_ap = stats["max_ap"]
        self.ap = stats["max_ap"]
        self.strength = stats["strength"]
        self.speed = stats["speed"]
        self.intelligence = stats["intelligence"]
        self.auto_roam = stats["auto_roam"]
        # Use the asset with key as the lowercase ally type
        self.frames = ASSETS[ally_type.lower()]
    def reset_ap(self):
        self.ap = self.max_ap

class Enemy:
    def __init__(self, grid_x, grid_y):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.hp = ENEMY_STATS["hp"]
        self.max_ap = ENEMY_STATS["max_ap"]
        self.ap = ENEMY_STATS["max_ap"]
        self.strength = ENEMY_STATS["strength"]
        self.frames = ASSETS["enemy"]
        self.color = ENEMY_STATS["color"]
    def reset_ap(self):
        self.ap = self.max_ap

class Obstacle:
    def __init__(self, grid_x, grid_y, grid_width, grid_height, obs_type):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.type = obs_type  # "tree", "building", "swamp"

class Portal:
    def __init__(self, grid_x, grid_y):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.countdown = PORTAL_COUNTDOWN

# --- Main Game Class ---
# (For brevity, the rest of the game logic remains largely unchanged.)
# In drawing functions, we now blit the current animation frame of each unit.

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Turn-Based Lords of Chaos Clone")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 16)
        self.state = "EDITOR"
        self.exp = 400
        self.wizard_config = copy.deepcopy(BASE_WIZARD_CONFIG)
        self.purchased_allies = {"Imp": 0, "Ogre": 0, "Goblin": 0}
        self.editor_options = [
            {"name": "Max Mana (+10)", "key": "max_mana", "increment": 10, "cost": UPGRADE_COSTS["max_mana"]},
            {"name": "Max AP (+1)", "key": "max_ap", "increment": 1, "cost": UPGRADE_COSTS["max_ap"]},
            {"name": "Strength (+1)", "key": "strength", "increment": 1, "cost": UPGRADE_COSTS["strength"]},
            {"name": "Stamina (+10)", "key": "stamina", "increment": 10, "cost": UPGRADE_COSTS["stamina"]},
            {"name": "Buy Imp", "key": "Imp", "increment": 1, "cost": ALLY_PURCHASE_COSTS["Imp"]},
            {"name": "Buy Ogre", "key": "Ogre", "increment": 1, "cost": ALLY_PURCHASE_COSTS["Ogre"]},
            {"name": "Buy Goblin", "key": "Goblin", "increment": 1, "cost": ALLY_PURCHASE_COSTS["Goblin"]},
            {"name": "Start Level", "action": "start"}
        ]
        self.editor_index = 0
        self.level = 1
        self.turn_count = 0
        self.turn_limit = BASE_TURN_LIMIT
        self.portal = None
        self.wizard = None
        self.player_units = []
        self.allowed_allies = {}
        self.enemies = []
        self.obstacles = []
        self.explored = [[False for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)]
        self.current_unit_index = 0
        self.attack_effects = []
        self.game_over = False
        self.game_win = False
        self.setup_world()
    
    def setup_world(self):
        self.obstacles = []
        for _ in range(20):
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            self.obstacles.append(Obstacle(x, y, 1, 1, "tree"))
        for _ in range(10):
            x = random.randint(0, GRID_WIDTH - 2)
            y = random.randint(0, GRID_HEIGHT - 2)
            self.obstacles.append(Obstacle(x, y, 2, 2, "building"))
        for _ in range(5):
            x = random.randint(0, GRID_WIDTH - 3)
            y = random.randint(0, GRID_HEIGHT - 3)
            self.obstacles.append(Obstacle(x, y, 3, 3, "swamp"))
    
    def handle_editor_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.editor_index = (self.editor_index - 1) % len(self.editor_options)
                elif event.key == pygame.K_DOWN:
                    self.editor_index = (self.editor_index + 1) % len(self.editor_options)
                elif event.key in [pygame.K_RIGHT, pygame.K_RETURN]:
                    option = self.editor_options[self.editor_index]
                    if "action" in option and option["action"] == "start":
                        self.start_level()
                        self.state = "GAME"
                    else:
                        if self.exp >= option["cost"]:
                            self.exp -= option["cost"]
                            key = option["key"]
                            if key in self.wizard_config:
                                self.wizard_config[key] += option["increment"]
                            else:
                                self.purchased_allies[key] += option["increment"]
    
    def draw_editor(self):
        self.screen.fill(BLACK)
        title = self.font.render("Wizard Editor - Spend your XP", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 20))
        xp_text = self.font.render(f"XP: {self.exp}", True, YELLOW)
        self.screen.blit(xp_text, (SCREEN_WIDTH//2 - xp_text.get_width()//2, 50))
        start_y = 100
        for i, option in enumerate(self.editor_options):
            color = YELLOW if i == self.editor_index else WHITE
            if "action" in option and option["action"] == "start":
                text_str = f"Start Level {self.level}"
            else:
                key = option["key"]
                if key in self.wizard_config:
                    current = self.wizard_config[key]
                else:
                    current = self.purchased_allies[key]
                text_str = f"{option['name']}: {current} (Cost {option['cost']})"
            text = self.font.render(text_str, True, color)
            self.screen.blit(text, (50, start_y + i * 25))
        instr = self.font.render("Use UP/DOWN and RIGHT/ENTER to upgrade", True, WHITE)
        self.screen.blit(instr, (50, start_y + len(self.editor_options)*25 + 20))
        pygame.display.flip()
    
    def start_level(self):
        self.turn_count = 0
        self.turn_limit = BASE_TURN_LIMIT + (self.level - 1) * 10
        self.portal = None
        self.explored = [[False for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)]
        self.current_unit_index = 0
        self.wizard = Wizard(GRID_WIDTH//2, GRID_HEIGHT - 5, self.wizard_config)
        self.player_units = [self.wizard]
        self.allowed_allies = copy.deepcopy(self.purchased_allies)
        self.enemies = []
        enemy_count = ENEMY_SPAWN_BASE + (self.level - 1) * 2
        for _ in range(enemy_count):
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT // 2)
            self.enemies.append(Enemy(x, y))
        self.update_fog_for_unit(self.wizard)
    
    def update_fog_for_unit(self, unit):
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                x = unit.grid_x + dx
                y = unit.grid_y + dy
                if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                    self.explored[x][y] = True
    
    def handle_game_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if self.game_over or self.game_win:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.__init__()
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e:
                        self.end_turn()
                    elif event.key == pygame.K_TAB:
                        self.current_unit_index = (self.current_unit_index + 1) % len(self.player_units)
                    elif event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                        dx, dy = 0, 0
                        if event.key == pygame.K_UP: dy = -1
                        elif event.key == pygame.K_DOWN: dy = 1
                        elif event.key == pygame.K_LEFT: dx = -1
                        elif event.key == pygame.K_RIGHT: dx = 1
                        self.move_current_unit(dx, dy)
                    elif event.key == pygame.K_1:
                        self.attempt_spawn("Imp")
                    elif event.key == pygame.K_2:
                        self.attempt_spawn("Ogre")
                    elif event.key == pygame.K_3:
                        self.attempt_spawn("Goblin")
    
    def attempt_spawn(self, ally_type):
        if self.player_units[self.current_unit_index] != self.wizard:
            return
        if self.allowed_allies.get(ally_type, 0) > 0:
            new_ally = Ally(self.wizard.grid_x, self.wizard.grid_y, ally_type)
            self.player_units.append(new_ally)
            self.allowed_allies[ally_type] -= 1
            self.update_fog_for_unit(new_ally)
    
    def get_enemy_at(self, x, y):
        for enemy in self.enemies:
            if enemy.grid_x == x and enemy.grid_y == y:
                return enemy
        return None
    
    def perform_attack(self, attacker, defender, original_pos):
        if attacker.strength >= defender.strength:
            damage = attacker.strength
        else:
            damage = max(1, attacker.strength // 2)
        defender.hp -= damage
        effect = AttackEffect(defender.grid_x, defender.grid_y)
        self.attack_effects.append(effect)
        attacker.grid_x, attacker.grid_y = original_pos
        if defender.hp <= 0:
            if defender in self.enemies:
                reward = XP_PER_ENEMY + (defender.strength * 2)
                self.exp += reward
                self.enemies.remove(defender)
    
    def move_current_unit(self, dx, dy):
        unit = self.player_units[self.current_unit_index]
        if unit.ap > 0:
            new_x = unit.grid_x + dx
            new_y = unit.grid_y + dy
            enemy = self.get_enemy_at(new_x, new_y)
            original_pos = (unit.grid_x, unit.grid_y)
            if enemy:
                unit.ap -= 1
                self.perform_attack(unit, enemy, original_pos)
            elif is_tile_walkable(new_x, new_y, self.obstacles):
                unit.grid_x = new_x
                unit.grid_y = new_y
                unit.ap -= 1
                self.update_fog_for_unit(unit)
                if unit == self.wizard and self.portal and self.wizard.grid_x == self.portal.grid_x and self.wizard.grid_y == self.portal.grid_y:
                    self.complete_level()
    
    def end_turn(self):
        self.turn_count += 1
        self.wizard.mana = min(self.wizard.max_mana, self.wizard.mana + self.wizard.speed)
        for unit in self.player_units:
            unit.reset_ap()
        if self.turn_count >= self.turn_limit and self.portal is None:
            while True:
                x = random.randint(0, GRID_WIDTH - 1)
                y = random.randint(0, GRID_HEIGHT - 1)
                if is_tile_walkable(x, y, self.obstacles):
                    self.portal = Portal(x, y)
                    break
        if self.portal:
            self.portal.countdown -= 1
            if self.portal.countdown <= 0:
                self.game_over = True
        self.enemy_turn()
    
    def enemy_turn(self):
        for enemy in self.enemies:
            for _ in range(enemy.ap):
                if line_of_sight(enemy.grid_x, enemy.grid_y, self.wizard.grid_x, self.wizard.grid_y, self.obstacles):
                    target = self.wizard
                else:
                    target = None
                if target:
                    dx = 1 if enemy.grid_x < target.grid_x else -1 if enemy.grid_x > target.grid_x else 0
                    dy = 1 if enemy.grid_y < target.grid_y else -1 if enemy.grid_y > target.grid_y else 0
                    if is_tile_walkable(enemy.grid_x + dx, enemy.grid_y, self.obstacles):
                        enemy.grid_x += dx
                    elif is_tile_walkable(enemy.grid_x, enemy.grid_y + dy, self.obstacles):
                        enemy.grid_y += dy
                    if abs(enemy.grid_x - self.wizard.grid_x) <= 1 and abs(enemy.grid_y - self.wizard.grid_y) <= 1:
                        self.wizard.hp -= enemy.strength
                        if self.wizard.hp <= 0:
                            self.game_over = True
                        break
                else:
                    dx, dy = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
                    if is_tile_walkable(enemy.grid_x + dx, enemy.grid_y + dy, self.obstacles):
                        enemy.grid_x += dx
                        enemy.grid_y += dy
        for enemy in self.enemies:
            enemy.reset_ap()
    
    def complete_level(self):
        bonus = XP_LEVEL_BONUS + (self.level * 2)
        self.exp += bonus
        if self.level >= MAX_LEVEL:
            self.game_win = True
        else:
            self.level += 1
            self.state = "EDITOR"
    
    def draw_game(self):
        game_area = pygame.Surface((GAME_VIEW_WIDTH, GAME_VIEW_HEIGHT))
        # Tile the background with grass
        for tx in range((GAME_VIEW_WIDTH // TILE_SIZE) + 2):
            for ty in range((GAME_VIEW_HEIGHT // TILE_SIZE) + 2):
                # Compute world tile coordinates based on camera offset later.
                pass  # We'll blit the grass tile in the drawing loop below.
        if self.player_units:
            center_x = self.player_units[self.current_unit_index].grid_x * TILE_SIZE + TILE_SIZE//2
            center_y = self.player_units[self.current_unit_index].grid_y * TILE_SIZE + TILE_SIZE//2
        else:
            center_x, center_y = WORLD_WIDTH//2, WORLD_HEIGHT//2
        cam_x = center_x - GAME_VIEW_WIDTH//2
        cam_y = center_y - GAME_VIEW_HEIGHT//2
        cam_x = max(0, min(cam_x, WORLD_WIDTH - GAME_VIEW_WIDTH))
        cam_y = max(0, min(cam_y, WORLD_HEIGHT - GAME_VIEW_HEIGHT))
        # Draw background tiles (grass)
        for tile_x in range(cam_x // TILE_SIZE, (cam_x + GAME_VIEW_WIDTH) // TILE_SIZE + 1):
            for tile_y in range(cam_y // TILE_SIZE, (cam_y + GAME_VIEW_HEIGHT) // TILE_SIZE + 1):
                pos_x = tile_x * TILE_SIZE - cam_x
                pos_y = tile_y * TILE_SIZE - cam_y
                game_area.blit(ASSETS["grass_tile"], (pos_x, pos_y))
        # Draw obstacles using tile images based on type
        for obs in self.obstacles:
            pos_x = obs.grid_x * TILE_SIZE - cam_x
            pos_y = obs.grid_y * TILE_SIZE - cam_y
            if obs.type == "tree":
                game_area.blit(ASSETS["tree_tile"], (pos_x, pos_y))
            elif obs.type == "building":
                game_area.blit(ASSETS["building_tile"], (pos_x, pos_y))
            elif obs.type == "swamp":
                game_area.blit(ASSETS["swamp_tile"], (pos_x, pos_y))
        # Draw portal if exists
        if self.portal:
            rect = pygame.Rect(self.portal.grid_x * TILE_SIZE - cam_x, self.portal.grid_y * TILE_SIZE - cam_y, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(game_area, BLUE, rect)
            p_text = self.font.render(str(self.portal.countdown), True, WHITE)
            game_area.blit(p_text, (rect.x, rect.y))
        # Draw player units using animation frames
        for i, unit in enumerate(self.player_units):
            frame = unit.frames[(pygame.time.get_ticks() // 300) % len(unit.frames)]
            pos = (unit.grid_x * TILE_SIZE - cam_x, unit.grid_y * TILE_SIZE - cam_y)
            game_area.blit(frame, pos)
            hp_text = self.font.render(str(unit.hp), True, WHITE)
            game_area.blit(hp_text, pos)
            if i == self.current_unit_index:
                pygame.draw.rect(game_area, WHITE, (pos[0]-2, pos[1]-2, TILE_SIZE+4, TILE_SIZE+4), 2)
        # Draw enemies
        for enemy in self.enemies:
            frame = enemy.frames[(pygame.time.get_ticks() // 300) % len(enemy.frames)]
            pos = (enemy.grid_x * TILE_SIZE - cam_x, enemy.grid_y * TILE_SIZE - cam_y)
            game_area.blit(frame, pos)
            e_text = self.font.render(str(enemy.hp), True, WHITE)
            game_area.blit(e_text, pos)
        # Draw attack effects
        for effect in self.attack_effects[:]:
            if effect.is_active():
                eff_x = effect.grid_x * TILE_SIZE - cam_x + TILE_SIZE//2
                eff_y = effect.grid_y * TILE_SIZE - cam_y + TILE_SIZE//2
                pygame.draw.circle(game_area, RED, (eff_x, eff_y), 10)
            else:
                self.attack_effects.remove(effect)
        # Apply fog-of-war
        for x in range(cam_x//TILE_SIZE, (cam_x+GAME_VIEW_WIDTH)//TILE_SIZE + 1):
            for y in range(cam_y//TILE_SIZE, (cam_y+GAME_VIEW_HEIGHT)//TILE_SIZE + 1):
                if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                    if not self.explored[x][y]:
                        fog_rect = pygame.Rect(x * TILE_SIZE - cam_x, y * TILE_SIZE - cam_y, TILE_SIZE, TILE_SIZE)
                        s = pygame.Surface((TILE_SIZE, TILE_SIZE))
                        s.set_alpha(200)
                        s.fill(BLACK)
                        game_area.blit(s, fog_rect.topleft)
        self.screen.blit(game_area, (0, 0))
        self.draw_sidebar(cam_x, cam_y)
        if self.game_over:
            over_text = self.font.render("Game Over! Press Enter to restart.", True, RED)
            self.screen.blit(over_text, (GAME_VIEW_WIDTH//2 - over_text.get_width()//2, GAME_VIEW_HEIGHT//2))
        if self.game_win:
            win_text = self.font.render("You Win! Press Enter to restart.", True, GREEN)
            self.screen.blit(win_text, (GAME_VIEW_WIDTH//2 - win_text.get_width()//2, GAME_VIEW_HEIGHT//2))
        pygame.display.flip()
    
    def draw_sidebar(self, cam_x, cam_y):
        sidebar_rect = pygame.Rect(GAME_VIEW_WIDTH, 0, SIDEBAR_WIDTH, SIDEBAR_HEIGHT)
        pygame.draw.rect(self.screen, (50, 50, 50), sidebar_rect)
        minimap_size = 180
        minimap_surface = pygame.Surface((minimap_size, minimap_size))
        minimap_surface.fill((34, 139, 34))
        scale = minimap_size / WORLD_WIDTH
        for obs in self.obstacles:
            x = obs.grid_x * TILE_SIZE * scale
            y = obs.grid_y * TILE_SIZE * scale
            w = obs.grid_width * TILE_SIZE * scale
            h = obs.grid_height * TILE_SIZE * scale
            pygame.draw.rect(minimap_surface, GRAY, (x, y, w, h))
        for unit in self.player_units:
            x = unit.grid_x * TILE_SIZE * scale
            y = unit.grid_y * TILE_SIZE * scale
            size = TILE_SIZE * scale
            pygame.draw.rect(minimap_surface, (0,0,0), (x, y, size, size))  # simple block
        for enemy in self.enemies:
            x = enemy.grid_x * TILE_SIZE * scale
            y = enemy.grid_y * TILE_SIZE * scale
            size = TILE_SIZE * scale
            pygame.draw.rect(minimap_surface, RED, (x, y, size, size))
        if self.portal:
            x = self.portal.grid_x * TILE_SIZE * scale
            y = self.portal.grid_y * TILE_SIZE * scale
            size = TILE_SIZE * scale
            pygame.draw.rect(minimap_surface, BLUE, (x, y, size, size))
        cam_rect = pygame.Rect(cam_x * scale, cam_y * scale, GAME_VIEW_WIDTH * scale, GAME_VIEW_HEIGHT * scale)
        pygame.draw.rect(minimap_surface, YELLOW, cam_rect, 2)
        self.screen.blit(minimap_surface, (sidebar_rect.x + 10, 10))
        stats_start_y = 200
        current_unit = self.player_units[self.current_unit_index]
        if current_unit == self.wizard:
            unit_type = "Wizard"
            extra = f"Mana: {self.wizard.mana}/{self.wizard.max_mana}"
        else:
            unit_type = current_unit.type
            extra = ""
        stats_lines = [
            f"Type: {unit_type}",
            f"HP: {current_unit.hp}",
            f"AP: {current_unit.ap}/{current_unit.max_ap}",
            f"Str: {getattr(current_unit, 'strength', '-')}",
            f"Spd: {getattr(current_unit, 'speed', '-')}",
            extra
        ]
        for i, line in enumerate(stats_lines):
            text = self.font.render(line, True, WHITE)
            self.screen.blit(text, (sidebar_rect.x + 10, stats_start_y + i * 20))
        turn_text = self.font.render(f"Turn: {self.turn_count}/{self.turn_limit}", True, WHITE)
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        xp_text = self.font.render(f"XP: {self.exp}", True, WHITE)
        self.screen.blit(turn_text, (sidebar_rect.x + 10, 375))
        self.screen.blit(level_text, (sidebar_rect.x + 10, 395))
        self.screen.blit(xp_text, (sidebar_rect.x + 10, 415))
        if self.portal:
            portal_text = self.font.render(f"Portal: {self.portal.countdown}", True, WHITE)
            self.screen.blit(portal_text, (sidebar_rect.x + 10, 440))
        controls = [
            "Controls:",
            "Arrows: Move/Attack",
            "TAB: Next Unit",
            "1/2/3: Spawn Ally",
            "E: End Turn"
        ]
        for i, line in enumerate(controls):
            text = self.font.render(line, True, WHITE)
            self.screen.blit(text, (sidebar_rect.x + 10, 500 + i * 20))
    
    def run(self):
        while True:
            self.clock.tick(FPS)
            if self.state == "EDITOR":
                self.handle_editor_events()
                self.draw_editor()
            elif self.state == "GAME":
                self.handle_game_events()
                self.draw_game()

if __name__ == "__main__":
    game = Game()
    game.run()
