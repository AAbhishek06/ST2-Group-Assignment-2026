# utilities.py
# This utility.py file has all of the drawing elements that other python files will import as necessary 

import pygame
from configure import *


def create_fonts():
    return {
        "title": pygame.font.SysFont(FONT_NAME, TITLE_FONT_SIZE),
        "heading": pygame.font.SysFont(FONT_NAME, HEADING_FONT_SIZE),
        "normal": pygame.font.SysFont(FONT_NAME, NORMAL_FONT_SIZE),
        "small": pygame.font.SysFont(FONT_NAME, SMALL_FONT_SIZE),
    }


def draw_text(screen, text, x, y, font, colour=BLACK, centre=False):
    text_surface = font.render(str(text), True, colour)
    text_rect = text_surface.get_rect()

    if centre:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)

    screen.blit(text_surface, text_rect)
    return text_rect


def draw_title(screen, title, font):
    draw_text(screen, title, WIDTH // 2, TITLE_Y, font, DARK_BLUE, centre=True)


def draw_status(screen, message, font):
    pygame.draw.rect(screen, LIGHT_GREY, (0, HEIGHT - 45, WIDTH, 45))
    draw_text(screen, message, 20, HEIGHT - 32, font, DARK_GREY)


def draw_button(screen, rect, text, font, mouse_pos=None, active=True):
    if not active:
        colour = LIGHT_GREY
        text_colour = DARK_GREY
    elif mouse_pos and rect.collidepoint(mouse_pos):
        colour = DARK_BLUE
        text_colour = WHITE
    else:
        colour = BLUE
        text_colour = WHITE

    pygame.draw.rect(screen, colour, rect, border_radius=8)
    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=8)
    draw_text(screen, text, rect.centerx, rect.centery, font, text_colour, centre=True)


def draw_back_button(screen, font, mouse_pos=None):
    rect = pygame.Rect(20, 20, 150, 42)
    draw_button(screen, rect, "Return to Menu", font, mouse_pos)
    return rect


def draw_node_rect(screen, x, y, value, font, highlight=False):
    fill_colour = YELLOW if highlight else LIGHT_BLUE
    outline_colour = RED if highlight else BLACK

    rect = pygame.Rect(x, y, NODE_WIDTH, NODE_HEIGHT)
    pygame.draw.rect(screen, fill_colour, rect, border_radius=5)
    pygame.draw.rect(screen, outline_colour, rect, 2, border_radius=5)

    draw_text(screen, value, rect.centerx, rect.centery, font, BLACK, centre=True)
    return rect


def draw_arrow(screen, start_pos, end_pos, colour=BLACK, width=2):
    pygame.draw.line(screen, colour, start_pos, end_pos, width)

    # Simple arrow head
    x1, y1 = start_pos
    x2, y2 = end_pos

    angle = pygame.math.Vector2(x1 - x2, y1 - y2).angle_to(pygame.math.Vector2(1, 0))
    direction = pygame.math.Vector2(x1 - x2, y1 - y2).normalize() if start_pos != end_pos else pygame.math.Vector2(1, 0)

    left = pygame.math.Vector2(x2, y2) + direction.rotate(30) * 12
    right = pygame.math.Vector2(x2, y2) + direction.rotate(-30) * 12

    pygame.draw.polygon(screen, colour, [(x2, y2), left, right])


def clear_screen(screen):
    screen.fill(WHITE)
