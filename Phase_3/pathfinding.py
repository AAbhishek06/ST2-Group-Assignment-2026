# Imports
import pygame
import sys
import os
import heapq
import time
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import ui

# Visualiser setup
class PathfindingVisualiser:
    def __init__(self):
        self.rows = 25
        self.cols = 25
        self.cell_size = 18

        self.grid_width = self.cols * self.cell_size
        self.offset_x = (ui.WIDTH - self.grid_width) // 2
        self.offset_y = 230

        self.grid = self.make_empty_grid()
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

        self.controls_panel = pygame.Rect(24, ui.HEADER_H + 16, ui.WIDTH - 48, 150)
        self.buttons = {}
        self.back_btn = None
        self.test_btn = None

    def make_empty_grid(self):
        return [["empty" for _ in range(self.cols)] for _ in range(self.rows)]

    def create_buttons(self):
        labels = ["Start", "Clear"]
        button_width = 140
        spacing = 12
        total_width = len(labels) * button_width + (len(labels) - 1) * spacing
        start_x = ui.WIDTH // 2 - total_width // 2
        y = self.controls_panel.bottom - 50

        self.buttons = {
            label: pygame.Rect(start_x + i * (button_width + spacing), y, button_width, 42)
            for i, label in enumerate(labels)
        }

    def reset_path_state(self):
        self.path = []
        self.visited = set()
        self.visited_order = []
        self.final_path = []
        self.animating = False
        self.animation_stage = None
        self.step_index = 0
        self.start_time = None
        self.algorithm_time = 0

    # User actions
    def clear(self):
        self.grid = self.make_empty_grid()
        self.start = None
        self.end = None
        self.reset_path_state()
        self.status_message = "Grid cleared"

    def handle_click(self, pos):
        if self.animating or self.test_mode:
            return

        cell = self.get_clicked_cell(pos)

        if cell is None:
            return

        row, col = cell

        if not self.start:
            self.start = cell
            self.grid[row][col] = "start"
            self.status_message = "Start point set"
            return

        if not self.end and cell != self.start:
            self.end = cell
            self.grid[row][col] = "end"
            self.status_message = "End point set"
            return

        if cell != self.start and cell != self.end:
            self.grid[row][col] = "wall" if self.grid[row][col] == "empty" else "empty"

    def get_clicked_cell(self, pos):
        x, y = pos

        if y < self.offset_y:
            return None

        col = (x - self.offset_x) // self.cell_size
        row = (y - self.offset_y) // self.cell_size

        if 0 <= row < self.rows and 0 <= col < self.cols:
            return row, col

        return None

    # Pathfinding logic
    def run_pathfinding(self):
        if self.animating:
            return

        if not self.start or not self.end:
            self.status_message = "Set Start and End first"
            return

        self.start_time = time.time()

        pq = [(0, self.start)]
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

            for neighbour in self.get_neighbours(current):
                new_cost = cost + 1

                if neighbour not in dist or new_cost < dist[neighbour]:
                    dist[neighbour] = new_cost
                    heapq.heappush(pq, (new_cost, neighbour))
                    came_from[neighbour] = current

        self.visited = set()
        self.path = []
        self.visited_order = visited_order
        self.final_path = self.reconstruct_path(came_from)
        self.algorithm_time = round(time.time() - self.start_time, 3)

        self.animating = True
        self.animation_stage = "visited"
        self.step_index = 0
        self.last_step_time = pygame.time.get_ticks()

        self.status_message = "Search complete" if self.final_path else "No path found"

    def get_neighbours(self, cell):
        row, col = cell
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        for row_change, col_change in directions:
            new_row = row + row_change
            new_col = col + col_change

            if 0 <= new_row < self.rows and 0 <= new_col < self.cols:
                if self.grid[new_row][new_col] != "wall":
                    yield new_row, new_col

    def reconstruct_path(self, came_from):
        path = []
        node = self.end

        while node in came_from:
            path.append(node)
            node = came_from[node]

        path.reverse()
        return path

    # Animation and testing
    def update_animation(self):
        if not self.animating:
            return

        now = pygame.time.get_ticks()

        if now - self.last_step_time < self.step_delay:
            return

        self.last_step_time = now

        if self.animation_stage == "visited":
            self.animate_visited_step()

        elif self.animation_stage == "path":
            self.animate_path_step()

    def animate_visited_step(self):
        if self.step_index < len(self.visited_order):
            cell = self.visited_order[self.step_index]

            if cell != self.start and cell != self.end:
                self.visited.add(cell)

            self.step_index += 1
            return

        self.animation_stage = "path"
        self.step_index = 0

    def animate_path_step(self):
        if self.step_index < len(self.final_path):
            cell = self.final_path[self.step_index]

            if cell != self.start and cell != self.end:
                self.path.append(cell)

            self.step_index += 1
            return

        self.animating = False
        self.animation_stage = None

        if self.final_path:
            self.status_message = f"Path found in {self.algorithm_time}s"
        else:
            self.status_message = "No path found"

    def start_test(self):
        self.clear()

        self.test_mode = True
        self.test_stage = 0
        self.test_cells = random.sample(
            [(row, col) for row in range(self.rows) for col in range(self.cols)],
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
            self.set_test_cell("start")

        elif self.test_stage == 1:
            self.set_test_cell("end")

        elif self.test_stage == 2:
            self.add_test_walls()

        elif self.test_stage == 3:
            self.run_pathfinding()
            self.test_mode = False
            self.test_stage = 0
            return

        self.test_stage += 1

    def set_test_cell(self, cell_type):
        cell = self.test_cells[0] if cell_type == "start" else self.test_cells[1]
        row, col = cell

        if cell_type == "start":
            self.start = cell
        else:
            self.end = cell

        self.grid[row][col] = cell_type

    def add_test_walls(self):
        for _ in range(30):
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)

            if (row, col) not in (self.start, self.end):
                self.grid[row][col] = "wall"

    # Drawing interface
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
            style = "start" if label == "Start" else "ghost"
            ui.draw_button(screen, rect, label, fonts["small"], mouse, style=style)

        self.back_btn = ui.draw_back_button(screen, fonts["small"], mouse)
        self.test_btn = ui.draw_test_button(screen, fonts["small"], mouse)

    def draw_grid(self, screen):
        for row in range(self.rows):
            for col in range(self.cols):
                self.draw_cell(screen, row, col)

    def draw_cell(self, screen, row, col):
        x = self.offset_x + col * self.cell_size
        y = self.offset_y + row * self.cell_size
        rect = pygame.Rect(x, y, self.cell_size, self.cell_size)

        pygame.draw.rect(screen, self.get_cell_colour(row, col), rect)
        pygame.draw.rect(screen, ui.BLACK, rect, 1)

    def get_cell_colour(self, row, col):
        cell = (row, col)

        if self.grid[row][col] == "wall":
            return ui.BLACK

        if cell in self.path:
            return ui.YELLOW

        if cell in self.visited:
            return ui.LIGHT_BLUE

        if cell == self.start:
            return ui.GREEN

        if cell == self.end:
            return ui.ORANGE

        return ui.WHITE

    def draw(self, screen, fonts, mouse):
        ui.clear_screen(screen)
        ui.draw_header(screen, "Pathfinding", fonts, right_label="Algorithms")

        self.draw_controls(screen, fonts, mouse)
        self.draw_grid(screen)

        ui.draw_status(screen, self.status_message, fonts["small"])

# Main loop
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

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if vis.back_btn.collidepoint(event.pos):
                    running = False
                    continue

                if vis.test_btn.collidepoint(event.pos):
                    vis.start_test()
                    continue

                clicked_button = False

                for label, rect in vis.buttons.items():
                    if rect.collidepoint(event.pos):
                        actions[label]()
                        clicked_button = True
                        break

                if not clicked_button:
                    vis.handle_click(event.pos)

        pygame.display.flip()
        clock.tick(ui.FPS)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((ui.WIDTH, ui.HEIGHT))
    clock = pygame.time.Clock()
    run_pathfinding(screen, clock)
