import pygame

pygame.init()

# ─────────────────────────────────────────────────────────────────
# SCREEN
# ─────────────────────────────────────────────────────────────────
WIDTH = 1100
HEIGHT = 720
FPS = 60

# ─────────────────────────────────────────────────────────────────
# COLOURS
# ─────────────────────────────────────────────────────────────────
BG_TOP = (248, 248, 248)
BG_BOTTOM = (236, 236, 236)

SURFACE_0 = (255, 255, 255)
SURFACE_1 = (250, 250, 250)
SURFACE_2 = (242, 242, 242)
SURFACE_3 = (230, 230, 230)

BORDER_SUBTLE = (222, 222, 222)
BORDER_DEFAULT = (200, 200, 200)
BORDER_STRONG = (175, 175, 175)

ACCENT = (90, 150, 255)
ACCENT_SOFT = (220, 35, 35)
ACCENT_HOVER = (255, 50, 50)

TEXT_1 = (25, 25, 25)
TEXT_2 = (85, 85, 85)
TEXT_3 = (130, 130, 130)

TEXT_ON_ACCENT = (255, 255, 255)

BTN_START = (34, 160, 90)
BTN_START_HOVER = (42, 185, 105)

BTN_DANGER = (210, 45, 50)
BTN_DANGER_HOVER = (230, 60, 65)

BTN_DEFAULT = (245, 245, 245)
BTN_DEFAULT_HOVER = (235, 235, 235)

BTN_GHOST_HOVER = (240, 240, 240)

NODE_BG = (255, 255, 255)
NODE_BG_HIGHLIGHT = (255, 242, 242)

NODE_BORDER = (210, 210, 210)
NODE_BORDER_HIGHLIGHT = ACCENT

# ─────────────────────────────────────────────────────────────────
# LEGACY ALIASES
# ─────────────────────────────────────────────────────────────────
PRIMARY = BTN_DEFAULT
PRIMARY_HOVER = BTN_DEFAULT_HOVER

BACKGROUND = BG_TOP
SURFACE = SURFACE_0

SUCCESS = BTN_START
DANGER = BTN_DANGER

TEXT = TEXT_2
DARK_GREY = TEXT_2

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

LIGHT_BLUE = (110, 170, 255)
LIGHT_GREY = (220, 220, 220)

BLUE = (90, 150, 255)
DARK_BLUE = (50, 95, 185)

GREEN = BTN_START
RED = BTN_DANGER

YELLOW = (245, 210, 70)
ORANGE = (240, 145, 55)
PURPLE = (170, 120, 255)

# ─────────────────────────────────────────────────────────────────
# LAYOUT
# ─────────────────────────────────────────────────────────────────
HEADER_H = 56
STATUS_H = 32

RADIUS = 10

MENU_BUTTON_WIDTH = 260
MENU_BUTTON_HEIGHT = 48
MENU_BUTTON_GAP = 12

NODE_WIDTH = 88
NODE_HEIGHT = 42
NODE_RADIUS = 24

VERTICAL_GAP = 12
HORIZONTAL_GAP = 44

# ─────────────────────────────────────────────────────────────────
# TYPOGRAPHY
# ─────────────────────────────────────────────────────────────────
TITLE_FONT_SIZE = 22
HEADING_FONT_SIZE = 16
NORMAL_FONT_SIZE = 15
SMALL_FONT_SIZE = 12

_SANS = [
    "Segoe UI",
    "SF Pro Display",
    "Helvetica Neue",
    "Arial",
    "Ubuntu",
    "Calibri",
    "Verdana"
]

_MONO = [
    "Consolas",
    "JetBrains Mono",
    "Courier New"
]


def _load_font(candidates, size, bold=False):

    for name in candidates:

        try:
            font = pygame.font.SysFont(
                name,
                size,
                bold=bold
            )

            if font:
                return font

        except Exception:
            pass

    return pygame.font.SysFont(
        None,
        size,
        bold=bold
    )


