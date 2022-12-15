# main  with GUI
import logging

import tools.Logger as Logger
import variable
from autonomy.autonomyThread import AutonomyThread
from autonomy.Controller import Controller

# detector
from autonomy.Detectors.simulation_noGPU import Simulation_noGPU_detector

# cameraStream
from cameraStream.SimulationWAPIStreamClient import SimulationWAPIStreamClient
from cameraStream.ToGuiStream import ToGuiStream

# for GUI only
from communicationThreads.GUI.Server import JetsonServer
from communicationThreads.GUI.Setup import PrepareCallbacks
from config.ConfigLoader import ConfigLoader

# controlThread
from controlThread.controlThread_simulation import SimulationControlThread

if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)
    # init cameraStream
    cameraStream = SimulationWAPIStreamClient()
    cameraStream.setFov(60, 60)
    # init control thread
    controlThread = SimulationControlThread()

    # init autonomy helpers
    # we can switch them according to environment
    detector = Simulation_noGPU_detector(cameraStream, controlThread)
    controller = Controller(controlThread)

    # init autonomy
    autonomyThread = AutonomyThread(detector, controller)
    autonomyThread.StartAutonomy()

    # load config and start camera
    controlThread.setPIDs(ConfigLoader.LoadPIDs("config/PID_simulation.json"))
    cameraStream.start()
    # detector.StartDetecting()

    # lines only for gui
    mode = "simulation"
    # mode = "jetson_stm"
    guiStream = ToGuiStream(cameraStream)
    server = JetsonServer(variable.GUI_ADDRESS, mode)
    controlThread.ArmNotificator += server.sender.SendArmCallback
    controlThread.DisarmNotificator += server.sender.SendDisarmCallback
    guiStream.Start()

    # after receiving a msg server invokes a callback
    # for sending telemetry server uses 'dataCollector' marked below as 'd'
    c, d = PrepareCallbacks(detector, autonomyThread, controlThread)
    server.SetCallbacks(c, d)

    # event handling - make sure that arguments are matching
    detector.RegisterDetectionCallback(server.sender.SendDetection)

    # start when ready
    server.StartServer()

    # setup logger. F.e. Logger.setStream(print, None) or:
    # fd = open("log.txt","a")
    # Logger.setStream(fd.write, None)
    Logger.setStream(server.sender.SendLog, None)
