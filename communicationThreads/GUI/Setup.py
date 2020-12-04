import autonomy.AutonomyThread as at
import controlThread.controlThread as ct
from .Callbacks import  Callbacks, DataCollector

def ConvertPad(data, controlThread = ct.ControlThread()):
    mode = controlThread.getControlMode()
    roll = data[0]*30/1000;
    pitch = data[1]*30/1000;
    yaw = data[2]*30/1000;
    if(mode=="stable"):
        controlThread.setAttitude(roll,pitch,yaw)
        controlThread.addHeading(data[2])
        controlThread.moveForward(data[3])
        controlThread.addDepth(data[4]/100)
    elif(mode=="acro"):
        pass

def PrepareCallbacks(autonomyThread = at.AutonomyThread(), controlThread = ct.ControlThread()):
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


