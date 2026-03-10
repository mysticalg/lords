# Lords: HTML5 Edition

A lightweight turn-based fantasy tactics game that runs directly in the browser.

## Run locally

Because this project uses static HTML/CSS/JS, you can open `index.html` directly,
or run a tiny local server:

```bash
python3 -m http.server 8000
```

Then visit `http://localhost:8000`.

## Automatic GitHub Pages deployment

This repository includes a GitHub Actions workflow at
`.github/workflows/deploy-pages.yml` that automatically publishes the game to
GitHub Pages on every push to `main` or `master`.

### One-time setup in GitHub

1. Open **Settings → Pages** in your repository.
2. Set **Source** to **GitHub Actions**.
3. Push to `main`/`master` (or run the workflow manually from the **Actions** tab).

After deployment, your game will be available at:

- `https://<your-github-username>.github.io/<repo-name>/`

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
