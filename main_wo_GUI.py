# main without GUI

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
    # init control thread
    controlThread = SimulationControlThread()

    # init autonomy helpers
    # we can switch them according to environment
    detector = Simulation_noGPU_detector(cameraStream, controlThread)
    controller = Controller(controlThread)

    # init autonomy
    autonomyThread = AutonomyThread(detector, controller)

    # load config and start camera
    controlThread.setPIDs(ConfigLoader.LoadPIDs("config/PID_simulation.json"))
    cameraStream.start()
    autonomyThread.StartAutonomy()
