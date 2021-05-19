from .SwimToXYZTask import SwimToXYZTask
from .FindGateTask import FindGateTask
class Tasks:
    SwimToXYZ = SwimToXYZTask
    FindGate = FindGateTask
    def __init__(self, controller):
        self.FindGate = FindGateTask(controller)
    #    self.SwimToXYZ = SwimToXYZTask(controller)