from typing import Optional, Union
from sprites import *
from elements import Door


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
