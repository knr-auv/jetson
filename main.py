from controlThread.controlThread_simulation import SimulationControlThread
from communicationThreads.GUI.Server import JetsonServer 
from communicationThreads.GUI.DataCollector import DataCollector
from communicationThreads.GUI.Callbacks import Callbacks
from cameraStream.SimulationStreamClient import SimulationStreamClient
from cameraStream.ToGuiStream import ToGuiStream
from autonomy.AutonomyThread import AutonomyThread
import logging
import variable

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    #core elements
    controlThread = SimulationControlThread()
    cameraStream = SimulationStreamClient()
    cameraStream.start()
    guiStream = ToGuiStream(cameraStream)
    guiStream.Start()
    autonomyThread = AutonomyThread(controlThread, cameraStream)
    #either autonomy thread or gui...

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

    server = JetsonServer(variable.GUI_ADDRESS)
    server.SetCallbacks(cb,dc)
    server.StartServer()
