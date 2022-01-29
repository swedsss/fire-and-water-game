import sys
from typing import Union
import pygame
from constants import *
from sprites import BaseSprite
from sprites import Floor, Wall, Lava, River, Acid
from sprites import FirePlayer, WaterPlayer
from sprites import ElementSprite, Ruby, Aquamarine, FireExit, WaterExit
from sprites import DoorButton, Door, PortalSwitch, Portal
from screens import StartScreen, EndScreen


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
        """Определение вида элемента по его обозначению"""
        return 1 if elem.isupper() else 0

    def load_level(self, filename):
        """Загрузка уровня"""
        fullname = os.path.join(LEVELS_DIR, filename)

        with open(fullname) as f:
            data = [line.rstrip() for line in f.readlines()]

        # Определение размеров уровня
        self.width = min([max(map(len, data)), MAX_LEVEL_SIZE])
        self.height = min([len(data), MAX_LEVEL_SIZE])
        # Определение сдвига при отображении спрайтов уровня
        self.col_offset = (MAX_LEVEL_SIZE - self.width) // 2
        self.row_offset = (MAX_LEVEL_SIZE - self.height) // 2
        # Добавление пустых элементов в неполных строках
        # и обрезка уровня, который превышает максимальные размеры
        data = list(map(lambda x: x[:self.width].ljust(self.width, LEVEL_BLOCK_EMPTY),
                        data[:self.height]))

        # Множество обозначений блоков
        blocks_set = {LEVEL_BLOCK_EMPTY, LEVEL_BLOCK_WALL, LEVEL_BLOCK_FLOOR,
                      LEVEL_BLOCK_LAVA, LEVEL_BLOCK_RIVER, LEVEL_BLOCK_ACID}
        # Меожество обозначений элементов,
        # которые могут присутствовать на уровне в единственном экземпляре
        elem_single_set = {LEVEL_ELEM_FIRE_EXIT, LEVEL_ELEM_WATER_EXIT,
                           LEVEL_ELEM_INPUT_PORTAL_1, LEVEL_ELEM_INPUT_PORTAL_2,
                           LEVEL_ELEM_OUTPUT_PORTAL_1, LEVEL_ELEM_OUTPUT_PORTAL_2}
        # Меожество обозначений элементов,
        # которые может быть несколько на уровне
        elems_multi_set = {LEVEL_ELEM_RUBY, LEVEL_ELEM_AQUAMARINE,
                           LEVEL_ELEM_DOORBUTTON_1, LEVEL_ELEM_DOORBUTTON_2,
                           LEVEL_ELEM_DOOR_1, LEVEL_ELEM_DOOR_2,
                           LEVEL_ELEM_PORTAL_SWITCH_1, LEVEL_ELEM_PORTAL_SWITCH_2}

        # Заполнение данных об уровне
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

        # Подсчёт индексов на уровне
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

        # Группы спрайтов
        self.all_sprites = pygame.sprite.Group()
        self.wall_sprites = pygame.sprite.Group()
        self.lava_sprites = pygame.sprite.Group()
        self.river_sprites = pygame.sprite.Group()
        self.acid_sprites = pygame.sprite.Group()

        self.elements_sprites = pygame.sprite.Group()
        self.door_sprites = pygame.sprite.Group()

        # Уникальные объекты
        self.fire_player = None
        self.water_player = None
        self.fire_exit = None
        self.water_exit = None

        self.connection_dict = {}

    def reset_game(self):
        """Сброс атрибутов игры"""
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

        # Создание объекта с данными уровня
        level = Level(levelname)
        # Загрузка сдвига для текущего уровня
        BaseSprite.set_offset(level.col_offset, level.row_offset)

        # Создание спрайтов для блоков уровня
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

        # Создание спрайтов для элементов уровня
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

                # Добавление элементов в словарь соединений
                if elem not in self.connection_dict:
                    self.connection_dict[elem] = []
                self.connection_dict[elem].append(level_sprite)

                self.elements_sprites.add(level_sprite)
                self.all_sprites.add(level_sprite)

        # Создание спрайтов для игроков
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

        # Соединение элементов
        self.connect_elements()

        self.win_game = False
        self.game_over = False

    def connect_elements(self):
        """Соединение элементов для корректной обработки взаимодействий"""
        # Соединение камней, выходов из уровня и игроков
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

        # Соединение кнопок, дверей и игроков
        for level_elem_doorbutton, level_elem_door in \
                [(LEVEL_ELEM_DOORBUTTON_1, LEVEL_ELEM_DOOR_1),
                 (LEVEL_ELEM_DOORBUTTON_2, LEVEL_ELEM_DOOR_2)]:

            if level_elem_doorbutton in self.connection_dict and \
                    level_elem_door in self.connection_dict:
                for button in self.connection_dict[level_elem_doorbutton]:
                    for door in self.connection_dict[level_elem_door]:
                        button.connect_door(door)
                        door.connect_button(button)
                        door.connect_players(self.fire_player, self.water_player)

        # Соединение рычагов и порталов
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
                # Выход из уровня по кнопке Escape
                if event.key == pygame.K_ESCAPE:
                    self.game_over = True
                    self.with_end_screen = False

                # Клавиши для перемещения игроков
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

        # Уровень не пройден, если один из игроков не выжил
        for player in [self.fire_player, self.water_player]:
            if player is not None and not player.is_alive:
                self.win_game = False
                self.game_over = True
                self.with_end_screen = True
                return

        # Уровень пройден, если произошло взаимодейтвие игроков с обоими выходами одновременно
        if self.fire_exit is not None and self.fire_exit.is_interacted and \
                self.water_exit is not None and self.water_exit.is_interacted:
            self.win_game = True
            self.start_screen.unlock_new_level()
            self.game_over = True
            self.with_end_screen = True
            return

        # Сброс признака взаимодействия со всех элементов уровня
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
        """Показ начального экрана"""
        self.start_screen.show(self.screen)
        self.levelname = self.start_screen.level_sprite.get_levelname()

    def show_end_screen(self):
        """Показ конечного экрана"""
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
