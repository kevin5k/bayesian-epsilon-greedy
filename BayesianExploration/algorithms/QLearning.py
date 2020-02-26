import numpy as np

from adaptive.Epsilon import Epsilon
from adaptive.LearningRate import LearningRate
from agents.Tabular import Tabular
from algorithms.TabularTDLearning import TabularTDLearning
from tasks.Task import Task


class QLearning(TabularTDLearning):
        
    def __init__(self, discount, episode_length):
        super().__init__(discount, episode_length)
    
    def run_episode(self, Q : Tabular, task : Task, epsilon : Epsilon, alpha : LearningRate):
        
        # to compute backup
        rewards = np.zeros(self.episode_length, dtype=np.float32)
        epsilons = np.zeros(self.episode_length, dtype=np.float32)
        
        # initialize state
        state = task.initial_state()
           
        # repeat for each step of episode
        for t in range(self.episode_length):
            
            # choose action from state using policy derived from Q
            epsilons[t] = epsilon_t = epsilon.get_epsilon(state)
            action = self.epsilon_greedy(Q, task, state, epsilon_t) 
                    
            # take action and observe reward and new state
            new_state, reward, done = task.transition(state, action) 
            rewards[t] = reward  
            
            # compute model means for exploration
            G_Q = reward + self.gamma * Q.max_value(new_state)
            G_U = reward + self.gamma * np.mean(Q.values(new_state))  
            
            # update Q
            old_Q = Q.values(state)[action]
            delta = G_Q - old_Q
            Q.alpha = alpha.get_alpha(state) 
            Q.update(state, action, delta)
            new_Q = Q.values(state)[action]
            
            # update epsilon
            epsilon.update_from_experts(state, data=(G_Q, G_U, new_Q - old_Q)) 
            
            # update learning rate
            alpha.update_alpha(state, None)
            
            # update state
            state = new_state
        
            # until state is terminal
            if done:
                break
        
        return t + 1, rewards[0:t + 1], epsilons[0:t + 1]
