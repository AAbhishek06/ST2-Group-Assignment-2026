import pygame
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import ui


class DynamicProgrammingVisualiser:

    def __init__(self):

        self.rows = 25
        self.cols = 25
        self.cell_size = 18

        self.grid_width = self.cols * self.cell_size

        self.offset_x = (ui.WIDTH - self.grid_width) // 2
        self.offset_y = 230

        self.grid = [
            ["empty" for _ in range(self.cols)]
            for _ in range(self.rows)
        ]

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

        self.status = "Click a cell to set start, end, and wall points"

        self.start_time = 0
        self.dp = None

        self.controls_panel = pygame.Rect(
            24,
            ui.HEADER_H + 16,
            ui.WIDTH - 48,
            150
        )

        self.buttons = {}

    def create_buttons(self):

        labels = ["Run", "Clear"]

        button_width = 140
        spacing = 18

        total_width = len(labels) * button_width + (len(labels) - 1) * spacing

        start_x = ui.WIDTH // 2 - total_width // 2
        y = self.controls_panel.bottom - 50

        self.buttons = {}

        for i, label in enumerate(labels):

            x = start_x + i * (button_width + spacing)

            self.buttons[label.lower()] = pygame.Rect(
                x,
                y,
                button_width,
                42
            )

    def clear(self):

        self.grid = [
            ["empty" for _ in range(self.cols)]
            for _ in range(self.rows)
        ]

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

        self.dp = None

        self.status = "Grid cleared"

    def handle_click(self, pos):

        if self.animating:
            return

        x, y = pos

        if y < self.offset_y:
            return

        col = (x - self.offset_x) // self.cell_size
        row = (y - self.offset_y) // self.cell_size

        if row < 0 or row >= self.rows:
            return

        if col < 0 or col >= self.cols:
            return

        cell = (row, col)

        if not self.start:

            self.start = cell
            self.grid[row][col] = "start"
            self.status = "Start point set, add an End point"
            return

        if not self.end and cell != self.start:

            self.end = cell
            self.grid[row][col] = "end"
            self.status = "End point set, add walls or press Run"
            return

        if cell != self.start and cell != self.end:

            self.grid[row][col] = "wall" if self.grid[row][col] == "empty" else "empty"

    def run_dp(self):

        if self.animating:
            return

        if not self.start or not self.end:
            self.status = "Set start and end first"
            return

        self.start_time = time.time()

        sr, sc = self.start
        er, ec = self.end

        row_step = 1 if er >= sr else -1
        col_step = 1 if ec >= sc else -1

        dp = [
            [0 for _ in range(self.cols)]
            for _ in range(self.rows)
        ]

        dp[sr][sc] = 1

        for r in range(sr, er + row_step, row_step):
            for c in range(sc, ec + col_step, col_step):

                if self.grid[r][c] == "wall":
                    dp[r][c] = 0
                    continue

                if (r, c) == self.start:
                    continue

                previous_row = r - row_step
                previous_col = c - col_step

                from_row = 0
                from_col = 0

                if 0 <= previous_row < self.rows:
                    from_row = dp[previous_row][c]

                if 0 <= previous_col < self.cols:
                    from_col = dp[r][previous_col]

                dp[r][c] = from_row + from_col

        self.dp = dp
        self.final_path = self.reconstruct_path(row_step, col_step)

        elapsed = time.time() - self.start_time

        self.path = []
        self.visited = set()

        if not self.final_path:
            self.animating = False
            self.animation_stage = None
            self.status = "No DP path found"
            return

        self.animating = True
        self.animation_stage = "path"
        self.step_index = 0
        self.last_step_time = pygame.time.get_ticks()

        er, ec = self.end
        path_count = self.dp[er][ec]

        self.status = f"DP complete: {path_count} path(s), {elapsed:.2f}s"

    def reconstruct_path(self, row_step, col_step):

        if not self.start or not self.end:
            return []

        if not hasattr(self, "dp"):
            return []

        sr, sc = self.start
        er, ec = self.end

        if self.dp[er][ec] == 0:
            return []

        path = []
        r, c = self.end

        while (r, c) != self.start:

            path.append((r, c))

            up_r = r - row_step
            left_c = c - col_step

            can_up = 0 <= up_r < self.rows and self.dp[up_r][c] > 0
            can_left = 0 <= left_c < self.cols and self.dp[r][left_c] > 0

            if can_up and can_left:
                if self.dp[up_r][c] >= self.dp[r][left_c]:
                    r = up_r
                else:
                    c = left_c
            elif can_up:
                r = up_r
            elif can_left:
                c = left_c
            else:
                return []

        path.append(self.start)
        path.reverse()

        return path

    def update_animation(self):

        if not self.animating:
            return

        now = pygame.time.get_ticks()

        if now - self.last_step_time < self.step_delay:
            return

        self.last_step_time = now

        if self.animation_stage == "path":

            if self.step_index < len(self.final_path):

                cell = self.final_path[self.step_index]

                if cell != self.start and cell != self.end:
                    self.path.append(cell)

                self.step_index += 1

            else:

                self.animating = False
                self.animation_stage = None

                self.status = f"Path found: {len(self.final_path)} steps"

    def draw_controls(self, screen, fonts, mouse):

        ui.draw_panel(screen, self.controls_panel)

        ui.draw_text(
            screen,
            "Visualise a grid based pathfinding system with dynamic programming.",
            self.controls_panel.centerx,
            self.controls_panel.y + 28,
            fonts["heading"],
            ui.TEXT_1,
            centre=True
        )

        for key, rect in self.buttons.items():

            style = "neutral"

            if key == "run":
                style = "start"
            elif key == "clear":
                style = "danger"

            ui.draw_button(
                screen,
                rect,
                key.capitalize(),
                fonts["small"],
                mouse,
                style=style
            )

    def draw_grid(self, screen, fonts):

        for r in range(self.rows):
            for c in range(self.cols):

                x = self.offset_x + c * self.cell_size
                y = self.offset_y + r * self.cell_size

                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)

                colour = ui.WHITE

                if self.grid[r][c] == "wall":
                    colour = ui.BLACK
                elif (r, c) in self.path:
                    colour = ui.YELLOW
                elif (r, c) == self.start:
                    colour = ui.GREEN
                elif (r, c) == self.end:
                    colour = ui.ORANGE

                pygame.draw.rect(screen, colour, rect)
                pygame.draw.rect(screen, ui.BLACK, rect, 1)

                if self.dp is not None:
                    val = self.dp[r][c]
                    if val > 0:
                        ui.draw_text(
                            screen,
                            str(val),
                            x + self.cell_size // 2,
                            y + self.cell_size // 2,
                            fonts["small"],
                            ui.BLACK,
                            centre=True
                        )

    def draw(self, screen, fonts, mouse):

        ui.clear_screen(screen)

        ui.draw_header(screen, "Dynamic Programming", fonts)

        self.draw_controls(screen, fonts, mouse)
        self.draw_grid(screen, fonts)

        ui.draw_status(
            screen,
            self.status,
            fonts["small"]
        )


def run_dynamic(screen, clock):

    fonts = ui.create_fonts()

    vis = DynamicProgrammingVisualiser()
    vis.create_buttons()

    actions = {
        "run": vis.run_dp,
        "clear": vis.clear,
    }

    running = True

    while running:

        mouse = pygame.mouse.get_pos()

        vis.update_animation()
        vis.draw(screen, fonts, mouse)

        back = ui.draw_back_button(screen, fonts["small"], mouse)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            if event.type == pygame.MOUSEBUTTONDOWN:

                if back.collidepoint(event.pos):
                    running = False

                else:
                    for key, rect in vis.buttons.items():
                        if rect.collidepoint(event.pos):
                            actions[key]()
                            break

                    vis.handle_click(event.pos)

        pygame.display.flip()
        clock.tick(ui.FPS)


if __name__ == "__main__":

    pygame.init()
    screen = pygame.display.set_mode((ui.WIDTH, ui.HEIGHT))
    clock = pygame.time.Clock()

    run_dynamic(screen, clock)
