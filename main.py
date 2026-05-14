# main.py
import pygame

from Phase_1 import stack_queue, linked_list, bst
from Phase_2 import sorting, graph, heap
from Phase_3 import pathfinding, event_queue, dynamic

from ui import *

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DSA Explorer")

clock = pygame.time.Clock()
fonts = create_fonts()

# Extra colours
BG = (245, 247, 251)
WHITE = (255, 255, 255)
SHADOW = (218, 225, 235)
DARK = (25, 32, 44)
MUTED = (105, 116, 135)

PURPLE = (120, 74, 220)
GREEN = (55, 165, 85)
BLUE = (45, 120, 220)

MODULES = {
    "Phase 1": {
        "colour": PURPLE,
        "items": [
            ("Stack & Queue", "Learn stack and queue operations", "≡", stack_queue.run_stack_queue),
            ("Linked List", "Explore node-based structures", "⛓", linked_list.run_linked_list),
            ("Binary Search Tree", "Visualise BST insert/search", "▲", bst.run_bst),
        ],
    },
    "Phase 2": {
        "colour": GREEN,
        "items": [
            ("Sorting", "Compare sorting algorithms", "↕", sorting.run_sorting),
            ("Graph", "Study BFS and DFS traversal", "⌬", graph.run_graph),
            ("Heap", "Understand priority queues", "♟", heap.run_heap),
        ],
    },
    "Phase 3": {
        "colour": BLUE,
        "items": [
            ("Pathfinding", "Find shortest paths visually", "▦", pathfinding.run_pathfinding),
            ("Event Queue", "Simulate event processing", "◷", event_queue.run_event_queue),
            ("Dynamic Programming", "Solve grid-based DP problems", "</>", dynamic.run_dynamic),
        ],
    },
}

COL_COUNT = 3
SIDE_PAD = 48
COL_GAP = 34

usable_width = WIDTH - (SIDE_PAD * 2) - (COL_GAP * (COL_COUNT - 1))
COL_W = usable_width // COL_COUNT

CARD_H = 132
CARD_GAP = 24

CONTENT_TOP = HEADER_H + 74

card_rects = {}


def col_left(index):
    return SIDE_PAD + index * (COL_W + COL_GAP)


for col_index, (phase, data) in enumerate(MODULES.items()):
    x = col_left(col_index)
    card_rects[phase] = []

    for row_index, item in enumerate(data["items"]):
        name, desc, icon, func = item
        y = CONTENT_TOP + 80 + row_index * (CARD_H + CARD_GAP)
        rect = pygame.Rect(x, y, COL_W, CARD_H)
        card_rects[phase].append((name, desc, icon, func, rect))


def draw_round_rect(surface, colour, rect, radius=16):
    pygame.draw.rect(surface, colour, rect, border_radius=radius)


def draw_shadow(surface, rect):
    shadow_rect = pygame.Rect(rect.x + 4, rect.y + 5, rect.w, rect.h)
    pygame.draw.rect(surface, SHADOW, shadow_rect, border_radius=18)


def draw_modern_header():
    pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, HEADER_H))
    pygame.draw.line(screen, (225, 230, 238), (0, HEADER_H), (WIDTH, HEADER_H), 1)

    draw_text(
        screen,
        "DSA Explorer",
        WIDTH // 2,
        HEADER_H // 2,
        fonts["heading"],
        DARK,
        centre=True,
    )


def draw_phase_heading(x, phase, colour):
    icon_box = pygame.Rect(x + 8, CONTENT_TOP, 52, 52)
    pygame.draw.rect(screen, WHITE, icon_box, border_radius=12)
    pygame.draw.rect(screen, (225, 230, 238), icon_box, 1, border_radius=12)

    draw_text(
        screen,
        "◆",
        icon_box.centerx,
        icon_box.centery,
        fonts["heading"],
        colour,
        centre=True,
    )

    draw_text(
        screen,
        phase,
        x + 76,
        CONTENT_TOP + 26,
        fonts["label"],
        DARK,
        centre=False,
    )

    pygame.draw.line(
        screen,
        colour,
        (x + 8, CONTENT_TOP + 64),
        (x + 150, CONTENT_TOP + 64),
        3,
    )


def draw_card(name, desc, icon, rect, colour, hover):
    if hover:
        rect = rect.move(0, -4)

    draw_shadow(screen, rect)

    fill = WHITE if not hover else (252, 253, 255)
    draw_round_rect(screen, fill, rect, 18)

    border_colour = colour if hover else (222, 228, 238)
    pygame.draw.rect(screen, border_colour, rect, 2 if hover else 1, border_radius=18)

    icon_rect = pygame.Rect(rect.x + 28, rect.y + 32, 68, 68)
    pygame.draw.rect(screen, (248, 250, 255), icon_rect, border_radius=14)
    pygame.draw.rect(screen, (225, 230, 238), icon_rect, 1, border_radius=14)

    draw_text(
        screen,
        icon,
        icon_rect.centerx,
        icon_rect.centery,
        fonts["heading"],
        colour,
        centre=True,
    )

    draw_text(
        screen,
        name,
        rect.x + 122,
        rect.y + 45,
        fonts["label"],
        DARK,
        centre=False,
    )

    draw_text(
        screen,
        desc,
        rect.x + 122,
        rect.y + 76,
        fonts["small"],
        MUTED,
        centre=False,
    )

    draw_text(
        screen,
        "›",
        rect.right - 32,
        rect.centery,
        fonts["heading"],
        colour,
        centre=True,
    )


def draw_cards(mouse_pos):
    for col_index, (phase, data) in enumerate(MODULES.items()):
        x = col_left(col_index)
        colour = data["colour"]

        draw_phase_heading(x, phase, colour)

        for name, desc, icon, func, rect in card_rects[phase]:
            hover = rect.collidepoint(mouse_pos)
            draw_card(name, desc, icon, rect, colour, hover)


def draw_background():
    screen.fill(BG)

    # subtle decorative dots
    dot_colour = (232, 236, 244)
    for x in range(12, 150, 14):
        for y in range(HEADER_H + 18, HEIGHT - 90, 14):
            pygame.draw.circle(screen, dot_colour, (x, y), 2)

    for x in range(WIDTH - 150, WIDTH - 12, 14):
        for y in range(HEADER_H + 18, HEIGHT - 90, 14):
            pygame.draw.circle(screen, dot_colour, (x, y), 2)


def draw_footer():
    pygame.draw.rect(screen, WHITE, (0, HEIGHT - 52, WIDTH, 52))
    pygame.draw.line(screen, (225, 230, 238), (0, HEIGHT - 52), (WIDTH, HEIGHT - 52), 1)

    draw_text(
        screen,
        "ⓘ",
        38,
        HEIGHT - 26,
        fonts["small"],
        MUTED,
        centre=True,
    )

    draw_text(
        screen,
        "Click a module to get started",
        68,
        HEIGHT - 26,
        fonts["small"],
        MUTED,
        centre=False,
    )


def draw_ui(mouse_pos):
    draw_background()
    draw_modern_header()
    draw_cards(mouse_pos)
    draw_footer()


running = True

while running:
    mouse_pos = pygame.mouse.get_pos()
    draw_ui(mouse_pos)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for phase in card_rects:
                for name, desc, icon, func, rect in card_rects[phase]:
                    if rect.collidepoint(event.pos):
                        func(screen, clock)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
