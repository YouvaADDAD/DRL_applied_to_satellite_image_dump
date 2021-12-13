import gym
import numpy as np
from gym import error, spaces, utils
from gym.utils import seeding
from gym.spaces import Discrete
from Satellite import Satellite
from Station import Station
from Earth2D import Earth2D
from multiprocessing import Pool
import matplotlib.pyplot as plt
import pickle as pkl
import queue

class SatEnv(gym.Env):
    def __init__(self,numbersatellites=20,numberstations=500,resultfilname=""):
        with open("/content/drive/My Drive/PLDAC/PLDAC/data/stations.pkl", "rb")  as file:
            stations_coord = pkl.load(file).get("stations_coords")
            np.random.shuffle(stations_coord)
        self.result_filename="result"+resultfilname+str(numbersatellites)+'_'+str(numberstations)+".csv"
        with open(self.result_filename,"w") as f:
          f.write("episode,step,id_sat,visilbiltys,connexions,completed,completed_reward,aquisition_loss,requests_loss")
        self.numberstations=numberstations
        self.numbersatellites=numbersatellites
        self.stationList=[Station(np.array(coord),np.random.randint(400,750),np.random.randint(15,20)) for coord in stations_coord[:numberstations]]
        self.satList=[Satellite(np.random.randint(30,45),Earth2D.getRandomPosition(),Earth2D.getRandonDirection(),
                                np.random.randint(1,3), np.random.randint(30000,50000)) for _ in range(numbersatellites)]
        
        self.actionsqueue=queue.Queue()
        self.currentsatellite=None
        #preparation pour avoir un choix de vidage a la premiere étape
        self.action_space =  Discrete(2)
        self.n_step=0
        self.episode=0

    def step(self, action):
        assert self.action_space.contains(action)
        reward=0
        reward+=self.update_current_satellite()
        
        if(self.currentsatellite==None):
          info={}
          return self.observation_space, reward,True,info
        with open(self.result_filename,"a") as f:
          f.write(str(self.episode)+','+str(self.n_step)+','+self.currentsatellite.getCsvDescription())
        reward+=self.currentsatellite.update(self.stationList,bool(action))
        self.observation_space=self.currentsatellite.state
        self.n_step+=1
        info={}
        return self.observation_space, reward,len(self.satList)==0,info
        
    
    def reset(self):
        self.render()
        self.satList = [Satellite(np.random.randint(20,35), Earth2D.getRandomPosition(), Earth2D.getRandonDirection(),
                      np.random.randint(1,3), np.random.randint(50000, 80000)) for _ in range(self.numbersatellites)]
        self.update_current_satellite()

        assert self.currentsatellite != None
        
        self.observation_space=self.currentsatellite.state
        self.episode+=1
        self.n_step=0
        return self.currentsatellite.state


    def render(self,mode='human'):

        print("""\n\n###############################################################################################################################################################################################################""")
        for sat in self.satList:
            print(sat)
            print("__________________________________________________________________________________________________________________________________________________________________________________________________________________")


    def close(self):
      pass

        
    def update_current_satellite(self):
      reward=0

      #for each satellite
      reward+=self.updatePossibleAction()
      if(len(self.satList)==0):
          self.currentsatellite=None
          return reward

      #get action from possible actions
      self.currentsatellite = self.actionsqueue.get()

      #to update status of the satellite
      reward+=self.currentsatellite.NextAction(self.stationList)
      return reward




    def exec(self,f,iterator_):
        return np.array(list (map(f,iterator_)))



    def updatePossibleAction(self):
        reward=0
        while self.actionsqueue.empty() and len(self.satList)>0:
            reward+=self.exec(self.exec_update,self.satList).sum()
            self.exec(self.exec_PossibleAction, self.satList)
        return reward



    def exec_PossibleAction(self,sat):
        is_possible,ended=sat.possibleAction(self.stationList)
        if(ended):
            self.satList.remove(sat)
            return False
        if(is_possible):
            self.actionsqueue.put(sat)
        return is_possible

    def exec_update(self,sat):
        return sat.update(self.stationList)


    


