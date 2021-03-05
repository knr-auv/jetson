import time, math
import tools.MathUtils as h
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
        LastDetections = list()
        detection = self.get_detection()
        detection = detection["detected"]
        for i in detection:
            if(i['visibleInFrame']):
                o = self.handle_detection(i)
                LastDetections.append(o.toDictionary())

        ####################################
        fps = 1
        self.InvokeCallback(fps,LastDetections)

        
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
        x,y,z = [self.controlThread.getPosition()[0],self.controlThread.getPosition()[1],self.controlThread.getPosition()[2]]
        name = detection["className"]
        dist = detection["distance"]
        min =detection["min"]
        minx= min['x']
        miny= min['y']
        max = detection["max"]
        maxx = max["x"]
        maxy = max["y"]
        center_width = (minx+maxx)/2
        center_height = (miny+maxy)/2

        obj = base.Object()
        obj.type = name
        obj.accuracy = 1
        obj.distance = dist;
        obj.boundingBox = [minx,miny,maxx,maxy]
        a,b,c = [self.controlThread.getAttitude()[0],self.controlThread.getAttitude()[1],self.controlThread.getAttitude()[2]]
        pos = h.posFromPicture(107,60,dist,center_width,center_height)
        obj.position = h.toGlobalRef(pos,[a,b,c])
        obj.width = 1.2;
        obj.height =1.4;

        #more smart stuff
        return obj



    def get_detection(self):
        #camera stream is based on simulation web api.
        return self.client.get_detection()



