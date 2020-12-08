
import socket, struct, logging, time, threading
from variable import SIM_STREAM_ADDRESS
from cameraStream.stream import cameraStream


class SimulationStreamerClient(cameraStream):
    """Stream client which use simulation streamer"""

    def __init__(self):
        threading.Thread.__init__(self)
        """Inicjalizacja socekta """
        self.port = SIM_STREAM_ADDRESS[1]
        self.ip = SIM_STREAM_ADDRESS[0]
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.active = True
        self.data = b""
        self.frame = None
        self.newFrame = False
        self.lastframe =0
        self.lock = threading.Lock()

    def run(self):
        logging.debug("Connecting to stream from simulation")
        self.socket.connect((self.ip, self.port))
        logging.debug("Connected with simulation stream")
        while self.active:
            self.receive_frame()
            #around 50 fps
            time.sleep(0.02)
            
    def stop(self):
        self.socket.close()

    def __del__(self):
        self.socket.close()
    
    def getFrame(self):
        return self.frame

    def receive_frame(self):
        self.newFrame = False
        self.data = b""
        self.socket.send(b"\x69")
        confirm = self.socket.recv(1)
        if not(confirm == b"\x69"):
            logging.debug("Message error s")
        lenght = self.socket.recv(4)
        lenght = struct.unpack('<I', lenght)[0]
        while not(len(self.data) >= lenght):
            self.data += self.socket.recv(4096)
        self.frame=self.data        
        self.newFrame = True