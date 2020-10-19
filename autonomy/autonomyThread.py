import threading, time, logging
import socket, struct
from controlThread.controlThread import controlThread
from cameraStream.stream import cameraStream
from variable import GUI_DEPTH_MAP
import cv2
import numpy as np
import random
class autonomy(threading.Thread):
    def __init__(self,controlThread = controlThread(), stream = cameraStream(), gui_active=True):
        threading.Thread.__init__(self)
        self.active = False
        self.gui_active = gui_active
        logging.debug("starting autonomy")
        self.stream = stream
        self.cT= controlThread
        self.client = controlThread.client;
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
                detection = self.client.get_detection()
                
                print(detection)
            except:
               logging.debug("detection error")
            if self.gui_active and not error:
                #detections should be tuple of detection. Detection must look like (name, accuracy, distance, position), where position is x,y,w,h 
                #detection, fps, image
                self.streamToGui.send_detection(detection,1/(time.perf_counter()-now),image)

        
    def stop(self):
        #self.depthMapStream.active = False
        self.active = False
        if self.gui_active:
            self.streamToGui.stop()
            del(self.streamToGui)

