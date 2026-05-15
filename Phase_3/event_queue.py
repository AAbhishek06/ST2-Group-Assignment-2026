# Imports
import pygame
import sys
import os
import heapq
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import ui

# Event structure
class Event:
    def __init__(self, name, priority, timestamp):
        self.name = name
        self.priority = priority
        self.timestamp = timestamp

    def __lt__(self, other):
        return (self.priority, self.timestamp) < (other.priority, other.timestamp)

# Visualiser setup
class EventQueueVisualiser:
    def __init__(self):
        self.heap = []
        self.processed_events = []

        self.input_name = ""
        self.input_priority = ""
        self.active_input = None
        self.status = "Ready"

        self.animating = False
        self.last_step_time = 0
        self.step_delay = 700

        self.current_event = None
        self.highlight_index = None
        self.start_time = None
        self.end_time = None

        self.testing = False
        self.test_stage = None
        self.test_items = []
        self.test_index = 0
        self.test_timer = 0

        self.controls_panel = pygame.Rect(24, ui.HEADER_H + 16, ui.WIDTH - 48, 150)
        self.name_box = pygame.Rect(ui.WIDTH // 2 - 190, self.controls_panel.y + 42, 180, 40)
        self.prio_box = pygame.Rect(ui.WIDTH // 2 + 10, self.controls_panel.y + 42, 180, 40)
        self.processed_panel = pygame.Rect(ui.WIDTH - 310, 250, 270, 360)

        self.buttons = {}

    def create_buttons(self):
        labels = ["Add", "Process", "Step", "Reset"]
        button_width = 130
        spacing = 12
        total_width = len(labels) * button_width + (len(labels) - 1) * spacing
        start_x = ui.WIDTH // 2 - total_width // 2
        y = self.controls_panel.bottom - 50

        self.buttons = {
            label: pygame.Rect(start_x + i * (button_width + spacing), y, button_width, 42)
            for i, label in enumerate(labels)
        }

        self.buttons["Test"] = pygame.Rect(ui.WIDTH - 160, ui.HEADER_H + 18, 120, 38)

    def reset(self):
        self.heap = []
        self.processed_events = []
        self.input_name = ""
        self.input_priority = ""
        self.active_input = None

        self.animating = False
        self.last_step_time = 0
        self.current_event = None
        self.highlight_index = None
        self.start_time = None
        self.end_time = None

        self.testing = False
        self.test_stage = None
        self.test_items = []
        self.test_index = 0
        self.test_timer = 0

        self.status = "Queue cleared"

    def get_active_text(self):
        return self.input_name if self.active_input == "name" else self.input_priority

    def set_active_text(self, text):
        if self.active_input == "name":
            self.input_name = text
        elif self.active_input == "priority":
            self.input_priority = text

    # User actions
    def add_event(self):
        if self.animating or self.testing:
            self.status = "Busy"
            return

        if not self.input_name.strip() or not self.input_priority.isdigit():
            self.status = "Enter valid name and priority"
            return

        event = Event(self.input_name.strip(), int(self.input_priority), time.time())
        heapq.heappush(self.heap, event)

        self.input_name = ""
        self.input_priority = ""
        self.active_input = None

        self.current_event = event
        self.highlight_index = self.heap.index(event)
        self.status = "Event added"

    def start_processing(self):
        if self.animating or self.testing:
            return

        if not self.heap:
            self.status = "Queue empty"
            return

        self.processed_events = []
        self.start_time = time.time()
        self.animating = True
        self.last_step_time = pygame.time.get_ticks()
        self.status = "Processing started"

    def process_one(self):
        if not self.heap:
            self.finish_processing()
            return

        event = heapq.heappop(self.heap)
        self.processed_events.append(event)

        self.current_event = event
        self.highlight_index = 0 if self.heap else None

        if self.heap:
            self.status = "Processed event"
        else:
            self.finish_processing()

    def finish_processing(self):
        self.animating = False
        self.highlight_index = None

        if self.start_time:
            self.end_time = time.time()
            self.status = f"Done in {self.end_time - self.start_time:.2f}s"
        else:
            self.status = "Queue empty"

    def manual_step(self):
        if self.animating or self.testing:
            self.status = "Busy"
            return

        if not self.heap:
            self.status = "Queue empty"
            return

        if not self.start_time:
            self.start_time = time.time()

        self.process_one()

    # Test mode
    def start_test(self):
        if self.animating:
            return

        self.reset()

        self.testing = True
        self.test_stage = "add"
        self.test_index = 0
        self.test_timer = pygame.time.get_ticks()
        self.test_items = list(zip(["A", "B", "C", "D", "E"], [5, 1, 3, 2, 4]))

        self.status = "Test started"

    def update_test(self):
        if not self.testing:
            return

        now = pygame.time.get_ticks()

        if now - self.test_timer < 500:
            return

        self.test_timer = now

        if self.test_stage == "add":
            self.add_test_event()
        elif self.test_stage == "process":
            self.process_test_event()

    def add_test_event(self):
        if self.test_index < len(self.test_items):
            name, priority = self.test_items[self.test_index]
            heapq.heappush(self.heap, Event(name, priority, time.time()))
            self.test_index += 1
            self.status = f"Added {name}"
            return

        self.test_stage = "process"
        self.test_index = 0

    def process_test_event(self):
        if self.heap:
            event = heapq.heappop(self.heap)
            self.processed_events.append(event)
            self.status = f"Processed {event.name}"
            return

        self.testing = False
        self.status = "Test complete"

    def update_animation(self):
        if self.testing:
            self.update_test()
            return

        if not self.animating:
            return

        now = pygame.time.get_ticks()

        if now - self.last_step_time >= self.step_delay:
            self.process_one()
            self.last_step_time = now

    # Drawing interface
    def draw_inputs(self, screen, fonts, mouse):
        inputs = [
            ("NAME", self.name_box, self.input_name, "name"),
            ("PRIORITY", self.prio_box, self.input_priority, "priority")
        ]

        for label, rect, text, input_name in inputs:
            ui.draw_label(screen, label, rect.x, rect.y - 22, fonts["heading"])

            ui.draw_input_box(
                screen,
                rect,
                text,
                fonts["normal"],
                active=(self.active_input == input_name),
                mouse_pos=mouse
            )

    def draw_controls(self, screen, fonts, mouse):
        ui.draw_panel(screen, self.controls_panel)
        self.draw_inputs(screen, fonts, mouse)

        styles = {
            "Add": "start",
            "Process": "start",
            "Step": "ghost",
            "Reset": "danger",
            "Test": "accent"
        }

        for label, rect in self.buttons.items():
            ui.draw_button(
                screen,
                rect,
                label,
                fonts["small"],
                mouse,
                style=styles.get(label, "neutral")
            )

    # Drawing heap
    def get_pos(self, index):
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
        y = 280 + level * 85

        return x, y

    def draw_heap(self, screen, fonts):
        if not self.heap:
            ui.draw_text(
                screen,
                "No events queued",
                ui.WIDTH // 2,
                360,
                fonts["normal"],
                ui.TEXT_1,
                centre=True
            )
            return

        self.draw_heap_edges(screen)
        self.draw_heap_nodes(screen, fonts)

    def draw_heap_edges(self, screen):
        for index in range(len(self.heap)):
            x1, y1 = self.get_pos(index)

            for child in (2 * index + 1, 2 * index + 2):
                if child < len(self.heap):
                    x2, y2 = self.get_pos(child)
                    pygame.draw.line(screen, ui.BLACK, (x1, y1), (x2, y2), 2)

    def draw_heap_nodes(self, screen, fonts):
        for index, event in enumerate(self.heap):
            x, y = self.get_pos(index)
            colour = ui.YELLOW if index == self.highlight_index else ui.LIGHT_BLUE

            pygame.draw.circle(screen, colour, (x, y), 30)
            pygame.draw.circle(screen, ui.BLACK, (x, y), 30, 2)

            ui.draw_text(screen, event.name[:6], x, y - 10, fonts["small"], ui.BLACK, centre=True)
            ui.draw_text(screen, f"P:{event.priority}", x, y + 10, fonts["small"], ui.DARK_GREY, centre=True)

    # Drawing processed order
    def draw_processed(self, screen, fonts):
        ui.draw_panel(screen, self.processed_panel)

        ui.draw_text(
            screen,
            "PROCESSED ORDER",
            self.processed_panel.centerx,
            self.processed_panel.y + 25,
            fonts["heading"],
            ui.TEXT_3,
            centre=True
        )

        if not self.processed_events:
            ui.draw_text(
                screen,
                "None",
                self.processed_panel.centerx,
                self.processed_panel.y + 70,
                fonts["small"],
                ui.TEXT_3,
                centre=True
            )
            return

        y = self.processed_panel.top + 62
        spacing = 50

        for event in self.processed_events[-6:]:
            ui.draw_node_rect(
                screen,
                self.processed_panel.x + 91,
                y,
                f"{event.name[:10]} P:{event.priority}",
                fonts["small"],
                highlight=False
            )

            y += spacing

    def draw(self, screen, fonts, mouse):
        ui.clear_screen(screen)
        ui.draw_header(screen, "Event Queue", fonts)

        self.draw_controls(screen, fonts, mouse)
        self.draw_heap(screen, fonts)
        self.draw_processed(screen, fonts)

        ui.draw_status(screen, self.status, fonts["small"])

# Main loop
def run_event_queue(screen, clock):
    fonts = ui.create_fonts()
    vis = EventQueueVisualiser()
    vis.create_buttons()

    actions = {
        "Add": vis.add_event,
        "Process": vis.start_processing,
        "Step": vis.manual_step,
        "Reset": vis.reset,
        "Test": vis.start_test
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

                elif event.key == pygame.K_BACKSPACE:
                    vis.set_active_text(vis.get_active_text()[:-1])

                elif event.unicode.isprintable():
                    vis.set_active_text(vis.get_active_text() + event.unicode)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back.collidepoint(event.pos):
                    running = False
                    continue

                if vis.name_box.collidepoint(event.pos):
                    vis.active_input = "name"
                elif vis.prio_box.collidepoint(event.pos):
                    vis.active_input = "priority"
                else:
                    vis.active_input = None

                for label, rect in vis.buttons.items():
                    if rect.collidepoint(event.pos):
                        actions[label]()

        pygame.display.flip()
        clock.tick(ui.FPS)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((ui.WIDTH, ui.HEIGHT))
    clock = pygame.time.Clock()
    run_event_queue(screen, clock)
