import sys
import csv
from typing import Optional
from sprites import *


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


class SaveFile:
    """Класс для файла с сохранением прогресса"""

    def __init__(self):
        self.filename = os.path.join(CURRENT_DIR, CSV_FILE_SAVE)
        self.headers = ["levels_done"]

        self.levels_done = 0

        self.load_values()

    def load_values(self):
        """Загрузка пройденного прогресса"""
        try:
            with open(self.filename, 'r', encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';')
                for line in reader:
                    if "levels_done" in line:
                        self.levels_done = int(line["levels_done"])
        except FileNotFoundError:
            return

    def save_values(self):
        """Сохранение пройденного прогресса"""
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

    def reset_screen(self):
        """Сброс необходимых атрибутов перед показаом экрана"""
        BaseSprite.reset_offset()
        self.screen_sprites.empty()

    def prepare(self, surface):
        """Прорисовка общего фона для экранов"""
        surface.fill(self.bg_color1)
        pygame.draw.rect(surface, self.bg_color2, self.text_rect)
        pygame.draw.rect(surface, self.shadow_color, self.shadow_rect)
        image = pygame.image.load(os.path.join(IMG_DIR, IMG_FILE_TITLE)).convert_alpha()
        rect = image.get_rect()
        surface.blit(image, rect)

    def render(self, surface):
        """Отрисовка всех элементов экрана"""
        # Метод реализован в дочерних классах
        pass

    def process_events(self):
        """Обработка событий экрана"""
        self.pause()

    @staticmethod
    def pause():
        """Пауза"""
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                # Ожидание нажатия на Escape, Enter или пробел
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN]:
                        waiting = False

    def show(self, surface):
        """Переключение на текущий экран"""
        self.reset_screen()
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
        super().reset_screen()
        self.level_sprites.empty()
        self.create_levels()
        self.level_sprite = None

    def create_levels(self):
        """Создание спрайтов уровней"""
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
        """Разблокировка следующего уровня"""
        # Следующий уровень разблокируется если был пройден ещё не пройденный уровень
        if self.level_sprite.number > self.save_file.levels_done:
            self.save_file.levels_done += 1
            self.save_file.save_values()


class EndScreen(Screen):
    """Конечный экран для отображения результатов"""

    def __init__(self):
        super().__init__()
        self.win_game = False

    def set_result(self, result):
        """Установка результатов игры"""
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
