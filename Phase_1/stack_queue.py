import pygame
import sys
import os
from collections import deque

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import ui

class StackQueueVisualiser:
    def __init__(self):
        self.stack = []
        self.queue = deque()

        self.input_text = ""
        self.status = "Ready"

        self.highlight_stack_index = None
        self.highlight_queue_index = None

        self.stack_scroll = 0
        self.queue_scroll = 0
        self.scroll_speed = 35
        self.scroll_limit = 1200

        self.controls_panel = pygame.Rect(24, ui.HEADER_H + 16, ui.WIDTH - 48, 150)
        self.input_rect = pygame.Rect(ui.WIDTH // 2 - 170, self.controls_panel.y + 42, 340, 46)

        self.stack_panel = pygame.Rect(160, 260, 380, 360)
        self.queue_panel = pygame.Rect(560, 260, 380, 360)

        self.buttons = {}

    def create_buttons(self):
        labels = ["Push", "Pop", "Clear", "Enqueue", "Dequeue"]
        button_width = 130
        spacing = 12
        total_width = (button_width * len(labels)) + (spacing * (len(labels) - 1))
        start_x = ui.WIDTH // 2 - total_width // 2
        y = self.controls_panel.bottom - 50

        self.buttons = {
            label: pygame.Rect(start_x + i * (button_width + spacing), y, button_width, 42)
            for i, label in enumerate(labels)
        }

    def handle_scroll(self, event, mouse):
        if event.type != pygame.MOUSEWHEEL:
            return

        if self.stack_panel.collidepoint(mouse):
            self.stack_scroll += event.y * self.scroll_speed
            self.stack_scroll = max(-self.scroll_limit, min(self.scroll_limit, self.stack_scroll))

        elif self.queue_panel.collidepoint(mouse):
            self.queue_scroll += event.y * self.scroll_speed
            self.queue_scroll = max(-self.scroll_limit, min(self.scroll_limit, self.queue_scroll))

    def add_stack(self):
        if not self.input_text:
            self.status = "Enter value"
            return

        self.stack.append(self.input_text)
        self.highlight_stack_index = len(self.stack) - 1
        self.input_text = ""
        self.status = "Pushed"

    def remove_stack(self):
        if not self.stack:
            self.status = "Stack empty"
            return

        self.stack.pop()
        self.highlight_stack_index = None
        self.status = "Popped"

    def add_queue(self):
        if not self.input_text:
            self.status = "Enter value"
            return

        self.queue.append(self.input_text)
        self.highlight_queue_index = len(self.queue) - 1
        self.input_text = ""
        self.status = "Enqueued"

    def remove_queue(self):
        if not self.queue:
            self.status = "Queue empty"
            return

        self.queue.popleft()
        self.highlight_queue_index = 0 if self.queue else None
        self.status = "Dequeued"

    def clear_all(self):
        self.stack.clear()
        self.queue.clear()
        self.input_text = ""
        self.highlight_stack_index = None
        self.highlight_queue_index = None
        self.stack_scroll = 0
        self.queue_scroll = 0
        self.status = "Cleared"

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
            "Push": "start",
            "Enqueue": "start",
            "Clear": "ghost",
            "Pop": "danger",
            "Dequeue": "danger",
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

    def draw_vertical_panel(self, screen, fonts, panel, title, values, highlight_index, scroll, reverse=False):
        ui.draw_panel(screen, panel)

        ui.draw_text(
            screen,
            title,
            panel.centerx,
            panel.y + 25,
            fonts["heading"],
            ui.TEXT_3,
            centre=True
        )

        clip = screen.get_clip()
        screen.set_clip(panel)

        x = panel.centerx - 37
        y_start = panel.top + 60
        spacing = 60

        display_values = list(reversed(values)) if reverse else list(values)

        for i, value in enumerate(display_values):
            real_index = len(values) - 1 - i if reverse else i
            rect = pygame.Rect(x, y_start + i * spacing + scroll, 75, 42)

            ui.draw_node_rect(
                screen,
                rect.x,
                rect.y,
                value,
                fonts["normal"],
                highlight=(real_index == highlight_index)
            )

        screen.set_clip(clip)

    def draw_stack(self, screen, fonts):
        self.draw_vertical_panel(
            screen,
            fonts,
            self.stack_panel,
            "STACK LIFO",
            self.stack,
            self.highlight_stack_index,
            self.stack_scroll,
            reverse=True
        )

    def draw_queue(self, screen, fonts):
        self.draw_vertical_panel(
            screen,
            fonts,
            self.queue_panel,
            "QUEUE FIFO",
            self.queue,
            self.highlight_queue_index,
            self.queue_scroll
        )

    def draw(self, screen, fonts, mouse):
        ui.clear_screen(screen)
        ui.draw_header(screen, "Stack and Queue", fonts)

        self.draw_controls(screen, fonts, mouse)
        self.draw_stack(screen, fonts)
        self.draw_queue(screen, fonts)

        back = ui.draw_back_button(screen, fonts["small"], mouse)
        ui.draw_status(screen, self.status, fonts["small"])

        return back


def run_stack_queue(screen, clock):
    fonts = ui.create_fonts()
    vis = StackQueueVisualiser()
    vis.create_buttons()

    actions = {
        "Push": vis.add_stack,
        "Pop": vis.remove_stack,
        "Enqueue": vis.add_queue,
        "Dequeue": vis.remove_queue,
        "Clear": vis.clear_all,
    }

    running = True

    while running:
        mouse = pygame.mouse.get_pos()
        back = vis.draw(screen, fonts, mouse)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            vis.handle_scroll(event, mouse)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_BACKSPACE:
                    vis.input_text = vis.input_text[:-1]
                elif event.unicode.isprintable():
                    vis.input_text += event.unicode

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back.collidepoint(event.pos):
                    running = False
                else:
                    for label, rect in vis.buttons.items():
                        if rect.collidepoint(event.pos):
                            actions[label]()

        pygame.display.flip()
        clock.tick(ui.FPS)


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((ui.WIDTH, ui.HEIGHT))
    clock = pygame.time.Clock()
    run_stack_queue(screen, clock)