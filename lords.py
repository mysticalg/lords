import pygame
import sys
import random
import math
import copy
import os

# --- Global Constants ---
TILE_SIZE = 40
GRID_WIDTH, GRID_HEIGHT = 32, 24
WORLD_WIDTH = TILE_SIZE * GRID_WIDTH   # 2000 pixels wide
WORLD_HEIGHT = TILE_SIZE * GRID_HEIGHT   # 2000 pixels tall

GAME_VIEW_WIDTH, GAME_VIEW_HEIGHT = 600, 600
SIDEBAR_WIDTH, SIDEBAR_HEIGHT = 200, 600
SCREEN_WIDTH, SCREEN_HEIGHT = GAME_VIEW_WIDTH + SIDEBAR_WIDTH, 600

FPS = 60

# Colors
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

# --- Base Stats & Costs ---
BASE_WIZARD_CONFIG = {
    "max_mana": 100,
    "max_ap": 5,
    "strength": 5,
    "stamina": 100  # HP
}
WIZARD_SPEED = 3

ALLY_TYPES = {
    "Imp": {
         "color": ORANGE,
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
         "auto_roam": False,
         "mana_cost": 15
    },
    "Ghost": {
         "color": (200, 200, 255),
         "max_ap": 6,
         "hp": 12,
         "strength": 6,
         "speed": 4,
         "intelligence": 5,
         "auto_roam": False,
         "mana_cost": 30
    },
    "Demon": {
         "color": (255, 100, 100),
         "max_ap": 4,
         "hp": 30,
         "strength": 12,
         "speed": 3,
         "intelligence": 4,
         "auto_roam": False,
         "mana_cost": 50
    },
    "Zombie": {
         "color": (100, 150, 100),
         "max_ap": 4,
         "hp": 20,
         "strength": 8,
         "speed": 2,
         "intelligence": 1,
         "auto_roam": False,
         "mana_cost": 35
    },
    "Bat": {
         "color": (50, 50, 50),
         "max_ap": 8,
         "hp": 6,
         "strength": 4,
         "speed": 8,
         "intelligence": 2,
         "auto_roam": True,
         "mana_cost": 20
    }
}
ALLY_PURCHASE_COSTS = {
    "Imp": 30,
    "Ogre": 50,
    "Goblin": 25,
    "Ghost": 40,
    "Demon": 70,
    "Zombie": 45,
    "Bat": 30
}
UPGRADE_COSTS = {
    "max_mana": 20,
    "max_ap": 15,
    "strength": 25,
    "stamina": 25
}

ENEMY_STATS = {
    "color": RED,
    "max_ap": 2,
    "hp": 15,
    "strength": 5
}

XP_PER_ENEMY = 10
XP_LEVEL_BONUS = 50
BASE_TURN_LIMIT = 40
ENEMY_SPAWN_BASE = 10
MAX_LEVEL = 100
PORTAL_COUNTDOWN = 10

MAP_TEMPLATES = [
    {
        "name": "Borderlands",
        "trees": [(2, 2, 3, 2), (8, 1, 4, 2), (21, 3, 5, 2), (27, 8, 3, 2)],
        "buildings": [(4, 10, 2, 2), (16, 14, 2, 2), (24, 16, 2, 2)],
        "swamps": [(11, 6, 3, 3), (18, 9, 3, 2)],
        "structures": [(6, 4, 7, 6), (20, 12, 8, 7)],
        "chests": [(3, 20), (14, 11), (29, 19)],
        "enemy_spawns": [(1, 1), (30, 1), (30, 22), (1, 22), (15, 2), (17, 21)],
    },
    {
        "name": "Cursed Marsh",
        "trees": [(3, 3, 4, 2), (9, 18, 4, 2), (24, 2, 5, 2)],
        "buildings": [(2, 12, 2, 2), (14, 4, 2, 2), (26, 15, 2, 2)],
        "swamps": [(6, 7, 4, 4), (12, 10, 5, 4), (20, 8, 4, 4)],
        "structures": [(4, 2, 9, 7), (19, 14, 10, 8)],
        "chests": [(5, 20), (15, 15), (27, 6), (30, 21)],
        "enemy_spawns": [(2, 2), (29, 2), (28, 20), (5, 12), (16, 6), (22, 18), (30, 10)],
    },
    {
        "name": "Iron Keep",
        "trees": [(1, 2, 3, 2), (27, 3, 3, 2), (10, 20, 6, 2)],
        "buildings": [(7, 5, 2, 2), (12, 5, 2, 2), (17, 5, 2, 2), (22, 5, 2, 2)],
        "swamps": [(5, 15, 3, 3), (24, 15, 3, 3)],
        "structures": [(9, 8, 14, 10)],
        "chests": [(15, 12), (10, 10), (21, 10), (15, 17)],
        "enemy_spawns": [(2, 1), (29, 1), (2, 22), (29, 22), (9, 6), (23, 6), (15, 3), (15, 21)],
    },
    {
        "name": "Chaos Citadel",
        "trees": [(2, 5, 3, 2), (27, 5, 3, 2), (2, 17, 3, 2), (27, 17, 3, 2)],
        "buildings": [(6, 3, 2, 2), (24, 3, 2, 2), (6, 19, 2, 2), (24, 19, 2, 2)],
        "swamps": [(11, 3, 3, 3), (18, 3, 3, 3), (11, 18, 3, 3), (18, 18, 3, 3)],
        "structures": [(8, 7, 16, 10)],
        "chests": [(9, 8), (22, 8), (9, 15), (22, 15), (16, 12)],
        "enemy_spawns": [(1, 1), (30, 1), (1, 22), (30, 22), (16, 1), (16, 22), (1, 12), (30, 12)],
    },
]

ENEMY_ARCHETYPES = [
    {"name": "Brute", "hp": 18, "max_ap": 2, "strength": 6, "ranged": False, "spellcaster": False},
    {"name": "Hunter", "hp": 14, "max_ap": 3, "strength": 4, "ranged": True, "spellcaster": False},
    {"name": "Sorcerer", "hp": 12, "max_ap": 3, "strength": 3, "ranged": True, "spellcaster": True},
]

SPELLBOOK = {
    pygame.K_z: {"name": "Magic Bolt", "mana": 8, "range": 6},
    pygame.K_x: {"name": "Heal", "mana": 10},
    pygame.K_c: {"name": "Teleport", "mana": 14, "range": 8},
    pygame.K_v: {"name": "Fire Storm", "mana": 18, "radius": 1},
    pygame.K_b: {"name": "Haste", "mana": 12},
}

