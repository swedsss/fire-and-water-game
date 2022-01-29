import pygame
from typing import Optional, Union
from constants import *
from functions import get_empty_image, display_text
from spritesheets import SpriteSheet, EdgeSpriteSheet


class BaseSprite(pygame.sprite.Sprite):
    """Общий класс для всех спрайтов на экране"""

    # Сдвиг отображения спрайтов на уровне
    col_offset = 0
    row_offset = 0

    @classmethod
    def set_offset(cls, col_offset, row_offset):
        """Установка сдвига при отображении спрайтов"""
        cls.col_offset = col_offset
        cls.row_offset = row_offset

    @classmethod
    def reset_offset(cls):
        """Сброс сдвига при отображении спрайтов"""
        cls.set_offset(0, 0)

    def __init__(self):
        super().__init__()
        self.image = get_empty_image()
        self.rect = self.image.get_rect()

    def get_pos(self):
        """Получение позиции центра спрайта"""
        return self.rect.centerx, self.rect.centery

    def set_pos(self, x, y):
        """Задание позиции центра спрайта"""
        self.rect.centerx = x
        self.rect.centery = y

    def set_cell_pos(self, col, row):
        """Задание позиции спрайта в табличном представлении и с учётом сдвига"""
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
        """Определение файла для набора спрайтов"""
        # Метод реализован в дочерних классах.
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

        self.is_alive = True
        self.death_groups = []

        self.walk_offset = None
        self.current_sprite_index = None
        self.last_anim_tick = None

    def define_sprite_sheet(self):
        # Метод реализован в дочерних классах.
        pass

    def load_sprites(self):
        """Загрузка спрайтов для анимаций перемещения вверх, влево, вправо и вниз"""
        for row, sprite_list in enumerate([self.down_sprites, self.left_sprites,
                                           self.right_sprites, self.up_sprites]):
            for col in range(4):
                image = self.sprite_sheet.get_cell_image(col, row)
                sprite_list.append(image)

    def add_death_group(self, group):
        """Определение групп спрайтов, при пересечении с которыми игрок погибает"""
        self.death_groups.append(group)

    def move_to_cell(self, col, row, stop_group, door_group):
        """Перемещение в соседнюю клетку"""

        # Пока игрок двигается, задать новое движение нельзя
        if self.walk_offset is not None:
            return

        # Координаты до и после перемещения
        pos_before_move = self.get_pos()
        self.rect = self.rect.move(col * SPRITE_SIZE, row * SPRITE_SIZE)
        pos_after_move = self.get_pos()
        pos_offset = [pos_after_move[0] - pos_before_move[0],
                      pos_after_move[1] - pos_before_move[1]]

        can_walk = True
        if pygame.sprite.spritecollideany(self, stop_group):
            # Пересечение со спрайтом из стоп-группы при перемещении.
            # Значит, в соседнюю клетку переместиться нельзя.
            can_walk = False
        else:
            # В соседней клекте дверь. Туда можно переместиться, если она открыта.
            door = pygame.sprite.spritecollideany(self, door_group)
            door: Union[Door, pygame.sprite.Sprite]
            if door is not None and door.is_active:
                can_walk = False

        # Если координаты отличаются, то происходит
        # замена спрайтов, направленных по ходу движения игрока
        if pos_after_move != pos_before_move:
            self.change_sprites(pos_offset)
        else:
            return

        # Если можно переместиться, то запоминается смещение
        # относительно текущего положения (в пикселях)
        if can_walk:
            self.walk_offset = pos_offset
        else:
            self.image = self.sprites[-1]
            self.rect = self.image.get_rect()

        # Возвращение персонажа на место после проверки
        self.set_pos(*pos_before_move)

    def change_sprites(self, pos_offset):
        """Выбор группы спрайтов, направленных по ходу движения"""

        if pos_offset[0] < 0:
            self.sprites = self.left_sprites
        elif pos_offset[0] > 0:
            self.sprites = self.right_sprites
        elif pos_offset[1] < 0:
            self.sprites = self.up_sprites
        elif pos_offset[1] > 0:
            self.sprites = self.down_sprites

    def update(self):
        # Если игрок не собирается перемещаться, то обработка метода заканчивается
        if self.walk_offset is None:
            return

        # Анимация перемещения
        self.animate()

        # Если игрок пришёл в нужное место,
        # то происходит сброс переменных, заполняемых для перемещения
        if self.walk_offset == [0, 0]:
            self.reset_walking()
            self.after_move_checks()

    def animate(self):
        """Анимация игрока при перемещении"""
        # Фиксация текущего времени
        now = pygame.time.get_ticks()
        do_step = False
        # Начало анимации
        if self.last_anim_tick is None:
            self.current_sprite_index = 0
            do_step = True
        elif now - self.last_anim_tick > PLAYER_ANIMATION_DURATION:
            # Если после предыдущего шага прошло достаточно времени,
            # то разрешается сделать следующий шаг
            # при этом вычисляется индекс следующего кадра анимации
            self.current_sprite_index = (self.current_sprite_index + 1) % len(self.sprites)
            do_step = True

        # Проверка, может ли игрок сделать шаг в нужную сторону
        if do_step is True:
            self.last_anim_tick = now

            # Расчёт длины шага игрока
            step_x = min(abs(self.walk_offset[0]), PLAYER_STEP)
            if self.walk_offset[0] < 0:
                step_x = - step_x
            step_y = min(abs(self.walk_offset[1]), PLAYER_STEP)
            if self.walk_offset[1] < 0:
                step_y = - step_y

            # Выполнение шага (смещение игрока на шаг)
            # При этом относительные координаты уменьшаются на длину шага
            self.rect.centerx += step_x
            self.walk_offset[0] -= step_x
            self.rect.centery += step_y
            self.walk_offset[1] -= step_y

            # Замена спрайта игрока
            self.change_sprites(self.walk_offset)

            pos_x, pos_y = self.get_pos()
            self.image = self.sprites[self.current_sprite_index]
            self.rect = self.image.get_rect()
            self.set_pos(pos_x, pos_y)

    def reset_walking(self):
        """Сброс перемещения игрока"""
        self.walk_offset = None
        self.current_sprite_index = None
        self.last_anim_tick = None

    def after_move_checks(self):
        """Проверки после перемещения персонажа в соседнюю клетку"""
        for death_group in self.death_groups:
            if pygame.sprite.spritecollideany(self, death_group):
                self.is_alive = False


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
        image = get_empty_image()
        self.images = [image for _ in range(2)]

    def set_active(self, active):
        """Изменение состояния активности объекта"""
        pos = self.get_pos()
        self.is_active = active
        # Изменение спрайта
        self.image = self.images[1] if self.is_active else self.images[0]
        self.rect = self.image.get_rect()
        self.set_pos(*pos)

    def interact_with(self, subject):
        """Взаимодействие текущего элемента с другим элементом"""
        # Метод реализован в дочерних классах
        pass

    def reset_interaction(self):
        """Сброс признака взаимодействия"""
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
        """Соединение с игроком, который может взаимодействовать с объектом"""
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
        """Соединение с игроком, который может взаимодействовать с объектом"""
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
        """Соединение с игроком, который может взаимодействовать с объектом"""
        self.fire_player = player

    def connect_stone(self, stone):
        """Добавление камней, которые необходимы для активации выхода"""
        self.ruby_sprites.add(stone)

    def interact_with(self, subject):
        if self.is_active and subject == self.fire_player:
            self.is_interacted = True

    def update(self):
        if not self.is_active:
            if not len(self.ruby_sprites):
                # Если камней на уровне не осталось, то выход активируется
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
        """Соединение с игроком, который может взаимодействовать с объектом"""
        self.water_player = player

    def connect_stone(self, stone):
        """Добавление камней, которые необходимы для активации выхода"""
        self.aquamarine_sprites.add(stone)

    def interact_with(self, subject):
        if self.is_active and subject == self.water_player:
            self.is_interacted = True

    def update(self):
        if not self.is_active:
            if not len(self.aquamarine_sprites):
                # Если камней на уровне не осталось, то выход активируется
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
        """Добавление двери в множество дверей, которые эта кнопка открывает"""
        self.door_set.add(door)

    def interact_with(self, subject):
        self.set_active(True)
        # Взаимодействие кнопки с каждой подключенной дверью
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
        """Добавление игроков, с которыми взаимодействует дверь"""
        self.fire_player = fire_player
        self.water_player = water_player

    def connect_button(self, button):
        """Добавление кнопки в множество кнопок, которые могут открывать эту дверь"""
        self.button_set.add(button)

    def interact_with(self, subject):
        if subject in self.button_set:
            self.set_active(False)
            self.is_interacted = True

    def update(self):
        if not self.is_interacted and not self.is_active:
            # Если дверь открыта кнопкой, но в ней стоит игрок, то она не закроется до его ухода
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
        """Подключение входного и выходного портала к рычагу"""
        self.portal_set.add(input_portal)
        self.portal_set.add(output_portal)

    def connect_other_switches(self, switch):
        """Подключение других рычагов (для одновременной смены состояний)"""
        if self != switch:
            self.other_switches_set.add(switch)

    def interact_with(self, subject):
        if not self.is_paused:
            self.set_active(not self.is_active)
            # Смена состояний других рычагов
            for switch in self.other_switches_set:
                switch.set_active(self.is_active)
            # Смена направления подключенных порталов
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
        output_image = self.sprite_sheet.get_cell_image(self.kind * 2, 5)
        input_image = self.sprite_sheet.get_cell_image(self.kind * 2 + 1, 5)
        self.images = [output_image, input_image]

    def is_input(self):
        return self.is_active

    def set_input(self, is_input):
        self.set_active(is_input)

    def reverse_direction(self):
        """Смена направления портала"""
        self.set_input(not self.is_input())

    def connect_portal(self, portal):
        """Подключение другого портала в пару к текущему"""
        self.other_portal = portal

    def interact_with(self, subject):
        if self.is_input() and \
                self.other_portal is not None:
            subject.reset_walking()
            new_pos = self.other_portal.get_pos()
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
        """Определение изображения для уровня в зависимости от того, пройден он или нет"""
        self.image = get_empty_image(SPRITE_SIZE, SPRITE_SIZE * 2)
        if not self.is_unlocked:
            image = self.sprite_sheet.get_cell_image(0, 0)
            color = None
        elif not self.is_done:
            image = self.sprite_sheet.get_cell_image(1, 0)
            color = WHITE
        else:
            image = self.sprite_sheet.get_cell_image(2, 0)
            color = GREEN
        self.image.blit(image, (0, 0))
        if color is not None:
            display_text(self.image, str(self.number), 24, color,
                         SPRITE_SIZE // 2, SPRITE_SIZE + SPRITE_SIZE // 2)

    def get_levelname(self):
        """Получение имени файла по номеру уровня"""
        return f"level{self.number}.txt"
