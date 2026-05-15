import pygame
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import ui


class HeapVisualiser:
    def __init__(self):
        self.heap = []
        self.input_text = ""

        self.status = "Enter value then insert"

        self.steps = []
        self.step_index = 0
        self.animating = False

        self.highlight_a = None
        self.highlight_b = None

        self.camera = pygame.Vector2(0, 0)
        self.dragging = False
        self.last_mouse = pygame.Vector2(0, 0)

        self.cam_limit_x = 800
        self.cam_limit_y = 600

        self.controls_panel = pygame.Rect(
            24,
            ui.HEADER_H + 16,
            ui.WIDTH - 48,
            150
        )

        self.input_rect = pygame.Rect(
            ui.WIDTH // 2 - 170,
            self.controls_panel.y + 50,
            340,
            46
        )

        self.buttons = {}

    def create_buttons(self):
        labels = ["Insert", "Extract", "Clear", "Recenter"]

        button_width = 140
        spacing = 14

        total_width = (button_width * len(labels)) + (spacing * (len(labels) - 1))
        start_x = ui.WIDTH // 2 - total_width // 2
        y = self.controls_panel.bottom - 50

        for i, label in enumerate(labels):
            x = start_x + i * (button_width + spacing)
            self.buttons[label] = pygame.Rect(x, y, button_width, 42)

    def clamp_camera(self):
        self.camera.x = max(-self.cam_limit_x, min(self.cam_limit_x, self.camera.x))
        self.camera.y = max(-self.cam_limit_y, min(self.cam_limit_y, self.camera.y))

    def world(self, x, y):
        return x + self.camera.x, y + self.camera.y

    def handle_drag(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.dragging = True
            self.last_mouse = pygame.Vector2(event.pos)

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False

        if event.type == pygame.MOUSEMOTION and self.dragging:
            pos = pygame.Vector2(event.pos)
            delta = pos - self.last_mouse
            self.camera += delta
            self.last_mouse = pos
            self.clamp_camera()

    def reset_view(self):
        self.camera = pygame.Vector2(0, 0)

    def clear_state(self):
        self.steps = []
        self.step_index = 0
        self.animating = False
        self.highlight_a = None
        self.highlight_b = None

    def add_step(self, heap_state, a=None, b=None, msg=""):
        self.steps.append((heap_state.copy(), a, b, msg))

    def start_animation(self):
        self.step_index = 0
        self.animating = True

    def update_animation(self):
        if not self.animating:
            return

        if self.step_index < len(self.steps):
            self.heap, self.highlight_a, self.highlight_b, self.status = self.steps[self.step_index]
            self.step_index += 1
        else:
            self.animating = False
            self.highlight_a = None
            self.highlight_b = None
            self.status = f"Heap size {len(self.heap)}"

    def insert_value(self):
        if self.animating:
            return

        if not self.input_text.isdigit():
            self.status = "Enter number"
            return

        value = int(self.input_text)

        temp = self.heap.copy()
        temp.append(value)

        self.steps = []

        child = len(temp) - 1
        self.add_step(temp, child, None, f"Insert {value}")

        while child > 0:
            parent = (child - 1) // 2
            self.add_step(temp, child, parent, "Compare")

            if temp[child] < temp[parent]:
                temp[child], temp[parent] = temp[parent], temp[child]
                self.add_step(temp, child, parent, "Swap")
                child = parent
            else:
                break

        self.add_step(temp, None, None, "Insert complete")
        self.input_text = ""
        self.start_animation()

    def extract_min(self):
        if self.animating:
            return

        if not self.heap:
            self.status = "Heap empty"
            return

        temp = self.heap.copy()
        self.steps = []

        min_val = temp[0]
        self.add_step(temp, 0, None, f"Remove {min_val}")

        if len(temp) == 1:
            temp.pop()
            self.add_step(temp, None, None, "Empty heap")
            self.start_animation()
            return

        temp[0] = temp.pop()
        parent = 0

        while True:
            left = 2 * parent + 1
            right = 2 * parent + 2
            smallest = parent

            if left < len(temp) and temp[left] < temp[smallest]:
                smallest = left

            if right < len(temp) and temp[right] < temp[smallest]:
                smallest = right

            if smallest != parent:
                temp[parent], temp[smallest] = temp[smallest], temp[parent]
                self.add_step(temp, parent, smallest, "Swap down")
                parent = smallest
            else:
                break

        self.add_step(temp, None, None, f"Extract complete {min_val}")
        self.start_animation()

    def get_node_pos(self, i):
        level = 0
        count = i + 1

        while count > 1:
            count //= 2
            level += 1

        first = (2 ** level) - 1
        pos = i - first

        nodes = 2 ** level
        gap = ui.WIDTH // (nodes + 1)

        x = gap * (pos + 1)
        y = self.controls_panel.bottom + 120 + level * 90

        return x, y

    def draw_back_button(self, screen, font, mouse):
        return ui.draw_back_button(screen, font, mouse)

    def draw_input(self, screen, fonts, mouse):
        ui.draw_label(
            screen,
            "VALUE",
            self.input_rect.x,
            self.input_rect.y - 22,
            fonts["heading"]
        )

        ui.draw_input_box(
            screen,
            self.input_rect,
            self.input_text,
            fonts["normal"],
            active=True,
            mouse_pos=mouse
        )

    def draw_controls(self, screen, fonts, mouse):
        ui.draw_panel(screen, self.controls_panel)

        self.draw_input(screen, fonts, mouse)

        for label, rect in self.buttons.items():
            style = "neutral"

            if label == "Insert":
                style = "start"
            if label == "Extract":
                style = "danger"
            if label == "Recenter":
                style = "ghost"

            ui.draw_button(screen, rect, label, fonts["small"], mouse, style=style)

    def draw_heap(self, screen, fonts):
        if not self.heap:
            ui.draw_text(
                screen,
                "Heap empty",
                ui.WIDTH // 2,
                ui.HEIGHT // 2 + 80,
                fonts["heading"],
                ui.TEXT_1,
                centre=True
            )
            return

        for i in range(len(self.heap)):
            x, y = self.get_node_pos(i)
            sx, sy = self.world(x, y)

            left = 2 * i + 1
            right = 2 * i + 2

            if left < len(self.heap):
                lx, ly = self.world(*self.get_node_pos(left))
                pygame.draw.line(screen, ui.BLACK, (sx, sy), (lx, ly), 2)

            if right < len(self.heap):
                rx, ry = self.world(*self.get_node_pos(right))
                pygame.draw.line(screen, ui.BLACK, (sx, sy), (rx, ry), 2)

        for i, val in enumerate(self.heap):
            x, y = self.get_node_pos(i)
            sx, sy = self.world(x, y)

            colour = ui.YELLOW if i in (self.highlight_a, self.highlight_b) else ui.LIGHT_BLUE

            pygame.draw.circle(screen, colour, (int(sx), int(sy)), 26)
            pygame.draw.circle(screen, ui.BLACK, (int(sx), int(sy)), 26, 2)

            ui.draw_text(
                screen,
                str(val),
                sx,
                sy,
                fonts["small"],
                ui.BLACK,
                centre=True
            )

    def draw(self, screen, fonts, mouse):
        ui.clear_screen(screen)

        ui.draw_header(screen, "Heap Visualiser", fonts)

        self.draw_controls(screen, fonts, mouse)
        self.draw_heap(screen, fonts)

        back = self.draw_back_button(screen, fonts["small"], mouse)

        ui.draw_status(screen, self.status, fonts["small"])

        return back


def run_heap(screen, clock):
    fonts = ui.create_fonts()
    vis = HeapVisualiser()
    vis.create_buttons()

    actions = {
        "Insert": vis.insert_value,
        "Extract": vis.extract_min,
        "Clear": lambda: (vis.heap.clear(), vis.clear_state()),
        "Recenter": vis.reset_view,
    }

    running = True

    while running:
        mouse = pygame.mouse.get_pos()

        vis.update_animation()
        back = vis.draw(screen, fonts, mouse)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            vis.handle_drag(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_BACKSPACE:
                    vis.input_text = vis.input_text[:-1]

                elif event.key == pygame.K_RETURN:
                    vis.insert_value()

                elif event.unicode.isdigit() and len(vis.input_text) < 5:
                    vis.input_text += event.unicode

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back.collidepoint(event.pos):
                    running = False
                else:
                    for k, action in actions.items():
                        if vis.buttons[k].collidepoint(event.pos):
                            action()

        pygame.display.flip()
        clock.tick(ui.FPS)


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((ui.WIDTH, ui.HEIGHT))
    clock = pygame.time.Clock()
    run_heap(screen, clock)