import json
import logging
import struct
import time

from .Callbacks import DataCollector
from .Protocol import Protocol


class Sender:
    def __init__(self):
        self.dataColector = None
        self.connection = None
        self.ShouldSend = True

    def SetDataCollector(self, dataCollector=DataCollector()):
        self.dataColector = dataCollector

    def SetConnection(self, connection):
        self.connection = connection

    def TelemetryLoop(self, interval):
        self.ShouldSend = True
        sleep_time = interval / 1000
        last_time = time.time()

        while self.ShouldSend:
            if time.time() - last_time >= sleep_time:
                try:
                    self.SendIMU()
                    self.SendPosition()
                    self.SendBattery()
                    self.SendMotors()

                except:
                    self.ShouldSend = False

                last_time = time.time()
            else:
                time.sleep(sleep_time)
                # msg should be json

    def SendTaskManagerInfo(self, msg):
        msg = json.dumps(msg)
        data = msg.encode()
        key = bytes([Protocol.TO_GUI.STATUS_MSG.TASK_MANAGER])
        self.SendStatusMsg(data, key)

    def SendLog(self, msg):
        data = msg.encode()
        key = bytes([Protocol.TO_GUI.STATUS_MSG.LOGGER])
        self.SendStatusMsg(data, key)

    def SendOperationMode(self, mode):
        key = None
        if mode == "jetson_stm":
            key = Protocol.TO_GUI.STATUS_MSG.MODE_JETSON_STM
        elif mode == "pc_simulation":
            key = Protocol.TO_GUI.STATUS_MSG.MODE_PC_SIMULATION
        elif mode == "jetson_simulation":
            key = Protocol.TO_GUI.STATUS_MSG.MODE_JETSON_SIMULATION
        if key != None:
            self.SendStatusMsg(None, bytes([key]))

    def SendJetsonStatus(self):
        data = self.dataColector.GetJetsonStatus()
        msg = struct.pack(str(len(data)) + "f", *(data))
        key = bytes([Protocol.TO_GUI.STATUS_MSG.SENSOR_STATUS])

    def SendTemperature(self):
        data = self.dataColector.GetTemperature()
        msg = struct.pack(str(len(data)) + "f", *(data))
        key = bytes([Protocol.TO_GUI.TELEMETRY_MSG.TEMPERATURE])

    def SendHummidity(self):
        data = self.dataColector.GetHummidity()
        msg = struct.pack(str(len(data)) + "f", *(data))
        key = bytes([Protocol.TO_GUI.TELEMETRY_MSG.HUMMIDITY])

        self.Send_Telemetry_msg(msg, key)

    def SendBattery(self):
        data = self.dataColector.GetBattery()
        msg = struct.pack(str(len(data)) + "f", *(data))
        key = bytes([Protocol.TO_GUI.TELEMETRY_MSG.BATTERY])
        self.Send_Telemetry_msg(msg, key)

    def SendDetection(self, fps, detectionList):
        key = bytes([Protocol.TO_GUI.AUTONOMY_MSG.DETECTION])
        test = {"fps": fps, "ObjectsList": detectionList}
        # print(test)
        data = json.dumps({"fps": fps, "ObjectsList": detectionList})
        data = data.encode()
        self.SendAutonomyMsg(data, key)

    def SendDetectionStart(self, val):
        if val:
            key = bytes([Protocol.TO_GUI.AUTONOMY_MSG.DETECTOR_STARTED])
        else:
            key = bytes([Protocol.TO_GUI.AUTONOMY_MSG.DETECTOR_STOPED])
        self.SendAutonomyMsg(None, key)

    def SendAutonomyStart(self, val):

        if val:
            key = bytes([Protocol.TO_GUI.AUTONOMY_MSG.AUTONOMY_STARTED])
        else:
            key = bytes([Protocol.TO_GUI.AUTONOMY_MSG.AUTONOMY_STOPED])
        self.SendAutonomyMsg(None, key)

    def SendArmCallback(self):
        key = bytes([Protocol.TO_GUI.REQUEST_RESPONCE_MSG.ARMED])
        self.SendRequestResponceMsg(bytes(), key)
        print("arm confirmed")

    def SendDisarmCallback(self):
        key = bytes([Protocol.TO_GUI.REQUEST_RESPONCE_MSG.DISARMED])
        self.SendRequestResponceMsg(bytes(), key)
        print("disarm confirmed")

    def SendPosition(self):
        data = self.dataColector.GetPosition()
        msg = struct.pack(str(len(data)) + "f", *(data))
        key = bytes([Protocol.TO_GUI.TELEMETRY_MSG.POSITION])
        self.Send_Telemetry_msg(msg, key)

    def SendMotors(self):
        data = self.dataColector.GetMotors()
        msg = struct.pack(str(len(data)) + "f", *(data))
        key = bytes([Protocol.TO_GUI.TELEMETRY_MSG.MOTORS])
        self.Send_Telemetry_msg(msg, key)

    def SendIMU(self):
        data = self.dataColector.GetIMU()  # roll, pitch,yaw,depth
        msg = struct.pack(str(len(data)) + "f", *(data))
        key = bytes([Protocol.TO_GUI.TELEMETRY_MSG.IMU])
        self.Send_Telemetry_msg(msg, key)

    def SendPIDs(self):
        data = self.dataColector.GetPIDs()
        msg = struct.pack(str(len(data)) + "f", *(data))
        key = bytes([Protocol.TO_GUI.REQUEST_RESPONCE_MSG.PID])
        self.SendRequestResponceMsg(msg, key)
        pass

    def SendStatusMsg(self, data, type):
        if data == None:
            data = type
        else:
            data = type + data
        self.__Send_msg(data, bytes([Protocol.TO_GUI.STATUS]))

    def SendAutonomyMsg(self, data, type):
        if data == None:
            data = type
        else:
            data = type + data
        self.__Send_msg(data, bytes([Protocol.TO_GUI.AUTONOMY]))

    def SendRequestResponceMsg(self, data, type):
        data = type + data
        self.__Send_msg(data, bytes([Protocol.TO_GUI.REQUEST_RESPONCE]))

    def Send_Telemetry_msg(self, data, type):
        data = type + data
        self.__Send_msg(data, bytes([Protocol.TO_GUI.TELEMETRY]))

    def __Send_msg(self, data, type):
        header = struct.pack("<i", len(data) + 1)
        msg = bytearray(header + type + data)
        try:
            self.connection.send(msg)
        except:
            pass
