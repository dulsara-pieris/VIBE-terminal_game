#!/usr/bin/env python3
"""VIBE Terminal Game: sandbox-style terminal action game for Linux."""

from __future__ import annotations

import argparse
import curses
import json
import random
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

APP_NAME = "vibe-terminal-game"
SAVE_PATH = Path.home() / ".config" / APP_NAME / "save.json"
MAP_W = 58
MAP_H = 22
MAP_TOP = 4

COLOR_DEFAULT = 1
COLOR_WATER = 2
COLOR_TREE = 3
COLOR_ORE = 4
COLOR_COIN = 5
COLOR_PLAYER = 6
COLOR_ENEMY = 7


@dataclass
class Enemy:
    x: int
    y: int
    hp: int


@dataclass
class State:
    x: int = MAP_W // 2
    y: int = MAP_H // 2
    hp: int = 100
    max_hp: int = 100
    coins: int = 0
    wood: int = 0
    ore: int = 0
    score: int = 0
    wave: int = 1
    combo: int = 0
    combo_timer: int = 0
    dash_charges: int = 2
    bomb_charges: int = 1
    high_score: int = 0
    terrain_seed: int = field(default_factory=lambda: random.randint(1, 999999))


class SandboxGame:
    def __init__(self) -> None:
        self.state = State()
        self.msg = "Welcome! Move with arrows/WASD, gather resources, fight enemies, and press H for guided help."
        self.enemies: list[Enemy] = []
        self.powerups: dict[tuple[int, int], str] = {}
        self.tiles: list[list[str]] = []
        self.rng = random.Random(self.state.terrain_seed)
        self.show_help = True
        self.use_color = False
        self.make_world()

    def init_colors(self) -> None:
        if not curses.has_colors():
            return
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(COLOR_DEFAULT, curses.COLOR_WHITE, -1)
        curses.init_pair(COLOR_WATER, curses.COLOR_CYAN, -1)
        curses.init_pair(COLOR_TREE, curses.COLOR_GREEN, -1)
        curses.init_pair(COLOR_ORE, curses.COLOR_MAGENTA, -1)
        curses.init_pair(COLOR_COIN, curses.COLOR_YELLOW, -1)
        curses.init_pair(COLOR_PLAYER, curses.COLOR_BLUE, -1)
        curses.init_pair(COLOR_ENEMY, curses.COLOR_RED, -1)
        self.use_color = True

    def style_for_tile(self, ch: str) -> int:
        if not self.use_color:
            return curses.A_NORMAL
        palette = {
            "~": curses.color_pair(COLOR_WATER),
            "T": curses.color_pair(COLOR_TREE),
            "O": curses.color_pair(COLOR_ORE),
            "$": curses.color_pair(COLOR_COIN) | curses.A_BOLD,
            "@": curses.color_pair(COLOR_PLAYER) | curses.A_BOLD,
            "g": curses.color_pair(COLOR_ENEMY) | curses.A_BOLD,
            "*": curses.color_pair(COLOR_COIN) | curses.A_BOLD,
            "+": curses.color_pair(COLOR_TREE) | curses.A_BOLD,
            ".": curses.color_pair(COLOR_DEFAULT),
        }
        return palette.get(ch, curses.color_pair(COLOR_DEFAULT))

    def make_world(self) -> None:
        self.rng = random.Random(self.state.terrain_seed)
        self.tiles = [["." for _ in range(MAP_W)] for _ in range(MAP_H)]

        for y in range(MAP_H):
            for x in range(MAP_W):
                r = self.rng.random()
                if r < 0.06:
                    self.tiles[y][x] = "~"  # water
                elif r < 0.12:
                    self.tiles[y][x] = "T"  # tree
                elif r < 0.16:
                    self.tiles[y][x] = "O"  # ore rock
                elif r < 0.17:
                    self.tiles[y][x] = "$"  # coin cache

        self.state.x = max(1, min(MAP_W - 2, self.state.x))
        self.state.y = max(1, min(MAP_H - 2, self.state.y))
        self.tiles[self.state.y][self.state.x] = "."

        self.enemies = []
        count = min(6 + self.state.wave, 18)
        for _ in range(count):
            for _attempt in range(100):
                ex, ey = self.rng.randint(1, MAP_W - 2), self.rng.randint(1, MAP_H - 2)
                if (ex, ey) != (self.state.x, self.state.y) and self.tiles[ey][ex] != "~":
                    self.enemies.append(Enemy(ex, ey, 18 + self.state.wave * 3))
                    break

        self.powerups = {}
        for _ in range(2):
            px, py = self.random_floor_tile()
            self.powerups[(px, py)] = "*"  # score star
        if self.state.wave % 2 == 0:
            px, py = self.random_floor_tile()
            self.powerups[(px, py)] = "+"  # hp orb

    def random_floor_tile(self) -> tuple[int, int]:
        for _ in range(200):
            x, y = self.rng.randint(1, MAP_W - 2), self.rng.randint(1, MAP_H - 2)
            if (
                self.tiles[y][x] == "."
                and (x, y) != (self.state.x, self.state.y)
                and not any((e.x, e.y) == (x, y) for e in self.enemies)
            ):
                return x, y
        return 1, 1

    def draw(self, stdscr: curses.window) -> None:
        stdscr.erase()
        hud = (
            f"HP {self.state.hp}/{self.state.max_hp} | Coins {self.state.coins} | "
            f"Wood {self.state.wood} | Ore {self.state.ore} | Wave {self.state.wave} | "
            f"Combo x{max(1, self.state.combo)} | Score {self.state.score}"
        )
        stdscr.addstr(0, 0, hud[: MAP_W + 25])
        action_bar = f"Dash(E): {self.state.dash_charges}  Bomb(F): {self.state.bomb_charges}  High score: {self.state.high_score}"
        stdscr.addstr(1, 0, action_bar[: MAP_W + 25])
        stdscr.addstr(2, 0, self.msg[: MAP_W + 25])
        legend = "Legend: @ you g enemy * star + hp ~ water T tree O ore $ coins"
        stdscr.addstr(3, 0, legend[: MAP_W + 25])

        enemy_positions = {(e.x, e.y): e for e in self.enemies}
        for y in range(MAP_H):
            for x in range(MAP_W):
                if (x, y) == (self.state.x, self.state.y):
                    ch = "@"
                elif (x, y) in enemy_positions:
                    ch = "g"
                elif (x, y) in self.powerups:
                    ch = self.powerups[(x, y)]
                else:
                    ch = self.tiles[y][x]
                stdscr.addch(MAP_TOP + y, x, ch, self.style_for_tile(ch))
        if self.show_help:
            help_lines = [
                "How to play (press H to hide/show):",
                "1) Explore and collect: walk onto T/O/$ tiles to gather resources.",
                "2) Fight nearby enemies with SPACE to earn score and coins.",
                "3) Chain enemy kills for combo multipliers and huge score boosts.",
                "4) Use E to dash and F to blast nearby enemies.",
                "5) Save with P, load with L, and quit with Q.",
            ]
            for idx, line in enumerate(help_lines):
                stdscr.addstr(MAP_TOP + MAP_H + 1 + idx, 0, line[: MAP_W + 25])
        stdscr.refresh()

    def can_walk(self, x: int, y: int) -> bool:
        if x < 0 or y < 0 or x >= MAP_W or y >= MAP_H:
            return False
        return self.tiles[y][x] != "~"

    def collect_tile(self) -> None:
        pos = (self.state.x, self.state.y)
        if pos in self.powerups:
            power = self.powerups.pop(pos)
            if power == "*":
                self.state.score += 25
                self.state.combo_timer = max(self.state.combo_timer, 8)
                self.msg = "Star collected! +25 score and combo timer boosted."
            elif power == "+":
                self.state.hp = min(self.state.max_hp, self.state.hp + 18)
                self.msg = "HP orb grabbed! +18 HP."

        t = self.tiles[self.state.y][self.state.x]
        if t == "T":
            self.state.wood += 1
            self.state.score += 2
            self.tiles[self.state.y][self.state.x] = "."
            self.msg = "Chopped tree: +1 wood"
        elif t == "O":
            self.state.ore += 1
            self.state.score += 3
            self.tiles[self.state.y][self.state.x] = "."
            self.msg = "Mined ore: +1 ore"
        elif t == "$":
            gain = random.randint(5, 15)
            self.state.coins += gain
            self.state.score += gain
            self.tiles[self.state.y][self.state.x] = "."
            self.msg = f"Found cache: +{gain} coins"

    def move_player(self, dx: int, dy: int) -> None:
        nx = self.state.x + dx
        ny = self.state.y + dy
        if not self.can_walk(nx, ny):
            self.msg = "Blocked by water."
            return
        self.state.x, self.state.y = nx, ny
        self.collect_tile()

    def attack(self) -> None:
        hits = 0
        kills = 0
        for enemy in list(self.enemies):
            if abs(enemy.x - self.state.x) <= 1 and abs(enemy.y - self.state.y) <= 1:
                dmg = random.randint(8, 16)
                enemy.hp -= dmg
                hits += 1
                if enemy.hp <= 0:
                    self.enemies.remove(enemy)
                    self.state.coins += 6
                    kills += 1
                    self.state.score += 10 * max(1, self.state.combo)
        if hits == 0:
            self.msg = "No enemy in range."
            self.state.combo = 0
        else:
            if kills > 0:
                self.state.combo = min(9, self.state.combo + kills)
                self.state.combo_timer = 12
            self.msg = f"Slash hits {hits} enemy(ies)! Kills: {kills}."

    def dash(self) -> None:
        if self.state.dash_charges <= 0:
            self.msg = "No dash charges. Clear a wave to refill!"
            return
        self.state.dash_charges -= 1
        best_enemy = min(self.enemies, key=lambda e: abs(e.x - self.state.x) + abs(e.y - self.state.y), default=None)
        if not best_enemy:
            self.msg = "Dash fizzled. No enemies found."
            return
        candidates = [
            (best_enemy.x + 1, best_enemy.y),
            (best_enemy.x - 1, best_enemy.y),
            (best_enemy.x, best_enemy.y + 1),
            (best_enemy.x, best_enemy.y - 1),
        ]
        self.rng.shuffle(candidates)
        for nx, ny in candidates:
            if self.can_walk(nx, ny):
                self.state.x, self.state.y = nx, ny
                break
        self.collect_tile()
        self.msg = "Arcade dash! You're back in the action."

    def bomb(self) -> None:
        if self.state.bomb_charges <= 0:
            self.msg = "No bombs left."
            return
        self.state.bomb_charges -= 1
        removed = 0
        for enemy in list(self.enemies):
            if abs(enemy.x - self.state.x) <= 2 and abs(enemy.y - self.state.y) <= 2:
                self.enemies.remove(enemy)
                removed += 1
        if removed:
            self.state.coins += removed * 5
            self.state.score += removed * 14 * max(1, self.state.combo)
            self.state.combo = min(9, self.state.combo + removed)
            self.state.combo_timer = 10
            self.msg = f"BOOM! Removed {removed} enemies."
        else:
            self.msg = "Bomb exploded... but no enemies were nearby."

    def craft(self) -> None:
        if self.state.wood >= 3 and self.state.ore >= 1:
            self.state.wood -= 3
            self.state.ore -= 1
            heal = min(24, self.state.max_hp - self.state.hp)
            self.state.hp += heal
            self.state.score += 8
            self.msg = f"Crafted camp kit. Healed {heal} HP."
        elif self.state.wood >= 2 and self.state.coins >= 12:
            self.state.wood -= 2
            self.state.coins -= 12
            self.state.max_hp += 6
            self.state.hp += 6
            self.msg = "Crafted armor plates. Max HP +6."
        else:
            self.msg = "Need (3 wood+1 ore) to heal OR (2 wood+12 coins) for armor."

    def enemy_turn(self) -> None:
        if self.state.combo_timer > 0:
            self.state.combo_timer -= 1
            if self.state.combo_timer == 0:
                self.state.combo = 0

        for enemy in self.enemies:
            dx = self.state.x - enemy.x
            dy = self.state.y - enemy.y
            dist = abs(dx) + abs(dy)
            if dist <= 1:
                dmg = random.randint(4, 9) + self.state.wave // 2
                self.state.hp -= dmg
                self.msg = f"Enemy hit you for {dmg}!"
                continue

            step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
            step_y = 0 if dy == 0 else (1 if dy > 0 else -1)
            if abs(dx) > abs(dy):
                nx, ny = enemy.x + step_x, enemy.y
            else:
                nx, ny = enemy.x, enemy.y + step_y

            if self.can_walk(nx, ny) and (nx, ny) != (self.state.x, self.state.y):
                if not any((e.x, e.y) == (nx, ny) for e in self.enemies):
                    enemy.x, enemy.y = nx, ny

        if not self.enemies:
            self.state.wave += 1
            self.state.score += 25
            self.state.dash_charges = min(3, self.state.dash_charges + 1)
            self.state.bomb_charges = min(2, self.state.bomb_charges + 1)
            self.msg = "Wave cleared! Dash/Bomb recharged. Press N for a fresh zone."

        self.state.high_score = max(self.state.high_score, self.state.score)

    def save(self) -> None:
        SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
        payload = {"state": asdict(self.state), "enemies": [asdict(e) for e in self.enemies], "tiles": self.tiles}
        with SAVE_PATH.open("w", encoding="utf-8") as f:
            json.dump(payload, f)
        self.msg = f"Saved to {SAVE_PATH}"

    def load(self) -> None:
        if not SAVE_PATH.exists():
            self.msg = "No save file found."
            return
        with SAVE_PATH.open("r", encoding="utf-8") as f:
            payload = json.load(f)
        saved_state = payload["state"]
        defaults = asdict(State())
        defaults.update(saved_state)
        self.state = State(**defaults)
        self.enemies = [Enemy(**e) for e in payload["enemies"]]
        self.tiles = payload["tiles"]
        self.msg = f"Loaded save. Wave {self.state.wave}."

    def handle_key(self, key: int) -> bool:
        if key in (ord("q"), ord("Q")):
            return False
        if key in (curses.KEY_UP, ord("w"), ord("W")):
            self.move_player(0, -1)
        elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
            self.move_player(0, 1)
        elif key in (curses.KEY_LEFT, ord("a"), ord("A")):
            self.move_player(-1, 0)
        elif key in (curses.KEY_RIGHT, ord("d"), ord("D")):
            self.move_player(1, 0)
        elif key == ord(" "):
            self.attack()
        elif key in (ord("c"), ord("C")):
            self.craft()
        elif key in (ord("e"), ord("E")):
            self.dash()
        elif key in (ord("f"), ord("F")):
            self.bomb()
        elif key in (ord("n"), ord("N")):
            self.state.terrain_seed = random.randint(1, 999999)
            self.make_world()
            self.msg = "New zone generated."
        elif key in (ord("l"), ord("L")):
            self.load()
        elif key in (ord("p"), ord("P")):
            self.save()
        elif key in (ord("h"), ord("H")):
            self.show_help = not self.show_help
            if self.show_help:
                self.msg = "Help is now ON. Follow the 1-5 guide below the map."
            else:
                self.msg = "Help is now OFF. Press H any time to bring it back."
        return True

    def loop(self, stdscr: curses.window) -> None:
        curses.curs_set(0)
        self.init_colors()
        stdscr.nodelay(True)
        stdscr.timeout(100)

        while self.state.hp > 0:
            self.draw(stdscr)
            key = stdscr.getch()
            if key != -1:
                if not self.handle_key(key):
                    return
            self.enemy_turn()
            time.sleep(0.03)

        self.draw(stdscr)
        stdscr.addstr(MAP_TOP + MAP_H + 7, 0, f"Game over. Final score: {self.state.score}. Press any key.")
        stdscr.nodelay(False)
        stdscr.getch()


def smoke_test() -> None:
    game = SandboxGame()
    for _ in range(10):
        game.move_player(random.choice([-1, 0, 1]), random.choice([-1, 0, 1]))
        if random.random() < 0.2:
            game.dash()
        if random.random() < 0.1:
            game.bomb()
        game.enemy_turn()
    assert game.state.max_hp >= 100
    assert game.state.high_score >= game.state.score
    print("smoke-ok")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="VIBE sandbox terminal game")
    parser.add_argument("--smoke-test", action="store_true", help="Run non-interactive smoke test")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.smoke_test:
        smoke_test()
        return
    curses.wrapper(SandboxGame().loop)


if __name__ == "__main__":
    main()
