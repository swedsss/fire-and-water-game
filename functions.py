from constants import *


def get_empty_image(width=SPRITE_SIZE, height=SPRITE_SIZE):
    image = pygame.Surface((width, height), pygame.SRCALPHA, 32)
    return image


def display_text(surface, text, size, color, x, y):
    """Отображение текста"""
    font = pygame.font.SysFont("sans-serif", size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    surface.blit(text_surface, text_rect)
    return text_surface
