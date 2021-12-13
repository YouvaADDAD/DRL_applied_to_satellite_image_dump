import random

from     Earth2D import *
class Task(object):
    count = 0
    def __init__(self,begin_position,length,priority,expiration=2000000000):
        self.id=Task.count
        self.begin_position=begin_position
        self.length=length
        self.priority=priority
        self.expiration=expiration
        self.ploted=None
        Task.count+=1

    @classmethod
    def getRadomTasks(cls,n,satellite):
        tasks=[]
        for i in range(n):
            begining=Earth2D.getRandomPosition()
            length=abs(np.random.normal(1.3*satellite.width,1/5*satellite.width))
            priority=np.random.randint(1,5)
            #create a proportional priority to needed distance to reach  this task
            pos_diff=(begining[0]-satellite.position[0])/(satellite.direction[0]*satellite.speed)
            expiration= (pos_diff if pos_diff>0 else (360-pos_diff))*(0.6+random.random())*np.random.randint(4,6)+np.random.randint(1000,2000)

            tasks.append(Task(begining,length,priority,expiration))
        return tasks
    def begin(self):
        self.rest=self.length

    #def remove(self):
    #    self.ploted.remove()
    def __str__(self):
        return  'TASk ' +str(self.begin_position)+"  length: "+str(self.length)
    def unplot(self):
        if(self.ploted):
          self.ploted.pop(0).remove()

