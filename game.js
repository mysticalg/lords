// Lords HTML5 edition.
// This file keeps game logic intentionally compact and heavily commented
// so it is easy to extend without digging through framework abstractions.

const TILE = 48;
const COLS = 16;
const ROWS = 12;

const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

const ui = {
  health: document.getElementById('healthStat'),
  mana: document.getElementById('manaStat'),
  xp: document.getElementById('xpStat'),
  level: document.getElementById('levelStat'),
  log: document.getElementById('log'),
  waitBtn: document.getElementById('waitBtn'),
  boltBtn: document.getElementById('boltBtn'),
  healBtn: document.getElementById('healBtn'),
  teleportBtn: document.getElementById('teleportBtn'),
  resetBtn: document.getElementById('resetBtn'),
};

const state = {
  player: null,
  enemies: [],
  walls: new Set(),
  chests: [],
  gameOver: false,
};

function key(x, y) {
  return `${x},${y}`;
}

function randInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function log(message, type = '') {
  const line = document.createElement('div');
  line.className = `log-entry ${type}`.trim();
  line.textContent = message;
  ui.log.prepend(line);
  while (ui.log.childNodes.length > 12) ui.log.lastChild.remove();
}

function setupWorld() {
  state.player = { x: 1, y: 1, hp: 100, maxHp: 100, mana: 24, maxMana: 24, xp: 0, level: 1 };
  state.enemies = [];
  state.walls.clear();
  state.chests = [];
  state.gameOver = false;

  // Border walls and a few interior blocks for tactical movement choices.
  for (let x = 0; x < COLS; x++) {
    state.walls.add(key(x, 0));
    state.walls.add(key(x, ROWS - 1));
  }
  for (let y = 0; y < ROWS; y++) {
    state.walls.add(key(0, y));
    state.walls.add(key(COLS - 1, y));
  }

  [[4,3],[4,4],[4,5],[8,7],[9,7],[10,7],[12,4],[12,5]].forEach(([x,y]) => state.walls.add(key(x,y)));

  // Spawn enemies away from the player.
  while (state.enemies.length < 6) {
    const enemy = { x: randInt(2, COLS - 3), y: randInt(2, ROWS - 3), hp: 24 };
    const blocked = state.walls.has(key(enemy.x, enemy.y)) || (enemy.x === 1 && enemy.y === 1) || state.enemies.some(e => e.x === enemy.x && e.y === enemy.y);
    if (!blocked) state.enemies.push(enemy);
  }

  // Chests reward mana and XP, making exploration meaningful.
  while (state.chests.length < 4) {
    const chest = { x: randInt(1, COLS - 2), y: randInt(1, ROWS - 2), opened: false };
    const blocked = state.walls.has(key(chest.x, chest.y)) || state.enemies.some(e => e.x === chest.x && e.y === chest.y) || (chest.x === 1 && chest.y === 1);
    if (!blocked) state.chests.push(chest);
  }

  ui.log.innerHTML = '';
  log('A new run begins. Defeat every enemy!', 'good');
  updateUI();
  draw();
}

function enemyAt(x, y) {
  return state.enemies.find(e => e.x === x && e.y === y);
}

function canStep(x, y) {
  if (x < 0 || y < 0 || x >= COLS || y >= ROWS) return false;
  if (state.walls.has(key(x, y))) return false;
  return !enemyAt(x, y);
}

function movePlayer(dx, dy) {
  if (state.gameOver) return;
  const nx = state.player.x + dx;
  const ny = state.player.y + dy;
  const enemy = enemyAt(nx, ny);

  if (enemy) {
    // Melee is automatic by stepping into an enemy tile.
    enemy.hp -= 12;
    log('You strike an enemy for 12 damage.');
    if (enemy.hp <= 0) {
      state.enemies = state.enemies.filter(e => e !== enemy);
      gainXp(12);
      log('Enemy defeated in melee!', 'good');
    }
    enemyTurn();
    return;
  }

  if (!canStep(nx, ny)) return;

  state.player.x = nx;
  state.player.y = ny;
  lootIfOnChest();
  enemyTurn();
}

function lootIfOnChest() {
  const chest = state.chests.find(c => !c.opened && c.x === state.player.x && c.y === state.player.y);
  if (!chest) return;
  chest.opened = true;
  state.player.mana = Math.min(state.player.maxMana, state.player.mana + 8);
  gainXp(8);
  log('Chest opened: +8 mana and +8 XP.', 'good');
}

function gainXp(amount) {
  state.player.xp += amount;
  const needed = state.player.level * 35;
  if (state.player.xp >= needed) {
    state.player.xp -= needed;
    state.player.level += 1;
    state.player.maxHp += 8;
    state.player.maxMana += 3;
    state.player.hp = state.player.maxHp;
    state.player.mana = state.player.maxMana;
    log(`Level up! You are now level ${state.player.level}.`, 'good');
  }
}

function castBolt() {
  if (state.gameOver || state.player.mana < 6) return;
  if (!state.enemies.length) return;
  const target = [...state.enemies].sort((a, b) => manhattan(a, state.player) - manhattan(b, state.player))[0];
  state.player.mana -= 6;
  target.hp -= 17;
  log('Magic Bolt hits the closest enemy for 17.', 'good');
  if (target.hp <= 0) {
    state.enemies = state.enemies.filter(e => e !== target);
    gainXp(15);
    log('Enemy disintegrated by arcane force!', 'good');
  }
  enemyTurn();
}

function castHeal() {
  if (state.gameOver || state.player.mana < 8) return;
  state.player.mana -= 8;
  state.player.hp = Math.min(state.player.maxHp, state.player.hp + 18);
  log('Healing spell restores 18 health.', 'good');
  enemyTurn();
}

