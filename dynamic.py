import pygame
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from configure import *
from utilities import *


class DynamicProgrammingVisualiser:
    def __init__(self):
        self.rows = 25
        self.cols = 25
        self.cell_size = 19

        self.grid_width = self.cols * self.cell_size
        self.offset_x = (WIDTH - self.grid_width) // 2
        self.offset_y = 165

        self.grid = [["empty" for _ in range(self.cols)] for _ in range(self.rows)]

        self.start = None
        self.end = None

        self.dp = []
        self.path = []
        self.visited = set()

        self.running = False

        self.status_message = "Click start, end, walls, then run"

        self.ui_block = pygame.Rect(0, 0, WIDTH, 150)
        self.buttons = {}

        self.start_time = 0

    def create_buttons(self):
        center = WIDTH // 2

        labels = ["Run", "Clear"]

        button_w = 140
        spacing = 30

        total = len(labels) * button_w + (len(labels) - 1) * spacing
        start_x = center - total // 2
        y = 100

        self.buttons = {}

        for i, label in enumerate(labels):
            self.buttons[label.lower()] = pygame.Rect(
                start_x + i * (button_w + spacing),
                y,
                button_w,
                40
            )

    def clear(self):
        self.grid = [["empty" for _ in range(self.cols)] for _ in range(self.rows)]
        self.start = None
        self.end = None
        self.dp = []
        self.path = []
        self.visited = set()
        self.running = False
        self.status_message = "Grid cleared"

    def handle_click(self, pos):
        x, y = pos

        if y < self.offset_y:
            return

        col = (x - self.offset_x) // self.cell_size
        row = (y - self.offset_y) // self.cell_size

        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return

        cell = (row, col)

        if not self.start:
            self.start = cell
            self.grid[row][col] = "start"
            self.status_message = "Start set"
            return

        if not self.end and cell != self.start:
            self.end = cell
            self.grid[row][col] = "end"
            self.status_message = "End set"
            return

        if cell != self.start and cell != self.end:
            if self.grid[row][col] == "wall":
                self.grid[row][col] = "empty"
            else:
                self.grid[row][col] = "wall"

    def run_dp(self):
        if not self.start or not self.end:
            self.status_message = "Set start and end first"
            return

        self.start_time = time.time()

        sr, sc = self.start
        er, ec = self.end

        dp = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        dp[sr][sc] = 1

        for r in range(self.rows):
            for c in range(self.cols):

                if self.grid[r][c] == "wall":
                    continue

                if r == sr and c == sc:
                    continue

                from_top = dp[r - 1][c] if r > 0 else 0
                from_left = dp[r][c - 1] if c > 0 else 0

                dp[r][c] = from_top + from_left

        self.dp = dp

        self.reconstruct_path()

        elapsed = time.time() - self.start_time

        self.status_message = f"Paths computed in {elapsed:.2f}s"

    def reconstruct_path(self):
        if not self.start or not self.end:
            return

        r, c = self.end

        path = []

        while (r, c) != self.start:
            path.append((r, c))

            up = self.dp[r - 1][c] if r > 0 else 0
            left = self.dp[r][c - 1] if c > 0 else 0

            if up >= left and r > 0:
                r -= 1
            elif c > 0:
                c -= 1
            else:
                break

        path.append(self.start)
        self.path = path[::-1]

    def draw_ui_block(self, screen):
        pygame.draw.rect(screen, BACKGROUND, self.ui_block)
        pygame.draw.line(screen, BLACK, (0, self.ui_block.bottom), (WIDTH, self.ui_block.bottom), 2)

    def draw_grid(self, screen):
        for r in range(self.rows):
            for c in range(self.cols):

                x = self.offset_x + c * self.cell_size
                y = self.offset_y + r * self.cell_size

                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)

                colour = WHITE

                if self.grid[r][c] == "wall":
                    colour = BLACK
                elif (r, c) == self.start:
                    colour = GREEN
                elif (r, c) == self.end:
                    colour = ORANGE
                elif (r, c) in self.path:
                    colour = YELLOW

                pygame.draw.rect(screen, colour, rect)
                pygame.draw.rect(screen, BLACK, rect, 1)

    def draw_buttons(self, screen, fonts, mouse):
        draw_button(screen, self.buttons["run"], "Run", fonts["small"], mouse)
        draw_button(screen, self.buttons["clear"], "Clear", fonts["small"], mouse)

    def draw_ui(self, screen, fonts):
        draw_text(screen, "Dynamic Programming Grid", WIDTH // 2, 60, fonts["heading"], TEXT, centre=True)

    def draw_screen(self, screen, fonts, mouse):
        clear_screen(screen)

        self.draw_ui_block(screen)
        self.draw_ui(screen, fonts)
        self.draw_grid(screen)
        self.draw_buttons(screen, fonts, mouse)

        draw_status(screen, self.status_message, fonts["small"])


def run_dynamic(screen, clock):
    fonts = create_fonts()
    vis = DynamicProgrammingVisualiser()
    vis.create_buttons()

    running = True

    while running:
        mouse = pygame.mouse.get_pos()

        vis.draw_screen(screen, fonts, mouse)
        back = draw_back_button(screen, fonts["small"], mouse)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.MOUSEBUTTONDOWN:
                if back.collidepoint(event.pos):
                    running = False

                elif vis.buttons["run"].collidepoint(event.pos):
                    vis.run_dp()

                elif vis.buttons["clear"].collidepoint(event.pos):
                    vis.clear()

                else:
                    vis.handle_click(event.pos)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    run_dynamic(screen, clock)