import controlThread.controlThread as ct
import tools.Logger as Logger
from communicationThreads.GUI.Callbacks import Callbacks, DataCollector
from Detectors.DetectorBaseClass import DetectorBaseClass, start_detector


def PrepareCallbacks(detector: DetectorBaseClass, autonomyThread, controlThread=ct.ControlThread):
    """Method which prepares interface for GUI"""

    dc = DataCollector()
    cb = Callbacks()

    dc.GetControlMode = controlThread.getControlMode
    dc.GetDepth = controlThread.getDepth
    dc.GetIMU = controlThread.getIMUData
    dc.GetMotors = controlThread.getMotors
    dc.GetPIDs = controlThread.getPIDs
    # dc.GetHumidity = controlThread.getHumidity
    dc.GetPosition = controlThread.getPosData
    dc.GetBattery = lambda: [12.1, 13.1]

    # callbacks
    # TODO: add autonomy Callbacks for new autonomy
    # cb.StartAutonomyCallback += autonomyThread.StartAutonomy
    # cb.StopAutonomyCallback += autonomyThread.StopAutonomy
    # TODO: currently detector is only usable once. FIX!!!
    cb.StartDetectorCallback += detector.StartDetecting
    cb.StopDetectorCallback += detector.StopDetecting

    cb.ArmCallback += controlThread.arm
    cb.DisarmCallback += controlThread.disarm
    cb.ChangeModeCallback += controlThread.setControlMode
    cb.SteeringDataCallback += controlThread.HandleSteeringInput
    cb.SetPIDs += controlThread.setPIDs

    cb.GUIDisconnected += controlThread.disarm
    cb.GUIDisconnected += detector.StopDetecting
    return cb, dc
