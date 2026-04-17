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
        self.msg = "Welcome! Move with arrows/WASD."
        self.enemies: list[Enemy] = []
        self.powerups: dict[tuple[int, int], str] = {}
        self.tiles: list[list[str]] = []
        self.rng = random.Random(self.state.terrain_seed)
        self.show_help = True
        self.use_color = False
        self.make_world()

    def safe_addstr(self, stdscr, y, x, text):
        max_y, max_x = stdscr.getmaxyx()
        if y >= max_y:
            return
        try:
            stdscr.addstr(y, x, text[: max_x - x - 1])
        except curses.error:
            pass

    def safe_addch(self, stdscr, y, x, ch, attr):
        max_y, max_x = stdscr.getmaxyx()
        if y >= max_y or x >= max_x:
            return
        try:
            stdscr.addch(y, x, ch, attr)
        except curses.error:
            pass

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
        return {
            "~": curses.color_pair(COLOR_WATER),
            "T": curses.color_pair(COLOR_TREE),
            "O": curses.color_pair(COLOR_ORE),
            "$": curses.color_pair(COLOR_COIN) | curses.A_BOLD,
            "@": curses.color_pair(COLOR_PLAYER) | curses.A_BOLD,
            "g": curses.color_pair(COLOR_ENEMY) | curses.A_BOLD,
            "*": curses.color_pair(COLOR_COIN) | curses.A_BOLD,
            "+": curses.color_pair(COLOR_TREE) | curses.A_BOLD,
            ".": curses.color_pair(COLOR_DEFAULT),
        }.get(ch, curses.A_NORMAL)

    def make_world(self) -> None:
        self.tiles = [["." for _ in range(MAP_W)] for _ in range(MAP_H)]

        for y in range(MAP_H):
            for x in range(MAP_W):
                r = self.rng.random()
                if r < 0.06:
                    self.tiles[y][x] = "~"
                elif r < 0.12:
                    self.tiles[y][x] = "T"
                elif r < 0.16:
                    self.tiles[y][x] = "O"
                elif r < 0.17:
                    self.tiles[y][x] = "$"

        self.enemies = []
        for _ in range(8):
            x, y = self.rng.randint(1, MAP_W - 2), self.rng.randint(1, MAP_H - 2)
            self.enemies.append(Enemy(x, y, 20))

    def draw(self, stdscr):
        stdscr.erase()

        max_y, max_x = stdscr.getmaxyx()

        # 🔴 terminal too small check
        if max_y < MAP_TOP + MAP_H + 5 or max_x < MAP_W:
            stdscr.addstr(0, 0, "Terminal too small! Resize please.")
            stdscr.refresh()
            return

        self.safe_addstr(stdscr, 0, 0, f"HP {self.state.hp}")
        self.safe_addstr(stdscr, 1, 0, self.msg)

        enemy_positions = {(e.x, e.y) for e in self.enemies}

        for y in range(MAP_H):
            for x in range(MAP_W):
                if (x, y) == (self.state.x, self.state.y):
                    ch = "@"
                elif (x, y) in enemy_positions:
                    ch = "g"
                else:
                    ch = self.tiles[y][x]

                self.safe_addch(
                    stdscr,
                    MAP_TOP + y,
                    x,
                    ch,
                    self.style_for_tile(ch),
                )

        stdscr.refresh()

    def loop(self, stdscr):
        curses.curs_set(0)
        self.init_colors()
        stdscr.nodelay(True)

        while True:
            self.draw(stdscr)
            key = stdscr.getch()

            if key == ord("q"):
                break

            elif key in (ord("w"), curses.KEY_UP):
                self.state.y = max(0, self.state.y - 1)
            elif key in (ord("s"), curses.KEY_DOWN):
                self.state.y = min(MAP_H - 1, self.state.y + 1)
            elif key in (ord("a"), curses.KEY_LEFT):
                self.state.x = max(0, self.state.x - 1)
            elif key in (ord("d"), curses.KEY_RIGHT):
                self.state.x = min(MAP_W - 1, self.state.x + 1)

            time.sleep(0.05)


def main():
    curses.wrapper(SandboxGame().loop)


if __name__ == "__main__":
    main()
