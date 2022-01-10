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

SPRITE_FILE_WALLS = 'walls.png'
SPRITE_FILE_FLOOR = "floor.png"

LEVEL_ELEM_FLOOR = "."
LEVEL_ELEM_WALL = "#"


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


class Wall(pygame.sprite.Sprite):
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
        self.set_pos(col, row)

    def set_pos(self, col, row):
        self.rect.x = col * SPRITE_SIZE
        self.rect.y = row * SPRITE_SIZE


class Floor(pygame.sprite.Sprite):
    """Класс для спрайта пола"""
    class_init_done = False
    SPRITES = None

    @classmethod
    def class_init(cls):
        cls.SPRITES = [load_image(os.path.join(IMG_DIR, SPRITE_FILE_FLOOR))]
        cls.class_init_done = True

    def __init__(self, col, row):
        super().__init__()
        if self.class_init_done is False:
            self.class_init()
        self.image = self.SPRITES[0].convert()
        self.rect = self.image.get_rect()
        self.set_pos(col, row)

    def set_pos(self, col, row):
        self.rect.x = col * SPRITE_SIZE
        self.rect.y = row * SPRITE_SIZE


class Level:
    """Уровень игры"""
    def __init__(self, filename):
        self.filename = filename
        self.width, self.height = 0, 0
        self.elems = []
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

        self.level = None

    def new_game(self):
        """Создание новой игры"""
        self.all_sprites.empty()

        self.level = Level('level1.txt')
        for row in range(self.level.height):
            for col in range(self.level.width):
                if self.level.elems[row][col] < 0:
                    level_sprite = Floor(col, row)
                else:
                    level_sprite = Wall(col, row, self.level.elems[row][col])
                    self.wall_sprites.add(level_sprite)
                self.all_sprites.add(level_sprite)

    def process_events(self):
        """Обработка событий игры"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
                self.running = False

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
