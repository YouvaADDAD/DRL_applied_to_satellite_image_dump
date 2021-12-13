import pkg_resources
from    Satellite import *
import time
from    Station import *
from multiprocessing import Pool
from    Earth2D  import *
from    sat_env import  *
from tqdm import tqdm
import pickle as pkl
import matplotlib.pyplot as plt
satList= [Satellite(np.random.randint(50,75),Earth2D.getRandomPosition(),Earth2D.getRandonDirection(),np.random.randint(6,8),np.random.randint(50000 ,80000)) for i in range(1)]

with open("/home/kns/PycharmProjects/PLDAC/data/stations.pkl", "rb")  as file:
    stations_coords = pkl.load(file).get("stations_coords")
    np.random.shuffle(stations_coords)

stationList = [Station(np.array(coord), np.random.randint(750, 1100), np.random.randint(10, 15)) for coord in stations_coords[:40]]

def _test_collecting_and_Sending(satellitesList,stationsList):
    reward=0
    for x in tqdm(range(2000)):
        for sat in satellitesList[:1] :
            reward+=sat.NextAction(stationsList)
            reward+=sat.update(stationsList,1)#sat.estimatedfillingrate() > 0.75 or sat.state[7]<10000)
            reward=0
            print(sat)


def glouton_test_env(nbsats,nbstations):
  env=SatEnv(nbsats,nbstations)
  score = 0
  step = 0
  for x in range(30):
      env.reset()
      done = False
      while not done:
          obs=env.observation_space
          print(bool(obs[0]) , obs[3]>0.75 , obs[-6] > 1.0 )
          decision=bool(obs[0]) or obs[3]>0.75 or obs[-6] > 1.0
          status,reward,done,_=env.step(int(decision))
          score+=reward
          step+=1

      print("reward : ", score/step, "Pertincence Score completed", env.positifReward())



def simple_test_sat(satList,stationList):
    step=0
    begin_position=satList[0].position
    while(1):
        for sat in satList:
            sat.NextAction(stationList)
            print(step, sat.position, begin_position)
            sat.update(stationList, False)  # int(sat.state[6]>0.9))


simple_test_sat(satList,stationList)
#_test_collecting_and_Sending(satList,stationList)

#plot_sccater(satList,stationList)

#glouton_test_env(1,50)

