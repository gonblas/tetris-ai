import pygame
from tetris.tetromino import Tetromino
from tetris.block import Block
from tetris.timer import Timer # type: ignore
import random
from tetris.settings import *
from tetris.ui.board import Board
from tetris.ui.score import Score
from tetris.ui.preview import Preview
import numpy as np
from pygame import Vector2
import sys



class Game:
    def __init__(self, user_mode: bool = True) -> None:
        self.user_mode = user_mode       

        # Pygame settings
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.display_surface = pygame.display.get_surface()     
        

        # UI and pygame
        pygame.init()
        self.board_ui = Board()
        self.preview_ui = Preview()
        self.score_ui = Score()
        

        self.icon = pygame.image.load(ICON_PATH)
        pygame.display.set_icon(self.icon)

        self.music = pygame.mixer.music.load(MUSIC_PATH)
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.2)
        
        self._init_game()
        

    def _move(self):
        self.cur_tetromino.update()

    def _timer_update(self):
        for timer in self.timers.values():
            timer.update()

    def _check_game_over(self):
        for block in self.cur_tetromino.blocks:
            if(len(pygame.sprite.spritecollide(block, self.board_sprites, False))>0):
                self.game_over = True

    def _init_game(self):
        # Data
        self.score: int = 0
        self.level: int = 0 
        self.lines: int = 0
        self.game_over = False
        
        #Game Logic
        self.board = [[0 for _ in range(COLUMNS)] for _ in range(ROWS)]    

        #Sprites
        self.sprites = pygame.sprite.Group()
        self.board_sprites = pygame.sprite.Group()  
        
        self.piece_frequency = [1 for _ in range(7)]
        self.next_pieces = [self._get_random_shape() for _ in range(3)]
        self.cur_tetromino: Tetromino = Tetromino(shape = self._get_next_piece(),  group = self.sprites, board = self.board, current = True)
        
        
        #Speed
        self.down_speed = UPDATE_START_SPEED
        self.down_speed_faster = self.down_speed * 0.25
        self.down_pressed = False
        self.timers = {
			'vertical move': Timer(self.down_speed, True, self._move),
			'horizontal move': Timer(MOVE_WAIT_TIME),
			'rotate': Timer(ROTATE_WAIT_TIME),
		}
        
        self.timers['vertical move'].activate()


    def reset(self):
        self._init_game()
        self.score_ui.update_score(score=self.score, level=self.level, lines=self.lines)
        self.update()
        

    def _check_landing(self):
        if(self.cur_tetromino.landing == True):
            self.speed_up = False
            for block in self.cur_tetromino.blocks:
                block.current = False
                self.board_sprites.add(block)
                self.board[block.pos.x.__int__()][block.pos.y.__int__()] = block #type: ignore
            self._check_completed_lines()
            self.cur_tetromino = Tetromino(shape = self._get_next_piece(), group = self.sprites, board = self.board)

            
    def _check_completed_lines(self):
        full_lines = self._check_lines()
        if (len(full_lines) > 0):
            for line in full_lines:
                for block in self.board[line]:
                    block.kill()
                for row in self.board:
                    for block in row:
                        if isinstance(block, Block) and block.pos.x < line:
                            block.pos.x += 1
                self.board = [[0 for _ in range(COLUMNS)] for _ in range(ROWS)]
                for block in self.sprites:
                    if block.current == False:
                        self.board[block.pos.x.__int__()][block.pos.y.__int__()] = block
                        
            self._calculate_score(len(full_lines))

    def _check_lines(self) -> list:
        full_lines = []
        for i,row in enumerate(self.board):
            if all([block for block in row]):
                full_lines.append(i)
                
        return full_lines

    def _calculate_score(self,lines: int) -> None:
        self.lines += lines
        self.score += SCORE_DATA[lines] * (self.level + 1)

        if (self.lines // ((self.level + 1) * 10) > 0):
            self.level += 1
            self.down_speed = round(self.down_speed * (0.98-((self.level)*0.0025))**(self.level))
            self.timers['vertical move'].duration = self.down_speed
            self.down_speed_faster = self.down_speed * 0.25
            
            self.timers['vertical move'].duration = self.down_speed
            
        self.score_ui.update_score(score=self.score, level=self.level, lines=self.lines)

    def _get_next_piece(self)->str:
        next_shape= self.next_pieces.pop(0)
        self.next_pieces.append(self._get_random_shape())
        return next_shape

    def _get_random_shape(self):
        inverse_probabilities = [1 / frequency for frequency in self.piece_frequency]
        
        total_sum = sum(self.piece_frequency)
        probabilities = [prob  / total_sum for prob in inverse_probabilities]
        
        next_piece = random.choices(range(len(probabilities)),weights=probabilities)[0]
        self.piece_frequency[next_piece] += 1

        return list(TETROMINOS.keys())[next_piece]

    def _check_close(self):
        for event in pygame.event.get():
            if((event.type == pygame.QUIT) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)):
                pygame.quit()
                sys.exit(0)

    def _handle_events(self):
        keys = pygame.key.get_pressed()

        # checking horizontal movement
        if not self.timers['horizontal move'].active:
            if keys[pygame.K_LEFT]:
                self.cur_tetromino.move(MOVE_DIRECTION[pygame.K_LEFT])
                self.timers['horizontal move'].activate()
            if keys[pygame.K_RIGHT]:
                self.cur_tetromino.move(MOVE_DIRECTION[pygame.K_RIGHT])	
                self.timers['horizontal move'].activate()

        # check for rotation
        if not self.timers['rotate'].active:
            if keys[pygame.K_UP] or keys[pygame.K_z] or keys[pygame.KSCAN_Z]:
                self.cur_tetromino.rotate(ROTATE_DIRECTION["clockwise"])
                self.timers['rotate'].activate()
    
            if keys[pygame.KSCAN_X] or keys[pygame.K_x]:
                self.cur_tetromino.rotate(ROTATE_DIRECTION["counter_clockwise"])
                self.timers['rotate'].activate()

		# down speedup
        if not self.down_pressed and keys[pygame.K_DOWN]:
            self.down_pressed = True
            self.timers['vertical move'].duration = self.down_speed_faster

        if self.down_pressed and not keys[pygame.K_DOWN]:
            self.down_pressed = False
            self.timers['vertical move'].duration = self.down_speed
            

    def check(self):
        self._check_game_over()
        self._check_landing()
        self._check_close()
        self._handle_events()
        
    def update(self):
        self._timer_update()
        self.sprites.update()
        self.surface.fill(WINDOW)
        self.sprites.draw(self.board_ui.surface)


        self.board_ui.run()
        self.score_ui.run()
        self.preview_ui.run(self.next_pieces)

        pygame.display.update()
        
    def play_step(self, action = None):
        self.check()
        if action is not None:
            index = action.argmax()
            #[ROTATE, LEFT, RIGHT, DOWN, CHILLING]
            actions = {
                0: lambda: self.cur_tetromino.rotate(ROTATE_DIRECTION["clockwise"]),
                1: lambda: self.cur_tetromino.move(Vector2(-1, 0)),
                2: lambda: self.cur_tetromino.move(Vector2(1, 0)),
                3: lambda: self.cur_tetromino.move(Vector2(0, 1)),
                4: lambda: None
            }
            
            actions[index]()
            
        self.update()
        self.clock.tick()
        if self.user_mode is not True:
            return self.get_game_information()


    def run(self):
        while(True):
            self.play_step()
            if self.game_over: 
                pygame.quit()
                sys.exit(0)




    def get_game_information(self):
        board = np.array(self.board)
        board = np.where(np.vectorize(lambda x: isinstance(x, Block))(board), 1, board)
        blocks= np.array([block.pos  for block in self.cur_tetromino.blocks], dtype=np.int8)
        return board, blocks



if __name__ == "__main__":
    game = Game()
    game.run()
