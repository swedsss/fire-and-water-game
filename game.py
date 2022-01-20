import sys
import os
import pygame
import csv
from typing import Optional, Union

SPRITE_SIZE = 32
MAX_LEVEL_SIZE = 25

TITLE = 'ОГОНЬ и ВОДА'
SCREEN_WIDTH = MAX_LEVEL_SIZE * SPRITE_SIZE
SCREEN_HEIGHT = MAX_LEVEL_SIZE * SPRITE_SIZE

FPS = 30

BLACK = pygame.Color('black')
WHITE = pygame.Color('white')

DIR_NAME_LEVELS = 'levels'
DIR_NAME_IMAGES = 'img'

CURRENT_DIR = os.path.dirname(__file__)
LEVELS_DIR = os.path.join(CURRENT_DIR, DIR_NAME_LEVELS)
IMG_DIR = os.path.join(CURRENT_DIR, DIR_NAME_IMAGES)

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

PLAYER_STEP = SPRITE_SIZE // 8
PlAYER_ANIMATION_DURATION = 70

SCREEN_BG_COLOR1 = "bg_color1"
SCREEN_BG_COLOR2 = "bg_color2"
SCREEN_SHADOW_COLOR = "shadow_color"
SCREEN_TEXT_COLOR = "text_color"

SCREEN_COLORS_DICT = {
    SCREEN_BG_COLOR1: pygame.Color(47, 72, 78),
    SCREEN_BG_COLOR2: pygame.Color(54, 54, 54),
    SCREEN_SHADOW_COLOR: pygame.Color(27, 38, 50),
    SCREEN_TEXT_COLOR: pygame.Color(56, 105, 117)
}


