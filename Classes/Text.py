from os import path
import pygame


class Text:
    def __init__(self, window: pygame.Surface, text: str, text_size: int, color: tuple, pos: tuple[int, int]):
        self.window: pygame.Surface = window
        self.text: str = text
        self.text_size: int = text_size
        self.color: tuple[int, int, int] = color
        self.pos: tuple[int, int] = pos
        self.font: pygame.font = pygame.font.Font(path.join("Assets", "FiraCode.ttf"), self.text_size)
    
    def draw(self, from_right: bool = False) -> None:
        label: pygame.Surface = self.font.render(self.text, True, self.color)
        label_box: pygame.Rect = label.get_rect(topleft=self.pos)
        if from_right:
            label_box.right = self.pos[0]
        self.window.blit(label, label_box)
        return None
    
    def hide(self, color: tuple, from_right: bool = False) -> None:
        label: pygame.Surface = self.font.render(self.text, True, color, color)
        label_box: pygame.Rect = label.get_rect(topleft=self.pos)
        if from_right:
            label_box.right = self.pos[0]
        self.window.blit(label, label_box)
        return None