function castTeleport() {
  if (state.gameOver || state.player.mana < 10) return;
  // Search nearby safe cells quickly. First valid tile is used for snappy UX.
  for (let i = 0; i < 16; i++) {
    const nx = state.player.x + randInt(-3, 3);
    const ny = state.player.y + randInt(-3, 3);
    if (canStep(nx, ny)) {
      state.player.mana -= 10;
      state.player.x = nx;
      state.player.y = ny;
      lootIfOnChest();
      log('Teleport successful.', 'good');
      enemyTurn();
      return;
    }
  }
  log('Teleport fizzled: no safe location found.', 'danger');
}

function enemyTurn() {
  if (state.gameOver) return;

  for (const enemy of state.enemies) {
    const dx = Math.sign(state.player.x - enemy.x);
    const dy = Math.sign(state.player.y - enemy.y);
    const dist = manhattan(enemy, state.player);

    if (dist === 1) {
      state.player.hp -= 9;
      log('An enemy hits you for 9.', 'danger');
      continue;
    }

    const options = [
      { x: enemy.x + dx, y: enemy.y },
      { x: enemy.x, y: enemy.y + dy },
      { x: enemy.x + randInt(-1, 1), y: enemy.y + randInt(-1, 1) },
    ];

    for (const pos of options) {
      if (state.walls.has(key(pos.x, pos.y))) continue;
      if (pos.x < 1 || pos.y < 1 || pos.x >= COLS - 1 || pos.y >= ROWS - 1) continue;
      if (enemyAt(pos.x, pos.y)) continue;
      if (pos.x === state.player.x && pos.y === state.player.y) continue;
      enemy.x = pos.x;
      enemy.y = pos.y;
      break;
    }
  }

  if (state.player.hp <= 0) {
    state.player.hp = 0;
    state.gameOver = true;
    log('You have fallen. Press New Game to try again.', 'danger');
  } else if (!state.enemies.length) {
    state.gameOver = true;
    log('Victory! All enemies defeated.', 'good');
  }

  // Regeneration gives players comeback potential and reduces stalemates.
  state.player.mana = Math.min(state.player.maxMana, state.player.mana + 1);

  updateUI();
  draw();
}

function updateUI() {
  ui.health.textContent = `${state.player.hp} / ${state.player.maxHp}`;
  ui.mana.textContent = `${state.player.mana} / ${state.player.maxMana}`;
  ui.xp.textContent = `${state.player.xp}`;
  ui.level.textContent = `${state.player.level}`;

  const disabled = state.gameOver;
  ui.waitBtn.disabled = disabled;
  ui.boltBtn.disabled = disabled || state.player.mana < 6;
  ui.healBtn.disabled = disabled || state.player.mana < 8;
  ui.teleportBtn.disabled = disabled || state.player.mana < 10;
}

function manhattan(a, b) {
  return Math.abs(a.x - b.x) + Math.abs(a.y - b.y);
}

function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Draw board and walls.
  for (let y = 0; y < ROWS; y++) {
    for (let x = 0; x < COLS; x++) {
      ctx.fillStyle = '#0f2536';
      ctx.fillRect(x * TILE, y * TILE, TILE - 1, TILE - 1);

      if (state.walls.has(key(x, y))) {
        ctx.fillStyle = '#374151';
        ctx.fillRect(x * TILE + 2, y * TILE + 2, TILE - 5, TILE - 5);
      }
    }
  }

  // Chests.
  for (const chest of state.chests) {
    ctx.fillStyle = chest.opened ? '#6b7280' : '#92400e';
    ctx.fillRect(chest.x * TILE + 10, chest.y * TILE + 10, TILE - 20, TILE - 20);
  }

  // Enemies with hp strips.
  for (const enemy of state.enemies) {
    ctx.fillStyle = '#ef4444';
    ctx.beginPath();
    ctx.arc(enemy.x * TILE + TILE / 2, enemy.y * TILE + TILE / 2, 14, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = '#1f2937';
    ctx.fillRect(enemy.x * TILE + 7, enemy.y * TILE + 3, TILE - 14, 5);
    ctx.fillStyle = '#22c55e';
    ctx.fillRect(enemy.x * TILE + 7, enemy.y * TILE + 3, (TILE - 14) * (enemy.hp / 24), 5);
  }

  // Player wizard.
  ctx.fillStyle = '#7c3aed';
  ctx.beginPath();
  ctx.arc(state.player.x * TILE + TILE / 2, state.player.y * TILE + TILE / 2, 14, 0, Math.PI * 2);
  ctx.fill();

  // Banner text to keep game state obvious.
  if (state.gameOver) {
    ctx.fillStyle = 'rgba(15, 23, 42, 0.78)';
    ctx.fillRect(170, 240, 430, 90);
    ctx.fillStyle = '#f9fafb';
    ctx.font = 'bold 26px sans-serif';
    ctx.fillText(state.enemies.length ? 'Defeat!' : 'Victory!', 320, 278);
    ctx.font = '16px sans-serif';
    ctx.fillText('Press New Game to play again', 258, 308);
  }
}

window.addEventListener('keydown', (e) => {
  const map = {
    ArrowUp: [0, -1], ArrowDown: [0, 1], ArrowLeft: [-1, 0], ArrowRight: [1, 0],
    w: [0, -1], s: [0, 1], a: [-1, 0], d: [1, 0],
  };
  if (map[e.key]) {
    e.preventDefault();
    movePlayer(...map[e.key]);
    updateUI();
    draw();
  }
});

ui.waitBtn.addEventListener('click', () => enemyTurn());
ui.boltBtn.addEventListener('click', castBolt);
ui.healBtn.addEventListener('click', castHeal);
ui.teleportBtn.addEventListener('click', castTeleport);
ui.resetBtn.addEventListener('click', setupWorld);

setupWorld();
