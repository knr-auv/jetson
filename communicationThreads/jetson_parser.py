import struct, logging, sys

class JetsonParser():
    def parse(self, data):
        proto = self.protocol["TO_JETSON"]
        pid_spec = self.protocol["PID_SPEC"]
        control_spec = self.protocol["CONTROL_SPEC"]
        try:
            if data[0]== proto["PID"]:
                if data[1]!= pid_spec['all']:
                    msg = struct.unpack('<2B4f', data)
                    msg = list(msg)
                    msg.pop(0)
                    if msg[0]==pid_spec["roll"]:
                        msg[0] = 'roll'
                    elif msg[0]==pid_spec["pitch"]:
                        msg[0] ='pitch'
                    elif msg[0]==pid_spec["yaw"]:
                        msg[0]='yaw'
                    elif msg[0]==pid_spec["depth"]:
                        msg[0]='depth'
                    self.signals.receivedPID.emit(msg)
                elif data[1]==pid_spec["all"]:
                    msg  = struct.unpack('<2B16f', data)
                    msg = list(msg)
                    msg.pop(0)
                    msg[0]='all'
                    self.signals.receivedPID.emit(msg)

            elif data[0]==proto["MOTORS"]:
                msg = struct.unpack('<B5f', data)
                msg = list(msg)
                msg.pop(0)
                self.signals.receivedMotors.emit(msg)

            elif data[0] == proto["BOAT_DATA"]:
                msg = struct.unpack('<2B'+str(data[1])+'s',data)
                self.signals.receivedBoatData.emit(msg[2])

            elif data[0] == proto["IMU"]:
                msg = struct.unpack('<B4f',data)
                msg = list(msg)
                msg.pop(0)
                self.signals.receivedIMUData.emit(msg)

            elif data[0] == proto["CONTROL"]:
                if data[1]==control_spec["ARMED"]:
                    logging.debug("ARMED")
                    self.signals.armed.emit()
                elif data[1]==control_spec["DISARMED"]:
                    logging.debug("DISARMED")
                    self.signals.disarmed.emit()


            elif data[0] == proto["AUTONOMY_MSG"]:
                msg = struct.unpack('<2B'+str(data[1])+'s',data)
                text = msg[2].decode('utf-8')
                self.signals.receivedAutonomyMsg.emit(text)

        except:
            sys.exc_info()
            logging.critical("error while parsing data")
