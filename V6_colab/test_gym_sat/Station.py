import random

from   InOrbit import *
class Station(InOrbit):
    station_count=0
    def __init__(self,initial_position,debit=200,limitdistance=13,avg_connexion=random.randint(1,3)):
        InOrbit.__init__(self,initial_position,0,0)
        self.id=Station.station_count
        Station.station_count+=1
        self.debit = debit
        self.limitdistance=limitdistance#limitdistance
        self.avg_connexion=avg_connexion
        self.scatte=None
        self.possibleconnections=0
        self.connected=False
    def transmission(self):
        self.scatte.set_color('g')
    def endTransmission(self):
        self.scatte.set_color('b')

    def __str__(self):
        return 'Station  {}  pos '.format(self.id) + str(self.position)+" debit " +str(self.debit)

        






