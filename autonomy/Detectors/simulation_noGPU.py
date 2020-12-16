import time, math
import autonomy.Detectors.Helpers as h
import autonomy.Detectors.DetectorBaseClass as base
from communicationThreads.Simulation.simulationClient import SimulationClient
class Simulation_noGPU_detector(base.DetectorBaseClass):
    cameraStream = None
    def __init__(self, cameraStream, controlThread):
        super().__init__()
        #control thread is used for obtaining position and attitude data
        self.controlThread = controlThread
        self.cameraStream = cameraStream
        self.client = SimulationClient()
        if(cameraStream==None):
            return None

    def DetectorTask(self):
        time.sleep(1)
        detection = self.get_detection()
        detection = detection["detected"]
        for i in detection:
            if(i['visibleInFrame']):
                o = self.handle_detection(i)

        #########only for testing ###########
        if(len(self.LastDetections)==5):
            self.ObjectsList.pop(0)
            self.LastDetections.pop(0)
        ####################################
        fps = 1
        self.InvokeCallback(fps,*self.prepareCb())
        
    def handle_detection(self, detection):
        """
        dictionary keys (not sure about min,max... probably min = [min_x,min_y]) you can just print this dictionary and check...:
        visibleInFrame;
        min, max ->vec2
        fill
        className
        distance;
        colorPercentVisible;
        """
        name = detection["className"]
        dist = detection["distance"]
        obj = base.Object()
        #more smart stuff
        return obj

    def check_if_seen(self, o):
        #sprawdź, czy widziany
        #jeśli tak to może popraw pozycje już wcześniej znalezionego obiektu
        #cokolwiek
        return False
    
    def prepareCb(self):
        a = list()
        b = list()
        for i in self.ObjectsList:
            a.append(i.toDictionary())
        for i in self.LastDetections:
            b.append(i.toDictionary())
        return a,b

    def get_detection(self):
        #camera stream is based on simulation web api.
        return self.client.get_detection()

