import pkg_resources
from    Satellite import *
import time
from    Station import *
from multiprocessing import Pool
from    Earth2D  import *
from    sat_env import  *
from tqdm import tqdm
import matplotlib.pyplot as plt
import pickle as pkl
satList= [Satellite(np.random.randint(50,75),Earth2D.getRandomPosition(),Earth2D.getRandonDirection(),np.random.randint(6,8),np.random.randint(50000 ,80000)) for i in range(1)]

with open("/content/drive/My Drive/PLDAC/PLDAC/data/stations.pkl", "rb")  as file:
    stations_coords = pkl.load(file).get("stations_coords")
    np.random.shuffle(stations_coords)

stationList = [Station(np.array(coord), np.random.randint(750, 1100), np.random.randint(10, 15)) for coord in stations_coords[:4]]


def simple_position_test(satList):
    beginpositions=[(s.id,s.position) for s in satList]
    N=10000
    it=0
    X=[]
    Y=[]
    c=0
    while(it<N):
        for i,sat in enumerate(satList):
            sat.update_position()
            if(Earth2D.getDistance(beginpositions[i][1],sat.position)<sat.step-0.1):
                print("staps ", c)
                fig = plt.figure()
                fig.set_size_inches(18.5, 10.5)
                m = plot_map()
                draw_map(m)
                m.scatter(X,Y,color="black",s=5)
                plt.show()

                return
            X.append(sat.position[0])
            Y.append([sat.position[1]])
            c+=1



