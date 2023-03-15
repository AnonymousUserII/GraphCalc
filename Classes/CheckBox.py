from os import path
import pygame

from Classes.Button import Button


class CheckBox(Button):
    def __init__(self, window: pygame.Surface, pos: tuple[int, int], size: int, color: tuple, start_on: bool = False):
        super().__init__(window, pos, (size, size))
        self.color: tuple = color
        self.on: bool = start_on

        self.click_sound: pygame.mixer.Sound = pygame.mixer.Sound(path.join("Assets", "thock.wav"))
        pygame.mixer.Channel(4).set_volume(0.4)
    
    def update(self) -> bool:
        """
        Returns True if the checkbox was updated
        :return: self.is_click
        """
        super(CheckBox, self).update()
        if self.is_click:
            self.on = not self.on
            pygame.mixer.Channel(4).play(self.click_sound)
        return self.is_click
    
    def draw(self) -> None:
        pygame.draw.rect(surface=self.window, color=(255, 255, 255), rect=pygame.Rect(self.pos, self.size))
        pygame.draw.rect(surface=self.window, color=self.color, rect=pygame.Rect(self.pos, self.size), width=2)
    
        smaller_pos: list[int, int] = [p + 3 for p in self.pos]
        smaller_size: list[int, int] = [s - 6 for s in self.size]
        if self.on:  # Draw a smaller square inside to show as active
            pygame.draw.rect(surface=self.window, color=self.color, rect=pygame.Rect(smaller_pos, smaller_size))
        else:  # Draw a blank square inside to show as inactive
            pygame.draw.rect(surface=self.window, color=(255, 255, 255), rect=pygame.Rect(smaller_pos, smaller_size))
        return None
