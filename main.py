from controlThread.controlThread_simulation import simulationConnection
from communicationThreads.GUI.GUIServer import connectionHandler
from cameraStream.stream_simulation import SimulationStreamClient
import logging
import variable
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    cameraStream = SimulationStreamClient()
    guiServer = connectionHandler(cameraStream)
    controlThread = simulationConnection(guiServer.comunicator)
    guiServer.setControlThread(controlThread)
    guiServer.start()
