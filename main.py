from controlThread.controlThread_simulation import simulationConnection
from comunicationThreads.GUIServer import connectionHandler


if __name__ == '__main__':
    
    guiServer = connectionHandler()
    controlThread = simulationConnection(guiServer.comunicator)
    guiServer.setControlThread(controlThread)
    guiServer.start()
