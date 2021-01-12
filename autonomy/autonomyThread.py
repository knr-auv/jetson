import autonomy.Detectors.DetectorBaseClass as Detector
import autonomy.TaskManagers.FindGate as task
from autonomy.Controller import Controller
import tools.Logger as Logger
import threading

class AutonomyThread:
    detector = Detector.DetectorBaseClass()
    controller = Controller(None)
    menager = None
    def __init__(self, detector, controller):#, detector = Detectors.Detector()):
     self.detector = detector
     self.controller = controller
     self.name = "AutonomyThread"
     self.manager = task.Mission(self.detector, self.controller)
    def StartAutonomy(self):
        Logger.write('Autonomy started', self.name)
        #x = threading.Thread(target= self.controller.test_swim())
        #self.controller.arm()
        #x.start()
        #self.controller.swim_to_xyz([0,0,0])

        self.manager.run()


    def StopAutonomy(self):
        self.controller.disarm()
        self.manager.MissionCompleted()
        Logger.write('AutonomyStoped', self.name)

    def StartDetector(self):
        if(not self.detector.isDetecting()):
            self.detector.StartDetecting()
            Logger.write("Detector started",self.name)

    def StopDetector(self):
        if(self.detector.isDetecting):
            self.detector.StopDetecting()
            Logger.write("Detector stoped",self.name)