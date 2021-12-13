import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from itertools import chain
from   Satellite import *
import random
import string
import matplotlib.colors as mcolors
colors=list(mcolors.CSS4_COLORS)
global anim
anim=0
def draw_map(m, scale=0.2):
    # draw a shaded-relief image
    m.shadedrelief(scale=scale)

    # lats and longs are returned as a dictionary
    lats = m.drawparallels(np.linspace(-90, 90, 13))
    lons = m.drawmeridians(np.linspace(-180, 180, 13))

    # keys contain the plt.Line2D instances
    lat_lines = chain(*(tup[1][0] for tup in lats.items()))
    lon_lines = chain(*(tup[1][0] for tup in lons.items()))
    all_lines = chain(lat_lines, lon_lines)

    # cycle through these lines and set the desired style
    for line in all_lines:
        line.set(linestyle='-', alpha=0.3, color='w')



def plot_map():
    m = Basemap(projection='cyl',
            llcrnrlat=-90, urcrnrlat=90,
            llcrnrlon=-180, urcrnrlon=180, )
    draw_map(m)
    return m

def getListCoordinates(satList):
    return [sat.position[0] for sat in satList ],[sat.position[1] for sat in satList ]


def plot_tasks(satList,map):
    for sat in list(satList):
        for task in sat.tasks:
            plot_task(sat,task,map)

def plot_task(sat,task,map):
    arriving = task.begin_position + sat.direction * (task.length /2)
    difx = sat.direction[0] * (sat.width /2)
    dify = sat.direction[1] * (sat.width /2)
    x1, y1 = normalyzePlotCoords([task.begin_position[0] - difx, task.begin_position[1] + dify])
    x2, y2 = normalyzePlotCoords([arriving[0] - difx, arriving[1] + dify])
    x3, y3 = normalyzePlotCoords([arriving[0] + difx, arriving[1] - dify])
    x4, y4 = normalyzePlotCoords([task.begin_position[0] + difx, task.begin_position[1] - dify])
    x = [x1, x2, x3, x4, x1]
    y = [y1, y2, y3, y4, y1]
    task.ploted = map.plot(x, y, color=colors[sat.id])


def normalyzePlotCoords(coords):
    return np.sign(coords[0]) *min(abs(coords[0]),180) , np.sign(abs(coords[1]))*min(coords[1],90)

def save_anim():
  global anim
  path="animations/step%02d.png"%anim
  with open(path,"w") as f:
    pass
  plt.savefig(path)
  anim+=1

def plot_sccater(satList,stationList):
    plt.ion()  # Turn on interactive mode
    fig=plt.figure()
    fig.set_size_inches(18.5, 10.5)
    m = plot_map()
    draw_map(m)
    
    plot_tasks(satList, m)
    for s  in stationList:
        s.scatte = m.scatter(s.position[:1], s.position[1:], s=100/np.log(len(stationList)),color="b" )
    N=10000
    i=0
    satellite=None
    plt.show()
    while(i<N):
        possible_action = False
        while (not possible_action):
            for sat in satList:
                possible_action=sat.possibleAction(stationList)
                if possible_action :
                    satellite=sat
                    break;
                sat.update(stationList,decision=False,map=m,fig=fig)
                plt.show()
        satellite.NextAction(stationList)
        satellite.update(stationList,decision=True,map=m,fig=fig)
        plt.show()
        i+=1
    plt.ioff()

