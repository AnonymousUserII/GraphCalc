from os import path
from copy import deepcopy

import pygame


class InputBox:
    def __init__(self, window: pygame.Surface, pos: tuple[int, int], width: int,
                 init_text: str = "", text_size: int = 16):
        import pygame
        self.text_size: int = text_size
        self.text_color: tuple = (0, 0, 0, 255)
        self.font: pygame.font = pygame.font.Font(path.join("Assets", "FiraCode.ttf"), self.text_size)
        self.window: pygame.Surface = window
        self.pos: tuple[int, int] = pos  # Top-left
        self.size: tuple[int, int] = (width, int(self.text_size * 1.5))  # Length, Height
        self.rect: pygame.Rect = pygame.Rect(pos, self.size)
        
        self.is_click, self.off_click, self.click_cooldown = False, False, False
        
        self.active, self.was_active = False, False
        self.text: str = init_text
        self.text_limit: int = (width - 3) // self.font.render('m', False, self.text_size, (0, 0, 0)).get_width()
        self.cursor_pos: float = pos[0] + 5.5  # Holds x-coord of cursor
        self.index: int = len(self.text)
        self.lindex: int = self.index  # Holds position of cursor to show
        self.view: int = 0  # Holds the first character to be shown
    
    def insert_text(self, text: str, function: bool = True) -> None:
        """
        Used by the function inserts to add the function's text to the function input
        """
        self.text = self.text[:self.index] + text + self.text[self.index:]
        self.index += len(text) - (1 if function else 0)
        self.lindex += len(text) - (1 if function else 0)
        if self.lindex > self.text_limit - 1:
            over_lindex: int = deepcopy(self.lindex)
            self.lindex = self.text_limit - 1
            self.view += over_lindex - self.lindex
        return None
    
    def update(self, events, set_active: bool = False) -> bool:
        """
        Process input of InputBox.
        Returns True if input is 'submitted' or changed
        """
        old_text: str = deepcopy(self.text)
        if self.active:
            self.was_active = True
        elif self.was_active:
            self.was_active = False
        
        self.is_click = self.rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0] and not \
            self.click_cooldown
        self.off_click = not self.rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0] and not \
            self.click_cooldown
        self.click_cooldown = pygame.mouse.get_pressed()[0] or self.is_click
        
        if self.is_click:
            self.active = True
        if self.off_click and not set_active:
            self.active = False
        
        if self.active:
            if pygame.key.get_pressed()[pygame.K_RETURN]:
                self.active = False
                return True
        
        for event in events:
            if event.type == pygame.KEYDOWN and self.active:
                try:
                    if event.key == pygame.K_BACKSPACE:
                        if len(self.text) > 0 and self.index > 0:
                            self.text = self.text[:self.index - 1] + self.text[self.index:]
                            self.index -= 1 if self.index > 0 else 0
                            self.lindex -= 1
                            if self.lindex < 0:  # If backspace at start of shown text
                                self.lindex = 0
                                self.view -= 1 if self.view > 0 else 0
                    
                    elif event.key == pygame.K_DELETE:
                        if len(self.text) > 0:
                            self.text = self.text[:self.index] + self.text[self.index + 1:]
                    
                    elif event.key == pygame.K_LEFT:
                        self.index -= 1 if self.index > 0 else 0
                        self.lindex -= 1
                        if self.lindex < 0:
                            self.lindex = 0
                            self.view -= 1 if self.view > 0 else 0
                    
                    elif event.key == pygame.K_RIGHT:
                        self.index += 1 if self.index < len(self.text) else 0
                        self.lindex += 1
                        if self.lindex > min(self.text_limit, len(self.text)):
                            self.lindex = min(self.text_limit, len(self.text))
                            self.view += 1 if self.view < len(self.text) - self.text_limit else 0
                    
                    elif event.unicode in "1234567890Aabcefgilmnopqrstxy =+-*/^().$":
                        old_len: int = len(self.text)
                        self.text = self.text[:self.index] + event.unicode + self.text[self.index:]
                        self.index += len(self.text) - old_len  # Stop modifier keys from incrementing
                        self.lindex += len(self.text) - old_len
                        if self.lindex > self.text_limit:
                            self.lindex = self.text_limit
                            self.view += 1
                except AttributeError:  # If there is no ASCII for the "input" key
                    pass
        
        self.cursor_pos = min(self.rect.left + 3 + 0.585 * self.text_size * self.lindex,
                              self.rect.left + self.size[0] - 3)  # Make sure cursor doesn't leave box
        
        return old_text != self.text
    
    def draw(self) -> None:
        pygame.draw.rect(surface=self.window, color=(255, 255, 255, 255), rect=pygame.Rect(self.pos, self.size))
        box_text = self.font.render(self.text[self.view:self.view + self.text_limit], True, self.text_color)
        box = box_text.get_rect(midleft=(self.rect.midleft[0] + 3, self.rect.midleft[1]))
        self.window.blit(box_text, box)
        
        if self.active:  # Draw cursor
            pygame.draw.line(surface=self.window, color=self.text_color, start_pos=(self.cursor_pos, self.rect.top + 2),
                             end_pos=(self.cursor_pos, self.rect.bottom - 2), width=1)
        return None
