# menu.py
# Main menu screen for the DSA Explorer and Visualiser App

import pygame
from configure import *
from utilities import create_fonts, clear_screen, draw_title, draw_text, draw_button, draw_status


def run_menu(screen, clock, module_names):
    fonts = create_fonts()

    buttons = []
    start_y = 130

    for index, name in enumerate(module_names):
        x = (WIDTH - MENU_BUTTON_WIDTH) // 2
        y = start_y + index * (MENU_BUTTON_HEIGHT + MENU_BUTTON_GAP)
        rect = pygame.Rect(x, y, MENU_BUTTON_WIDTH, MENU_BUTTON_HEIGHT)
        buttons.append((name, rect))

    exit_rect = pygame.Rect(
        (WIDTH - MENU_BUTTON_WIDTH) // 2,
        start_y + len(module_names) * (MENU_BUTTON_HEIGHT + MENU_BUTTON_GAP) + 15,
        MENU_BUTTON_WIDTH,
        MENU_BUTTON_HEIGHT
    )

    running = True

    while running:
        mouse_pos = pygame.mouse.get_pos()

        clear_screen(screen)

        draw_title(screen, "DSA Explorer and Visualiser App", fonts["title"])

        draw_text(
            screen,
            "Select a module to explore data structures, algorithms, visualisations, and puzzles.",
            WIDTH // 2,
            88,
            fonts["small"],
            DARK_GREY,
            centre=True
        )

        for name, rect in buttons:
            draw_button(screen, rect, name, fonts["normal"], mouse_pos)

        draw_button(screen, exit_rect, "Exit", fonts["normal"], mouse_pos)

        draw_status(
            screen,
            "Mouse: select module | Each module returns to this menu | Week 13 demo-ready navigation",
            fonts["small"]
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "Exit"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "Exit"

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for name, rect in buttons:
                        if rect.collidepoint(event.pos):
                            return name

                    if exit_rect.collidepoint(event.pos):
                        return "Exit"

        pygame.display.flip()
        clock.tick(FPS)


# Allows testing menu.py before main.py and phase files are finished
if __name__ == "__main__":
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("DSA Explorer Menu Test")
    clock = pygame.time.Clock()

    test_modules = [
        "Stack and Queue",
        "Linked List",
        "Binary Search Tree",
        "Sorting Algorithms",
        "Graph Traversal",
        "Heap Visualiser",
        "Pathfinding Puzzle",
        "Event Queue Simulator",
        "Dynamic Programming Puzzle",
    ]

    selected = run_menu(screen, clock, test_modules)
    print("Selected:", selected)

    pygame.quit()
