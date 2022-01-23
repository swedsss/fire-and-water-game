from typing import Optional
from sprites import *


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
