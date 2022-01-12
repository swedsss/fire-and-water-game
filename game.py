import sys
import os
import pygame


SPRITE_SIZE = 32
MAX_LEVEL_SIZE = 25

TITLE = 'Огонь и вода'
SCREEN_WIDTH = MAX_LEVEL_SIZE * SPRITE_SIZE
SCREEN_HEIGHT = MAX_LEVEL_SIZE * SPRITE_SIZE

FPS = 60

BLACK = pygame.Color('black')
WHITE = pygame.Color('white')

CURRENT_DIR = os.path.dirname(__file__)
LEVELS_DIR = os.path.join(CURRENT_DIR, 'levels')
IMG_DIR = os.path.join(CURRENT_DIR, 'img')

SPRITE_FILE_WALLS = "walls.png"
SPRITE_FILE_FLOOR = "floor.png"
SPRITE_FILE_FIRE_PLAYER = "fire_player.png"
SPRITE_FILE_WATER_PLAYER = "water_player.png"

LEVEL_ELEM_FLOOR = "."
LEVEL_ELEM_WALL = "#"
LEVEL_ELEM_FIRE_PLAYER = "1"
LEVEL_ELEM_WATER_PLAYER = "2"

PLAYER_STEP = SPRITE_SIZE // 8
PlAYER_ANIMATION_DURATION = 100


