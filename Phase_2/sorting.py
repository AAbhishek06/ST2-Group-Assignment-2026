# Imports
import pygame
import sys
import os
import random
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import ui

# Visualiser setup
class SortingVisualiser:
    def __init__(self):
        self.original_numbers = []
        self.numbers = []
        self.algorithm = "Bubble Sort"

        self.steps = []
        self.step_index = 0
        self.sorting = False
        self.highlight_a = None
        self.highlight_b = None

        self.status = "Enter amount 2 to 50 then generate"
        self.input_text = ""
        self.start_time = 0

        self.controls_panel = pygame.Rect(24, ui.HEADER_H + 16, ui.WIDTH - 48, 150)
        self.input_rect = pygame.Rect(ui.WIDTH // 2 - 170, self.controls_panel.y + 52, 340, 46)
        self.buttons = {}

        self.test_mode = False
        self.test_queue = []
        self.test_last_action = 0
        self.test_delay = 900

    def create_buttons(self):
        labels = ["Bubble", "Selection", "Merge", "Start", "Reset", "Generate"]
        button_width = 120
        spacing = 12
        total_width = len(labels) * button_width + (len(labels) - 1) * spacing
        start_x = ui.WIDTH // 2 - total_width // 2
        y = self.controls_panel.bottom - 50

        self.buttons = {
            label.lower(): pygame.Rect(start_x + i * (button_width + spacing), y, button_width, 42)
            for i, label in enumerate(labels)
        }

    def clear_state(self):
        self.steps = []
        self.step_index = 0
        self.sorting = False
        self.highlight_a = None
        self.highlight_b = None

    def set_numbers(self, count):
        self.original_numbers = random.sample(range(50, 501), count)
        self.numbers = self.original_numbers.copy()
        self.clear_state()

    # User actions
    def reset(self):
        self.numbers = self.original_numbers.copy()
        self.clear_state()
        self.status = "Reset complete"

    def auto_generate(self):
        self.set_numbers(10)

    def randomise(self):
        if not self.input_text.isdigit():
            self.status = "Enter number 2 to 50"
            return

        count = int(self.input_text)

        if count < 2 or count > 50:
            self.status = "Range 2 to 50 only"
            return

        self.set_numbers(count)
        self.input_text = ""
        self.status = f"{count} values created"

    def choose_algorithm(self, algorithm):
        self.algorithm = algorithm
        self.reset()
        self.status = f"{algorithm} selected"

    def start_sort(self):
        if not self.numbers:
            self.status = "Generate values first"
            return

        self.clear_state()

        methods = {
            "Bubble Sort": self.build_bubble_steps,
            "Selection Sort": self.build_selection_steps,
            "Merge Sort": self.build_merge_steps,
        }

        self.start_time = time.time()
        methods[self.algorithm]()

        self.sorting = True
        self.status = f"Sorting {self.algorithm}"

    # Sorting algorithms
    def build_bubble_steps(self):
        arr = self.numbers.copy()

        for i in range(len(arr)):
            for j in range(len(arr) - i - 1):
                self.steps.append((arr.copy(), j, j + 1))

                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    self.steps.append((arr.copy(), j, j + 1))

        self.steps.append((arr.copy(), None, None))

    def build_selection_steps(self):
        arr = self.numbers.copy()

        for i in range(len(arr)):
            min_index = i

            for j in range(i + 1, len(arr)):
                self.steps.append((arr.copy(), min_index, j))

                if arr[j] < arr[min_index]:
                    min_index = j

            arr[i], arr[min_index] = arr[min_index], arr[i]
            self.steps.append((arr.copy(), i, min_index))

        self.steps.append((arr.copy(), None, None))

    def build_merge_steps(self):
        arr = self.numbers.copy()

        def merge(left, right):
            if right - left <= 1:
                return

            mid = (left + right) // 2
            merge(left, mid)
            merge(mid, right)

            temp = []
            i = left
            j = mid

            while i < mid and j < right:
                self.steps.append((arr.copy(), i, j))

                if arr[i] <= arr[j]:
                    temp.append(arr[i])
                    i += 1
                else:
                    temp.append(arr[j])
                    j += 1

            temp.extend(arr[i:mid])
            temp.extend(arr[j:right])

            for k, value in enumerate(temp):
                arr[left + k] = value
                self.steps.append((arr.copy(), left + k, None))

        merge(0, len(arr))
        self.steps.append((arr.copy(), None, None))

    # Animation and testing
    def update_animation(self):
        if not self.sorting:
            self.run_test_flow()
            return

        if self.step_index < len(self.steps):
            self.numbers, self.highlight_a, self.highlight_b = self.steps[self.step_index]
            self.step_index += 1
            return

        self.sorting = False
        self.highlight_a = None
        self.highlight_b = None

        duration = time.time() - self.start_time
        self.status = f"{self.algorithm} completed in {duration:.2f}s"

    def run_tests(self):
        if self.sorting:
            return

        self.test_mode = True
        self.test_queue = [
            "Bubble Sort",
            "Selection Sort",
            "Merge Sort"
        ]
        self.test_last_action = pygame.time.get_ticks()
        self.status = "TEST RUNNING"

    def run_test_flow(self):
        if not self.test_mode or self.sorting:
            return

        now = pygame.time.get_ticks()

        if now - self.test_last_action < self.test_delay:
            return

        if not self.test_queue:
            self.test_mode = False
            self.status = "TEST COMPLETE"
            return

        self.algorithm = self.test_queue.pop(0)
        self.auto_generate()
        self.start_sort()

        self.test_last_action = now

    # Drawing interface
    def draw_input(self, screen, fonts, mouse):
        ui.draw_label(screen, "VALUE", self.input_rect.x, self.input_rect.y - 22, fonts["heading"])

        ui.draw_input_box(
            screen,
            self.input_rect,
            self.input_text,
            fonts["normal"],
            active=True,
            mouse_pos=mouse
        )

    def draw_buttons(self, screen, fonts, mouse):
        button_styles = {
            "bubble": "ghost",
            "selection": "ghost",
            "merge": "ghost",
            "start": "start",
            "reset": "danger",
        }

        for key, rect in self.buttons.items():
            ui.draw_button(
                screen,
                rect,
                key.capitalize(),
                fonts["normal"],
                mouse,
                style=button_styles.get(key, "neutral")
            )

    def draw_bars(self, screen, fonts):
        if not self.numbers:
            ui.draw_text(
                screen,
                "Generate values",
                ui.WIDTH // 2,
                350,
                fonts["normal"],
                ui.BLACK,
                centre=True
            )
            return

        count = len(self.numbers)
        start_x = 40
        end_x = ui.WIDTH - 40
        gap = 4
        bar_width = (end_x - start_x - (count - 1) * gap) // count
        base_y = 660

        for i, value in enumerate(self.numbers):
            x = start_x + i * (bar_width + gap)
            height = int(value * 0.5)
            y = base_y - height

            colour = ui.YELLOW if i in (self.highlight_a, self.highlight_b) else ui.LIGHT_BLUE
            bar = pygame.Rect(x, y, bar_width, height)

            pygame.draw.rect(screen, colour, bar)
            pygame.draw.rect(screen, ui.BLACK, bar, 1)

            ui.draw_text(
                screen,
                str(value),
                bar.centerx,
                y - 18,
                fonts["normal"],
                ui.BLACK,
                centre=True
            )

    def draw_ui(self, screen, fonts, mouse):
        ui.draw_panel(screen, self.controls_panel)
        self.draw_input(screen, fonts, mouse)
        self.draw_buttons(screen, fonts, mouse)
        self.draw_bars(screen, fonts)

    def draw(self, screen, fonts, mouse):
        ui.clear_screen(screen)
        ui.draw_header(screen, "Sorting Algorithms", fonts)
        self.draw_ui(screen, fonts, mouse)
        ui.draw_status(screen, self.status, fonts["normal"])

# Main loop
def run_sorting(screen, clock):
    fonts = ui.create_fonts()
    vis = SortingVisualiser()
    vis.create_buttons()

    actions = {
        "bubble": lambda: vis.choose_algorithm("Bubble Sort"),
        "selection": lambda: vis.choose_algorithm("Selection Sort"),
        "merge": lambda: vis.choose_algorithm("Merge Sort"),
        "start": vis.start_sort,
        "reset": vis.reset,
        "generate": vis.randomise,
    }

    running = True

    while running:
        mouse = pygame.mouse.get_pos()

        vis.update_animation()
        vis.draw(screen, fonts, mouse)

        back = ui.draw_back_button(screen, fonts["normal"], mouse)
        test = ui.draw_test_button(screen, fonts["normal"], mouse)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_BACKSPACE:
                    vis.input_text = vis.input_text[:-1]

                elif event.unicode.isdigit():
                    vis.input_text += event.unicode

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back.collidepoint(event.pos):
                    running = False
                    continue

                if test.collidepoint(event.pos):
                    vis.run_tests()
                    continue

                for key, action in actions.items():
                    if vis.buttons[key].collidepoint(event.pos):
                        action()
                        break

        pygame.display.flip()
        clock.tick(8)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((ui.WIDTH, ui.HEIGHT))
    clock = pygame.time.Clock()
    run_sorting(screen, clock)