def create_fonts():

    return {
        "title": _load_font(
            _SANS,
            TITLE_FONT_SIZE,
            bold=True
        ),

        "heading": _load_font(
            _SANS,
            HEADING_FONT_SIZE,
            bold=True
        ),

        "normal": _load_font(
            _SANS,
            NORMAL_FONT_SIZE
        ),

        "small": _load_font(
            _SANS,
            SMALL_FONT_SIZE
        ),

        "label": _load_font(
            _SANS,
            SMALL_FONT_SIZE,
            bold=True
        ),

        "mono": _load_font(
            _MONO,
            NORMAL_FONT_SIZE
        )
    }

# ─────────────────────────────────────────────────────────────────
# BACKGROUND
# ─────────────────────────────────────────────────────────────────
_gradient_cache = None


def draw_background(screen):

    global _gradient_cache

    width, height = screen.get_size()

    if (
        _gradient_cache is None
        or _gradient_cache.get_size() != (width, height)
    ):

        surface = pygame.Surface(
            (width, height)
        )

        for y in range(height):

            t = y / height

            r = int(
                BG_TOP[0]
                + (BG_BOTTOM[0] - BG_TOP[0]) * t
            )

            g = int(
                BG_TOP[1]
                + (BG_BOTTOM[1] - BG_TOP[1]) * t
            )

            b = int(
                BG_TOP[2]
                + (BG_BOTTOM[2] - BG_TOP[2]) * t
            )

            pygame.draw.line(
                surface,
                (r, g, b),
                (0, y),
                (width, y)
            )

        _gradient_cache = surface

    screen.blit(
        _gradient_cache,
        (0, 0)
    )


def clear_screen(screen):

    draw_background(screen)

# ─────────────────────────────────────────────────────────────────
# TEXT
# ─────────────────────────────────────────────────────────────────
def draw_text(
    screen,
    text,
    x,
    y,
    font,
    colour=TEXT_1,
    centre=False
):

    surface = font.render(
        str(text),
        True,
        colour
    )

    rect = surface.get_rect()

    if centre:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    screen.blit(
        surface,
        rect
    )

    return rect


# ─────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────
def draw_header(
    screen,
    title,
    fonts,
    right_label=""
):

    width = screen.get_width()

    pygame.draw.rect(
        screen,
        SURFACE_0,
        (0, 0, width, HEADER_H)
    )

    pygame.draw.line(
        screen,
        BORDER_SUBTLE,
        (0, HEADER_H),
        (width, HEADER_H),
        1
    )


    draw_text(
        screen,
        title,
        WIDTH // 2,
        HEADER_H // 2,
        fonts["title"],
        TEXT_1,
        centre=True
    )

    if right_label:

        text_width = fonts["small"].size(
            right_label
        )[0]

        draw_text(
            screen,
            right_label,
            width - text_width - 20,
            HEADER_H // 2 - fonts["small"].get_height() // 2,
            fonts["small"],
            TEXT_3
        )

# ─────────────────────────────────────────────────────────────────
# STATUS BAR
# ─────────────────────────────────────────────────────────────────
def draw_status(
    screen,
    message,
    font
):

    width, height = screen.get_size()

    y = height - STATUS_H

    pygame.draw.rect(
        screen,
        SURFACE_0,
        (0, y, width, STATUS_H)
    )

    pygame.draw.line(
        screen,
        BORDER_SUBTLE,
        (0, y),
        (width, y),
        1
    )

    draw_text(
        screen,
        message,
        20,
        y + STATUS_H // 2 - font.get_height() // 2,
        font,
        TEXT_3
    )

# ─────────────────────────────────────────────────────────────────
# BUTTONS
# ─────────────────────────────────────────────────────────────────
def _button_colours(
    style,
    hover,
    active
):

    if not active:

        return (
            SURFACE_1,
            TEXT_3,
            BORDER_SUBTLE
        )

    styles = {

        "start": (
            BTN_START_HOVER if hover else BTN_START,
            TEXT_ON_ACCENT,
            BTN_START_HOVER if hover else BTN_START
        ),

        "danger": (
            BTN_DANGER_HOVER if hover else BTN_DANGER,
            TEXT_ON_ACCENT,
            BTN_DANGER_HOVER if hover else BTN_DANGER
        ),

        "accent": (
            ACCENT_HOVER if hover else ACCENT_SOFT,
            TEXT_ON_ACCENT,
            ACCENT_HOVER if hover else ACCENT_SOFT
        ),

        "neutral": (
            BTN_DEFAULT_HOVER if hover else BTN_DEFAULT,
            TEXT_1,
            BORDER_DEFAULT
        ),

        "ghost": (
            BTN_GHOST_HOVER if hover else SURFACE_0,
            TEXT_1,
            BORDER_DEFAULT
        )
    }

    return styles.get(
        style,
        styles["neutral"]
    )


