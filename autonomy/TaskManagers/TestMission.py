import autonomy.Tasks.Tasks as Tasks
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
        task = Tasks.SwimToXYZTask(self.controller,0,0,0)
        self.controller.arm()
        task.Start()
    