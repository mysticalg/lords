# Lords: HTML5 Edition

A lightweight turn-based fantasy tactics game that runs directly in the browser.

## Run locally

Because this project uses static HTML/CSS/JS, you can open `index.html` directly,
or run a tiny local server:

```bash
python3 -m http.server 8000
```

Then visit `http://localhost:8000`.

## Controls

- Move: `WASD` or Arrow Keys
- Wait turn: `Wait` button
- Cast spells: Bolt / Heal / Teleport buttons
- Restart: `New Game`

## Gameplay loop

1. Move around the grid, open chests for mana and XP.
2. Attack enemies in melee by walking into them.
3. Use spells tactically to survive and clear the map.
4. Win by defeating all enemies.
