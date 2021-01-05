import autonomy.Detectors.DetectorBaseClass as Detector
from autonomy.Controller import Controller
import tools.Logger as Logger
import threading

class AutonomyThread:
    detector = Detector.DetectorBaseClass()
    controller = Controller(None)
    def __init__(self, detector, controller):#, detector = Detectors.Detector()):
     self.detector = detector
     self.controller = controller
     self.name = "AutonomyThread"

    def StartAutonomy(self):
        Logger.write('Autonomy started', self.name)
        x = threading.Thread(target= self.controller.test_swim())
        self.controller.arm()
        x.start()
        #self.controller.swim_to_xyz([0,0,0])


    def StopAutonomy(self):
        self.controller.disarm()
        Logger.write('AutonomyStoped', self.name)

    def StartDetector(self):
        if(not self.detector.isDetecting()):
            self.detector.StartDetecting()
            Logger.write("Detector started",self.name)

    def StopDetector(self):
        if(self.detector.isDetecting):
            self.detector.StopDetecting()
            Logger.write("Detector stoped",self.name)