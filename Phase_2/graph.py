# Imports
import pygame
import sys
import os
from collections import deque

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import ui

# Visualiser setup
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

        self.controls_panel = pygame.Rect(24, ui.HEADER_H + 16, ui.WIDTH - 48, 150)
        self.buttons = {}

        self.test_mode = False
        self.test_steps = []
        self.test_index = 0
        self.test_last = 0

    def center_graph(self):
        xs = [x for x, y in self.nodes.values()]
        ys = [y for x, y in self.nodes.values()]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        offset_x = (ui.WIDTH - (max_x - min_x)) // 2 - min_x
        offset_y = (ui.HEIGHT - (max_y - min_y)) // 2 - min_y + 40

        self.nodes = {
            node: (x + offset_x, y + offset_y)
            for node, (x, y) in self.nodes.items()
        }

    def create_buttons(self):
        labels = ["BFS", "DFS", "RESET"]
        button_w = 130
        spacing = 16
        total_width = len(labels) * button_w + (len(labels) - 1) * spacing
        start_x = ui.WIDTH // 2 - total_width // 2
        y = self.controls_panel.y + 85

        self.buttons = {
            label: pygame.Rect(start_x + i * (button_w + spacing), y, button_w, 42)
            for i, label in enumerate(labels)
        }

    def reset(self):
        self.visited.clear()
        self.order.clear()
        self.queue.clear()
        self.stack.clear()

        self.mode = None
        self.current = None
        self.auto = False
        self.status = "Reset"

    def set_start(self, node):
        self.start_node = node
        self.reset()
        self.current = node
        self.status = f"Start {node}"

    # Traversal controls
    def start_search(self, mode):
        if not self.start_node:
            self.status = "Select start node"
            return

        self.reset()
        self.mode = mode
        self.auto = True
        self.last_step = pygame.time.get_ticks()

        if mode == "BFS":
            self.queue.append(self.start_node)
        else:
            self.stack.append(self.start_node)

        self.status = f"{mode} running"

    def start_bfs(self):
        self.start_search("BFS")

    def start_dfs(self):
        self.start_search("DFS")

    def auto_update(self):
        if self.auto and pygame.time.get_ticks() - self.last_step >= self.delay:
            self.step()
            self.last_step = pygame.time.get_ticks()

        if self.test_mode:
            self.run_test_step()

    def step(self):
        if self.mode == "BFS":
            self.search_step(self.queue, pop_left=True)
        elif self.mode == "DFS":
            self.search_step(self.stack, pop_left=False)

    def search_step(self, structure, pop_left):
        if not structure:
            self.auto = False
            self.status = f"{self.mode} done {self.order}"
            return

        node = structure.popleft() if pop_left else structure.pop()

        if node in self.visited:
            return

        self.visited.add(node)
        self.order.append(node)
        self.current = node

        neighbours = self.adj[node] if pop_left else reversed(self.adj[node])

        for neighbour in neighbours:
            if neighbour not in self.visited and neighbour not in structure:
                structure.append(neighbour)

    # Test mode
    def run_tests(self):
        self.test_mode = True
        self.test_steps = [
            ("click_node", "D"),
            ("click_button", "BFS"),
            ("wait", 2500),
            ("click_button", "RESET"),
            ("click_node", "A"),
            ("click_button", "DFS"),
            ("wait", 2500),
            ("end", None),
        ]
        self.test_index = 0
        self.test_last = pygame.time.get_ticks()
        self.status = "TEST RUNNING"

    def run_test_step(self):
        if self.test_index >= len(self.test_steps):
            self.end_test()
            return

        action, value = self.test_steps[self.test_index]
        now = pygame.time.get_ticks()

        if action == "wait":
            if now - self.test_last < value:
                return
            self.test_last = now

        elif action == "click_node":
            self.set_start(value)

        elif action == "click_button":
            test_actions = {
                "BFS": self.start_bfs,
                "DFS": self.start_dfs,
                "RESET": self.reset
            }
            test_actions[value]()

        elif action == "end":
            self.end_test()
            return

        self.test_index += 1

    def end_test(self):
        self.test_mode = False
        self.status = "TEST COMPLETE"

    # Drawing interface
    def draw_controls(self, screen, fonts, mouse):
        ui.draw_panel(screen, self.controls_panel)

        button_styles = {
            "BFS": "start",
            "DFS": "start",
            "RESET": "danger"
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

    def draw_edges(self, screen):
        for start, end in self.edges:
            pygame.draw.line(screen, ui.BORDER_DEFAULT, self.nodes[start], self.nodes[end], 2)

    def draw_nodes(self, screen, fonts):
        for node, pos in self.nodes.items():
            colour = ui.LIGHT_BLUE

            if node in self.visited:
                colour = ui.GREEN

            if node == self.start_node:
                colour = ui.ORANGE

            pygame.draw.circle(screen, colour, pos, 26)
            pygame.draw.circle(screen, ui.BLACK, pos, 26, 2)

            ui.draw_text(
                screen,
                node,
                pos[0],
                pos[1],
                fonts["small"],
                ui.BLACK,
                centre=True
            )

    def draw_order(self, screen, fonts):
        if not self.order:
            return

        ui.draw_text(
            screen,
            " -> ".join(self.order),
            ui.WIDTH // 2,
            ui.HEIGHT - 80,
            fonts["small"],
            ui.WHITE,
            centre=True
        )

    def draw(self, screen, fonts, mouse):
        ui.clear_screen(screen)

        self.draw_edges(screen)
        self.draw_nodes(screen, fonts)

        ui.draw_header(screen, "Graph Traversal", fonts)
        self.draw_controls(screen, fonts, mouse)
        self.draw_order(screen, fonts)
        ui.draw_status(screen, self.status, fonts["small"])

        return ui.draw_test_button(screen, fonts["small"], mouse)

# Main loop
def run_graph(screen, clock):
    fonts = ui.create_fonts()
    graph = GraphVisualiser()
    graph.create_buttons()

    actions = {
        "BFS": graph.start_bfs,
        "DFS": graph.start_dfs,
        "RESET": graph.reset
    }

    running = True

    while running:
        mouse = pygame.mouse.get_pos()

        graph.auto_update()
        test = graph.draw(screen, fonts, mouse)
        back = ui.draw_back_button(screen, fonts["small"], mouse)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back.collidepoint(event.pos):
                    running = False
                    continue

                if test.collidepoint(event.pos):
                    graph.run_tests()
                    continue

                clicked_button = False

                for label, rect in graph.buttons.items():
                    if rect.collidepoint(event.pos):
                        actions[label]()
                        clicked_button = True
                        break

                if clicked_button:
                    continue

                for node, pos in graph.nodes.items():
                    dx = event.pos[0] - pos[0]
                    dy = event.pos[1] - pos[1]

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
