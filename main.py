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

usable_width = WIDTH - (MENU_SIDE_PAD * 2) - (MENU_COL_GAP * (MENU_COL_COUNT - 1))
COL_W = usable_width // MENU_COL_COUNT

CONTENT_TOP = HEADER_H + 42


def col_left(index):
    return MENU_SIDE_PAD + index * (COL_W + MENU_COL_GAP)


card_rects = {}

for col_index, (phase, items) in enumerate(MODULES.items()):
    x = col_left(col_index)
    card_rects[phase] = []

    for row_index, (name, desc, icon, func) in enumerate(items):
        y = CONTENT_TOP + MENU_SEC_H + 14 + row_index * (MENU_CARD_H + MENU_CARD_GAP)
        rect = pygame.Rect(x, y, COL_W, MENU_CARD_H)
        card_rects[phase].append((name, desc, icon, func, rect))


def draw_cards(mouse_pos):
    for col_index, (phase, items) in enumerate(MODULES.items()):
        x = col_left(col_index)
        colour = PHASE_COLOURS[phase]

        draw_menu_section_label(screen, x, CONTENT_TOP, COL_W, phase, colour, fonts)

        for name, desc, icon, func, rect in card_rects[phase]:
            draw_menu_card(screen, name, desc, icon, rect, colour, mouse_pos, fonts)


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