def display_text(surface, text, size, color, x, y):
    """Отображение текста"""
    font = pygame.font.SysFont("sans-serif", size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    surface.blit(text_surface, text_rect)
    return text_surface


class SpriteSheet:
    """Набор спрайтов"""

    def __init__(self, file_name):
        self.sprite_sheet = pygame.image.load(file_name).convert()

    def get_image(self, x, y, width, height):
        image = pygame.Surface((width, height)).convert()
        image.blit(self.sprite_sheet, (0, 0), pygame.Rect(x, y, width, height))
        image.set_colorkey(BLACK)
        return pygame.transform.scale(image, (width, height))

    def get_cell_image(self, col, row, width=SPRITE_SIZE, height=SPRITE_SIZE):
        return self.get_image(col * width, row * height, width, height)


class EdgeSpriteSheet(SpriteSheet):
    """Класс для набора спрайтов, которые расположены с учётом соседних спрайтов"""
    TILE_COORDS_DICT = {
        4: (0, 0), 6: (1, 0), 14: (2, 0), 12: (3, 0),
        5: (0, 1), 7: (1, 1), 15: (2, 1), 13: (3, 1),
        1: (0, 2), 3: (1, 2), 11: (2, 2), 9: (3, 2),
        0: (0, 3), 2: (1, 3), 10: (2, 3), 8: (3, 3)
    }

    def get_image_by_index(self, index):
        if index < 0 or index >= 16:
            raise ValueError("Индекс должен быть в пределах от 0 до 15 включительно!")
        col, row = self.TILE_COORDS_DICT[index]
        return self.get_cell_image(col, row)


class BaseSprite(pygame.sprite.Sprite):
    """Общий класс для всех спрайтов на экране"""

    col_offset = 0
    row_offset = 0

    @classmethod
    def reset_offset(cls):
        cls.col_offset = 0
        cls.row_offset = 0

    @classmethod
    def set_offset(cls, col_offset, row_offset):
        cls.col_offset = col_offset
        cls.row_offset = row_offset

    @staticmethod
    def get_empty_image(width=SPRITE_SIZE, height=SPRITE_SIZE):
        image = pygame.Surface((width, height)).convert()
        image.set_colorkey(BLACK)
        return image

    def __init__(self):
        super().__init__()
        self.image = self.get_empty_image()
        self.rect = self.image.get_rect()

    def get_pos(self):
        return self.rect.centerx, self.rect.centery

    def set_pos(self, x, y):
        self.rect.centerx = x
        self.rect.centery = y

    def set_cell_pos(self, col, row):
        new_col = col + self.col_offset
        new_row = row + self.row_offset
        self.set_pos(new_col * SPRITE_SIZE + SPRITE_SIZE // 2,
                     new_row * SPRITE_SIZE + SPRITE_SIZE // 2)


class BlockSprite(BaseSprite):
    """Общий класс для спрайтов, отображающих блоки уровня.
       Спрайты этих блоков зависят от соседних ячеек того же класса."""

    def __init__(self, col, row, index):
        super().__init__()
        self.sprite_sheet: Optional[EdgeSpriteSheet] = None
        self.define_sprite_sheet()

        self.image = self.sprite_sheet.get_image_by_index(index)
        self.rect = self.image.get_rect()
        self.set_cell_pos(col, row)

        self.sprite_sheet = None

    def define_sprite_sheet(self):
        pass


class Wall(BlockSprite):
    """Класс для спрайта стены"""

    def define_sprite_sheet(self):
        self.sprite_sheet = EdgeSpriteSheet(os.path.join(IMG_DIR, SPRITE_FILE_WALLS))


class Floor(BlockSprite):
    """Класс для спрайта пола"""

    def define_sprite_sheet(self):
        self.sprite_sheet = EdgeSpriteSheet(os.path.join(IMG_DIR, SPRITE_FILE_FLOOR))


class Lava(BlockSprite):
    """Класс для спрайта лавы"""

    def define_sprite_sheet(self):
        self.sprite_sheet = EdgeSpriteSheet(os.path.join(IMG_DIR, SPRITE_FILE_LAVA))


class River(BlockSprite):
    """Класс для спрайта реки"""

    def define_sprite_sheet(self):
        self.sprite_sheet = EdgeSpriteSheet(os.path.join(IMG_DIR, SPRITE_FILE_RIVER))


class Acid(BlockSprite):
    """Класс для спрайта кислоты"""

    def define_sprite_sheet(self):
        self.sprite_sheet = EdgeSpriteSheet(os.path.join(IMG_DIR, SPRITE_FILE_ACID))


class Player(BaseSprite):
    """Общий класс для игроков"""

    def __init__(self, col, row):
        super().__init__()
        self.sprite_sheet: Optional[SpriteSheet] = None
        self.define_sprite_sheet()

        self.left_sprites = []
        self.right_sprites = []
        self.up_sprites = []
        self.down_sprites = []
        self.load_sprites()

        self.sprites = self.down_sprites
        self.image = self.sprites[-1]
        self.rect = self.image.get_rect()
        self.set_cell_pos(col, row)

        self.alive = True
        self.death_groups = []

        self.walk_offset = None
        self.current_sprite_index = None
        self.last_anim_tick = None

    def define_sprite_sheet(self):
        pass

    def load_sprites(self):
        """Загрузка спрайтов для анимаций перемещения"""
        for row, sprite_list in enumerate([self.down_sprites, self.left_sprites,
                                           self.right_sprites, self.up_sprites]):
            for col in range(4):
                image = self.sprite_sheet.get_cell_image(col, row)
                sprite_list.append(image)

    def add_death_group(self, group):
        self.death_groups.append(group)

    def move_to_cell(self, col, row, stop_group, door_group):
        """Перемещение в соседнюю клетку"""
        if self.walk_offset is not None:
            return
        pos_before_move = self.get_pos()
        self.rect = self.rect.move(col * SPRITE_SIZE, row * SPRITE_SIZE)
        pos_after_move = self.get_pos()
        pos_offset = [pos_after_move[0] - pos_before_move[0],
                      pos_after_move[1] - pos_before_move[1]]

        can_walk = True
        if pygame.sprite.spritecollideany(self, stop_group):
            can_walk = False
        else:
            door = pygame.sprite.spritecollideany(self, door_group)
            door: Union['Door', pygame.sprite.Sprite]
            if door is not None and door.is_active:
                can_walk = False

        if pos_after_move != pos_before_move:
            self.change_sprites(pos_offset)
        else:
            return

        if can_walk:
            self.walk_offset = pos_offset
        else:
            self.image = self.sprites[-1]
            self.rect = self.image.get_rect()

        self.set_pos(*pos_before_move)

    def change_sprites(self, pos_offset):
        if pos_offset[0] < 0:
            self.sprites = self.left_sprites
        elif pos_offset[0] > 0:
            self.sprites = self.right_sprites
        elif pos_offset[1] < 0:
            self.sprites = self.up_sprites
        elif pos_offset[1] > 0:
            self.sprites = self.down_sprites

    def update(self):
        if self.walk_offset is None:
            return

        self.animate()

        if self.walk_offset == [0, 0]:
            self.reset_walking()
            self.after_move_checks()

    def animate(self):
        now = pygame.time.get_ticks()
        do_step = False
        if self.last_anim_tick is None:
            self.current_sprite_index = 0
            do_step = True
        elif now - self.last_anim_tick > PlAYER_ANIMATION_DURATION:
            self.current_sprite_index = (self.current_sprite_index + 1) % len(self.sprites)
            do_step = True

        if do_step is True:
            self.last_anim_tick = now

            step_x = min(abs(self.walk_offset[0]), PLAYER_STEP)
            if self.walk_offset[0] < 0:
                step_x = - step_x
            step_y = min(abs(self.walk_offset[1]), PLAYER_STEP)
            if self.walk_offset[1] < 0:
                step_y = - step_y

            self.rect.centerx += step_x
            self.walk_offset[0] -= step_x
            self.rect.centery += step_y
            self.walk_offset[1] -= step_y

            self.change_sprites(self.walk_offset)

            pos_x, pos_y = self.get_pos()
            self.image = self.sprites[self.current_sprite_index]
            self.rect = self.image.get_rect()
            self.set_pos(pos_x, pos_y)

    def reset_walking(self):
        self.walk_offset = None
        self.current_sprite_index = None
        self.last_anim_tick = None

    def after_move_checks(self):
        """Проверки после перемещения персонажа в соседнюю клетку"""
        for death_group in self.death_groups:
            if pygame.sprite.spritecollideany(self, death_group):
                self.alive = False


class FirePlayer(Player):
    """Класс для игрока 'Огонь'"""

    def define_sprite_sheet(self):
        self.sprite_sheet = SpriteSheet(os.path.join(IMG_DIR, SPRITE_FILE_FIRE_PLAYER))


class WaterPlayer(Player):
    """Класс для игрока 'Вода'"""

    def define_sprite_sheet(self):
        self.sprite_sheet = SpriteSheet(os.path.join(IMG_DIR, SPRITE_FILE_WATER_PLAYER))


class ElementSprite(BaseSprite):
    """Общий класс для элементов, с которыми могут взаимодействовать игроки"""

    def __init__(self, col, row):
        super().__init__()
        self.is_active = False
        self.is_interacted = False
        self.is_paused = False

        self.sprite_sheet = SpriteSheet(os.path.join(IMG_DIR, SPRITE_FILE_ELEMENTS))
        self.images = []
        self.load_images()
        self.sprite_sheet = None

        self.image: Optional[pygame.Surface] = None
        self.set_active(False)
        self.set_cell_pos(col, row)

    def load_images(self):
        """Загрузка 2х спрайтов, для элемента в неактивном и активном состоянии"""
        image = self.get_empty_image()
        self.images = [image for _ in range(2)]

    def set_active(self, active):
        pos = self.get_pos()
        self.is_active = active
        self.image = self.images[1] if self.is_active else self.images[0]
        self.rect = self.image.get_rect()
        self.set_pos(*pos)

    def interact_with(self, subject):
        """Взаимодействие игрока с текущим элементом"""
        pass

    def reset_interaction(self):
        self.is_interacted = False


class Ruby(ElementSprite):
    """Класс для камня 'Рубин'"""

    def __init__(self, col, row):
        super().__init__(col, row)
        self.set_active(True)
        self.fire_player = None

    def load_images(self):
        inactive_image = self.sprite_sheet.get_cell_image(0, 0)
        active_image = self.sprite_sheet.get_cell_image(1, 0)
        self.images = [inactive_image, active_image]

    def connect_player(self, player):
        self.fire_player = player

    def interact_with(self, subject):
        if subject == self.fire_player:
            self.is_interacted = True
            self.set_active(False)
            self.kill()


class Aquamarine(ElementSprite):
    """Класс для камня 'Аквамарин'"""

    def __init__(self, col, row):
        super().__init__(col, row)
        self.set_active(True)
        self.water_player = None

    def load_images(self):
        inactive_image = self.sprite_sheet.get_cell_image(2, 0)
        active_image = self.sprite_sheet.get_cell_image(3, 0)
        self.images = [inactive_image, active_image]

    def connect_player(self, player):
        self.water_player = player

    def interact_with(self, subject):
        if subject == self.water_player:
            self.is_interacted = True
            self.set_active(False)
            self.kill()


class FireExit(ElementSprite):
    """Класс для завершения уровня для игрока 'Огонь'"""

    def __init__(self, col, row):
        super().__init__(col, row)
        self.ruby_sprites = pygame.sprite.Group()
        self.fire_player = None

    def load_images(self):
        inactive_image = self.sprite_sheet.get_cell_image(0, 1)
        active_image = self.sprite_sheet.get_cell_image(1, 1)
        self.images = [inactive_image, active_image]

    def connect_player(self, player):
        self.fire_player = player

    def connect_stone(self, stone):
        self.ruby_sprites.add(stone)

    def interact_with(self, subject):
        if self.is_active and subject == self.fire_player:
            self.is_interacted = True

    def update(self):
        if not self.is_active:
            if not len(self.ruby_sprites):
                self.set_active(True)


class WaterExit(ElementSprite):
    """Класс для завершения уровня для игрока 'Огонь'"""

    def __init__(self, col, row):
        super().__init__(col, row)
        self.aquamarine_sprites = pygame.sprite.Group()
        self.water_player = None

    def load_images(self):
        inactive_image = self.sprite_sheet.get_cell_image(2, 1)
        active_image = self.sprite_sheet.get_cell_image(3, 1)
        self.images = [inactive_image, active_image]

    def connect_player(self, player):
        self.water_player = player

    def connect_stone(self, stone):
        self.aquamarine_sprites.add(stone)

    def interact_with(self, subject):
        if self.is_active and subject == self.water_player:
            self.is_interacted = True

    def update(self):
        if not self.is_active:
            if not len(self.aquamarine_sprites):
                self.set_active(True)


class DoorButton(ElementSprite):
    """Класс для кнопки открытия двери"""

    def __init__(self, col, row, kind):
        self.kind = kind
        super().__init__(col, row)
        self.door_set = set()

    def load_images(self):
        inactive_image = self.sprite_sheet.get_cell_image(self.kind * 2, 2)
        active_image = self.sprite_sheet.get_cell_image(self.kind * 2 + 1, 2)
        self.images = [inactive_image, active_image]

    def connect_door(self, door):
        self.door_set.add(door)

    def interact_with(self, subject):
        self.set_active(True)
        for door in self.door_set:
            door.interact_with(self)
        self.is_interacted = True

    def update(self):
        if not self.is_interacted and self.is_active:
            self.set_active(False)


class Door(ElementSprite):
    """Класс для двери"""

    def __init__(self, col, row, kind):
        self.kind = kind
        super().__init__(col, row)
        self.set_active(True)
        self.button_set = set()
        self.fire_player = None
        self.water_player = None

    def load_images(self):
        inactive_image = self.sprite_sheet.get_cell_image(self.kind * 2, 3)
        active_image = self.sprite_sheet.get_cell_image(self.kind * 2 + 1, 3)
        self.images = [inactive_image, active_image]

    def connect_players(self, fire_player, water_player):
        self.fire_player = fire_player
        self.water_player = water_player

    def connect_to_button(self, button):
        self.button_set.add(button)

    def interact_with(self, subject):
        if subject in self.button_set:
            self.set_active(False)
            self.is_interacted = True

    def update(self):
        if not self.is_interacted and not self.is_active:
            if not pygame.sprite.collide_rect(self, self.water_player) and \
                    not pygame.sprite.collide_rect(self, self.fire_player):
                self.set_active(True)


class PortalSwitch(ElementSprite):
    """Класс рычага для переключения направления порталов"""

    def __init__(self, col, row, kind):
        self.kind = kind
        super().__init__(col, row)
        self.set_active(False)

        self.portal_set = set()
        self.other_switches_set = set()

    def load_images(self):
        inactive_image = self.sprite_sheet.get_cell_image(self.kind * 2, 4)
        active_image = self.sprite_sheet.get_cell_image(self.kind * 2 + 1, 4)
        self.images = [inactive_image, active_image]

    def connect_portals(self, input_portal, output_portal):
        self.portal_set.add(input_portal)
        self.portal_set.add(output_portal)

    def connect_other_switches(self, switch):
        if self != switch:
            self.other_switches_set.add(switch)

    def interact_with(self, subject):
        if not self.is_paused:
            self.set_active(not self.is_active)
            for switch in self.other_switches_set:
                switch.set_active(self.is_active)
            for portal in self.portal_set:
                portal.reverse_direction()
            self.is_paused = True

        self.is_interacted = True

    def update(self):
        if self.is_paused and not self.is_interacted:
            self.is_paused = False


class Portal(ElementSprite):
    """Класс для портала"""

    def __init__(self, col, row, kind, is_output):
        self.kind = kind
        super().__init__(col, row)
        self.col, self.row = col, row
        self.set_active(is_output)
        self.other_portal = None

    def load_images(self):
        input_image = self.sprite_sheet.get_cell_image(self.kind * 2, 5)
        output_image = self.sprite_sheet.get_cell_image(self.kind * 2 + 1, 5)
        self.images = [output_image, input_image]

    def is_input(self):
        return self.is_active

    def set_input(self, is_input):
        self.set_active(is_input)

    def reverse_direction(self):
        self.set_input(not self.is_input())

    def connect_portal(self, portal):
        self.other_portal = portal

    def interact_with(self, subject):
        if self.is_input() and \
                self.other_portal is not None:
            subject.reset_walking()
            new_pos = list(self.other_portal.get_pos())
            # new_pos[0] += subject.get_pos()[0] - self.get_pos()[0]
            # new_pos[1] += subject.get_pos()[1] - self.get_pos()[1]
            subject.set_pos(*new_pos)


class LevelSprite(BaseSprite):
    """Класс для спрайтов уровней при выборе уровня"""

    def __init__(self, col, row, number, is_unlocked, is_done):
        super().__init__()
        self.number = number

        self.is_unlocked = is_unlocked
        self.is_done = is_done

        self.sprite_sheet = SpriteSheet(os.path.join(IMG_DIR, SPRITE_FILE_LEVEL_ICONS))
        self.define_image()
        self.sprite_sheet = None

        self.set_cell_pos(col, row)

    def define_image(self):
        self.image = self.get_empty_image(SPRITE_SIZE, SPRITE_SIZE * 2)
        if not self.is_unlocked:
            image = self.sprite_sheet.get_cell_image(0, 0)
            color = None
        elif not self.is_done:
            image = self.sprite_sheet.get_cell_image(1, 0)
            color = pygame.Color('white')
        else:
            image = self.sprite_sheet.get_cell_image(2, 0)
            color = pygame.Color('green')
        self.image.blit(image, (0, 0))
        if color is not None:
            display_text(self.image, str(self.number), 24, color,
                         SPRITE_SIZE // 2, SPRITE_SIZE + SPRITE_SIZE // 2)

    def get_levelname(self):
        return f"level{self.number}.txt"


class Level:
    """Уровень игры"""

    def __init__(self, filename):
        self.filename = filename
        self.width, self.height = 0, 0
        self.col_offset, self.row_offset = 0, 0
        self.blocks = []
        self.indexes = []
        self.fire_player_pos = None
        self.water_player_pos = None
        self.elem_pos_dict = dict()
        self.load_level(filename)

    @staticmethod
    def get_kind(elem):
        return 1 if elem.isupper() else 0

    def load_level(self, filename):
        """Загрузка уровня"""
        fullname = os.path.join(LEVELS_DIR, filename)

        with open(fullname) as f:
            data = [line.rstrip() for line in f.readlines()]

        self.width = min([max(map(len, data)), MAX_LEVEL_SIZE])
        self.height = min([len(data), MAX_LEVEL_SIZE])
        self.col_offset = (MAX_LEVEL_SIZE - self.width) // 2
        self.row_offset = (MAX_LEVEL_SIZE - self.height) // 2
        data = list(map(lambda x: x[:self.width].ljust(self.width, LEVEL_BLOCK_EMPTY),
                        data[:self.height]))

        blocks_set = {LEVEL_BLOCK_EMPTY, LEVEL_BLOCK_WALL, LEVEL_BLOCK_FLOOR,
                      LEVEL_BLOCK_LAVA, LEVEL_BLOCK_RIVER, LEVEL_BLOCK_ACID}
        elem_single_set = {LEVEL_ELEM_FIRE_EXIT, LEVEL_ELEM_WATER_EXIT,
                           LEVEL_ELEM_INPUT_PORTAL_1, LEVEL_ELEM_INPUT_PORTAL_2,
                           LEVEL_ELEM_OUTPUT_PORTAL_1, LEVEL_ELEM_OUTPUT_PORTAL_2}
        elems_multi_set = {LEVEL_ELEM_RUBY, LEVEL_ELEM_AQUAMARINE,
                           LEVEL_ELEM_DOORBUTTON_1, LEVEL_ELEM_DOORBUTTON_2,
                           LEVEL_ELEM_DOOR_1, LEVEL_ELEM_DOOR_2,
                           LEVEL_ELEM_PORTAL_SWITCH_1, LEVEL_ELEM_PORTAL_SWITCH_2}

        self.blocks = [[0] * self.width for _ in range(self.height)]
        for row, line in enumerate(data):
            for col, elem in enumerate(line):
                self.blocks[row][col] = elem if elem in blocks_set else LEVEL_BLOCK_FLOOR
                if elem == LEVEL_PLAYER_FIRE:
                    self.fire_player_pos = col, row
                elif elem == LEVEL_PLAYER_WATER:
                    self.water_player_pos = col, row
                elif elem in elem_single_set:
                    self.elem_pos_dict[elem] = [(col, row)]
                elif elem in elems_multi_set:
                    if elem not in self.elem_pos_dict:
                        self.elem_pos_dict[elem] = []
                    self.elem_pos_dict[elem].append((col, row))

        self.indexes = [[0] * self.width for _ in range(self.height)]
        self.calculate_indexes()

    def calculate_indexes(self):
        """Расчёт индексов блоков уровня с учётом соседних блоков того же типа"""
        for row in range(self.height):
            for col in range(self.width):
                if self.indexes[row][col] < 0:
                    continue
                index = 0
                near_list = [(col, row - 1, 1), (col + 1, row, 2),
                             (col, row + 1, 4), (col - 1, row, 8)]
                for near_col, near_row, weight in near_list:
                    if not self.cell_on_board(near_col, near_row):
                        continue
                    if self.blocks[near_row][near_col] == self.blocks[row][col]:
                        index += weight
                self.indexes[row][col] = index

    def cell_on_board(self, col, row):
        """Проверка на присутствие координат на игровом уровне"""
        return 0 <= col < self.width and 0 <= row < self.height


class SaveFile:
    """Класс для файла с сохранением прогресса"""

    def __init__(self):
        self.filename = os.path.join(CURRENT_DIR, CSV_FILE_SAVE)
        self.headers = ["levels_done"]

        self.levels_done = 0

        self.load_values()

    def load_values(self):
        try:
            with open(self.filename, 'r', encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';')
                for line in reader:
                    if "levels_done" in line:
                        self.levels_done = int(line["levels_done"])
        except FileNotFoundError:
            return

    def save_values(self):
        data = [self.headers, [self.levels_done]]

        with open(self.filename, 'w', encoding="utf-8", newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            for row in data:
                writer.writerow(row)


class Screen:
    """Общий класс для экранов"""

    def __init__(self):
        self.screen_sprites = pygame.sprite.Group()

        self.bg_color1 = SCREEN_COLORS_DICT[SCREEN_BG_COLOR1]
        self.bg_color2 = SCREEN_COLORS_DICT[SCREEN_BG_COLOR2]
        self.shadow_color = SCREEN_COLORS_DICT[SCREEN_SHADOW_COLOR]
        self.text_color = SCREEN_COLORS_DICT[SCREEN_TEXT_COLOR]

        self.shadow_cell_rect = pygame.Rect(2, 3, 21, 1)
        self.text_cell_rect = pygame.Rect(2, 4, 21, 20)
        self.shadow_rect = pygame.Rect(SPRITE_SIZE * self.shadow_cell_rect.left,
                                       SPRITE_SIZE * self.shadow_cell_rect.top,
                                       SPRITE_SIZE * self.shadow_cell_rect.width,
                                       SPRITE_SIZE * self.shadow_cell_rect.height)
        self.text_rect = pygame.Rect(SPRITE_SIZE * self.text_cell_rect.left,
                                     SPRITE_SIZE * self.text_cell_rect.top,
                                     SPRITE_SIZE * self.text_cell_rect.width,
                                     SPRITE_SIZE * self.text_cell_rect.height)

    def prepare(self, surface):
        surface.fill(self.bg_color1)
        pygame.draw.rect(surface, self.bg_color2, self.text_rect)
        pygame.draw.rect(surface, self.shadow_color, self.shadow_rect)
        image = pygame.image.load(os.path.join(IMG_DIR, IMG_FILE_TITLE)).convert()
        image.set_colorkey(BLACK)
        rect = image.get_rect()
        surface.blit(image, rect)

    def render(self, surface):
        pass

    def process_events(self):
        self.pause()

    @staticmethod
    def pause():
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN]:
                        waiting = False

    def show(self, surface):
        self.render(surface)
        self.process_events()


class StartScreen(Screen):
    """Стартовый экран для выбора уровня"""

    def __init__(self):
        super().__init__()
        self.level_sprites = pygame.sprite.Group()
        self.save_file = SaveFile()
        self.create_levels()

        self.level_sprite: Optional[LevelSprite] = None

    def reset_screen(self):
        BaseSprite.reset_offset()
        self.screen_sprites.empty()
        self.level_sprites.empty()
        self.create_levels()
        self.level_sprite = None

    def create_levels(self):
        for row in range(3):
            for col in range(3):
                num = row * 3 + col + 1
                is_unlocked, is_done = False, False
                if num <= self.save_file.levels_done:
                    is_unlocked, is_done = True, True
                elif num == self.save_file.levels_done + 1:
                    is_unlocked = True

                level = LevelSprite(self.shadow_cell_rect.left + col * 7 + 3,
                                    self.shadow_cell_rect.top + row * 7 + 4,
                                    num, is_unlocked, is_done)

                self.screen_sprites.add(level)
                self.level_sprites.add(level)

    def show(self, surface):
        self.reset_screen()
        self.render(surface)
        self.process_events()

    def process_events(self):
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
                    for level in self.level_sprites:
                        level: LevelSprite
                        if level.is_unlocked and level.rect.collidepoint(*event.pos):
                            self.level_sprite = level
                            waiting = False

    def render(self, surface):
        self.prepare(surface)
        for y_offset, color in [(4, self.shadow_color), (0, self.text_color)]:
            display_text(surface, 'ВЫБЕРИТЕ УРОВЕНЬ:', 50, color,
                         SCREEN_WIDTH // 2, SCREEN_WIDTH // 5 + y_offset)
        self.screen_sprites.draw(surface)
        pygame.display.flip()

    def unlock_new_level(self):
        if self.level_sprite.number > self.save_file.levels_done:
            self.save_file.levels_done += 1
            self.save_file.save_values()


class EndScreen(Screen):
    """Конечный экран для отображения результатов"""

    def __init__(self):
        super().__init__()
        self.win_game = False

    def set_result(self, result):
        self.win_game = result

    def render(self, surface):
        self.prepare(surface)
        if self.win_game:
            result_text = 'УРОВЕНЬ ПРОЙДЕН!'
        else:
            result_text = 'ВЫ ПРОИГРАЛИ!'
        for i, word in enumerate(result_text.split()):
            y = self.text_rect.top + self.text_rect.height // 3 + self.text_rect.height // 6 * i
            for y_offset, color in [(4, self.shadow_color), (0, self.text_color)]:
                display_text(surface, word, 80, color,
                             SCREEN_WIDTH // 2, y + y_offset)
        pygame.display.flip()


class Game:
    """Основной класс игры"""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.levelname = None

        self.start_screen = StartScreen()
        self.end_screen = EndScreen()

        self.running = True
        self.game_over = False
        self.win_game = False
        self.with_end_screen = False

        self.all_sprites = pygame.sprite.Group()
        self.wall_sprites = pygame.sprite.Group()
        self.lava_sprites = pygame.sprite.Group()
        self.river_sprites = pygame.sprite.Group()
        self.acid_sprites = pygame.sprite.Group()

        self.elements_sprites = pygame.sprite.Group()
        self.door_sprites = pygame.sprite.Group()

        self.fire_player = None
        self.water_player = None
        self.fire_exit = None
        self.water_exit = None

        self.connection_dict = {}

    def reset_game(self):
        BaseSprite.reset_offset()
        for sprite in self.all_sprites:
            sprite.kill()

        self.fire_player = None
        self.water_player = None
        self.fire_exit = None
        self.water_exit = None

        self.connection_dict.clear()

    def new_game(self, levelname):
        """Создание новой игры"""
        self.reset_game()

        level = Level(levelname)
        BaseSprite.set_offset(level.col_offset, level.row_offset)

        for row in range(level.height):
            for col in range(level.width):
                if level.blocks[row][col] == LEVEL_BLOCK_WALL:
                    level_sprite = Wall(col, row, level.indexes[row][col])
                    self.wall_sprites.add(level_sprite)
                elif level.blocks[row][col] == LEVEL_BLOCK_LAVA:
                    level_sprite = Lava(col, row, level.indexes[row][col])
                    self.lava_sprites.add(level_sprite)
                elif level.blocks[row][col] == LEVEL_BLOCK_RIVER:
                    level_sprite = River(col, row, level.indexes[row][col])
                    self.river_sprites.add(level_sprite)
                elif level.blocks[row][col] == LEVEL_BLOCK_ACID:
                    level_sprite = Acid(col, row, level.indexes[row][col])
                    self.acid_sprites.add(level_sprite)
                elif level.blocks[row][col] == LEVEL_BLOCK_EMPTY:
                    continue
                else:
                    level_sprite = Floor(col, row, level.indexes[row][col])

                self.all_sprites.add(level_sprite)

        for elem in level.elem_pos_dict:
            for col, row in level.elem_pos_dict[elem]:
                if elem == LEVEL_ELEM_RUBY:
                    level_sprite = Ruby(col, row)
                elif elem == LEVEL_ELEM_AQUAMARINE:
                    level_sprite = Aquamarine(col, row)
                elif elem == LEVEL_ELEM_FIRE_EXIT:
                    level_sprite = FireExit(col, row)
                    self.fire_exit = level_sprite
                elif elem == LEVEL_ELEM_WATER_EXIT:
                    level_sprite = WaterExit(col, row)
                    self.water_exit = level_sprite
                elif elem == LEVEL_ELEM_DOORBUTTON_1 or \
                        elem == LEVEL_ELEM_DOORBUTTON_2:
                    level_sprite = DoorButton(col, row, level.get_kind(elem))
                elif elem == LEVEL_ELEM_DOOR_1 or \
                        elem == LEVEL_ELEM_DOOR_2:
                    level_sprite = Door(col, row, level.get_kind(elem))
                    self.door_sprites.add(level_sprite)
                elif elem == LEVEL_ELEM_INPUT_PORTAL_1 or \
                        elem == LEVEL_ELEM_INPUT_PORTAL_2:
                    level_sprite = Portal(col, row, level.get_kind(elem), True)
                elif elem == LEVEL_ELEM_OUTPUT_PORTAL_1 or \
                        elem == LEVEL_ELEM_OUTPUT_PORTAL_2:
                    level_sprite = Portal(col, row, level.get_kind(elem), False)
                elif elem == LEVEL_ELEM_PORTAL_SWITCH_1 or \
                        elem == LEVEL_ELEM_PORTAL_SWITCH_2:
                    level_sprite = PortalSwitch(col, row, level.get_kind(elem))
                else:
                    continue

                if elem not in self.connection_dict:
                    self.connection_dict[elem] = []
                self.connection_dict[elem].append(level_sprite)

                self.elements_sprites.add(level_sprite)
                self.all_sprites.add(level_sprite)

        if level.fire_player_pos is not None:
            self.fire_player = FirePlayer(*level.fire_player_pos)
            self.all_sprites.add(self.fire_player)
            for group in [self.river_sprites, self.acid_sprites]:
                self.fire_player.add_death_group(group)
        if level.water_player_pos is not None:
            self.water_player = WaterPlayer(*level.water_player_pos)
            self.all_sprites.add(self.water_player)
            for group in [self.lava_sprites, self.acid_sprites]:
                self.water_player.add_death_group(group)

        self.connect_elements()

        self.win_game = False
        self.game_over = False

    def connect_elements(self):
        for level_elem_stone, level_elem_exit, player in \
                [(LEVEL_ELEM_RUBY, LEVEL_ELEM_FIRE_EXIT, self.fire_player),
                 (LEVEL_ELEM_AQUAMARINE, LEVEL_ELEM_WATER_EXIT, self.water_player)]:

            if level_elem_stone in self.connection_dict and \
                    level_elem_exit in self.connection_dict:
                level_exit = self.connection_dict[level_elem_exit][0]
                if player is not None:
                    level_exit.connect_player(player)
                for stone in self.connection_dict[level_elem_stone]:
                    if player is not None:
                        stone.connect_player(player)
                    level_exit.connect_stone(stone)

        for level_elem_doorbutton, level_elem_door in \
                [(LEVEL_ELEM_DOORBUTTON_1, LEVEL_ELEM_DOOR_1),
                 (LEVEL_ELEM_DOORBUTTON_2, LEVEL_ELEM_DOOR_2)]:

            if level_elem_doorbutton in self.connection_dict and \
                    level_elem_door in self.connection_dict:
                for button in self.connection_dict[level_elem_doorbutton]:
                    for door in self.connection_dict[level_elem_door]:
                        button.connect_door(door)
                        door.connect_to_button(button)
                        door.connect_players(self.fire_player, self.water_player)

        for level_elem_input_portal, level_elem_output_portal, level_elem_portal_switch in \
                [(LEVEL_ELEM_INPUT_PORTAL_1, LEVEL_ELEM_OUTPUT_PORTAL_1, LEVEL_ELEM_PORTAL_SWITCH_1),
                 (LEVEL_ELEM_INPUT_PORTAL_2, LEVEL_ELEM_OUTPUT_PORTAL_2, LEVEL_ELEM_PORTAL_SWITCH_2)
                 ]:

            if level_elem_input_portal in self.connection_dict and \
                    level_elem_output_portal in self.connection_dict:
                input_portal = self.connection_dict[level_elem_input_portal][0]
                output_portal = self.connection_dict[level_elem_output_portal][0]
                input_portal.connect_portal(output_portal)
                output_portal.connect_portal(input_portal)
                if level_elem_portal_switch in self.connection_dict:
                    switch: PortalSwitch
                    for switch in self.connection_dict[level_elem_portal_switch]:
                        switch.connect_portals(input_portal, output_portal)
                        for other_switch in self.connection_dict[level_elem_portal_switch]:
                            if switch != other_switch:
                                switch.connect_other_switches(other_switch)

    def process_events(self):
        """Обработка событий игры"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game_over = True
                    self.with_end_screen = False
                if event.key == pygame.K_a:
                    self.fire_player.move_to_cell(-1, 0, self.wall_sprites, self.door_sprites)
                elif event.key == pygame.K_d:
                    self.fire_player.move_to_cell(1, 0, self.wall_sprites, self.door_sprites)
                elif event.key == pygame.K_w:
                    self.fire_player.move_to_cell(0, -1, self.wall_sprites, self.door_sprites)
                elif event.key == pygame.K_s:
                    self.fire_player.move_to_cell(0, 1, self.wall_sprites, self.door_sprites)
                elif event.key == pygame.K_LEFT:
                    self.water_player.move_to_cell(-1, 0, self.wall_sprites, self.door_sprites)
                elif event.key == pygame.K_RIGHT:
                    self.water_player.move_to_cell(1, 0, self.wall_sprites, self.door_sprites)
                elif event.key == pygame.K_UP:
                    self.water_player.move_to_cell(0, -1, self.wall_sprites, self.door_sprites)
                elif event.key == pygame.K_DOWN:
                    self.water_player.move_to_cell(0, 1, self.wall_sprites, self.door_sprites)

        pressed_key = pygame.key.get_pressed()
        # Если нажаты левый и/или правый CTRL,
        # то соответствующий игрок взаимодействует с предметом, с которым пересекается
        interaction_list = []
        if pressed_key[pygame.K_LCTRL]:
            interaction_list.append(self.fire_player)
        if pressed_key[pygame.K_RCTRL]:
            interaction_list.append(self.water_player)
        for player in interaction_list:
            elem_sprite: Union[pygame.sprite.Sprite, ElementSprite]
            elem_sprite = pygame.sprite.spritecollideany(player, self.elements_sprites)
            if elem_sprite is not None:
                elem_sprite.interact_with(player)

    def update(self):
        """Обновление спрайтов"""
        self.all_sprites.update()

        for player in [self.fire_player, self.water_player]:
            if not player.alive:
                self.win_game = False
                self.game_over = True
                self.with_end_screen = True
                return

        if self.water_exit.is_interacted and self.water_exit.is_interacted:
            self.win_game = True
            self.start_screen.unlock_new_level()
            self.game_over = True
            self.with_end_screen = True
            return

        for elem_sprite in self.elements_sprites:
            elem_sprite: Union[pygame.sprite.Sprite, ElementSprite]
            elem_sprite.reset_interaction()

    def display(self):
        """Отрисовка элементов игры"""
        self.screen.fill(BLACK)

        self.all_sprites.draw(self.screen)

        pygame.display.flip()

    def run(self):
        """Основной цикл игры"""
        while not self.game_over:
            self.process_events()
            self.update()
            self.display()

            self.clock.tick(FPS)

    def show_start_screen(self):
        self.start_screen.show(self.screen)
        self.levelname = self.start_screen.level_sprite.get_levelname()

    def show_end_screen(self):
        self.end_screen.set_result(self.win_game)
        self.end_screen.show(self.screen)


def main():
    mygame = Game()

    while mygame.running:
        mygame.show_start_screen()
        mygame.new_game(mygame.levelname)
        mygame.run()
        if mygame.with_end_screen:
            mygame.show_end_screen()

    pygame.quit()


if __name__ == "__main__":
    main()