# --- Asset Loader ---
def load_image(name):
    path = os.path.join("assets", name)
    try:
        img = pygame.image.load(path)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        img = pygame.Surface((TILE_SIZE, TILE_SIZE))
        img.fill(RED)
    return img

def load_anim(name):
    return [load_image(f"{name}_0.png"), load_image(f"{name}_1.png")]

def load_assets():
    assets = {}
    assets["wizard"] = load_anim("wizard")
    assets["imp"] = load_anim("imp")
    assets["ogre"] = load_anim("ogre")
    assets["goblin"] = load_anim("goblin")
    assets["ghost"] = load_anim("ghost")
    assets["demon"] = load_anim("demon")
    assets["zombie"] = load_anim("zombie")
    assets["bat"] = load_anim("bat")
    assets["enemy"] = load_anim("enemy")
    assets["grass_tile"] = load_image("grass_tile.png")
    assets["tree_tile"] = load_image("tree_tile.png")
    assets["building_tile"] = load_image("building_tile.png")
    assets["swamp_tile"] = load_image("swamp_tile.png")
    assets["wall_tile"] = load_image("wall_tile.png")
    assets["floor_tile"] = load_image("floor_tile.png")
    assets["door_tile"] = load_image("door_tile.png")
    assets["chest_closed"] = load_image("chest_closed.png")
    assets["chest_open"] = load_image("chest_open.png")
    return assets

ASSETS = load_assets()

# --- Helper Functions for Toroidal Map ---
def mod_coord(x, max_val):
    return x % max_val

