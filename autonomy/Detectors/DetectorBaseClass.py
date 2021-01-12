from tools.Delegate import Delegate
import threading
import json

class Object(object):
    type = None
    accuracy = None
    boundingBox = None #must by list [minX,minY,maxX,maxY]

    boundingBox3D = None
    position = None #object position relative to boat attitude
    distance = None
    height = None
    width = None
    
class DetectorBaseClass(object):
    ObjectsList = list()
    LastDetections = list()
    __callback = Delegate()
    shouldDetect= False
    detectionThread = None
    __isDetecting = False
    def __init__(self):
        self.__callback = Delegate()
    def isDetecting(self):
        return self.__isDetecting
    def StartDetecting(self):
        self.ObjectsList = list()
        self.LastDetections = list()
        self.detectionThread = threading.Thread(target = self.__DetectorLoop, name="DetectorThread")
        self.shouldDetect = True
        self.detectionThread.start();

    def StopDetecting(self):
        self.shouldDetect = False
        if(self.detectionThread != None and self.detectionThread.is_alive()):
            self.detectionThread.join()

    def __DetectorLoop(self):
        self.__isDetecting = True
        while(self.shouldDetect):
            self.DetectorTask()
        self.__isDetecting = False

    def DetectorTask(self):
        pass
    
    def InvokeCallback(self, fps, NewDetection):
        self.__callback.Invoke(fps, NewDetection)

    def RegisterDetectionCallback(self, callback):
        self.__callback.Register(callback)

    def RemoveDetectionCallback(self, callback):
        self.__callback.Remove(callback)

    


