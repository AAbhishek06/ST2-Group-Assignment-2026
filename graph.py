import pygame
import sys
import os
from collections import deque

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from configure import *
from utilities import *


class GraphVisualizer:
    def __init__(self):
        self.nodes = {
            "A": (250, 320),
            "B": (450, 220),
            "C": (450, 420),
            "D": (650, 320),
        }

        self.edges = [
            ("A", "B"),
            ("A", "C"),
            ("B", "D"),
            ("C", "D"),
        ]

        self.adj = {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["D"],
            "D": [],
        }

        self.center_graph()

        self.start_node = None
        self.visited = set()

        self.queue = deque()
        self.stack = []

        self.mode = None
        self.running = False
        self.current = None

        self.buttons = {}

    def center_graph(self):
        xs = [x for x, y in self.nodes.values()]
        ys = [y for x, y in self.nodes.values()]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        graph_width = max_x - min_x
        graph_height = max_y - min_y

        offset_x = (WIDTH - graph_width) // 2 - min_x
        offset_y = (HEIGHT - graph_height) // 2 - min_y

        self.nodes = {
            n: (x + offset_x, y + offset_y)
            for n, (x, y) in self.nodes.items()
        }

    def create_buttons(self):
        center_x = WIDTH // 2
        labels = ["bfs", "dfs", "step", "reset"]

        spacing = 140
        button_w = 120

        total_width = (button_w * len(labels)) + (spacing * (len(labels) - 1))
        start_x = center_x - total_width // 2
        y = 160

        self.buttons = {}

        for i in range(len(labels)):
            self.buttons[labels[i]] = pygame.Rect(
                start_x + i * (button_w + spacing),
                y,
                button_w,
                40
            )

    def reset(self):
        self.visited = set()
        self.queue = deque()
        self.stack = []
        self.current = None
        self.running = False
        self.mode = None

    def set_start(self, node):
        self.start_node = node
        self.reset()
        self.current = node

    def start_bfs(self):
        if self.start_node is None:
            return

        self.reset()
        self.mode = "BFS"
        self.running = True
        self.queue = deque([self.start_node])

    def start_dfs(self):
        if self.start_node is None:
            return

        self.reset()
        self.mode = "DFS"
        self.running = True
        self.stack = [self.start_node]

    def step(self):
        if self.mode == "BFS":
            self.bfs_step()
        elif self.mode == "DFS":
            self.dfs_step()

    def bfs_step(self):
        while self.queue:
            node = self.queue.popleft()

            if node in self.visited:
                continue

            self.visited.add(node)
            self.current = node

            for n in self.adj[node]:
                if n not in self.visited and n not in self.queue:
                    self.queue.append(n)

            return

        self.running = False

    def dfs_step(self):
        while self.stack:
            node = self.stack.pop()

            if node in self.visited:
                continue

            self.visited.add(node)
            self.current = node

            for n in reversed(self.adj[node]):
                if n not in self.visited and n not in self.stack:
                    self.stack.append(n)

            return

        self.running = False

    def draw_edges(self, screen):
        for a, b in self.edges:
            pygame.draw.line(screen, BLACK, self.nodes[a], self.nodes[b], 2)

    def draw_nodes(self, screen, fonts):
        for node, pos in self.nodes.items():
            x, y = pos

            if node == self.current:
                colour = YELLOW
            elif node in self.visited:
                colour = GREEN
            elif node == self.start_node:
                colour = ORANGE
            else:
                colour = LIGHT_BLUE

            pygame.draw.circle(screen, colour, (x, y), 26)
            pygame.draw.circle(screen, BLACK, (x, y), 26, 2)

            draw_text(screen, node, x, y, fonts["small"], BLACK, centre=True)

    def draw_buttons(self, screen, fonts, mouse_pos):
        draw_button(screen, self.buttons["bfs"], "BFS", fonts["small"], mouse_pos)
        draw_button(screen, self.buttons["dfs"], "DFS", fonts["small"], mouse_pos)
        draw_button(screen, self.buttons["step"], "STEP", fonts["small"], mouse_pos)
        draw_button(screen, self.buttons["reset"], "RESET", fonts["small"], mouse_pos)

    def draw_ui(self, screen, fonts):
        draw_text(screen, "Graph Traversal", WIDTH // 2, 60, fonts["heading"], DARK_GREY, centre=True)

        if self.start_node:
            draw_text(screen, "Start " + self.start_node, WIDTH // 2, 105, fonts["small"], BLACK, centre=True)

        if self.mode:
            draw_text(screen, self.mode, WIDTH // 2, 125, fonts["small"], BLACK, centre=True)

    def draw_screen(self, screen, fonts, mouse_pos):
        clear_screen(screen)
        self.draw_edges(screen)
        self.draw_nodes(screen, fonts)
        self.draw_ui(screen, fonts)
        self.draw_buttons(screen, fonts, mouse_pos)
        draw_status(screen, "Visited " + str(list(self.visited)), fonts["small"])


def run_graph(screen, clock):
    fonts = create_fonts()
    graph = GraphVisualizer()
    graph.create_buttons()

    running = True

    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                back_button = draw_back_button(screen, fonts["small"], mouse_pos)
                if back_button.collidepoint(event.pos):
                    running = False

                for node, pos in graph.nodes.items():
                    x, y = pos
                    dx = event.pos[0] - x
                    dy = event.pos[1] - y

                    if dx * dx + dy * dy <= 26 * 26:
                        graph.set_start(node)

                if graph.buttons["bfs"].collidepoint(event.pos):
                    graph.start_bfs()

                if graph.buttons["dfs"].collidepoint(event.pos):
                    graph.start_dfs()

                if graph.buttons["step"].collidepoint(event.pos):
                    graph.step()

                if graph.buttons["reset"].collidepoint(event.pos):
                    graph.reset()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    graph.step()

        graph.draw_screen(screen, fonts, mouse_pos)
        draw_back_button(screen, fonts["small"], mouse_pos)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Graph Traversal Visualiser")
    clock = pygame.time.Clock()

    run_graph(screen, clock)

    pygame.quit()
