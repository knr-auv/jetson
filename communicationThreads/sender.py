import struct, logging, json


class Sender:
    def __init__(self, protocol):
        self.pid_spec = protocol["PID_SPEC"]
        self.control_spec = protocol['CONTROL_SPEC']

    def send_msg(self, data):
        # self.ack = b""
        logging.debug("send_msg")
        length = struct.pack('<I', len(data))
        #logging.debug(f"frame length: {len(data)}")
        # logging.debug(length)
        header = length
        # header = b"\xA0" + length
        # logging.debug(header)
        try:
            self.active_conn.send(header)
        except Exception as e:
            logging.critical(e)
        logging.debug("Header sent")
        self.active_conn.sendall(data)
        logging.debug("Data sent")

    def sendPid(self, PID=[]):
        axis = PID[0]
        if axis == 'roll':
            spec = self.pid_spec["roll"]
        elif axis == 'pitch':
            spec = self.pid_spec["pitch"]
        elif axis == 'yaw':
            spec = self.pid_spec["yaw"]
        elif axis == 'all':
            spec = self.pid_spec["all"]
        elif axis == 'depth':
            spec = self.pid_spec['depth']
        else:
            logging.debug(f"{axis} is not a valid argument of sendPid. Valid arguments: 'roll', 'pitch', 'yaw', 'all'")
            return
        PID.pop(0)
        frame = [self.sender_proto["PID"], spec] + PID
        logging.debug(f"frame: {frame}")
        frame=json.dumps(frame).encode("ansi")
        self.send_msg(frame)
