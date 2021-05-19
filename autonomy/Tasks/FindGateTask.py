import tools.Logger as Logger
from.TaskBaseClass import TaskBaseClass
class FindGateTask(TaskBaseClass):
    controller = None
    detections = None
    name = "FGTask"
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

    """
    center_x = 0
    center_y =0 

    width = 0
    height = 0
    width_to_x =0 
    width_to_y = 0
    w_h_ratio = 0
    width_on_screen = 0 
    height_on_screen = 0
    """

    def Worker(self, *args):
        Logger.write('Starting autonomy loop', self.name)
        while len(self.detections)==0 and self.__should_work:
            Logger.write('Looking for gate', self.name)
            for i in range(8):
                if(len(self.detections)==0):
                    time.sleep(0.2)
                    self.controller.turn_right(5)
            self.controller.turn_left(40)
            for i in range(8):
                if(len(self.detections)==0):
                    time.sleep(0.2)
                    self.controller.turn_left(5)
        Logger.write('Gate found', self.name)
        #here we can pass some status msg and task index
        self.InvokeCallback(1,2)
    def HandleDetection(self, detection):
        self.detections = detection

    def Stop(self):
        pass