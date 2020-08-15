
import numpy as np
import asyncio,socket, struct, logging, time
from variable import STREAM_ADDRESS
from cameraStream.stream import cameraStream


class SimulationClient(cameraStream):
    """Klasa Tworzy clienta do odbierania ramek zdjec z symulacji"""
    def __init__(self):
        super(SimulationClient, self).__init__()
        """Inicjalizacja socekta """
        self.port = STREAM_ADDRESS[1]
        self.ip = STREAM_ADDRESS[0]
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.active = True
        self.data = b""
        self.frame = None
        self.newFrame = False

    def run(self):
        self.socket.connect((self.ip, self.port))
        while self.active:
            self.receive_frame()
            #around 40 fps
            time.sleep(0.01)
            
    def stop(self):
        self.socket.close()

    def __del__(self):
        self.socket.close()

    def getFrame(self):
        return self.frame

    """Metdoa zwraca klatke OpenCV uzyskana z Symulacji"""
    def receive_frame(self):
        self.data = b""
        self.socket.send(b"\x69")
        confirm = self.socket.recv(1)
        if not(confirm == b"\x69"):
            logging.debug("Message error s")
        lenght = self.socket.recv(4)
        lenght = struct.unpack('<I', lenght)[0]
        while not(len(self.data) >= lenght):
            self.data += self.socket.recv(4096)
        self.frame = self.data
        self.newFrame = True