import autonomy.AutonomyThread as at
import controlThread.controlThread as ct

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
    
    def GetDepth(self):
        pass

    def GetIMU(self):
        pass

    def GetMotors(self):
        pass

    def GetDetections(self):
        pass

    def GetPIDs(self):
        pass

    def GetHumidity(self):
        pass

    def GetPosition(self):
        pass

def ConvertPad(data, controlThread = ct.ControlThread()):
    mode = controlThread.getControlMode()
    if(mode=="stable"):
        controlThread.setAngle(data[1],data[0])
        controlThread.addHeading(data[2])
        controlThread.moveForward(data[3])
        controlThread.addDepth(data[4])
    elif(mode=="acro"):
        pass

def PrepareCallbacks(autonomyThread = at.AutonomyThread(), controlThread = ct.ControlThread()):
    dc = DataCollector()
    cb = Callbacks()

    dc.GetControlMode = controlThread.getControlMode
    dc.GetDepth = controlThread.getDepth
    dc.GetIMU = controlThread.getImuData
    dc.GetMotors = controlThread.getMotors
    dc.GetPIDs = controlThread.getPIDs
    dc.GetHumidity = controlThread.getHumidity
    dc.GetPosition = controlThread.getPosition

    cb.ArmCallback = controlThread.arm
    cb.DisarmCallback = controlThread.disarm
    cb.ChangeModeCallback = controlThread.setControlMode
    cb.SteeringDataCallback = lambda x:ConvertPad(x, controlThread)
    cb.SetPIDs = controlThread.setPIDs
    return cb,dc


