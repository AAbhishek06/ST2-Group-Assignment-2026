# Imports
import pygame

from Phase_1 import stack_queue, linked_list, bst
from Phase_2 import sorting, graph, heap
from Phase_3 import pathfinding, event_queue, dynamic
from ui import *

pygame.init()

# Setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DSA Explorer")
clock = pygame.time.Clock()
fonts = create_fonts()

# Modules
MODULES = {
    "Phase 1": [
        ("Stack & Queue", "Learn how LIFO and FIFO work", "1.1", stack_queue.run_stack_queue),
        ("Linked List", "Learn how Linked lists work", "1.2", linked_list.run_linked_list),
        ("Binary Search Tree", "Learn how Binary Search Trees work", "1.3", bst.run_bst),
    ],
    "Phase 2": [
        ("Sorting", "Learn how different sorting algorithms work", "2.1", sorting.run_sorting),
        ("Graph", "Learn how BFS and DFS work", "2.2", graph.run_graph),
        ("Heap", "Learn how inserting and extracting work", "2.3", heap.run_heap),
    ],
    "Phase 3": [
        ("Pathfinding", "Learn how pathfinding with obstacles work", "3.1", pathfinding.run_pathfinding),
        ("Event Queue", "Learn how event process and orders work", "3.2", event_queue.run_event_queue),
        ("Dynamic Programming", "Learn how dynamic pathfinding work", "3.3", dynamic.run_dynamic),
    ],
}

# Layout
CONTENT_TOP = HEADER_H + 42
COL_W = (
    WIDTH
    - (MENU_SIDE_PAD * 2)
    - (MENU_COL_GAP * (MENU_COL_COUNT - 1))
) // MENU_COL_COUNT


def col_left(index):
    return MENU_SIDE_PAD + index * (COL_W + MENU_COL_GAP)


# Cards
card_rects = {
    phase: [
        (
            name,
            desc,
            icon,
            func,
            pygame.Rect(
                col_left(col_index),
                CONTENT_TOP + MENU_SEC_H + 14 + row_index * (MENU_CARD_H + MENU_CARD_GAP),
                COL_W,
                MENU_CARD_H
            )
        )
        for row_index, (name, desc, icon, func) in enumerate(items)
    ]
    for col_index, (phase, items) in enumerate(MODULES.items())
}


def draw_cards(mouse_pos):
    for col_index, phase in enumerate(MODULES):
        x = col_left(col_index)
        colour = PHASE_COLOURS[phase]

        draw_menu_section_label(
            screen,
            x,
            CONTENT_TOP,
            COL_W,
            phase,
            colour,
            fonts
        )

        for name, desc, icon, func, rect in card_rects[phase]:
            draw_menu_card(
                screen,
                name,
                desc,
                icon,
                rect,
                colour,
                mouse_pos,
                fonts
            )


# Main screen
def draw_ui(mouse_pos):
    clear_screen(screen)
    draw_header(screen, "DSA Explorer", fonts)
    draw_cards(mouse_pos)
    draw_status(screen, "Choose a module to start learning.", fonts["small"])


# Main loop
running = True

while running:
    mouse_pos = pygame.mouse.get_pos()
    draw_ui(mouse_pos)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            for cards in card_rects.values():
                for name, desc, icon, func, rect in cards:
                    if rect.collidepoint(event.pos):
                        func(screen, clock)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()