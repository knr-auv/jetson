from .Callbacks import DataCollector
from .Protocol import Protocol
import struct, time

class Sender:

    def __init__(self):
        self.dataColector = None
        self.connection = None
        self.ShouldSend = True

    def SetDataCollector(self, dataCollector = DataCollector()):
        self.dataColector = dataCollector;

    def SetConnection(self, connection):
        self.connection = connection

    def TelemetryLoop(self, interval):
        self.ShouldSend = True
        sleep_time = interval/1000
        last_time = time.time()
        try:
            while (self.ShouldSend):
                if(time.time()-last_time>=sleep_time):
                    self.SendIMU()
                    last_time = time.time()
                else:
                    time.sleep(sleep_time)
        except:
            pass


    def SendArmCallback(self):
        key = bytes([Protocol.TO_GUI.REQUEST_RESPONCE_MSG.ARMED])
        self.SendRequestResponceMsg(bytes(), key)
        print("arm confirmed")
    def SendDisarmCallback(self):
        key = bytes([Protocol.TO_GUI.REQUEST_RESPONCE_MSG.DISARMED])
        self.SendRequestResponceMsg(bytes(), key)
        print("disarm confirmed")
    def SendIMU(self):
        data = self.dataColector.GetIMU() #roll, pitch,yaw,depth
        msg = struct.pack(str(len(data))+'f', *(data))
        key = bytes([Protocol.TO_GUI.TELEMETRY_MSG.IMU])
        self.Send_Telemetry_msg(msg, key)
    def SendPIDs(self):
        data = self.dataColector.GetPIDs()
        msg = struct.pack(str(len(data))+'f', *(data))
        key = bytes([Protocol.TO_GUI.REQUEST_RESPONCE_MSG.PID])
        self.SendRequestResponceMsg(msg, key)
        pass

    def SendAutonomyMsg(self, data, type):
        data = type+data
        self.__Send_msg(data,bytes([Protocol.TO_GUI.AUTONOMY]))

    def SendRequestResponceMsg(self,data,type):
        data = type+data
        self.__Send_msg(data,bytes([Protocol.TO_GUI.REQUEST_RESPONCE]))

    def Send_Telemetry_msg(self, data, type):
        data = type+data
        self.__Send_msg(data,bytes([Protocol.TO_GUI.TELEMETRY]))

    def __Send_msg(self, data, type):
        header = struct.pack('<i', len(data)+ 1)
        msg = bytearray(header+type+data)
        self.connection.send(msg)