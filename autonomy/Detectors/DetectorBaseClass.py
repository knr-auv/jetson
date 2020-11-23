from tools.Delegate import Delegate

class Object(object):
    index = int() # numer obiektu w ogóle
    type_index = int() #numer obiektu danego typu
    type = str() #typ obiektu
    pos = None #położenie obiektu


class DetectorBaseClass(object):
    ObjectsList = list()
    __callback = Delegate()

    def __init__(self):
        self.__callback = Delegate()

    def StartDetecting(self):
        pass

    def StopDetecting(self):
        pass

    
    def InvokeCallback(self, objectList, NewDetection):
        self.__callback.Invoke(objectList, newDetection)

    def RegisterDetectionCallback(self, callback):
        self.__callback.Register(callback)

    def RemoveDetectionCallback(self, callback):
        self.__callback.Remove(callback)




