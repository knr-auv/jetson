

class Callbacks:

    def __init__(self):
        pass
    
    def ArmCallback(self):
        pass

    def DisarmCallback(self):
        pass

    #data is int[5] roll, pitch, yaw, throttle, up/down
    def SteeringDataCallback(self, data = list()):
        pass

    def ChangeModeCallback(self,mode = str()):
        pass

    def SetPIDs(self, data):
        pass
    
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
