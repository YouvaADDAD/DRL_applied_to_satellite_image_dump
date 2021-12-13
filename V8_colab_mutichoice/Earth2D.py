import numpy as np
class Earth2D(object):
    extremums=np.array([180,90])
    @classmethod
    def normalyzePosition(self,newcoords):

        for i  in range(len(self.extremums)):
            newcoords[i] = newcoords[i] if abs(newcoords[i]) < self.extremums[i]  else  (abs(newcoords[i]) % self.extremums[i])  - self.extremums[i] * np.sign(newcoords[i])

        return newcoords
    @classmethod
    def getRandomPosition(self):
        return self.normalyzePosition(np.random.normal(0,0.4,2)*self.extremums)
    @classmethod
    def getRandonDirection(self):
        return np.array([((-1)**np.random.randint(0,2)*np.random.normal(0.02,0.001,1))[0],0.2])

    @staticmethod
    def getDistance(position1,position2):
        return np.linalg.norm((position1-position2))



