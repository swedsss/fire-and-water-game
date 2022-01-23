from functions import *


class SpriteSheet:
    """Набор спрайтов"""

    def __init__(self, file_name):
        self.sprite_sheet = pygame.image.load(file_name).convert_alpha()

    def get_image(self, x, y, width, height):
        """Получение фрагмента из набора спрайтов, заданного координатами и размерами"""
        image = get_empty_image(width, height)
        image.blit(self.sprite_sheet, (0, 0), pygame.Rect(x, y, width, height))
        return pygame.transform.scale(image, (width, height))

    def get_cell_image(self, col, row, width=SPRITE_SIZE, height=SPRITE_SIZE):
        """Получение фрагмента, заданного столбцом и строкой"""
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
        """Получение фрагмента, заданного индексом"""
        if index < 0 or index >= 16:
            raise ValueError("Индекс должен быть в пределах от 0 до 15 включительно!")
        col, row = self.TILE_COORDS_DICT[index]
        return self.get_cell_image(col, row)


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
