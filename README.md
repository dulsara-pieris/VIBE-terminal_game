# VIBE Terminal Game: Arcade Mode

A Linux-first arcade survival game made with Python + curses.

## Gameplay

- Fast arena combat in your terminal
- Dodge enemies, shoot projectiles, and survive waves
- Score-based progression that ramps difficulty over time
- Health pickups (`+`) spawn occasionally to keep runs alive

## Run from repo

```bash
python3 game.py
```

## Controls

- Move: `Arrow keys` or `W/A/S/D`
- Shoot in facing direction: `Space`
- Shoot precise direction: `I/J/K/L` (up/left/down/right)
- Pause/resume: `H`
- Quit: `Q`

## Linux install

One-line install (recommended):

```bash
curl -fsSL https://raw.githubusercontent.com/dulsara-pieris/VIBE-terminal_game/main/installer.sh | bash
```

If you already cloned this repo, run:

```bash
bash installer.sh
```

Then start the game with:

```bash
vibe-game
```

Installs to user-local paths:

- `~/.local/share/vibe-terminal-game/`
- `~/.local/bin/vibe-game`
- `~/.local/share/applications/vibe-game.desktop`
- `~/.local/share/man/man6/vibe-game.6.gz`

## Uninstall

```bash
bash uninstaller.sh
```

## Update (Git)

```bash
bash updater.sh
```
