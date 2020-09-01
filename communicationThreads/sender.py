import struct, logging


class Sender():
    def __init__(self, protocol):
        self.pid_spec = protocol["PID_SPEC"]
        self.control_spec = protocol['CONTROL_SPEC']

    def send(self, msg):
        pass

    def send_msg(self, msg):
        header = struct.pack('<i', len(msg)+ 4)
        msg = bytearray(header+msg)
        self.send(msg)

    def sendPid(self, PID = []):
        axis = PID[0]
        if axis=='roll':
            spec=self.pid_spec["roll"]
        elif axis =='pitch':
            spec = self.pid_spec["pitch"]
        elif axis == 'yaw':
            spec = self.pid_spec["yaw"]
        elif axis =='all':
            spec = self.pid_spec["all"]
        elif axis == 'depth':
            spec = self.pid_spec['depth']
        else:
            logging.debug(f"{axis} is not a valid argument of sendPid. Valid arguments: 'roll', 'pitch', 'yaw', 'all'")
            return
        PID.pop(0)
        if spec != self.pid_spec['all']:
            tx_buffer = [self.proto["PID"],spec]  + PID
            tx_buffer = struct.pack('<2B4f', *(tx_buffer))
            self.send_msg(tx_buffer)
        elif spec == self.pid_spec['all']:
            tx_buffer = [self.proto["PID"],spec]  + PID
            tx_buffer = struct.pack('<2B16f', *(tx_buffer))
            self.send_msg(tx_buffer)
