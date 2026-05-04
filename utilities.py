# utilities.py
import pygame
from configure import *

pygame.init()

# ---------- Colour System ----------
PRIMARY         = (33, 33, 33)
PRIMARY_HOVER   = (66, 66, 66)
ACCENT          = (158, 158, 158)

# Layout
BACKGROUND      = (180, 180, 180)
SURFACE         = (30, 30, 30)

# Typography
TEXT_PRIMARY    = (245, 245, 245)
TEXT_SECONDARY  = (170, 170, 170)

# UI Elements
BORDER          = (55, 55, 55)

SUCCESS         = (140, 140, 140)
WARNING         = (100, 100, 100)
DANGER          = (200, 200, 200)

# Node Specifics
NODE_FILL       = (45, 45, 45)
NODE_HIGHLIGHT  = (80, 80, 80)
# ---------- Fonts ----------
def create_fonts():
    return {
        "title": pygame.font.SysFont("Verdana", TITLE_FONT_SIZE, bold=True),
        "heading": pygame.font.SysFont("Verdana", HEADING_FONT_SIZE, bold=True),
        "normal": pygame.font.SysFont("Verdana", NORMAL_FONT_SIZE),
        "small": pygame.font.SysFont("Verdana", SMALL_FONT_SIZE),
    }

# ---------- Text ----------
def draw_text(screen, text, x, y, font, colour=TEXT_PRIMARY, centre=False):
    surface = font.render(str(text), True, colour)
    rect = surface.get_rect()

    if centre:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    screen.blit(surface, rect)
    return rect

def draw_title(screen, title, font):
    draw_text(screen, title, WIDTH // 2, TITLE_Y, font, PRIMARY, centre=True)

# ---------- Status Bar ----------
def draw_status(screen, message, font):
    pygame.draw.rect(screen, SURFACE, (0, HEIGHT - 50, WIDTH, 50))
    pygame.draw.line(screen, BORDER, (0, HEIGHT - 50), (WIDTH, HEIGHT - 50), 1)
    draw_text(screen, message, 20, HEIGHT - 32, font, TEXT_SECONDARY)

# ---------- Buttons ----------
def draw_button(screen, rect, text, font, mouse_pos=None, active=True):
    if not active:
        colour = BORDER
        text_colour = TEXT_SECONDARY
    elif mouse_pos and rect.collidepoint(mouse_pos):
        colour = PRIMARY_HOVER
        text_colour = (255, 255, 255)
    else:
        colour = PRIMARY
        text_colour = (255, 255, 255)

    pygame.draw.rect(screen, colour, rect, border_radius=14)
    draw_text(screen, text, rect.centerx, rect.centery, font, text_colour, centre=True)

def draw_back_button(screen, font, mouse_pos=None):
    rect = pygame.Rect(20, 20, 180, 45)
    draw_button(screen, rect, "Back to Menu", font, mouse_pos)
    return rect

# ---------- Input Box ----------
def draw_input_box(screen, rect, text, font, active=False, mouse_pos=None):
    if active:
        border_colour = PRIMARY
    elif mouse_pos and rect.collidepoint(mouse_pos):
        border_colour = PRIMARY_HOVER
    else:
        border_colour = BORDER

    pygame.draw.rect(screen, SURFACE, rect, border_radius=14)
    pygame.draw.rect(screen, border_colour, rect, 2, border_radius=14)

    draw_text(screen, text, rect.x + 12, rect.centery, font, TEXT_PRIMARY)

# ---------- Nodes ----------
def draw_node_rect(screen, x, y, value, font, highlight=False):
    fill = NODE_HIGHLIGHT if highlight else NODE_FILL
    outline = PRIMARY if highlight else BORDER

    rect = pygame.Rect(x, y, NODE_WIDTH, NODE_HEIGHT)

    pygame.draw.rect(screen, fill, rect, border_radius=10)
    pygame.draw.rect(screen, outline, rect, 2, border_radius=10)

    draw_text(screen, value, rect.centerx, rect.centery, font, TEXT_PRIMARY, centre=True)
    return rect

# ---------- Arrows ----------
def draw_arrow(screen, start_pos, end_pos, colour=TEXT_PRIMARY, width=2):
    pygame.draw.line(screen, colour, start_pos, end_pos, width)

    x1, y1 = start_pos
    x2, y2 = end_pos

    direction = pygame.math.Vector2(x1 - x2, y1 - y2)

    if direction.length() == 0:
        return

    direction = direction.normalize()

    left = pygame.math.Vector2(x2, y2) + direction.rotate(30) * 10
    right = pygame.math.Vector2(x2, y2) + direction.rotate(-30) * 10

    pygame.draw.polygon(screen, colour, [(x2, y2), left, right])

# ---------- Screen ----------
def clear_screen(screen):
    screen.fill(BACKGROUND)
