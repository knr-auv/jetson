from cameraStream.stream import cameraStream
from controlThread.controlThread import controlThread
from.Detector import Detector

class AutonomyThread:
    """
    This class should be responsible for creating and managing autonomy and vision system
    """
    def __init__(self, controlThread = controlThread(), cameraStream= cameraStream()):
        self.cameraStream = cameraStream
        self.controlThread = controlThread
        self.detector = Detector()
        
    def StartAutonomy(self):
        pass

    def StartDetections(self, callback):
        pass