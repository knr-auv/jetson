import threading, time, logging
import socket, struct
from controlThread.controlThread import controlThread
from cameraStream.stream import cameraStream
from autonomy.detectionStream import *
from variable import GUI_DEPTH_MAP
import cv2
import numpy as np
import random
from .detector import detector, draw_rectangle
det = detector("autonomy/cfg/op6.cfg","autonomy/cfg/data.txt","autonomy/op9_best.weights")
class autonomy(threading.Thread):
    def __init__(self,controlThread = controlThread(), stream = cameraStream(), gui_active=True):
        threading.Thread.__init__(self)
        self.active = False
        self.gui_active = gui_active
        logging.debug("starting autonomy")
        self.stream = stream
        self.cT= controlThread
        self.getDepthMap = self.cT.client.get_depth_map #map is tandard jpg(bytes). u can use cv2.imdecode(numpy.frombuffer(self.getDepthMap(), np.uint8), 0) to use it with opencv
        self.detector = det
        if gui_active:
            self.streamToGui = detectionStream()
        
    def run(self):
        self.active = True
        while self.active:

            error = False
            time.sleep(1)
            now = time.perf_counter()
            #gray_scale =self.getDepthMap()
            image = self.stream.getFrame()
            #gray_scale =cv2.imdecode(np.frombuffer(gray_scale, np.uint8), -1)
            img = cv2.imdecode(np.frombuffer(image, np.uint8), -1)
            try:
                #img, detections =self.detector.detect_distance(img, gray_scale)
                #print(detections)
                img, detections = self.detector.detect(img,0.4)
            except:
                error=True
            if self.gui_active and not error:
                self.streamToGui.send_detection(detections,1/(time.perf_counter()-now),image)

        
    def stop(self):
        #self.depthMapStream.active = False
        self.active = False
        if self.gui_active:
            self.streamToGui.stop()
            del(self.streamToGui)

