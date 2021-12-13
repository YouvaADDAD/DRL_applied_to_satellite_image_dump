import numpy as np
import random
from IPython.display import clear_output
import time
import gym
import tensorflow as tf
from multiprocessing import Pool
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.optimizers import Adam
from rl.agents import DQNAgent
from rl.policy import BoltzmannQPolicy
from rl.memory import SequentialMemory
from sat_env import SatEnv


class DQN_Dual_Agent_Experimentation():

    def __init__(self, numbersatellites=50, numberstations=400):
        self.env = SatEnv(numbersatellites=numbersatellites, numberstations=numberstations,resultfilname="dqn_duel_fit")
        self.states = self.env.reset().shape
        self.actions = self.env.action_space.n
        self.model = self.build_model()
        self.dqn = self.build_agent()
        self.dqn.compile(Adam(lr=1e-3), metrics=['mae'])
        
    def test(self):
        env_test = SatEnv(numbersatellites=numbersatellites, numberstations=numberstations,resultfilname="dqn_duel_test")
        self.dqn.load_weights('dqn_duel_weights{}_{}_connexionPenalisation.h5f'.format(self.env.numbersatellites, self.env.numberstations))
        scores = self.dqn.test(env_test, nb_episodes=3, visualize=False)
        print(scores)

    def fitModel(self):
       
        self.dqn.fit(self.env, nb_steps=20000, visualize=False, verbose=1,log_interval=1000)
        self.dqn.save_weights('dqn_duel_weights{}_{}_connexionPenalisation.h5f'.format(self.env.numbersatellites, self.env.numberstations),
                              overwrite=True)

    def build_model(self):
        model = Sequential()
        model.add(Flatten(input_shape=(1, self.states[0])))
        model.add(Dense(40, activation='relu'))
        model.add(Dense(60, activation='relu'))
        model.add(Dense(20, activation='relu'))
        model.add(Dense(self.actions, activation='linear'))
        return model

    def build_agent(self):
        policy = BoltzmannQPolicy()
        memory = SequentialMemory(limit=50000, window_length=1)
        dqn = DQNAgent(model=self.model, memory=memory, policy=policy,
                       nb_actions=self.actions, nb_steps_warmup=10, target_model_update=1e-2,enable_dueling_network=True)
        return dqn




