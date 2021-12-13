import gym
import numpy as np
from gym import error, spaces, utils
from gym.utils import seeding
from gym.spaces import Discrete
from       Satellite import Satellite

from       Station import Station
from       Earth2D import Earth2D
from multiprocessing import Pool
import matplotlib.pyplot as plt
import pickle as pkl
import queue

class SatEnv(gym.Env):
    def __init__(self,numbersatellites=20,numberstations=500):
        with open("/content/drive/My Drive/PLDAC/PLDAC/data/stations.pkl", "rb")  as file:
            stations_coord = pkl.load(file).get("stations_coords")
            np.random.shuffle(stations_coord)

        self.numbersatellties=numbersatellites
        self.stationList=[Station(np.array(coord),np.random.randint(400,750),np.random.randint(15,20)) for coord in stations_coord[:numberstations]]
        
        self.satList=np.array([Satellite(np.random.randint(20,35),Earth2D.getRandomPosition(),Earth2D.getRandonDirection(),
                                np.random.randint(1,3), np.random.randint(50000,80000)) for _ in range(numbersatellites)])

        self.actionsqueue=queue.Queue()
        self.max_step=numbersatellites*50
        self.currentstep=0
        self.currentsatellite=None
        #preparation pour avoir un choix de vidage a la premiere étape
        self.update_current_satellite()
        self.observation_space=self.currentsatellite.state
        self.action_space =  Discrete(2)

    def step(self, action):
        assert self.action_space.contains(action)
        reward=0
        reward+=self.currentsatellite.update(self.stationList,bool(action))
        self.update_current_satellite()
        self.currentstep+=1
        info={}
        self.observation_space=self.currentsatellite.state
        return self.observation_space, reward,self.currentstep>self.max_step,info

    def reset(self):
        self.render()
        self.satList = np.array( [Satellite(np.random.randint(20,35), Earth2D.getRandomPosition(), Earth2D.getRandonDirection(),
                      np.random.randint(1,3), np.random.randint(50000, 80000)) for _ in range(self.numbersatellties)])
        self.currentstep = 0
        self.update_current_satellite()
        return self.currentsatellite.state


    def render(self,mode='human'):
        """        storage,debit,images,tasks=self.satellite.getstate()
        fig, axs = plt.subplots(2, 1, constrained_layout=True)
        axs[0].imshow(images)
        axs[0].set_title(' images ')

        axs[1].imshow(tasks)
        axs[1].set_title(' tasks ')

        fig.suptitle('satellite stroage {}  , station debit {}'.format(storage,debit), fontsize=16)
        plt.show()"""

        print("""\n\n###############################################################################################################################################################################################################""")
        for sat in self.satList:
            print(sat)
            print("__________________________________________________________________________________________________________________________________________________________________________________________________________________")




  
    def close(self):
        pass

    def update_current_satellite(self):
      raward=0
      raward+=self.updatePossibleAction()
      self.currentsatellite =self.actionsqueue.get()
      raward+=self.currentsatellite.NextAction(self.stationList)


    def exec(self,f,iterator_):
        return np.array(list (map(f,iterator_)))


    def updatePossibleAction(self):
        reward=0
        while self.actionsqueue.empty():
            reward+=self.exec(self.exec_update,self.satList).sum()
            self.exec(self.exec_PossibleAction, self.satList)
        return reward



    def exec_PossibleAction(self,sat):
        is_possible=sat.possibleAction(self.stationList)
        if(is_possible):
          self.actionsqueue.put(sat)
        return is_possible
    
    def exec_update(self,sat):
        return sat.update(self.stationList)


