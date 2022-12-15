import json
import threading

from tools.Delegate import Delegate


class Object(object):
    keys = ["type", "accuracy", "boundingBox", "boundingBox3D", "position", "distance", "height", "width"]

    type = None
    accuracy = None
    boundingBox = None  # must by list [minX,minY,maxX,maxY]

    boundingBox3D = None
    position = None  # object position relative to boat attitude
    distance = None
    height = None
    width = None

    def toDictionary(self):
        ret = {}
        for i in self.keys:
            a = eval("self." + i)
            if a != None:
                ret[i] = a
        return ret


class DetectorBaseClass(object):
    __callback = Delegate()
    shouldDetect = False
    detectionThread = None
    __isDetecting = False

    def __init__(self):
        self.__callback = Delegate()

    def isDetecting(self):
        return self.__isDetecting

    def StartDetecting(self):
        self.detectionThread = threading.Thread(target=self.__DetectorLoop, name="DetectorThread")
        self.shouldDetect = True
        self.detectionThread.start()

    def StopDetecting(self):
        self.shouldDetect = False
        if self.detectionThread != None and self.detectionThread.is_alive():
            self.detectionThread.join()

    def __DetectorLoop(self):
        self.__isDetecting = True
        while self.shouldDetect:
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
