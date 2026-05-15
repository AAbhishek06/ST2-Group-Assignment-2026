# bst.py
import pygame
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import ui

# Classes
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class SingleLinkedList:
    def __init__(self):
        self.head = None

    def insert_at_index(self, data, index):
        new_node = Node(data)

        if index == 0:
            new_node.next = self.head
            self.head = new_node
            return True

        current = self.head

        for _ in range(index - 1):
            if current is None:
                return False
            current = current.next

        if current is None:
            return False

        new_node.next = current.next
        current.next = new_node
        return True

    def delete_value(self, value):
        current = self.head
        previous = None

        while current:
            if str(current.data) == str(value):
                if previous:
                    previous.next = current.next
                else:
                    self.head = current.next
                return True

            previous = current
            current = current.next

        return False

    def search(self, value):
        current = self.head
        index = 0

        while current:
            if str(current.data) == str(value):
                return index

            current = current.next
            index += 1

        return -1

    def reverse(self):
        previous = None
        current = self.head

        while current:
            next_node = current.next
            current.next = previous
            previous = current
            current = next_node

        self.head = previous

    def to_list(self):
        values = []
        current = self.head

        while current:
            values.append(current.data)
            current = current.next

        return values

    def clear(self):
        self.head = None

class LinkedListVisualiser:
    def __init__(self):
        self.list = SingleLinkedList()
        self.value_text = ""
        self.index_text = ""
        self.active_box = "value"
        self.highlight_index = None
        self.status = "Enter value and index"

        self.camera = pygame.Vector2(0, 0)
        self.dragging = False
        self.last_mouse = pygame.Vector2(0, 0)
        self.cam_limit_x = 1200
        self.cam_limit_y = 1200

        self.input_rect = pygame.Rect(ui.WIDTH // 2 - 255, ui.HEADER_H + 56, 340, 46)
        self.index_rect = pygame.Rect(self.input_rect.right + 20, ui.HEADER_H + 56, 150, 46)
        self.controls_panel = pygame.Rect(24, ui.HEADER_H + 16, ui.WIDTH - 48, 150)
        self.buttons = {}

    # Buttons
    def create_buttons(self):
        labels = ["Insert", "Delete", "Search", "Reverse", "Clear"]
        button_width = 130
        spacing = 12
        total_width = (button_width * len(labels)) + (spacing * (len(labels) - 1))
        start_x = ui.WIDTH // 2 - total_width // 2
        y = self.input_rect.bottom + 18

        self.buttons = {
            label: pygame.Rect(start_x + i * (button_width + spacing), y, button_width, 42)
            for i, label in enumerate(labels)
        }

    # Dragging
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
            current = pygame.Vector2(event.pos)
            self.camera += current - self.last_mouse
            self.last_mouse = current
            self.clamp_camera()

    # Input actions
    def handle_input_click(self, pos):
        if self.input_rect.collidepoint(pos):
            self.active_box = "value"
        elif self.index_rect.collidepoint(pos):
            self.active_box = "index"

    # List actions
    def insert_node(self):
        if not self.value_text:
            self.status = "Enter value"
            return

        if not self.index_text:
            self.status = "Enter index"
            return

        if not self.index_text.isdigit():
            self.status = "Invalid index"
            return

        index = int(self.index_text)

        if self.list.insert_at_index(self.value_text, index):
            self.highlight_index = index
            self.status = "Inserted"
            self.value_text = ""
            self.index_text = ""
        else:
            self.status = "Index out of range"

    def delete_node(self):
        if not self.value_text:
            self.status = "Enter value"
            return

        if self.list.delete_value(self.value_text):
            self.status = "Deleted"
            self.value_text = ""
        else:
            self.status = "Not found"

    def search_node(self):
        if not self.value_text:
            self.status = "Enter value"
            return

        self.highlight_index = self.list.search(self.value_text)

        if self.highlight_index == -1:
            self.highlight_index = None
            self.status = "Not found"
        else:
            self.status = "Found"

    def reverse_list(self):
        self.list.reverse()
        self.status = "Reversed"

    def clear_list(self):
        self.list.clear()
        self.value_text = ""
        self.index_text = ""
        self.highlight_index = None
        self.status = "Cleared"

    # Input drawing
    def draw_inputs(self, screen, fonts, mouse):
        inputs = [
            ("INSERT VALUE", self.input_rect, self.value_text, "value"),
            ("INSERT INDEX", self.index_rect, self.index_text, "index"),
        ]

        for label, rect, text, box_name in inputs:
            ui.draw_label(screen, label, rect.x, rect.y - 22, fonts["heading"])

            ui.draw_input_box(
                screen,
                rect,
                text,
                fonts["normal"],
                active=(self.active_box == box_name),
                mouse_pos=mouse
            )

    # List drawing
    def draw_list(self, screen, fonts):
        values = self.list.to_list()

        if not values:
            ui.draw_text(
                screen,
                "List empty",
                ui.WIDTH // 2,
                ui.HEIGHT // 2,
                fonts["heading"],
                ui.TEXT_1,
                centre=True
            )
            return

        x = ui.WIDTH // 2 - (len(values) * 60)
        y = 360

        for i, value in enumerate(values):
            rect = pygame.Rect(x, y, 75, 42)

            ui.draw_node_rect(
                screen,
                rect.x,
                rect.y,
                value,
                fonts["normal"],
                highlight=(i == self.highlight_index)
            )

            ui.draw_text(
                screen,
                str(i),
                rect.centerx,
                rect.bottom + 18,
                fonts["small"],
                ui.TEXT_3,
                centre=True
            )

            if i < len(values) - 1:
                ui.draw_arrow(screen, (rect.right, rect.centery), (rect.right + 30, rect.centery))

            x += 120

    def draw_controls(self, screen, fonts, mouse):
        ui.draw_panel(screen, self.controls_panel)
        self.draw_inputs(screen, fonts, mouse)

        button_styles = {
            "Insert": "start",
            "Delete": "danger",
            "Reverse": "ghost",
        }

        for label, rect in self.buttons.items():
            style = button_styles.get(label, "neutral")
            ui.draw_button(screen, rect, label, fonts["small"], mouse, style=style)

    # Screen drawing
    def draw(self, screen, fonts, mouse):
        ui.clear_screen(screen)
        self.draw_list(screen, fonts)
        ui.draw_header(screen, "Linked List", fonts)
        self.draw_controls(screen, fonts, mouse)
        back = ui.draw_back_button(screen, fonts["small"], mouse)
        ui.draw_status(screen, self.status, fonts["small"])
        return back


# Main loop
def run_linked_list(screen, clock):
    fonts = ui.create_fonts()
    vis = LinkedListVisualiser()
    vis.create_buttons()

    actions = {
        "Insert": vis.insert_node,
        "Delete": vis.delete_node,
        "Search": vis.search_node,
        "Reverse": vis.reverse_list,
        "Clear": vis.clear_list,
    }

    running = True

    while running:
        mouse = pygame.mouse.get_pos()
        back = vis.draw(screen, fonts, mouse)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            vis.handle_drag(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_TAB:
                    vis.active_box = "index" if vis.active_box == "value" else "value"

                elif event.key == pygame.K_BACKSPACE:
                    if vis.active_box == "value":
                        vis.value_text = vis.value_text[:-1]
                    else:
                        vis.index_text = vis.index_text[:-1]

                elif event.key == pygame.K_RETURN:
                    vis.insert_node()

                elif event.unicode.isdigit() or event.unicode.isalpha():
                    if vis.active_box == "value":
                        vis.value_text += event.unicode
                    else:
                        vis.index_text += event.unicode

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back.collidepoint(event.pos):
                    running = False
                else:
                    vis.handle_input_click(event.pos)

                    for label, rect in vis.buttons.items():
                        if rect.collidepoint(event.pos):
                            actions[label]()

        pygame.display.flip()
        clock.tick(ui.FPS)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((ui.WIDTH, ui.HEIGHT))
    clock = pygame.time.Clock()
    run_linked_list(screen, clock)