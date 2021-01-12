# Mission plan for finding gate and swiming under it
from .TaskManagerBase import TaskManager
import threading, time

class Mission(TaskManager):
    controller = None
    gate = False
    gatePos = None
    def __init__(self, detector, controller):
        super().__init__(detector, controller)
        self.controller = controller
        x = None
    def run(self):
        #something none blocking f.e. task
        #self.starttask(findgate,None);
        self.x = threading.Thread(target= lambda: self.find_gate())
        self.detector.StartDetecting()
        self.controller.arm()
        self.x.start()
        self.detector.RegisterDetectionCallback(self.HandleDetection)
        pass

    def find_gate(self):
        #self.controller.swim_to_xyz([0,0,1],2)
        self.controller._Controller__set_depth(1)
        angle = 40
        t = 1
        while not self.gate:
            self.controller.turn_right(angle)
            time.sleep(t)
            self.controller.move_forward(700)
            t+=0.1
            pass
        self.go_under()
        
    def go_under(self):
        self.controller.swim_to_xyz(self.gatePos)
        self.controller.move_forward(300)
        time.sleep(1)
        self.controller.stop()

    def HandleDetection(self,fps, detectionList):
        for i in detectionList:
            if i.type =="gate":
                self.gate = True
                self.gatePos = i.pos
        #do something when new detection received
        #if gate detected swim to it
        #swim under the gate
        pass