#menu.py
import pygame

from Phase_1 import stack_queue
from Phase_1 import linked_list
from Phase_1 import bst


from Phase_2 import sorting
from Phase_2 import graph
from Phase_2 import heap

from Phase_3 import pathfinding
from Phase_3 import event_queue
from Phase_3 import dynamic

from configure import *
from utilities import *

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DSA Explorer and Visualiser App")

clock = pygame.time.Clock()
fonts = create_fonts()

phase_modules = {
    "Phase 1": [
        ("Stack Queue", stack_queue.run_stack_queue),
        ("Linked List", linked_list.run_linked_list),
        ("BST", bst.run_bst),
    ],
    "Phase 2": [
        ("Sorting", sorting.run_sorting),
        ("Graph", graph.run_graph),
        ("Heap", heap.run_heap),
    ],
    "Phase 3": [
        ("Pathfinding", pathfinding.run_pathfinding),
        ("Event Queue", event_queue.run_event_queue),
        ("Dynamic", dynamic.run_dynamic),
    ]
}

columns = {
    "Phase 1": WIDTH // 6,
    "Phase 2": WIDTH // 2,
    "Phase 3": (WIDTH * 5) // 6,
}

start_y = 180
gap = 80

button_width = 240
button_height = 50

phase_buttons = {}

for phase, items in phase_modules.items():
    x = columns[phase]
    y = start_y

    phase_buttons[phase] = []

    for name, _ in items:
        rect = pygame.Rect(x - button_width // 2, y, button_width, button_height)
        phase_buttons[phase].append((name, rect))
        y += gap

running = True

while running:
    mouse_pos = pygame.mouse.get_pos()

    clear_screen(screen)

    draw_title(screen, "DSA Explorer and Visualiser App", fonts["title"])

    draw_text(screen, "Phase 1", columns["Phase 1"], 130, fonts["heading"], TEXT, centre=True)

    draw_text(screen, "Phase 2", columns["Phase 2"], 130, fonts["heading"], TEXT, centre=True)

    draw_text(screen, "Phase 3", columns["Phase 3"], 130, fonts["heading"], TEXT, centre=True)

    for phase, buttons in phase_buttons.items():
        for name, rect in buttons:
            draw_button(screen, rect, name, fonts["normal"], mouse_pos)

    draw_status(screen, "Select a module to launch", fonts["small"])

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            for phase, items in phase_modules.items():
                for i, (name, func) in enumerate(items):
                    rect = phase_buttons[phase][i][1]

                    if rect.collidepoint(event.pos):
                        func(screen, clock)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
