# Imports
import pygame
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import ui

# Visualiser setup
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

        self.controls_panel = pygame.Rect(24, ui.HEADER_H + 16, ui.WIDTH - 48, 150)
        self.input_rect = pygame.Rect(ui.WIDTH // 2 - 170, self.controls_panel.y + 50, 340, 46)
        self.buttons = {}

        self.test_mode = False
        self.test_queue = []
        self.test_values = []
        self.test_last_action = 0
        self.test_delay = 900

    def create_buttons(self):
        labels = ["Insert", "Extract", "Clear", "Recenter"]
        button_width = 140
        spacing = 14
        total_width = button_width * len(labels) + spacing * (len(labels) - 1)
        start_x = ui.WIDTH // 2 - total_width // 2
        y = self.controls_panel.bottom - 50

        self.buttons = {
            label: pygame.Rect(start_x + i * (button_width + spacing), y, button_width, 42)
            for i, label in enumerate(labels)
        }

    def world(self, x, y):
        return x + self.camera.x, y + self.camera.y

    # Camera movement
    def clamp_camera(self):
        self.camera.x = max(-self.cam_limit_x, min(self.cam_limit_x, self.camera.x))
        self.camera.y = max(-self.cam_limit_y, min(self.cam_limit_y, self.camera.y))

    def handle_drag(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.dragging = True
            self.last_mouse = pygame.Vector2(event.pos)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            pos = pygame.Vector2(event.pos)
            self.camera += pos - self.last_mouse
            self.last_mouse = pos
            self.clamp_camera()

    def reset_view(self):
        self.camera = pygame.Vector2(0, 0)

    # Animation state
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
        if self.animating:
            if self.step_index < len(self.steps):
                self.heap, self.highlight_a, self.highlight_b, self.status = self.steps[self.step_index]
                self.step_index += 1
            else:
                self.animating = False
                self.highlight_a = None
                self.highlight_b = None
                self.status = f"Heap size {len(self.heap)}"

        self.run_test_flow()

    # Heap actions
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

            if temp[child] >= temp[parent]:
                break

            temp[child], temp[parent] = temp[parent], temp[child]
            self.add_step(temp, child, parent, "Swap")
            child = parent

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
            smallest = self.get_smallest_child(temp, parent)

            if smallest == parent:
                break

            temp[parent], temp[smallest] = temp[smallest], temp[parent]
            self.add_step(temp, parent, smallest, "Swap down")
            parent = smallest

        self.add_step(temp, None, None, f"Extract complete {min_val}")
        self.start_animation()

    def get_smallest_child(self, heap, parent):
        left = 2 * parent + 1
        right = 2 * parent + 2
        smallest = parent

        if left < len(heap) and heap[left] < heap[smallest]:
            smallest = left

        if right < len(heap) and heap[right] < heap[smallest]:
            smallest = right

        return smallest

    def clear_heap(self):
        self.heap.clear()
        self.clear_state()

    # Test mode
    def run_tests(self):
        if self.animating:
            return

        self.heap = []
        self.clear_state()

        self.test_mode = True
        self.test_values = [5, 2, 9, 1, 7]
        self.test_queue = [
            "INSERT", "INSERT", "INSERT", "INSERT", "INSERT",
            "EXTRACT", "EXTRACT",
            "END"
        ]
        self.test_last_action = pygame.time.get_ticks()
        self.status = "TEST RUNNING"

    def run_test_flow(self):
        if not self.test_mode or self.animating:
            return

        now = pygame.time.get_ticks()

        if now - self.test_last_action < self.test_delay:
            return

        if not self.test_queue:
            self.end_test()
            return

        action = self.test_queue.pop(0)

        if action == "INSERT" and self.test_values:
            self.input_text = str(self.test_values.pop(0))
            self.insert_value()

        elif action == "EXTRACT":
            self.extract_min()

        elif action == "END":
            self.end_test()

        self.test_last_action = now

    def end_test(self):
        self.test_mode = False
        self.status = "TEST COMPLETE"

    # Drawing interface
    def get_node_pos(self, index):
        level = 0
        count = index + 1

        while count > 1:
            count //= 2
            level += 1

        first = 2 ** level - 1
        position = index - first
        nodes = 2 ** level
        gap = ui.WIDTH // (nodes + 1)

        x = gap * (position + 1)
        y = self.controls_panel.bottom + 120 + level * 90

        return x, y

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

    def draw_controls(self, screen, fonts, mouse):
        ui.draw_panel(screen, self.controls_panel)
        self.draw_input(screen, fonts, mouse)

        button_styles = {
            "Insert": "start",
            "Extract": "danger",
            "Recenter": "ghost"
        }

        for label, rect in self.buttons.items():
            ui.draw_button(
                screen,
                rect,
                label,
                fonts["small"],
                mouse,
                style=button_styles.get(label, "neutral")
            )

    # Drawing heap
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

        self.draw_heap_edges(screen)
        self.draw_heap_nodes(screen, fonts)

    def draw_heap_edges(self, screen):
        for index in range(len(self.heap)):
            x, y = self.world(*self.get_node_pos(index))

            for child in (2 * index + 1, 2 * index + 2):
                if child < len(self.heap):
                    child_x, child_y = self.world(*self.get_node_pos(child))
                    pygame.draw.line(screen, ui.BORDER_DEFAULT, (x, y), (child_x, child_y), 2)

    def draw_heap_nodes(self, screen, fonts):
        for index, value in enumerate(self.heap):
            x, y = self.world(*self.get_node_pos(index))
            highlight = index in (self.highlight_a, self.highlight_b)

            ui.draw_node_rect(
                screen,
                x - ui.NODE_WIDTH // 2,
                y - ui.NODE_HEIGHT // 2,
                str(value),
                fonts["normal"],
                highlight=highlight
            )

    def draw(self, screen, fonts, mouse):
        ui.clear_screen(screen)
        self.draw_heap(screen, fonts)

        ui.draw_header(screen, "Heap Visualiser", fonts)
        self.draw_controls(screen, fonts, mouse)

        back = ui.draw_back_button(screen, fonts["small"], mouse)
        test = ui.draw_test_button(screen, fonts["small"], mouse)

        ui.draw_status(screen, self.status, fonts["small"])

        return back, test

# Main loop
def run_heap(screen, clock):
    fonts = ui.create_fonts()
    vis = HeapVisualiser()
    vis.create_buttons()

    actions = {
        "Insert": vis.insert_value,
        "Extract": vis.extract_min,
        "Clear": vis.clear_heap,
        "Recenter": vis.reset_view,
    }

    running = True

    while running:
        mouse = pygame.mouse.get_pos()

        vis.update_animation()
        back, test = vis.draw(screen, fonts, mouse)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            vis.handle_drag(event)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back.collidepoint(event.pos):
                    running = False
                    continue

                if test.collidepoint(event.pos):
                    vis.run_tests()
                    continue

                for label, action in actions.items():
                    if vis.buttons[label].collidepoint(event.pos):
                        action()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    vis.input_text = vis.input_text[:-1]

                elif event.key == pygame.K_RETURN:
                    vis.insert_value()

                elif event.unicode.isdigit():
                    vis.input_text += event.unicode

        pygame.display.flip()
        clock.tick(ui.FPS)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((ui.WIDTH, ui.HEIGHT))
    clock = pygame.time.Clock()
    run_heap(screen, clock)
