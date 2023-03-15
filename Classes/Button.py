from abc import ABC

import pygame


class Button(ABC):
    def __init__(self, window: pygame.Surface, pos: tuple[int, int], size: tuple[int, int]):
        import pygame
        self.window: pygame.Surface = window
        self.is_hover, self.is_click, self.click_cooldown = False, False, False
        self.rect: pygame.Rect = pygame.Rect(pos, size)
        self.pos: tuple[int, int] = pos  # Top-left
        self.size: tuple[int, int] = size  # Length, Height
    
    def update(self) -> None:
        self.is_hover = self.rect.collidepoint(pygame.mouse.get_pos())
        self.is_click = self.is_hover and pygame.mouse.get_pressed()[0] and not self.click_cooldown
        self.click_cooldown = pygame.mouse.get_pressed()[0] or self.is_click  # Requires unclick to click again
        return None
