from controlThread.controlThread_simulation import SimulationControlThread
from communicationThreads.GUI.Server import JetsonServer 
from communicationThreads.GUI.Setup import PrepareCallbacks
import cameraStream.SimulationWAPIStreamClient as sc
from cameraStream.ToGuiStream import ToGuiStream
from autonomy.autonomyThread import AutonomyThread
from config.ConfigLoader import ConfigLoader
import logging
import variable
import tools.Logger as Logger


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    controlThread = SimulationControlThread()
    controlThread.setPIDs(ConfigLoader.LoadPIDs("config/PID_simulation.json"))
    #obraz z kamery + pełna komunikacja z symulacją -> można np. użyc cameraStream.client.get_detection
    cameraStream = sc.SimulationWAPIStreamClient()
    autonomyThread = AutonomyThread(controlThread, cameraStream)
    cameraStream.start() 

#lines only for gui (comment them if u are not using it)
    guiStream = ToGuiStream(cameraStream)
    server = JetsonServer(variable.GUI_ADDRESS)
    guiStream.Start()
    c,d =PrepareCallbacks(autonomyThread, controlThread)
    server.SetCallbacks(c,d)
    server.StartServer()

    #setting up logger
    #pierwszy argument to funkjca,która przyjmuje tekst jako argument
    #żeby wysyłać dane do GUI trzeba zaimportować logger i wywołać Logger.write(wiadomosc, autor), gdzie autor to np MainThread, AutonomyThread, detector etc...
    Logger.setStream(server.sender.SendLog, None)

    
