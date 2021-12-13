from Tools import *
from Station import *
from Image import *
import numpy as np


class Satellite(InOrbit):
    counter = 0

    def __init__(self, width, initial_position, direction, speed, storage_capacity):

        InOrbit.__init__(self, initial_position, direction, speed)
        self.id = Satellite.counter
        Satellite.counter += 1
        self.width = width  # maximu with tha can be token
        self.completed = 0
        self.allconnexions = 0
        self.updated = 0
        self.allvisibylitys = 0
        # advenccemebt parapmeters
        self.step = np.linalg.norm(direction * speed)
        # strorage parameters
        self.storage_capacity = storage_capacity
        self.memory = storage_capacity
        self.fillingrate = lambda: ((self.memory - self.storage_capacity) / self.memory)
        self.nextStorageEstimation = 0
        self.estimatedfillingrate = lambda: ((
                                                         self.memory - self.storage_capacity) + self.nextStorageEstimation) / self.memory

        # tasks parameters
        self.tasks = set(Task.getRadomTasks(350, self))
        self.job = None
        self.intransmission = None
        self.possibleaction = False

        # Unlaoding  parameters
        self.tokenImages = set()
        self.scatte = None
        self.availableStation = None
        self.next_tasks = set()
        self.possibleUnloading = set()
        self.maxPriority = 0
        self.maxSize=0
        self.minExpiration=np.inf
        self.toUnload = None
        self.state = np.array([])

        # Connexion parameters
        self.connexionTime = 0
        self.isConnected = False
        self.disconnecting = False
        self.isconnecting = False

        # mytircs variables
        self.totalRequestsPriority = np.array([  t.priority for t in self.tasks]).sum()
        self.totalAquisitionPriority = 0
        self.totalcompletedPriority = 0
        self.totalExpiredRequestsPriority = 0
        self.totalExpiredAquisitionPriority = 0

    def update(self, stations, decision=None, map=None, fig=None):
        # adding a task with probability 0.05
        reward = 0
        if np.random.random() < (1e-2)*(1150/len(self.tasks)):
            self.addTask(map=None)
        taskloss = self.updateTasks(map)

        if self.job:
            self.progressJob()

        # check if there are an available station to transfert images
        if self.availableStation:
            reward += self.tryTransfertImages(stations, decision)

        # update images expiration and remove expired images

        imagesloss = self.updateImages()

        super().update_position()

        self.totalExpiredRequestsPriority += taskloss
        self.totalExpiredAquisitionPriority += imagesloss

        if (map):
            if (self.scatte):
                self.scatte.remove()
            self.plot(map)

            if (not self.disconnecting and self.isConnected):
                self.availableStation.transmission()

            else:
                if (self.availableStation):
                    self.availableStation.endTransmission()
        return reward - (taskloss + imagesloss)

    def graphicUpdate(self, map):
        if (self.scatte):
            self.scatte.remove()
        self.update_position()
        self.plot(map)

    def progressJob(self):
        if self.job.rest > 0:
            self.job.rest -= self.step
            self.storage_capacity -= self.step * self.width
        else:
            self.storage_capacity -= self.job.rest * self.width  # si le rest est negatif du au cacul on le récupére
            self.totalAquisitionPriority += self.job.priority
            self.tokenImages.add(Image(self.job, self.width))
            self.job = None

    def updateTasks(self, map=None):
        expired = set()
        taskloss=0
        self.next_tasks = set()
        self.nextStorageEstimation = 0
        for task in self.tasks:
            task.expiration -= 1
            if task.expiration <= 0:
                # for plots
                if (map):
                    task.unplot()
                # we remember  expired images to be removed at the last
                expired.add(task)
            else:
                if(not self.job):
                  loss=self.tryBeginTask(map,task)
                  if(self.job):
                    expired.add(task)
                  else:
                    if loss>0:
                      taskloss+=loss
                      expired.add(task)
                    else: 
                      if (self.possibleaction and self.nearInTrajectory(task.begin_position, steps=300 / self.speed)):
                        self.nextStorageEstimation += (task.length * self.width)
                        self.next_tasks.add(task)
 
                else: 
                  if (self.possibleaction and self.nearInTrajectory(task.begin_position, steps=300 / self.speed)):
                      self.nextStorageEstimation += (task.length * self.width)
                      self.next_tasks.add(task)

        # we delete expired  images
        self.tasks -= expired
        return taskloss

    def tryBeginTask(self, map,task):
        
        # if it's possible to do this task we wil make it as current job
        decision,loss=self.can_do(task)
        if decision:
            self.job = task
            if (map):
              task.unplot()
            self.job.begin()
        return loss

    def can_do(self, task):

        if Earth2D.getDistance(self.position,task.begin_position) < 6:
            self.totalRequestsPriority += task.priority 
            if not  (task.length * self.width) <= self.storage_capacity :
              return False,task.priority
              
            else :
              return True,0
        else:
          return False,0
          
    def addTask(self, map):
        task = Task.getRadomTasks(1, self)[0]
        if (map):
            plot_task(self, task, map)
        self.totalRequestsPriority += task.priority
        self.tasks.add(task)

    def plot(self, map):
        self.scatte = map.scatter(self.position[0], self.position[1],
                                  color=(colors[self.id] if not self.isConnected else 'g'),
                                  s=int(100 / np.log(Satellite.counter)))

    def isAtteignable(self, station):
        # if the satellite is connected we check just if we can send another aquisition to this station , and check that we have enoght time to deconnect pro from
        return Earth2D.getDistance(station.position, self.getPostStepsPossition(
            (int(self.isConnected) + 1) * station.avg_connexion)) < station.limitdistance

    def canTransfert(self, image, station):
        transferttime = image.needTime(station.debit)
        # check if the time of trasnfert is lower than expiration of the aquisition plus probably time of connection
        if transferttime + station.avg_connexion * int(self.isConnected) >= image.expiration:
            return False

        PostTransmissionPos = self.getPostStepsPossition(
            (1 + int(self.isConnected)) * transferttime + station.avg_connexion)
        distance = Earth2D.getDistance(station.position, PostTransmissionPos)

        return distance < station.limitdistance

    def updateImages(self):
        penalisation = 0
        self.maxPriority = 0
        self.maxSize=0
        self.minExpiration=np.inf
        expired = set()
        self.possibleUnloading = set()
        for image in self.tokenImages:
            image.expiration -= 1
            if (image.expiration <= 0):
                expired.add(image)
                self.storage_capacity += image.size
                penalisation += image.priority / 2
            else:
                if self.availableStation:
                    if self.canTransfert(image, self.availableStation):
                        self.possibleUnloading.add(image)
                        if (self.maxPriority < image.priority):
                            self.maxPriority = image.priority
                        
                        if (self.maxSize < image.size):
                            self.maxSize = image.size

                        if (self.minExpiration < image.expiration):
                            self.minExpiration = image.expiration


        self.tokenImages -= expired
        return penalisation

    def tryTransfertImages(self, stations, unload=None, map=None):
        reward = 0

        if self.isConnected and self.intransmission:
            reward += self.progressTransmission()


        elif (self.disconnecting):

            self.progressDisconnexion()

        elif self.isconnecting:
            self.progressConnexion()

        elif unload != None:
            if (unload):
                self.intransmission = True
                if(unload==1):
                   self.toUnload = np.random.choice(
                          [image for image in self.possibleUnloading if image.priority >= self.maxPriority])
                elif unload==2:
                   self.toUnload = np.random.choice(
                          [image for image in self.possibleUnloading if image.size >= self.maxSize])
                
                else:
                   self.toUnload = np.random.choice(
                          [image for image in self.possibleUnloading if image.expiration <= self.minExpiration])

                if (not self.isConnected):
                    if (self.estimatedfillingrate() < 0.8):
                        reward -= self.availableStation.avg_connexion
                    self.availableStation.connected=True
                    self.isconnecting = True
                    self.progressConnexion()

            else:
                if (self.isConnected):
                    self.disconnecting = True
                    self.progressDisconnexion()

        return reward

    def endOfLap(self):
        self.updated += 1
        distance = Earth2D.getDistance(self.initial_position, self.position)
        if (distance < self.step * 8 and self.updated > 10):
            print(distance, self.position, self.initial_position, self.step)
        return distance < self.step * 5 and self.updated > 6

    def getAvailableStation(self, stations):
        # check if we are aleready connected to a station we check that it's in the area where we can do a transmission
        if (self.disconnecting or self.isconnecting):
            return False
        if (self.availableStation):
            if not self.isAtteignable(self.availableStation):

                if (self.isConnected):
                    self.disconnecting = True
                else:
                    self.availableStation.possibleconnections -=1
                    self.availableStation = None
                return False
            return True


        for station in stations:
            if (self.isAtteignable(station)):
                self.availableStation = station
                self.availableStation.possibleconnections += 1
                self.allvisibylitys += 1
                # preparing connexion time to be used after
                self.connexionTime = 0
                return True

        self.connexionTime = 0
        self.availableStation = None
        return False

    def progressConnexion(self):
        self.connexionTime += 1
        self.isConnected = self.connexionTime >= self.availableStation.avg_connexion
        self.isconnecting = not self.isConnected
        if (self.isConnected):
            self.allconnexions += 1

    def progressDisconnexion(self):
        self.connexionTime -= 1
        self.isConnected = self.connexionTime != 0
        if (not self.isConnected):
            self.availableStation.connected = False
            self.availableStation = None
            self.disconnecting = False

    """
    when we are connected to a station  and we progress acquisition transfering  
    """

    def progressTransmission(self):
        image, station = self.toUnload, self.availableStation
        image.size -= station.debit
        self.storage_capacity += station.debit
        if (image.size <= 0):
            self.storage_capacity += image.size
            try:
                self.tokenImages.remove(image)
                self.possibleUnloading.remove(image)
            except:
                pass
            self.intransmission = False
            self.toUnload = None
            self.completed += 1
            self.totalcompletedPriority += image.priority
            return image.priority

        return 0


    def possibleAction(self, stations):
        ended = self.endOfLap()
        return (self.getAvailableStation(stations)  and not self.availableStation.connected and
                not (self.isconnecting or self.disconnecting or self.intransmission) and
                len(self.possibleUnloading) > 0) or ended, ended  # if we have possible action or have ended

    def __str__(self):
        return "Satellite  id : {} | storage capacity : {} | current filling : {} | estimated next filling : {}  | number of tasks : {} | number of stored images : {} | copleted : {} | cumulate priority : {} | visibylity : {} |  coneexions : {}".format(
            self.id, self.storage_capacity, self.fillingrate(), self.estimatedfillingrate(), len(self.tasks),
            len(self.tokenImages), self.completed, self.totalcompletedPriority, self.allvisibylitys, self.allconnexions)

    def NextAction(self, stations):
        reward = 0
        self.possibleaction = False
        while (not self.possibleAction(stations)):
            reward += self.update(stations)
        self.possibleaction = True
        self.updateTasks()
        self.state = self.getstate()
        return reward


    def getstate(self):
        assert self.availableStation != None and len(self.possibleUnloading) > 0
      

        avilableiamgesstate = np.array([np.array([im.size, im.priority, im.expiration]) for im in self.possibleUnloading]).reshape(-1, 3)
        nexttasksstate = np.array([np.array([task.length * self.width, task.priority, task.expiration]) for task in self.next_tasks]).reshape(-1, 3)
        tokenimagesstate = np.array([np.array([im.size, im.priority, im.expiration]) for im in self.tokenImages]).reshape(-1, 3)

        if (nexttasksstate.shape[0] < 1):
            nexttasksstate = np.ones((1, 3))
        state = [np.array([int(self.isConnected),int(self.availableStation.connected),self.availableStation.possibleconnections, self.storage_capacity,
                           self.fillingrate(), len(self.tokenImages), len(self.possibleUnloading)]).reshape(-1),
                 avilableiamgesstate.mean(0).reshape(-1),
                 tokenimagesstate.mean(0).reshape(-1),
                 np.array([self.estimatedfillingrate(), self.nextStorageEstimation, len(self.next_tasks)]).reshape(-1),
                 np.nanmean(nexttasksstate, axis=0).reshape(-1)]
        res = np.hstack(state)
        return res
    def getCsvDescription(self):
      return "{},{},{},{},{},{},{}\n".format(self.id,self.allvisibylitys,self.allconnexions,self.completed,self.totalcompletedPriority,self.totalExpiredAquisitionPriority,self.totalExpiredRequestsPriority)

