import struct, logging, json
from sender import Sender


class JetsonSender(Sender):
    def __init__(self, protocol):
        super().__init__(protocol)
        self.sender_proto = protocol["TO_ODROID"]

    def sendControl(self, msg):
        logging.debug("Sending control")
        if msg[0] == self.control_spec['START_TELEMETRY']:
            logging.debug('START_TELEMETRY')

        elif msg[0] == self.control_spec['STOP_TELEMETRY']:
            logging.debug('STOP_TELEMETRY')

        elif msg[0] == self.control_spec['START_PID']:
            logging.debug('START_PID')

        elif msg[0] == self.control_spec['STOP_PID']:
            logging.debug('STOP_PID')

        elif msg[0] == self.control_spec['START_AUTONOMY']:
            logging.debug('START_AUTONOMY')

        elif msg[0] == self.control_spec['STOP_AUTONOMY']:
            logging.debug('STOP_AUTONOMY')

        elif msg[0] == self.control_spec['MODE']:
            logging.debug('MODE')

        frame = [self.sender_proto["CONTROL"]] + msg
        logging.debug(f"frame: {frame}")
        frame=json.dumps(frame).encode("ansi")
        self.send_msg(frame)

    def sendPIDRequest(self, axis):
        logging.debug("Send PID request")
        if axis == 'roll':
            spec = self.pid_spec["roll"]
        elif axis == 'pitch':
            spec = self.pid_spec["pitch"]
        elif axis == 'yaw':
            spec = self.pid_spec["yaw"]
        elif axis == 'depth':
            spec = self.pid_spec["depth"]
        elif axis == 'all':
            spec = self.pid_spec["all"]
        else:
            logging.debug(f"{axis} is not a valid argument of pidSend. Valid arguments: 'roll', 'pitch', 'yaw', 'all'")
            return
        frame = [self.sender_proto["PID_REQUEST"], spec]
        logging.debug(f"frame: {frame}")
        frame=json.dumps(frame).encode("ansi")
        self.send_msg(frame)

    def sendBoatDataRequest(self):
        logging.debug("send boat data request")
        frame = [self.sender_proto["BOAT_DATA_REQUEST"]]
        logging.debug(f"frame: {frame}")
        frame=json.dumps(frame).encode("ansi")
        self.send_msg(frame)

    def sendInput(self, data):
        frame = [self.sender_proto['PAD']] + data
        logging.debug(f"frame: {frame}")
        frame=json.dumps(frame).encode("ansi")
        self.send_msg(frame)
        if (self.checked == False):
            self.checked = True
            logging.debug("Msg was sent succesfully, connection with odroid has been established")
