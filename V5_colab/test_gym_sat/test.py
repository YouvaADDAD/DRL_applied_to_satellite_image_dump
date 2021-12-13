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
satList= [Satellite(np.random.randint(50,75),Earth2D.getRandomPosition(),Earth2D.getRandonDirection(),np.random.randint(1,3),np.random.randint(100000 ,200000)) for i in range(20)]

with open("/content/drive/My Drive/PLDAC/PLDAC/data/stations.pkl", "rb")  as file:
    stations_coords = pkl.load(file).get("stations_coords")
    np.random.shuffle(stations_coords)

stationList = [Station(np.array(coord), np.random.randint(750, 1100), np.random.randint(10, 15)) for coord in stations_coords[:80]]

def _test_collecting_and_Sending(satellitesList,stationsList):
    reward=0
    for x in tqdm(range(2000)):
        for sat in satellitesList[:1] :
            reward+=sat.goToNextAction(stationsList)
            reward+=sat.update(stationsList,sat.estimatedfillingrate() > 0.75 or sat.state[7]<10000)
            reward=0


def test_env(nbsats,nbstations):
  env=SatEnv(nbsats,nbstations)
  for x in range(5):
      done = False
      score=0
      while not done:
          status,reward,done,_=env.step(True)
          score+=reward
      env.render()


#_test_collecting_and_Sending(satList,stationList)


#plot_sccater(satList,stationList)