def world_to_screen(x, cam, world_size, view_size):
    dx = ((x - cam + world_size/2) % world_size) - world_size/2
    return int(view_size//2 + dx)

def grid_distance(x0, y0, x1, y1):
    dx = abs(x0 - x1)
    dy = abs(y0 - y1)
    dx = min(dx, GRID_WIDTH - dx)
    dy = min(dy, GRID_HEIGHT - dy)
    return dx + dy

def movement_cost_for_tile(x, y, obstacles, flying=False):
    if flying:
        return 1
    x = mod_coord(x, GRID_WIDTH)
    y = mod_coord(y, GRID_HEIGHT)
    for obs in obstacles:
        if obs.grid_x <= x < obs.grid_x + obs.grid_width and obs.grid_y <= y < obs.grid_y + obs.grid_height:
            if obs.type == "swamp":
                return 2
            return 99
    return 1

# --- Helper Functions ---
def is_tile_walkable(x, y, obstacles, structures, flying=False):
    x = mod_coord(x, GRID_WIDTH)
    y = mod_coord(y, GRID_HEIGHT)
    if not flying:
        for obs in obstacles:
            if (obs.grid_x <= x < obs.grid_x + obs.grid_width and
                obs.grid_y <= y < obs.grid_y + obs.grid_height):
                return False
        for struct in structures:
            if struct.grid_x <= x < struct.grid_x + struct.width and struct.grid_y <= y < struct.grid_y + struct.height:
                local_x = x - struct.grid_x
                local_y = y - struct.grid_y
                tile = struct.tile_map[local_x][local_y]
                if tile in ("wall", "door_closed"):
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
    for (x, y) in get_line(x0, y0, x1, y1):
        for obs in obstacles:
            if (obs.grid_x <= x < obs.grid_x + obs.grid_width and
                obs.grid_y <= y < obs.grid_y + obs.grid_height):
                return False
    return True

# --- Attack Visual Effect ---
class AttackEffect:
    def __init__(self, grid_x, grid_y):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.start_time = pygame.time.get_ticks()
        self.duration = 200
    def is_active(self):
        return pygame.time.get_ticks() - self.start_time < self.duration

# --- Structure Class ---
class Structure:
    def __init__(self, grid_x, grid_y, width, height):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.width = width
        self.height = height
        self.tile_map = [["floor" for _ in range(height)] for _ in range(width)]
        for i in range(width):
            self.tile_map[i][0] = "wall"
            self.tile_map[i][height-1] = "wall"
        for j in range(height):
            self.tile_map[0][j] = "wall"
            self.tile_map[width-1][j] = "wall"
        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top":
            door_x = random.randint(1, width-2)
            door_y = 0
        elif side == "bottom":
            door_x = random.randint(1, width-2)
            door_y = height-1
        elif side == "left":
            door_x = 0
            door_y = random.randint(1, height-2)
        else:
            door_x = width-1
            door_y = random.randint(1, height-2)
        self.door_position = (door_x, door_y)
        self.door_open = False
        self.tile_map[door_x][door_y] = "door_closed"
    def toggle_door(self):
        self.door_open = not self.door_open
        door_x, door_y = self.door_position
        if self.door_open:
            self.tile_map[door_x][door_y] = "floor"
        else:
            self.tile_map[door_x][door_y] = "door_closed"

# --- Chest Class ---
class Chest:
    def __init__(self, grid_x, grid_y):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.locked = random.choice([True, False])
        self.opened = False
        possible_items = ["ruby", "gemstone", "diamond", "gold", "key"]
        count = random.randint(1, 3)
        self.contents = random.sample(possible_items, count)
    def open(self, inventory):
        if self.locked:
            if inventory.get("key", 0) > 0:
                inventory["key"] -= 1
                self.opened = True
                return self.contents
            else:
                return None
        else:
            self.opened = True
            return self.contents

# --- GamePlayer Class (for each player) ---
class GamePlayer:
    def __init__(self, wizard_config, purchased_allies, start_pos):
        self.wizard_config = wizard_config
        self.purchased_allies = purchased_allies
        self.wizard = Wizard(start_pos[0], start_pos[1], wizard_config)
        self.player_units = [self.wizard]
        self.allowed_allies = copy.deepcopy(purchased_allies)
        # Each player gets their own fog-of-war grid (initially unexplored)
        self.explored = [[False for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)]
        self.current_unit_index = 0
        self.inventory = {}
        self.look_mode = False
        self.look_cursor_x = start_pos[0]
        self.look_cursor_y = start_pos[1]
        self.xp = 0
        self.level = 1
        self.spellcasting = 1
        self.haste_turns = 0

    def gain_xp(self, amount):
        self.xp += amount
        leveled = False
        required = self.level * 50
        while self.xp >= required:
            self.xp -= required
            self.level += 1
            self.wizard.max_mana += 5
            self.wizard.mana = self.wizard.max_mana
            self.wizard.max_hp += 5
            self.wizard.hp = self.wizard.max_hp
            self.wizard.strength += 1
            self.spellcasting += 1
            leveled = True
            required = self.level * 50
        return leveled

    def update_fog_for_unit(self, unit):
        # Reveal a radius of 3 tiles around the unit.
        radius = 3
        for dx in range(-radius, radius+1):
            for dy in range(-radius, radius+1):
                x = (unit.grid_x + dx) % GRID_WIDTH
                y = (unit.grid_y + dy) % GRID_HEIGHT
                self.explored[x][y] = True

# --- Entity Classes with Animation and Attributes ---
class Wizard:
    def __init__(self, grid_x, grid_y, config):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.max_mana = config["max_mana"]
        self.mana = config["max_mana"]
        self.max_ap = config["max_ap"]
        self.ap = config["max_ap"]
        self.max_hp = config["stamina"]
        self.hp = config["stamina"]
        self.strength = config["strength"]
        self.speed = WIZARD_SPEED
        self.frames = ASSETS["wizard"]
        self.can_open_doors = True
        self.flying = False
    def reset_ap(self):
        self.ap = self.max_ap

class Ally:
    def __init__(self, grid_x, grid_y, ally_type):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.type = ally_type
        stats = ALLY_TYPES[ally_type]
        self.max_hp = stats["hp"]
        self.hp = stats["hp"]
        self.max_ap = stats["max_ap"]
        self.ap = stats["max_ap"]
        self.strength = stats["strength"]
        self.speed = stats["speed"]
        self.intelligence = stats["intelligence"]
        self.auto_roam = stats["auto_roam"]
        self.frames = ASSETS[ally_type.lower()]
        if ally_type in ["Imp", "Ogre", "Goblin", "Demon"]:
            self.can_open_doors = True
            self.flying = False
        elif ally_type == "Ghost":
            self.can_open_doors = False
            self.flying = True
        elif ally_type == "Zombie":
            self.can_open_doors = False
            self.flying = False
        elif ally_type == "Bat":
            self.can_open_doors = False
            self.flying = True
        else:
            self.can_open_doors = True
            self.flying = False
    def reset_ap(self):
        self.ap = self.max_ap

class Enemy:
    def __init__(self, grid_x, grid_y, archetype=None):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.archetype = archetype or random.choice(ENEMY_ARCHETYPES)
        self.max_hp = self.archetype["hp"]
        self.hp = self.max_hp
        self.max_ap = self.archetype["max_ap"]
        self.ap = self.max_ap
        self.strength = self.archetype["strength"]
        self.ranged = self.archetype["ranged"]
        self.spellcaster = self.archetype["spellcaster"]
        self.frames = ASSETS["enemy"]
        self.can_open_doors = False
        self.flying = False
    def reset_ap(self):
        self.ap = self.max_ap

class Obstacle:
    def __init__(self, grid_x, grid_y, grid_width, grid_height, obs_type):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.type = obs_type

class Portal:
    def __init__(self, grid_x, grid_y):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.countdown = PORTAL_COUNTDOWN

# --- Helper: Starting positions for players ---
def get_start_pos(player_index, total_players):
    if total_players == 1:
        return (GRID_WIDTH//2, GRID_HEIGHT//2)
    elif total_players == 2:
        return [(0, 0), (GRID_WIDTH-1, GRID_HEIGHT-1)][player_index]
    elif total_players == 3:
        return [(0, 0), (GRID_WIDTH-1, 0), (0, GRID_HEIGHT-1)][player_index]
    else:
        positions = [(0, 0), (GRID_WIDTH-1, 0), (0, GRID_HEIGHT-1), (GRID_WIDTH-1, GRID_HEIGHT-1)]
        return positions[player_index]

# --- Main Game Class ---
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Multiplayer Turn-Based Lords of Chaos Clone")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 16)
        # Game state: "PLAYER_COUNT", "EDITOR", "GAME"
        self.state = "PLAYER_COUNT"
        self.selected_num = 1
        self.num_players = 1
        self.player_configs = []  # List of (wizard_config, purchased_allies) for each player
        self.default_wizard = copy.deepcopy(BASE_WIZARD_CONFIG)
        self.default_allies = {"Imp": 0, "Ogre": 0, "Goblin": 0, "Ghost": 0, "Demon": 0, "Zombie": 0, "Bat": 0}
        self.players = []  # List of GamePlayer objects
        self.active_player_index = 0
        self.editor_options = [
            {"name": "Max Mana (+10)", "key": "max_mana", "increment": 10, "cost": UPGRADE_COSTS["max_mana"]},
            {"name": "Max AP (+1)", "key": "max_ap", "increment": 1, "cost": UPGRADE_COSTS["max_ap"]},
            {"name": "Strength (+1)", "key": "strength", "increment": 1, "cost": UPGRADE_COSTS["strength"]},
            {"name": "Stamina (+10)", "key": "stamina", "increment": 10, "cost": UPGRADE_COSTS["stamina"]},
            {"name": "Buy Imp", "key": "Imp", "increment": 1, "cost": ALLY_PURCHASE_COSTS["Imp"]},
            {"name": "Buy Ogre", "key": "Ogre", "increment": 1, "cost": ALLY_PURCHASE_COSTS["Ogre"]},
            {"name": "Buy Goblin", "key": "Goblin", "increment": 1, "cost": ALLY_PURCHASE_COSTS["Goblin"]},
            {"name": "Buy Ghost", "key": "Ghost", "increment": 1, "cost": ALLY_PURCHASE_COSTS["Ghost"]},
            {"name": "Buy Demon", "key": "Demon", "increment": 1, "cost": ALLY_PURCHASE_COSTS["Demon"]},
            {"name": "Buy Zombie", "key": "Zombie", "increment": 1, "cost": ALLY_PURCHASE_COSTS["Zombie"]},
            {"name": "Buy Bat", "key": "Bat", "increment": 1, "cost": ALLY_PURCHASE_COSTS["Bat"]},
            {"name": "Finish Editor", "action": "finish"}
        ]
        self.editor_index = 0
        self.current_editor_player = 0
        self.exp = 400  # Each player starts with 400 XP
        # Global game settings
        self.level = 1
        self.turn_count = 0
        self.turn_limit = BASE_TURN_LIMIT
        self.portal = None
        self.map_index = 0
        self.active_map_name = MAP_TEMPLATES[0]["name"]
        self.spell_message = ""
        self.enemies = []
        self.obstacles = []
        self.structures = []
        self.chests = []
        self.setup_world()
        self.attack_effects = []
        self.state_inventory = {}
        self.game_over = False
        self.game_win = False
        # NEW: Restart flag for safe restarting
        self.restart_flag = False

    # --- Shared target detection ---
    def get_target_at(self, x, y, current_player):
        # Check units from other players.
        for player in self.players:
            if player == current_player:
                continue
            for unit in player.player_units:
                if unit.grid_x == x and unit.grid_y == y:
                    return unit
        # Check computer-controlled enemies.
        for enemy in self.enemies:
            if enemy.grid_x == x and enemy.grid_y == y:
                return enemy
        return None

    # --- State: PLAYER_COUNT ---
    def handle_player_count_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.selected_num = 1
                elif event.key == pygame.K_2:
                    self.selected_num = 2
                elif event.key == pygame.K_3:
                    self.selected_num = 3
                elif event.key == pygame.K_4:
                    self.selected_num = 4
                elif event.key == pygame.K_RETURN:
                    self.num_players = self.selected_num
                    for _ in range(self.num_players):
                        self.player_configs.append((copy.deepcopy(self.default_wizard), copy.deepcopy(self.default_allies)))
                    self.state = "EDITOR"
                    self.current_editor_player = 0
                    self.exp = 400
                    self.editor_index = 0

    def draw_player_count(self):
        pygame.mixer.init()
        pygame.mixer.music.load("assets/editor_music.mp3")
        #pygame.mixer.music.play(-1)
        self.screen.fill(BLACK)
        title = self.font.render("Select Number of Players (1-4):", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 200))
        choice_text = self.font.render(f"Current Choice: {self.selected_num}", True, YELLOW)
        self.screen.blit(choice_text, (SCREEN_WIDTH//2 - choice_text.get_width()//2, 250))
        instr = self.font.render("Press 1-4 then ENTER", True, WHITE)
        self.screen.blit(instr, (SCREEN_WIDTH//2 - instr.get_width()//2, 300))
        pygame.display.flip()

    # --- Editor State for Each Player ---
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
                    if "action" in option and option["action"] == "finish":
                        self.player_configs[self.current_editor_player] = (
                            copy.deepcopy(self.default_wizard),
                            copy.deepcopy(self.default_allies)
                        )
                        self.default_wizard = copy.deepcopy(BASE_WIZARD_CONFIG)
                        self.default_allies = {"Imp": 0, "Ogre": 0, "Goblin": 0, "Ghost": 0, "Demon": 0, "Zombie": 0, "Bat": 0}
                        self.current_editor_player += 1
                        if self.current_editor_player >= self.num_players:
                            self.players = []
                            for i, config in enumerate(self.player_configs):
                                start_pos = get_start_pos(i, self.num_players)
                                player = GamePlayer(config[0], config[1], start_pos)
                                # Initially update fog around starting unit.
                                player.update_fog_for_unit(player.wizard)
                                self.players.append(player)
                            self.state = "GAME"
                            self.active_player_index = 0
                        else:
                            self.exp = 400
                            self.editor_index = 0
                    else:
                        if self.exp >= option["cost"]:
                            self.exp -= option["cost"]
                            key = option["key"]
                            if key in self.default_wizard:
                                self.default_wizard[key] += option["increment"]
                            else:
                                self.default_allies[key] += option["increment"]

    def draw_editor(self):
        self.screen.fill(BLACK)
        title = self.font.render(f"Player {self.current_editor_player+1} Editor - Spend your XP", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 20))
        xp_text = self.font.render(f"XP: {self.exp}", True, YELLOW)
        self.screen.blit(xp_text, (SCREEN_WIDTH//2 - xp_text.get_width()//2, 50))
        start_y = 100
        for i, option in enumerate(self.editor_options):
            color = YELLOW if i == self.editor_index else WHITE
            if "action" in option and option["action"] == "finish":
                text_str = "Finish Editor for this player"
            else:
                key = option["key"]
                if key in self.default_wizard:
                    current = self.default_wizard[key]
                else:
                    current = self.default_allies[key]
                text_str = f"{option['name']}: {current} (Cost {option['cost']})"
            text = self.font.render(text_str, True, color)
            self.screen.blit(text, (50, start_y + i * 25))
        instr = self.font.render("Use UP/DOWN & RIGHT/ENTER to upgrade", True, WHITE)
        self.screen.blit(instr, (50, start_y + len(self.editor_options)*25 + 20))
        pygame.display.flip()

    # --- Global Map Setup (shared among players) ---
    def place_obstacle_rects(self, rects, obs_type):
        for x, y, w, h in rects:
            self.obstacles.append(Obstacle(x, y, w, h, obs_type))

    def setup_world(self):
        template = MAP_TEMPLATES[self.map_index % len(MAP_TEMPLATES)]
        self.active_map_name = template["name"]
        self.obstacles = []
        self.place_obstacle_rects(template["trees"], "tree")
        self.place_obstacle_rects(template["buildings"], "building")
        self.place_obstacle_rects(template["swamps"], "swamp")

        self.structures = []
        for sx, sy, sw, sh in template["structures"]:
            self.structures.append(Structure(sx, sy, sw, sh))

        self.chests = []
        for cx, cy in template["chests"]:
            if is_tile_walkable(cx, cy, self.obstacles, self.structures, flying=False):
                self.chests.append(Chest(cx, cy))

        self.enemies = []
        stage_bonus = max(0, self.level - 1)
        spawn_points = list(template["enemy_spawns"])
        for i, (ex, ey) in enumerate(spawn_points):
            archetype = ENEMY_ARCHETYPES[(i + self.level) % len(ENEMY_ARCHETYPES)]
            if is_tile_walkable(ex, ey, self.obstacles, self.structures, flying=False):
                enemy = Enemy(ex, ey, archetype=archetype)
                enemy.max_hp += stage_bonus * 2
                enemy.hp = enemy.max_hp
                enemy.strength += stage_bonus // 2
                self.enemies.append(enemy)

    def get_tile_info(self, x, y):
        for player in self.players:
            for unit in player.player_units:
                if unit.grid_x == x and unit.grid_y == y:
                    label = "Wizard" if unit == player.wizard else unit.type
                    return f"{label} HP:{unit.hp}"
        for enemy in self.enemies:
            if enemy.grid_x == x and enemy.grid_y == y:
                return f"Enemy HP:{enemy.hp}"
        for chest in self.chests:
            if chest.grid_x == x and chest.grid_y == y:
                return "Opened Chest" if chest.opened else "Chest"
        for obs in self.obstacles:
            if obs.grid_x <= x < obs.grid_x + obs.grid_width and obs.grid_y <= y < obs.grid_y + obs.grid_height:
                return obs.type.title()
        return "Grass"

    def cast_spell(self, key, player):
        spell = SPELLBOOK.get(key)
        if not spell:
            return
        wizard = player.wizard
        if player.player_units[player.current_unit_index] != wizard:
            self.spell_message = "Select wizard to cast."
            return
        if wizard.ap <= 0:
            self.spell_message = "No AP left."
            return
        if wizard.mana < spell["mana"]:
            self.spell_message = "Not enough mana."
            return

        if spell["name"] == "Magic Bolt":
            target = self.find_spell_target(wizard.grid_x, wizard.grid_y, spell["range"], player)
            if not target:
                self.spell_message = "No target for Magic Bolt."
                return
            wizard.mana -= spell["mana"]
            wizard.ap -= 1
            target.hp -= wizard.strength + player.spellcasting
            self.attack_effects.append(AttackEffect(target.grid_x, target.grid_y))
            if target.hp <= 0 and target in self.enemies:
                self.enemies.remove(target)
                player.gain_xp(XP_PER_ENEMY + 8)
                self.exp += XP_PER_ENEMY
            self.spell_message = "Magic Bolt cast!"
        elif spell["name"] == "Heal":
            wizard.mana -= spell["mana"]
            wizard.ap -= 1
            wizard.hp = min(wizard.max_hp, wizard.hp + 18 + player.spellcasting)
            self.spell_message = "Heal cast."
        elif spell["name"] == "Teleport":
            dx, dy = random.randint(-spell["range"], spell["range"]), random.randint(-spell["range"], spell["range"])
            tx = (wizard.grid_x + dx) % GRID_WIDTH
            ty = (wizard.grid_y + dy) % GRID_HEIGHT
            if not is_tile_walkable(tx, ty, self.obstacles, self.structures, wizard.flying):
                self.spell_message = "Teleport fizzled."
                return
            wizard.mana -= spell["mana"]
            wizard.ap -= 1
            wizard.grid_x, wizard.grid_y = tx, ty
            player.update_fog_for_unit(wizard)
            self.spell_message = "Teleport success."
        elif spell["name"] == "Fire Storm":
            wizard.mana -= spell["mana"]
            wizard.ap -= 1
            for enemy in self.enemies[:]:
                if grid_distance(wizard.grid_x, wizard.grid_y, enemy.grid_x, enemy.grid_y) <= spell["radius"] + 2:
                    enemy.hp -= 8 + player.spellcasting
                    self.attack_effects.append(AttackEffect(enemy.grid_x, enemy.grid_y))
                    if enemy.hp <= 0:
                        self.enemies.remove(enemy)
                        player.gain_xp(XP_PER_ENEMY + 6)
                        self.exp += XP_PER_ENEMY
            self.spell_message = "Fire Storm cast."
        elif spell["name"] == "Haste":
            wizard.mana -= spell["mana"]
            wizard.ap -= 1
            player.haste_turns = 3
            self.spell_message = "Haste active for 3 turns."

    def find_spell_target(self, x, y, max_range, caster_player):
        best_target = None
        best_dist = 999
        for enemy in self.enemies:
            dist = grid_distance(x, y, enemy.grid_x, enemy.grid_y)
            if dist <= max_range and dist < best_dist:
                best_target = enemy
                best_dist = dist
        for player in self.players:
            if player == caster_player:
                continue
            for unit in player.player_units:
                dist = grid_distance(x, y, unit.grid_x, unit.grid_y)
                if dist <= max_range and dist < best_dist:
                    best_target = unit
                    best_dist = dist
        return best_target

    # --- Game State Methods ---
    def handle_game_events(self):
        active_player = self.players[self.active_player_index]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            # When the game is over or won, wait for ENTER to restart.
            if self.game_over or self.game_win:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    # Instead of reinitializing here, we set a flag.
                    self.restart_flag = True
                return
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_l:
                        active_player.look_mode = not active_player.look_mode
                        if active_player.look_mode:
                            active_player.look_cursor_x = active_player.player_units[active_player.current_unit_index].grid_x
                            active_player.look_cursor_y = active_player.player_units[active_player.current_unit_index].grid_y
                    elif active_player.look_mode:
                        if event.key == pygame.K_UP:
                            active_player.look_cursor_y = max(0, active_player.look_cursor_y - 1)
                        elif event.key == pygame.K_DOWN:
                            active_player.look_cursor_y = min(GRID_HEIGHT - 1, active_player.look_cursor_y + 1)
                        elif event.key == pygame.K_LEFT:
                            active_player.look_cursor_x = max(0, active_player.look_cursor_x - 1)
                        elif event.key == pygame.K_RIGHT:
                            active_player.look_cursor_x = min(GRID_WIDTH - 1, active_player.look_cursor_x + 1)
                    else:
                        if event.key == pygame.K_d:
                            unit = active_player.player_units[active_player.current_unit_index]
                            if unit.can_open_doors:
                                for struct in self.structures:
                                    door_x, door_y = struct.door_position
                                    world_door_x = (struct.grid_x + door_x) % GRID_WIDTH
                                    world_door_y = (struct.grid_y + door_y) % GRID_HEIGHT
                                    if abs(unit.grid_x - world_door_x) + abs(unit.grid_y - world_door_y) <= 1:
                                        struct.toggle_door()
                                        break
                        elif event.key == pygame.K_o:
                            unit = active_player.player_units[active_player.current_unit_index]
                            for chest in self.chests:
                                if chest.grid_x == unit.grid_x and chest.grid_y == unit.grid_y and not chest.opened:
                                    contents = chest.open(active_player.inventory)
                                    if contents is None:
                                        print("Chest is locked and you have no key!")
                                    else:
                                        print(f"Chest opened! You found: {contents}")
                                        for item in contents:
                                            active_player.inventory[item] = active_player.inventory.get(item, 0) + 1
                                    break
                        elif event.key == pygame.K_e:
                            self.end_turn()
                        elif event.key == pygame.K_TAB:
                            active_player.current_unit_index = (active_player.current_unit_index + 1) % len(active_player.player_units)
                        elif event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                            dx = dy = 0
                            if event.key == pygame.K_UP: dy = -1
                            elif event.key == pygame.K_DOWN: dy = 1
                            elif event.key == pygame.K_LEFT: dx = -1
                            elif event.key == pygame.K_RIGHT: dx = 1
                            self.move_current_unit(dx, dy, active_player)
                        elif event.key == pygame.K_1:
                            self.attempt_spawn("Imp", active_player)
                        elif event.key == pygame.K_2:
                            self.attempt_spawn("Ogre", active_player)
                        elif event.key == pygame.K_3:
                            self.attempt_spawn("Goblin", active_player)
                        elif event.key == pygame.K_4:
                            self.attempt_spawn("Ghost", active_player)
                        elif event.key == pygame.K_5:
                            self.attempt_spawn("Demon", active_player)
                        elif event.key == pygame.K_6:
                            self.attempt_spawn("Zombie", active_player)
                        elif event.key == pygame.K_7:
                            self.attempt_spawn("Bat", active_player)
                        elif event.key in SPELLBOOK:
                            self.cast_spell(event.key, active_player)
    
    def attempt_spawn(self, ally_type, player):
        if player.player_units[player.current_unit_index] != player.wizard:
            return
        if player.allowed_allies.get(ally_type, 0) > 0:
            new_ally = Ally(player.wizard.grid_x, player.wizard.grid_y, ally_type)
            player.player_units.append(new_ally)
            player.allowed_allies[ally_type] -= 1
    
    def get_enemy_at(self, x, y):
        x = x % GRID_WIDTH
        y = y % GRID_HEIGHT
        for enemy in self.enemies:
            if enemy.grid_x == x and enemy.grid_y == y:
                return enemy
        return None
    
    def perform_attack(self, attacker, defender, original_pos, player):
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
                player.gain_xp(reward)
                self.exp += reward
                self.enemies.remove(defender)
    
    def move_current_unit(self, dx, dy, player):
        unit = player.player_units[player.current_unit_index]
        if unit.ap <= 0:
            return
        new_x = (unit.grid_x + dx) % GRID_WIDTH
        new_y = (unit.grid_y + dy) % GRID_HEIGHT
        original_pos = (unit.grid_x, unit.grid_y)
        target = self.get_target_at(new_x, new_y, player)
        if target:
            unit.ap -= 1
            self.perform_attack(unit, target, original_pos, player)
            return
        if not is_tile_walkable(new_x, new_y, self.obstacles, self.structures, unit.flying):
            return
        blocked = False
        for struct in self.structures:
            if struct.grid_x <= new_x < struct.grid_x + struct.width and struct.grid_y <= new_y < struct.grid_y + struct.height:
                local_x = new_x - struct.grid_x
                local_y = new_y - struct.grid_y
                if struct.tile_map[local_x][local_y] == "door_closed" and not unit.flying:
                    blocked = True
                break
        if blocked:
            return
        move_cost = movement_cost_for_tile(new_x, new_y, self.obstacles, unit.flying)
        if player.haste_turns > 0:
            move_cost = max(1, move_cost - 1)
        if move_cost > unit.ap:
            self.spell_message = "Not enough AP for terrain."
            return
        unit.grid_x = new_x
        unit.grid_y = new_y
        unit.ap -= move_cost
        player.update_fog_for_unit(unit)
        if unit == player.wizard and self.portal and player.wizard.grid_x == self.portal.grid_x and player.wizard.grid_y == self.portal.grid_y:
            self.complete_level()
    
    def end_turn(self):
        self.turn_count += 1
        active_player = self.players[self.active_player_index]
        active_player.wizard.mana = min(active_player.wizard.max_mana, active_player.wizard.mana + active_player.wizard.speed + active_player.spellcasting)
        for unit in active_player.player_units:
            unit.reset_ap()
            if active_player.haste_turns > 0:
                unit.ap += 1
        if active_player.haste_turns > 0:
            active_player.haste_turns -= 1
        if self.turn_count >= self.turn_limit and self.portal is None:
            while True:
                x = random.randint(0, GRID_WIDTH - 1)
                y = random.randint(0, GRID_HEIGHT - 1)
                if is_tile_walkable(x, y, self.obstacles, self.structures, False):
                    self.portal = Portal(x, y)
                    break
        if self.portal:
            self.portal.countdown -= 1
            if self.portal.countdown <= 0:
                self.game_over = True
        self.active_player_index = (self.active_player_index + 1) % len(self.players)
        if self.active_player_index == 0:
            self.enemy_turn()
    
    def get_nearest_enemy_target(self, enemy):
        best_target = None
        best_dist = 999
        for player in self.players:
            for unit in player.player_units:
                dist = grid_distance(enemy.grid_x, enemy.grid_y, unit.grid_x, unit.grid_y)
                if dist < best_dist:
                    best_dist = dist
                    best_target = unit
        return best_target, best_dist

    def enemy_turn(self):
        for enemy in self.enemies:
            for _ in range(enemy.ap):
                target, dist = self.get_nearest_enemy_target(enemy)
                if not target:
                    break

                if enemy.spellcaster and dist <= 5 and random.random() < 0.35:
                    target.hp -= (enemy.strength + 2)
                    self.attack_effects.append(AttackEffect(target.grid_x, target.grid_y))
                elif enemy.ranged and dist <= 4 and line_of_sight(enemy.grid_x, enemy.grid_y, target.grid_x, target.grid_y, self.obstacles):
                    target.hp -= max(2, enemy.strength)
                    self.attack_effects.append(AttackEffect(target.grid_x, target.grid_y))
                else:
                    dx = 1 if enemy.grid_x < target.grid_x else -1 if enemy.grid_x > target.grid_x else 0
                    dy = 1 if enemy.grid_y < target.grid_y else -1 if enemy.grid_y > target.grid_y else 0
                    if abs(target.grid_x - enemy.grid_x) > GRID_WIDTH // 2:
                        dx *= -1
                    if abs(target.grid_y - enemy.grid_y) > GRID_HEIGHT // 2:
                        dy *= -1

                    candidate_steps = [(dx, 0), (0, dy), (dx, dy), random.choice([(1,0),(-1,0),(0,1),(0,-1)])]
                    moved = False
                    for sx, sy in candidate_steps:
                        nx = (enemy.grid_x + sx) % GRID_WIDTH
                        ny = (enemy.grid_y + sy) % GRID_HEIGHT
                        if is_tile_walkable(nx, ny, self.obstacles, self.structures, enemy.flying):
                            enemy.grid_x, enemy.grid_y = nx, ny
                            moved = True
                            break
                    if not moved:
                        continue

                    if grid_distance(enemy.grid_x, enemy.grid_y, target.grid_x, target.grid_y) <= 1:
                        target.hp -= enemy.strength
                        self.attack_effects.append(AttackEffect(target.grid_x, target.grid_y))

                if target.hp <= 0:
                    for player in self.players:
                        if target in player.player_units:
                            if target == player.wizard:
                                self.game_over = True
                            else:
                                player.player_units.remove(target)
                            break
                    if self.game_over:
                        break
            if self.game_over:
                break

        for enemy in self.enemies:
            enemy.reset_ap()

    def complete_level(self):
        bonus = XP_LEVEL_BONUS + (self.level * 2)
        self.exp += bonus
        for player in self.players:
            player.gain_xp(bonus // max(1, len(self.players)))
        if self.level >= MAX_LEVEL:
            self.game_win = True
            return

        self.level += 1
        self.turn_count = 0
        self.portal = None
        self.map_index = (self.map_index + 1) % len(MAP_TEMPLATES)
        self.setup_world()
        for i, player in enumerate(self.players):
            start_pos = get_start_pos(i, self.num_players)
            player.wizard.grid_x, player.wizard.grid_y = start_pos
            player.wizard.mana = player.wizard.max_mana
            player.player_units = [player.wizard]
            player.current_unit_index = 0
            player.look_mode = False
            player.explored = [[False for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)]
            player.update_fog_for_unit(player.wizard)

    def draw_game(self):
        # Center camera on active player's current unit.
        active_player = self.players[self.active_player_index]
        current_unit = active_player.player_units[active_player.current_unit_index]
        center_x = current_unit.grid_x * TILE_SIZE + TILE_SIZE // 2
        center_y = current_unit.grid_y * TILE_SIZE + TILE_SIZE // 2
        cam_x = center_x
        cam_y = center_y
        game_area = pygame.Surface((GAME_VIEW_WIDTH, GAME_VIEW_HEIGHT))
        # Draw background tiles
        for i in range(GRID_WIDTH):
            for j in range(GRID_HEIGHT):
                tile_world_x = i * TILE_SIZE
                tile_world_y = j * TILE_SIZE
                screen_x = world_to_screen(tile_world_x, cam_x, WORLD_WIDTH, GAME_VIEW_WIDTH)
                screen_y = world_to_screen(tile_world_y, cam_y, WORLD_HEIGHT, GAME_VIEW_HEIGHT)
                if -TILE_SIZE < screen_x < GAME_VIEW_WIDTH and -TILE_SIZE < screen_y < GAME_VIEW_HEIGHT:
                    drawn = False
                    for struct in self.structures:
                        if struct.grid_x <= i < struct.grid_x + struct.width and struct.grid_y <= j < struct.grid_y + struct.height:
                            local_x = i - struct.grid_x
                            local_y = j - struct.grid_y
                            tile = struct.tile_map[local_x][local_y]
                            if tile == "wall":
                                game_area.blit(ASSETS["wall_tile"], (screen_x, screen_y))
                            elif tile in ("door_closed", "door_open"):
                                if tile == "door_closed":
                                    game_area.blit(ASSETS["door_tile"], (screen_x, screen_y))
                                else:
                                    game_area.blit(ASSETS["floor_tile"], (screen_x, screen_y))
                            else:
                                game_area.blit(ASSETS["floor_tile"], (screen_x, screen_y))
                            drawn = True
                            break
                    if not drawn:
                        game_area.blit(ASSETS["grass_tile"], (screen_x, screen_y))
        # Draw obstacles
        for obs in self.obstacles:
            ox = obs.grid_x * TILE_SIZE
            oy = obs.grid_y * TILE_SIZE
            sx = world_to_screen(ox, cam_x, WORLD_WIDTH, GAME_VIEW_WIDTH)
            sy = world_to_screen(oy, cam_y, WORLD_HEIGHT, GAME_VIEW_HEIGHT)
            if obs.type == "tree":
                game_area.blit(ASSETS["tree_tile"], (sx, sy))
            elif obs.type == "building":
                game_area.blit(ASSETS["building_tile"], (sx, sy))
            elif obs.type == "swamp":
                game_area.blit(ASSETS["swamp_tile"], (sx, sy))
        # Draw chests
        for chest in self.chests:
            cx = chest.grid_x * TILE_SIZE
            cy = chest.grid_y * TILE_SIZE
            sx = world_to_screen(cx, cam_x, WORLD_WIDTH, GAME_VIEW_WIDTH)
            sy = world_to_screen(cy, cam_y, WORLD_HEIGHT, GAME_VIEW_HEIGHT)
            if chest.opened:
                game_area.blit(ASSETS["chest_open"], (sx, sy))
            else:
                game_area.blit(ASSETS["chest_closed"], (sx, sy))
        # Draw portal
        if self.portal:
            px = self.portal.grid_x * TILE_SIZE
            py = self.portal.grid_y * TILE_SIZE
            sx = world_to_screen(px, cam_x, WORLD_WIDTH, GAME_VIEW_WIDTH)
            sy = world_to_screen(py, cam_y, WORLD_HEIGHT, GAME_VIEW_HEIGHT)
            rect = pygame.Rect(sx, sy, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(game_area, BLUE, rect)
            p_text = self.font.render(str(self.portal.countdown), True, WHITE)
            game_area.blit(p_text, (rect.x, rect.y))
        # Draw all player units (from every player)
        for player in self.players:
            for unit in player.player_units:
                ux = unit.grid_x * TILE_SIZE
                uy = unit.grid_y * TILE_SIZE
                sx = world_to_screen(ux, cam_x, WORLD_WIDTH, GAME_VIEW_WIDTH)
                sy = world_to_screen(uy, cam_y, WORLD_HEIGHT, GAME_VIEW_HEIGHT)
                frame = unit.frames[(pygame.time.get_ticks() // 300) % len(unit.frames)]
                game_area.blit(frame, (sx, sy))
                hp_text = self.font.render(str(unit.hp), True, WHITE)
                game_area.blit(hp_text, (sx, sy))
                # Highlight active player's selected unit.
                if player == active_player and unit == active_player.player_units[active_player.current_unit_index]:
                    pygame.draw.rect(game_area, WHITE, (sx-2, sy-2, TILE_SIZE+4, TILE_SIZE+4), 2)
        # Draw enemies
        for enemy in self.enemies:
            ex = enemy.grid_x * TILE_SIZE
            ey = enemy.grid_y * TILE_SIZE
            sx = world_to_screen(ex, cam_x, WORLD_WIDTH, GAME_VIEW_WIDTH)
            sy = world_to_screen(ey, cam_y, WORLD_HEIGHT, GAME_VIEW_HEIGHT)
            frame = enemy.frames[(pygame.time.get_ticks() // 300) % len(enemy.frames)]
            game_area.blit(frame, (sx, sy))
            e_text = self.font.render(str(enemy.hp), True, WHITE)
            game_area.blit(e_text, (sx, sy))
        # Draw attack effects
        for effect in self.attack_effects[:]:
            if effect.is_active():
                sx = world_to_screen(effect.grid_x * TILE_SIZE, cam_x, WORLD_WIDTH, GAME_VIEW_WIDTH) + TILE_SIZE//2
                sy = world_to_screen(effect.grid_y * TILE_SIZE, cam_y, WORLD_HEIGHT, GAME_VIEW_HEIGHT) + TILE_SIZE//2
                pygame.draw.circle(game_area, RED, (sx, sy), 10)
            else:
                self.attack_effects.remove(effect)
        # Draw fog-of-war overlay based on active player's explored grid.
        for i in range(GRID_WIDTH):
            for j in range(GRID_HEIGHT):
                if not active_player.explored[i][j]:
                    tx = i * TILE_SIZE
                    ty = j * TILE_SIZE
                    sx = world_to_screen(tx, cam_x, WORLD_WIDTH, GAME_VIEW_WIDTH)
                    sy = world_to_screen(ty, cam_y, WORLD_HEIGHT, GAME_VIEW_HEIGHT)
                    fog = pygame.Surface((TILE_SIZE, TILE_SIZE))
                    fog.set_alpha(200)
                    fog.fill(BLACK)
                    game_area.blit(fog, (sx, sy))
        self.screen.blit(game_area, (0, 0))
        self.draw_sidebar(cam_x, cam_y, active_player)
        if self.game_over:
            over_text = self.font.render("Game Over! Press Enter to restart.", True, RED)
            self.screen.blit(over_text, (GAME_VIEW_WIDTH//2 - over_text.get_width()//2, GAME_VIEW_HEIGHT//2))
        if self.game_win:
            win_text = self.font.render("You Win! Press Enter to restart.", True, GREEN)
            self.screen.blit(win_text, (GAME_VIEW_WIDTH//2 - win_text.get_width()//2, GAME_VIEW_HEIGHT//2))
        pygame.display.flip()

    def draw_sidebar(self, cam_x, cam_y, active_player):
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
        for struct in self.structures:
            x = struct.grid_x * TILE_SIZE * scale
            y = struct.grid_y * TILE_SIZE * scale
            w = struct.width * TILE_SIZE * scale
            h = struct.height * TILE_SIZE * scale
            pygame.draw.rect(minimap_surface, DARK_GRAY, (x, y, w, h), 2)
        for chest in self.chests:
            x = chest.grid_x * TILE_SIZE * scale
            y = chest.grid_y * TILE_SIZE * scale
            size = TILE_SIZE * scale
            pygame.draw.rect(minimap_surface, (255,215,0), (x, y, size, size))
        for player in self.players:
            x = player.wizard.grid_x * TILE_SIZE * scale
            y = player.wizard.grid_y * TILE_SIZE * scale
            size = TILE_SIZE * scale
            pygame.draw.rect(minimap_surface, player.wizard.frames[0].get_at((0,0)), (x, y, size, size))
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
        cam_rect = pygame.Rect(world_to_screen(0, cam_x, WORLD_WIDTH, minimap_size),
                                 world_to_screen(0, cam_y, WORLD_HEIGHT, minimap_size),
                                 GAME_VIEW_WIDTH * scale, GAME_VIEW_HEIGHT * scale)
        pygame.draw.rect(minimap_surface, YELLOW, cam_rect, 2)
        self.screen.blit(minimap_surface, (sidebar_rect.x + 10, 10))
        stats_start_y = 200
        current_unit = active_player.player_units[active_player.current_unit_index]
        if current_unit == active_player.wizard:
            unit_type = "Wizard"
            extra = f"Mana: {active_player.wizard.mana}/{active_player.wizard.max_mana}"
        else:
            unit_type = current_unit.type
            extra = ""
        stats_lines = [
            f"Type: {unit_type}",
            f"HP: {current_unit.hp}/{getattr(current_unit, 'max_hp', current_unit.hp)}",
            f"AP: {current_unit.ap}/{current_unit.max_ap}",
            f"Str: {getattr(current_unit, 'strength', '-')}",
            f"Spd: {getattr(current_unit, 'speed', '-')}",
            extra
        ]
        for i, line in enumerate(stats_lines):
            text = self.font.render(line, True, WHITE)
            self.screen.blit(text, (sidebar_rect.x + 10, stats_start_y + i * 20))
        if active_player.look_mode:
            look_info = self.get_tile_info(active_player.look_cursor_x, active_player.look_cursor_y)
            look_text = self.font.render("LOOK: " + look_info, True, WHITE)
            self.screen.blit(look_text, (sidebar_rect.x + 10, 350))
        turn_text = self.font.render(f"Turn: {self.turn_count}/{self.turn_limit}", True, WHITE)
        level_text = self.font.render(f"Stage: {self.level}", True, WHITE)
        xp_text = self.font.render(f"Global XP: {self.exp}", True, WHITE)
        wiz_lvl_text = self.font.render(f"Wizard Lvl: {active_player.level} XP:{active_player.xp}", True, WHITE)
        map_text = self.font.render(f"Map: {self.active_map_name}", True, WHITE)
        self.screen.blit(turn_text, (sidebar_rect.x + 10, 375))
        self.screen.blit(level_text, (sidebar_rect.x + 10, 395))
        self.screen.blit(xp_text, (sidebar_rect.x + 10, 415))
        self.screen.blit(wiz_lvl_text, (sidebar_rect.x + 10, 435))
        self.screen.blit(map_text, (sidebar_rect.x + 10, 455))
        if self.portal:
            portal_text = self.font.render(f"Portal: {self.portal.countdown}", True, WHITE)
            self.screen.blit(portal_text, (sidebar_rect.x + 10, 475))
        controls = [
            "Arrows: Move/Attack",
            "TAB: Next Unit",
            "1-7: Spawn Ally",
            "Z/X/C/V/B: Spells",
            "O: Open Chest",
            "L: Look Mode",
            "D: Toggle Door"
        ]
        base_y = 495
        for i, line in enumerate(controls):
            self.screen.blit(self.font.render(line, True, WHITE), (sidebar_rect.x + 10, base_y + i * 20))
        if all(unit.ap == 0 for unit in active_player.player_units):
            flash_color = RED if (pygame.time.get_ticks() // 500) % 2 == 0 else WHITE
        else:
            flash_color = WHITE
        end_turn_text = self.font.render("E: End Turn", True, flash_color)
        self.screen.blit(end_turn_text, (sidebar_rect.x + 10, base_y + len(controls)*20))
        if self.spell_message:
            self.screen.blit(self.font.render(self.spell_message[:28], True, YELLOW), (10, GAME_VIEW_HEIGHT - 20))
    
    def run(self):
        while True:
            self.clock.tick(FPS)
            if self.state == "PLAYER_COUNT":
                self.handle_player_count_events()
                self.draw_player_count()
            elif self.state == "EDITOR":
                self.handle_editor_events()
                self.draw_editor()
            elif self.state == "GAME":
                self.handle_game_events()
                self.draw_game()
            # If the restart flag is set, exit the run loop to restart the game.
            if self.restart_flag:
                break

if __name__ == "__main__":
    # Wrap the game in a loop so that a new instance is created each time.
    while True:
        game = Game()
        game.run()
