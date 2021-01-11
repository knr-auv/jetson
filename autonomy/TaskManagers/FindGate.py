# Mission plan for finding gate and swiming under it
from .TaskManagerBase import TaskManager

class Mission(TaskManager):
    def __init__(self, detector, controller):
        super.__init__(self,  detector, controller)

    def run():
        #something none blocking f.e. task
        #self.starttask(findgate,None);
        pass

    def HandleDetection(self,fps, detectionList):
        #do something when new detection received
        #if gate detected swim to it
        #swim under the gate
        pass