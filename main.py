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

MODULES = {
    "Phase 1": [
        ("Stack & Queue", "Push, pop, enqueue and dequeue", "1.1", stack_queue.run_stack_queue),
        ("Linked List", "Insert, delete and traverse nodes", "1.2", linked_list.run_linked_list),
        ("Binary Search Tree", "Insert, search and visualise BST", "1.3", bst.run_bst),
    ],
    "Phase 2": [
        ("Sorting", "Bubble, selection and merge sort", "2.1", sorting.run_sorting),
        ("Graph", "BFS and DFS traversal", "2.2", graph.run_graph),
        ("Heap", "Insert and extract heap values", "2.3", heap.run_heap),
    ],
    "Phase 3": [
        ("Pathfinding", "Find paths through grids", "3.1", pathfinding.run_pathfinding),
        ("Event Queue", "Process events in order", "3.2", event_queue.run_event_queue),
        ("Dynamic Programming", "Grid paths and reconstruction", "3.3", dynamic.run_dynamic),
    ],
}

PHASE_COLOURS = {
    "Phase 1": (90, 150, 255),
    "Phase 2": (34, 160, 90),
    "Phase 3": (170, 120, 255),
}

COL_COUNT = 3
SIDE_PAD = 36
COL_GAP = 22

usable_width = WIDTH - (SIDE_PAD * 2) - (COL_GAP * (COL_COUNT - 1))
COL_W = usable_width // COL_COUNT

SEC_H = 42
CARD_H = 150
CARD_GAP = 16

CONTENT_TOP = HEADER_H + 42


def col_left(index):
    return SIDE_PAD + index * (COL_W + COL_GAP)


card_rects = {}

for col_index, (phase, items) in enumerate(MODULES.items()):
    x = col_left(col_index)
    card_rects[phase] = []

    for row_index, (name, desc, icon, func) in enumerate(items):
        y = CONTENT_TOP + SEC_H + 14 + row_index * (CARD_H + CARD_GAP)
        rect = pygame.Rect(x, y, COL_W, CARD_H)
        card_rects[phase].append((name, desc, icon, func, rect))


def draw_shadow(rect):
    shadow = pygame.Rect(rect.x + 3, rect.y + 4, rect.w, rect.h)
    pygame.draw.rect(screen, (215, 215, 215), shadow, border_radius=16)


def draw_section_label(x, y, label, colour):
    pill = pygame.Rect(x, y, COL_W, SEC_H)

    pygame.draw.rect(screen, SURFACE_0, pill, border_radius=18)
    pygame.draw.rect(screen, BORDER_SUBTLE, pill, 1, border_radius=18)

    dot = pygame.Rect(pill.x + 18, pill.centery - 5, 10, 10)
    pygame.draw.ellipse(screen, colour, dot)

    draw_text(
        screen,
        label,
        pill.centerx,
        pill.centery,
        fonts["heading"],
        TEXT_1,
        centre=True
    )


def draw_card(name, desc, icon, rect, colour, mouse_pos):
    hover = rect.collidepoint(mouse_pos)

    draw_shadow(rect)

    fill = (255, 255, 255) if not hover else (248, 250, 255)
    border = colour if hover else BORDER_SUBTLE

    pygame.draw.rect(screen, fill, rect, border_radius=16)
    pygame.draw.rect(screen, border, rect, 2 if hover else 1, border_radius=16)

    icon_box = pygame.Rect(rect.centerx - 23, rect.y + 24, 46, 46)
    pygame.draw.rect(screen, colour, icon_box, border_radius=14)

    draw_text(
        screen,
        icon,
        icon_box.centerx,
        icon_box.centery,
        fonts["heading"],
        WHITE,
        centre=True
    )

    draw_text(
        screen,
        name,
        rect.centerx,
        rect.y + 88,
        fonts["heading"],
        TEXT_1,
        centre=True
    )

    draw_text(
        screen,
        desc,
        rect.centerx,
        rect.y + 116,
        fonts["small"],
        TEXT_3,
        centre=True
    )

    if hover:
        draw_text(
            screen,
            "›",
            rect.right - 30,
            rect.centery,
            fonts["title"],
            colour,
            centre=True
        )


def draw_cards(mouse_pos):
    for col_index, (phase, items) in enumerate(MODULES.items()):
        x = col_left(col_index)
        colour = PHASE_COLOURS[phase]

        draw_section_label(x, CONTENT_TOP, phase, colour)

        for name, desc, icon, func, rect in card_rects[phase]:
            draw_card(name, desc, icon, rect, colour, mouse_pos)


def draw_ui(mouse_pos):
    clear_screen(screen)

    draw_header(screen, "DSA Explorer", fonts)

    draw_cards(mouse_pos)

    draw_status(screen, "Choose a module to start learning.", fonts["small"])


running = True

while running:
    mouse_pos = pygame.mouse.get_pos()
    draw_ui(mouse_pos)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            for phase in card_rects:
                for name, desc, icon, func, rect in card_rects[phase]:
                    if rect.collidepoint(event.pos):
                        func(screen, clock)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
