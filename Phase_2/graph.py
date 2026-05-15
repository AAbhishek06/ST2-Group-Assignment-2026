import pygame
import sys
import os
from collections import deque

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import ui


class GraphVisualiser:
    def __init__(self):
        self.nodes = {
            "A": (250, 450),
            "B": (430, 380),
            "C": (430, 520),
            "D": (650, 350),
            "E": (650, 450),
            "F": (650, 550),
            "G": (880, 450),
        }

        self.edges = [
            ("A", "B"),
            ("A", "C"),
            ("B", "D"),
            ("B", "E"),
            ("C", "E"),
            ("C", "F"),
            ("D", "G"),
            ("E", "G"),
            ("F", "G"),
        ]

        self.adj = {
            "A": ["B", "C"],
            "B": ["D", "E"],
            "C": ["E", "F"],
            "D": ["G"],
            "E": ["G"],
            "F": ["G"],
            "G": [],
        }

        self.center_graph()

        self.start_node = None
        self.visited = set()
        self.order = []

        self.queue = deque()
        self.stack = []

        self.mode = None
        self.current = None

        self.auto = False
        self.last_step = 0
        self.delay = 700

        self.status = "Select a start node then select BFS or DFS"

        self.controls_panel = pygame.Rect(
            24,
            ui.HEADER_H + 16,
            ui.WIDTH - 48,
            150
        )

        self.buttons = {}

    def center_graph(self):
        xs = [x for x, y in self.nodes.values()]
        ys = [y for x, y in self.nodes.values()]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        offset_x = (ui.WIDTH - (max_x - min_x)) // 2 - min_x
        offset_y = (ui.HEIGHT - (max_y - min_y)) // 2 - min_y + 40

        self.nodes = {
            k: (x + offset_x, y + offset_y)
            for k, (x, y) in self.nodes.items()
        }

    def create_buttons(self):
        labels = ["BFS", "DFS", "RESET"]

        button_w = 130
        spacing = 16

        total_width = len(labels) * button_w + (len(labels) - 1) * spacing
        start_x = ui.WIDTH // 2 - total_width // 2
        y = self.controls_panel.y + 85

        for i, label in enumerate(labels):
            self.buttons[label] = pygame.Rect(
                start_x + i * (button_w + spacing),
                y,
                button_w,
                42
            )

    def reset(self):
        self.visited.clear()
        self.order.clear()
        self.queue.clear()
        self.stack.clear()
        self.mode = None
        self.auto = False
        self.current = None
        self.status = "Reset"

    def set_start(self, node):
        self.start_node = node
        self.reset()
        self.current = node
        self.status = f"Start {node}"

    def start_bfs(self):
        if not self.start_node:
            self.status = "Select start node"
            return

        self.reset()
        self.mode = "BFS"
        self.queue.append(self.start_node)
        self.auto = True
        self.last_step = pygame.time.get_ticks()
        self.status = "BFS running"

    def start_dfs(self):
        if not self.start_node:
            self.status = "Select start node"
            return

        self.reset()
        self.mode = "DFS"
        self.stack.append(self.start_node)
        self.auto = True
        self.last_step = pygame.time.get_ticks()
        self.status = "DFS running"

    def auto_update(self):
        if not self.auto:
            return

        now = pygame.time.get_ticks()

        if now - self.last_step >= self.delay:
            self.step()
            self.last_step = now

    def step(self):
        if self.mode == "BFS":
            self.bfs()
        elif self.mode == "DFS":
            self.dfs()

    def bfs(self):
        if not self.queue:
            self.auto = False
            self.status = f"BFS done {self.order}"
            return

        node = self.queue.popleft()

        if node in self.visited:
            return

        self.visited.add(node)
        self.order.append(node)
        self.current = node

        for n in self.adj[node]:
            if n not in self.visited and n not in self.queue:
                self.queue.append(n)

    def dfs(self):
        if not self.stack:
            self.auto = False
            self.status = f"DFS done {self.order}"
            return

        node = self.stack.pop()

        if node in self.visited:
            return

        self.visited.add(node)
        self.order.append(node)
        self.current = node

        for n in reversed(self.adj[node]):
            if n not in self.visited and n not in self.stack:
                self.stack.append(n)

    def draw_controls(self, screen, fonts, mouse):
        ui.draw_panel(screen, self.controls_panel)

        for label, rect in self.buttons.items():
            style = "neutral"

            if label == "BFS":
                style = "start"
            if label == "DFS":
                style = "start"
            if label == "RESET":
                style = "danger"

            ui.draw_button(screen, rect, label, fonts["small"], mouse, style=style)

    def draw_edges(self, screen):
        for a, b in self.edges:
            pygame.draw.line(screen, ui.BORDER_DEFAULT, self.nodes[a], self.nodes[b], 2)

    def draw_nodes(self, screen, fonts):
        for node, pos in self.nodes.items():
            x, y = pos

            colour = ui.LIGHT_BLUE

            if node in self.visited:
                colour = ui.GREEN

            if node == self.start_node:
                colour = ui.ORANGE

            pygame.draw.circle(screen, colour, (x, y), 26)
            pygame.draw.circle(screen, ui.BLACK, (x, y), 26, 2)

            ui.draw_text(
                screen,
                node,
                x,
                y,
                fonts["small"],
                ui.BLACK,
                centre=True
            )

    def draw_header(self, screen, fonts):
        ui.draw_header(screen, "Graph Traversal", fonts)

        if self.start_node:
            ui.draw_text(
                screen,
                f"Start {self.start_node}",
                ui.WIDTH // 2,
                95,
                fonts["small"],
                ui.TEXT_1,
                centre=True
            )

        if self.mode:
            ui.draw_text(
                screen,
                f"Mode {self.mode}",
                ui.WIDTH // 2,
                120,
                fonts["small"],
                ui.TEXT_1,
                centre=True
            )

    def draw_order(self, screen, fonts):
        if self.order:
            ui.draw_text(
                screen,
                " -> ".join(self.order),
                ui.WIDTH // 2,
                ui.HEIGHT - 80,
                fonts["small"],
                ui.BLACK,
                centre=True
            )

    def draw(self, screen, fonts, mouse):
        ui.clear_screen(screen)

        self.draw_edges(screen)
        self.draw_nodes(screen, fonts)

        self.draw_header(screen, fonts)

        self.draw_controls(screen, fonts, mouse)
        self.draw_order(screen, fonts)

        ui.draw_status(screen, self.status, fonts["small"])


def run_graph(screen, clock):
    fonts = ui.create_fonts()
    graph = GraphVisualiser()
    graph.create_buttons()

    running = True

    while running:
        mouse = pygame.mouse.get_pos()

        graph.auto_update()
        graph.draw(screen, fonts, mouse)

        back = ui.draw_back_button(screen, fonts["small"], mouse)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back.collidepoint(event.pos):
                    running = False
                    continue

                if graph.buttons["BFS"].collidepoint(event.pos):
                    graph.start_bfs()

                elif graph.buttons["DFS"].collidepoint(event.pos):
                    graph.start_dfs()

                elif graph.buttons["RESET"].collidepoint(event.pos):
                    graph.reset()

                else:
                    for node, pos in graph.nodes.items():
                        x, y = pos
                        dx = event.pos[0] - x
                        dy = event.pos[1] - y

                        if dx * dx + dy * dy <= 26 * 26:
                            graph.set_start(node)
                            break

        pygame.display.flip()
        clock.tick(ui.FPS)


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((ui.WIDTH, ui.HEIGHT))
    clock = pygame.time.Clock()
    run_graph(screen, clock)
