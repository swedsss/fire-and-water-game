import pygame
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


def display_text_with_shadow(surface, text, size, text_color, shadow_color, x, y, offset):
    """Отображение текста c тенью"""
    for y_offset, color in [(offset, shadow_color), (0, text_color)]:
        display_text(surface, text, size, color, x, y + y_offset)
