from tools.Delegate import Delegate

class Object(object):
    index = int() # numer obiektu w ogóle
    type_index = int() #numer obiektu danego typu
    type = str() #typ obiektu
    pos = None #położenie obiektu


class TaskManager(object):
    currentTask =None # obecnie wykonywany task
    detector = None
    controller = None
    def __init__(self, detector, controller):
        self.__callback = Delegate()
        self.tasksList = task_list
        detector.RegisterDetectionCallback(self.HandleDetection)
        self.controller = controller
        self.detector = detector

    def run(self):
        #do some non blocking stuff here
        pass

    def StartTask(self,task,*args):
        self.currentTask = task
        pass

    def StopCurrentTask(self):
        if self.currentTask:
            self.currentTask.stop()
        pass
    
    def MissionCompleted(self):
        self.controller.disarm()
        self.detector.RemoveDetectionCallback(self.HandleDetection)

    #Handle sensors input
    def HandleDetection(self, detectionList):
        pass
    