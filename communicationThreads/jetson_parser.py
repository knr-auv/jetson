import json
import logging
import sys

from parser_baseclass import Parser


class JetsonParser(Parser):
    def __init__(self, protocol):
        super().__init__(protocol)
        self.parser_proto = protocol["TO_JETSON"]

    def parse(self, data):
        logging.debug("Parsing")
        data = data.decode("ansi")
        data = json.loads(data)
        logging.debug(f"frame:{data}")
        msg = list(data)
        try:
            if data[0] == self.parser_proto["PID"]:
                logging.debug("PID")
                if data[1] != self.pid_spec["all"]:
                    msg.pop(0)
                    if msg[0] == self.pid_spec["roll"]:
                        msg[0] = "roll"
                    elif msg[0] == self.pid_spec["pitch"]:
                        msg[0] = "pitch"
                    elif msg[0] == self.pid_spec["yaw"]:
                        msg[0] = "yaw"
                    elif msg[0] == self.pid_spec["depth"]:
                        msg[0] = "depth"
                    logging.debug(msg)
                elif data[1] == self.pid_spec["all"]:
                    msg.pop(0)
                    msg[0] = "all"
                    logging.debug(msg)

            elif data[0] == self.parser_proto["MOTORS"]:
                logging.debug("MOTORS")
                msg.pop(0)
                logging.debug(msg)

            elif data[0] == self.parser_proto["BOAT_DATA"]:
                logging.debug("BOAT_DATA")
                logging.debug(msg)

            elif data[0] == self.parser_proto["IMU"]:
                logging.debug("IMU")
                msg.pop(0)
                logging.debug(msg)

            elif data[0] == self.parser_proto["CONTROL"]:
                logging.debug("CONTROL")
                if data[1] == self.control_spec["START_TELEMETRY"]:
                    logging.debug("START_TELEMETRY")
                elif data[1] == self.control_spec["STOP_TELEMETRY"]:
                    logging.debug("STOP_TELEMETRY")
                elif data[1] == self.control_spec["START_PID"]:
                    logging.debug("START_PID")
                elif data[1] == self.control_spec["STOP_PID"]:
                    logging.debug("STOP_PID")
                elif data[1] == self.control_spec["ARMED"]:
                    logging.debug("ARMED")
                elif data[1] == self.control_spec["DISARMED"]:
                    logging.debug("DISARMED")
                elif data[1] == self.control_spec["START_AUTONOMY"]:
                    logging.debug("START_AUTONOMY")
                elif data[1] == self.control_spec["STOP_AUTONOMY"]:
                    logging.debug("STOP_AUTONOMY")
                elif data[1] == self.control_spec["MODE"]:
                    logging.debug("MODE")

            elif data[0] == self.parser_proto["AUTONOMY_MSG"]:
                logging.debug("AUTONOMY_MSG")
                text = msg[2]
                logging.debug(text)
        except Exception as exc:
            logging.critical("error while parsing data")
            logging.critical(exc)
