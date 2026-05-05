import pygame
import sys
import os
import heapq
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from configure import *
from utilities import *


class Event:
    def __init__(self, name, priority, timestamp):
        self.name = name
        self.priority = priority
        self.timestamp = timestamp

    def __lt__(self, other):
        return (self.priority, self.timestamp) < (other.priority, other.timestamp)


class EventQueueVisualiser:
    def __init__(self):
        self.heap = []

        self.input_name = ""
        self.input_priority = ""

        self.active_input = None

        self.name_box = pygame.Rect(WIDTH // 2 - 170, 90, 160, 40)
        self.prio_box = pygame.Rect(WIDTH // 2 + 10, 90, 160, 40)

        self.status_message = "Enter name and priority then press Add"

        self.steps = []
        self.step_index = 0
        self.animating = False

        self.highlight_index = None

        self.buttons = {}

        self.ui_block = pygame.Rect(0, 0, WIDTH, 225)

        self.start_time = None
        self.end_time = None

    def create_buttons(self):
        center = WIDTH // 2

        labels = ["Add", "Process", "Reset"]

        button_width = 120
        spacing = 20

        total_width = len(labels) * button_width + (len(labels) - 1) * spacing
        start_x = center - total_width // 2
        y = 170

        self.buttons = {}

        for i, label in enumerate(labels):
            x = start_x + i * (button_width + spacing)
            self.buttons[label.lower()] = pygame.Rect(x, y, button_width, 40)

    def clear_state(self):
        self.steps = []
        self.step_index = 0
        self.animating = False
        self.highlight_index = None

    def reset(self):
        self.heap = []
        self.clear_state()
        self.status_message = "Queue cleared"

    def add_event(self):
        if self.animating:
            return

        if not self.input_name or not self.input_priority.isdigit():
            self.status_message = "Enter valid name and priority"
            return

        event = Event(
            self.input_name,
            int(self.input_priority),
            time.time()
        )

        heapq.heappush(self.heap, event)

        self.input_name = ""
        self.input_priority = ""
        self.active_input = None

        self.status_message = f"Added {event.name}"

    def process_events(self):
        if self.animating:
            return

        if not self.heap:
            self.status_message = "Queue is empty"
            return

        self.clear_state()
        self.start_time = time.time()

        temp = self.heap.copy()

        while temp:
            event = heapq.heappop(temp)
            self.steps.append((event.name, event.priority))

        self.animating = True
        self.status_message = "Processing events"

    def update_animation(self):
        if not self.animating:
            return

        if self.step_index < len(self.steps):
            name, priority = self.steps[self.step_index]

            self.highlight_index = self.step_index
            self.status_message = f"Processing {name} priority {priority}"

            self.step_index += 1
            return

        self.animating = False
        self.highlight_index = None

        self.end_time = time.time()
        duration = self.end_time - self.start_time

        self.status_message = f"Processed {len(self.steps)} events in {duration:.2f}s"

    def draw_ui_block(self, screen):
        pygame.draw.rect(screen, BACKGROUND, self.ui_block)
        pygame.draw.line(screen, BLACK, (0, self.ui_block.bottom), (WIDTH, self.ui_block.bottom), 2)

    def draw_inputs(self, screen, fonts):
        pygame.draw.rect(screen, WHITE, self.name_box)
        pygame.draw.rect(screen, BLACK, self.name_box, 2)

        pygame.draw.rect(screen, WHITE, self.prio_box)
        pygame.draw.rect(screen, BLACK, self.prio_box, 2)

        name_text = self.input_name if self.input_name else "Event name"
        prio_text = self.input_priority if self.input_priority else "Priority"

        name_col = BLACK if self.input_name else DARK_GREY
        prio_col = BLACK if self.input_priority else DARK_GREY

        draw_text(screen, name_text, self.name_box.centerx, self.name_box.centery, fonts["small"], name_col, centre=True)
        draw_text(screen, prio_text, self.prio_box.centerx, self.prio_box.centery, fonts["small"], prio_col, centre=True)

    def get_node_pos(self, index):
        level = 0
        count = index + 1

        while count > 1:
            count //= 2
            level += 1

        first = (2 ** level) - 1
        pos = index - first
        nodes = 2 ** level

        x_gap = WIDTH // (nodes + 1)
        x = x_gap * (pos + 1)
        y = 260 + level * 85

        return x, y

    def draw_heap(self, screen, fonts):
        draw_text(screen, "Event Queue", WIDTH // 2, 60, fonts["heading"], TEXT, centre=True)

        if not self.heap:
            draw_text(screen, "No events", WIDTH // 2, 360, fonts["normal"], TEXT, centre=True)
            return

        for i in range(len(self.heap)):
            left = 2 * i + 1
            right = 2 * i + 2

            x1, y1 = self.get_node_pos(i)

            if left < len(self.heap):
                x2, y2 = self.get_node_pos(left)
                pygame.draw.line(screen, BLACK, (x1, y1), (x2, y2), 2)

            if right < len(self.heap):
                x2, y2 = self.get_node_pos(right)
                pygame.draw.line(screen, BLACK, (x1, y1), (x2, y2), 2)

        for i, event in enumerate(self.heap):
            x, y = self.get_node_pos(i)

            colour = YELLOW if i == self.highlight_index else LIGHT_BLUE

            pygame.draw.circle(screen, colour, (x, y), 28)
            pygame.draw.circle(screen, BLACK, (x, y), 28, 2)

            draw_text(screen, event.name, x, y - 8, fonts["small"], BLACK, centre=True)
            draw_text(screen, str(event.priority), x, y + 12, fonts["small"], DARK_GREY, centre=True)

    def draw_buttons(self, screen, fonts, mouse):
        for key, rect in self.buttons.items():
            draw_button(screen, rect, key.capitalize(), fonts["small"], mouse)

    def draw_screen(self, screen, fonts, mouse):
        clear_screen(screen)

        self.draw_ui_block(screen)
        self.draw_inputs(screen, fonts)
        self.draw_heap(screen, fonts)
        self.draw_buttons(screen, fonts, mouse)

        draw_status(screen, self.status_message, fonts["small"])


def run_event_queue(screen, clock):
    fonts = create_fonts()
    vis = EventQueueVisualiser()
    vis.create_buttons()

    running = True

    while running:
        mouse = pygame.mouse.get_pos()

        vis.update_animation()
        vis.draw_screen(screen, fonts, mouse)

        back = draw_back_button(screen, fonts["small"], mouse)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                if back.collidepoint(event.pos):
                    running = False
                    continue

                if vis.name_box.collidepoint(event.pos):
                    vis.active_input = "name"

                elif vis.prio_box.collidepoint(event.pos):
                    vis.active_input = "priority"

                else:
                    vis.active_input = None

                for key, rect in vis.buttons.items():
                    if rect.collidepoint(event.pos):
                        if key == "add":
                            vis.add_event()
                        elif key == "process":
                            vis.process_events()
                        elif key == "reset":
                            vis.reset()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_BACKSPACE:
                    if vis.active_input == "name":
                        vis.input_name = vis.input_name[:-1]
                    elif vis.active_input == "priority":
                        vis.input_priority = vis.input_priority[:-1]

                elif event.key == pygame.K_RETURN:
                    vis.add_event()

                else:
                    if vis.active_input == "name":
                        if event.unicode.isprintable() and len(vis.input_name) < 12:
                            vis.input_name += event.unicode

                    elif vis.active_input == "priority":
                        if event.unicode.isdigit() and len(vis.input_priority) < 3:
                            vis.input_priority += event.unicode

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    run_event_queue(screen, clock)