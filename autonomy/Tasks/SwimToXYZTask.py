import autonomy.Controller as Ctr
from.TaskBaseClass import TaskBaseClass
import threading, time

class SwimToXYZTask(TaskBaseClass):
    x = None
    controller =  Ctr.Controller
    def __init__(self,controller, x,y,z):
        self.x = threading.Thread(target= lambda: self.__run(x,y,z))
        self.controller = controller
    def Start(self):
          self.x.start()

    def Stop(self):
        pass
    def __run(self,x,y,z):
        #self.controller.swim_to_xyz([x,y,z])
        self.controller.test_swim()
