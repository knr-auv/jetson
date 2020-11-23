from controlThread.controlThread_simulation import SimulationControlThread
from communicationThreads.GUI.Server import JetsonServer 
from communicationThreads.GUI.Callbacks import PrepareCallbacks
from cameraStream.SimulationStreamClient import SimulationStreamClient
from cameraStream.ToGuiStream import ToGuiStream
from autonomy.AutonomyThread import AutonomyThread
from config.ConfigLoader import ConfigLoader
import logging
import variable


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    #core elements
    controlThread = SimulationControlThread()
    cameraStream = SimulationStreamClient()
    autonomyThread = AutonomyThread(controlThread, cameraStream)
    
    guiStream = ToGuiStream(cameraStream)
    server = JetsonServer(variable.GUI_ADDRESS)
    cameraStream.start() 
    guiStream.Start()

    controlThread.setPIDs(ConfigLoader.LoadPIDs("config/PID_simulation.json"))
    c,d =PrepareCallbacks(autonomyThread, controlThread)
    server.SetCallbacks(c,d)
    server.StartServer()
    
