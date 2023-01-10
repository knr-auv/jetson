# main  with GUI
import logging

import tools.Logger as Logger
import variable
from cameraStream.SimulationWAPIStreamClient import SimulationWAPIStreamClient
from cameraStream.ToGuiStream import ToGuiStream
from communicationThreads.GUI.Server import JetsonServer
from communicationThreads.GUI.Setup import PrepareCallbacks
from communicationThreads.Simulation.okon_sim_client import OkonSimClient
from config.ConfigLoader import ConfigLoader
from controlThread.controlThread_simulation import SimulationControlThread
from Detectors.simulation_noGPU import Simulation_noGPU_detector

if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)
    # init sim_client
    simulation_client = OkonSimClient(ip="127.0.0.1", port=44210, sync_interval=0.05, debug=False)
    if not simulation_client.connect():
        print("Not connected!")

    # init cameraStream
    cameraStream = SimulationWAPIStreamClient(simulation_client)
    cameraStream.setFov(60, 60)
    # init control thread
    controlThread = SimulationControlThread(simulation_client)

    # init autonomy helpers
    # we can switch them according to environment
    # TODO: currently detector is only usable once. FIX!!!
    detector = Simulation_noGPU_detector(cameraStream, controlThread, simulation_client)

    # TODO: add new autonomy
    # init autonomy
    autonomyThread = None
    # autonomyThread = AutonomyThread(detector, controller)
    # autonomyThread.StartAutonomy()

    # load config and start camera
    controlThread.setPIDs(ConfigLoader.LoadPIDs("config/PID_simulation.json"))
    cameraStream.start()

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
    Logger.setStream(server.sender.SendLog, None)