def load_image(name, colorkey=None):
    """
    Загрузка изображения спрайта
    :param name: имя файла
    :param colorkey: фоновый цвет
    :return: спрайт
    """
    fullname = os.path.join(name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    width, height = image.get_rect().size
    return pygame.transform.scale(image, (width, height))


class SpriteSheet:
    """Набор спрайтов"""
    def __init__(self, file_name):
        self.sprite_sheet = pygame.image.load(file_name).convert()

    def get_image(self, x, y, width, height):
        image = pygame.Surface((width, height)).convert()
        image.blit(self.sprite_sheet, (0, 0), pygame.Rect(x, y, width, height))
        image.set_colorkey(BLACK)
        return pygame.transform.scale(image, (width, height))


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
        return self.get_image(SPRITE_SIZE * col, SPRITE_SIZE * row, SPRITE_SIZE, SPRITE_SIZE)


class Sprite(pygame.sprite.Sprite):
    """Общий класс для всех спрайтов на экране"""
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((SPRITE_SIZE, SPRITE_SIZE)).convert()
        self.rect = self.image.get_rect()

    def get_pos(self):
        return self.rect.centerx, self.rect.centery

    def set_pos(self, x, y):
        self.rect.centerx = x
        self.rect.centery = y

    def set_cell_pos(self, col, row):
        self.set_pos(col * SPRITE_SIZE + SPRITE_SIZE // 2, row * SPRITE_SIZE + SPRITE_SIZE // 2)


class Wall(Sprite):
    """Класс для спрайта стены"""
    class_init_done = False
    SPRITES = []

    @classmethod
    def class_init(cls):
        edge_sheet = EdgeSpriteSheet(os.path.join(IMG_DIR, SPRITE_FILE_WALLS))
        cls.SPRITES = [edge_sheet.get_image_by_index(i) for i in range(16)]
        cls.class_init_done = True

    def __init__(self, col, row, index):
        super().__init__()
        if self.class_init_done is False:
            self.class_init()
        self.image = self.SPRITES[index].convert()
        self.rect = self.image.get_rect()
        self.set_cell_pos(col, row)


class Floor(Sprite):
    """Класс для спрайта пола"""
    class_init_done = False
    SPRITES = None

    @classmethod
    def class_init(cls):
        edge_sheet = EdgeSpriteSheet(os.path.join(IMG_DIR, SPRITE_FILE_FLOOR))
        cls.SPRITES = [edge_sheet.get_image_by_index(i) for i in range(16)]
        cls.class_init_done = True

    def __init__(self, col, row):
        super().__init__()
        if self.class_init_done is False:
            self.class_init()
        self.image = self.SPRITES[0].convert()
        self.rect = self.image.get_rect()
        self.set_cell_pos(col, row)


class Player(Sprite):
    """Общий класс для игроков"""
    def __init__(self, col, row):
        super().__init__()
        self.sprite_sheet = None
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

        self.walk_to_pos = None
        self.current_sprite_index = None
        self.last_anim_tick = None

    def define_sprite_sheet(self):
        pass

    def load_sprites(self):
        """Загрузка спрайтов для анимаций перемещения"""
        for row, sprite_list in enumerate([self.down_sprites, self.left_sprites,
                                           self.right_sprites, self.up_sprites]):
            for col in range(4):
                image = self.sprite_sheet.get_image(col * SPRITE_SIZE, row * SPRITE_SIZE,
                                                    SPRITE_SIZE, SPRITE_SIZE)
                sprite_list.append(image)

    def move_to_cell(self, col, row, stop_group):
        """Перемещение в соседнню клетку"""
        if self.walk_to_pos is not None:
            return
        pos_before_move = self.get_pos()
        self.rect = self.rect.move(col * SPRITE_SIZE, row * SPRITE_SIZE)
        pos_after_move = self.get_pos()
        can_walk = not pygame.sprite.spritecollideany(self, stop_group)

        if pos_after_move != pos_before_move:
            self.change_sprites(pos_before_move, pos_after_move)
        else:
            return

        if can_walk:
            self.walk_to_pos = pos_after_move
        else:
            self.image = self.sprites[-1]
            self.rect = self.image.get_rect()

        self.set_pos(*pos_before_move)

    def change_sprites(self, old_pos, new_pos):
        if new_pos[0] < old_pos[0]:
            self.sprites = self.left_sprites
        elif new_pos[0] > old_pos[0]:
            self.sprites = self.right_sprites
        elif new_pos[1] < old_pos[1]:
            self.sprites = self.up_sprites
        elif new_pos[1] > old_pos[1]:
            self.sprites = self.down_sprites

    def update(self):
        if self.walk_to_pos is None:
            return

        self.animate()

        if self.walk_to_pos == self.get_pos():
            self.reset_animation()

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
            step = min([max([abs(self.walk_to_pos[0] - self.rect.x),
                             abs(self.walk_to_pos[1] - self.rect.y)]), PLAYER_STEP])
            self.change_sprites(self.get_pos(), self.walk_to_pos)
            if self.walk_to_pos[0] < self.rect.centerx:
                self.rect.centerx -= step
            elif self.walk_to_pos[0] > self.rect.centerx:
                self.rect.centerx += step
            if self.walk_to_pos[1] < self.rect.centery:
                self.rect.centery -= step
            elif self.walk_to_pos[1] > self.rect.centery:
                self.rect.centery += step
            pos_x, pos_y = self.get_pos()
            self.image = self.sprites[self.current_sprite_index]
            self.rect = self.image.get_rect()
            self.set_pos(pos_x, pos_y)

    def reset_animation(self):
        self.walk_to_pos = None
        self.current_sprite_index = None
        self.last_anim_tick = None


class FirePlayer(Player):
    """Класс для игрока 'Огонь'"""
    def __init__(self, col, row):
        super().__init__(col, row)

    def define_sprite_sheet(self):
        self.sprite_sheet = SpriteSheet(os.path.join(IMG_DIR, SPRITE_FILE_FIRE_PLAYER))


class WaterPlayer(Player):
    """Класс для игрока 'Вода'"""
    def __init__(self, col, row):
        super().__init__(col, row)

    def define_sprite_sheet(self):
        self.sprite_sheet = SpriteSheet(os.path.join(IMG_DIR, SPRITE_FILE_WATER_PLAYER))


class Level:
    """Уровень игры"""
    def __init__(self, filename):
        self.filename = filename
        self.width, self.height = 0, 0
        self.elems = []
        self.fire_player_pos = None
        self.water_player_pos = None
        self.load_level(filename)

    def load_level(self, filename):
        """Загрузка уровня"""
        fullname = os.path.join(LEVELS_DIR, filename)

        with open(fullname) as f:
            data = [line.strip() for line in f.readlines()]

        self.width = max(map(len, data))
        self.height = len(data)
        data = list(map(lambda x: x.ljust(self.width, '.'), data))

        self.elems = [[-1] * self.width for _ in range(self.height)]
        for row, line in enumerate(data):
            for col, elem in enumerate(line):
                if elem == LEVEL_ELEM_WALL:
                    self.elems[row][col] = 0
                elif elem == LEVEL_ELEM_FIRE_PLAYER:
                    self.fire_player_pos = col, row
                elif elem == LEVEL_ELEM_WATER_PLAYER:
                    self.water_player_pos = col, row

        self.connect_near_walls()

    def connect_near_walls(self):
        """Расчёт индекса отображаемого спрайта стены с учётом соседних стен"""
        for row in range(self.height):
            for col in range(self.width):
                if self.elems[row][col] < 0:
                    continue
                wall_index = 0
                near_list = [(col, row - 1, 1), (col + 1, row, 2),
                             (col, row + 1, 4), (col - 1, row, 8)]
                for near_col, near_row, weight in near_list:
                    if not self.cell_on_board(near_col, near_row):
                        continue
                    if self.elems[near_row][near_col] >= 0:
                        wall_index += weight
                self.elems[row][col] = wall_index

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

        self.running = True
        self.game_over = False

        self.all_sprites = pygame.sprite.Group()
        self.wall_sprites = pygame.sprite.Group()

        self.fire_player = None
        self.water_player = None

        self.level = None

    def new_game(self):
        """Создание новой игры"""
        self.all_sprites.empty()

        self.level = Level('level1.txt')
        for row in range(self.level.height):
            for col in range(self.level.width):
                if self.level.elems[row][col] >= 0:
                    level_sprite = Wall(col, row, self.level.elems[row][col])
                    self.wall_sprites.add(level_sprite)
                else:
                    level_sprite = Floor(col, row)

                self.all_sprites.add(level_sprite)

        if self.level.fire_player_pos is not None:
            self.fire_player = FirePlayer(*self.level.fire_player_pos)
            self.all_sprites.add(self.fire_player)
        if self.level.water_player_pos is not None:
            self.water_player = WaterPlayer(*self.level.water_player_pos)
            self.all_sprites.add(self.water_player)

    def process_events(self):
        """Обработка событий игры"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self.fire_player.move_to_cell(-1, 0, self.wall_sprites)
                elif event.key == pygame.K_d:
                    self.fire_player.move_to_cell(1, 0, self.wall_sprites)
                elif event.key == pygame.K_w:
                    self.fire_player.move_to_cell(0, -1, self.wall_sprites)
                elif event.key == pygame.K_s:
                    self.fire_player.move_to_cell(0, 1, self.wall_sprites)
                elif event.key == pygame.K_LEFT:
                    self.water_player.move_to_cell(-1, 0, self.wall_sprites)
                elif event.key == pygame.K_RIGHT:
                    self.water_player.move_to_cell(1, 0, self.wall_sprites)
                elif event.key == pygame.K_UP:
                    self.water_player.move_to_cell(0, -1, self.wall_sprites)
                elif event.key == pygame.K_DOWN:
                    self.water_player.move_to_cell(0, 1, self.wall_sprites)

    def update(self):
        """Обновление спрайтов"""
        self.all_sprites.update()

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


def main():
    mygame = Game()

    while mygame.running:
        mygame.new_game()
        mygame.run()

    pygame.quit()


if __name__ == "__main__":
    main()
