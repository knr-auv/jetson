from tools.Delegate import Delegate

class Object(object):
    index = int() # numer taska
    status = int() # status taska. Np. 0- todo, 1- done, 2- aborted/failed

class TaskBaseClass(object):
    __callback = Delegate()

    def __init__(self):
        self.__callback = Delegate()

    def StartTask(self, task_id):
        pass

    
    def InvokeCallback(self, index, status):
        self.__callback.Invoke(index, status)

    def RegisterTaskCallback(self, callback):
        self.__callback.Register(callback)

    def RemoveTaskCallback(self, callback):
        self.__callback.Remove(callback)