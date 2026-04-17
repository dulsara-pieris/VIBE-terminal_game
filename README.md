# VIBE Terminal Game: Arcade Mode

A Linux-priority terminal sandbox game made with Python + curses.

## What's new (Arcade Upgrade)

- Real movement game feel (arrow keys/WASD), not menu-only text loops
- Open sandbox zone with roaming enemies, resources, and random terrain
- Action combat: **Space** for melee attacks
- Combo multiplier system for kill streak scoring
- Arcade powerups: score stars (`*`) and health orbs (`+`)
- Dash (`E`) and bomb (`F`) abilities with charge/recharge mechanics
- Crafting system: use gathered wood/ore/coins for healing/upgrades
- Wave progression, high-score tracking, and faster reward loops
- Save/load support in `~/.config/vibe-terminal-game/save.json`

## Run from repo

```bash
python3 game.py
```

## Controls

- Move: `Arrow keys` or `W/A/S/D`
- Attack: `Space`
- Craft: `C`
- Dash to nearest fight: `E`
- Bomb nearby enemies: `F`
- New random zone: `N`
- Save: `P`
- Load: `L`
- Help hint: `H`
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
