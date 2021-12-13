from abc import ABC
from      Earth2D  import *
class InOrbit(ABC):
    def __init__( self , initial_position , direction , speed ):
        self.initial_position=initial_position
        self.position = Earth2D.normalyzePosition(initial_position)  # the initial position  victor in the plan of the satellite latitude , longitude
        self.direction = direction  # the vertor of direction of the satellite
        self.speed = speed


    def update_position(self):
        self.position = Earth2D.normalyzePosition(self.position + self.direction * self.speed)

    def getPostStepsPossition(self,steps):
        return Earth2D.normalyzePosition( self.position + self.direction * self.speed  * steps)

    def nearInTrajectory(self,position,steps=50):
        limitpos=self.getPostStepsPossition(steps)
        if(self.direction[0]<0):
            return self.position[0]>position[0] > limitpos[0]
        return self.position[0] < position[0] < limitpos[0]

