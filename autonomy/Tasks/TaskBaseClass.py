from tools.Delegate import Delegate
import threading
class Object(object):
    index = int() # numer taska
    status = int() # status taska. Np. 0- todo, 1- done, 2- aborted/failed

class TaskBaseClass(object):
    __callback = Delegate()
    __should_work = True
    __thread = None
    def __init__(self):
        self.__callback = Delegate()

    def Start(self, *args):
        __should_work = True
        __thread= threading.Thread(target = self.Worker, args = args)
        __thread.start()

    def Stop(self):
        __should_work = False
        __thread.join()

    def Worker(self, *args):
        pass
    def InvokeCallback(self, index, status):
        self.__callback.Invoke(index, status)

    def RegisterTaskCallback(self, callback):
        self.__callback.Register(callback)

    def RemoveTaskCallback(self, callback):
        self.__callback.Remove(callback)