from   Tools import *
from   Task import *
from   Station import *
from   Image import  *
from gym.spaces import Discrete , Box
import numpy as np
import random
import string

class Satellite(InOrbit):
    counter=0
    def __init__(self,width,initial_position,direction,speed,storage_capacity):

        InOrbit.__init__(self,initial_position,direction,speed)
        self.id=Satellite.counter
        Satellite.counter+=1
        self.width = width # maximu with tha can be token

        self.completed=0
        self.completedpertineces=0
        self.allconnexions=0
        self.allvisibylitys=0
        #advenccemebt parapmeters
        self.step = np.linalg.norm(direction * speed)
        #strorage parameters
        self.storage_capacity=storage_capacity
        self.memory=storage_capacity
        self.fillingrate= lambda : ((self.memory-self.storage_capacity)/self.memory )
        self.nextStorageEstimation = 0
        self.estimatedfillingrate=lambda : ((self.memory-self.storage_capacity)+self.nextStorageEstimation) / self.memory

        #tasks parameters
        self.tasks=set(Task.getRadomTasks(10,self))
        self.job=None
        self.intransmission=None
        self.possibleaction=False


        #Unlaoding  parameters
        self.tokenImages=set()
        self.scatte=None
        self.availableStation=None
        self.next_tasks=set()
        self.possibleUnloading=set()
        self.maxPriority=0
        self.toUnload=None
        self.state=np.array([])

        #Connexion parameters
        self.connexionTime = 0
        self.isConnected=False
        self.disconnecting=False
        self.isconnecting=False
        self.it=0


    def update(self,stations,decision=None,map=None,fig=None):
        # adding a task with probability 1e-2
        reward=0
        assert self.storage_capacity<=self.memory+1

        #self.storage_capacity=min(self.storage_capacity,self.memory)

        if np.random.random()<1e-1:
            self.addTask(map)
        taskloss=self.updateTasks(map)
        if (len(self.tasks)>0 and not(self.job)):
            self.tryBeginTask(map)
        #if we are in progression of task
        elif self.job:
            self.progressJob()
        #check if there are an available station to transfert images

        if self.availableStation :
            reward+=self.tryTransfertImages(stations,decision)
        imagesloss=self.updateImages()
        super().update_position()


        if(map):
          if(self.scatte):
            self.scatte.remove()
          self.plot(map)

          if (not self.disconnecting and self.isConnected):
            self.availableStation.transmission()
            
          else :
            if(self.availableStation):
              self.availableStation.endTransmission()
        return reward - (taskloss+imagesloss)
      


    def progressJob(self):
        if self.job.rest > 0:
            self.job.rest -= self.step
            self.storage_capacity -=self.step*self.width
        else:
            self.storage_capacity-=self.job.rest*self.width # si le rest est negatif du au cacul on le récupére
            self.tokenImages.add(Image(self.job, self.width))
            self.job = None
            




    def updateTasks(self,map=None):
        tasksloss=0
        expired = set()
        self.next_tasks=set()
        self.nextStorageEstimation=0
        for task in self.tasks:

            task.expiration -= 1
            if task.expiration <= 0:
                tasksloss+=task.priority
                # for plots
                if (map):
                    task.ploted.pop(0).remove()
                #we remember  expired images to be removed at the last
                expired.add(task)
            else :
                if(self.possibleaction and self.nearInTrajectory(task.begin_position,steps=300/self.speed)):
                    self.nextStorageEstimation+=(task.length*self.width)
                    self.next_tasks.add(task)

        # we delete expired  images
        self.tasks-=expired
        return tasksloss




    def tryBeginTask(self,map):

        for task in self.tasks:
        # if it's possible to do this task we wil make it as current job
            if self.can_do(task):
                self.job = task
                if (map):
                  task.unplot()
                self.tasks.remove(self.job)
                
                self.job.begin()
                return 

    def can_do(self,task):
        return ((task.length*self.width)<=self.storage_capacity)  and  Earth2D.getDistance(self.position , task.begin_position) < 6

    def addTask(self,map):
        task = Task.getRadomTasks(1, self)[0]
        if(map):
            plot_task(self, task, map)
        self.tasks.add(task)




    def plot(self,map):
      self.scatte=map.scatter(self.position[0],self.position[1],color= (colors[self.id] if not self.isConnected else 'g'),s=int(100 / np.log(Satellite.counter)))

  



    def isAtteignable(self, station):
        #if the satellite is connected we check just if we can send another aquisition to this station , and check that we have enoght time to deconnect pro from
        return  Earth2D.getDistance(station.position,self.getPostStepsPossition((int(self.isConnected)+1)*station.avg_connexion)) < station.limitdistance





    def canTransfert(self, image, station):
        transferttime = image.needTime(station.debit)
        # check if the time of trasnfert is lower than expiration of the aquisition plus probably time of connection
        if transferttime +station.avg_connexion*int(self.isConnected) >= image.expiration:
            return False

        PostTransmissionPos = self.getPostStepsPossition((1+int(self.isConnected))*transferttime + station.avg_connexion)
        distance = Earth2D.getDistance(station.position, PostTransmissionPos)

        return distance < station.limitdistance




    def updateImages(self):
        penalisation=0
        expired=set()
        self.possibleUnloading=set()
        for image in self.tokenImages:
            image.expiration-=1    
            if(image.expiration<=0 ):
                expired.add(image)
                self.storage_capacity+=image.size
                penalisation+=image.priority/2
            else:
                if self.availableStation:
                    if self.canTransfert(image,self.availableStation):
                        self.possibleUnloading.add(image)
                        if(self.maxPriority>image.priority):
                            self.maxPriority=image.priority

        self.tokenImages-=expired
        return penalisation









    def tryTransfertImages(self,stations,unload=None,map=None):
        reward=0
        
        if self.isConnected and self.intransmission:
            reward+=self.progressTransmission()


        elif (self.disconnecting):
            
            self.progressDisconnexion()

        elif self.isconnecting:
            self.progressConnexion()

        elif unload !=None :
          if(unload):
              self.intransmission = True
              if(not self.isConnected):
                if (self.estimatedfillingrate() < 0.9):
                      reward -= self.availableStation.avg_connexion / 2
                self.isconnecting=True
                self.progressConnexion()

          else:
              if (self.isConnected):
                  self.disconnecting=True
                  self.progressDisconnexion()

        return reward




    def getAvailableStation(self,stations):
        #check if we are aleready connected to a station we check that it's in the area where we can do a transmission
        if(self.disconnecting or self.isconnecting):
          return False
        if( self.availableStation):
            if not self.isAtteignable(self.availableStation) :
                if(self.isConnected):
                    self.disconnecting=True
                else:
                    self.availableStation=None
               
                return False
            return True

        for station in stations:
            if (self.isAtteignable(station)):
                self.availableStation=station
                self.allvisibylitys+=1
                # preparing connexion time that we will use after
                self.connexionTime=0
                return True
        self.connexionTime = 0
        self.availableStation = None
        return False



    def progressConnexion(self):
        self.connexionTime+=1
        self.isConnected= self.connexionTime>=self.availableStation.avg_connexion
        self.isconnecting=not self.isConnected
        if(self.isConnected):
            self.allconnexions+=1




    def progressDisconnexion(self):
        self.connexionTime-=1
        self.isConnected=self.connexionTime!=0
        if(not self.isConnected):
            self.availableStation.connected=False
            self.availableStation=None
            self.disconnecting=False


    """
    when we are connected to a station  and we progress acquisition transfering  
    """
    def progressTransmission(self):
        image, station =self.toUnload,self.availableStation
        image.size -= station.debit
        self.storage_capacity += station.debit
        if (image.size <= 0):
            self.storage_capacity+=image.size
            try :
                self.tokenImages.remove(image)
                self.possibleUnloading.remove(image)
            except :
                pass

            self.intransmission = False
            self.toUnload=None
            self.completed+=1
            self.completedpertineces+=image.priority
            return image.priority

        return 0



    def possibleAction(self,stations):
        return  self.getAvailableStation(stations) and not(self.isconnecting or self.disconnecting or self.intransmission) and len(self.possibleUnloading)>0 
      
    def __str__(self):
        return "Satellite  id : {} | storage capacity : {} | current filling : {} | estimated next filling : {}  | number of tasks : {} | number of stored images : {} | copleted : {} | cumulate priority : {} | visibylity : {} |  coneexions : {}".format(
            self.id,self.storage_capacity,self.fillingrate(),self.estimatedfillingrate(),len(self.tasks), len(self.tokenImages),self.completed,self.completedpertineces,self.allvisibylitys,self.allconnexions)




    def NextAction(self,stations):
        reward=0
        self.possibleaction = False
        while(not  self.possibleAction(stations)):
            reward+=self.update(stations)
        self.possibleaction = True
        self.updateTasks()
        self.state=self.getstate()


        return reward



    def getstate(self):
        assert self.availableStation != None and len(self.possibleUnloading) >0
        self.toUnload = np.random.choice([image for image in self.possibleUnloading if image.priority >= self.maxPriority ])

        tounoadstate=np.array([self.toUnload.size,self.toUnload.priority,self.toUnload.expiration])
        avilableiamgesstate = np.array([np.array([im.size, im.priority , im.expiration]) for im in self.possibleUnloading]).reshape(-1, 3)
        nexttasksstate=np.array([np.array([task.length * self.width, task.priority, task.expiration]) for task in self.next_tasks]).reshape(-1,3)
        tokenimagesstate=np.array([np.array([im.size, im.priority , im.expiration]) for im in self.tokenImages]).reshape(-1, 3)


        if(nexttasksstate.shape[0]<1):
            nexttasksstate=np.ones((1,3))
        state=[ np.array([int(self.isConnected),self.availableStation.possibleconnections, self.storage_capacity,self.fillingrate(),len(self.tokenImages),len(self.possibleUnloading)]).reshape(-1),
                tounoadstate.mean(0).reshape(-1),
                avilableiamgesstate.mean(0).reshape(-1),
                tokenimagesstate.mean(0).reshape(-1),
                np.array([self.estimatedfillingrate(),self.nextStorageEstimation,len(self.next_tasks)]).reshape(-1),
                np.nanmean(nexttasksstate,axis=0).reshape(-1)]
        res=np.hstack(state)
        return res

    