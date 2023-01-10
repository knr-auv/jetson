import json
from threading import Lock, Thread

import tools.Logger as Logger
from tools.Delegate import Delegate


class Object:
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


class DetectorBaseClass(Thread):
    def __init__(self):
        super().__init__()
        self.__callback = Delegate()
        self.shouldDetect = False
        self.__isDetecting = False
        self.lock = Lock()

    def isDetecting(self):
        return self.__isDetecting

    def StartDetecting(self):
        with self.lock:
            self.shouldDetect = True
        self.start()
        Logger.write("Detector started", self.name)

    def StopDetecting(self):
        self.shouldDetect = False
        Logger.write("Stoping detector...", self.name)

    def DetectorTask(self):
        pass

    def run(self):
        self.__isDetecting = True
        while True:
            with self.lock:
                if not self.shouldDetect:
                    break
            self.DetectorTask()
        print("stopped")
        self.__isDetecting = False
        Logger.write("Detector stoped", self.name)

    def InvokeCallback(self, fps, NewDetection):
        self.__callback.Invoke(fps, NewDetection)

    def RegisterDetectionCallback(self, callback):
        self.__callback.Register(callback)

    def RemoveDetectionCallback(self, callback):
        self.__callback.Remove(callback)


def start_detector(detector: DetectorBaseClass):
    detector = detector()
    detector.StartDetecting()
