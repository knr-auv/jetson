from tools.Delegate import Delegate

class Object(object):
    index = int() # numer obiektu w ogóle
    type_index = int() #numer obiektu danego typu
    type = str() #typ obiektu
    pos = None #położenie obiektu


class TaskManager(object):
    tasksList # lista zdefiniowanych wczesniej tasków
    currentTask # obecnie wykonywany task
    controller # obiekt controller'a 
    detector # obiekt detector'a 
    __callback = Delegate()

    def __init__(self, task_list, controller, detector):
        self.__callback = Delegate()
        self.tasksList = task_list
        self.controller = controller
        self.detector = detector

    def StartTaskManager(self):
        pass

    def StopTaskManager(self):
        pass

    
    def InvokeCallback(self, tasksList, currentTask):
        self.__callback.Invoke(tasksList, currentTask)

    def RegisterTaskManagerCallback(self, callback):
        self.__callback.Register(callback)

    def RemoveTaskManagerCallback(self, callback):
        self.__callback.Remove(callback)