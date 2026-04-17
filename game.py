#!/usr/bin/env python3
import curses
import random
import time

W, H = 60, 25

class Game:
        def __init__(self):
                self.px = W // 2
                self.py = H // 2
                self.enemies = []
                self.bullets = []
                self.score = 0
                self.hp = 10
                self.wave = 1
                self.tick = 0

        def spawn_wave(self):
                for _ in range(3 + self.wave * 2):
                        x = random.randint(1, W-2)
                        y = random.randint(1, H-2)
                        self.enemies.append([x, y, 1])

        def move_player(self, dx, dy):
                nx = self.px + dx
                ny = self.py + dy
                if 0 < nx < W-1 and 0 < ny < H-1:
                        self.px, self.py = nx, ny

        def shoot(self):
                self.bullets.append([self.px, self.py - 1])

        def update(self):
                self.tick += 1

                # bullets move
                for b in self.bullets:
                        b[1] -= 1
                self.bullets = [b for b in self.bullets if b[1] > 0]

                # enemies move toward player
                if self.tick % 2 == 0:
                        for e in self.enemies:
                                dx = 1 if self.px > e[0] else -1 if self.px < e[0] else 0
                                dy = 1 if self.py > e[1] else -1 if self.py < e[1] else 0
                                e[0] += dx
                                e[1] += dy

                # collisions
                for b in list(self.bullets):
                        for e in list(self.enemies):
                                if b[0] == e[0] and b[1] == e[1]:
                                        self.enemies.remove(e)
                                        self.bullets.remove(b)
                                        self.score += 10
                                        break

                # enemy hits player
                for e in self.enemies:
                        if e[0] == self.px and e[1] == self.py:
                                self.hp -= 1
                                self.enemies.remove(e)

                # next wave
                if not self.enemies:
                        self.wave += 1
                        self.spawn_wave()

        def draw(self, stdscr):
                stdscr.erase()
                max_y, max_x = stdscr.getmaxyx()

                if max_y < H+2 or max_x < W:
                        stdscr.addstr(0, 0, "Resize terminal!")
                        return

                # border
                for x in range(W):
                        stdscr.addch(0, x, "#")
                        stdscr.addch(H-1, x, "#")
                for y in range(H):
                        stdscr.addch(y, 0, "#")
                        stdscr.addch(y, W-1, "#")

                # player
                stdscr.addch(self.py, self.px, "@")

                # enemies
                for e in self.enemies:
                        stdscr.addch(e[1], e[0], "X")

                # bullets
                for b in self.bullets:
                        stdscr.addch(b[1], b[0], "|")

                # HUD
                stdscr.addstr(H, 0, f"HP:{self.hp} Score:{self.score} Wave:{self.wave}")

                stdscr.refresh()


def main(stdscr):
        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.keypad(True)

        g = Game()
        g.spawn_wave()

        while g.hp > 0:
                key = stdscr.getch()

                if key == ord("q"):
                        break
                elif key in (ord("w"), curses.KEY_UP):
                        g.move_player(0, -1)
                elif key in (ord("s"), curses.KEY_DOWN):
                        g.move_player(0, 1)
                elif key in (ord("a"), curses.KEY_LEFT):
                        g.move_player(-1, 0)
                elif key in (ord("d"), curses.KEY_RIGHT):
                        g.move_player(1, 0)
                elif key == ord(" "):
                        g.shoot()

                # auto fire (arcade feel)
                if g.tick % 5 == 0:
                        g.shoot()

                g.update()
                g.draw(stdscr)

                time.sleep(0.05)

        stdscr.nodelay(False)
        stdscr.addstr(H+2, 0, f"GAME OVER | Score: {g.score} | Press any key")
        stdscr.getch()


if __name__ == "__main__":
        curses.wrapper(main)
