from os import path
import pygame

from Classes.Button import Button


class SpriteButton(Button):
    def __init__(self, window: pygame.Surface, pos: tuple[int, int], size: tuple[int, int], text: str,
                 text_color: tuple, text_size: int, norm_sprite: pygame.Surface, hover_sprite: pygame.Surface = None):
        super().__init__(window, pos, size)
        
        self.text: str = text
        self.text_size: int = text_size
        self.text_color: tuple = text_color
        self.label = pygame.font.Font(path.join("Assets", "FiraCode.ttf"), text_size).render(text, True, text_color)
        self.label_box = self.label.get_rect(center=self.rect.center)
        
        self.click_sound: pygame.mixer.Sound = pygame.mixer.Sound(path.join("Assets", "thock.wav"))
        pygame.mixer.Channel(4).set_volume(0.4)
        
        self.sprite: pygame.Surface = norm_sprite  # Holds button's current color
        self.norm_sprite: pygame.Surface = norm_sprite
        self.hover_sprite: pygame.Surface = hover_sprite if hover_sprite else norm_sprite
    
    def update(self) -> bool:
        super().update()
        if self.is_click:
            pygame.mixer.Channel(4).play(self.click_sound)
        orig_sprite: pygame.Surface = self.sprite
        self.sprite = self.hover_sprite if self.is_hover else self.norm_sprite
        return orig_sprite != self.sprite  # If there is a change in sprite
    
    def draw(self) -> None:
        self.label = pygame.font.Font(path.join("Assets", "FiraCode.ttf"), self.text_size)\
            .render(self.text, True, self.text_color)
        self.label_box = self.label.get_rect(center=self.rect.center)
        self.window.blit(self.sprite, self.rect)
        self.window.blit(self.label, self.label_box)
        return None
