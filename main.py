from controlThread.controlThread_simulation import simulationConnection
from comunicationThreads.GUIServer import connectionHandler
from cameraStream.stream_simulation import SimulationClient

if __name__ == '__main__':
    cameraStream = SimulationClient()
    guiServer = connectionHandler(cameraStream)
    controlThread = simulationConnection(guiServer.comunicator)
    guiServer.setControlThread(controlThread)
    guiServer.start()
