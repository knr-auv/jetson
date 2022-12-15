from tools.Delegate import Delegate


class Callbacks:
    ArmCallback = Delegate()
    DisarmCallback = Delegate()
    SteeringDataCallback = Delegate()
    ChangeModeCallback = Delegate()
    SetPIDs = Delegate()
    StartAutonomyCallback = Delegate()
    StopAutonomyCallback = Delegate()
    StartDetectorCallback = Delegate()
    StopDetectorCallback = Delegate()

    GUIDisconnected = Delegate()


class DataCollector:
    def __init__(self):
        pass

    def GetControlMode(self):
        pass

    def GetHummidity(self):
        pass

    def GetDepth(self):
        pass

    def GetIMU(self):
        pass

    def GetMotors(self):
        pass

    def GetPIDs(self):
        pass

    def GetHumidity(self):
        pass

    def GetPosition(self):
        pass

    def GetBattery(self):
        pass

    def GetJetsonStatus(self):
        pass
