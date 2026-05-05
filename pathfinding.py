import pygame
import sys
import os
import heapq
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from configure import *
from utilities import *


class PathfindingVisualiser:
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

        self.path = []
        self.visited = set()

        self.status_message = "Click start, then end, then walls"
        self.ui_block = pygame.Rect(0, 0, WIDTH, 150)

        self.buttons = {}

    def create_buttons(self):
        center = WIDTH // 2
        labels = ["Start", "Clear"]

        button_w = 140
        spacing = 30

        total_width = len(labels) * button_w + (len(labels) - 1) * spacing
        start_x = center - total_width // 2
        y = 100

        for i, label in enumerate(labels):
            x = start_x + i * (button_w + spacing)
            self.buttons[label.lower()] = pygame.Rect(x, y, button_w, 40)

    def clear(self):
        self.grid = [["empty" for _ in range(self.cols)] for _ in range(self.rows)]
        self.start = None
        self.end = None
        self.path = []
        self.visited = set()
        self.status_message = "Grid cleared"

    def handle_click(self, pos):
        x, y = pos

        if y < self.offset_y:
            return

        col = (x - self.offset_x) // self.cell_size
        row = (y - self.offset_y) // self.cell_size

        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return

        if not self.start:
            self.start = (row, col)
            self.grid[row][col] = "start"
            self.status_message = "Start set. Select end"
            return

        if not self.end and (row, col) != self.start:
            self.end = (row, col)
            self.grid[row][col] = "end"
            self.status_message = "Add walls or press start"
            return

        if (row, col) != self.start and (row, col) != self.end:
            if self.grid[row][col] == "wall":
                self.grid[row][col] = "empty"

            else:
                self.grid[row][col] = "wall"
            self.status_message = "Add more walls or click the wall to remove"


    def run_pathfinding(self):
        if not self.start or not self.end:
            self.status_message = "Set start and end first"
            return

        start_time = time.time()

        pq = []
        heapq.heappush(pq, (0, self.start))

        came_from = {}
        dist = {self.start: 0}

        self.visited = set()

        while pq:
            cost, current = heapq.heappop(pq)

            if current == self.end:
                break

            if current in self.visited:
                continue

            self.visited.add(current)

            r, c = current

            for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
                nr, nc = r + dr, c + dc

                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    if self.grid[nr][nc] == "wall":
                        continue

                    new_cost = cost + 1

                    if (nr, nc) not in dist or new_cost < dist[(nr, nc)]:
                        dist[(nr, nc)] = new_cost
                        heapq.heappush(pq, (new_cost, (nr, nc)))
                        came_from[(nr, nc)] = current

        self.path = []
        node = self.end

        while node in came_from:
            self.path.append(node)
            node = came_from[node]

        self.path.reverse()

        end_time = time.time()
        elapsed = round(end_time - start_time, 3)

        if self.path:
            steps = len(self.path)
            self.status_message = f"Path found {steps} steps in {elapsed}s"
        else:
            self.status_message = "No path found"

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
                elif (r, c) in self.visited:
                    colour = LIGHT_BLUE
                if (r, c) in self.path:
                    colour = YELLOW
                if (r, c) == self.start:
                    colour = GREEN
                if (r, c) == self.end:
                    colour = ORANGE

                pygame.draw.rect(screen, colour, rect)
                pygame.draw.rect(screen, BLACK, rect, 1)

    def draw_ui(self, screen, fonts):
        draw_text(screen, "Pathfinding", WIDTH // 2, 60, fonts["heading"], TEXT, centre=True)

    def draw_buttons(self, screen, fonts, mouse):
        draw_button(screen, self.buttons["start"], "Start", fonts["small"], mouse)
        draw_button(screen, self.buttons["clear"], "Clear", fonts["small"], mouse)

    def draw_screen(self, screen, fonts, mouse):
        clear_screen(screen)

        self.draw_ui_block(screen)
        self.draw_ui(screen, fonts)
        self.draw_grid(screen)
        self.draw_buttons(screen, fonts, mouse)

        draw_status(screen, self.status_message, fonts["small"])


def run_pathfinding(screen, clock):
    fonts = create_fonts()
    vis = PathfindingVisualiser()
    vis.create_buttons()

    running = True

    while running:
        mouse = pygame.mouse.get_pos()

        vis.draw_screen(screen, fonts, mouse)
        back = draw_back_button(screen, fonts["small"], mouse)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back.collidepoint(event.pos):
                    running = False
                elif vis.buttons["start"].collidepoint(event.pos):
                    vis.run_pathfinding()
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

    run_pathfinding(screen, clock)