import pygame
import sys
import os
import heapq
import time
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import ui


class PathfindingVisualiser:
    def __init__(self):
        self.rows = 25
        self.cols = 25
        self.cell_size = 18

        self.grid_width = self.cols * self.cell_size
        self.offset_x = (ui.WIDTH - self.grid_width) // 2
        self.offset_y = 230

        self.grid = [["empty" for _ in range(self.cols)] for _ in range(self.rows)]

        self.start = None
        self.end = None

        self.path = []
        self.visited = set()
        self.visited_order = []
        self.final_path = []

        self.animating = False
        self.animation_stage = None
        self.step_index = 0
        self.last_step_time = 0
        self.step_delay = 20

        self.status_message = "Click start, end, then walls"

        self.start_time = None
        self.algorithm_time = 0

        self.test_mode = False
        self.test_stage = 0
        self.test_cells = []
        self.test_timer = 0

        self.controls_panel = pygame.Rect(
            24,
            ui.HEADER_H + 16,
            ui.WIDTH - 48,
            150
        )

        self.buttons = {}

    def create_buttons(self):
        labels = ["Start", "Clear"]

        button_w = 140
        spacing = 12

        total_width = len(labels) * button_w + (len(labels) - 1) * spacing
        start_x = ui.WIDTH // 2 - total_width // 2
        y = self.controls_panel.bottom - 50

        self.buttons = {}

        for i, label in enumerate(labels):
            self.buttons[label] = pygame.Rect(
                start_x + i * (button_w + spacing),
                y,
                button_w,
                42
            )

    def clear(self):
        self.grid = [["empty" for _ in range(self.cols)] for _ in range(self.rows)]
        self.start = None
        self.end = None
        self.path = []
        self.visited = set()
        self.visited_order = []
        self.final_path = []
        self.animating = False
        self.animation_stage = None
        self.step_index = 0
        self.start_time = None
        self.algorithm_time = 0
        self.status_message = "Grid cleared"

    def handle_click(self, pos):
        if self.animating or self.test_mode:
            return

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
            self.status_message = "Start point set"
            return

        if not self.end and (row, col) != self.start:
            self.end = (row, col)
            self.grid[row][col] = "end"
            self.status_message = "End point set"
            return

        if (row, col) != self.start and (row, col) != self.end:
            self.grid[row][col] = "wall" if self.grid[row][col] == "empty" else "empty"

    def run_pathfinding(self):
        if self.animating:
            return

        if not self.start or not self.end:
            self.status_message = "Set Start and End first"
            return

        self.start_time = time.time()

        pq = []
        heapq.heappush(pq, (0, self.start))

        came_from = {}
        dist = {self.start: 0}

        visited_check = set()
        visited_order = []

        while pq:
            cost, current = heapq.heappop(pq)

            if current in visited_check:
                continue

            visited_check.add(current)
            visited_order.append(current)

            if current == self.end:
                break

            r, c = current

            for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nr, nc = r + dr, c + dc

                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    if self.grid[nr][nc] == "wall":
                        continue

                    new_cost = cost + 1

                    if (nr, nc) not in dist or new_cost < dist[(nr, nc)]:
                        dist[(nr, nc)] = new_cost
                        heapq.heappush(pq, (new_cost, (nr, nc)))
                        came_from[(nr, nc)] = current

        path = []
        node = self.end

        while node in came_from:
            path.append(node)
            node = came_from[node]

        path.reverse()

        self.visited = set()
        self.path = []
        self.visited_order = visited_order
        self.final_path = path

        self.animating = True
        self.animation_stage = "visited"
        self.step_index = 0
        self.last_step_time = pygame.time.get_ticks()

        if path:
            self.algorithm_time = round(time.time() - self.start_time, 3)
            self.status_message = "Search complete"
        else:
            self.algorithm_time = round(time.time() - self.start_time, 3)
            self.status_message = "No path found"

    def start_test(self):
        self.clear()

        self.test_mode = True
        self.test_stage = 0
        self.test_cells = random.sample(
            [(r, c) for r in range(self.rows) for c in range(self.cols)],
            2
        )
        self.test_timer = pygame.time.get_ticks()

        self.status_message = "Test running"

    def update_test(self):
        if not self.test_mode:
            return

        now = pygame.time.get_ticks()
        if now - self.test_timer < 300:
            return

        self.test_timer = now

        if self.test_stage == 0:
            self.start = self.test_cells[0]
            r, c = self.start
            self.grid[r][c] = "start"

        elif self.test_stage == 1:
            self.end = self.test_cells[1]
            r, c = self.end
            self.grid[r][c] = "end"

        elif self.test_stage == 2:
            for _ in range(30):
                r = random.randint(0, self.rows - 1)
                c = random.randint(0, self.cols - 1)
                if (r, c) not in [self.start, self.end]:
                    self.grid[r][c] = "wall"

        elif self.test_stage == 3:
            self.run_pathfinding()
            self.test_mode = False
            self.test_stage = 0
            return

        self.test_stage += 1

    def update_animation(self):
        if not self.animating:
            return

        now = pygame.time.get_ticks()

        if now - self.last_step_time < self.step_delay:
            return

        self.last_step_time = now

        if self.animation_stage == "visited":
            if self.step_index < len(self.visited_order):
                cell = self.visited_order[self.step_index]
                if cell != self.start and cell != self.end:
                    self.visited.add(cell)
                self.step_index += 1
            else:
                self.animation_stage = "path"
                self.step_index = 0

        elif self.animation_stage == "path":
            if self.step_index < len(self.final_path):
                cell = self.final_path[self.step_index]
                if cell != self.start and cell != self.end:
                    self.path.append(cell)
                self.step_index += 1
            else:
                self.animating = False
                self.animation_stage = None

                if self.final_path:
                    self.status_message = f"Path found in {self.algorithm_time}s"
                else:
                    self.status_message = "No path found"

    def draw_grid(self, screen):
        for r in range(self.rows):
            for c in range(self.cols):
                x = self.offset_x + c * self.cell_size
                y = self.offset_y + r * self.cell_size

                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)

                colour = ui.WHITE

                if self.grid[r][c] == "wall":
                    colour = ui.BLACK
                elif (r, c) in self.visited:
                    colour = ui.LIGHT_BLUE
                if (r, c) in self.path:
                    colour = ui.YELLOW
                if (r, c) == self.start:
                    colour = ui.GREEN
                if (r, c) == self.end:
                    colour = ui.ORANGE

                pygame.draw.rect(screen, colour, rect)
                pygame.draw.rect(screen, ui.BLACK, rect, 1)

    def draw_controls(self, screen, fonts, mouse):
        ui.draw_panel(screen, self.controls_panel)

        ui.draw_text(
            screen,
            "Visualise pathfinding",
            self.controls_panel.centerx,
            self.controls_panel.y + 28,
            fonts["heading"],
            ui.TEXT_1,
            centre=True
        )

        for label, rect in self.buttons.items():
            ui.draw_button(
                screen,
                rect,
                label,
                fonts["small"],
                mouse,
                style="start" if label == "Start" else "ghost"
            )

        back = ui.draw_back_button(screen, fonts["small"], mouse)
        test = ui.draw_test_button(screen, fonts["small"], mouse)

        self.back_btn = back
        self.test_btn = test

    def draw(self, screen, fonts, mouse):
        ui.clear_screen(screen)

        ui.draw_header(screen, "Pathfinding", fonts, right_label="Algorithms")

        self.draw_controls(screen, fonts, mouse)
        self.draw_grid(screen)

        ui.draw_status(screen, self.status_message, fonts["small"])


def run_pathfinding(screen, clock):
    fonts = ui.create_fonts()
    vis = PathfindingVisualiser()
    vis.create_buttons()

    actions = {
        "Start": vis.run_pathfinding,
        "Clear": vis.clear
    }

    running = True

    while running:
        mouse = pygame.mouse.get_pos()

        vis.update_animation()
        vis.update_test()
        vis.draw(screen, fonts, mouse)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if vis.back_btn.collidepoint(event.pos):
                    running = False
                    continue

                if vis.test_btn.collidepoint(event.pos):
                    vis.start_test()
                    continue

                for label, rect in vis.buttons.items():
                    if rect.collidepoint(event.pos):
                        actions[label]()
                        break

                vis.handle_click(event.pos)

        pygame.display.flip()
        clock.tick(ui.FPS)


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((ui.WIDTH, ui.HEIGHT))
    clock = pygame.time.Clock()
    run_pathfinding(screen, clock)
