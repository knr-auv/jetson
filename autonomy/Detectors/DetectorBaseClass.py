from tools.Delegate import Delegate
import threading
import json

class Object(object):
    #keys must match class properties names
    #if you need something new just add property and key. for now gui is ignoring distance, height, width 
    #nie każdy paramter musi mieć nadaną wartość
    keys = ["type","x","y","z","accuracy","distance","height","width"]
    index = None
    type_index = None
    type = None
    #polozenie obiektu
    x = None
    y=None
    z=None
    #
    distance = None
    accuracy = None
    width = None
    height = None
    def toDictionary(self):
        ret = {}
        for i in keys:
            a = eval('self.'+i)
            if a !=None:
                ret[i]=a
        return ret

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
    
    def InvokeCallback(self, fps,objectList, NewDetection):
        self.__callback.Invoke(fps,objectList, NewDetection)

    def RegisterDetectionCallback(self, callback):
        self.__callback.Register(callback)

    def RemoveDetectionCallback(self, callback):
        self.__callback.Remove(callback)

    


