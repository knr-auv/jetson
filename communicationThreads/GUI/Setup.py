
import controlThread.controlThread as ct
from .Callbacks import  Callbacks, DataCollector


def PrepareCallbacks(autonomyThread, controlThread = ct.ControlThread()):
    dc = DataCollector()
    cb = Callbacks()

    dc.GetControlMode = controlThread.getControlMode
    dc.GetDepth = controlThread.getDepth
    dc.GetIMU = controlThread.getIMUData
    dc.GetMotors = controlThread.getMotors
    dc.GetPIDs = controlThread.getPIDs
    #dc.GetHumidity = controlThread.getHumidity
    dc.GetPosition =  controlThread.getPosData
    dc.GetBattery = lambda: [12.1,13.1]
    cb.ArmCallback = controlThread.arm
    cb.DisarmCallback = controlThread.disarm
    cb.ChangeModeCallback = controlThread.setControlMode
    cb.SteeringDataCallback = controlThread.HandleSteeringInput
    cb.SetPIDs = controlThread.setPIDs
    return cb,dc


