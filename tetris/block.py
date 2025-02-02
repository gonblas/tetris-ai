import pygame
from enum import Enum
from collections import namedtuple
from tetris.settings import *
from pygame.math import Vector2


class Block(pygame.sprite.Sprite):
    
    def __init__(self, pos: tuple, image, group: pygame.sprite.Group):
        super().__init__(group)
        self.group = group
        self.image = pygame.image.load(image).convert_alpha()
        self.pos = Vector2(pos) + INIT_POS_OFFSET
        self.rect = self.image.get_rect(topleft = self.pos * BLOCK_SIZE)
        self.current = True


    def _set_rect_pos(self):
        self.rect.topleft = (self.pos.y.__int__() * BLOCK_SIZE, self.pos.x.__int__() * BLOCK_SIZE) 


    def update(self):
        self._set_rect_pos()



    def move(self, direction: Vector2, board):
        if(not self.check_collision(self.pos + direction, board)):
            self.pos += direction
            return True
        self.pos += direction



    def rotate(self, pivot_pos, degrees: int) -> Vector2:
        translated = self.pos - pivot_pos
        rotated = translated.rotate(degrees)
        return rotated + pivot_pos
    

    def check_collision(self, pos: Vector2, board) -> bool:
        return not ((0 <= pos.x.__int__() < ROWS  and 0 <= pos.y.__int__() < COLUMNS) and not board[pos.x.__int__()][pos.y.__int__()] )
