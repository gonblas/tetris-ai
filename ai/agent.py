
import numpy as np
from collections import deque
from ai.ai_settings import *
from tetris.settings import *
import random
import math

#5 input
#256 hidden
#5 output

class Agent:
    
    
    '''Deep Q Learning Agent + Maximin

    Args:
        state_size (int): Size of the input domain
        mem_size (int): Size of the replay buffer
        discount (float): How important is the future rewards compared to the immediate ones [0,1]
        epsilon (float): Exploration (probability of random values given) value at the start
        epsilon_min (float): At what epsilon value the agent stops decrementing it
        epsilon_stop_episode (int): At what episode the agent stops decreasing the exploration variable
        n_neurons (list(int)): List with the number of neurons in each inner layer
        activations (list): List with the activations used in each inner layer, as well as the output
        loss (obj): Loss function
        optimizer (obj): Otimizer used
        replay_start_size: Minimum size needed to train
        
    '''
    
    def __init__(self, game = None):
        self.n_games = 0
        self.game= game
        self.memory = deque(maxlen=MAX_MEMORY) 
        # self.game.run()
        self.epsilon = EPSILON
        #TODO: instanciar el trainer y el model
        # self.positions=

    # def evaluate_height(self, grid):
        # heights = np.array([np.argmax(grid[col, :] != 0) if np.any(grid[col, :] != 0) else grid.shape[0] - 1 for col in range(grid.shape[1])])
        # return heights

    def evaluate_height(self, grid):
        heights = np.array([np.argmax(grid[:, col] != 0) if np.any(grid[:, col] != 0) else grid.shape[0] for col in range(grid.shape[1])])
        return heights
    #cambie esto
    
    def evaluate_bumpiness(self, heights):
        # Calculate the absolute differences between adjacent elements
        height_diffs = np.abs(heights[:-1] - heights[1:])
        # Sum up the absolute differences to get the total bumpiness
        total_bumpiness = np.sum(height_diffs)

        return total_bumpiness

    def evaluate_holes(self, grid): #pola perdon pero te lo cambiamos, Si podes hacerlo como lo tenias antes pero que ande estaria bueno
        holes = 0
        width = len(grid[0])

        for col in range(width):
            isCeiling = False
            for row in range(len(grid)):
                if grid[row][col]:
                    isCeiling = True
                elif isCeiling:
                    holes += 1

        return holes

    def evaluate_completed_lines(self, grid):
        completed_lines = np.sum(np.all(grid, axis=1))
        return completed_lines 


    def get_status(self):
        return (self.game.get_game_information())


    def get_reward(self, grid): #No confirmo que esto este bien (G. Blasco, lease gei blascou)
        grid, blocks = self.get_status()
        heights = self.evaluate_height(grid)
        bumpiness = self.evaluate_bumpiness(heights)
        holes = self.evaluate_holes(grid)
        completed_lines = self.evaluate_completed_lines(grid)
        return LINES_COEF * completed_lines + HEIGHTS_COEF * heights + HOLES_COEF * holes + BUMPINESS_COEF * bumpiness


    def remember(self, status, action, reward, next_status):
        self.memory.append((status, action, reward, next_status))

    # def train_short_memory(self, state, action, reward, next_state):
    #     self.trainer.train_step(state, action, reward, next_state)

    def train_long_memory(self):
        if(len(self.memory) >= BATCH_SIZE):
            mini_sample = random.sample(self.memory, BATCH_SIZE) 
        else:
            mini_sample = self.memory
        
        states, actions, rewards, next_states = zip(*mini_sample)
        # self.trainer.train(states, actions, rewards, next_states)



    def get_action(self, state): #poner el tipo de retorno
        self.epsilon = max(EPSILON - self.n_games / (self.n_games ** 0.30999), 1)
        #[ROTATE, LEFT, RIGHT, DOWN, CHILLING]
        move = [0, 0, 0, 0, 0]
        if(random.randint(0, 100) < self.epsilon):
            index = random.randint(0, 4)
            move[index] = 1
        else: #ACA ACTUA LA IA, NI IDEA COMO SE HA
            self.model.predict(state)[0]
        return move



def train(game):
    #TODO: setear todo
    score, record = 0, 0
    agent = Agent(game)
    while(True):
        old_state = agent.get_state(game)
        final_move = agent.get_action(old_state)
        game.run(final_move)
        reward = agent.get_reward()
        new_state = agent.get_state(game)
        agent.train_short_memory(old_state, final_move, reward, new_state)
        agent.remember(old_state, final_move, reward, new_state)

        if(game.level < 80):
            agent.train_long_memory()
        
        agent.n_games += 1
        if(score > record):
                record = score
            
    #TODO: plot


if __name__ =="__main__":
    train()
