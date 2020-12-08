import communicationThreads.Simulation.simulationClient as sc
import threading, logging, time, socket
from cameraStream.stream import cameraStream
import variable

class SimulationWAPIStreamClient(cameraStream):
    """Stream client which use simulation web API"""

    def __init__(self):
        threading.Thread.__init__(self)
        self.frame = None
        self.client = sc.SimulationClient()

    def run(self):
        while self.active:
            self.receive_frame()
            #around 50 fps
            time.sleep(0.01)

    def getFrame(self):
        return self.frame

    def receive_frame(self):
        val = self.client.get_stream_frame()
        if(val != None):
            self.frame = val