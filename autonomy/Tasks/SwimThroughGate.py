import tools.Logger as Logger
from.TaskBaseClass import TaskBaseClass
class SwimThroughGate(TaskBaseClass):
    controller = None
    detections = None
    name = "FGTask"

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

    def Worker(self, *args):
        Logger.write('Swiming throught gate', self.name)
        self.controller.move_forward(700)
        time.sleep(2)
        self.controller.stop()
        self.should_work = False
        self.InvokeCallback(1,1);
