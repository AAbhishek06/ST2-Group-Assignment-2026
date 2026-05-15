import pygame
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import ui


class TreeNode:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None


class BinarySearchTree:
    def __init__(self):
        self.root = None

    def insert(self, data):
        if self.root is None:
            self.root = TreeNode(data)
            return True
        return self._insert(self.root, data)

    def _insert(self, node, data):
        if data == node.data:
            return False

        side = "left" if data < node.data else "right"
        child = getattr(node, side)

        if child is None:
            setattr(node, side, TreeNode(data))
            return True

        return self._insert(child, data)

    def traverse(self, mode):
        result = []
        self._traverse(self.root, result, mode)
        return result

    def _traverse(self, node, result, mode):
        if node is None:
            return

        if mode == "pre":
            result.append(node.data)

        self._traverse(node.left, result, mode)

        if mode == "in":
            result.append(node.data)

        self._traverse(node.right, result, mode)

        if mode == "post":
            result.append(node.data)

    def clear(self):
        self.root = None


class BSTVisualiser:
    def __init__(self):
        self.tree = BinarySearchTree()
        self.input_text = ""
        self.input_active = False

        self.status = "Ready"
        self.traversal = ""
        self.highlight = None

        self.camera = pygame.Vector2(0, 0)
        self.dragging = False
        self.last_mouse = pygame.Vector2(0, 0)

        self.cam_limit_x = 1200
        self.cam_limit_y = 1200

        self.input_rect = pygame.Rect(ui.WIDTH // 2 - 170, ui.HEADER_H + 56, 340, 46)
        self.controls_panel = pygame.Rect(24, ui.HEADER_H + 16, ui.WIDTH - 48, 150)
        self.buttons = {}

        self._test_active = False
        self._test_values = []
        self._test_index = 0
        self._test_timer = 0
        self._test_delay = 700
        self._test_phase = "insert"
        self._test_log = []

    def create_buttons(self):
        labels = ["Insert", "Inorder", "Preorder", "Postorder", "Clear", "Recenter"]
        button_width = 130
        spacing = 12
        total_width = (button_width * len(labels)) + (spacing * (len(labels) - 1))
        start_x = ui.WIDTH // 2 - total_width // 2
        y = self.input_rect.bottom + 18

        self.buttons = {
            label: pygame.Rect(start_x + i * (button_width + spacing), y, button_width, 42)
            for i, label in enumerate(labels)
        }

    def world(self, x, y):
        return x + self.camera.x, y + self.camera.y

    def insert_node(self):
        if self.input_text == "":
            self.status = "Enter value"
            return

        if not self.input_text.isdigit():
            self.status = "Numbers only"
            return

        value = int(self.input_text)

        if self.tree.insert(value):
            self.highlight = value
            self.status = "Inserted"
            self.input_text = ""
        else:
            self.status = "Duplicate"

    def show(self, mode):
        labels = {
            "in": "Inorder",
            "pre": "Preorder",
            "post": "Postorder",
        }

        self.traversal = str(self.tree.traverse(mode))
        self.status = labels[mode]

    def clear_all(self):
        self.tree.clear()
        self.input_text = ""
        self.traversal = ""
        self.highlight = None
        self.status = "Cleared"

    def reset_view(self):
        self.camera = pygame.Vector2(0, 0)
        self.status = "Recentered"

    def bst_test(self):
        self.tree.clear()

        self.input_text = ""
        self.traversal = ""
        self.highlight = None

        self._test_active = True
        self._test_values = [50, 30, 70, 20, 40, 60, 80]
        self._test_index = 0
        self._test_timer = pygame.time.get_ticks()
        self._test_phase = "insert"
        self._test_log = []

        self.status = "Test started"

    def update_test(self):
        if not self._test_active:
            return

        now = pygame.time.get_ticks()

        if now - self._test_timer < self._test_delay:
            return

        self._test_timer = now

        if self._test_phase == "insert":
            if self._test_index < len(self._test_values):
                value = self._test_values[self._test_index]
                self.tree.insert(value)
                self.highlight = value
                self._test_log.append(value)
                self.status = f"Inserted {value}"
                self._test_index += 1
                return

            self._test_phase = "verify"
            self._test_index = 0
            return

        if self._test_phase == "verify":
            inorder = self.tree.traverse("in")
            self.traversal = str(inorder)

            expected = sorted(self._test_values)

            if inorder == expected:
                self.status = f"PASS inorder {inorder}"
            else:
                self.status = f"FAIL expected {expected} got {inorder}"

            self._test_phase = "done"
            self._test_active = False

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

    def draw_node(self, screen, fonts, node, x, y, gap):
        sx, sy = self.world(x, y)

        ui.draw_node_rect(
            screen,
            sx - ui.NODE_WIDTH // 2,
            sy - ui.NODE_HEIGHT // 2,
            node.data,
            fonts["normal"],
            highlight=(node.data == self.highlight)
        )

        for child, cx in [(node.left, x - gap), (node.right, x + gap)]:
            if child:
                px, py = self.world(cx, y + 100)

                ui.draw_arrow(
                    screen,
                    (sx, sy + ui.NODE_HEIGHT // 2),
                    (px, py - ui.NODE_HEIGHT // 2),
                    ui.BORDER_DEFAULT,
                    2
                )

                self.draw_node(screen, fonts, child, cx, y + 100, max(gap // 2, 70))

    def draw_tree(self, screen, fonts):
        if self.tree.root is None:
            ui.draw_text(
                screen,
                "Tree empty",
                ui.WIDTH // 2,
                ui.HEIGHT // 2 + 40,
                fonts["heading"],
                ui.TEXT_1,
                centre=True
            )
            return

        self.draw_node(screen, fonts, self.tree.root, ui.WIDTH // 2, 280, 240)

    def draw_controls(self, screen, fonts, mouse):
        ui.draw_panel(screen, self.controls_panel)

        ui.draw_label(
            screen,
            "INSERT VALUE",
            self.input_rect.x,
            self.input_rect.y - 22,
            fonts["heading"]
        )

        ui.draw_input_box(
            screen,
            self.input_rect,
            self.input_text,
            fonts["normal"],
            active=self.input_active,
            mouse_pos=mouse
        )

        button_styles = {
            "Insert": "start",
            "Clear": "danger",
            "Recenter": "ghost",
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

    def draw_traversal(self, screen, fonts):
        if self.traversal == "":
            return

        panel = pygame.Rect(24, ui.HEIGHT - ui.STATUS_H - 88, ui.WIDTH - 48, 52)
        ui.draw_panel(screen, panel)

        ui.draw_text(
            screen,
            self.traversal,
            panel.centerx,
            panel.centery,
            fonts["normal"],
            ui.TEXT_1,
            centre=True
        )

    def draw(self, screen, fonts, mouse):
        ui.clear_screen(screen)
        self.draw_tree(screen, fonts)
        ui.draw_header(screen, "Binary Search Tree", fonts)
        self.draw_controls(screen, fonts, mouse)
        self.draw_traversal(screen, fonts)

        back = ui.draw_back_button(screen, fonts["small"], mouse)
        test = ui.draw_test_button(screen, fonts["small"], mouse)

        ui.draw_status(screen, self.status, fonts["small"])

        return back, test


def run_bst(screen, clock):
    fonts = ui.create_fonts()
    vis = BSTVisualiser()
    vis.create_buttons()

    actions = {
        "Insert": vis.insert_node,
        "Inorder": lambda: vis.show("in"),
        "Preorder": lambda: vis.show("pre"),
        "Postorder": lambda: vis.show("post"),
        "Clear": vis.clear_all,
        "Recenter": vis.reset_view,
        "Run Test": vis.bst_test
    }

    running = True

    while running:
        mouse = pygame.mouse.get_pos()
        back, test = vis.draw(screen, fonts, mouse)

        vis.update_test()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            vis.handle_drag(event)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                if back.collidepoint(event.pos):
                    running = False
                    continue

                if test.collidepoint(event.pos):
                    vis.bst_test()
                    continue

                vis.input_active = vis.input_rect.collidepoint(event.pos)

                if vis.input_active:
                    continue

                for label, rect in vis.buttons.items():
                    if rect.collidepoint(event.pos):
                        actions[label]()

            if event.type == pygame.KEYDOWN:

                if vis.input_active:

                    if event.key == pygame.K_BACKSPACE:
                        vis.input_text = vis.input_text[:-1]

                    elif event.key == pygame.K_RETURN:
                        vis.insert_node()

                    elif event.unicode.isdigit():
                        vis.input_text += event.unicode

        pygame.display.flip()
        clock.tick(ui.FPS)


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((ui.WIDTH, ui.HEIGHT))
    clock = pygame.time.Clock()
    run_bst(screen, clock)
