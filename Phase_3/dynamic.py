# Imports
import pygame
import sys
import os
import time
from collections import deque

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import ui

# Visualiser setup
class DynamicProgrammingVisualiser:
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
        self.final_path = []
        self.dp = None

        self.animating = False
        self.step_index = 0
        self.last_step_time = 0
        self.step_delay = 20

        self.status = "Click a cell to set start, end, and wall points"
        self.start_time = 0

        self.controls_panel = pygame.Rect(24, ui.HEADER_H + 16, ui.WIDTH - 48, 150)
        self.buttons = {}

        self.test_mode = False
        self.test_stage = None
        self.test_last = 0
        self.test_delay = 800

    def make_empty_grid(self):
        return [["empty" for _ in range(self.cols)] for _ in range(self.rows)]

    def create_buttons(self):
        labels = ["Run", "Clear"]
        button_width = 140
        spacing = 18
        total_width = len(labels) * button_width + (len(labels) - 1) * spacing
        start_x = ui.WIDTH // 2 - total_width // 2
        y = self.controls_panel.bottom - 50

        self.buttons = {
            label.lower(): pygame.Rect(start_x + i * (button_width + spacing), y, button_width, 42)
            for i, label in enumerate(labels)
        }

    def reset_path_state(self):
        self.path = []
        self.final_path = []
        self.dp = None
        self.animating = False
        self.step_index = 0
        self.last_step_time = 0

    # User actions
    def clear(self):
        self.grid = self.make_empty_grid()
        self.start = None
        self.end = None
        self.reset_path_state()
        self.test_mode = False
        self.test_stage = None
        self.status = "Grid cleared"

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
            self.status = "Start set"
            return

        if not self.end and cell != self.start:
            self.end = cell
            self.grid[row][col] = "end"
            self.status = "End set"
            return

        if cell != self.start and cell != self.end:
            self.grid[row][col] = "wall" if self.grid[row][col] == "empty" else "empty"
            self.reset_path_state()

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
    def run_dp(self):
        if self.animating:
            return

        if not self.start or not self.end:
            self.status = "Set start and end"
            return

        self.reset_path_state()
        self.start_time = time.time()

        self.final_path = self.find_path()
        self.path = []

        if not self.final_path:
            self.status = "No path found"
            return

        elapsed = time.time() - self.start_time

        self.animating = True
        self.step_index = 0
        self.last_step_time = pygame.time.get_ticks()
        self.status = f"Path found in {elapsed:.2f}s"

    def find_path(self):
        queue = deque([self.start])
        visited = {self.start}
        previous = {}

        directions = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1)
        ]

        while queue:
            current = queue.popleft()

            if current == self.end:
                return self.reconstruct_path(previous)

            row, col = current

            for row_change, col_change in directions:
                next_row = row + row_change
                next_col = col + col_change
                next_cell = (next_row, next_col)

                if not self.is_valid_cell(next_row, next_col):
                    continue

                if next_cell in visited:
                    continue

                visited.add(next_cell)
                previous[next_cell] = current
                queue.append(next_cell)

        return []

    def is_valid_cell(self, row, col):
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return False

        if self.grid[row][col] == "wall":
            return False

        return True

    def reconstruct_path(self, previous):
        path = []
        current = self.end

        while current != self.start:
            path.append(current)

            if current not in previous:
                return []

            current = previous[current]

        path.append(self.start)
        path.reverse()
        return path

    # Animation and testing
    def update_animation(self):
        if self.animating:
            now = pygame.time.get_ticks()

            if now - self.last_step_time >= self.step_delay:
                self.last_step_time = now
                self.animate_path_step()

        if self.test_mode:
            self.update_test()

    def animate_path_step(self):
        if self.step_index < len(self.final_path):
            cell = self.final_path[self.step_index]

            if cell != self.start and cell != self.end:
                self.path.append(cell)

            self.step_index += 1
            return

        self.animating = False
        self.status = "Complete"

    def start_test(self):
        if self.animating:
            return

        self.clear()
        self.test_mode = True
        self.test_stage = "init"
        self.test_last = pygame.time.get_ticks()
        self.status = "Test started"

    def update_test(self):
        if not self.test_mode:
            return

        now = pygame.time.get_ticks()

        if self.test_stage == "init":
            if now - self.test_last < self.test_delay:
                return

            self.setup_test_grid()
            self.test_stage = "run"
            self.run_dp()
            return

        if self.test_stage == "run" and not self.animating:
            self.test_stage = "done"
            self.test_mode = False
            self.status = "Test complete"

    def setup_test_grid(self):
        self.grid = self.make_empty_grid()
        self.reset_path_state()

        self.start = (3, 3)
        self.end = (20, 20)

        sr, sc = self.start
        er, ec = self.end

        self.grid[sr][sc] = "start"
        self.grid[er][ec] = "end"

        # Extra walls 
        walls = [
            (5, 4), (5, 5), (5, 6), (5, 7), (5, 8),
            (6, 8), (7, 8), (8, 8),

            (9, 10), (9, 11), (9, 12), (9, 13), (9, 14),
            (9, 15), (9, 16),

            (10, 12), (11, 12), (12, 12), (13, 12),

            (13, 5), (14, 5), (15, 5), (16, 5),
            (16, 6), (16, 7), (16, 8), (16, 9),

            (13, 17), (14, 17), (15, 17), (16, 17),
            (17, 17), (18, 17), (19, 17),

            (20, 8), (20, 9), (20, 10), (20, 11),
            (20, 12), (20, 13), (20, 14),

            (4, 14), (4, 15), (4, 16),
            (6, 18), (7, 18), (8, 18),
            (11, 3), (12, 3), (13, 3),
            (18, 10), (18, 11), (18, 12),
            (21, 16), (21, 17), (21, 18)
        ]

        for row, col in walls:
            if (row, col) not in (self.start, self.end):
                self.grid[row][col] = "wall"

    # Drawing interface
    def draw_controls(self, screen, fonts, mouse):
        ui.draw_panel(screen, self.controls_panel)

        ui.draw_text(
            screen,
            "Visualise grid pathfinding",
            self.controls_panel.centerx,
            self.controls_panel.y + 28,
            fonts["heading"],
            ui.TEXT_1,
            centre=True
        )

        button_styles = {
            "run": "start",
            "clear": "danger"
        }

        for key, rect in self.buttons.items():
            ui.draw_button(
                screen,
                rect,
                key.capitalize(),
                fonts["small"],
                mouse,
                style=button_styles.get(key, "neutral")
            )

    def draw_grid(self, screen, fonts):
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

        if cell == self.start:
            return ui.GREEN

        if cell == self.end:
            return ui.ORANGE

        return ui.WHITE

    def draw(self, screen, fonts, mouse):
        ui.clear_screen(screen)
        ui.draw_header(screen, "Dynamic Programming", fonts)

        self.draw_controls(screen, fonts, mouse)
        self.draw_grid(screen, fonts)

        ui.draw_status(screen, self.status, fonts["small"])

# Main loop
def run_dynamic(screen, clock):
    fonts = ui.create_fonts()
    vis = DynamicProgrammingVisualiser()
    vis.create_buttons()

    actions = {
        "run": vis.run_dp,
        "clear": vis.clear
    }

    running = True

    while running:
        mouse = pygame.mouse.get_pos()

        vis.update_animation()
        vis.draw(screen, fonts, mouse)

        back = ui.draw_back_button(screen, fonts["small"], mouse)
        test = ui.draw_test_button(screen, fonts["small"], mouse)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back.collidepoint(event.pos):
                    running = False
                    continue

                if test.collidepoint(event.pos):
                    vis.start_test()
                    continue

                clicked_button = False

                for key, rect in vis.buttons.items():
                    if rect.collidepoint(event.pos):
                        actions[key]()
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
    run_dynamic(screen, clock)