def draw_button(
    screen,
    rect,
    text,
    font,
    mouse_pos=None,
    active=True,
    style="neutral"
):

    hover = bool(
        mouse_pos
        and rect.collidepoint(mouse_pos)
    )

    fill, text_colour, border = _button_colours(
        style,
        hover,
        active
    )

    pygame.draw.rect(
        screen,
        fill,
        rect,
        border_radius=RADIUS
    )

    pygame.draw.rect(
        screen,
        border,
        rect,
        1,
        border_radius=RADIUS
    )

    draw_text(
        screen,
        text,
        rect.centerx,
        rect.centery,
        font,
        text_colour,
        centre=True
    )


def draw_back_button(
    screen,
    font,
    mouse_pos=None
):

    rect = pygame.Rect(
        20,
        HEADER_H + 16,
        110,
        38
    )

    draw_button(
        screen,
        rect,
        "Return to Menu",
        font,
        mouse_pos,
        style="danger"
    )

    return rect

# ─────────────────────────────────────────────────────────────────
# INPUT BOX
# ─────────────────────────────────────────────────────────────────
def draw_input_box(
    screen,
    rect,
    text,
    font,
    active=False,
    mouse_pos=None
):

    hover = bool(
        mouse_pos
        and rect.collidepoint(mouse_pos)
    )

    if active:
        border = ACCENT
    elif hover:
        border = BORDER_DEFAULT
    else:
        border = BORDER_SUBTLE

    background = SURFACE_0

    pygame.draw.rect(
        screen,
        background,
        rect,
        border_radius=RADIUS
    )

    pygame.draw.rect(
        screen,
        border,
        rect,
        2 if active else 1,
        border_radius=RADIUS
    )

    cursor = ""

    if (
        active
        and (pygame.time.get_ticks() // 500) % 2 == 0
    ):
        cursor = "|"

    display = text + cursor

    draw_text(
        screen,
        display,
        rect.x + 12,
        rect.centery - font.get_height() // 2,
        font,
        TEXT_1 if text else TEXT_3
    )

# ─────────────────────────────────────────────────────────────────
# PANEL
# ─────────────────────────────────────────────────────────────────
def draw_panel(
    screen,
    rect,
    fill=None,
    border=True
):

    pygame.draw.rect(
        screen,
        fill or SURFACE_1,
        rect,
        border_radius=RADIUS
    )

    if border:

        pygame.draw.rect(
            screen,
            BORDER_SUBTLE,
            rect,
            1,
            border_radius=RADIUS
        )

# ─────────────────────────────────────────────────────────────────
# LABEL
# ─────────────────────────────────────────────────────────────────
def draw_label(
    screen,
    text,
    x,
    y,
    font,
    colour=TEXT_3
):

    draw_text(
        screen,
        text,
        x,
        y,
        font,
        colour
    )

# ─────────────────────────────────────────────────────────────────
# TREE / GRAPH NODE
# ─────────────────────────────────────────────────────────────────
def draw_node_rect(
    screen,
    x,
    y,
    value,
    font,
    highlight=False
):

    fill = (
        NODE_BG_HIGHLIGHT
        if highlight
        else NODE_BG
    )

    border = (
        NODE_BORDER_HIGHLIGHT
        if highlight
        else NODE_BORDER
    )

    rect = pygame.Rect(
        x,
        y,
        NODE_WIDTH,
        NODE_HEIGHT
    )

    pygame.draw.rect(
        screen,
        fill,
        rect,
        border_radius=RADIUS
    )

    pygame.draw.rect(
        screen,
        border,
        rect,
        1,
        border_radius=RADIUS
    )

    if highlight:

        top_bar = pygame.Rect(
            x + 2,
            y,
            NODE_WIDTH - 4,
            3
        )

        pygame.draw.rect(
            screen,
            ACCENT,
            top_bar,
            border_radius=2
        )

    draw_text(
        screen,
        value,
        rect.centerx,
        rect.centery,
        font,
        TEXT_1,
        centre=True
    )

    return rect

# ─────────────────────────────────────────────────────────────────
# ARROWS
# ─────────────────────────────────────────────────────────────────
def draw_arrow(
    screen,
    start_pos,
    end_pos,
    colour=BORDER_DEFAULT,
    width=2
):

    pygame.draw.line(
        screen,
        colour,
        start_pos,
        end_pos,
        width
    )

    x1, y1 = start_pos
    x2, y2 = end_pos

    direction = pygame.math.Vector2(
        x1 - x2,
        y1 - y2
    )

    if direction.length() == 0:
        return

    direction = direction.normalize()

    tip = pygame.math.Vector2(
        x2,
        y2
    )

    left = tip + direction.rotate(28) * 10
    right = tip + direction.rotate(-28) * 10

    pygame.draw.polygon(
        screen,
        colour,
        [
            (x2, y2),
            left,
            right
        ]
    )

# ─────────────────────────────────────────────────────────────────
# MENU STYLE
# ─────────────────────────────────────────────────────────────────
PHASE_COLOURS = {
    "Phase 1": (90, 150, 255),
    "Phase 2": (34, 160, 90),
    "Phase 3": (170, 120, 255),
}

MENU_COL_COUNT = 3
MENU_SIDE_PAD = 36
MENU_COL_GAP = 22

MENU_SEC_H = 42
MENU_CARD_H = 150
MENU_CARD_GAP = 16

MENU_CARD_RADIUS = 16
MENU_SECTION_RADIUS = 18
MENU_ICON_RADIUS = 14

MENU_SHADOW_COLOUR = (215, 215, 215)
MENU_CARD_FILL = (255, 255, 255)
MENU_CARD_HOVER_FILL = (248, 250, 255)

# ─────────────────────────────────────────────────────────────────
# MENU CARDS
# ─────────────────────────────────────────────────────────────────
def draw_menu_shadow(screen, rect):
    shadow = pygame.Rect(
        rect.x + 3,
        rect.y + 4,
        rect.w,
        rect.h
    )

    pygame.draw.rect(
        screen,
        MENU_SHADOW_COLOUR,
        shadow,
        border_radius=MENU_CARD_RADIUS
    )


def draw_menu_section_label(screen, x, y, width, label, colour, fonts):
    pill = pygame.Rect(
        x,
        y,
        width,
        MENU_SEC_H
    )

    pygame.draw.rect(
        screen,
        SURFACE_0,
        pill,
        border_radius=MENU_SECTION_RADIUS
    )

    pygame.draw.rect(
        screen,
        BORDER_SUBTLE,
        pill,
        1,
        border_radius=MENU_SECTION_RADIUS
    )

    dot = pygame.Rect(
        pill.x + 18,
        pill.centery - 5,
        10,
        10
    )

    pygame.draw.ellipse(
        screen,
        colour,
        dot
    )

    draw_text(
        screen,
        label,
        pill.centerx,
        pill.centery,
        fonts["heading"],
        TEXT_1,
        centre=True
    )


def draw_menu_card(screen, name, desc, icon, rect, colour, mouse_pos, fonts):
    hover = rect.collidepoint(mouse_pos)

    draw_menu_shadow(screen, rect)

    fill = MENU_CARD_HOVER_FILL if hover else MENU_CARD_FILL
    border = colour if hover else BORDER_SUBTLE
    border_width = 2 if hover else 1

    pygame.draw.rect(
        screen,
        fill,
        rect,
        border_radius=MENU_CARD_RADIUS
    )

    pygame.draw.rect(
        screen,
        border,
        rect,
        border_width,
        border_radius=MENU_CARD_RADIUS
    )

    icon_box = pygame.Rect(
        rect.centerx - 23,
        rect.y + 24,
        46,
        46
    )

    pygame.draw.rect(
        screen,
        colour,
        icon_box,
        border_radius=MENU_ICON_RADIUS
    )

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
