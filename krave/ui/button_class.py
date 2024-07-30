import pygame
from krave.ui.constants import Colors

class Button(object):
     def __init__(self, x,y,width,height, color):
          self._x = x
          self._y = y
          self._width = width
          self._height = height
          self._color = color
          self.activated = False

          pygame.font.init()
          self._LETTER_FONT = pygame.font.SysFont('comicsans', 20)
          self._WORD_FONT = pygame.font.SysFont('comicsans', 30 - self.width //7)
          self._TITLE_FONT = pygame.font.SysFont('comicsans', 50)

     #SETTERS AND GETTERS
     @property
     def x(self):
          return self._x
     @x.setter
     def x(self, value):
          self._x = value
     
     @property
     def y(self):
          return self._y
     @y.setter
     def y(self, value):
          self._y = value
     
     @property
     def width(self):
          return self._width
     @width.setter
     def width(self, value):
          self._width = value
     
     @property
     def height(self):
          return self._height
     @height.setter
     def height(self, value):
          self._height = value
     
     @property
     def color(self):
          return self._color
     @color.setter
     def color(self, newColor):
          self._color = newColor
     
     #METHODS
     def pressed(self, x2, y2):
          if(x2 >= self._x and x2 <= self._x + self._width):
               if((y2 >= self._y and y2 <= self._y + self._height)):
                    return True
          return False
     
     def display_text(self, in_text, win):
        self._WORD_FONT = pygame.font.SysFont('comicsans', self.width // len(in_text))
        text = self._WORD_FONT.render(in_text, 1, Colors.WHITE)
        text_rect = text.get_rect(center=(self._x + self._width / 2, self._y + self._height / 2))
        win.blit(text, text_rect.topleft)

     def draw(self, text_in, win):
          pygame.draw.rect(win, self._color, (self._x, self._y, self._width, self._height))
          self.display_text(text_in, win)
