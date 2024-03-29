import math
import time

import tools.MathUtils as h
from Detectors.DetectorBaseClass import DetectorBaseClass, Object


class Simulation_noGPU_detector(DetectorBaseClass):
    def __init__(self, cameraStream, controlThread, client):
        super().__init__()
        # control thread is used for obtaining position and attitude data
        self.controlThread = controlThread
        self.cameraStream = cameraStream
        self.client = client
        if cameraStream == None:
            return None

    j = 0

    def DetectorTask(self):
        time.sleep(1 / 30)
        LastDetections = list()
        detection = self.get_detection()
        # detection = detection["detected"]
        for i in detection:
            o = self.handle_detection(i)
            LastDetections.append(o.toDictionary())

        ####################################
        """
        fdd = open("depth"+str(self.j)+".jpg","wb");
        fdc = open("color"+str(self.j)+".jpg","wb");
        depth =self.client.get_depth_map()
        color =self.cameraStream.getFrame()
        fdd.write(depth)
        fdc.write(color)
        fdd.close()
        fdc.close()
        self.j +=1
        """
        fps = 30
        self.InvokeCallback(fps, LastDetections)

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
        x, y, z = [
            self.controlThread.getPosition()[0],
            self.controlThread.getPosition()[1],
            self.controlThread.getPosition()[2],
        ]
        name = detection["className"]
        dist = detection["distance"]
        min = detection["min"]
        minx = min["x"]
        miny = min["y"]
        max = detection["max"]
        maxx = max["x"]
        maxy = max["y"]
        center_width = (minx + maxx) / 2
        center_height = (miny + maxy) / 2

        obj = Object()
        obj.type = name
        obj.accuracy = 1
        obj.distance = dist
        obj.boundingBox = [minx, miny, maxx, maxy]
        a, b, c = [
            self.controlThread.getAttitude()[0],
            self.controlThread.getAttitude()[1],
            self.controlThread.getAttitude()[2],
        ]
        pos = h.posFromPicture(107, 60, dist, center_width, center_height)
        obj.position = h.toGlobalRef(pos, [a, b, c])
        obj.width = 1.2
        obj.height = 1.4

        # more smart stuff
        return obj

    def get_detection(self):
        # camera stream is based on simulation web api.
        return self.client.okon.get_visible_detection()
