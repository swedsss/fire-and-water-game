import sys
import csv
from typing import Optional
import pygame
from constants import *
from functions import display_text_with_shadow
from sprites import BaseSprite, LevelSprite


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
        surface.fill(SCREEN_COLORS_DICT[SCREEN_BG_COLOR1])
        pygame.draw.rect(surface, SCREEN_COLORS_DICT[SCREEN_BG_COLOR2], self.text_rect)
        pygame.draw.rect(surface, SCREEN_COLORS_DICT[SCREEN_SHADOW_COLOR], self.shadow_rect)
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
        display_text_with_shadow(surface, 'ВЫБЕРИТЕ УРОВЕНЬ:', 50,
                                 SCREEN_COLORS_DICT[SCREEN_TEXT_COLOR],
                                 SCREEN_COLORS_DICT[SCREEN_SHADOW_COLOR],
                                 SCREEN_WIDTH // 2, SCREEN_WIDTH // 5, 4)
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
    ATTRIB_OFFSET = 120
    VALUE_OFFSET = 40

    def __init__(self):
        super().__init__()
        self.game_info = None

    def set_info(self, game_info):
        """Установка результатов игры"""
        self.game_info = game_info

    def render(self, surface):
        self.prepare(surface)
        if self.game_info.win_game:
            result_text = 'УРОВЕНЬ ПРОЙДЕН!'
        else:
            result_text = 'УРОВЕНЬ НЕ ПРОЙДЕН!'
        display_text_with_shadow(surface, result_text, 60,
                                 SCREEN_COLORS_DICT[SCREEN_TEXT_COLOR],
                                 SCREEN_COLORS_DICT[SCREEN_SHADOW_COLOR],
                                 SCREEN_WIDTH // 2, SCREEN_WIDTH // 5, 4)

        attrib_y = SCREEN_HEIGHT // 3
        value_y = attrib_y + self.VALUE_OFFSET
        display_text_with_shadow(surface, "Результат игры", 40,
                                 SCREEN_COLORS_DICT[SCREEN_TEXT_COLOR],
                                 SCREEN_COLORS_DICT[SCREEN_SHADOW_COLOR],
                                 SCREEN_WIDTH // 2, attrib_y, 4)
        color = COLOR_GREEN if self.game_info.win_game else COLOR_RED
        display_text_with_shadow(surface, self.game_info.get_players_status_text(), 30,
                                 color,
                                 COLOR_BLACK,
                                 SCREEN_WIDTH // 2, value_y, 2)

        attrib_y += self.ATTRIB_OFFSET
        value_y = attrib_y + self.VALUE_OFFSET
        display_text_with_shadow(surface, "Общее время игры", 40,
                                 SCREEN_COLORS_DICT[SCREEN_TEXT_COLOR],
                                 SCREEN_COLORS_DICT[SCREEN_SHADOW_COLOR],
                                 SCREEN_WIDTH // 2, attrib_y, 4)
        display_text_with_shadow(surface, self.game_info.get_duration(DURATION_GAME_TIME), 30,
                                 COLOR_WHITE,
                                 COLOR_BLACK,
                                 SCREEN_WIDTH // 2, value_y, 2)

        attrib_y += self.ATTRIB_OFFSET
        value_y = attrib_y + self.VALUE_OFFSET
        display_text_with_shadow(surface, "Количество собранных камней", 40,
                                 SCREEN_COLORS_DICT[SCREEN_TEXT_COLOR],
                                 SCREEN_COLORS_DICT[SCREEN_SHADOW_COLOR],
                                 SCREEN_WIDTH // 2, attrib_y, 4)
        stone_text = ' из '.join([str(num) for num in self.game_info.get_ruby_info()])
        display_text_with_shadow(surface, stone_text, 30,
                                 SCREEN_COLORS_DICT[SCREEN_FIRE_TEXT_COLOR],
                                 SCREEN_COLORS_DICT[SCREEN_FIRE_SHADOW_COLOR],
                                 SCREEN_WIDTH // 3, value_y, 1)
        stone_text = ' из '.join([str(num) for num in self.game_info.get_aquamarine_info()])
        display_text_with_shadow(surface, stone_text, 30,
                                 SCREEN_COLORS_DICT[SCREEN_WATER_TEXT_COLOR],
                                 SCREEN_COLORS_DICT[SCREEN_WATER_SHADOW_COLOR],
                                 SCREEN_WIDTH * 2 // 3, value_y, 2)

        attrib_y += self.ATTRIB_OFFSET
        value_y = attrib_y + self.VALUE_OFFSET
        display_text_with_shadow(surface, "Время активации портала", 40,
                                 SCREEN_COLORS_DICT[SCREEN_TEXT_COLOR],
                                 SCREEN_COLORS_DICT[SCREEN_SHADOW_COLOR],
                                 SCREEN_WIDTH // 2, attrib_y, 4)
        display_text_with_shadow(surface,
                                 self.game_info.get_duration(DURATION_FIRE_EXIT_ACTIVATION), 30,
                                 SCREEN_COLORS_DICT[SCREEN_FIRE_TEXT_COLOR],
                                 SCREEN_COLORS_DICT[SCREEN_FIRE_SHADOW_COLOR],
                                 SCREEN_WIDTH // 3, value_y, 2)
        display_text_with_shadow(surface,
                                 self.game_info.get_duration(DURATION_WATER_EXIT_ACTIVATION), 30,
                                 SCREEN_COLORS_DICT[SCREEN_WATER_TEXT_COLOR],
                                 SCREEN_COLORS_DICT[SCREEN_WATER_SHADOW_COLOR],
                                 SCREEN_WIDTH * 2 // 3, value_y, 2)

        pygame.display.flip()
