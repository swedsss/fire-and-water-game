from typing import Optional
from sprites import *


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
