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


class Level:
    """Уровень игры"""
    def __init__(self, filename):
        self.filename = filename
        self.width, self.height = 0, 0
        self.data = []
        self.load_level(filename)

    def load_level(self, filename):
        """Загрузка уровня"""
        fullname = os.path.join(LEVELS_DIR, filename)

        with open(fullname) as f:
            data = [line.strip() for line in f.readlines()]

        self.width = max(map(len, data))
        self.height = len(data)
        data = list(map(lambda x: x.ljust(self.width, '.'), data))
        self.data = data


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

        self.level = None

    def new_game(self):
        """Создание новой игры"""
        self.all_sprites.empty()

        self.level = Level('level1.txt')

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

        # Отображение прямоугольников на месте стен
        for row in range(self.level.height):
            for col in range(self.level.width):
                if self.level.data[row][col] == LEVEL_ELEM_WALL:
                    pygame.draw.rect(self.screen, WHITE, (col * SPRITE_SIZE, row * SPRITE_SIZE,
                                                          SPRITE_SIZE, SPRITE_SIZE))

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
