# Lords

This repository now includes a GitHub Actions workflow to package the game as a Windows `.exe` build.

## Build a Windows executable on GitHub

1. Push your branch to GitHub.
2. Open the **Actions** tab.
3. Run **Build Windows EXE** (or let it run automatically on pushes/PRs).
4. Download the `lords-windows-exe` artifact from the workflow run.

The artifact includes the packaged app under `dist/lords/` with all required `assets/` files bundled.
