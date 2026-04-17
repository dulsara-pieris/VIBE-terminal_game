# VIBE Terminal Game: Sandbox Mode

A Linux-priority terminal sandbox game made with Python + curses.

## What's new

- Real movement game feel (arrow keys/WASD), not menu-only text loops
- Open sandbox zone with roaming enemies, resources, and random terrain
- Action combat: **Space** for melee attacks
- Crafting system: use gathered wood/ore/coins for healing/upgrades
- Wave progression + score system
- Save/load support in `~/.config/vibe-terminal-game/save.json`

## Run from repo

```bash
python3 game.py
```

## Controls

- Move: `Arrow keys` or `W/A/S/D`
- Attack: `Space`
- Craft: `C`
- New random zone: `N`
- Save: `P`
- Load: `L`
- Help hint: `H`
- Quit: `Q`

## Linux install

```bash
bash installer.sh
```

Or install directly with `curl`:

```bash
curl -fsSL https://github.com/dulsara-pieris/VIBE-terminal_game/raw/refs/heads/main/installer.sh | bash -s --
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
