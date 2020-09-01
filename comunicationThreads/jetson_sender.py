import struct
from sender import Sender

class JetsonSender(Sender):
    def __init__(self, protocol):
        super().__init__(protocol)
        self.proto = protocol["TO_JETSON"]
    def sendMotors(self,data):
        tx_buffer = [self.proto["MOTORS"]]+data
        tx_buffer = struct.pack('<B5f', *(tx_buffer))
        self.send_msg(tx_buffer)

    def sendBoatData(self, data =[]):
        tx_buffer = [self.proto["BOAT_DATA"]]+data
        tx_buffer = struct.pack('<B5f', *(tx_buffer))
        self.send_msg(tx_buffer)
