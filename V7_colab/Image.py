from      Task import *
from      Satellite import  *

class Image(object):
    def __init__(self,task,width):
        self.id=task.id
        self.size=task.length*width
        self.priority=task.priority
        self.expiration=task.expiration
    def needTime(self,debit):
        return self.size/debit
    def __str__(self):
        return ' Image  {} size:{} , proiority :  {} , expiration {} '.format(self.id,self.size , self.priority,self.expiration)