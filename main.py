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
        ("Stack & Queue", stack_queue.run_stack_queue),
        ("Linked List", linked_list.run_linked_list),
        ("Binary Search Tree", bst.run_bst),
    ],
    "Phase 2": [
        ("Sorting", sorting.run_sorting),
        ("Graph", graph.run_graph),
        ("Heap", heap.run_heap),
    ],
    "Phase 3": [
        ("Pathfinding", pathfinding.run_pathfinding),
        ("Event Queue", event_queue.run_event_queue),
        ("Dynamic Programming", dynamic.run_dynamic),
    ],
}

COL_COUNT = 3
SIDE_PAD = 32
COL_GAP = 16

usable_width = WIDTH - (SIDE_PAD * 2) - (COL_GAP * (COL_COUNT - 1))
COL_W = usable_width // COL_COUNT

SEC_H = 36
CARD_H = 156
CARD_GAP = 8

CONTENT_TOP = HEADER_H + 32


def col_left(index):
    return SIDE_PAD + index * (COL_W + COL_GAP)


card_rects = {}

for col_index, (phase, items) in enumerate(MODULES.items()):
    x = col_left(col_index)

    card_rects[phase] = []

    for row_index, (name, func) in enumerate(items):
        y = CONTENT_TOP + SEC_H + 12 + row_index * (CARD_H + CARD_GAP)

        rect = pygame.Rect(x, y, COL_W, CARD_H)

        card_rects[phase].append((name, func, rect))


def draw_section_label(x, label):
    draw_text(
        screen,
        label,
        x,
        CONTENT_TOP + (SEC_H // 2),
        fonts["label"],
        TEXT_3,
        centre=True
    )



def draw_cards(mouse_pos):
    for col_index, (phase, items) in enumerate(MODULES.items()):
        x = col_left(col_index)

        draw_section_label(x + COL_W // 2, phase)

        for name, func, rect in card_rects[phase]:

            hover = rect.collidepoint(mouse_pos)

            fill = SURFACE_2 if hover else SURFACE_1

            pygame.draw.rect(
                screen,
                fill,
                rect,
                border_radius=10
            )

            border = BORDER_DEFAULT if hover else BORDER_SUBTLE

            pygame.draw.rect(
                screen,
                border,
                rect,
                1,
                border_radius=10
            )

            text_color = TEXT_1 if hover else TEXT_2

            draw_text(
                screen,
                name,
                rect.x + 20,
                rect.centery,
                fonts["normal"],
                text_color,
                centre=False
            )

            if hover:
                draw_text(
                    screen,
                    "›",
                    rect.right - 20,
                    rect.centery,
                    fonts["heading"],
                    ACCENT,
                    centre=True
                )


def draw_ui(mouse_pos):

    clear_screen(screen)

    draw_header(screen, "DSA Explorer", fonts)

    draw_cards(mouse_pos)

    draw_status(screen, "Click a module", fonts["small"])


running = True

while running:

    mouse_pos = pygame.mouse.get_pos()

    draw_ui(mouse_pos)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:

            for phase in card_rects:

                for name, func, rect in card_rects[phase]:

                    if rect.collidepoint(event.pos):
                        func(screen, clock)

    pygame.display.flip()

    clock.tick(FPS)

pygame.quit()
