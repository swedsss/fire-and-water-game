import os
from pygame import Color

SPRITE_SIZE = 32
MAX_LEVEL_SIZE = 25

TITLE = 'ОГОНЬ и ВОДА'
SCREEN_WIDTH = MAX_LEVEL_SIZE * SPRITE_SIZE
SCREEN_HEIGHT = MAX_LEVEL_SIZE * SPRITE_SIZE

TURBO_MODE = False

FPS = 30 if not TURBO_MODE else 100
PLAYER_STEP = SPRITE_SIZE // (8 if not TURBO_MODE else 4)
PLAYER_ANIMATION_DURATION = 70 if not TURBO_MODE else 10

# Константы цветов
BLACK = Color('black')
WHITE = Color('white')
GREEN = Color('green')

# Константы папок и путей к ним
DIR_NAME_LEVELS = 'levels'
DIR_NAME_IMAGES = 'img'

CURRENT_DIR = os.path.dirname(__file__)
LEVELS_DIR = os.path.join(CURRENT_DIR, DIR_NAME_LEVELS)
IMG_DIR = os.path.join(CURRENT_DIR, DIR_NAME_IMAGES)

# Константы имён файлов
CSV_FILE_SAVE = "save.csv"

SPRITE_FILE_WALLS = "walls.png"
SPRITE_FILE_FLOOR = "floor.png"
SPRITE_FILE_LAVA = "lava.png"
SPRITE_FILE_RIVER = "river.png"
SPRITE_FILE_ACID = "acid.png"
SPRITE_FILE_FIRE_PLAYER = "fire_player.png"
SPRITE_FILE_WATER_PLAYER = "water_player.png"
SPRITE_FILE_ELEMENTS = "elements.png"
SPRITE_FILE_LEVEL_ICONS = "level_icons.png"

IMG_FILE_TITLE = "title.png"

# Константы обозначений блоков и элементов на уровне
LEVEL_BLOCK_EMPTY = " "
LEVEL_BLOCK_FLOOR = "."
LEVEL_BLOCK_WALL = "#"
LEVEL_BLOCK_LAVA = "L"
LEVEL_BLOCK_RIVER = "R"
LEVEL_BLOCK_ACID = "A"

LEVEL_PLAYER_FIRE = "f"
LEVEL_PLAYER_WATER = "w"

LEVEL_ELEM_RUBY = "<"
LEVEL_ELEM_AQUAMARINE = ">"
LEVEL_ELEM_FIRE_EXIT = "F"
LEVEL_ELEM_WATER_EXIT = "W"
LEVEL_ELEM_DOORBUTTON_1 = "b"
LEVEL_ELEM_DOORBUTTON_2 = "B"
LEVEL_ELEM_DOOR_1 = "d"
LEVEL_ELEM_DOOR_2 = "D"
LEVEL_ELEM_INPUT_PORTAL_1 = "i"
LEVEL_ELEM_INPUT_PORTAL_2 = "I"
LEVEL_ELEM_OUTPUT_PORTAL_1 = "o"
LEVEL_ELEM_OUTPUT_PORTAL_2 = "O"
LEVEL_ELEM_PORTAL_SWITCH_1 = "y"
LEVEL_ELEM_PORTAL_SWITCH_2 = "Y"

# Константы для цветов на начальном и конечном экранах
SCREEN_BG_COLOR1 = "bg_color1"
SCREEN_BG_COLOR2 = "bg_color2"
SCREEN_SHADOW_COLOR = "shadow_color"
SCREEN_TEXT_COLOR = "text_color"

SCREEN_COLORS_DICT = {
    SCREEN_BG_COLOR1: Color(47, 72, 78),
    SCREEN_BG_COLOR2: Color(54, 54, 54),
    SCREEN_SHADOW_COLOR: Color(27, 38, 50),
    SCREEN_TEXT_COLOR: Color(56, 105, 117)
}
