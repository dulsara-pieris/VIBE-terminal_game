#!/usr/bin/env python3
"""VIBE Terminal Game: fast arcade survival game for Linux terminals."""

from __future__ import annotations

import argparse
import curses
import random
import time
from dataclasses import dataclass, field

MAP_W = 58
MAP_H = 22
MAP_TOP = 3

COLOR_DEFAULT = 1
COLOR_PLAYER = 2
COLOR_ENEMY = 3
COLOR_BULLET = 4
COLOR_HEART = 5


@dataclass
class Enemy:
    x: int
    y: int
    hp: int = 1


@dataclass
class Bullet:
    x: int
    y: int
    dx: int
    dy: int


@dataclass
class Heart:
    x: int
    y: int
    ttl: int = 120


@dataclass
class State:
    x: int = MAP_W // 2
    y: int = MAP_H // 2
    hp: int = 5
    max_hp: int = 5
    score: int = 0
    wave: int = 1
    terrain_seed: int = field(default_factory=lambda: random.randint(1, 999999))


class ArcadeGame:
    def __init__(self) -> None:
        self.state = State()
        self.msg = "Arcade mode: move (WASD/arrows), shoot (SPACE or IJKL), pause (H), quit (Q)."
        self.rng = random.Random(self.state.terrain_seed)
        self.enemies: list[Enemy] = []
        self.bullets: list[Bullet] = []
        self.hearts: list[Heart] = []
        self.use_color = False
        self.paused = False
        self.fire_dx, self.fire_dy = 1, 0
        self.ticks = 0
        self.invuln_ticks = 0

    def init_colors(self) -> None:
        if not curses.has_colors():
            return
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(COLOR_DEFAULT, curses.COLOR_WHITE, -1)
        curses.init_pair(COLOR_PLAYER, curses.COLOR_CYAN, -1)
        curses.init_pair(COLOR_ENEMY, curses.COLOR_RED, -1)
        curses.init_pair(COLOR_BULLET, curses.COLOR_YELLOW, -1)
        curses.init_pair(COLOR_HEART, curses.COLOR_GREEN, -1)
        self.use_color = True

    def style_for(self, ch: str) -> int:
        if not self.use_color:
            return curses.A_NORMAL
        if ch == "@":
            return curses.color_pair(COLOR_PLAYER) | curses.A_BOLD
        if ch == "g":
            return curses.color_pair(COLOR_ENEMY) | curses.A_BOLD
        if ch == "*":
            return curses.color_pair(COLOR_BULLET) | curses.A_BOLD
        if ch == "+":
            return curses.color_pair(COLOR_HEART) | curses.A_BOLD
        return curses.color_pair(COLOR_DEFAULT)

    def spawn_enemy(self) -> None:
        edge = self.rng.choice(["top", "bottom", "left", "right"])
        if edge == "top":
            ex, ey = self.rng.randint(1, MAP_W - 2), 1
        elif edge == "bottom":
            ex, ey = self.rng.randint(1, MAP_W - 2), MAP_H - 2
        elif edge == "left":
            ex, ey = 1, self.rng.randint(1, MAP_H - 2)
        else:
            ex, ey = MAP_W - 2, self.rng.randint(1, MAP_H - 2)
        if (ex, ey) != (self.state.x, self.state.y):
            self.enemies.append(Enemy(ex, ey))

    def maybe_spawn_heart(self) -> None:
        if self.rng.random() < 0.004 and len(self.hearts) < 2:
            self.hearts.append(Heart(self.rng.randint(2, MAP_W - 3), self.rng.randint(2, MAP_H - 3)))

    def move_player(self, dx: int, dy: int) -> None:
        nx = min(MAP_W - 2, max(1, self.state.x + dx))
        ny = min(MAP_H - 2, max(1, self.state.y + dy))
        self.state.x, self.state.y = nx, ny
        if dx != 0 or dy != 0:
            self.fire_dx, self.fire_dy = dx, dy

    def shoot(self, dx: int | None = None, dy: int | None = None) -> None:
        sdx = self.fire_dx if dx is None else dx
        sdy = self.fire_dy if dy is None else dy
        if sdx == 0 and sdy == 0:
            sdx = 1
        bx, by = self.state.x + sdx, self.state.y + sdy
        if 1 <= bx < MAP_W - 1 and 1 <= by < MAP_H - 1:
            self.bullets.append(Bullet(bx, by, sdx, sdy))

    def update_bullets(self) -> None:
        updated: list[Bullet] = []
        for bullet in self.bullets:
            bullet.x += bullet.dx
            bullet.y += bullet.dy
            if 1 <= bullet.x < MAP_W - 1 and 1 <= bullet.y < MAP_H - 1:
                updated.append(bullet)
        self.bullets = updated

    def update_enemies(self) -> None:
        for enemy in self.enemies:
            dx = self.state.x - enemy.x
            dy = self.state.y - enemy.y
            step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
            step_y = 0 if dy == 0 else (1 if dy > 0 else -1)
            if abs(dx) > abs(dy):
                enemy.x += step_x
            else:
                enemy.y += step_y

    def handle_collisions(self) -> None:
        bullet_positions = {(b.x, b.y): b for b in self.bullets}
        survivors: list[Enemy] = []
        kills = 0
        for enemy in self.enemies:
            if (enemy.x, enemy.y) in bullet_positions:
                kills += 1
            else:
                survivors.append(enemy)
        if kills:
            self.state.score += kills * 10
            self.msg = f"Boom! {kills} enemy down."
        self.enemies = survivors
        self.bullets = [b for b in self.bullets if (b.x, b.y) not in {(e.x, e.y) for e in self.enemies}]

        for heart in list(self.hearts):
            if (heart.x, heart.y) == (self.state.x, self.state.y):
                self.state.hp = min(self.state.max_hp, self.state.hp + 1)
                self.hearts.remove(heart)
                self.msg = "Picked up a heart: +1 HP"

        if self.invuln_ticks > 0:
            return
        for enemy in self.enemies:
            if (enemy.x, enemy.y) == (self.state.x, self.state.y):
                self.state.hp -= 1
                self.invuln_ticks = 10
                self.msg = "You got hit! Keep moving."
                break

    def tick(self) -> None:
        self.ticks += 1
        if self.invuln_ticks > 0:
            self.invuln_ticks -= 1

        spawn_rate = max(5, 18 - self.state.wave)
        if self.ticks % spawn_rate == 0:
            self.spawn_enemy()
        if self.ticks % 120 == 0:
            self.state.wave += 1
            self.msg = f"Wave {self.state.wave}! Enemies are faster now."

        self.maybe_spawn_heart()
        for heart in self.hearts:
            heart.ttl -= 1
        self.hearts = [h for h in self.hearts if h.ttl > 0]

        self.update_bullets()
        if self.ticks % 2 == 0:
            self.update_enemies()
        self.handle_collisions()

    def handle_key(self, key: int) -> bool:
        if key in (ord("q"), ord("Q")):
            return False
        if key in (ord("h"), ord("H")):
            self.paused = not self.paused
            self.msg = "Paused." if self.paused else "Back to action!"
            return True

        if key in (curses.KEY_UP, ord("w"), ord("W")):
            self.move_player(0, -1)
        elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
            self.move_player(0, 1)
        elif key in (curses.KEY_LEFT, ord("a"), ord("A")):
            self.move_player(-1, 0)
        elif key in (curses.KEY_RIGHT, ord("d"), ord("D")):
            self.move_player(1, 0)
        elif key == ord(" "):
            self.shoot()
        elif key in (ord("i"), ord("I")):
            self.shoot(0, -1)
        elif key in (ord("k"), ord("K")):
            self.shoot(0, 1)
        elif key in (ord("j"), ord("J")):
            self.shoot(-1, 0)
        elif key in (ord("l"), ord("L")):
            self.shoot(1, 0)
        return True

    def draw(self, stdscr: curses.window) -> None:
        stdscr.erase()
        hud = f"HP {self.state.hp}/{self.state.max_hp} | Score {self.state.score} | Wave {self.state.wave} | Enemies {len(self.enemies)}"
        stdscr.addstr(0, 0, hud[: MAP_W + 25])
        stdscr.addstr(1, 0, self.msg[: MAP_W + 25])

        for x in range(MAP_W):
            stdscr.addch(MAP_TOP, x, "#")
            stdscr.addch(MAP_TOP + MAP_H - 1, x, "#")
        for y in range(1, MAP_H - 1):
            stdscr.addch(MAP_TOP + y, 0, "#")
            stdscr.addch(MAP_TOP + y, MAP_W - 1, "#")

        canvas: dict[tuple[int, int], str] = {}
        for heart in self.hearts:
            canvas[(heart.x, heart.y)] = "+"
        for enemy in self.enemies:
            canvas[(enemy.x, enemy.y)] = "g"
        for bullet in self.bullets:
            canvas[(bullet.x, bullet.y)] = "*"
        player_symbol = "@" if self.invuln_ticks % 2 == 0 else "o"
        canvas[(self.state.x, self.state.y)] = player_symbol

        for y in range(1, MAP_H - 1):
            for x in range(1, MAP_W - 1):
                ch = canvas.get((x, y), " ")
                stdscr.addch(MAP_TOP + y, x, ch, self.style_for(ch))

        controls = "Move: WASD/Arrows | Shoot: SPACE or IJKL | Pause: H | Quit: Q | + = heal"
        stdscr.addstr(MAP_TOP + MAP_H, 0, controls[: MAP_W + 25])
        stdscr.refresh()

    def loop(self, stdscr: curses.window) -> None:
        curses.curs_set(0)
        self.init_colors()
        stdscr.nodelay(True)
        stdscr.timeout(50)

        while self.state.hp > 0:
            self.draw(stdscr)
            key = stdscr.getch()
            if key != -1 and not self.handle_key(key):
                return
            if not self.paused:
                self.tick()
            time.sleep(0.02)

        self.draw(stdscr)
        stdscr.addstr(MAP_TOP + MAP_H + 1, 0, f"Game over! Final score: {self.state.score}. Press any key.")
        stdscr.nodelay(False)
        stdscr.getch()


def smoke_test() -> None:
    game = ArcadeGame()
    for _ in range(40):
        game.move_player(random.choice([-1, 0, 1]), random.choice([-1, 0, 1]))
        if random.random() < 0.4:
            game.shoot()
        game.tick()
    assert game.state.max_hp >= 1
    print("smoke-ok")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="VIBE arcade terminal game")
    parser.add_argument("--smoke-test", action="store_true", help="Run non-interactive smoke test")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.smoke_test:
        smoke_test()
        return
    curses.wrapper(ArcadeGame().loop)


if __name__ == "__main__":
    main()
